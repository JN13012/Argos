/*
 * Database access.
 *
 * Every statement in this codebase is parameterised. If you find yourself
 * wanting to build SQL by concatenation, add a column instead.
 */

const { Pool } = require("pg");

const pool = new Pool({
  host: process.env.DB_HOST || "127.0.0.1",
  port: parseInt(process.env.DB_PORT || "5432", 10),
  user: process.env.DB_USER || "brayford",
  password: process.env.DB_PASSWORD || "brayford",
  database: process.env.DB_NAME || "brayford",
  max: 12,
});

const q = (text, params) => pool.query(text, params);
const one = async (text, params) => (await pool.query(text, params)).rows[0] || null;
const all = async (text, params) => (await pool.query(text, params)).rows;

/*
 * Run fn inside a transaction on a dedicated client. Anything fn does must go
 * through the client it is handed, or it will run on a different connection
 * and outside the transaction.
 */
async function tx(fn) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await fn(client);
    await client.query("COMMIT");
    return result;
  } catch (e) {
    await client.query("ROLLBACK").catch(() => {});
    throw e;
  } finally {
    client.release();
  }
}

module.exports = { pool, q, one, all, tx };
