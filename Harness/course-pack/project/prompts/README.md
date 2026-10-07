# prompts/

One prompt file per vulnerability class, plus the shared output schema every class
subagent emits.

```
finding.schema.json   The shared output schema. It is why findings from separate
                      subagents merge into one finding set.
classes/<slug>.md     One file per entry across the OWASP Top 10 and the
                      OWASP API Security Top 10.
```

The rule these files exist to enforce: **one class per prompt, never two.** The moment
one prompt covers BOLA and injection, both get tested shallowly and neither produces
evidence you can put in front of a client. A prompt covering ten classes gives each
one a sentence. A per-class prompt gives it numbered steps, an evidence bar and a
named false positive, and that is what moves results.

## The seven blocks

Every file in `classes/` has the same seven blocks, in this order. If you write your
own class file, copy the structure rather than the prose.

**1. Identity.** Exactly one class, named, plus what this subagent explicitly does not
test and which file owns that instead. A subagent that knows what to hand off stops
half-testing three classes at once.

**2. Scope.** The host and path allowlist restated inside the subagent, not inherited
and assumed. Enforcement lives in the hook and in the harness, which referee the raw
action and never read the paragraph the agent wrote explaining why a request was in
scope. This block exists so the model does not waste a run arguing with a block it
cannot lift, and so class-specific danger gets stated where it will be read: the write
limits in `bopla.md`, the request caps in `unrestricted-resource-consumption.md`, the
transitive egress rule in `ssrf.md`.

**3. Identities held.** Which accounts it can act as, the privilege each holds, and
which one is the victim. BOLA needs two accounts at the same privilege level. BFLA
needs two tiers. Injection and SSRF need one. One account per concurrent run, because
parallel agents sharing one identity race on refresh token rotation and everything
after the first refresh gets `invalid_grant`.

**4. Method, as numbered steps.** Ordered steps, not a goal statement. Each step names
the request to send and what to record. This is the block that carries the class's
actual technique, and the one worth rewriting after every engagement.

**5. Evidence required.** What must exist before anything counts as a finding. Always
request ids, never pasted bodies: `http_request` returns an id, `record_finding` takes
ids, and the harness pulls the real bytes itself. That is the defence against
soliloquizing, where a model writes tool output lines into its transcript without ever
issuing the call. If `record_finding` accepted bodies the model supplied, a fabricated
finding would pass validation.

**6. The named false positive.** Name the common one for this class, in bold, with how
to rule it out. This block is cheap and removes most of the noise before it reaches
you. Two show up in nearly every file for a reason: the single page application that
answers with 200 and an HTML login page, and the catch-all route that answers every
path with the same 200.

**7. Output schema reference.** `prompts/finding.schema.json`, with the field values
this class should use: its `vuln_class` slug, its `capability_granted`, its
`dedupe_key` shape. Without this block the chaining pass has nothing to join on, and
the run ends as a pile of chat transcripts instead of a finding set.

## Choosing which classes to run

You do not run eighteen subagents. Pick 4 to 6, because each one is a full run against
a live target and the chaining pass afterwards costs more than any single class.

**Start from the target shape.**

- An API, with or without a spec, means the API Top 10 is the list that describes what
  you will find. Start with `bola.md`, `bfla.md`, `bopla.md`.
- A server rendered web application means the OWASP Top 10 list. Start with
  `broken-access-control.md`, `injection.md`, `xss.md`.
- Anything that fetches a URL on your behalf means `ssrf.md`, regardless of which list
  you started from.

**Then cut by what you can actually hold.**

Identities decide this before the target does. With one account you cannot run
`bola.md` at all, and `bfla.md` needs two privilege tiers. If the client cannot
provision them, say so before the engagement rather than reporting nothing afterwards.

**Then cut by what the engagement type supports.**

- Black box: everything in `classes/` runs, with `cryptographic-failures.md` and
  `logging-and-monitoring-failures.md` producing mostly observations.
- White box, with source access: `insecure-design.md`,
  `software-and-data-integrity-failures.md` and `vulnerable-components.md` get much
  stronger, because you can establish reachability instead of guessing at it.
