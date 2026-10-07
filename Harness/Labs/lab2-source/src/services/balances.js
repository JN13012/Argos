/*
 * Balances.
 *
 * Two of them, and they answer different questions.
 *
 *   postedBalance    what the ledger says has actually happened
 *   availableBalance what the customer may spend right now
 *
 * They differ by everything in flight: memo posted debits that have been
 * authorised but not settled, and holds placed by the card rails or by
 * operations. Reporting wants the first. Anything that authorises a debit
 * wants the second.
 */

const { one } = require("../db");

/* Settled movements only. Used by statements and end of day reconciliation. */
async function postedBalance(accountId, client) {
  const run = client ? client.query.bind(client) : null;
  const sql = `SELECT COALESCE(SUM(amount_minor), 0)::bigint AS total
                 FROM ledger_entries
                WHERE account_id = $1 AND status = 'posted'`;
  const row = run
    ? (await run(sql, [accountId])).rows[0]
    : await one(sql, [accountId]);
  return Number(row.total);
}

/*
 * Posted, less anything already committed, plus the agreed overdraft.
 * This is the number a debit has to fit inside.
 */
async function availableBalance(accountId, client) {
  const run = client ? client.query.bind(client) : null;
  const get = async (sql, params) =>
    run ? (await run(sql, params)).rows[0] : await one(sql, params);

  const posted = await get(
    `SELECT COALESCE(SUM(amount_minor), 0)::bigint AS total
       FROM ledger_entries WHERE account_id = $1 AND status = 'posted'`, [accountId]);
  const pending = await get(
    `SELECT COALESCE(SUM(amount_minor), 0)::bigint AS total
       FROM ledger_entries WHERE account_id = $1 AND status = 'pending'`, [accountId]);
  const held = await get(
    `SELECT COALESCE(SUM(amount_minor), 0)::bigint AS total
       FROM holds WHERE account_id = $1 AND released_at IS NULL`, [accountId]);
  const acct = await get(
    "SELECT overdraft_limit_minor FROM accounts WHERE id = $1", [accountId]);

  return Number(posted.total) + Number(pending.total)
       - Number(held.total) + Number(acct.overdraft_limit_minor);
}

/* How much of today's limit is left. */
async function remainingDailyLimit(accountId) {
  const acct = await one(
    "SELECT daily_limit_minor FROM accounts WHERE id = $1", [accountId]);
  const spent = await one(
    `SELECT COALESCE(SUM(-amount_minor), 0)::bigint AS total
       FROM ledger_entries
      WHERE account_id = $1 AND amount_minor < 0
        AND created_at::date = CURRENT_DATE`, [accountId]);
  return Number(acct.daily_limit_minor) - Number(spent.total);
}

module.exports = { postedBalance, availableBalance, remainingDailyLimit };
