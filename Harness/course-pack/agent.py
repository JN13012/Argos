#!/usr/bin/env python3
"""
A small pentest harness. Web application testing and source code review.

Built to run against a local model over an OpenAI compatible endpoint, which means
Ollama, LM Studio or vLLM without modification.

The seven parts of any harness, labelled so you can find them:

  1 TOOL ACCESS        TOOLS + dispatch()
  2 CONTEXT MANAGEMENT trim()
  3 ORCHESTRATION      run()
  4 STOPPING RULES     MAX_CALLS, MAX_TURNS, MAX_IDLE, MAX_REJECTS, MAX_NOT_FOUND
  5 VALIDATION         record_finding() checks before it accepts
  6 PERSISTENCE        findings.jsonl and notes.md
  7 PERMISSIONS        in_scope() and in_repo(), called before every tool that reaches out

Deliberately small. You should be able to read the whole thing in one sitting, which is
the point: you cannot reason about what an agent is allowed to do if you cannot read the
thing that allows it.

  MODE=web    python3 agent.py "Test the orders API for broken object level authorization"
  MODE=source python3 agent.py "Find injection flaws in this codebase"
"""

import json, os, re, sys, time, fnmatch, urllib.parse, urllib.request

# ---------------------------------------------------------------- configuration

BASE_URL  = os.environ.get("AGENT_BASE_URL", "http://localhost:11434/v1")
MODEL     = os.environ.get("AGENT_MODEL", "qwen3.5:9b-32k")
API_KEY   = os.environ.get("AGENT_API_KEY", "not-needed-for-local")
MODE      = os.environ.get("MODE", "web")              # web | source | both

TARGET    = os.environ.get("AGENT_TARGET", "http://localhost:8080")
REPO_ROOT = os.path.realpath(os.environ.get("AGENT_REPO", "."))

# 7 PERMISSIONS. Set at launch. Nothing at runtime can widen these.
ALLOWED_HOSTS  = {urllib.parse.urlparse(TARGET).netloc}
BLOCKED_VERBS  = {"DELETE"}
BLOCKED_PATHS  = ("/admin/delete", "/api/v1/wipe")
SKIP_DIRS      = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
SKIP_FILES     = {"findings.jsonl", "notes.md"}   # never let it read its own output back

# 4 STOPPING RULES
MAX_CALLS, MAX_TURNS, MAX_IDLE, MAX_REJECTS, MAX_NOT_FOUND = 60, 40, 300, 6, 8

# 6 PERSISTENCE
FINDINGS, NOTES = "findings.jsonl", "notes.md"

MAX_TOOL_CHARS = 3000        # what the model sees of any tool result
REQUESTS = {}                # request id -> what we actually sent and got back

# ---------------------------------------------------------------- 7 permissions

def in_scope(method, url):
    """Every outbound request passes through here. There is no path around it.

    Resolution happens inside the check, not before it, so there is no way to
    reach the network with a URL this function has not seen and approved. It
    returns the absolute URL it approved; the caller sends that, not its input.
    """
    # Models write paths, not absolute URLs. Resolve against the target first.
    url = urllib.parse.urljoin(TARGET + "/", url) if "://" not in url else url
    p = urllib.parse.urlparse(url)
    hint = f"In scope: {sorted(ALLOWED_HOSTS)[0]}. Send a path like /orders/1."
    if p.netloc not in ALLOWED_HOSTS:
        return False, f"host {p.netloc or 'none'} is not in scope. {hint}", None
    if method.upper() in BLOCKED_VERBS:
        return False, f"verb {method} is blocked", None
    if any(p.path.startswith(b) for b in BLOCKED_PATHS):
        return False, f"path {p.path} is blocked", None
    return True, "", url

def in_repo(path):
    """Same idea, for the filesystem. Blocks traversal out of the checkout."""
    full = os.path.realpath(os.path.join(REPO_ROOT, path))
    if not full.startswith(REPO_ROOT):
        return False, f"{path} is outside the repository root", None
    return True, "", full

# ---------------------------------------------------------------- 1 tool access

def t_http_request(method="GET", url="", headers=None, body=None, identity=""):
    ok, why, url = in_scope(method, url)
    if not ok:
        return f"BLOCKED BY SCOPE: {why}"
    hdrs = dict(headers or {})
    if identity:
        token = os.environ.get(f"TOKEN_{identity.upper()}")
        if not token:
            return f"no token in the environment for identity '{identity}'"
        hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, method=method.upper(),
                                 data=body.encode() if body else None, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            status, text = r.status, r.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read(200_000).decode("utf-8", "replace")
    except Exception as e:
        return f"request failed: {e}"

    rid = f"req-{len(REQUESTS)+1:03d}"
    REQUESTS[rid] = {"method": method, "url": url, "identity": identity,
                     "status": status, "body": text}
    return (f"request_id={rid} status={status}\n"
            f"{text[:MAX_TOOL_CHARS]}")

