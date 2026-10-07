/*
 * Minor units.
 *
 * An amount is an integer of minor units plus the currency it is counted in.
 * How many minor units make a major unit depends on the currency: two for
 * sterling and dollars, none at all for yen. currencies.exponent carries it.
 *
 * Never use a float for money. The functions here take and return integers.
 */

const { one } = require("../db");

const EXPONENT_CACHE = new Map();

async function exponentOf(code) {
  if (EXPONENT_CACHE.has(code)) return EXPONENT_CACHE.get(code);
  const row = await one("SELECT exponent FROM currencies WHERE code = $1", [code]);
  const exp = row ? row.exponent : 2;
  EXPONENT_CACHE.set(code, exp);
  return exp;
}

/* Render minor units for a human, in the currency they belong to. */
async function format(minor, code) {
  const exp = await exponentOf(code);
  const sign = minor < 0 ? "-" : "";
  const abs = Math.abs(Number(minor));
  if (exp === 0) return `${sign}${abs.toLocaleString("en-GB")} ${code}`;
  const major = Math.floor(abs / 10 ** exp);
  const rest = String(abs % 10 ** exp).padStart(exp, "0");
  return `${sign}${major.toLocaleString("en-GB")}.${rest} ${code}`;
}

/*
 * Convert between currencies, taking both exponents into account. The rate
 * table is quoted in major units, so the exponents have to be unwound and
 * reapplied around it.
 */
async function convert(minor, from, to, rate) {
  if (from === to) return minor;
  const fromExp = await exponentOf(from);
  const toExp = await exponentOf(to);
  const major = Number(minor) / 10 ** fromExp;
  return Math.round(major * Number(rate) * 10 ** toExp);
}

module.exports = { exponentOf, format, convert };
