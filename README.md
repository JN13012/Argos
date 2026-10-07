# Argos

An early-stage research project exploring AI-assisted security assessment,
with an emphasis on traceable evidence, clear boundaries and useful reports.

**Current stage:** product specifications and educational prototypes. The Argos
platform described in the product brief is not implemented yet. This repository
does not demonstrate performance comparable to commercial platforms.

## What is here

| Path | Purpose | Status |
| --- | --- | --- |
| [Product brief](00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md) | Long-term vision and product principles | Vision document |
| [V0 scope](01_SCOPE_V0_ARGOS.md) | Proposed initial scope and acceptance criteria | Draft, awaiting validation |
| [Project status](PROJECT_STATUS_ARGOS.md) | Decisions and current progress | Project record |
| [Canonical manifest](CANONICAL_MANIFEST_ARGOS.md) | Document authority and dependencies | Documentation index |
| `Harness/Harness/` | Experimental agent profile, hooks and engagement templates | Prototype, not a security boundary |
| `Harness/Labs/lab2-source/` | Imported training application | Educational reference; provenance pending |
| [Roadmap](docs/ROADMAP.md) | Proposed milestones for a public portfolio | Proposal |
| [Repository review](docs/REPOSITORY_REVIEW.md) | Publication findings and validation limits | Preparation record |
| [Related projects](docs/RELATED_PROJECTS.md) | Competitors, design references and license observations | Research notes |

## Review the repository

No model, API key, dependency installation or network access is required:

```bash
python3 scripts/check_repository.py
git diff --check
```

The checker inspects the public working tree, validates Python and JSON syntax,
and validates JavaScript syntax when Node.js is available. It does not start the
agent, execute the training application or contact a target. It also reports
publication-sensitive paths still tracked in Git.

A supported Argos installation and a reproducible end-to-end demo are future
milestones. Imported course instructions may refer to files not present in this
checkout; see the repository review for the known gaps. The downloaded course
pack has been removed from the current tree.

## Data and provenance

Engagement data, evidence, reports, active engagement selection and personal
settings belong outside the public repository. The `.gitignore` keeps the
unconfirmed engagement template and excludes local runs. Ignoring a file does
not remove it from previous commits.

The imported materials are identified in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
The training application and experimental profile still require provenance
clarification. No repository-wide redistribution license has been selected while
their origin and permissions remain unresolved. The GitHub repository is already
public; historical course imports and engagement data have not been purged.

Project specifications are currently written in French. Development milestones
and the preparation review are linked above so reviewers can distinguish the
existing work from the intended product.
