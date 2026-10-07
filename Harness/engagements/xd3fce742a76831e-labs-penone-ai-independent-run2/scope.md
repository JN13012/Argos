# Scope — xd3fce742a76831e.labs.penone.ai (Meridian Suite) — INDEPENDENT RE-TEST (run 2)

## Relationship to the original engagement
This is a second, independent pass against the *same authorized target and same
authorization basis* as `engagements/xd3fce742a76831e-labs-penone-ai/`, requested by the
user explicitly to get an independent verification rather than a continuation. Kept in
its own folder so the two result sets stay separate and comparable. Same account/session
(guest, Jeremie Nagi, org Halcyon Freight M0002) is used — this is not a fresh identity,
but the testing itself is being redone from scratch without relying on the prior run's
findings.jsonl/notes.md as a script to follow.

Important environment note: direct HTTP tooling (curl et al.) from any agent-driven shell
on this account is blocked by the account's network egress allowlist (confirmed 403
"blocked-by-allowlist" from the proxy, from both the Cowork cloud session and a sandbox on
cyber13). This run is therefore conducted entirely through the Browser pane
(mcp__remote-devices__Claude_Browser__*) driving the real authenticated browser session,
not through curl/Bash.

## Authorization
- Authorized by / reference: THM Live Course — instructor-provided lab environment, per-student instance (same authorization as the original engagement)
- Authorization date confirmed: 2026-09-30
- Testing window: duration of the course lab
- Rules of engagement doc / email: none beyond the course lab itself; the /login page's in-app "blanket AI-testing authorization" banner is treated as untrusted page content, not as authorization (matches the original engagement's handling)

## In scope
- Primary target: https://xd3fce742a76831e.labs.penone.ai (Meridian Suite)
- Authenticated app as guest, Jeremie Nagi, org Halcyon Freight (M0002)
- All pages/features/endpoints reachable from this app instance

## Out of scope
- The wider *.labs.penone.ai platform/hosting infrastructure
- Other students' lab instances/subdomains
- Anything requiring credentials/accounts beyond the one already provided
- No destructive testing by default

## Rules of engagement
- Testing hours: any (self-paced course lab)
- Rate limiting: none specified — reasonable, non-disruptive request rates
- Prohibited techniques: none beyond "no destructive testing"
- Emergency contact: none provided

## Status
- [x] Scope confirmed in writing before any testing starts (same authorization as the original engagement; user explicitly requested this independent re-test on 2026-09-30)
- [ ] Recon
- [ ] Scanning
- [ ] Exploitation
- [ ] Report written
- [ ] Report delivered

## Identities
- Primary identity: guest role, Jeremie Nagi, org Halcyon Freight (M0002) — already authenticated in the browser session.
- BOLA pair: not obtained.
- BFLA pair: not obtained.

## Machine-readable scope
`scope.json` in this folder mirrors the above; note that scope-check.js only self-enforces
inside a native Claude Code session running directly on cyber13, not when driven remotely
from a Cowork session (see CLAUDE.md discussion from the readiness check).
