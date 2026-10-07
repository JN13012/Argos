# THM Pentest — project instructions for Claude

This project holds web application pentest engagements. Testing is done **one domain
at a time**: only one engagement is "active" at any point, and Claude should always
work inside that engagement's folder, not across engagements.

## What actually enforces the rules here

This file shapes behaviour. It does not enforce anything by itself. What holds:

- `.claude/settings.json` — tool permission allow/deny, and hook registration.
- `.claude/hooks/scope-check.js` — a `PreToolUse` hook. Every Bash call and every
  browser `navigate`/`javascript_tool` call is checked against the active engagement's
  `scope.json` before it runs. A host not on `allowed_hosts`/`callback_hosts` is
  blocked (exit 2), regardless of what Claude decides in the moment. **Known limit**:
  it can see a literal URL/hostname in the call, but it cannot fully police a URL built
  dynamically inside a `javascript_tool` script from a variable or a redirect chain —
  treat a pass as necessary, not sufficient, and keep testing disciplined about what it
  points at in the first place.
- `.claude/hooks/evidence-log.js` — a `PostToolUse` hook. It, not the model, assigns an
  id (`ev_000001`, ...) to every real request/response from Bash and the browser tools,
  and appends it to `engagements/<slug>/evidence/evidence.jsonl`. This is what makes a
  finding's cited evidence non-fabricable: the `review` subagent checks every cited id
  actually exists in that file before trusting a finding.

Never run active testing (scanning, exploitation, class-hunter subagents) against a
domain unless `engagements/<domain>/scope.md` exists, its "Scope confirmed in writing"
box is checked, **and** `engagements/<domain>/scope.json` exists with `"confirmed":
true` — the hook reads the second one, not the first, so both need to be true or the
hook blocks everything.

## Autonomy

This project runs engagements end to end without pausing between phases for approval.
The approval gate is at the engagement level — a human confirms `scope.md` and
`scope.json` before a run starts — not at the phase level once it has. Recon, the
relevant class-hunter subagents, the chain pass, and review all run back to back.

That is a statement about *pausing*, not about *ceiling*. Every class file in
`prompts/classes/` and every subagent in `.claude/agents/` carries its own hard limit
on what a single action may do (read-only proof, identity-only commands for command
injection, no data dumps, no persistence, no destructive payloads) regardless of
whether a human is watching. Removing the pause did not remove those limits. A stop
condition (WAF block, account lockout, captcha, target unavailable, anything that looks
like client impact) still means stop and record it, not push through.

## Folder structure

```
THM Pentest/
├── CLAUDE.md                  ← this file
├── CURRENT_ENGAGEMENT.md      ← name of the active engagement folder, or "none"
├── .claude/
│   ├── settings.json          ← permissions, hook registration
│   ├── hooks/
│   │   ├── scope-check.js     ← PreToolUse: blocks out-of-scope requests
│   │   └── evidence-log.js    ← PostToolUse: the non-fabricable evidence backend
│   ├── skills/recon/          ← in-conversation recon procedure
│   ├── rules/                 ← path-scoped guidance (loads only when a matching file opens)
│   └── agents/
│       ├── recon.md           ← maps the surface, does not test
│       ├── auth-hunter.md     ← authentication-failures (A07 / API2)
│       ├── xss-hunter.md      ← cross-site scripting (A03)
│       ├── ssrf-hunter.md     ← server-side request forgery (A10 / API7)
│       ├── injection-hunter.md ← SQL/NoSQL/command/template injection (A03), covers RCE
│       ├── bola-hunter.md.disabled  ← needs a second same-privilege identity, see scope.json
│       ├── bfla-hunter.md.disabled  ← needs a low+admin identity pair, see scope.json
│       ├── chain.md           ← joins findings on capability_granted/required, runs automatically
│       └── review.md          ← adversarial re-verification + coverage check + report
├── prompts/
│   ├── finding.schema.json    ← the one output shape every subagent emits
│   └── classes/               ← one method file per OWASP/API Top 10 category (17 total;
│                                  4 wired to a subagent so far, the rest are reference
│                                  material for subagents not yet built)
└── engagements/
    ├── _template/              ← blank layout, copy this to start a new engagement
    └── <domain-name>/          ← one folder per engagement, named after the target domain
        ├── scope.md            ← human-readable authorization, in/out of scope, RoE
        ├── scope.json          ← machine-readable — this is what the hook actually reads
        ├── notes.md            ← running dated log
        ├── recon/surface.json  ← written by the recon subagent
        ├── exploitation/findings.jsonl ← one JSON object per finding/non-finding/chain
        ├── evidence/
        │   ├── evidence.jsonl  ← hook-assigned ids + real request/response bytes
        │   └── .evidence_seq   ← the hook's own counter, don't edit by hand
        └── report/report.md    ← written by the review subagent
```

Use a plain, filesystem-safe folder name for `<domain-name>` (e.g. `example-com` for
`example.com`).

## Starting a new engagement

1. Ask the user for: the target domain, what authorizes the test, the testing window,
   any explicit exclusions, and what identities are available (a single account is
   enough for recon/auth/xss/ssrf/injection; BOLA and BFLA each need a second identity
   — see the `.disabled` agent files for exactly what).
2. Copy `engagements/_template/` to `engagements/<domain-name>/`.
3. Fill in `scope.md` completely, and write the matching `scope.json` (same
   allowlist, machine-readable — see the active engagement's `scope.json` for the
   shape). Check "Scope confirmed in writing" in `scope.md` **and** set
   `"confirmed": true` in `scope.json` only once the user has actually confirmed it.
4. Update `CURRENT_ENGAGEMENT.md` to `<domain-name>`.
5. Run `recon` first (subagent or skill), then dispatch the class-hunter subagents
   relevant to what recon found, then `chain`, then `review`. No pause between these
   once scope is confirmed.

## Switching or closing an engagement

- To switch focus, update `CURRENT_ENGAGEMENT.md` to the new domain name — the hook
  reads this file to find the right `scope.json`, so this is also what "in scope right
  now" means for enforcement purposes, not just organisation.
- When an engagement is finished, leave its folder in place as a record.

## Working in an engagement

- `notes.md` gets a dated entry each session.
- Findings and non-findings go in `exploitation/findings.jsonl`, one JSON object per
  line, matching `prompts/finding.schema.json` — never just prose in `notes.md`.
- Every evidence citation is a hook-assigned `ev_` id from `evidence.jsonl`, never a
  pasted body. See `.claude/rules/evidence.md`.
- The final report is `report/report.md`, written by the `review` subagent from the
  verified findings — ask the user if they also want it exported as a different file
  format (Word, PDF) once that's ready.
