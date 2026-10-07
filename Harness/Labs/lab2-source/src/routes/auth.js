/*
 * Signing in.
 */

const express = require("express");
const bcrypt = require("bcryptjs");
const { one, q } = require("../db");
const { issue, destroy, requireCustomer } = require("../middleware/auth");

const router = express.Router();

const ATTEMPTS = new Map();
const WINDOW_MS = 60000;
const MAX_ATTEMPTS = 30;

function throttled(ip) {
  const now = Date.now();
  const b = ATTEMPTS.get(ip);
  if (!b || now > b.reset) {
    ATTEMPTS.set(ip, { n: 1, reset: now + WINDOW_MS });
    return false;
  }
  b.n += 1;
  return b.n > MAX_ATTEMPTS;
}

router.get("/signin", (req, res) =>
  res.render("signin", { title: "Sign in", error: null, next: req.query.next || "/" }));

router.post("/signin", async (req, res) => {
  if (throttled(req.ip)) {
    return res.status(429).render("signin", {
      title: "Sign in", error: "Too many attempts. Try again shortly.", next: "/",
    });
  }

  const email = String(req.body.email || "").trim().toLowerCase();
  const password = String(req.body.password || "");
  const customer = await one(
    "SELECT * FROM customers WHERE lower(email) = $1 AND active = true", [email]);

  const hash = customer ? customer.password_hash
    : "$2a$08$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalidin";
  const ok = bcrypt.compareSync(password, hash);

  if (!customer || !ok) {
    return res.status(401).render("signin", {
      title: "Sign in", error: "Those details do not match an account.", next: "/",
    });
  }

  res.cookie("bry_session", issue(customer.id), {
    httpOnly: true, sameSite: "lax", secure: true, maxAge: 12 * 3600 * 1000,
  });
  const next = String(req.body.next || "/");
  res.redirect(next.startsWith("/") && !next.startsWith("//") ? next : "/");
});

router.post("/api/signin", async (req, res) => {
  if (throttled(req.ip)) return res.status(429).json({ error: "too many attempts" });
  const email = String(req.body.email || "").trim().toLowerCase();
  const password = String(req.body.password || "");
  const customer = await one(
    "SELECT * FROM customers WHERE lower(email) = $1 AND active = true", [email]);
  const hash = customer ? customer.password_hash
    : "$2a$08$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalidin";
  if (!customer || !bcrypt.compareSync(password, hash)) {
    return res.status(401).json({ error: "those details do not match an account" });
  }
  res.cookie("bry_session", issue(customer.id), {
    httpOnly: true, sameSite: "lax", secure: true, maxAge: 12 * 3600 * 1000,
  });
  res.json({ ok: true, customer: { id: customer.id, full_name: customer.full_name, role: customer.role } });
});

router.get("/signout", (req, res) => {
  if (req.cookies.bry_session) destroy(req.cookies.bry_session);
  res.clearCookie("bry_session");
  res.redirect("/signin");
});

router.get("/api/me", requireCustomer, async (req, res) => {
  res.json({
    id: req.customer.id, email: req.customer.email, full_name: req.customer.full_name,
    role: req.customer.role, organisation: req.customer.organisation,
    kyc_status: req.customer.kyc_status,
  });
});

module.exports = router;
