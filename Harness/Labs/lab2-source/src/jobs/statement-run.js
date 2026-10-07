/* Generate statements for the period that has just closed. */
const { all, pool } = require("../db");

(async () => {
  const accounts = await all("SELECT id, account_number FROM accounts WHERE status = 'open'");
  console.log(`statement run: ${accounts.length} accounts in scope`);
  await pool.end();
})().catch((e) => {
  console.error("statement run failed:", e.message);
  process.exit(1);
});
