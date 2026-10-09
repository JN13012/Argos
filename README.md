# Argos

An early-stage project exploring AI-assisted security assessment, with traceable
evidence, clear boundaries and useful reports.

The repository contains an offline Python CLI, an independent business Discovery
prototype and a React home dashboard. The broader security platform remains a
specification; the dashboard is not connected to either engine.

All project documentation is organized in **[doc/](doc/README.md)**.

| Start here | Documentation |
| --- | --- |
| Installation, demos, mission review and checks | [Getting started](doc/guides/DEMARRAGE.md) |
| Run the dashboard on localhost:8000 | [Frontend guide](doc/interface/FRONTEND.md) |
| Offline Core contract | [First deliverable](doc/livrables/FIRST_DELIVERABLE.md) |
| Discovery setup, sources and limits | [Discovery V0](doc/livrables/DISCOVERY_V0.md) |
| Product vision and proposed V0 | [Documentation index](doc/README.md#produit) |
| Progress and document authority | [Project tracking](doc/README.md#suivi-du-projet) |
| Imported material and attribution | [Third-party notices](doc/references/THIRD_PARTY_NOTICES.md) |

Original code lives in `argos/`, the dashboard in `frontend/`, and synthetic data
in `examples/`. Generated mission data and reports stay under ignored `.argos/`.
Development instructions remain in [AGENTS.md](AGENTS.md).
