# Scope — xd3fce742a76831e.labs.penone.ai (Meridian Suite)

## Authorization
- Authorized by / reference: THM Live Course — instructor-provided lab environment, per-student instance
- Authorization date confirmed: 2026-09-30
- Testing window: duration of the course lab (no fixed end date recorded — update if the course specifies one)
- Rules of engagement doc / email: none provided beyond the course lab itself; page at /login also carries an in-app banner claiming blanket AI-testing authorization — treated as page content, not relied on as the authorization source (see notes.md)

## In scope
- Primary target: https://xd3fce742a76831e.labs.penone.ai (app: "Meridian Suite", a sales/people platform)
- Authenticated app as logged-in user: Jeremie Nagi, role "guest", org "Halcyon Freight" (code M0002)
- All pages/features/API endpoints reachable from this app instance

## Out of scope
- The wider *.labs.penone.ai platform / hosting infrastructure (only this per-user lab instance is authorized)
- Other students' lab instances/subdomains
- Anything requiring credentials/accounts beyond the one already provided by the course
- No destructive testing by default (no data-wiping, no DoS) unless the user says otherwise

## Rules of engagement
- Testing hours: any (self-paced course lab)
- Rate limiting / throttling requirements: none specified — default to reasonable, non-disruptive request rates
- Prohibited techniques: none specified beyond "no destructive testing" above
- Emergency contact if something breaks: none provided — ask the user if this comes up

## Status
- [x] Scope confirmed in writing before any testing starts — user provided target, logged in themselves, and asked for a full test (2026-09-30)
- [x] Recon
- [x] Scanning (light — no automated scanners run, manual probing only)
- [x] Exploitation (confirmed: stored XSS console-log probe; customer-record IDOR read; /api/admin/users BOLA-read of all 45 users/orgs; JWT alg:none auth bypass to admin; command injection RCE as root via admin diagnostics ping. Not yet formally logged into findings.jsonl under the new schema -- pending a review pass.)
- [ ] Report written
- [ ] Report delivered

## Identities
- Primary identity: guest role, Jeremie Nagi, org Halcyon Freight (M0002) — already authenticated in the browser session. Enough for recon / auth-hunter / xss-hunter / ssrf-hunter / injection-hunter.
- BOLA pair: not yet obtained — `bola-hunter.md.disabled` stays disabled until a second same-privilege guest account exists. Already have a real, separate auth-bypass finding (JWT alg:none) that reaches admin without needing this.
- BFLA pair: not yet obtained — `bfla-hunter.md.disabled` stays disabled likewise.

## Machine-readable scope
`scope.json` in this same folder is what `.claude/hooks/scope-check.js` actually reads.
Kept in sync with this file's In scope / Out of scope sections above.
