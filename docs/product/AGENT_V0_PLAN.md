# ARGOS Agent V0 — Architecture and delivery plan

**Status:** implementation proposal; no agent or autonomous execution added.
**Branch:** `feat/agent-foundation` from main `cb34f66`.

## Decision

Build a **specialized pentest agent using a controlled harness**, rather than
a generic agent framework or a list of shell commands. The AI planner may
propose investigations later, but no LLM output can bypass mission signing,
scope policy, risk review or the existing execution manager.

The first milestone is **A1 — a deterministic, non-executable Knowledge
Base**. The existing `attack/pentest/methodology.py` is a small port-to-hint
table; A1 will introduce typed methods with explicit prerequisites and
evidence requirements. It must not import Enum2Root's source or data without
a separate license and provenance review.

## Proposed boundaries

```text
argos/backend/attack/pentest/
  knowledge/
    __init__.py       # public read-only lookup interface
    models.py         # typed techniques, prerequisites, observations, risks
    catalog.py        # original versioned initial methodology entries
    matcher.py        # deterministic evidence-to-technique matching
  methodology.py      # existing recommendations; adapter added in later lot
  adaptive_orchestrator.py  # existing execution flow; unchanged in A1
tests/
  test_pentest_knowledge_models.py
  test_pentest_knowledge_matcher.py
docs/product/
  AGENT_V0_PLAN.md
```

**A1 files:** 7 new files including this plan; no existing source files
changed in the initial implementation. If the implementation needs an
adapter, that becomes a separate commit and acceptance gate.

Future lots:
- **A2 Tool Registry:** typed capability descriptors, version, availability,
  prerequisites, input schema, policy action, risk class, side-effect flag;
  no arbitrary command string or open-ended shell interface.
- **A3 State Manager:** per-mission targets, immutable observation provenance,
  deduplicated findings/hypotheses, credential handles (no secrets in state),
  and resumable investigation checkpoints.
- **A4 Planner:** local LLM as an optional, untrusted proposal generator;
  structured proposals validated by deterministic policy and human approval
  for sensitive actions. First deliver a no-LLM baseline.

## A1 initial scope

Original, bounded entries for: TCP discovery, service identification,
HTTP/HTTPS review, SSH review, SMB exposure review, DNS configuration review,
LDAP/AD discovery recommendations. All entries are **non-executable**
instructions for the operator or a future approved tool.

Required fields: stable technique ID, title, category, description, service
and port predicates, explicit prerequisites, required observation types,
risk level, recommended follow-up, original reference/provenance, and
catalog version. Missing evidence or prerequisites must fail closed for
eligibility. A detected open port is not itself a confirmed vulnerability.

Matching:
1. Accept normalized `ScanObservation` and a separate validated operator
   context containing *declared* capabilities.
2. Match only observed open TCP services/ports and explicit prerequisites.
3. Return eligible and blocked recommendations with explainable reasons.
4. Never generate commands, expand targets, launch scans or handle credentials.
5. Deterministic ordering and stable results for identical inputs.

## Quality gates

- Unit tests for empty evidence, closed/filtered ports, matching services,
  missing prerequisites, unsupported service names, and deterministic order.
- Invalid catalog records and duplicate technique IDs rejected.
- Provenance and limits present on every knowledge entry.
- Existing ATTACK, OSINT, API and frontend tests remain green.
- `uv run ruff check argos/backend/core argos/backend/attack tests/`
- `uv run pytest -q` and `git diff --check`.

## Commit sequence

1. `docs(agent): define Agent V0 architecture and A1 acceptance gates`
2. `feat(agent): add typed, versioned pentest knowledge catalog`
3. `feat(agent): match investigation guidance to verified observations`
4. `test(agent): cover knowledge prerequisites and safety boundaries`
5. Optional separate adapter commit after acceptance of A1.

No merge into main until all validation gates pass and the diff is reviewed.

## Known prerequisite security debt

The P1 engine passed CI using synthetic subprocesses; this does not certify
live Nmap usage or a public scanning service. OS-level disk quotas, crash
recovery, process-tree cancellation on Windows and cross-process rate limits
remain separate hardening work. A1 does not weaken or bypass these controls.
