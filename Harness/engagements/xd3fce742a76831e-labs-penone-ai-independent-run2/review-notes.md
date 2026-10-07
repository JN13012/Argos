# Review notes — xd3fce742a76831e-labs-penone-ai-independent-run2

Adversarial re-verification pass, run 2026-09-30. Every entry in `exploitation/findings.jsonl`
was checked against `evidence/evidence.jsonl` (88 entries, ev_000001-ev_000088) before this
review touched anything. This file records every change made to `findings.jsonl` and why.
Nothing in this review consulted `engagements/xd3fce742a76831e-labs-penone-ai/` (the original
engagement) for any purpose.

## Changes made

### 1. `xss:/forum/{id}/reply:body` — downgraded confirmed/high → probable/medium, reproduced true → false

Cited evidence: `ev_000039` (a button click) and `ev_000041` (`get_page_text` on a fresh
reload). `ev_000041`'s logged response shows the reply rendering with no visible text after
"Jeremie Nagi / guest". The finding treats this as proof the `<img src=x onerror=...>` tag was
parsed as a live HTML element rather than escaped or stripped.

That inference does not hold up against the file's own other evidence. The non-finding two
lines later, `xss:/customers/{id}/notes:body`, shows the identical `<img onerror>` payload
being **fully stripped** server-side on a different field — and that stripped case *also*
renders as empty text under `get_page_text` (confirmed there only because a raw DOM dump via
`javascript_tool`, `ev_000051`, showed the `<div class="note">` with no child nodes at all). No
equivalent raw-DOM check was ever run against the forum reply. An empty rendered body is
therefore consistent with *either* an unescaped, executing tag *or* a fully stripped one — the
logged evidence for this finding cannot distinguish the two.

The finding's `marker` field claims `CLAUDE_PENTEST_XSS_PROBE_CONFIRMED_RUN2` was "printed to
browser console... twice." No entry in `evidence.jsonl` captures console output at all — the
logged tools here are `navigate` (returns a navigation confirmation string) and `get_page_text`
(returns rendered visible text). Neither can show a `console.log` call firing. There is no
console-reading tool call anywhere in this engagement's evidence log. The marker is not present
in any logged response.

Net effect: the stored-HTML-passthrough behavior on the forum reply field is a real and
plausible primitive (the field is clearly not HTML-escaping in the way a safe renderer would),
but "confirmed... js-execution-in-origin" overstates what the logged evidence actually shows.
Downgraded to `probable`/`medium`, `reproduced: false`. A follow-up pass should add a
`javascript_tool` DOM dump of the reply body (as was correctly done for the notes finding) and
an actual console-capture step before this is re-raised to confirmed.

### 2. `ssrf:/customers/{id}/logo:url` — severity high → medium (confidence unchanged)

Cited evidence `ev_000065` and `ev_000059` are real and do support the body_diff exactly as
written: two different URLs submitted to the logo-fetch field produced two different,
URL-specific live responses (a fresh 404 page vs. the literal contents of `/robots.txt`). The
server-side-fetch primitive is genuinely proven and `confidence: probable` was already the
correct, conservative call by the finding's own author.

The severity of `high`, however, is not justified by what was proven. The finding's own
`ownership_assertion` states plainly that this was only ever tested against the same in-scope
host, which the guest identity already had direct access to — and `prompts/classes/ssrf.md`
section 6 is explicit that "it is SSRF when it reaches somewhere you could not reach yourself,"
a bar this finding states outright it does not meet. Downgraded severity to `medium` to reflect
a real, well-evidenced primitive with no proven reach beyond what the tester could already see.
Confidence left at `probable`, unchanged.

### 3. `chain:xss-forum-reply-to-session-cookie-theft` — downgraded confirmed/critical → lead/informational, reproduced true → false

This is the more serious of the two downgrades. Cited evidence is `ev_000086` (a click, whose
logged response is just click coordinates) and `ev_000087` (a `navigate` call whose entire
logged response is the string `"navigated to https://xd3fce742a76831e.labs.penone.ai/forum/19"`).
That is the last entry in `evidence.jsonl` for this engagement. There is no subsequent
`get_page_text`, `javascript_tool`, or any other call that reads page content or console output
after the payload was posted. The claimed marker — `CLAUDE_PENTEST_CHAIN_CONFIRMED_RUN2 true`,
"printed twice" — appears nowhere in the evidence log. This chain's central claim (that the
injected script actually ran `document.cookie.includes(...)` and logged a boolean) has zero
supporting evidence of any kind in `evidence.jsonl`, not even the ambiguous kind available for
finding #1 above.

This chain also structurally depends on `xss:/forum/{id}/reply:body`'s `js-execution-in-origin`
capability, which is itself downgraded above.

Per the review brief: "a `lead` with no reproduction is never critical no matter what it claims
to reach." Downgraded to `confidence: lead`, `severity: informational`, `reproduced: false`.
The underlying hypothesis — stored XSS on an org-wide forum thread reading a non-HttpOnly
session cookie — remains plausible and is exactly the kind of thing worth a dedicated follow-up
with a real console-capture step, but it was not proven by what this run actually logged.

