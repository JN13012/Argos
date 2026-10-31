# ARGOS

ARGOS is a modular OSINT and cybersecurity platform with traceable information,
local-first development and optional AI assistance.

## Current implementation

The existing OSINT CLI provides bounded SIRENE discovery, SQLite persistence
and readable reports. A FastAPI health endpoint and a minimal React application
are available as the initial web/API foundation. Neither provides an active
offensive capability. The governance documents continue to identify OSINT as
the current product priority; the broader monorepo structure is an architectural
evolution and does not change those decisions.

OSINT services and models are organized under
`argos.backend.intel.osint`. The historical `argos.osint` import path remains
available as a compatibility layer; the CLI entry point stays `argos.cli`.

## Documentation

- [Vision](docs/product/VISION.md)
- [Scope](docs/product/SCOPE.md)
- [Project framework](docs/product/CADRE.md)
- [OSINT design](docs/product/OSINT.md)
- [Roadmap](docs/product/ROADMAP.md)
- [References](docs/product/REFERENCES.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Repository architecture](docs/architecture/README.md)
- [Frontend documentation](docs/development/frontend/PLAN_FRONTEND.md)

## Sirene API configuration

Run Argos from the project root. Create a local `.env` from `.env.example`
if it does not already exist, then fill in `INSEE_API_KEY` privately:

```dotenv
INSEE_API_KEY=your_personal_insee_api_key
```

The CLI loads `.env` from the current working directory before discovery.
An existing environment variable takes priority over the file. `.env` is
excluded from Git; `.env.example` contains no credentials and only non-secret
defaults. Never include your real key in source code, documentation, or
committed files.

```bash
uv run python -m argos osint discover --help
```

## Search results

`.argos/osint/argos.sqlite3` is the internal SQLite database, excluded from Git.
It is binary and is not intended to be opened as a text document.

Each `osint discover` run also creates a readable Markdown report under
`outputs/sirene/RESEARCH_NAME/rapport-001.md`. Reports contain the scope,
coverage, source, query, and establishments sorted by name, with identifiers,
current activity, administrative status, and formatted addresses. Dates use
Europe/Paris. Facts come from observations collected during the saved search.
Partial searches are explicitly identified as non-exhaustive; a historical
activity query can include closed establishments or changed activities.

Open a numbered report in VS Code and use **Open Preview** to read it comfortably.
`outputs/` is excluded from Git. Use `--output-dir` to choose a different root.
Use `--name garages-marseille` to choose a readable research folder. Names are
normalized to lowercase, with accents and punctuation removed. Without `--name`,
Argos reuses a folder for an existing search or scope (activity and location),
or derives a folder name from the activity and location.

New searches create `rapport-002.md`, `rapport-003.md`, etc. Re-exporting the same
search updates its existing numbered report. The date and search UUID remain in
the report contents. Collection limits and exact queries remain recorded there.

Export an existing search without another API call or an API key:

```bash
uv run python -m argos osint report --search-id SEARCH_UUID --name garages-marseille
```

## Frontend local

The shared React/TypeScript/Vite application is under `argos/frontend/`.
Its current entry page checks the local API health endpoint. Earlier prototype
components, fixtures and assets are retained, but are not presented as active
ARGOS capabilities.

```bash
# Terminal 1
bash scripts/dev-api.sh

# Terminal 2
bash argos/frontend/start-local.sh
```

The web app runs at http://localhost:8013/ and proxies `/api` to the API at
http://localhost:8000. The FastAPI application is in `argos/backend/` and is
managed with the root `pyproject.toml` and `uv.lock`. The prepared project-local
Node.js 24 runtime remains under the ignored `.argos/frontend-tooling/` path.
The API endpoint is `GET /api/v1/health`; it confirms process availability only.

```bash
uv run pytest
uv run ruff check argos/backend
cd argos/frontend
npm run test
npm run typecheck
npm run lint
```

The frontend tests/build run from `argos/frontend` with `npm run check`;
Playwright E2E tests use `npm run test:e2e`. See
[frontend instructions](argos/frontend/README.md),
[frontend plan](docs/development/frontend/PLAN_FRONTEND.md), and the
[architecture proposal](docs/architecture/README.md).
