/* Settle everything queued on the outbound rails. */
const { settleBatch } = require("../services/settlement");
const { pool } = require("../db");

(async () => {
  const result = await settleBatch(500);
  console.log(`settlement: ${result.settled} settled, ${result.failed} failed, of ${result.considered}`);
  await pool.end();
})().catch((e) => {
  console.error("settlement failed:", e.message);
  process.exit(1);
});