## Findings left unchanged after verification

- `authentication-failures:/admin:alg-none` (confirmed/critical) — verified. `ev_000020`
  (baseline, `{"error":"insufficient privileges"}`) and `ev_000021` (forged `alg:none` token,
  HTTP 200 with `<title>Administration · Meridian Suite</title>` in the body) both exist and
  match the claim exactly. A second independent pair (`ev_000016`/`ev_000017`) shows the same
  result from an earlier point in the session, satisfying the reproduction bar. `repro_script`
  present. This is a genuine, complete authentication bypass to an admin-shaped response and
  the `critical` severity is justified — privilege escalation on the live target, not a lead.
- `authentication-failures:cookie:http-only-flag` (confirmed/low) — verified. `ev_000012`
  shows `document.cookie` returning the live `mrd_session` JWT in script context at the
  application's own origin, which is only possible if the cookie lacks `HttpOnly`. `low`
  severity is appropriate on its own (it is a hardening gap, not exploitable in isolation); its
  real severity depends on a script-execution primitive existing elsewhere, which this run's
  more limited evidence for the XSS side no longer confirms to the same bar (see above).
- `xss:/customers/{id}/notes:body` (non-finding, confirmed) — verified. `ev_000051`'s raw DOM
  dump genuinely shows the injected tag stripped to nothing. This is the one XSS test in this
  engagement that was actually verified at the DOM level rather than inferred from rendered
  text, and it is correctly recorded as a negative.
- `injection:/customers:q` (non-finding, confirmed) — verified. `ev_000073` (baseline,
  9/340) and `ev_000075` (true-condition payload, 0/340) are both real and match the stated
  values; the false-condition result (`ev_000077`, also 0/340) is described in the body_diff
  narrative but the schema only permits two cited ids, which is a schema limitation, not a
  fabrication — the described numbers for all three requests check out against the log.
- All remaining `non_finding: true` / `lead` entries (`authentication-failures:/login:...`,
  `xss:/support:...`, `ssrf:...:scope-gap-no-collaborator`, `injection:/deals/{id}/discount:...`)
  correctly cite no fabricated evidence (their `request_id_a`/`b` are honestly `null`) and are
  explicit about why the surface was not tested. These do not misrepresent themselves as tested
  and are left as-is.

## Coverage check

17-18 method files exist under `prompts/classes/` (the file count is actually 18:
`authentication-failures, bfla, bola, bopla, broken-access-control, cryptographic-failures,
improper-inventory-management, injection, insecure-design, logging-and-monitoring-failures,
security-misconfiguration, sensitive-business-flows, software-and-data-integrity-failures,
ssrf, unrestricted-resource-consumption, unsafe-consumption-of-apis, vulnerable-components, xss`
— noted for the record since the review brief said 17).

- **Tested this run** (finding or explicit non-finding present in `findings.jsonl`):
  `authentication-failures`, `xss`, `ssrf`, `injection`.
- **Not run because the subagent is `.disabled`**, not because it was tried and came back
  clean: `bola` (`bola-hunter.md.disabled`), `bfla` (`bfla-hunter.md.disabled`). Both require a
  second identity (a same-privilege peer for BOLA, a low+admin pair for BFLA) that
  `scope.json` records as `"status": "pending"` for both `bola_peer` and `bfla_reference`. This
  is an explicit "not yet run," not a clean result — the dashboard's "0 customers assigned"
  vs. `/customers` listing all 340 org-wide accounts with no visible per-owner filter (recorded
  in `notes.md` recon section) is a strong BOLA-shaped lead that has never actually been tested.
- **Never attempted, no subagent exists or was dispatched for them this run**: `broken-access-control`,
  `bopla`, `cryptographic-failures`, `improper-inventory-management`, `insecure-design`,
  `logging-and-monitoring-failures`, `security-misconfiguration`, `sensitive-business-flows`,
  `software-and-data-integrity-failures`, `unrestricted-resource-consumption`,
  `unsafe-consumption-of-apis`, `vulnerable-components`. These are "not yet run," full stop —
  no claim of a clean result should be inferred for any of them.

## The unresolved chain gap (flagged, not papered over)

`authentication-failures:/admin:alg-none` grants `privilege-escalation`. No finding in this
run's `findings.jsonl` declares `capability_required: privilege-escalation`, so this capability
has no consumer this run — the chain pass correctly did not fabricate one. Per `notes.md`
("## Chains"), this is because recon in this run only walked the app as the already-authenticated
guest identity and never used the proven forged `alg:none` admin token to explore what routes
exist beyond `/admin` itself. In the original, separate engagement folder a command-injection
primitive on an admin-only diagnostics endpoint reportedly consumed exactly this capability —
but this review was explicitly instructed not to consult that folder, and does not rely on it
for anything here. Within this engagement's own evidence, the admin-only surface beyond `/admin`
was simply never explored, so the true downstream impact of the auth bypass — full admin
privilege escalation is proven, but what an admin can then *do* with it in this app instance is
unknown — is a genuine, reportable gap, not a finding to be assumed away. This is called out
explicitly in the report rather than silently left unaddressed.
