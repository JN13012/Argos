/*
 * Moving money between accounts.
 *
 *   internal  same customer, both sides ours, settles immediately
 *   external  another bank, leaves by the faster payments rail, memo posted
 *             until the settlement run confirms it
 */

const express = require("express");
const { q, one, all, tx } = require("../db");
const { availableBalance, remainingDailyLimit } = require("../services/balances");
const { postJournal } = require("../services/ledger");
const { internalTransfer } = require("../schemas");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

async function ownedAccount(customerId, accountId) {
  return one(
    "SELECT * FROM accounts WHERE id = $1 AND customer_id = $2 AND status = 'open'",
    [accountId, customerId]);
}

/*
 * Instant transfer between two of the customer's own accounts.
 *
 * Amounts arrive as a decimal string in major units. The channel team asked
 * for the string form so nothing is lost to JSON number handling between the
 * mobile client and here.
 */
router.post("/api/transfers/internal", requireCustomer, async (req, res) => {
  const parsed = internalTransfer.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid transfer" });
  const { from_account_id, to_account_id, narrative } = parsed.data;

  if (from_account_id === to_account_id) {
    return res.status(400).json({ error: "pick two different accounts" });
  }

  const from = await ownedAccount(req.customer.id, from_account_id);
  const to = await ownedAccount(req.customer.id, to_account_id);
  if (!from || !to) return res.status(404).json({ error: "account not found" });
  if (from.currency !== to.currency) {
    return res.status(400).json({ error: "both accounts must be in the same currency" });
  }

  const requested = Math.round(Number(parsed.data.amount) * 100);
  const available = await availableBalance(from.id);
  const dailyLeft = await remainingDailyLimit(from.id);

  if (requested > available) {
    return res.status(400).json({ error: "insufficient available funds", available });
  }
  if (requested > dailyLeft) {
    return res.status(400).json({ error: "daily limit reached", remaining: dailyLeft });
  }

  const minor = Math.round(parseFloat(parsed.data.amount) * 100);
  const result = await postJournal({
    kind: "internal-transfer",
    narrative: narrative || `Transfer to ${to.account_number}`,
    created_by: req.customer.id,
    entries: [
      { account_id: from.id, amount_minor: -minor, currency: from.currency, status: "posted" },
      { account_id: to.id, amount_minor: minor, currency: to.currency, status: "posted" },
    ],
  });

  res.json({
    ok: true,
    journal_id: result.journal_id,
    moved_minor: minor,
    from_balance: await availableBalance(from.id),
    to_balance: await availableBalance(to.id),
  });
});

/*
 * Payment out to another bank.
 *
 * The debit is memo posted straight away so the customer sees the money leave,
 * and queued for the settlement run which confirms it on the rail. Until that
 * runs the entry is pending, which is why availableBalance nets pending off.
 */
router.post("/api/transfers/external", requireCustomer, async (req, res) => {
  const accountId = parseInt(req.body.from_account_id, 10);
  const minor = parseInt(req.body.amount_minor, 10);
  const sortCode = String(req.body.sort_code || "");
  const accountNumber = String(req.body.account_number || "");

  if (!Number.isInteger(accountId) || !Number.isInteger(minor) || minor <= 0) {
    return res.status(400).json({ error: "invalid instruction" });
  }

  const from = await ownedAccount(req.customer.id, accountId);
  if (!from) return res.status(404).json({ error: "account not found" });

  const available = await availableBalance(from.id);
  if (minor > available) {
    return res.status(400).json({ error: "insufficient available funds", available });
  }

  const out = await tx(async (client) => {
    const posted = await postJournal({
      kind: "faster-payment-out",
      reference: `${sortCode} ${accountNumber}`,
      narrative: `Payment to ${accountNumber}`,
      created_by: req.customer.id,
      entries: [
        { account_id: from.id, amount_minor: -minor, currency: from.currency, status: "pending" },
        { account_id: SUSPENSE_ACCOUNT_ID, amount_minor: minor, currency: from.currency, status: "pending" },
      ],
    }, client);

    await client.query(
      `INSERT INTO settlement_queue (account_id, entry_id, amount_minor, rail)
       VALUES ($1,$2,$3,'faster-payments')`,
      [from.id, posted.entry_ids[0], minor]);
    return posted;
  });

  res.json({
    ok: true,
    journal_id: out.journal_id,
    state: "pending settlement",
    available_now: await availableBalance(from.id),
  });
});

// The bank's own suspense account, which the other leg of an outbound payment
// sits against until the rail confirms settlement. Seeded as account 1.
const SUSPENSE_ACCOUNT_ID = 1;

router.get("/api/transfers/recent", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT j.id, j.kind, j.narrative, j.created_at,
            le.amount_minor, le.currency, le.status, a.account_number
       FROM journals j
       JOIN ledger_entries le ON le.journal_id = j.id
       JOIN accounts a ON a.id = le.account_id
      WHERE a.customer_id = $1
      ORDER BY j.id DESC LIMIT 40`, [req.customer.id]);
  res.json(rows);
});

module.exports = router;
