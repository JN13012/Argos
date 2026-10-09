# Working on Argos

The current authorized implementation is the offline deliverable described in
`doc/livrables/FIRST_DELIVERABLE.md`. The broader V0 scope remains a draft. Read the
deliverable before changing its data contract or behavior.

- Original code lives in `argos/`; synthetic fixtures in `examples/offline/`.
- Use Python 3.11+ and the standard library for this deliverable.
- Imported files under `Harness/` are references with unresolved provenance;
  keep them separate from the original implementation and tests.
- Keep generated mission data and reports under ignored `.argos/` locally.
- Preserve input documents; validation and reporting must not contact a network
  or execute imported code. Verify evidence files and escape report text.
- Update the schema, deliverable and meaningful tests together when changing the
  public data contract. Do not promote the broader V0 scope implicitly.

Required checks for implementation changes:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
git diff --check
```

Documentation is indexed in `doc/README.md`. The demo and reference report are
described in `doc/guides/DEMARRAGE.md`. The workflow in
`.github/workflows/checks.yml` runs the same offline tests on several interpreters.
