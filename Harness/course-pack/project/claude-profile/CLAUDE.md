# Engagement profile

## What this file is
This file is delivered as a user message after the system prompt. It shapes behaviour and
it enforces nothing. Anything that genuinely has to hold lives in `.claude/settings.json`
or in `.claude/hooks/scope-check.sh`. Read `README.md` beside this file for why the deny
list is shaped the way it is.

## Rules of engagement
Target, authorisation reference and testing window are in `scope.md`. You may not edit
`scope.md`, and a write to it is denied rather than declined. If you believe the scope is
wrong, stop and say so. Widening it is a human decision made before a run, not during one.

The scope hook reads the host of every request you are about to make. It never reads the
paragraph you wrote explaining why the request is in scope. A `BLOCKED` result means stop,
not retry with different wording.

## Identities
Two accounts per class, provisioned per run, never production, never reused across
clients. BOLA needs two accounts at the same privilege level. BFLA needs two privilege
tiers. One identity per concurrent run: parallel runs sharing one identity race on
refresh token rotation, the first refresh wins, and the rest get `invalid_grant`.

Credentials come from the environment, never from this file and never from a finding.
There is no per subagent credential isolation in Claude Code, so every subagent you spawn
inherits every token in the environment. Use the identity handle the harness gives you and
do not go looking for the raw token.

## Evidence standard
`http_request` returns a request id. `record_finding` takes ids, and the harness pulls the
real bodies itself. A finding cites `evidence.request_id_a` and `evidence.request_id_b`
and never a response body you typed out.

This is not bookkeeping. The named failure mode is soliloquizing: a model writing tool
output lines without ever issuing the tool call. If `record_finding` accepted bodies you
supplied, a fabricated finding would pass validation cleanly. A fabricated id has nothing
behind it, so the harness holding the evidence is the only version of this that works.

A finding is not a finding until:

- the same request has been issued under two identities, both with harness request ids
- the bodies the harness holds for those two ids have been diffed, and `body_diff` says
  what differs rather than that something differs
- an explicit `ownership_assertion` names which object belongs to whom and why this
  access is wrong
- it has reproduced on a second run, and `repro_script` reproduces it from a clean state

Your own screenshot is a claim. Your own summary is a claim. The harness store is proof.

## House style for findings
One vulnerability class per subagent, never two. Emit the shared schema in
`prompts/finding.schema.json` and nothing else. Assert on a post authentication marker in
the response body, never on a status code: a 200 carrying an empty result set is not
access, and a 200 carrying a login page is not a finding.

Set `capability_granted`, because the chaining pass joins on what a finding grants and not
on `vuln_class`. Set `dedupe_key` to class plus normalised endpoint plus parameter. Use
`confidence: lead` freely; a lead is legitimate output that never reaches a client as a
finding.

Report non findings. A leaked hostname, an email address in a JSON response, an identifier
you could not attribute: that is raw material for somebody else's chain, and a genuine
clean result contains things that were tried and ruled out.

## Stop conditions
WAF block, account lockout, captcha, target unavailable, or anything that looks like
client impact. Stop and tell a human. Do not push through, do not back off and retry, and
do not widen the search because the task in front of you is not completable.

## The pieces of this profile
- `.claude/skills/recon/` runs once at the start and writes the surface map everything
  else reads. It does not test.
- `.claude/agents/bola-hunter.md`, `bfla-hunter.md`, `injection-hunter.md` and
  `ssrf-hunter.md` are one class each. Each one loads its method from
  `prompts/classes/<slug>.md`.
- `.claude/rules/` holds path scoped rules that load only when you open a matching file.
