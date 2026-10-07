# Scope — <domain.tld>

## Authorization
- Authorized by / reference: <client name, contract #, or THM room name>
- Authorization date confirmed: <YYYY-MM-DD>
- Testing window: <start> to <end>
- Rules of engagement doc / email: <link or path>

## In scope
- Primary domain: <domain.tld>
- Subdomains: <list, or "as enumerated during recon and confirmed in scope">
- IP ranges: <if applicable>
- Excluded paths/features (e.g. payment processing, third-party embeds): <list>

## Out of scope
- <anything explicitly excluded — other domains, prod data, DoS-style testing, social engineering, physical, etc.>

## Rules of engagement
- Testing hours: <e.g. any time / business hours only>
- Rate limiting / throttling requirements: <notes>
- Prohibited techniques: <e.g. no automated scanning without throttle, no destructive testing>
- Emergency contact if something breaks: <name / channel>

## Status
- [ ] Scope confirmed in writing before any testing starts
- [ ] Recon
- [ ] Scanning
- [ ] Exploitation
- [ ] Report written
- [ ] Report delivered

## Identities
- Primary identity: <role, how obtained> — enough for recon / auth-hunter / xss-hunter / ssrf-hunter / injection-hunter.
- BOLA pair (two same-privilege accounts owning different objects): <status: have / need to request>
- BFLA pair (low-privilege + admin reference): <status: have / need to request>
  (Without these two, `bola-hunter.md`/`bfla-hunter.md` stay `.disabled` for this engagement.)

## Machine-readable scope
Also fill in `scope.json` in this same folder — same allowlist, but that file is what
`.claude/hooks/scope-check.js` actually reads to block out-of-scope requests. `scope.md`
and `scope.json` must agree; the hook only trusts the `.json` one.
