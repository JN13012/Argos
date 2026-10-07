# Synthetic offline example

These files were written for Argos. They contain invented training observations,
two local evidence files and an unreviewed assessment. No application, external
service or real user's data is represented.

From the repository root:

```bash
python3 -m argos validate examples/offline/assessment.json
python3 -m argos report examples/offline/assessment.json --output .argos/report.md
```

The generated file must match [report.md](report.md) byte for byte. Repeated
exports to the same path require `--force`. Each proof's SHA-256 is declared in
[assessment.json](assessment.json) and checked against the actual file.

Both findings start as `needs_review`. A decision recorded using the `review`
command is a declared human review, not a technical confirmation. The complete
creation/import/review example is in the repository README.
