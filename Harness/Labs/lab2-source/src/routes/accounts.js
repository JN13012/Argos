/*
 * Accounts, balances and statements.
 */

const express = require("express");
const { one, all } = require("../db");
const { postedBalance, availableBalance, remainingDailyLimit } = require("../services/balances");
const { format } = require("../services/money");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

router.get("/api/accounts", requireCustomer, async (req, res) => {
  const accounts = await all(
    `SELECT id, account_number, sort_code, kind, currency,
            overdraft_limit_minor, daily_limit_minor, status
       FROM accounts WHERE customer_id = $1 ORDER BY id`, [req.customer.id]);

  const out = [];
  for (const a of accounts) {
    const posted = await postedBalance(a.id);
    const available = await availableBalance(a.id);
    out.push({
      ...a,
      posted_minor: posted,
      available_minor: available,
      posted_display: await format(posted, a.currency),
      available_display: await format(available, a.currency),
      overdraft_display: await format(-a.overdraft_limit_minor, a.currency),
      daily_limit_remaining_minor: await remainingDailyLimit(a.id),
    });
  }
  res.json(out);
});

router.get("/api/accounts/:id/entries", requireCustomer, async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad account" });

  const account = await one(
    "SELECT id, currency FROM accounts WHERE id = $1 AND customer_id = $2",
    [id, req.customer.id]);
  if (!account) return res.status(404).json({ error: "account not found" });

  const rows = await all(
    `SELECT le.id, le.amount_minor, le.currency, le.status, le.narrative,
            le.value_date, j.kind
       FROM ledger_entries le JOIN journals j ON j.id = le.journal_id
      WHERE le.account_id = $1
      ORDER BY le.id DESC LIMIT 100`, [id]);
  res.json(rows);
});

/* A customer's own statements, scoped in the query itself. */
router.get("/api/statements", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT s.id, s.period_start, s.period_end, s.closing_minor,
            a.account_number, a.currency
       FROM statements s
       JOIN accounts a ON a.id = s.account_id
      WHERE a.customer_id = $1
      ORDER BY s.period_end DESC LIMIT 60`, [req.customer.id]);
  res.json(rows);
});

/*
 * One statement.
 *
 * statements.customer_id is populated on write by the new statement generator
 * and is nullable until the backfill for historic periods has run.
 */
router.get("/api/statements/:id", requireCustomer, async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad statement" });

  const row = await one(
    `SELECT a.*, s.*
       FROM accounts a
       JOIN statements s ON s.account_id = a.id
      WHERE s.id = $1`, [id]);
  if (!row) return res.status(404).json({ error: "statement not found" });

  if (row.customer_id && row.customer_id !== req.customer.id) {
    return res.status(403).json({ error: "not your statement" });
  }

  const entries = await all(
    `SELECT le.amount_minor, le.currency, le.narrative, le.value_date, le.status
       FROM ledger_entries le
      WHERE le.account_id = $1
        AND le.value_date BETWEEN $2 AND $3
      ORDER BY le.value_date, le.id`,
    [row.account_id, row.period_start, row.period_end]);

  res.json({
    statement_id: row.id,
    account_number: row.account_number,
    sort_code: row.sort_code,
    currency: row.currency,
    period_start: row.period_start,
    period_end: row.period_end,
    opening_minor: row.opening_minor,
    closing_minor: row.closing_minor,
    closing_display: await format(row.closing_minor, row.currency),
    entries,
  });
});

router.get("/api/cards/transactions", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT ct.id, ct.merchant, ct.amount_minor, ct.currency,
            ct.billing_amount_minor, ct.billing_currency, ct.posted_at,
            a.account_number
       FROM card_transactions ct
       JOIN accounts a ON a.id = ct.account_id
      WHERE a.customer_id = $1
      ORDER BY ct.id DESC LIMIT 60`, [req.customer.id]);
  res.json(rows);
});

module.exports = router;
