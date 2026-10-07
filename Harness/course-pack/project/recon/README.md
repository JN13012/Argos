# The recon store

## The problem

Recon produces more output than an agent can hold. The published failure is specific: a run
enumerating over 30,000 subdomains filled its context before it ever reached analysis, and a
200 endpoint API map read back as a file evicts the plan by exactly the same mechanism. The
fix is not a smaller scan. It is to stop putting the map in the context window at all. Recon
writes rows into SQLite, and every later pass asks a question instead of reading a file:
aggregates first to learn the shape of the surface, then a filtered page of the handful of
rows it actually needs. The database is opened in WAL mode so the summariser and the class
subagents can read while a scan is still writing, and every tool takes an explicit `scan_id`,
because agents get implicit "most recent" state wrong and a cross run mixup is almost
invisible once it reaches a report.

## API

```python
import store
```

### `summarize_assets(scan_id, db=None)`

Aggregate counts only. Never returns a row. This is the tool that keeps a 200 endpoint map
out of the context window, and it is the one people skip.

Returns `total_assets`, `by_method`, `by_status`, `by_host`, `distinct_hosts`,
`hosts_not_shown`, `takes_object_id` and `authenticated`. `by_host` is capped at the top
`TOP_N` hosts (15) with the remainder counted in `hosts_not_shown`, because a `by_host` dict
with 30,000 keys is the problem we came here to avoid.

### `query_assets(scan_id, filter=None, cursor=None, limit=50, db=None)`

One page of matching rows, plus `next_cursor` for the following page. Also exported as
`list_assets`, which is the name on the slide.

Returns `{"rows": [...], "page_size": n, "has_more": bool, "next_cursor": str or None}`.
Pass `next_cursor` back as `cursor`. A cursor is opaque and pinned to its `scan_id`, so a
cursor from one run cannot silently page through another.

`limit` is clamped to `MAX_PAGE` (200) and the published tool schema does not expose it at
all. The harness sets the page size, not the model.

### `record_asset(scan_id, host, method, path, params=None, takes_object_id=False, status=None, authenticated=False, notes=None, db=None)`

Upsert, keyed on `(scan_id, host, method, path)`. Re-recording an endpoint refines it rather
than duplicating it, and a `status` or `notes` of `None` leaves the stored value alone, so a
second observation cannot blank out the first.

### `TOOL_SCHEMAS`

The three tools in OpenAI function calling shape, ready to drop into `harness/agent.py`.

## The filter language

Not string interpolated SQL. `parse_filter()` tokenises the expression, walks a small
grammar, emits a parameterised SQL fragment with a bound parameter list, and raises
`FilterError` on anything it does not recognise. Nothing from the agent reaches SQLite as
text.

```
<field> <op> <value>, combined with and / or / not and parentheses
```

| Fields | Type | Operators |
|---|---|---|
| `hostname` (alias `host`), `method`, `path`, `params`, `notes` | text | `=` `!=` `contains` `matches` `in` |
| `status` | int | `=` `!=` `>` `<` `>=` `<=` `in` |
| `takes_object_id`, `authenticated` | bool | `=` `!=` |

`matches` takes a `/regex/` literal, compiled by Python's `re` with no implicit flags. Write
`/(?i)staging/` if you want it case insensitive. `contains` is a `LIKE` with `%` and `_`
escaped, so a literal percent sign in the value stays literal. `params` is stored as JSON
text, so `params contains "id"` matches on that text.

Everything else is rejected with a message that says why:

```
"path = 'x' OR 1=1 --"          -> cannot parse filter at position 18: '--'
"path = 'x'; DROP TABLE assets" -> cannot parse filter at position 10: '; DROP TABLE assets'
"secret_column = 'x'"           -> unknown field 'secret_column'. Known fields: ...
"status contains '200'"         -> operator 'contains' is not allowed on status. Allowed: ...
"hostname matches /unclosed(/"  -> bad regex 'unclosed(': missing ), unterminated subpattern
```

