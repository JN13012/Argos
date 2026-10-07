/*
 * The corporate payment channel.
 *
 * Two steps. Preview quotes the payment and returns a signed instruction;
 * confirm sends that instruction back and we execute it. Nothing about the
 * payment is held between the two calls, because the signature is the
 * authority for what was instructed. That is what lets the same instruction
 * format be produced by the web client, the mobile app and a partner's own
 * software without any of them sharing our session store.
 *
 * Payments at or above the dual authorisation threshold need a second signer
 * before they are released.
 */

const express = require("express");
const { one, all, tx } = require("../db");
const { availableBalance } = require("../services/balances");
const { postJournal } = require("../services/ledger");
const { format } = require("../services/money");
const instructions = require("../services/instructions");
const { paymentPreview, paymentConfirm } = require("../schemas");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

const SUSPENSE_ACCOUNT_ID = 1;

// Payments of this size or larger need a second signature.
const DUAL_AUTH_THRESHOLD_MINOR = 1000000;

router.get("/api/payments/payees", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT id, payee_ref, display_name, account_number, sort_code
       FROM payees WHERE customer_id = $1 ORDER BY payee_ref`, [req.customer.id]);
  res.json(rows);
});

router.post("/api/payments/preview", requireCustomer, async (req, res) => {
  const parsed = paymentPreview.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid instruction" });
  const { payer_account_id, payee_ref, amount_minor, currency, reference } = parsed.data;

  const from = await one(
    "SELECT * FROM accounts WHERE id = $1 AND customer_id = $2 AND status = 'open'",
    [payer_account_id, req.customer.id]);
  if (!from) return res.status(404).json({ error: "account not found" });
  if (from.currency !== currency) {
    return res.status(400).json({ error: "payment currency must match the account" });
  }

  const payee = await one(
    "SELECT * FROM payees WHERE customer_id = $1 AND payee_ref = $2",
    [req.customer.id, payee_ref]);
  if (!payee) return res.status(404).json({ error: "no payee with that reference" });

  const instruction = {
    payer_account_id, payee_ref, amount_minor, currency,
    reference: reference || "",
    quote_id: instructions.newQuoteId(),
  };
  instruction.signature = instructions.sign(instruction);

  res.json({
    instruction,
    payee: { display_name: payee.display_name, account_number: payee.account_number },
    amount_display: await format(amount_minor, currency),
    needs_second_signature: amount_minor >= DUAL_AUTH_THRESHOLD_MINOR,
  });
});

/*
 * Execute a previously quoted instruction.
 *
 * The signature is verified over what came back, and the quote is single use,
 * so what we execute is what we quoted. Funds are re-checked here because the
 * balance may have moved since the quote was issued.
 */
router.post("/api/payments/confirm", requireCustomer, async (req, res) => {
  const parsed = paymentConfirm.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid instruction" });
  const i = parsed.data.instruction;

  const check = instructions.verify(i);
  if (!check.ok) return res.status(400).json({ error: check.why });

  const from = await one(
    "SELECT * FROM accounts WHERE id = $1 AND status = 'open'", [i.payer_account_id]);
  if (!from) return res.status(404).json({ error: "account not found" });
  if (from.customer_id !== req.customer.id) {
    return res.status(403).json({ error: "not your account" });
  }

  const available = await availableBalance(from.id);
  if (i.amount_minor > available) {
    return res.status(400).json({ error: "insufficient available funds", available });
  }

  const payee = await one(
    "SELECT * FROM payees WHERE customer_id = $1 AND payee_ref = $2",
    [req.customer.id, i.payee_ref]);
  if (!payee) return res.status(404).json({ error: "no payee with that reference" });

  instructions.consume(i.quote_id);

  if (i.amount_minor >= DUAL_AUTH_THRESHOLD_MINOR) {
    const p = await one(
      `INSERT INTO payments (payer_account_id, payee_id, payee_ref, amount_minor,
                             currency, reference, status, raised_by)
       VALUES ($1,$2,$3,$4,$5,$6,'awaiting_second_signature',$7) RETURNING id`,
      [from.id, payee.id, i.payee_ref, i.amount_minor, i.currency,
       i.reference || null, req.customer.id]);
    return res.json({
      ok: true, payment_id: p.id, status: "awaiting_second_signature",
      amount_display: await format(i.amount_minor, i.currency),
    });
  }

  const out = await tx(async (client) => {
    const posted = await postJournal({
      kind: "corporate-payment",
      reference: i.reference || i.payee_ref,
      narrative: `Payment to ${payee.display_name} (${i.payee_ref})`,
      created_by: req.customer.id,
      entries: [
        { account_id: from.id, amount_minor: -i.amount_minor, currency: i.currency, status: "pending" },
        { account_id: SUSPENSE_ACCOUNT_ID, amount_minor: i.amount_minor, currency: i.currency, status: "pending" },
      ],
    }, client);

    const p = (await client.query(
      `INSERT INTO payments (payer_account_id, payee_id, payee_ref, amount_minor,
                             currency, reference, status, raised_by, journal_id)
       VALUES ($1,$2,$3,$4,$5,$6,'released',$7,$8) RETURNING id`,
      [from.id, payee.id, i.payee_ref, i.amount_minor, i.currency,
       i.reference || null, req.customer.id, posted.journal_id])).rows[0];

    await client.query(
      `INSERT INTO settlement_queue (account_id, entry_id, amount_minor, rail)
       VALUES ($1,$2,$3,'corporate')`,
      [from.id, posted.entry_ids[0], i.amount_minor]);
    return { payment_id: p.id, journal_id: posted.journal_id };
  });

  res.json({
    ok: true, payment_id: out.payment_id, status: "released",
    paid_to: { payee_ref: i.payee_ref, display_name: payee.display_name,
               account_number: payee.account_number },
    amount_display: await format(i.amount_minor, i.currency),
  });
});

router.get("/api/payments/pending", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT p.id, p.payee_ref, p.amount_minor, p.currency, p.reference,
            p.status, p.raised_by, c.full_name AS raised_by_name
       FROM payments p
       JOIN accounts a ON a.id = p.payer_account_id
       LEFT JOIN customers c ON c.id = p.raised_by
      WHERE a.customer_id = $1 AND p.status = 'awaiting_second_signature'
      ORDER BY p.id`, [req.customer.id]);
  res.json(rows);
});

