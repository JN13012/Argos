"""Local mission creation, import, review and reporting commands."""

import argparse
import copy
from pathlib import Path
import sys

from . import __version__
from .report import render_report
from .storage import ValidationError, json_text, load_document, write_output
from .validation import DECISIONS, protected_evidence, validate_document


def _output_options(parser, *, required=True):
    parser.add_argument("--output", type=Path, required=required)
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")


def _input_options(parser):
    parser.add_argument("input", type=Path, help="Assessment JSON document")
    parser.add_argument("--evidence-root", type=Path, help="Evidence root (default: input directory)")


def _parser():
    parser = argparse.ArgumentParser(prog="argos", description="Argos Core — offline evidence and reporting")
    parser.add_argument("--version", action="version", version=f"Argos Core {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create an empty mission document")
    init.add_argument("--id", required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--description", required=True)
    init.add_argument("--scope", action="append", required=True, help="Repeat for each declared asset")
    _output_options(init)
    validate = commands.add_parser("validate", help="Validate data, scope and evidence integrity")
    _input_options(validate)
    report = commands.add_parser("report", help="Render a deterministic Markdown report")
    _input_options(report)
    _output_options(report, required=False)
    review = commands.add_parser("review", help="Record a human review in a new document")
    _input_options(review)
    review.add_argument("--finding", required=True)
    review.add_argument("--decision", choices=DECISIONS, required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--reason", required=True)
    _output_options(review)
    ingest = commands.add_parser("import", help="Import findings and evidence for the same mission")
    _input_options(ingest)
    ingest.add_argument("--from-file", type=Path, required=True)
    _output_options(ingest)
    return parser


def _run(args):
    if args.command == "init":
        document = {
            "schema_version": 1,
            "mission": {"id": args.id, "title": args.title,
                        "description": args.description, "scope": args.scope},
            "evidence": [], "findings": [],
        }
        validate_document(document, args.output.parent)
        write_output(args.output, json_text(document, bounded=True), force=args.force)
        print(f"Created mission {args.id}: {args.output}")
        return
    source = args.from_file if args.command == "import" else args.input
    root = args.evidence_root or source.parent
    document = validate_document(load_document(args.input), root)
    protected = [args.input, *protected_evidence(document, root)]
    if args.command == "validate":
        print(f"Valid assessment: {len(document['findings'])} findings, "
              f"{len(document['evidence'])} evidence files verified")
        return
    if args.command == "report":
        text = render_report(document)
        if args.output is None:
            if args.force:
                raise ValidationError("--force requires --output")
            sys.stdout.write(text)
            return
    else:
        document = copy.deepcopy(document)
        if args.command == "review":
            finding = next((item for item in document["findings"] if item["id"] == args.finding), None)
            if finding is None:
                raise ValidationError("Review refers to an unknown finding")
            finding["review"] = {"decision": args.decision, "reviewer": args.reviewer, "reason": args.reason}
        else:
            imported = validate_document(load_document(args.from_file), root)
            if (document["mission"]["id"] != imported["mission"]["id"]
                    or set(document["mission"]["scope"]) != set(imported["mission"]["scope"])):
                raise ValidationError("Import requires the same mission ID and scope")
            document["evidence"].extend(imported["evidence"])
            document["findings"].extend(imported["findings"])
            protected.extend([args.from_file, *protected_evidence(imported, root)])
        validate_document(document, root)
        text = json_text(document, bounded=True)
    write_output(args.output, text, force=args.force, protected=protected)
    print(f"Wrote {args.output}")


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        _run(args)
    except ValidationError as exc:
        print(f"argos: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"argos: file operation failed: {exc.strerror or type(exc).__name__}", file=sys.stderr)
        return 1
    return 0
