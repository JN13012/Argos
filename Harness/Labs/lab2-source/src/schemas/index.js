/*
 * Request shapes.
 *
 * Validation happens at the edge so the handlers can assume well formed input.
 * Anything not described here does not reach a handler.
 */

const { z } = require("zod");

/*
 * A payee code is the customer's own reference for a beneficiary. It is what
 * BACS and SEPA bulk files key on, so the charset follows those formats:
 * upper case letters and digits, between three and twelve characters. Suppliers
 * routinely number their codes, which is why digits are permitted.
 */
const payeeRef = z.string().regex(/^[A-Z0-9]{3,12}$/);

const accountNumber = z.string().regex(/^[0-9]{8}$/);
const sortCode = z.string().regex(/^[0-9]{2}-[0-9]{2}-[0-9]{2}$/);
const currency = z.string().regex(/^[A-Z]{3}$/);

/*
 * Amounts arrive as strings so that nothing is lost to JSON number handling
 * on the way in. The corporate channel sends scientific notation for large
 * values, so the character class has to accommodate it.
 */
const amountString = z.string().min(1).max(24).regex(/^[0-9eE.+-]+$/);

const createPayee = z.object({
  payee_ref: payeeRef,
  display_name: z.string().min(1).max(120),
  account_number: accountNumber,
  sort_code: sortCode,
});

const internalTransfer = z.object({
  from_account_id: z.coerce.number().int().positive(),
  to_account_id: z.coerce.number().int().positive(),
  amount: amountString,
  narrative: z.string().max(140).optional(),
});

const paymentPreview = z.object({
  payer_account_id: z.coerce.number().int().positive(),
  payee_ref: payeeRef,
  amount_minor: z.coerce.number().int().positive(),
  currency,
  reference: z.string().regex(/^[A-Za-z0-9 ._-]{0,35}$/).optional().default(""),
});

const paymentConfirm = z.object({
  instruction: z.object({
    payer_account_id: z.coerce.number().int().positive(),
    payee_ref: payeeRef,
    amount_minor: z.coerce.number().int().positive(),
    currency,
    reference: z.string().max(35).optional().default(""),
    quote_id: z.string().min(8).max(64),
    signature: z.string().regex(/^[0-9a-f]{64}$/),
  }),
});

const raiseDispute = z.object({
  transaction_id: z.coerce.number().int().positive(),
  reason: z.string().min(3).max(200),
  claimed_minor: z.coerce.number().int().positive(),
});

const scheduledJob = z.object({
  name: z.string().min(1).max(80),
  task: z.string().min(1).max(64),
  env: z.record(z.string().max(512)).optional().default({}),
});

module.exports = {
  payeeRef, accountNumber, sortCode, currency, amountString,
  createPayee, internalTransfer, paymentPreview, paymentConfirm,
  raiseDispute, scheduledJob,
};