- Time boxed or a first engagement: run the four the labs use, `bola.md`, `bfla.md`,
  `injection.md`, `ssrf.md`, and nothing else. They are where fan out pays, because
  they are mechanical enumeration over a large surface.

**One thing to decide with a human, not a model.** `insecure-design.md` is business
logic, and business logic is the class that moved least as models improved: IDOR went
from 70 to 100 percent and XSS from 71.7 to 95.7, while business logic moved only 78.6
to 85.7. Run it, and read everything it produces yourself before any of it reaches a
report.

## Coverage

18 files across the two lists. Three files carry an entry from each list, because the
entries describe the same defect.

| List entry | File |
|---|---|
| OWASP A01 Broken access control | `broken-access-control.md`, `bola.md`, `bfla.md` |
| OWASP A02 Cryptographic failures | `cryptographic-failures.md` |
| OWASP A03 Injection | `injection.md`, `xss.md` |
| OWASP A04 Insecure design | `insecure-design.md` |
| OWASP A05 Security misconfiguration | `security-misconfiguration.md` |
| OWASP A06 Vulnerable and outdated components | `vulnerable-components.md` |
| OWASP A07 Identification and authentication failures | `authentication-failures.md` |
| OWASP A08 Software and data integrity failures | `software-and-data-integrity-failures.md` |
| OWASP A09 Security logging and monitoring failures | `logging-and-monitoring-failures.md` |
| OWASP A10 Server side request forgery | `ssrf.md` |
| API1 BOLA | `bola.md` |
| API2 Broken authentication | `authentication-failures.md` |
| API3 BOPLA | `bopla.md` |
| API4 Unrestricted resource consumption | `unrestricted-resource-consumption.md` |
| API5 BFLA | `bfla.md` |
| API6 Unrestricted access to sensitive business flows | `sensitive-business-flows.md` |
| API7 Server side request forgery | `ssrf.md` |
| API8 Security misconfiguration | `security-misconfiguration.md` |
| API9 Improper inventory management | `improper-inventory-management.md` |
| API10 Unsafe consumption of APIs | `unsafe-consumption-of-apis.md` |

Category names follow the 2021 edition of the OWASP Top 10 and the 2023 edition of the
OWASP API Security Top 10, which are the names used in the deck. `xss.md` is split out
of A03 because the method is a rendering context test rather than the interpreter
differential the rest of injection uses.

## Running one

As a Claude Code subagent, the file body is the subagent prompt:

```bash
claude -p "Run prompts/classes/bola.md against $ENGAGEMENT_HOST. \
Recon is already in the store, so use list_assets rather than recrawling."
```

With the local harness, point the system prompt at the class file:

```bash
cd harness && AGENT_SYSTEM_PROMPT=../prompts/classes/bola.md python3 agent.py \
  "Test every object identifier alice can see for cross identity access as bob."
```

Recon runs once for the whole engagement, before any class subagent. Re-running
discovery inside every subagent multiplies cost and gives each one a different map.

## The schema, and the two fields that carry the most weight

Every file's block 7 points at `finding.schema.json`. Two of its fields do more than
the rest.

`capability_granted` is the join key. A chaining pass joins findings by what they
grant, not by what class they are, and `vuln_class` does not join: two IDORs and an
information disclosure share no field that tells you one feeds the other. Its values
are a fixed vocabulary, and `capability_required` is the other half of the pair. One
finding's granted value is the next one's required value.

`repro_script` is what PTES means when it requires that an unrelated qualified tester
can reproduce the findings from the report alone. It runs from a clean machine, takes
the target as an argument, reads credentials from the environment, and depends on
nothing the run that found it left behind. Re-run every one of them from a clean state
before the report ships. A finding that will not reproduce on demand is a lead, and a
lead does not reach a client.

Record non-findings as well, with `non_finding: true`. A leaked internal hostname or
an email address in a JSON response is raw material for the chaining pass, and the
subagent that saw it is the only thing in the run that ever will.
