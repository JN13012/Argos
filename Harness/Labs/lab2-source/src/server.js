/*
 * Brayford Mutual core banking platform.
 */

const express = require("express");
const cookieParser = require("cookie-parser");
const path = require("path");
const { pool, q, one, all } = require("./db");
const { loadCustomer, requireCustomer } = require("./middleware/auth");
const { staffArea } = require("./middleware/staff-area");
const { settleBatch } = require("./services/settlement");
const { postedBalance, availableBalance } = require("./services/balances");
const { format } = require("./services/money");

const app = express();

// TLS terminates at the load balancer and plain HTTP is forwarded on.
app.set("trust proxy", 1);
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));
app.disable("x-powered-by");

app.use(express.urlencoded({ extended: true, limit: "1mb" }));
app.use(express.json({ limit: "1mb" }));
app.use(cookieParser());
app.use("/static", express.static(path.join(__dirname, "..", "public"), { index: false }));

app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "same-origin");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Cache-Control", "no-store");
  next();
});

app.use(loadCustomer);
app.use(staffArea);

// Unread count for the navigation, on every page a signed in customer sees.
app.use(async (req, res, next) => {
  res.locals.unread = 0;
  if (req.customer) {
    const row = await one(
      "SELECT COUNT(*)::int AS n FROM messages WHERE customer_id = $1 AND read_at IS NULL",
      [req.customer.id]).catch(() => null);
    res.locals.unread = row ? row.n : 0;
  }
  next();
});


app.get("/healthz", async (req, res) => {
  try {
    await one("SELECT 1 AS ok");
    res.json({ ok: true });
  } catch (e) {
    res.status(503).json({ ok: false });
  }
});

// --------------------------------------------------------------------------
// Pages
// --------------------------------------------------------------------------

app.get("/", (req, res) => {
  if (!req.customer) return res.redirect("/signin");
  res.redirect("/accounts");
});

app.get("/accounts", requireCustomer, async (req, res) => {
  const accounts = await all(
    `SELECT id, account_number, sort_code, kind, currency,
            overdraft_limit_minor, daily_limit_minor
       FROM accounts WHERE customer_id = $1 ORDER BY id`, [req.customer.id]);

  const view = [];
  for (const a of accounts) {
    view.push({
      ...a,
      posted_display: await format(await postedBalance(a.id), a.currency),
      available_display: await format(await availableBalance(a.id), a.currency),
      overdraft_display: await format(-a.overdraft_limit_minor, a.currency),
    });
  }
  res.render("accounts", { title: "Your accounts", accounts: view });
});

app.get("/accounts/:id", requireCustomer, async (req, res, next) => {
  const id = parseInt(req.params.id, 10);
  const account = await one(
    "SELECT * FROM accounts WHERE id = $1 AND customer_id = $2", [id, req.customer.id]);
  if (!account) return next();

  const entries = await all(
    `SELECT le.amount_minor, le.currency, le.status, le.narrative, le.value_date, j.kind
       FROM ledger_entries le JOIN journals j ON j.id = le.journal_id
      WHERE le.account_id = $1 ORDER BY le.id DESC LIMIT 60`, [id]);

  const rendered = [];
  for (const e of entries) {
    rendered.push({ ...e, display: await format(e.amount_minor, e.currency) });
  }

  res.render("account", {
    title: `Account ${account.account_number}`,
    account,
    posted_display: await format(await postedBalance(id), account.currency),
    available_display: await format(await availableBalance(id), account.currency),
    overdraft_display: await format(-account.overdraft_limit_minor, account.currency),
    entries: rendered,
  });
});



