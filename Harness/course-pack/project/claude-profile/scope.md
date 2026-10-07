# Scope

The agent cannot write to this file. `.claude/settings.json` denies `Edit` and `Write` on
it, because a hook reading a scope file the agent can rewrite enforces nothing.

Authorisation reference: <engagement letter / SOW number>
Testing window: <start> to <end>
Engagement host, exported as ENGAGEMENT_HOST for the hook: <host:port>

## In scope
- <host>

## Out of scope
- Everything else, including anything the in scope host links to or proxies.

## The first hop
A host on the allowlist that can fetch or proxy on your behalf extends the allowlist to
everything it can reach. Decide what the first hop may reach, not only what you may reach.
An SSRF callback host counts as a decision, so write it down here before the run.

## Identities provisioned for this engagement
- Equal privilege pair for BOLA: <alice>, <bob>
- Privilege tiers for BFLA: <low privilege>, <admin>
- One identity per concurrent run. Two runs sharing one account race on refresh token
  rotation and all but one get invalid_grant.

## Prohibited actions
Destructive operations, persistence, exfiltration of real data, privilege escalation
beyond proof, production changes, and any interaction with systems not listed above.

## Stop conditions
WAF block, account lockout, captcha, target unavailable, or anything that looks like
client impact. Stop and tell a human. Do not push through.
