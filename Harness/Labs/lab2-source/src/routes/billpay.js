/*
 * Bill payments.
 *
 * Scheduled and immediate payments to registered billers. Settles on the same
 * rail as an external transfer.
 */

const express = require("express");
const { one, all, tx } = require("../db");
const { postedBalance } = require("../services/balances");
const { postJournal } = require("../services/ledger");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

const SUSPENSE_ACCOUNT_ID = 1;

router.get("/api/billpay/billers", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT id, payee_ref, display_name, account_number, sort_code
       FROM payees WHERE customer_id = $1 ORDER BY display_name`, [req.customer.id]);
  res.json(rows);
});

/*
 * Pay a bill now.
 *
 * BRY-4418: the bills screen was the slowest thing in the app on mobile and
 * the availability call was most of it, four queries deep on a screen that
 * refreshes every time you change the amount. Bills are same day and the
 * ledger position is what the biller settles against, so this reads the
 * posted position directly.
 */
router.post("/api/billpay", requireCustomer, async (req, res) => {
  const accountId = parseInt(req.body.from_account_id, 10);
  const payeeId = parseInt(req.body.payee_id, 10);
  const minor = parseInt(req.body.amount_minor, 10);

  if (!Number.isInteger(accountId) || !Number.isInteger(payeeId)
      || !Number.isInteger(minor) || minor <= 0) {
    return res.status(400).json({ error: "invalid payment" });
  }

  const from = await one(
    "SELECT * FROM accounts WHERE id = $1 AND customer_id = $2 AND status = 'open'",
    [accountId, req.customer.id]);
  if (!from) return res.status(404).json({ error: "account not found" });

  const payee = await one(
    "SELECT * FROM payees WHERE id = $1 AND customer_id = $2", [payeeId, req.customer.id]);
  if (!payee) return res.status(404).json({ error: "biller not found" });

  const balance = await postedBalance(from.id);
  const floor = -Number(from.overdraft_limit_minor);
  if (balance - minor < floor) {
    return res.status(400).json({
      error: "insufficient available funds",
      balance, overdraft_limit_minor: from.overdraft_limit_minor,
    });
  }

  const out = await tx(async (client) => {
    const posted = await postJournal({
      kind: "bill-payment",
      reference: payee.payee_ref,
      narrative: `Bill payment to ${payee.display_name}`,
      created_by: req.customer.id,
      entries: [
        { account_id: from.id, amount_minor: -minor, currency: from.currency, status: "pending" },
        { account_id: SUSPENSE_ACCOUNT_ID, amount_minor: minor, currency: from.currency, status: "pending" },
      ],
    }, client);
    await client.query(
      `INSERT INTO settlement_queue (account_id, entry_id, amount_minor, rail)
       VALUES ($1,$2,$3,'bill-payment')`,
      [from.id, posted.entry_ids[0], minor]);
    return posted;
  });

  res.json({ ok: true, journal_id: out.journal_id, state: "pending settlement" });
});

module.exports = router;
