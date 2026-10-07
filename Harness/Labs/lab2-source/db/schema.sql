-- Brayford Mutual core banking schema.
--
-- Money is always integer minor units in the currency named alongside it.
-- The number of minor units in a major unit varies by currency and is held in
-- currencies.exponent, so an amount is only meaningful together with its
-- currency code. Nothing in this schema stores a float.
--
-- The ledger is double entry. Every movement is a journal with two or more
-- entries that sum to zero. Balances are derived from entries and are never
-- stored on the account.

DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- --------------------------------------------------------------------------
-- Reference data
-- --------------------------------------------------------------------------

CREATE TABLE currencies (
  code      TEXT PRIMARY KEY,
  name      TEXT NOT NULL,
  -- Minor units per major unit, as a power of ten. USD and GBP are 2.
  -- JPY and KRW are 0: there is no such thing as a fractional yen.
  exponent  SMALLINT NOT NULL,
  symbol    TEXT
);

CREATE TABLE fx_rates (
  base      TEXT NOT NULL REFERENCES currencies(code),
  quote     TEXT NOT NULL REFERENCES currencies(code),
  -- Units of quote per one unit of base, both expressed in MAJOR units.
  rate      NUMERIC(18,8) NOT NULL,
  as_of     DATE NOT NULL,
  PRIMARY KEY (base, quote, as_of)
);

-- --------------------------------------------------------------------------
-- People
-- --------------------------------------------------------------------------

