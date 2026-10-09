# Argos — Getting started

Documentation is indexed in [doc/README.md](../README.md). Run the commands in
this guide from the repository root, unless a command explicitly changes the
working directory to `frontend/`.

An early-stage research project exploring AI-assisted security assessment,
with an emphasis on traceable evidence, clear boundaries and useful reports.

**Current stage:** Argos Core 0.1.0 implements an offline CLI for mission data,
local evidence validation, human review and Markdown reports. The broader Argos
platform described in the product brief remains a specification. This repository
does not demonstrate performance comparable to commercial platforms.

An independent **Discovery V0 prototype** discovers public French businesses,
optionally reads a few pages of a declared official website, and produces
traceable, deterministic potential-opportunity scores with SQLite/JSON snapshots.
It does not contact prospects or perform security scans. Its scope differs from
the security platform draft; see the [Discovery scope and contract](../livrables/DISCOVERY_V0.md).

## Run the Discovery demo

Requires Python 3.12+ and `uv`. From this checkout:

```bash
uv sync --locked
uv run argos discover businesses --activity "garage automobile" \
  --location Marseille --demo --limit 20 --json .argos/discovery-demo.json
```

The demo uses four fictional garages and simulated websites without network
access. Runtime data stays under ignored `.argos/`; an existing JSON export is
refused. Omit `--demo` to use the official French company and geographic APIs.
Registry records do not systematically identify websites: provide a local
`--website-hints` file to declare verified associations. Scores indicate potential
service opportunities and observation confidence, never proven commercial needs
or vulnerabilities. The [Discovery documentation](../livrables/DISCOVERY_V0.md) describes
sources, scoring, network limits, installation and further examples.

## Preview the dashboard

The [React dashboard](../interface/FRONTEND.md) recreates the provided Argos design
references with the project mascot and a fictional mission workspace.
It uses TypeScript and Vite; development requires Node.js 24 or newer.

```bash
cd frontend
npm ci
npm run dev
```

Open **http://localhost:8000**. Only the home dashboard is implemented; its
search, direct finding access, compact session logs, report download and
collapsible scripted chat work locally. The restored original home includes
the welcome mascot, five overview cards and document, mission and planned-agent
panels, with chat on the right on desktop and session logs below. The bundled report is
generated with Argos Core from the same fictional
assessment; the UI has no live connection to the core or an AI model. See the
[home design review](../interface/HOME_DESIGN_REVIEW.md) for its information priorities.
For a production preview, run `npm run build` then `npm run preview` from
`frontend/`. The Python CLI remains usable without installing frontend dependencies.

## Run the offline demo

Requires Python 3.11 or newer. From a clean checkout, no dependency installation,
API key, model, database or network access is required:

```bash
python3 -m argos report examples/offline/assessment.json --output .argos/report.md
```

Open `.argos/report.md` or read the committed [reference report](../../examples/offline/report.md).
The output is deterministic and contains two synthetic observations awaiting
review. Evidence hashes and references are checked before the report is written;
validation does not automatically confirm a vulnerability. Use `--force` to
replace an existing output. Runtime files under `.argos/` are ignored by Git.

## Create, import and review a mission

The sample below records a fictional review for the demonstration:

```bash
python3 -m argos init --id demo-offline --title "My offline demo" \
  --description "Synthetic training observations" --scope training-fixtures \
  --output .argos/mission.json
python3 -m argos import .argos/mission.json \
  --from-file examples/offline/assessment.json --output .argos/imported.json
python3 -m argos review .argos/imported.json --evidence-root examples/offline \
  --finding F-001 --decision accepted --reviewer "Demo reviewer" \
  --reason "Accepted for this synthetic demonstration only." --output .argos/reviewed.json
python3 -m argos report .argos/reviewed.json --evidence-root examples/offline \
  --output .argos/reviewed-report.md
```