def t_list_files(path=".", pattern="*"):
    ok, why, full = in_repo(path)
    if not ok:
        return f"BLOCKED BY SCOPE: {why}"
    out = []
    for root, dirs, files in os.walk(full):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES:
                continue
            if fnmatch.fnmatch(f, pattern):
                out.append(os.path.relpath(os.path.join(root, f), REPO_ROOT))
        if len(out) > 400:
            break
    return "\n".join(sorted(out)[:400]) or "no matching files"

def t_read_file(path="", start=1, lines=200):
    ok, why, full = in_repo(path)
    if not ok:
        return f"BLOCKED BY SCOPE: {why}"
    if os.path.basename(full) in SKIP_FILES:
        return "that is this run's own output, not source. Read the application code."
    if not os.path.isfile(full):
        return f"{path} is not a file"
    with open(full, encoding="utf-8", errors="replace") as fh:
        all_lines = fh.readlines()
    first = max(1, int(start))
    chunk = all_lines[first - 1: first - 1 + int(lines)]
    return "".join(f"{i+first}: {l}" for i, l in enumerate(chunk))[:MAX_TOOL_CHARS] \
        or "empty range"

def t_grep_files(pattern="", glob="*"):
    ok, why, full = in_repo(".")
    if not ok:
        return f"BLOCKED BY SCOPE: {why}"
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return f"bad regex: {e}"
    hits = []
    for root, dirs, files in os.walk(full):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES or not fnmatch.fnmatch(f, glob):
                continue
            p = os.path.join(root, f)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    for n, line in enumerate(fh, 1):
                        if rx.search(line):
                            hits.append(f"{os.path.relpath(p, REPO_ROOT)}:{n}: {line.strip()[:160]}")
                            if len(hits) > 80:
                                return "\n".join(hits[:80]) + "\n... truncated"
            except Exception:
                pass
    return "\n".join(hits) or "no matches"

def t_note(text=""):
    with open(NOTES, "a", encoding="utf-8") as fh:
        fh.write(text.rstrip() + "\n")
    return "noted"

# ---------------------------------------------------------------- 5 validation

