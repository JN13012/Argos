---
name: recon
description: "Map the attack surface of a web application: endpoints, parameters, object identifiers and auth model. Use at the start of an engagement, before any vulnerability class subagent runs."
when_to_use: "The user asks to map, enumerate, scope out or do recon on a target application."
allowed-tools: "Bash(curl:*), Read, Write, mcp__burp__get_proxy_http_history"
---

# Recon

Produce the surface map every other subagent will work from. Run once, share the output.

## Steps
1. Pull existing proxy history first. Do not re-crawl what is already captured.
2. Enumerate routes from JS bundles, source maps, and any OpenAPI or GraphQL schema.
3. For every endpoint record: method, path, parameters, which parameters look like
   object references, and whether it requires authentication.
4. Log in as each identity and repeat, because routes appear after auth.
5. Collect every object identifier observed, with the identity that owned it.

## Output
Write `surface.json`. One entry per endpoint. Object identifiers go in a separate
`identifiers` array tagged with their owning identity, because that is what the
authorization subagent consumes.

## Do not
Do not test anything. Recon only. Finding bugs here pollutes the surface map and
wastes the context the other subagents need.
