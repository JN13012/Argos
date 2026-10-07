/*
 * Reference data and a populated test estate.
 *
 * Deterministic: a fixed seed PRNG and pinned ids, so every environment built
 * from this file is identical and a defect reproduces from a ticket number.
 *
 * Run: node db/seed.js > db/seed.sql
 */

const bcrypt = require("bcryptjs");

function rng(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = rng(20260401);
const pick = (a) => a[Math.floor(rand() * a.length)];
const int = (lo, hi) => lo + Math.floor(rand() * (hi - lo + 1));

const esc = (s) =>
  s === null || s === undefined ? "NULL" : `'${String(s).replace(/'/g, "''")}'`;
const num = (n) => (n === null || n === undefined ? "NULL" : n);

const HASH = {};
const hash = (pw) => (HASH[pw] ||= bcrypt.hashSync(pw, 8));

const out = [];
const w = (s) => out.push(s);

// --------------------------------------------------------------------------
// Currencies and rates
// --------------------------------------------------------------------------

w("-- currencies");
const CURRENCIES = [
  { code: "GBP", name: "Pound sterling", exponent: 2, symbol: "£" },
  { code: "USD", name: "US dollar", exponent: 2, symbol: "$" },
  { code: "EUR", name: "Euro", exponent: 2, symbol: "€" },
  { code: "JPY", name: "Japanese yen", exponent: 0, symbol: "¥" },
  { code: "KRW", name: "South Korean won", exponent: 0, symbol: "₩" },
];
for (const c of CURRENCIES) {
  w(`INSERT INTO currencies (code,name,exponent,symbol) VALUES (${esc(c.code)},${esc(c.name)},${c.exponent},${esc(c.symbol)});`);
}

w("\n-- fx rates");
const RATES = [
  ["USD", "GBP", 0.79], ["GBP", "USD", 1.2658],
  ["USD", "EUR", 0.92], ["EUR", "USD", 1.0870],
  ["USD", "JPY", 151.20], ["JPY", "USD", 0.006614],
  ["USD", "KRW", 1350.00], ["KRW", "USD", 0.00074074],
];
for (const [b, q2, r] of RATES) {
  w(`INSERT INTO fx_rates (base,quote,rate,as_of) VALUES (${esc(b)},${esc(q2)},${r},CURRENT_DATE);`);
}

// --------------------------------------------------------------------------
// People
// --------------------------------------------------------------------------

w("\n-- customers");
const STAFF = [
  { id: 1, email: "treasury@brayford.example", name: "Brayford Mutual Treasury", role: "admin", pw: "Treasury!2026" },
  { id: 2, email: "ops.desk@brayford.example", name: "Ada Whitlock", role: "ops", pw: "Operations!26" },
  { id: 3, email: "branch.teller@brayford.example", name: "Ronan Pike", role: "teller", pw: "Branch!2026" },
  { id: 4, email: "compliance@brayford.example", name: "Ingrid Soltau", role: "compliance", pw: "Comply!2026" },
];
for (const s of STAFF) {
  w(`INSERT INTO customers (id,email,password_hash,full_name,role,kyc_status) VALUES (${s.id},${esc(s.email)},${esc(hash(s.pw))},${esc(s.name)},${esc(s.role)},'verified');`);
}

// The retail customer the test estate is built around.
w(`INSERT INTO customers (id,email,password_hash,full_name,role,kyc_status) VALUES (10,'nell.harrow@example.com',${esc(hash("Harrow!2026"))},'Nell Harrow','customer','verified');`);

// Other retail customers. Their statements are what a broken scope returns.
const FIRST = ["Ivo","Marguerite","Sol","Bettina","Cassius","Odile","Rafferty","Juno",
  "Teodor","Wren","Anselm","Lisbeth","Caspar","Nadia","Emrys","Sylvie","Hugo","Perrine"];
const LAST = ["Mannering","Calloway","Fitzhugh","Okonjo","Vasari","Lindqvist","Abernathy",
  "Rasmussen","Delacroix","Yusuf","Bramwell","Nakagawa","Ostrowski","Haverford",
  "Quennell","Ibarra","Thorsby","Winslow"];
const retail = [];
for (let i = 0; i < 18; i++) {
  const id = 11 + i;
  const email = `${FIRST[i].toLowerCase()}.${LAST[i].toLowerCase()}@example.com`;
  retail.push({ id, name: `${FIRST[i]} ${LAST[i]}`, email });
  w(`INSERT INTO customers (id,email,password_hash,full_name,role,kyc_status) VALUES (${id},${esc(email)},${esc(hash("Customer!2026"))},${esc(FIRST[i] + " " + LAST[i])},'customer','verified');`);
}

// Two signatories on one company. Payments above the threshold need both.
w(`INSERT INTO customers (id,email,password_hash,full_name,role,organisation,kyc_status) VALUES (40,'p.eastwood@fenmoor.example',${esc(hash("Fenmoor!2026"))},'Piers Eastwood','business','Fenmoor Logistics Ltd','verified');`);
w(`INSERT INTO customers (id,email,password_hash,full_name,role,organisation,kyc_status) VALUES (41,'h.baptiste@fenmoor.example',${esc(hash("Fenmoor!2026"))},'Helena Baptiste','business','Fenmoor Logistics Ltd','verified');`);
w("SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));");

// --------------------------------------------------------------------------
// Accounts
// --------------------------------------------------------------------------

w("\n-- accounts");
// The bank's own accounts. Outbound payments rest against suspense until the
// rail settles them; provisional credits are funded from disputes suspense.
w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (1,1,'00000001','40-11-00','checking','USD',0,999999999);`);
w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (2,1,'00000002','40-11-00','checking','USD',0,999999999);`);

