/*
 * Operations console.
 *
 * Back office tooling: release holds, inspect an account, post a correction.
 * Everything under /api/ops is behind the staff area gate in
 * src/middleware/staff-area.js, which runs before this router.
 */

const express = require("express");
const { q, one, all } = require("../db");
const { postedBalance, availableBalance } = require("../services/balances");

const router = express.Router();

router.get("/api/ops/accounts/:id", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad account" });
  const account = await one(
    `SELECT a.*, c.full_name, c.email
       FROM accounts a JOIN customers c ON c.id = a.customer_id
      WHERE a.id = $1`, [id]);
  if (!account) return res.status(404).json({ error: "account not found" });
  res.json({
    ...account,
    posted_minor: await postedBalance(id),
    available_minor: await availableBalance(id),
  });
});

router.get("/api/ops/holds", async (req, res) => {
  const rows = await all(
    `SELECT h.id, h.account_id, h.amount_minor, h.reason, h.created_at,
            a.account_number
       FROM holds h JOIN accounts a ON a.id = h.account_id
      WHERE h.released_at IS NULL ORDER BY h.id`);
  res.json(rows);
});

/* Releasing a hold puts the money back into what the customer can spend. */
router.post("/api/ops/holds/:id/release", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad hold" });

  const hold = await one("SELECT * FROM holds WHERE id = $1 AND released_at IS NULL", [id]);
  if (!hold) return res.status(404).json({ error: "no such open hold" });

  await q("UPDATE holds SET released_at = NOW() WHERE id = $1", [id]);
  await q("INSERT INTO audit_log (actor_id, action, detail) VALUES ($1,'hold.release',$2)",
    [req.customer ? req.customer.id : null, `hold ${id}`]);

  res.json({
    ok: true, hold_id: id, account_id: hold.account_id,
    available_minor: await availableBalance(hold.account_id),
  });
});

router.get("/api/ops/customers", async (req, res) => {
  const rows = await all(
    `SELECT id, email, full_name, role, organisation, kyc_status
       FROM customers ORDER BY id LIMIT 200`);
  res.json(rows);
});

module.exports = router;
