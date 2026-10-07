/*
 * Sessions and roles.
 *
 * The session cookie carries a random identifier and nothing else; everything
 * about the customer is read from the database on each request, so a change to
 * someone's role or status takes effect immediately rather than at their next
 * sign in.
 */

const crypto = require("crypto");
const { one } = require("../db");

const SESSIONS = new Map();
const TTL_MS = 12 * 3600 * 1000;

const RANK = { customer: 1, business: 1, teller: 2, ops: 3, compliance: 4, admin: 5 };

function issue(customerId) {
  const sid = crypto.randomBytes(24).toString("base64url");
  SESSIONS.set(sid, { customerId, expires: Date.now() + TTL_MS });
  return sid;
}

function destroy(sid) {
  SESSIONS.delete(sid);
}

async function loadCustomer(req, res, next) {
  req.customer = null;
  const sid = req.cookies.bry_session;
  if (sid) {
    const s = SESSIONS.get(sid);
    if (s && s.expires > Date.now()) {
      req.customer = await one(
        "SELECT * FROM customers WHERE id = $1 AND active = true", [s.customerId]);
    } else if (s) {
      SESSIONS.delete(sid);
    }
  }
  res.locals.customer = req.customer;
  next();
}

const requireCustomer = (req, res, next) => {
  if (!req.customer) {
    if (req.path.startsWith("/api/")) return res.status(401).json({ error: "not signed in" });
    return res.redirect("/signin?next=" + encodeURIComponent(req.originalUrl));
  }
  next();
};

const requireRole = (min) => (req, res, next) => {
  if (!req.customer) return res.status(401).json({ error: "not signed in" });
  if ((RANK[req.customer.role] || 0) < RANK[min]) {
    return res.status(403).json({ error: "insufficient privileges" });
  }
  next();
};

module.exports = { issue, destroy, loadCustomer, requireCustomer, requireRole, RANK };