// Nell Harrow: a current account with an arranged overdraft, and savings.
w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (10,10,'20451187','40-11-23','checking','USD',50000,2000000);`);
w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (11,10,'20451188','40-11-23','savings','USD',0,2000000);`);

// Fenmoor Logistics, on the corporate channel.
w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (20,40,'31002914','40-11-77','business','USD',500000,50000000);`);

const retailAccounts = [];
retail.forEach((c, i) => {
  const id = 100 + i;
  retailAccounts.push({ id, customer: c.id, number: String(20500000 + i * 37) });
  w(`INSERT INTO accounts (id,customer_id,account_number,sort_code,kind,currency,overdraft_limit_minor,daily_limit_minor) VALUES (${id},${c.id},${esc(String(20500000 + i * 37))},'40-11-23','checking','USD',25000,1000000);`);
});
w("SELECT setval('accounts_id_seq', (SELECT MAX(id) FROM accounts));");

// --------------------------------------------------------------------------
// Opening balances
// --------------------------------------------------------------------------

w("\n-- opening positions");
let journalId = 1;
let entryId = 1;

function openingBalance(accountId, minor, currency, narrative) {
  w(`INSERT INTO journals (id,kind,narrative,created_by) VALUES (${journalId},'opening-balance',${esc(narrative)},1);`);
  w(`INSERT INTO ledger_entries (id,journal_id,account_id,amount_minor,currency,status,narrative,value_date) VALUES (${entryId++},${journalId},${accountId},${minor},${esc(currency)},'posted',${esc(narrative)},CURRENT_DATE - 60);`);
  w(`INSERT INTO ledger_entries (id,journal_id,account_id,amount_minor,currency,status,narrative,value_date) VALUES (${entryId++},${journalId},1,${-minor},${esc(currency)},'posted','Funding',CURRENT_DATE - 60);`);
  journalId += 1;
}

openingBalance(10, 240000, "USD", "Opening balance");
openingBalance(11, 1850000, "USD", "Opening balance");
openingBalance(20, 8400000, "USD", "Opening balance");
for (const a of retailAccounts) openingBalance(a.id, int(80000, 900000), "USD", "Opening balance");

// A little history so a statement is not empty.
const NARRATIVES = ["Card purchase", "Direct debit", "Standing order", "Salary",
  "ATM withdrawal", "Refund", "Transfer in", "Subscription"];
for (let i = 0; i < 160; i++) {
  const acct = pick([10, 11, 20, ...retailAccounts.map((a) => a.id)]);
  const amount = (rand() < 0.65 ? -1 : 1) * int(500, 24000);
  const nar = pick(NARRATIVES);
  w(`INSERT INTO journals (id,kind,narrative,created_by) VALUES (${journalId},'historic',${esc(nar)},1);`);
  w(`INSERT INTO ledger_entries (id,journal_id,account_id,amount_minor,currency,status,narrative,value_date) VALUES (${entryId++},${journalId},${acct},${amount},'USD','posted',${esc(nar)},CURRENT_DATE - ${int(1, 55)});`);
  w(`INSERT INTO ledger_entries (id,journal_id,account_id,amount_minor,currency,status,narrative,value_date) VALUES (${entryId++},${journalId},1,${-amount},'USD','posted',${esc(nar)},CURRENT_DATE - ${int(1, 55)});`);
  journalId += 1;
}
w("SELECT setval('journals_id_seq', (SELECT MAX(id) FROM journals));");
w("SELECT setval('ledger_entries_id_seq', (SELECT MAX(id) FROM ledger_entries));");

// --------------------------------------------------------------------------
// Holds
// --------------------------------------------------------------------------

w("\n-- holds");
w(`INSERT INTO holds (id,account_id,amount_minor,reason,placed_by) VALUES (1,10,15000,'Card authorisation, Ferrymead Garage',2);`);
w(`INSERT INTO holds (id,account_id,amount_minor,reason,placed_by) VALUES (2,20,120000,'Cheque clearing',2);`);
w(`INSERT INTO holds (id,account_id,amount_minor,reason,placed_by) VALUES (3,100,8000,'Card authorisation, Ashby Fuel',2);`);
w("SELECT setval('holds_id_seq', (SELECT MAX(id) FROM holds));");

// --------------------------------------------------------------------------
// Payees
//
// Fenmoor number their suppliers, so the codes share prefixes. The clearing
// formats key on these codes, which is why they are the customer's to set.
// --------------------------------------------------------------------------

w("\n-- payees");
const PAYEES = [
  { id: 1, customer: 10, ref: "RENT01", name: "Marlow Property", acct: "60114477", sort: "23-00-11" },
  { id: 2, customer: 10, ref: "ENERGY7", name: "Northfield Energy", acct: "60114512", sort: "23-00-11" },
  { id: 3, customer: 10, ref: "COUNCIL", name: "Brayford District Council", acct: "60118890", sort: "23-00-11" },
  { id: 4, customer: 40, ref: "SUPP1", name: "Kestrel Pallets", acct: "71220031", sort: "60-02-14" },
  { id: 5, customer: 40, ref: "SUPP12", name: "Kestrel Pallets (Midlands)", acct: "71220032", sort: "60-02-14" },
  { id: 6, customer: 40, ref: "SUPP1234", name: "Kestrel Pallets (Depot)", acct: "71220034", sort: "60-02-14" },
  { id: 7, customer: 40, ref: "FUEL22", name: "Ashby Fuel Cards", acct: "71330077", sort: "60-02-14" },
  { id: 8, customer: 40, ref: "HAULAGE9", name: "Redwing Haulage", acct: "71440015", sort: "60-02-14" },
];
for (const p of PAYEES) {
  w(`INSERT INTO payees (id,customer_id,payee_ref,display_name,account_number,sort_code) VALUES (${p.id},${p.customer},${esc(p.ref)},${esc(p.name)},${esc(p.acct)},${esc(p.sort)});`);
}
w("SELECT setval('payees_id_seq', (SELECT MAX(id) FROM payees));");

// --------------------------------------------------------------------------
// Card transactions
// --------------------------------------------------------------------------

w("\n-- card transactions");
const CARDS = [
  { id: 1, account: 10, merchant: "Ferrymead Garage", amount: 8450, cur: "USD", billing: 8450 },
  { id: 2, account: 10, merchant: "Colman & Sons Grocers", amount: 3215, cur: "USD", billing: 3215 },
  { id: 3, account: 10, merchant: "Haneda Airport Retail", amount: 15120, cur: "JPY", billing: 10000 },
  // Won is a zero decimal currency: 135,000 won is one hundred dollars.
  { id: 4, account: 10, merchant: "Seoul Station Duty Free", amount: 135000, cur: "KRW", billing: 10000 },
  { id: 5, account: 20, merchant: "Ashby Fuel Cards", amount: 42800, cur: "USD", billing: 42800 },
  { id: 6, account: 100, merchant: "Northfield Energy", amount: 6600, cur: "USD", billing: 6600 },
];
for (const c of CARDS) {
  w(`INSERT INTO card_transactions (id,account_id,merchant,amount_minor,currency,billing_amount_minor,billing_currency,posted_at) VALUES (${c.id},${c.account},${esc(c.merchant)},${c.amount},${esc(c.cur)},${c.billing},'USD',NOW() - INTERVAL '${int(2, 30)} days');`);
}
w("SELECT setval('card_transactions_id_seq', (SELECT MAX(id) FROM card_transactions));");

// --------------------------------------------------------------------------
// Statements
//
// customer_id is written by the new statement generator. Historic periods
// predate it and are backfilled in a later release.
// --------------------------------------------------------------------------

w("\n-- statements");
let stmtId = 1;
const allAccounts = [10, 11, 20, ...retailAccounts.map((a) => a.id)];
for (const acct of allAccounts) {
  for (let m = 3; m >= 1; m--) {
    w(`INSERT INTO statements (id,account_id,customer_id,period_start,period_end,opening_minor,closing_minor) VALUES (${stmtId++},${acct},NULL,date_trunc('month', CURRENT_DATE - INTERVAL '${m} months')::date,(date_trunc('month', CURRENT_DATE - INTERVAL '${m - 1} months') - INTERVAL '1 day')::date,${int(20000, 900000)},${int(20000, 900000)});`);
  }
}
w("SELECT setval('statements_id_seq', (SELECT MAX(id) FROM statements));");

// --------------------------------------------------------------------------
// Batch schedule
// --------------------------------------------------------------------------

w("\n-- scheduled jobs");
w(`INSERT INTO scheduled_jobs (id,name,task,env,enabled,created_by) VALUES (1,'Overnight settlement','settlement-run','{}'::jsonb,true,2);`);
w(`INSERT INTO scheduled_jobs (id,name,task,env,enabled,created_by) VALUES (2,'Savings interest accrual','interest-accrual','{"ANNUAL_RATE_BPS":"180"}'::jsonb,true,2);`);
w(`INSERT INTO scheduled_jobs (id,name,task,env,enabled,created_by) VALUES (3,'Notice account accrual','interest-accrual','{"ANNUAL_RATE_BPS":"265"}'::jsonb,true,2);`);
w(`INSERT INTO scheduled_jobs (id,name,task,env,enabled,created_by) VALUES (4,'Monthly statements','statement-run','{}'::jsonb,false,2);`);
w("SELECT setval('scheduled_jobs_id_seq', (SELECT MAX(id) FROM scheduled_jobs));");

// --------------------------------------------------------------------------
// Secure messages
// --------------------------------------------------------------------------

w("\n-- messages");
let msgId = 1;
const CIRCULARS = [
  ["Brayford Mutual", "Your statement for last month is ready",
   "Your statement is available in the Statements section of online banking. Paper copies are no longer posted by default; you can change that in your profile.", "statements"],
  ["Brayford Mutual", "Changes to our arranged overdraft rates",
   "From the start of next month the representative rate on arranged overdraft borrowing changes to 34.9% EAR variable. Your arranged limit is not changing. If you would like to reduce or remove your limit, contact us.", "rates"],
  ["Payments Operations", "Faster payments: settlement timings",
   "Outbound payments are memo posted to your account as soon as they are authorised and confirmed on the rail by the next settlement run. Until that run completes the payment shows as pending and the money is not available to spend.", "payments"],
  ["Brayford Mutual", "We are improving statement search",
   "Over the coming weeks we are moving historic statements onto the new search. Statements from before the move may take a little longer to open while we finish transferring them.", "service"],
  ["Fraud Operations", "Did you make this payment?",
   "We placed a temporary hold on a card authorisation at Ferrymead Garage while we checked it. No action is needed if this was you. Holds reduce the balance available to spend until they are released.", "fraud"],
  ["Brayford Mutual", "Your card is due for renewal",
   "A replacement debit card will be posted to your registered address within ten working days. Your card number and PIN are not changing.", "cards"],
];
for (let i = 0; i < CIRCULARS.length; i++) {
  const [sender, subject, body, category] = CIRCULARS[i];
  w(`INSERT INTO messages (id,customer_id,sender,subject,body,category,read_at,created_at) VALUES (${msgId++},10,${esc(sender)},${esc(subject)},${esc(body)},${esc(category)},${i > 2 ? "NOW()" : "NULL"},NOW() - INTERVAL '${(i + 1) * 4} days');`);
}
// Every customer gets the statement notice, so an inbox is never empty.
for (const c of retail) {
  w(`INSERT INTO messages (id,customer_id,sender,subject,body,category,created_at) VALUES (${msgId++},${c.id},'Brayford Mutual','Your statement for last month is ready','Your statement is available in the Statements section of online banking.','statements',NOW() - INTERVAL '6 days');`);
}
w(`INSERT INTO messages (id,customer_id,sender,subject,body,category,created_at) VALUES (${msgId++},40,'Corporate Channel','Bulk payment file format',${esc("Payment instructions raised in the corporate channel are quoted and then confirmed against the quote. Payees are keyed on the supplier code you set, which is what appears in the clearing file. Payments of $10,000 or more require a second signatory before they release.")},'payments',NOW() - INTERVAL '9 days');`);
w("SELECT setval('messages_id_seq', (SELECT MAX(id) FROM messages));");

// --------------------------------------------------------------------------
// Standing orders
// --------------------------------------------------------------------------

w("\n-- standing orders");
w(`INSERT INTO standing_orders (id,account_id,payee_id,amount_minor,frequency,next_run,reference,active) VALUES (1,10,1,95000,'monthly',date_trunc('month', CURRENT_DATE + INTERVAL '1 month')::date,'Rent',true);`);
w(`INSERT INTO standing_orders (id,account_id,payee_id,amount_minor,frequency,next_run,reference,active) VALUES (2,10,2,7400,'monthly',(CURRENT_DATE + INTERVAL '11 days')::date,'Energy',true);`);
w(`INSERT INTO standing_orders (id,account_id,payee_id,amount_minor,frequency,next_run,reference,active) VALUES (3,20,7,180000,'weekly',(CURRENT_DATE + INTERVAL '3 days')::date,'Fuel cards',true);`);
w("SELECT setval('standing_orders_id_seq', (SELECT MAX(id) FROM standing_orders));");

w("\n-- audit");
for (let i = 0; i < 40; i++) {
  w(`INSERT INTO audit_log (actor_id,action,detail) VALUES (${pick([1, 2, 3, 4])},${esc(pick(["signin", "hold.release", "job.run", "account.view", "payment.release"]))},'ok');`);
}

process.stdout.write(out.join("\n") + "\n");
