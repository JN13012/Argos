# ADR 0001: Start ARGOS as a modular monolith

- **Status:** Implemented as repository structure; product scope still pending
  governance validation
- **Date:** 2026-10-31

## Context

ARGOS needs a maintainable foundation for multiple future cybersecurity
domains, while the repository already contains an independent OSINT package
and frontend prototype. The current mission requests an API, a Pentest-first
architecture, local development, Python 3.12+, and no premature infrastructure.
Existing governance instead records OSINT as the current priority and defers
the frontend and Red/Defense work.

## Decision

Start ARGOS as a modular monolith: one FastAPI process with explicit Core,
route, and domain package boundaries. Keep one Python import namespace and put
the API under `argos/backend/`, the OSINT domain at
`argos/backend/intel/osint/`, and the CLI entry point at `argos/cli.py`.
Retain `argos.osint` as a temporary compatibility import path.
Place the shared React application and retained frontend prototype in
`argos/frontend/`. The root `pyproject.toml` and `uv.lock` manage Python
dependencies; the frontend retains its own npm lockfile. Its current entry
page calls only the API health endpoint.

Only configuration, stable basic HTTP errors, and a non-invasive health route
are implemented. Core responsibilities and the ATTACK/PENTEST location are
documented as contracts and boundaries; they are not implemented as fake
services. No execution, database, AI provider, broker, container runtime, or
microservice is introduced.

## Rationale

- A single process and local `uv`/Vite workflows keep startup and testing
  reproducible without deployment infrastructure.
- Package boundaries allow ATTACK, INTEL, and DEFEND to be added without
  allowing Core to depend on a business domain.
- A single `argos` distribution avoids collisions between the pre-existing
  `argos` package and the former `argos_api` package.
- Grouping the backend under `argos/` makes domain ownership explicit while
  retaining the existing CLI module and import name.
- One root Python lock prevents drift between separately resolved API and OSINT
  environments. A root npm workspace is unnecessary for one frontend project.
- Typed HTTP/domain contracts can later be implemented by Python or replaced
  behind narrow interfaces, including by Rust where justified.
- Deferring execution and persistence avoids presenting unimplemented security
  controls as protections.

## Consequences

- The backend modules share the existing `argos` package namespace; backend
  dependency direction must continue to be enforced through module boundaries.
- The root project now supports Python 3.12+, matching the API and verified
  OSINT test runtime. `.python-version` remains the selected local interpreter.
- The frontend and documentation paths changed; scripts, asset links, and
  documentation references were updated without moving ignored runtime data.
- The current governance priority and the mission's Pentest-first scope conflict.
  This ADR records a proposal; it does not resolve or ratify that conflict.
- Health status confirms only that the API process responds. It says nothing
  about mission authorization, execution safety, evidence protection, or
  production readiness.

## Rejected alternatives

- **Microservices:** add operational complexity without independent scaling or
  deployment needs.
- **Keep a separate `argos_api` distribution:** retains duplicate Python
  packaging and risks namespace collisions when applications consume both.
- **Add a root npm workspace:** adds no useful coordination for a single web app.
- **Add placeholder domain/service trees:** creates misleading structure without
  working contracts or behavior.
- **Enable offensive or AI workflows now:** outside this foundation mission and
  requires separate authorization, policy, human-review, and security designs.

## Revisit when

Governance validates the product priority and scope, or when a concrete need
requires shared domain contracts, persistence, authorization policy, or
separately deployable components.