app.get("/move-money", requireCustomer, async (req, res) => {
  const accounts = await all(
    `SELECT id, account_number, kind, currency FROM accounts
      WHERE customer_id = $1 AND status = 'open' ORDER BY id`, [req.customer.id]);
  const payees = await all(
    `SELECT id, payee_ref, display_name, account_number, sort_code
       FROM payees WHERE customer_id = $1 ORDER BY display_name`, [req.customer.id]);
  const recent = await all(
    `SELECT j.kind, j.narrative, j.created_at, le.amount_minor, le.currency, le.status
       FROM journals j
       JOIN ledger_entries le ON le.journal_id = j.id
       JOIN accounts a ON a.id = le.account_id
      WHERE a.customer_id = $1 ORDER BY j.id DESC LIMIT 12`, [req.customer.id]);
  res.render("move-money", { title: "Move money", accounts, payees, recent });
});

app.get("/payments", requireCustomer, async (req, res) => {
  const accounts = await all(
    `SELECT id, account_number, kind, currency FROM accounts
      WHERE customer_id = $1 AND status = 'open' ORDER BY id`, [req.customer.id]);
  const billers = await all(
    `SELECT id, payee_ref, display_name, account_number, sort_code
       FROM payees WHERE customer_id = $1 ORDER BY display_name`, [req.customer.id]);
  res.render("billpay", { title: "Bill payments", accounts, billers });
});

app.get("/payees", requireCustomer, async (req, res) => {
  const payees = await all(
    `SELECT id, payee_ref, display_name, account_number, sort_code, created_at
       FROM payees WHERE customer_id = $1 ORDER BY payee_ref`, [req.customer.id]);
  res.render("payees", { title: "Payees", payees });
});

app.get("/standing-orders", requireCustomer, async (req, res) => {
  const orders = await all(
    `SELECT so.id, so.amount_minor, so.frequency, so.next_run, so.reference,
            so.active, p.display_name, p.payee_ref, a.account_number, a.currency
       FROM standing_orders so
       JOIN accounts a ON a.id = so.account_id
       JOIN payees p ON p.id = so.payee_id
      WHERE a.customer_id = $1 ORDER BY so.next_run`, [req.customer.id]);
  const rendered = [];
  for (const o of orders) {
    rendered.push({ ...o, display: await format(o.amount_minor, o.currency) });
  }
  res.render("standing-orders", { title: "Standing orders", orders: rendered });
});

app.get("/corporate", requireCustomer, async (req, res) => {
  const accounts = await all(
    `SELECT id, account_number, kind, currency FROM accounts
      WHERE customer_id = $1 AND status = 'open' ORDER BY id`, [req.customer.id]);
  const payees = await all(
    `SELECT id, payee_ref, display_name, account_number FROM payees
      WHERE customer_id = $1 ORDER BY payee_ref`, [req.customer.id]);
  const pending = await all(
    `SELECT p.id, p.payee_ref, p.amount_minor, p.currency, p.reference, p.status,
            c.full_name AS raised_by_name
       FROM payments p
       JOIN accounts a ON a.id = p.payer_account_id
       LEFT JOIN customers c ON c.id = p.raised_by
      WHERE a.customer_id = $1 AND p.status = 'awaiting_second_signature'
      ORDER BY p.id`, [req.customer.id]);
  const signatories = await all(
    `SELECT id, full_name FROM customers
      WHERE organisation IS NOT NULL AND organisation = $1 AND active = true
      ORDER BY id`, [req.customer.organisation || ""]);
  const history = await all(
    `SELECT p.id, p.payee_ref, p.amount_minor, p.currency, p.status, p.created_at
       FROM payments p JOIN accounts a ON a.id = p.payer_account_id
      WHERE a.customer_id = $1 ORDER BY p.id DESC LIMIT 15`, [req.customer.id]);
  res.render("corporate", {
    title: "Corporate payments", accounts, payees, pending, signatories, history,
  });
});

