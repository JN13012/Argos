"""Validate the version-one data contract and local evidence references."""

import hashlib
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

from .storage import ValidationError


SEVERITIES = ("critical", "high", "medium", "low", "info")
DECISIONS = ("accepted", "rejected")
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024
ID_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}"


def _fail(location, message):
    raise ValidationError(f"{location}: {message}")


def _object(value, fields, location):
    if not isinstance(value, dict):
        _fail(location, "expected an object")
    if set(value) != set(fields):
        _fail(location, "missing or unknown fields")


def _text(value, location, *, limit=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        _fail(location, f"expected a non-empty string of at most {limit} characters")
    if any(ord(char) < 32 and char not in "\n\r\t" for char in value):
        _fail(location, "control characters are not allowed")
    try:
        value.encode("utf-8")
    except UnicodeError:
        _fail(location, "expected valid Unicode text")


def _identifier(value, location):
    if not isinstance(value, str) or re.fullmatch(ID_PATTERN, value) is None:
        _fail(location, "expected a 1–64 character ASCII identifier")


def _list(value, location, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        _fail(location, "expected a non-empty array" if nonempty else "expected an array")


def _records(value, fields, location):
    _list(value, location)
    seen = set()
    for index, record in enumerate(value):
        here = f"{location}[{index}]"
        _object(record, fields, here)
        _identifier(record["id"], here + ".id")
        if record["id"] in seen:
            _fail(here + ".id", "duplicate identifier")
        seen.add(record["id"])
    return seen


def evidence_path(root, relative, location):
    _text(relative, location, limit=512)
    posix = PurePosixPath(relative)
    if (
        posix.is_absolute() or PureWindowsPath(relative).drive
        or "\\" in relative or ".." in posix.parts
        or ":" in relative or posix == PurePosixPath(".")
    ):
        _fail(location, "expected a relative file path without traversal")
    try:
        root = Path(root).resolve()
        path = (root / relative).resolve()
        path.relative_to(root)
    except (ValueError, RuntimeError, OSError):
        _fail(location, "evidence path escapes its root or cannot be resolved")
    if not path.is_file():
        _fail(location, "evidence file is missing or not a regular file")
    return path


def _verify_evidence(record, root, location):
    digest = record["sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        _fail(location + ".sha256", "expected a lowercase SHA-256 digest")
    path = evidence_path(root, record["path"], location + ".path")
    with path.open("rb") as stream:
        raw = stream.read(MAX_EVIDENCE_BYTES + 1)
    if len(raw) > MAX_EVIDENCE_BYTES:
        _fail(location + ".path", "evidence exceeds the 5 MiB limit")
    if hashlib.sha256(raw).hexdigest() != digest:
        _fail(location + ".sha256", "evidence content does not match its digest")
    for field in ("description", "source"):
        _text(record[field], location + "." + field)


def validate_document(document, evidence_root):
    _object(document, ("schema_version", "mission", "evidence", "findings"), "assessment")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        _fail("schema_version", "only integer version 1 is supported")
    mission = document["mission"]
    _object(mission, ("id", "title", "description", "scope"), "mission")
    _identifier(mission["id"], "mission.id")
    _text(mission["title"], "mission.title", limit=200)
    _text(mission["description"], "mission.description")
    _list(mission["scope"], "mission.scope", nonempty=True)
    scope = set()
    for index, asset in enumerate(mission["scope"]):
        _text(asset, f"mission.scope[{index}]", limit=200)
        if asset in scope:
            _fail("mission.scope", "duplicate asset")
        scope.add(asset)

    evidence_ids = _records(document["evidence"],
                            ("id", "path", "sha256", "description", "source"), "evidence")
    for index, record in enumerate(document["evidence"]):
        _verify_evidence(record, evidence_root, f"evidence[{index}]")

    _records(document["findings"],
             ("id", "title", "severity", "asset", "description", "recommendation",
              "evidence_ids", "review"), "findings")
    for index, record in enumerate(document["findings"]):
        location = f"findings[{index}]"
        for field in ("title", "asset", "description", "recommendation"):
            _text(record[field], location + "." + field,
                  limit=200 if field in ("title", "asset") else 4000)
        if record["severity"] not in SEVERITIES:
            _fail(location + ".severity", "unknown severity")
        if record["asset"] not in scope:
            _fail(location + ".asset", "asset is outside the declared scope")
        _list(record["evidence_ids"], location + ".evidence_ids", nonempty=True)
        references = set()
        for ref in record["evidence_ids"]:
            _identifier(ref, location + ".evidence_ids")
            if ref not in evidence_ids:
                _fail(location + ".evidence_ids", "unknown evidence reference")
            if ref in references:
                _fail(location + ".evidence_ids", "duplicate evidence reference")
            references.add(ref)
        review = record["review"]
        if review is not None:
            _object(review, ("decision", "reviewer", "reason"), location + ".review")
            if review["decision"] not in DECISIONS:
                _fail(location + ".review.decision", "unknown review decision")
            _text(review["reviewer"], location + ".review.reviewer", limit=200)
            _text(review["reason"], location + ".review.reason")
    return document


def protected_evidence(document, root):
    return [Path(root) / item["path"] for item in document["evidence"]]
