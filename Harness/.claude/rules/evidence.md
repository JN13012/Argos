---
description: The evidence bar for anything written against the finding schema, and how citation works in this project (no Burp -- a native PostToolUse hook is the evidence backend).
paths:
  - "findings*.json*"
  - "findings/**"
  - "notes.md"
  - "prompts/finding.schema.json"
---

# Evidence

You are looking at a findings artefact, so the evidence bar applies.

## How citation works in this project
Every Bash call and every browser call that can reach the target (`navigate`,
`javascript_tool`, `computer`, `read_page`, `get_page_text`) is automatically logged by
a `PostToolUse` hook (`.claude/hooks/evidence-log.js`) to
`engagements/<slug>/evidence/evidence.jsonl`, one line per call, with a hook-assigned
id (`ev_000001`, `ev_000002`, ...) and the real request/response bytes. The hook
assigns the id, not you -- that is the whole point. To learn the id your last call was
just given, read the tail of that file (`tail -n 1` via Bash, or Read the file) *before*
your next tool call. An id you did not get this way, or that does not appear in
`evidence.jsonl` when someone checks, is not evidence.

## Cite ids, never bodies
Every `evidence.*_id` field is one of these hook-assigned ids. Do not paste a request
or response you typed out into a finding -- the `review` subagent re-reads the actual
logged bytes for every id you cite and downgrades any finding whose claimed
`body_diff`/`marker` isn't actually present in the logged response.

## Required before anything is written
1. The pair was issued for real -- two ids, both present in `evidence.jsonl`.
2. `body_diff` says what differs, not that something differs.
3. `ownership_assertion` names which object or function belongs to whom and why this
   access is wrong.
4. It reproduced on a second run, and `repro_script` reproduces it from a clean state
   with no manual setup -- an unrelated tester has to get there from the file alone.

## Fields people leave empty and should not
- `capability_granted` is the join key for the chain pass. `vuln_class` does not join
  -- two findings in different classes only connect through this field.
- `capability_required` is the other half. One finding's granted value is the next
  one's required value.
- `dedupe_key` is class + normalised endpoint + parameter, so duplicates collapse when
  several subagent transcripts become one finding set.
- `confidence` has three values on purpose. `lead` is legitimate output that never
  reaches the report as a confirmed finding.

## Non-findings belong in here too
Set `non_finding: true` and write it down anyway. A leaked hostname or an email
address in a response is raw material for the chain pass, and a findings file with no
negatives in it is a file that did not test anything.
