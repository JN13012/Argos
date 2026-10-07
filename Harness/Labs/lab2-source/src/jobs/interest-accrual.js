/* Accrue credit interest on savings accounts and report what it would post. */
const { all, pool } = require("../db");

(async () => {
  const accounts = await all(
    "SELECT id, account_number, currency FROM accounts WHERE kind = 'savings' AND status = 'open'");
  const rate = parseFloat(process.env.ANNUAL_RATE_BPS || "180") / 10000;
  console.log(`interest accrual over ${accounts.length} savings accounts at ${(rate * 100).toFixed(2)}%`);
  for (const a of accounts) {
    console.log(`  ${a.account_number} ${a.currency}`);
  }
  await pool.end();
})().catch((e) => {
  console.error("accrual failed:", e.message);
  process.exit(1);
});
