/*
 * Card disputes.
 *
 * When a customer disputes a card transaction we raise a provisional credit
 * straight away and recover it from the acquirer afterwards. Regulation gives
 * us a short window to put the money back, so the credit is posted on the spot
 * rather than waiting for the scheme to respond.
 *
 * A customer may not claim back more than they were charged.
 */

const express = require("express");
const { one, all, tx } = require("../db");
const { postJournal } = require("../services/ledger");
const { format } = require("../services/money");
const { raiseDispute } = require("../schemas");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

// Where provisional credits are funded from until the scheme settles them.
const DISPUTES_SUSPENSE_ACCOUNT_ID = 2;

router.get("/api/disputes", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT d.id, d.reason, d.claimed_minor, d.provisional_credit_minor,
            d.status, d.created_at, ct.merchant, ct.amount_minor, ct.currency
       FROM disputes d
       JOIN card_transactions ct ON ct.id = d.transaction_id
      WHERE d.raised_by = $1
      ORDER BY d.id DESC`, [req.customer.id]);
  res.json(rows);
});

router.post("/api/disputes", requireCustomer, async (req, res) => {
  const parsed = raiseDispute.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid dispute" });
  const { transaction_id, reason, claimed_minor } = parsed.data;

  const txn = await one(
    `SELECT ct.*, a.customer_id, a.currency AS account_currency, a.id AS acct_id
       FROM card_transactions ct
       JOIN accounts a ON a.id = ct.account_id
      WHERE ct.id = $1`, [transaction_id]);
  if (!txn) return res.status(404).json({ error: "transaction not found" });
  if (txn.customer_id !== req.customer.id) {
    return res.status(403).json({ error: "not your transaction" });
  }

  const existing = await one(
    "SELECT id FROM disputes WHERE transaction_id = $1 AND status = 'open'", [transaction_id]);
  if (existing) {
    return res.status(409).json({ error: "there is already an open dispute on this transaction" });
  }

  // You cannot get back more than the transaction was for.
  if (claimed_minor > txn.amount_minor) {
    return res.status(400).json({
      error: "claim exceeds the transaction amount",
      transaction_amount_minor: txn.amount_minor,
    });
  }

  const out = await tx(async (client) => {
    const posted = await postJournal({
      kind: "dispute-provisional-credit",
      reference: `DISP-${transaction_id}`,
      narrative: `Provisional credit, dispute of ${txn.merchant}`,
      created_by: req.customer.id,
      entries: [
        { account_id: txn.acct_id, amount_minor: claimed_minor,
          currency: txn.account_currency, status: "posted" },
        { account_id: DISPUTES_SUSPENSE_ACCOUNT_ID, amount_minor: -claimed_minor,
          currency: txn.account_currency, status: "posted" },
      ],
    }, client);

    const d = (await client.query(
      `INSERT INTO disputes (transaction_id, raised_by, reason, claimed_minor,
                             provisional_credit_minor, journal_id, status)
       VALUES ($1,$2,$3,$4,$5,$6,'open') RETURNING id`,
      [transaction_id, req.customer.id, reason, claimed_minor,
       claimed_minor, posted.journal_id])).rows[0];
    return { dispute_id: d.id, journal_id: posted.journal_id };
  });

  res.json({
    ok: true,
    dispute_id: out.dispute_id,
    provisional_credit_minor: claimed_minor,
    provisional_credit_display: await format(claimed_minor, txn.account_currency),
    status: "open",
  });
});

module.exports = router;
