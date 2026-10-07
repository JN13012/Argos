#!/usr/bin/env python3
"""
recon/store.py, the recon asset store.

Why it exists: a published run that enumerated over 30,000 subdomains filled its
context before it reached analysis. Two hundred endpoints read back as a file
evict the plan by the same mechanism. So recon writes rows here, and every later
pass asks a question instead of reading a file.

Three tools, in the order an agent should use them:
  summarize_assets(scan_id)              aggregates only, call this first
  query_assets(scan_id, filter=...)      one page of matching rows
  record_asset(scan_id, ...)             upsert, used by the recon pass

SQLite in WAL mode, so the summariser and the class subagents can read while a
scan is still writing. Standard library only. Python 3.9 or newer.
"""
import base64
import json
import os
import re
import sqlite3
import time
from contextlib import closing

DB_PATH = os.environ.get("RECON_DB", "recon.db")

# The harness sets the page size, not the model. query_assets clamps whatever it
# is handed, and the tool schema at the bottom of this file does not expose
# `limit` to the agent at all.
DEFAULT_PAGE, MAX_PAGE = 50, 200

# summarize_assets must not become a context bomb of its own. 30,000 hosts means
# a by_host dict with 30,000 keys, which is the problem we came here to avoid.
TOP_N = 15

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
  id              INTEGER PRIMARY KEY,
  scan_id         TEXT    NOT NULL,
  host            TEXT    NOT NULL,
  method          TEXT    NOT NULL,
  path            TEXT    NOT NULL,
  params          TEXT    NOT NULL DEFAULT '[]',
  takes_object_id INTEGER NOT NULL DEFAULT 0,
  status          INTEGER,
  authenticated   INTEGER NOT NULL DEFAULT 0,
  notes           TEXT,
  first_seen      REAL    NOT NULL,
  last_seen       REAL    NOT NULL,
  UNIQUE (scan_id, host, method, path)
);
CREATE INDEX IF NOT EXISTS assets_scan ON assets (scan_id, id);
"""


class FilterError(ValueError):
    """The filter did not parse, or named something the store does not expose."""


def _regexp(pattern, value):
    return value is not None and re.search(pattern, str(value)) is not None


def connect(db=None):
    """Open the store, enabling WAL and creating the schema on first use."""
    conn = sqlite3.connect(db or DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.create_function("regexp", 2, _regexp)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.executescript(SCHEMA)
    return conn


# --- The filter language ----------------------------------------------------
# Small on purpose, and parsed rather than interpolated. Anything it does not
# recognise is rejected, never passed through to SQL.

# public name -> (column, type)
FIELDS = {
    "hostname":        ("host", "text"),
    "host":            ("host", "text"),
    "method":          ("method", "text"),
    "path":            ("path", "text"),
    "params":          ("params", "text"),
    "notes":           ("notes", "text"),
    "status":          ("status", "int"),
    "takes_object_id": ("takes_object_id", "bool"),
    "authenticated":   ("authenticated", "bool"),
}
OPS = {
    "text": ("=", "!=", "contains", "matches", "in"),
    "int":  ("=", "!=", ">", "<", ">=", "<=", "in"),
    "bool": ("=", "!="),
}
KEYWORDS = {"and", "or", "not", "in", "contains", "matches", "true", "false"}

_TOKEN_RE = re.compile(r"""\s*(?:
      (?P<regex>/(?:[^/\\]|\\.)*/)
    | (?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
    | (?P<num>-?\d+)
    | (?P<op>!=|>=|<=|=|>|<)
    | (?P<punc>[(),])
    | (?P<word>[A-Za-z_][A-Za-z0-9_]*)
    )""", re.VERBOSE)


def _tokenize(text):
    toks, pos = [], 0
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise FilterError("cannot parse filter at position %d: %r" % (pos, text[pos:pos + 20]))
        toks.append((m.lastgroup, m.group(m.lastgroup)))
        pos = m.end()
    return toks


# "quoted" -> quoted, with backslash escapes undone
def _unquote(tok):
    return re.sub(r"\\(.)", r"\1", tok[1:-1])


# /regex/ -> regex. Only \/ is an escape here, so the rest of the pattern
# reaches re.compile exactly as the agent wrote it.
def _unslash(tok):
    return tok[1:-1].replace("\\/", "/")


def _like_escape(s):
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class _Parser:
    def __init__(self, text):
        self.toks, self.i = _tokenize(text), 0

    # token helpers
    def _take(self):
        if self.i >= len(self.toks):
            raise FilterError("filter ended early")
        self.i += 1
        return self.toks[self.i - 1]

    def _accept(self, kind, val):
        if self.i < len(self.toks):
            k, v = self.toks[self.i]
            if k == kind and v.lower() == val:
                self.i += 1
                return True
        return False

    # grammar
    def parse(self):
        sql, params = self.expr()
        if self.i < len(self.toks):
            raise FilterError("unexpected %r in filter" % (self.toks[self.i][1],))
        return sql, params

    def expr(self):
        sql, params = self.term()
        while self._accept("word", "or"):
            r, p = self.term()
            sql, params = "(%s OR %s)" % (sql, r), params + p
        return sql, params

    def term(self):
        sql, params = self.factor()
        while self._accept("word", "and"):
            r, p = self.factor()
            sql, params = "(%s AND %s)" % (sql, r), params + p
        return sql, params

    def factor(self):
        if self._accept("word", "not"):
            sql, params = self.factor()
            return "(NOT %s)" % sql, params
        if self._accept("punc", "("):
            sql, params = self.expr()
            if not self._accept("punc", ")"):
                raise FilterError("missing closing parenthesis")
            return "(%s)" % sql, params
        return self.comparison()

    def comparison(self):
        kind, raw = self._take()
        if kind != "word" or raw.lower() in KEYWORDS:
            raise FilterError("expected a field name, got %r" % (raw,))
        if raw.lower() not in FIELDS:
            raise FilterError("unknown field %r. Known fields: %s"
                              % (raw, ", ".join(sorted(FIELDS))))
        col, ftype = FIELDS[raw.lower()]
        okind, oraw = self._take()
        op = oraw.lower() if okind == "word" else oraw
        if op not in OPS[ftype]:
            raise FilterError("operator %r is not allowed on %s. Allowed: %s"
                              % (oraw, raw, ", ".join(OPS[ftype])))
        if op == "in":
            if not self._accept("punc", "("):
                raise FilterError("`in` must be followed by a parenthesised list")
            vals = [self.literal(ftype)]
            while self._accept("punc", ","):
                vals.append(self.literal(ftype))
            if not self._accept("punc", ")"):
                raise FilterError("missing closing parenthesis after `in` list")
            return "%s IN (%s)" % (col, ",".join("?" * len(vals))), vals
        if op == "matches":
            kind, raw = self._take()
            if kind != "regex":
                raise FilterError("`matches` needs a /regex/, got %r" % (raw,))
            pattern = _unslash(raw)
            try:
                re.compile(pattern)
            except re.error as exc:
                raise FilterError("bad regex %r: %s" % (pattern, exc))
            return "regexp(?, %s)" % col, [pattern]
        if op == "contains":
            return ("%s LIKE ? ESCAPE '\\'" % col,
                    ["%" + _like_escape(self.literal(ftype)) + "%"])
        return "%s %s ?" % (col, op), [self.literal(ftype)]

    def literal(self, ftype):
        kind, raw = self._take()
        if ftype == "text":
            if kind != "str":
                raise FilterError("expected a quoted string, got %r" % (raw,))
            return _unquote(raw)
        if ftype == "int":
            if kind != "num":
                raise FilterError("expected a number, got %r" % (raw,))
            return int(raw)
        if kind == "num" and raw in ("0", "1"):
            return int(raw)
        if kind == "word" and raw.lower() in ("true", "false"):
            return 1 if raw.lower() == "true" else 0
        raise FilterError("expected true or false, got %r" % (raw,))


def parse_filter(text):
    """Return (sql_fragment, bound_params). Raises FilterError on anything else."""
    return _Parser(text).parse()


# --- Cursors ----------------------------------------------------------------
# Opaque to the agent, and pinned to a scan_id so a cursor from one run cannot
# silently page through another.

def _encode_cursor(scan_id, last_id):
    raw = json.dumps({"s": scan_id, "i": last_id}).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(cursor, scan_id):
    try:
        pad = "=" * (-len(cursor) % 4)
        data = json.loads(base64.urlsafe_b64decode(cursor + pad))
        last_id, owner = int(data["i"]), data["s"]
    except Exception:
        raise ValueError("cursor is not readable; start the listing again without one")
    if owner != scan_id:
        raise ValueError("cursor belongs to scan %r, not %r" % (owner, scan_id))
    return last_id


# --- The three tools --------------------------------------------------------

def record_asset(scan_id, host, method, path, params=None, takes_object_id=False,
                 status=None, authenticated=False, notes=None, db=None):
    """Upsert one endpoint or host. Re-recording refines a row, it does not blank it."""
    now = time.time()
    row = (scan_id, host, method.upper(), path, json.dumps(list(params or [])),
           1 if takes_object_id else 0, status, 1 if authenticated else 0, notes, now, now)
    with closing(connect(db)) as conn, conn:
        conn.execute("""
            INSERT INTO assets (scan_id, host, method, path, params, takes_object_id,
                                status, authenticated, notes, first_seen, last_seen)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT (scan_id, host, method, path) DO UPDATE SET
              params          = excluded.params,
              takes_object_id = excluded.takes_object_id,
              authenticated   = excluded.authenticated,
              status          = COALESCE(excluded.status, assets.status),
              notes           = COALESCE(excluded.notes,  assets.notes),
              last_seen       = excluded.last_seen""", row)
        found = conn.execute(
            "SELECT id FROM assets WHERE scan_id=? AND host=? AND method=? AND path=?",
            row[:4]).fetchone()
    return {"asset_id": found["id"], "scan_id": scan_id}


def _row(r):
    d = dict(r)
    d["params"] = json.loads(d["params"])
    d["takes_object_id"] = bool(d["takes_object_id"])
    d["authenticated"] = bool(d["authenticated"])
    return d


def query_assets(scan_id, filter=None, cursor=None, limit=DEFAULT_PAGE, db=None):
    """One page of matching rows, plus the cursor for the next page.

    `filter` is the small expression language above, for example:
        hostname matches /staging|dev|qa/
        method = "POST" and takes_object_id = true
        status in (401, 403) and not path contains "/static/"
    """
    limit = max(1, min(int(limit or DEFAULT_PAGE), MAX_PAGE))
    where, params = ["scan_id = ?"], [scan_id]
    if cursor:
        where.append("id > ?")
        params.append(_decode_cursor(cursor, scan_id))
    if filter:
        frag, bound = parse_filter(filter)
        where.append(frag)
        params.extend(bound)
    sql = "SELECT * FROM assets WHERE %s ORDER BY id LIMIT ?" % " AND ".join(where)
    with closing(connect(db)) as conn:
        rows = conn.execute(sql, params + [limit + 1]).fetchall()
    more = len(rows) > limit
    rows = rows[:limit]
    return {"rows": [_row(r) for r in rows],
            "page_size": limit,
            "has_more": more,
            "next_cursor": _encode_cursor(scan_id, rows[-1]["id"]) if more else None}


# The slide names this tool `list_assets`. Same function, kept so the example on
# the slide runs as written.
list_assets = query_assets


def summarize_assets(scan_id, db=None):
    """Aggregate counts only. No rows, ever. Call this before you query anything.

    This is the tool that keeps a 200 endpoint map out of the context window.
    """
    with closing(connect(db)) as conn:
        # `col` is a literal from the three call sites below, never agent input.
        # scan_id, which is agent input, is bound. Keep it that way.
        def counts(col):
            return {str(r[0]): r[1] for r in conn.execute(
                "SELECT %s, COUNT(*) FROM assets WHERE scan_id = ? GROUP BY 1 "
                "ORDER BY 2 DESC" % col, (scan_id,)) if r[0] is not None}

        by_method, by_status, by_host = counts("method"), counts("status"), counts("host")
        totals = conn.execute(
            "SELECT COUNT(*) t, SUM(takes_object_id) o, SUM(authenticated) a "
            "FROM assets WHERE scan_id = ?", (scan_id,)).fetchone()
    return {
        "scan_id": scan_id,
        "total_assets": totals["t"],
        "by_method": by_method,
        "by_status": by_status,
        "by_host": dict(list(by_host.items())[:TOP_N]),
        "distinct_hosts": len(by_host),
        "hosts_not_shown": max(0, len(by_host) - TOP_N),
        "takes_object_id": totals["o"] or 0,
        "authenticated": totals["a"] or 0,
    }


# --- Tool schemas -----------------------------------------------------------
# OpenAI function-calling shape, ready to drop into harness/agent.py. Note what
# is missing from query_assets: `limit`. The harness owns the page size.

def _fn(name, description, required, **props):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "required": required, "properties": props}}}


_STR, _INT, _BOOL = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}

TOOL_SCHEMAS = [
    _fn("summarize_assets",
        "Aggregate counts for a scan: by method, by status, by host, plus how many "
        "endpoints take an object id and how many are authenticated. Returns no rows. "
        "Call this before query_assets.",
        ["scan_id"], scan_id=_STR),
    _fn("query_assets",
        "One page of assets matching a filter. Filter grammar: <field> <op> <value>, "
        "joined with and/or/not and parentheses. Fields: " + ", ".join(sorted(FIELDS)) +
        ". Operators: = != > < >= <= contains matches in. `matches` takes a /regex/. "
        'Example: hostname matches /staging|dev|qa/ and takes_object_id = true. '
        "Pass next_cursor back as cursor for the following page.",
        ["scan_id"], scan_id=_STR, filter=_STR, cursor=_STR),
    _fn("record_asset",
        "Upsert one endpoint or host into the scan. Recon writes here instead of "
        "writing a file the agent has to read back.",
        ["scan_id", "host", "method", "path"],
        scan_id=_STR, host=_STR, method=_STR, path=_STR, status=_INT, notes=_STR,
        params={"type": "array", "items": _STR},
        takes_object_id=_BOOL, authenticated=_BOOL),
]
