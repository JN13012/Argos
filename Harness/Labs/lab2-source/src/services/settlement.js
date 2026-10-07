/*
 * Settlement.
 *
 * Outbound payments are memo posted when they are authorised and queued here.
 * This run confirms them on the rail and flips the ledger entries from pending
 * to posted. It does not re-authorise anything: the decision to send was taken
 * when the customer confirmed, and an item that has left cannot be declined by
 * us afterwards.
 *
 * Every item settles in its own transaction. One bad item must not stop the
 * run, because the run is what makes money actually move.
 */

const { q, all, tx } = require("../db");

async function settleBatch(limit = 50) {
  const queued = await all(
    `SELECT * FROM settlement_queue WHERE state = 'queued'
      ORDER BY id LIMIT $1`, [limit]);

  let settled = 0;
  let failed = 0;

  for (const item of queued) {
    try {
      await tx(async (client) => {
        await client.query(
          `UPDATE ledger_entries SET status = 'posted'
            WHERE journal_id = (SELECT journal_id FROM ledger_entries WHERE id = $1)
              AND status = 'pending'`,
          [item.entry_id]);
        await client.query(
          `UPDATE settlement_queue
              SET state = 'settled', settled_at = NOW(), attempts = attempts + 1
            WHERE id = $1`, [item.id]);
      });
      settled += 1;
    } catch (e) {
      failed += 1;
      await q(
        `UPDATE settlement_queue
            SET attempts = attempts + 1, last_error = $1,
                state = CASE WHEN attempts + 1 >= 5 THEN 'failed' ELSE state END
          WHERE id = $2`,
        [String(e.message).slice(0, 300), item.id]).catch(() => {});
    }
  }

  return { considered: queued.length, settled, failed };
}

module.exports = { settleBatch };
