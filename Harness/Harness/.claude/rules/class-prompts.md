---
description: The seven blocks a per class prompt has to contain, and the assertion trap.
paths:
  - "prompts/classes/**.md"
---

# Per class prompts

You are looking at a methodology file for one vulnerability class. One class per file.
The moment one file covers BOLA and injection, both get tested shallowly and neither
produces evidence you can put in front of a client.

## The seven blocks, in order
1. Identity. Exactly one class, named.
2. Scope. The host and path allowlist restated here, not inherited and assumed.
3. Identities held. Which accounts, what privilege each holds, which one is the victim.
4. Method as numbered steps. A step names the request to send and what to record. Not a
   goal statement.
5. Evidence required. Harness request ids, not pasted bodies.
6. The named false positive. Name the classic one for this class explicitly. It is cheap
   and it removes most of the noise before it reaches a human.
7. Output schema, with field names given. Without it the chaining pass has nothing to
   join on and the pipeline is a pile of chat transcripts.

## The assertion trap, which is the thing to get right
BOLA and BFLA are inverted, and almost every first harness reuses one assertion for both.

- BOLA swaps the auth token and keeps the object id. The assertion is sameness: the
  response body is at least 90 percent identical to the victim's. The proof is "I got
  their data".
- BFLA sends a privileged function as a low privilege role. The assertion is difference
  plus schema sameness: less than 10 percent identical to the low privilege baseline, and
  at least 90 percent schema identical to the admin response. The proof is "I got a
  different, admin shaped response".

A BFLA prompt carrying the BOLA assertion reports zero findings on a genuinely vulnerable
admin route, and reports them cleanly with no errors. That is the failure you cannot see.

Both carry a `not_contains` list of soft error strings. BFLA adds `not_contains: ["<html>"]`,
because a single page application redirecting to login returns 200 with HTML and that is
the classic false positive for the class.