## Worked example: twelve rows instead of two hundred

A scan named `lab-02` holding 200 endpoints across 10 hosts. Reading that map back as a file
costs 200 rows of context. Here is what the agent does instead.

**Step one, the shape of the surface. No rows.**

```python
store.summarize_assets("lab-02")
```

```json
{
  "scan_id": "lab-02",
  "total_assets": 200,
  "by_method": {"GET": 102, "POST": 49, "PUT": 48, "DELETE": 1},
  "by_status": {"200": 81, "403": 44, "401": 42, "201": 33},
  "by_host": {
    "api.shop.lab": 68, "admin.shop.lab": 40, "cdn.shop.lab": 40, "www.shop.lab": 40,
    "staging.shop.lab": 3, "dev-api.shop.lab": 2, "dev.shop.lab": 2, "qa.shop.lab": 2,
    "staging-api.shop.lab": 2, "qa2.shop.lab": 1
  },
  "distinct_hosts": 10,
  "hosts_not_shown": 0,
  "takes_object_id": 102,
  "authenticated": 133
}
```

That is the whole 200 endpoint surface in about 20 lines, and it is enough to pick a target:
six of the ten hosts are non production.

**Step two, ask for those rows and only those rows.**

```python
store.query_assets("lab-02", filter="hostname matches /staging|dev|qa/")
```

```
GET    staging.shop.lab      /api/v1/users/{id}          oid=True
GET    staging.shop.lab      /api/v1/debug/config        oid=False
PUT    staging.shop.lab      /api/v1/users/{id}          oid=True
GET    staging-api.shop.lab  /api/v1/orders/{id}         oid=True
POST   staging-api.shop.lab  /api/v1/orders/{id}/refund  oid=True
GET    dev.shop.lab          /api/v1/internal/keys       oid=False
GET    dev.shop.lab          /api/v1/users/{id}/token    oid=True
GET    dev-api.shop.lab      /api/v1/invoices/{id}       oid=True
DELETE dev-api.shop.lab      /api/v1/invoices/{id}       oid=True
GET    qa.shop.lab           /api/v1/carts/{id}          oid=True
GET    qa.shop.lab           /api/v1/debug/env           oid=False
POST   qa2.shop.lab          /api/v1/tickets             oid=False

12 rows returned out of 200 in the store, next_cursor: None
```

Twelve rows. A file read would have been two hundred, and the aggregate that chose those
twelve cost twenty lines.

Narrow it further the same way. The BOLA surface on those hosts is one more filter:

```python
store.query_assets(
    "lab-02",
    filter='hostname matches /staging|dev|qa/ and takes_object_id = true '
           'and method in ("GET", "PUT")')
```

## Paging

`next_cursor` is `None` on the last page. The loop is always the same shape:

```python
cursor = None
while True:
    page = store.query_assets(scan_id, filter=f, cursor=cursor, limit=15)
    handle(page["rows"])
    cursor = page["next_cursor"]
    if not cursor:
        break
```

```
page 1: 15 rows  has_more=True   next_cursor=eyJzIjogImxhYi0wMSIsICJpIjogMTV9
page 2: 15 rows  has_more=True   next_cursor=eyJzIjogImxhYi0wMSIsICJpIjogMzB9
page 3: 10 rows  has_more=False  next_cursor=None
```

Pagination alone is not the answer. It still walks the whole table one page at a time. The
aggregate is what lets the agent decide which rows it needs before it fetches any.

## Setup

Standard library only, Python 3.9 or newer. No install step.

```bash
export RECON_DB=/path/to/engagement/recon.db   # default: ./recon.db
```

Every function also takes `db=` directly. The schema is created on first connect, and WAL,
`synchronous=NORMAL` and a five second busy timeout are set on every connection, so separate
processes can read while a scan writes.