CREATE TABLE customers (
  id             SERIAL PRIMARY KEY,
  email          TEXT UNIQUE NOT NULL,
  password_hash  TEXT NOT NULL,
  full_name      TEXT NOT NULL,
  -- customer | business | teller | ops | compliance | admin
  role           TEXT NOT NULL DEFAULT 'customer',
  -- Business customers can raise payments that need a second signature.
  organisation   TEXT,
  kyc_status     TEXT NOT NULL DEFAULT 'verified',
  active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Accounts and the ledger
-- --------------------------------------------------------------------------

CREATE TABLE accounts (
  id                  SERIAL PRIMARY KEY,
  customer_id         INTEGER NOT NULL REFERENCES customers(id),
  account_number      TEXT UNIQUE NOT NULL,
  sort_code           TEXT NOT NULL,
  -- checking | savings | business
  kind                TEXT NOT NULL DEFAULT 'checking',
  -- The currency this account is denominated and billed in.
  currency            TEXT NOT NULL REFERENCES currencies(code),
  -- How far below zero the account is permitted to go, in this account's
  -- minor units. Enforced by the funds availability check, not by the
  -- database, because operations occasionally have to post past it.
  overdraft_limit_minor INTEGER NOT NULL DEFAULT 0,
  daily_limit_minor   INTEGER NOT NULL DEFAULT 500000,
  status              TEXT NOT NULL DEFAULT 'open',
  opened_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE journals (
  id          SERIAL PRIMARY KEY,
  kind        TEXT NOT NULL,
  reference   TEXT,
  narrative   TEXT,
  created_by  INTEGER REFERENCES customers(id),
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ledger_entries (
  id            SERIAL PRIMARY KEY,
  journal_id    INTEGER NOT NULL REFERENCES journals(id),
  account_id    INTEGER NOT NULL REFERENCES accounts(id),
  -- Signed. Debits are negative, credits positive. Entries of one journal
  -- sum to zero within a currency.
  amount_minor  BIGINT NOT NULL,
  currency      TEXT NOT NULL REFERENCES currencies(code),
  -- pending entries are memo posted: authorised and not yet settled.
  status        TEXT NOT NULL DEFAULT 'posted',
  narrative     TEXT,
  value_date    DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at    TIMESTAMP DEFAULT NOW()
);

-- Card authorisations and cheque holds reduce what is available without
-- being ledger entries at all.
CREATE TABLE holds (
  id            SERIAL PRIMARY KEY,
  account_id    INTEGER NOT NULL REFERENCES accounts(id),
  amount_minor  BIGINT NOT NULL,
  reason        TEXT,
  placed_by     INTEGER REFERENCES customers(id),
  released_at   TIMESTAMP,
  created_at    TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Moving money
-- --------------------------------------------------------------------------

-- A payee is scoped to the customer who created it. payee_ref is the code the
-- customer knows it by and is what bulk files key on, so it is theirs to
-- choose within a charset the clearing formats accept.
CREATE TABLE payees (
  id             SERIAL PRIMARY KEY,
  customer_id    INTEGER NOT NULL REFERENCES customers(id),
  payee_ref      TEXT NOT NULL,
  display_name   TEXT NOT NULL,
  account_number TEXT NOT NULL,
  sort_code      TEXT NOT NULL,
  created_at     TIMESTAMP DEFAULT NOW(),
  UNIQUE (customer_id, payee_ref)
);

CREATE TABLE payments (
  id                SERIAL PRIMARY KEY,
  payer_account_id  INTEGER NOT NULL REFERENCES accounts(id),
  payee_id          INTEGER REFERENCES payees(id),
  payee_ref         TEXT,
  amount_minor      BIGINT NOT NULL,
  currency          TEXT NOT NULL REFERENCES currencies(code),
  reference         TEXT,
  -- draft | awaiting_second_signature | released | posted | rejected
  status            TEXT NOT NULL DEFAULT 'draft',
  raised_by         INTEGER REFERENCES customers(id),
  approved_by       INTEGER REFERENCES customers(id),
  journal_id        INTEGER REFERENCES journals(id),
  created_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payment_approvals (
  id          SERIAL PRIMARY KEY,
  payment_id  INTEGER NOT NULL REFERENCES payments(id),
  approver_id INTEGER NOT NULL REFERENCES customers(id),
  created_at  TIMESTAMP DEFAULT NOW()
);

-- Outbound instructions that have been authorised and not yet settled.
CREATE TABLE settlement_queue (
  id            SERIAL PRIMARY KEY,
  account_id    INTEGER NOT NULL REFERENCES accounts(id),
  entry_id      INTEGER REFERENCES ledger_entries(id),
  amount_minor  BIGINT NOT NULL,
  rail          TEXT NOT NULL,
  -- queued | settled | failed
  state         TEXT NOT NULL DEFAULT 'queued',
  attempts      INTEGER NOT NULL DEFAULT 0,
  last_error    TEXT,
  created_at    TIMESTAMP DEFAULT NOW(),
  settled_at    TIMESTAMP
);

-- --------------------------------------------------------------------------
-- Card transactions and disputes
-- --------------------------------------------------------------------------

CREATE TABLE card_transactions (
  id                   SERIAL PRIMARY KEY,
  account_id           INTEGER NOT NULL REFERENCES accounts(id),
  merchant             TEXT NOT NULL,
  -- What the merchant charged, in the merchant's own currency.
  amount_minor         BIGINT NOT NULL,
  currency             TEXT NOT NULL REFERENCES currencies(code),
  -- What it settled at against this account, in the account's currency.
  billing_amount_minor BIGINT NOT NULL,
  billing_currency     TEXT NOT NULL REFERENCES currencies(code),
  entry_id             INTEGER REFERENCES ledger_entries(id),
  posted_at            TIMESTAMP DEFAULT NOW()
);

CREATE TABLE disputes (
  id                 SERIAL PRIMARY KEY,
  transaction_id     INTEGER NOT NULL REFERENCES card_transactions(id),
  raised_by          INTEGER NOT NULL REFERENCES customers(id),
  reason             TEXT NOT NULL,
  claimed_minor      BIGINT NOT NULL,
  provisional_credit_minor BIGINT,
  journal_id         INTEGER REFERENCES journals(id),
  status             TEXT NOT NULL DEFAULT 'open',
  created_at         TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Statements
-- --------------------------------------------------------------------------

CREATE TABLE statements (
  id             SERIAL PRIMARY KEY,
  account_id     INTEGER NOT NULL REFERENCES accounts(id),
  -- Denormalised for the new statement search, which filters by customer
  -- before it joins. Backfill runs with the next release.
  customer_id    INTEGER REFERENCES customers(id),
  period_start   DATE NOT NULL,
  period_end     DATE NOT NULL,
  opening_minor  BIGINT NOT NULL,
  closing_minor  BIGINT NOT NULL,
  created_at     TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Batch scheduler
-- --------------------------------------------------------------------------

CREATE TABLE scheduled_jobs (
  id            SERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  -- Names a script in src/jobs. The runner will not run anything else.
  task          TEXT NOT NULL,
  -- Per job overrides handed to the task process.
  env           JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled       BOOLEAN NOT NULL DEFAULT TRUE,
  created_by    INTEGER REFERENCES customers(id),
  created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE job_runs (
  id          SERIAL PRIMARY KEY,
  job_id      INTEGER NOT NULL REFERENCES scheduled_jobs(id),
  started_at  TIMESTAMP DEFAULT NOW(),
  finished_at TIMESTAMP,
  exit_code   INTEGER,
  output      TEXT,
  started_by  INTEGER REFERENCES customers(id)
);

-- --------------------------------------------------------------------------
-- Documents
-- --------------------------------------------------------------------------

CREATE TABLE documents (
  id            SERIAL PRIMARY KEY,
  customer_id   INTEGER NOT NULL REFERENCES customers(id),
  kind          TEXT NOT NULL,
  original_name TEXT NOT NULL,
  stored_path   TEXT NOT NULL,
  byte_size     INTEGER NOT NULL,
  created_at    TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Secure messaging
--
-- Regulated correspondence: statements ready, rate changes, fraud queries.
-- Kept in the app rather than sent by email, because none of it should be
-- readable from a mailbox.
-- --------------------------------------------------------------------------

CREATE TABLE messages (
  id          SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  sender      TEXT NOT NULL,
  subject     TEXT NOT NULL,
  body        TEXT NOT NULL,
  category    TEXT NOT NULL DEFAULT 'general',
  read_at     TIMESTAMP,
  created_at  TIMESTAMP DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- Standing orders
-- --------------------------------------------------------------------------

CREATE TABLE standing_orders (
  id           SERIAL PRIMARY KEY,
  account_id   INTEGER NOT NULL REFERENCES accounts(id),
  payee_id     INTEGER NOT NULL REFERENCES payees(id),
  amount_minor BIGINT NOT NULL,
  frequency    TEXT NOT NULL DEFAULT 'monthly',
  next_run     DATE NOT NULL,
  reference    TEXT,
  active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_log (
  id          SERIAL PRIMARY KEY,
  actor_id    INTEGER,
  action      TEXT NOT NULL,
  detail      TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON ledger_entries(account_id, status);
CREATE INDEX ON ledger_entries(journal_id);
CREATE INDEX ON holds(account_id) WHERE released_at IS NULL;
CREATE INDEX ON accounts(customer_id);
CREATE INDEX ON payees(customer_id);
CREATE INDEX ON card_transactions(account_id);
CREATE INDEX ON statements(account_id);
CREATE INDEX ON messages(customer_id);
CREATE INDEX ON standing_orders(account_id);
