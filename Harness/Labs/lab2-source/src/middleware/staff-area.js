/*
 * Staff area gate.
 *
 * The operations console and the compliance console are mounted under their
 * own prefixes and neither is reachable by a customer. This runs before the
 * routers so that a route added to either console is protected the moment it
 * is written, rather than relying on whoever adds it to remember the guard.
 */

const { RANK } = require("./auth");

const AREAS = [
  { prefix: "/api/ops", min: "ops" },
  { prefix: "/ops", min: "ops" },
];

function staffArea(req, res, next) {
  const area = AREAS.find((a) => req.path.startsWith(a.prefix));
  if (!area) return next();

  if (!req.customer) return res.status(401).json({ error: "not signed in" });
  if ((RANK[req.customer.role] || 0) < RANK[area.min]) {
    return res.status(403).json({ error: "staff only" });
  }
  next();
}

module.exports = { staffArea };