Sources are preserved. Imports require the same mission ID and scope and reject
identifier collisions. `--evidence-root` defaults to the input document's folder
(the imported document's folder for `import`). Keep passing the original proof
root after moving or copying an assessment. Proof paths must remain inside it;
each declared SHA-256 must match the local file. Reports list proof metadata,
without embedding proof content.

`accepted` and `rejected` record human review decisions. They are not signed or
authenticated, and do not certify technical validity. Pending and rejected
findings remain in the report. See `python3 -m argos --help` for the offline commands
and the independent Discovery entry point.

## What is here

| Path | Purpose | Status |
| --- | --- | --- |
| `argos/` | Original offline CLI and independent `discovery/` prototype | Implemented tranches |
| `examples/discovery/` | Fictional businesses and mock website responses | Offline Discovery demo |
| `schemas/discovery.schema.json` | Discovery result and provenance contract | Version one |
| `tests_discovery/` | Discovery unit, network-guard and SQLite/CLI tests | Run with `uv run pytest` |
| `frontend/` | React and TypeScript home dashboard with unit and browser tests | Interactive demo, not connected to the core |
| `schemas/assessment.schema.json` | Version-one structural data contract | Implemented |
| `examples/offline/` | Synthetic data, proofs and reference report | Reproducible demo |
| `tests/` | Contract, reporting and CLI integration tests | Run offline |
| [First deliverable](../livrables/FIRST_DELIVERABLE.md) | Authorized scope and acceptance criteria for Argos Core | Implemented tranche |
| [Product brief](../produit/00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md) | Long-term vision and product principles | Vision document |
| [V0 scope](../produit/01_SCOPE_V0_ARGOS.md) | Proposed initial scope and acceptance criteria | Draft, awaiting validation |
| [Project status](../suivi/PROJECT_STATUS_ARGOS.md) | Decisions and current progress | Project record |
| [Canonical manifest](../suivi/CANONICAL_MANIFEST_ARGOS.md) | Document authority and dependencies | Documentation index |
| `Harness/Harness/` | Experimental agent profile, hooks and engagement templates | Prototype, not a security boundary |
| [Roadmap](../suivi/ROADMAP.md) | Proposed milestones for a public portfolio | Proposal |
| [Repository review](../suivi/REPOSITORY_REVIEW.md) | Publication findings and validation limits | Preparation record |
| [Related projects](../references/RELATED_PROJECTS.md) | Competitors, design references and license observations | Research notes |

## Review the repository

No model, API key, dependency installation or network access is required:

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
git diff --check
```

The checker inspects the public working tree, validates Python and JSON syntax,
and validates JavaScript syntax when Node.js is available. It does not start the
agent, execute the training application or contact a target. It also reports
publication-sensitive paths still tracked in Git.

The original offline CLI runs directly from this checkout. The
[GitHub Actions workflow](../../.github/workflows/checks.yml) runs tests and reproduces
the reference report on Python 3.11, 3.12 and 3.13. The JSON Schema describes the
structure; runtime checks also enforce references, scope, path containment and
file integrity. Validation errors exit with code `2`; file I/O errors use `1`.
The dashboard has a separate CI job for locked npm dependencies, formatting,
TypeScript, unit tests and Playwright browser interactions. Its checks are
documented in the [frontend guide](../interface/FRONTEND.md).

Imported course instructions may refer to files not present in this checkout;
see the repository review for the known gaps. The downloaded course pack has
been removed from the current tree. The offline demo does not use those imports.

## Data and provenance

Engagement data, evidence, reports, active engagement selection and personal
settings belong outside the public repository. The `.gitignore` keeps the
unconfirmed engagement template and excludes local runs. Ignoring a file does
not remove it from previous commits.

The imported materials are identified in [THIRD_PARTY_NOTICES.md](../references/THIRD_PARTY_NOTICES.md).
The experimental profile still requires provenance clarification. No
repository-wide redistribution license has been selected while its origin and
permissions remain unresolved. The completed training lab was moved outside the
project by its owner. The GitHub repository is already public; historical course
imports and engagement data have not been purged.

Project specifications are currently written in French. Development milestones
and the preparation review are linked above so reviewers can distinguish the
existing work from the intended product.
