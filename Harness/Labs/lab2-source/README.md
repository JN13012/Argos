# Brayford Mutual

Core banking platform. Retail current and savings accounts, a corporate
payment channel, card disputes, and the back office tooling that supports them.

## Running it

```bash
docker compose up -d db
npm install
node db/seed.js > db/seed.sql
DB_PORT=55434 PORT=3200 INSTRUCTION_SIGNING_KEY=dev-only node src/server.js
```

Schema and fixtures load on first start. The platform listens on `$PORT` and
answers `/healthz`.

## Architecture

```
src/
  server.js              wiring, pages, startup, the settlement timer
  db.js                  pool, query helpers, tx()
  middleware/
    auth.js              sessions and role ranks
    staff-area.js        the gate in front of the staff consoles
  services/
    money.js             minor units, currency exponents, conversion
    balances.js          posted, available, remaining daily limit
    ledger.js            postJournal, the only writer of ledger_entries
    instructions.js      signing and verification for the corporate channel
    settlement.js        the outbound settlement run
  routes/
    auth.js accounts.js transfers.js billpay.js payments.js
    disputes.js documents.js ops.js jobs.js
  jobs/
    runner.js            starts a task as its own process
    settlement-run.js interest-accrual.js statement-run.js
  schemas/index.js       request shapes
db/
  schema.sql             tables, and the notes on what each one is for
  seed.js                deterministic reference data and test estate
```

## Concepts worth reading first

**Money is integer minor units plus a currency.** How many minor units make a
major unit varies: two for sterling and dollars, none for yen or won.
`currencies.exponent` carries it and `services/money.js` is the only place that
should be doing arithmetic across currencies.

**The ledger is double entry.** A journal is a set of entries summing to zero.
`services/ledger.js` `postJournal` is the only writer; balances are derived,
never stored.

**Posted is not available.** `postedBalance` is what has settled.
`availableBalance` also nets off memo posted debits and card holds and adds the
arranged overdraft. Reporting wants the first; anything authorising a debit
wants the second.

**Outbound payments settle asynchronously.** They are memo posted when
authorised, queued in `settlement_queue`, and confirmed by the settlement run
every 30 seconds.

## Test accounts

Every role, as you would be given on an engagement.

| role | email | password |
|---|---|---|
| retail customer | nell.harrow@example.com | `Harrow!2026` |
| retail customer | ivo.mannering@example.com | `Customer!2026` |
| business signatory | p.eastwood@fenmoor.example | `Fenmoor!2026` |
| business signatory | h.baptiste@fenmoor.example | `Fenmoor!2026` |
| branch teller | branch.teller@brayford.example | `Branch!2026` |
| operations | ops.desk@brayford.example | `Operations!26` |
| compliance | compliance@brayford.example | `Comply!2026` |
| admin | treasury@brayford.example | `Treasury!2026` |

Nell Harrow holds account 10 (current, with a $500 arranged overdraft) and
account 11 (savings). Fenmoor Logistics holds account 20 on the corporate
channel, where payments of $10,000 or more need a second signature.

## If you break it

Stop and restart the lab from your dashboard. The container is disposable and
the database is rebuilt from `db/` on every start, so a restart restores the
estate exactly as it began. Nothing you do to the money is permanent.
