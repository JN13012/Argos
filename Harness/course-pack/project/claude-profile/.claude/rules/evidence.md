---
description: The evidence bar for anything written against the finding schema.
paths:
  - "findings*.json*"
  - "findings/**"
  - "notes.md"
  - "prompts/finding.schema.json"
---

# Evidence

You are looking at a findings artefact, so the evidence bar applies.

## Cite ids, never bodies
Every evidence field is a harness request id. `evidence.request_id_a` and
`evidence.request_id_b` are the two halves of the pair. The harness pulls the bodies for
those ids itself. Do not paste a request or a response you wrote out; a fabricated id has
nothing behind it, which is the point.

## Required before anything is written
1. The pair was issued. Two ids, two identities, every other byte of the request identical.
2. `body_diff` says what differs, not that something differs.
3. `ownership_assertion` names which object belongs to whom and why the access is wrong.
4. It reproduced on a second run, and `repro_script` reproduces it from a clean state with
   no manual setup. An unrelated tester has to get there from the file alone.

## Fields people leave empty and should not
- `capability_granted` is the join key for the chaining pass. `vuln_class` does not join.
  Two IDORs and an information disclosure share no field that says one feeds the other.
- `capability_required` is the other half of the same pair. One finding's granted value is
  the next one's required value.
- `dedupe_key` is class plus normalised endpoint plus parameter. It is what collapses
  duplicates when eight subagent transcripts become one finding set.
- `confidence` has three values on purpose. `lead` is legitimate output. A lead does not
  reach a client as a finding.

## Non findings belong in here too
Set `non_finding: true` and write it down anyway. A leaked hostname or an email address in
a response is raw material for somebody else's chain, and a file with no negatives in it
is a file that did not test anything.
