# ARGOS architecture foundation — proposal

**Status:** implementation proposal for the initial application foundation;
pending review against the project's governing documents. This page does not
change the status or scope of those documents.

## Repository map

```text
argos/
├── cli.py                      Existing OSINT CLI entry point
├── backend/
│   ├── api/                    FastAPI composition root and route adapters
│   ├── core/                   Shared startup configuration and HTTP concerns
│   ├── intel/osint/             Existing OSINT models, services and adapters
│   └── attack/pentest/         Future domain boundary; no active capability
└── frontend/                   Shared React/Vite application and retained prototype
docs/
├── architecture/               Architecture and decision records
├── development/                Development and frontend documentation
└── product/                    Existing product and OSINT governance documents
scripts/                         Local development entry points
Harness/                         Not present in the audited repository
```

The existing root `argos` Python package remains the single import namespace.
The FastAPI application is integrated as `argos.backend`, avoiding a competing
`argos_api` distribution or a second package named `argos`. The existing OSINT
CLI entry point remains at `argos/cli.py`; its business logic now lives in
`argos/backend/intel/osint/`. `argos.osint` remains a thin compatibility package
for existing imports. The React project is moved to
`argos/frontend/`; its historical components and assets are retained, while
the current entry point is a minimal health-check page rather than an active
domain workspace.

The root `pyproject.toml` and `uv.lock` manage the Python application as one
distribution. The frontend keeps its own `package.json` and npm lockfile;
there is no root npm workspace because only one JavaScript project exists.

## Modular monolith and dependency direction

The API is one deployable Python application, divided by domain and layer:

```text
HTTP routes / adapters  → application services → domain contracts/models
                                  ↓
                       infrastructure adapters

ATTACK, INTEL, DEFEND → ARGOS CORE contracts
ARGOS CORE            → standard library / infrastructure ports only
```

The API composition root may assemble Core and domain adapters. A domain can
depend on Core contracts; Core must not import or call a domain. Domain models,
application services, and infrastructure adapters belong in separate modules
when real functionality is introduced. No database adapter, mission model, or
placeholder business service is created in this bootstrap.

Future cross-language boundaries should use explicit, versioned data contracts
and narrow ports so an implementation can be replaced without exposing Python
internals. Rust is a possible implementation choice, not a current dependency.

## ARGOS CORE responsibility boundaries

These are planned responsibilities, not implemented or validated controls:

| Responsibility | Planned ownership |
| --- | --- |
| Mission Management | Mission lifecycle and ownership |
| Authorization & Scope | Explicit grant, target scope, expiry and revocation |
| Policy Engine | Independent allow/deny decisions, fail-closed by default |
| Execution Control | Future brokered, bounded execution; no arbitrary API commands |
| Asset Registry | Scoped assets and provenance |
| Evidence Management | Isolated evidence metadata, access and retention |
| Audit Logging | Structured, attributable decision and lifecycle events |
| Reporting | Domain-neutral report composition and export contracts |
| Configuration | Validated process and deployment configuration |

Domain-specific discovery, pentest logic, analysis, and collection remain in
their owning modules. Core will expose typed contracts/ports and will not own
offensive or OSINT techniques.

## Security planes and current status

1. **Control Plane:** future missions, authorizations, scope, policies, and
   human decisions.
2. **Execution Plane:** future isolated execution adapters. It is absent from
   this bootstrap.
3. **Evidence Plane:** future mission-isolated storage and access controls. It
   is absent from this bootstrap.

The only API endpoint currently exposed is `GET /api/v1/health`. No active
offensive endpoint, arbitrary command execution, external target scan, agent,
broker, database, or LLM integration is started or configured.

Authorization must fail closed; an AI component must never independently
authorize execution; sensitive operations require human validation; mission
data must be isolated; secrets must remain outside source; and logs should be
structured. These are design requirements only. They are **not implemented,
tested, or security-validated** by the health endpoint or this document. The
experimental safeguards described in prototypes, if any, are not treated as
security controls.

## ATTACK and future Pentest contracts

ATTACK/PENTEST is a reserved domain boundary only. No technique or engine is
implemented. Future capability work should preserve the three requested
verticals:

- Web/API.
- Network/Linux.
- Windows/Active Directory.

Red Team may later reuse approved Pentest engines through stable capability
contracts, without duplicating them. It must not bypass Core authorization or
scope controls. OSINT is the existing implemented capability under INTEL;
Threat Intelligence, DEFEND, and Red Team remain without implementation
folders. Their future placement and the Pentest-first priority remain proposals
until governance confirms them.

The eventual Pentest Engine can be split into recognition, enumeration,
authorized testing, independent validation, evidence, reporting, cleanup, and
retest contracts. Any execution adapter needs a separate design, approval
workflow, and security testing before it is enabled.

## Integration and local development

- Python API and OSINT CLI: one root `uv` project, compatible with Python 3.12+.
- API import path: `argos.backend.api.main:app`; CLI import and invocation
  remain `argos` and `python -m argos`.
- Web: shared React + TypeScript + Vite project at `argos/frontend/`, with strict
  TypeScript checking and Vitest.
- `argos/frontend/vite.config.ts` proxies `/api` to the local API; no CORS exception
  is needed for the development setup.
- SQLite/PostgreSQL adapters, authentication, deployment, and model providers
  are intentionally deferred. Ollama or external LLM providers can later
  implement an optional port; no model is required at startup.
- Run the API with `bash scripts/dev-api.sh`, and the web app in a second
  terminal with `bash argos/frontend/start-local.sh`.

The backend tests cover the health contract and HTTP error shape. Frontend
tests cover the health check and unavailable state. Future domain behavior
should be tested independently at domain, service, adapter, and HTTP levels;
security-policy tests must be independent of any AI output.

## Governance audit and open conflicts

The requested files `00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md`,
`01_SCOPE_V0_ARGOS.md`, `CANONICAL_MANIFEST_ARGOS.md`,
`PROJECT_STATUS_ARGOS.md`, `docs/ROADMAP.md`, `docs/REPOSITORY_REVIEW.md`, and
`THIRD_PARTY_NOTICES.md` were not present in the audited worktree. The
corresponding existing documents reviewed are `docs/product/VISION.md`,
`docs/product/SCOPE.md`, `docs/product/ROADMAP.md`,
`docs/architecture/ARCHITECTURE.md`, `docs/product/CADRE.md`,
`docs/product/OSINT.md`, and `docs/product/REFERENCES.md`.

The existing governance documents identify OSINT/Business Discovery as the
current priority, exclude a frontend from immediate scope, and defer Red and
Defense. This bootstrap instead prepares the requested Pentest-first API and a
connected minimal frontend. That is a scope and priority conflict, recorded
here as a proposal; the existing canonical documents were not rewritten or
promoted. The OSINT implementation was relocated without rewriting its business
logic; the former import path is retained as a compatibility layer.

The repository has no `Harness/` tree. Existing frontend files are a historical
prototype, including demonstration content; they are not reused as operational
security functionality. `docs/development/frontend/PLAN_FRONTEND.md` records
prototype provenance; `argos/frontend/assets/WORLD_ATLAS_LICENSE.txt` contains
the world-atlas license notice. The two ARGOS logo assets have been confirmed
by the owner as project-specific and authorized. The requested third-party
notices and repository review were absent; broader history and imported-resource
provenance are not resolved by this reorganization. No third-party code or asset
was newly imported.

No `AGENTS.md` is introduced: the requested governance prerequisites are not
available to validate.
