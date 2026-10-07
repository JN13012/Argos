/*
 * Signed payment instructions.
 *
 * The corporate channel is stateless between preview and confirm: the client
 * asks for a quote, we hand back the instruction with a signature over it, and
 * the client sends the whole thing back to be executed. The signature is what
 * makes the returned instruction trustworthy, so nothing about the payment
 * needs to be held server side between the two calls.
 *
 * The quote id is single use. It is recorded when the instruction is executed
 * and an instruction whose quote has been seen before is refused, so a signed
 * instruction cannot be replayed.
 */

const crypto = require("crypto");

/*
 * The channel key. Set it in the environment so that instructions survive a
 * restart and so several application instances agree; otherwise one is
 * generated per process, which is fine for a single node and means an
 * instruction quoted before a restart will not verify after it.
 */
const KEY = process.env.INSTRUCTION_SIGNING_KEY || crypto.randomBytes(32).toString("hex");
if (!process.env.INSTRUCTION_SIGNING_KEY) {
  console.warn("no INSTRUCTION_SIGNING_KEY set, using a key generated for this process");
}

const SEEN_QUOTES = new Set();

/* Every field of the instruction goes into the signature. */
function baseString(i) {
  return [
    i.payer_account_id,
    i.payee_ref,
    i.amount_minor,
    i.currency,
    i.reference || "",
    i.quote_id,
  ].join("");
}

function sign(instruction) {
  return crypto
    .createHmac("sha256", KEY)
    .update(baseString(instruction))
    .digest("hex");
}

function newQuoteId() {
  return crypto.randomBytes(12).toString("hex");
}

/*
 * Verify the signature over exactly what the client sent back, in constant
 * time, then check the quote has not been used before.
 */
function verify(instruction) {
  const expected = sign(instruction);
  const given = String(instruction.signature || "");
  if (given.length !== expected.length) return { ok: false, why: "bad signature" };
  if (!crypto.timingSafeEqual(Buffer.from(expected, "hex"), Buffer.from(given, "hex"))) {
    return { ok: false, why: "bad signature" };
  }

  if (SEEN_QUOTES.has(instruction.quote_id)) {
    return { ok: false, why: "this instruction has already been executed" };
  }
  return { ok: true };
}

function consume(quoteId) {
  SEEN_QUOTES.add(quoteId);
}

module.exports = { sign, verify, consume, newQuoteId, baseString };