def t_record_finding(title="", severity="medium", evidence_ids=None,
                     file_path="", ownership="", detail=""):
    """The harness checks the evidence. The model does not get to assert it."""
    ids = [i for i in (evidence_ids or []) if i]

    # An id the harness never issued is fabricated evidence, whatever the mode.
    unknown = [i for i in ids if i not in REQUESTS]
    if unknown:
        return (f"REJECTED: no such request id {unknown}. Only cite ids returned by "
                "http_request. For a source finding, leave evidence_ids empty and set file_path.")

    # Unanchored findings are opinions. Web anchors on request ids, source on a file.
    if not ids and not file_path:
        return ("REJECTED: anchor the finding. Set evidence_ids to request ids from "
                "http_request, or set file_path to the file the flaw is in.")

    if MODE in ("web", "both") and not file_path:
        if not ids:
            return ("REJECTED: set evidence_ids to request ids returned by http_request. "
                    "A web finding cannot be recorded without them.")
        if len(set(ids)) < 2:
            return ("REJECTED: evidence_ids needs two different request ids, one per "
                    "identity, so the pair can be compared.")
        a, b = REQUESTS[ids[0]], REQUESTS[ids[1]]
        if a["identity"] == b["identity"]:
            return (f"REJECTED: both requests ran as '{a['identity']}'. "
                    "An authorization finding needs two different identities.")
        if not ownership.strip():
            return ("REJECTED: the 'ownership' parameter is empty. Put the assertion there, "
                    "not in 'detail': which object belongs to whom, and why this access is "
                    "wrong. Example: order 1 belongs to alice, bob read it.")

    if file_path:
        ok, why, _ = in_repo(file_path)
        if not ok:
            return f"REJECTED: {why}"
        if not detail.strip():
            return ("REJECTED: the 'detail' parameter is empty. Put the line number and why "
                    "it is wrong there.")

    rec = {"title": title, "severity": severity, "mode": MODE,
           "evidence_ids": ids, "file": file_path,
           "ownership_assertion": ownership, "detail": detail,
           "evidence": {i: {k: REQUESTS[i][k] for k in ("method", "url", "identity", "status")}
                        for i in ids if i in REQUESTS}}
    with open(FINDINGS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return f"recorded: {title}"

def t_finish(summary=""):
    return f"FINISH: {summary}"

# Small models cope badly with large tool surfaces. Give them only what the mode needs.
WEB_TOOLS = {
    "http_request": (t_http_request, "Send an HTTP request to the target. Returns a request_id you must cite as evidence.",
        {"method": "string", "url": "string, a path on the target such as /orders/1", "identity": "string, which test account to use, alice or bob", "body": "string"}),
}
SRC_TOOLS = {
    "list_files": (t_list_files, "List files in the repository.", {"path": "string", "pattern": "string, e.g. *.py"}),
    "read_file":  (t_read_file,  "Read a range of lines from a file.", {"path": "string", "start": "integer", "lines": "integer"}),
    "grep_files": (t_grep_files, "Search file contents by regular expression.", {"pattern": "string", "glob": "string"}),
}
COMMON_TOOLS = {
    "record_finding": (t_record_finding, "Record a confirmed finding. The harness validates the evidence.",
        {"title": "string", "severity": "string", "evidence_ids": "array of request ids",
         "file_path": "string, for source findings",
         "ownership": "string, REQUIRED for a web authorization finding: which object belongs to whom and why this access is wrong",
         "detail": "string, REQUIRED for a source finding: which line and why it is wrong"}),
    "note":   (t_note,   "Write a short note to keep across turns.", {"text": "string"}),
    "finish": (t_finish, "Call this when you are done or can make no further progress.", {"summary": "string"}),
}

def active_tools():
    t = dict(COMMON_TOOLS)
    if MODE in ("web", "both"):    t.update(WEB_TOOLS)
    if MODE in ("source", "both"): t.update(SRC_TOOLS)
    return t

def tool_schemas():
    out = []
    for name, (_, desc, params) in active_tools().items():
        props = {}
        for p, d in params.items():
            props[p] = {"type": "array", "items": {"type": "string"}, "description": d} \
                if d.startswith("array") else \
                {"type": "integer" if d.startswith("integer") else "string", "description": d}
        out.append({"type": "function", "function": {
            "name": name, "description": desc,
            "parameters": {"type": "object", "properties": props}}})
    return out

def dispatch(name, args):
    tools = active_tools()
    if name not in tools:
        return f"no such tool '{name}'. Available: {', '.join(tools)}"
    try:
        return str(tools[name][0](**args))
    except TypeError as e:
        return f"bad arguments for {name}: {e}"
    except Exception as e:
        return f"{name} failed: {e}"

# ---------------------------------------------------- 2 context management

def trim(messages, keep=16):
    """Drop the middle, keep the system prompt and the recent turns."""
    if len(messages) <= keep + 1:
        return messages
    return messages[:1] + [{"role": "user", "content": "[earlier turns trimmed]"}] + messages[-keep:]

# ---------------------------------------------------------------- 3 orchestration

SYSTEM = """You are a penetration tester working on an authorised engagement.

Work in small steps. Call exactly one tool at a time, look at the result, then decide.

Rules that matter:
- Assert on what is in the response body, never on the status code alone.
- For an authorization finding you must send the SAME request as two different identities
  and cite both request ids.
- If a tool returns BLOCKED BY SCOPE, that is final. Do not retry it a different way.
- Call finish when you are done or cannot make further progress.

Be concise. Do not explain what you are about to do at length; do it."""

def chat(messages):
    payload = {"model": MODEL, "messages": messages,
               "tools": tool_schemas(), "tool_choice": "auto", "temperature": 0.3}
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", method="POST",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["choices"][0]["message"]

REJECTIONS = ("BLOCKED BY SCOPE", "REJECTED", "request failed", "no token", "no such")

def rejected(result):
    """A rejected call is not progress. Without this the loop spins on its own errors."""
    return result.startswith(REJECTIONS)

def run(goal):
    print(f"model={MODEL}  mode={MODE}  target={TARGET if MODE!='source' else REPO_ROOT}")
    print(f"tools: {', '.join(active_tools())}\n")

    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": goal}]
    calls = rejects = notfound = 0
    last_progress = time.time()

    for turn in range(1, MAX_TURNS + 1):
        try:
            msg = chat(trim(messages))
        except Exception as e:
            print(f"model call failed: {e}"); return

        messages.append(msg)
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            text = (msg.get("content") or "").strip()
            print(f"[{turn}] {text[:400]}")
            # A small model sometimes narrates instead of calling a tool. Nudge once.
            messages.append({"role": "user",
                             "content": "Call a tool, or call finish. Do not reply with prose."})
            if time.time() - last_progress > MAX_IDLE:
                print("\nno progress, stopping."); return
            continue

        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls += 1
            result = dispatch(name, args)
            short = result.replace("\n", " ")[:120]
            print(f"[{turn}] {name}({', '.join(f'{k}={str(v)[:40]}' for k,v in args.items())}) -> {short}")

            if result.startswith("FINISH:"):
                print(f"\ndone. {result[7:].strip()}")
                print(f"{calls} tool calls, {len(REQUESTS)} requests, findings in {FINDINGS}")
                return

            messages.append({"role": "tool", "tool_call_id": tc.get("id", name),
                             "content": result[:MAX_TOOL_CHARS]})

            # Guessing at paths is not testing. A 404 streak means it has run out of
            # information and is enumerating. That is a stopping condition of its own.
            if result.startswith("request_id=") and " status=404" in result.split("\n")[0]:
                notfound += 1
                if notfound >= MAX_NOT_FOUND:
                    print(f"\n{notfound} not-found responses in a row, stopping. "
                          "The agent is guessing at paths, not testing what it found.")
                    return
            else:
                notfound = 0

            if rejected(result):
                rejects += 1
                if rejects >= MAX_REJECTS:
                    print(f"\n{rejects} rejected calls in a row, stopping. "
                          "The agent is arguing with the harness, not testing the target.")
                    return
            else:
                rejects = 0
                last_progress = time.time()

            if calls >= MAX_CALLS:
                print("\ncall cap reached, stopping."); return

    print("\nturn cap reached, stopping.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    run(" ".join(sys.argv[1:]))