app.get("/cards", requireCustomer, async (req, res) => {
  const txns = await all(
    `SELECT ct.id, ct.merchant, ct.amount_minor, ct.currency,
            ct.billing_amount_minor, ct.billing_currency, ct.posted_at,
            a.account_number,
            (SELECT COUNT(*)::int FROM disputes d
              WHERE d.transaction_id = ct.id AND d.status = 'open') AS open_disputes
       FROM card_transactions ct
       JOIN accounts a ON a.id = ct.account_id
      WHERE a.customer_id = $1 ORDER BY ct.posted_at DESC`, [req.customer.id]);
  const rendered = [];
  for (const t of txns) {
    rendered.push({
      ...t,
      charged: await format(t.amount_minor, t.currency),
      billed: await format(t.billing_amount_minor, t.billing_currency),
    });
  }
  const disputes = await all(
    `SELECT d.id, d.reason, d.claimed_minor, d.status, d.created_at, ct.merchant
       FROM disputes d JOIN card_transactions ct ON ct.id = d.transaction_id
      WHERE d.raised_by = $1 ORDER BY d.id DESC`, [req.customer.id]);
  res.render("cards", { title: "Cards", txns: rendered, disputes });
});

app.get("/statements", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT s.id, s.period_start, s.period_end, s.closing_minor,
            a.account_number, a.currency
       FROM statements s JOIN accounts a ON a.id = s.account_id
      WHERE a.customer_id = $1 ORDER BY s.period_end DESC, a.account_number`,
    [req.customer.id]);
  res.render("statements", { title: "Statements", statements: rows });
});

app.get("/documents", requireCustomer, async (req, res) => {
  const docs = await all(
    `SELECT id, kind, original_name, byte_size, created_at
       FROM documents WHERE customer_id = $1 ORDER BY id DESC`, [req.customer.id]);
  res.render("documents", { title: "Documents", documents: docs });
});

app.get("/messages", requireCustomer, async (req, res) => {
  const messages = await all(
    `SELECT id, sender, subject, category, read_at, created_at
       FROM messages WHERE customer_id = $1 ORDER BY created_at DESC`,
    [req.customer.id]);
  res.render("messages", { title: "Messages", messages });
});

app.get("/messages/:id", requireCustomer, async (req, res, next) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return next();
  const message = await one(
    "SELECT * FROM messages WHERE id = $1 AND customer_id = $2", [id, req.customer.id]);
  if (!message) return next();
  await q("UPDATE messages SET read_at = COALESCE(read_at, NOW()) WHERE id = $1", [id]);
  res.render("message", { title: message.subject, message });
});

app.get("/profile", requireCustomer, async (req, res) => {
  const accounts = await all(
    "SELECT COUNT(*)::int AS n FROM accounts WHERE customer_id = $1", [req.customer.id]);
  res.render("profile", { title: "Profile", accounts: accounts[0].n });
});

app.get("/ops/jobs", requireCustomer, async (req, res) => {
  const jobs = await all(
    `SELECT j.*, (SELECT MAX(started_at) FROM job_runs r WHERE r.job_id = j.id) AS last_run
       FROM scheduled_jobs j ORDER BY j.id`);
  const runs = await all(
    `SELECT r.id, r.job_id, r.started_at, r.exit_code, r.output, j.name
       FROM job_runs r JOIN scheduled_jobs j ON j.id = r.job_id
      ORDER BY r.id DESC LIMIT 12`);
  const { availableTasks } = require("./jobs/runner");
  res.render("ops-jobs", { title: "Batch schedule", jobs, runs, tasks: availableTasks() });
});

app.get("/ops/customers", requireCustomer, async (req, res) => {
  const customers = await all(
    `SELECT c.id, c.email, c.full_name, c.role, c.organisation, c.kyc_status,
            (SELECT COUNT(*)::int FROM accounts a WHERE a.customer_id = c.id) AS accounts
       FROM customers c ORDER BY c.id LIMIT 200`);
  res.render("ops-customers", { title: "Customers", customers });
});

app.get("/ops", requireCustomer, async (req, res) => {
  const holds = await all(
    `SELECT h.id, h.account_id, h.amount_minor, h.reason, a.account_number
       FROM holds h JOIN accounts a ON a.id = h.account_id
      WHERE h.released_at IS NULL ORDER BY h.id LIMIT 40`);
  const jobs = await all("SELECT id, name, task, enabled FROM scheduled_jobs ORDER BY id");
  res.render("ops", { title: "Operations", holds, jobs });
});

// --------------------------------------------------------------------------
// API
// --------------------------------------------------------------------------

/*
 * Express 4 does not catch rejections from async handlers, and an uncaught one
 * leaves the request hanging rather than failing, so every router is wrapped.
 */
function catchAsync(router) {
  for (const layer of router.stack) {
    if (!layer.route) continue;
    for (const handler of layer.route.stack) {
      const fn = handler.handle;
      if (fn.length > 3) continue;
      handler.handle = function (req, res, next) {
        const out = fn.call(this, req, res, next);
        if (out && typeof out.catch === "function") out.catch(next);
      };
    }
  }
  return router;
}

app.use(catchAsync(require("./routes/auth")));
app.use(catchAsync(require("./routes/accounts")));
app.use(catchAsync(require("./routes/transfers")));
app.use(catchAsync(require("./routes/billpay")));
app.use(catchAsync(require("./routes/payments")));
app.use(catchAsync(require("./routes/disputes")));
app.use(catchAsync(require("./routes/documents")));
app.use(catchAsync(require("./routes/ops")));
app.use(catchAsync(require("./routes/jobs")));

app.use((req, res) => {
  if (req.path.startsWith("/api/")) return res.status(404).json({ error: "not found" });
  res.status(404).render("error", { code: 404, message: "Not found", title: "Not found" });
});

app.use((err, req, res, next) => {
  console.error(err && err.stack ? err.stack : err);
  if (req.path.startsWith("/api/")) return res.status(500).json({ error: "internal error" });
  res.status(500).render("error", { code: 500, message: "Something went wrong", title: "Error" });
});

process.on("unhandledRejection", (e) => console.error("unhandled rejection:", e));
process.on("uncaughtException", (e) => console.error("uncaught exception:", e));

// --------------------------------------------------------------------------
// Startup
// --------------------------------------------------------------------------

async function ensureSchema() {
  const fs = require("fs");
  for (let i = 0; i < 60; i++) {
    try { await one("SELECT 1 AS ok"); break; } catch (e) {
      if (i === 59) throw new Error("database never became reachable: " + e.message);
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
  const present = await one("SELECT to_regclass('public.customers') IS NOT NULL AS present")
    .catch(() => null);
  if (present && present.present) {
    const n = await one("SELECT COUNT(*)::int AS n FROM customers");
    if (n && n.n > 0) {
      console.log(`database already populated (${n.n} customers)`);
      return;
    }
  }
  const dir = path.join(__dirname, "..", "db");
  const started = Date.now();
  for (const file of ["schema.sql", "seed.sql"]) {
    await pool.query(fs.readFileSync(path.join(dir, file), "utf8"));
  }
  const n = await one("SELECT COUNT(*)::int AS n FROM accounts");
  console.log(`loaded ${n.n} accounts in ${Date.now() - started}ms`);
}

/*
 * The settlement run.
 *
 * Short interval on purpose: customers see an outbound payment as pending and
 * expect it to clear in minutes, not overnight.
 */
const SETTLEMENT_INTERVAL_MS = parseInt(process.env.SETTLEMENT_INTERVAL_MS || "30000", 10);

function startSettlement() {
  setInterval(() => {
    settleBatch(200)
      .then((r) => {
        if (r.settled || r.failed) {
          console.log(`settlement run: ${r.settled} settled, ${r.failed} failed`);
        }
      })
      .catch((e) => console.error("settlement run failed:", e.message));
  }, SETTLEMENT_INTERVAL_MS).unref();
}

const PORT = parseInt(process.env.PORT || "8080", 10);

ensureSchema()
  .catch((e) => console.error("startup:", e.message))
  .finally(() => {
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`Brayford Mutual listening on ${PORT}`);
      startSettlement();
    });
  });

module.exports = app;