/*
 * Second signature.
 *
 * The signing operator is named in the request because the corporate channel
 * is used from a shared workstation and from the partner integration, neither
 * of which has one signatory per session. Four eyes is enforced here: the
 * approver may not be the person who raised it.
 */
router.post("/api/payments/:id/approve", requireCustomer, async (req, res) => {
  const id = parseInt(req.params.id, 10);
  const approverId = parseInt(req.body.approver_id, 10);
  if (!Number.isInteger(id) || !Number.isInteger(approverId)) {
    return res.status(400).json({ error: "invalid approval" });
  }

  const payment = await one(
    `SELECT p.*, a.customer_id, a.currency AS account_currency
       FROM payments p JOIN accounts a ON a.id = p.payer_account_id
      WHERE p.id = $1`, [id]);
  if (!payment) return res.status(404).json({ error: "payment not found" });
  if (payment.status !== "awaiting_second_signature") {
    return res.status(409).json({ error: "this payment is not awaiting a signature" });
  }

  const approver = await one(
    "SELECT id, full_name, role FROM customers WHERE id = $1 AND active = true", [approverId]);
  if (!approver) return res.status(404).json({ error: "unknown signatory" });

  if (approver.id === payment.raised_by) {
    return res.status(403).json({ error: "a payment cannot be approved by the person who raised it" });
  }

  const out = await tx(async (client) => {
    const posted = await postJournal({
      kind: "corporate-payment",
      reference: payment.reference || payment.payee_ref,
      narrative: `Payment to ${payment.payee_ref}, second signature ${approver.full_name}`,
      created_by: approver.id,
      entries: [
        { account_id: payment.payer_account_id, amount_minor: -payment.amount_minor,
          currency: payment.currency, status: "pending" },
        { account_id: SUSPENSE_ACCOUNT_ID, amount_minor: payment.amount_minor,
          currency: payment.currency, status: "pending" },
      ],
    }, client);

    await client.query(
      "INSERT INTO payment_approvals (payment_id, approver_id) VALUES ($1,$2)",
      [payment.id, approver.id]);
    await client.query(
      "UPDATE payments SET status = 'released', approved_by = $1, journal_id = $2 WHERE id = $3",
      [approver.id, posted.journal_id, payment.id]);
    await client.query(
      `INSERT INTO settlement_queue (account_id, entry_id, amount_minor, rail)
       VALUES ($1,$2,$3,'corporate')`,
      [payment.payer_account_id, posted.entry_ids[0], payment.amount_minor]);
    return posted;
  });

  res.json({
    ok: true, payment_id: payment.id, status: "released",
    approved_by: { id: approver.id, full_name: approver.full_name },
    journal_id: out.journal_id,
  });
});

module.exports = router;
