/*
 * Posting to the ledger.
 *
 * A journal is a set of entries that sum to zero. Nothing else may write to
 * ledger_entries; go through postJournal so the invariant holds and so every
 * movement has a narrative somebody can read back on a statement.
 */

const { tx } = require("../db");

/*
 * entries: [{ account_id, amount_minor, currency, status?, narrative? }]
 * The caller may pass an existing client to join an open transaction.
 */
async function postJournal({ kind, reference, narrative, created_by, entries }, client) {
  const sum = entries.reduce((n, e) => n + Number(e.amount_minor), 0);
  if (sum !== 0) {
    throw new Error(`journal does not balance: ${sum}`);
  }

  const run = async (c) => {
    const j = (await c.query(
      `INSERT INTO journals (kind, reference, narrative, created_by)
       VALUES ($1,$2,$3,$4) RETURNING id`,
      [kind, reference || null, narrative || null, created_by || null])).rows[0];

    const ids = [];
    for (const e of entries) {
      const row = (await c.query(
        `INSERT INTO ledger_entries
           (journal_id, account_id, amount_minor, currency, status, narrative)
         VALUES ($1,$2,$3,$4,$5,$6) RETURNING id`,
        [j.id, e.account_id, e.amount_minor, e.currency,
         e.status || "posted", e.narrative || narrative || null])).rows[0];
      ids.push(row.id);
    }
    return { journal_id: j.id, entry_ids: ids };
  };

  return client ? run(client) : tx(run);
}

module.exports = { postJournal };
