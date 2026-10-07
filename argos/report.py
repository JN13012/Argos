"""Render a reproducible Markdown report without embedding evidence contents."""

from collections import Counter
import html
import re

from .storage import document_digest
from .validation import SEVERITIES


def _escape(value):
    text = html.escape(" ".join(value.splitlines()), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>])", r"\\\1", text)


def render_report(document):
    mission = document["mission"]
    findings = sorted(document["findings"], key=lambda f: (SEVERITIES.index(f["severity"]), f["id"]))
    counts = Counter(item["severity"] for item in findings)
    reviews = Counter(item["review"]["decision"] if item["review"] else "needs_review"
                      for item in findings)
    lines = [
        "# Argos — Offline assessment report", "",
        "## Mission", "",
        f"**Title:** {_escape(mission['title'])}", "",
        f"**ID:** {_escape(mission['id'])}", "",
        _escape(mission["description"]), "",
        f"**Assessment SHA-256:** {document_digest(document)}", "",
        "**Scope:**", "",
        *[f"- {_escape(asset)}" for asset in sorted(mission["scope"])], "",
        "## Review summary", "",
        f"Findings: {len(findings)}. Accepted: {reviews['accepted']}. "
        f"Rejected: {reviews['rejected']}. Needs review: {reviews['needs_review']}.", "",
        "Evidence integrity and a recorded review decision do not establish that a "
        "vulnerability has been technically confirmed. Severity and provenance are "
        "declared by the input author. Rejected and unreviewed findings remain visible.", "",
        "| Declared severity | Findings |", "| --- | ---: |",
        *[f"| {level} | {counts[level]} |" for level in SEVERITIES], "",
        "## Findings", "",
    ]
    if not findings:
        lines.extend(["No findings were imported. This does not establish the absence of vulnerabilities.", ""])
    for item in findings:
        review = item["review"]
        lines.extend([
            f"### {_escape(item['id'])} — {_escape(item['title'])}", "",
            f"**Declared severity:** {item['severity']}", "",
            f"**Asset:** {_escape(item['asset'])}", "",
            f"**Review:** {review['decision'] if review else 'needs_review'}", "",
            _escape(item["description"]), "",
            f"**Recommendation:** {_escape(item['recommendation'])}", "",
            "**Evidence IDs:** " + ", ".join(_escape(ref) for ref in sorted(item["evidence_ids"])), "",
        ])
        if review:
            lines.extend([f"**Reviewer:** {_escape(review['reviewer'])}", "",
                          f"**Review reason:** {_escape(review['reason'])}", ""])
    lines.extend(["## Evidence register", ""])
    if not document["evidence"]:
        lines.extend(["No evidence was imported.", ""])
    for item in sorted(document["evidence"], key=lambda e: e["id"]):
        lines.extend([
            f"### {_escape(item['id'])}", "",
            f"**File:** {_escape(item['path'])}", "",
            f"**SHA-256:** {item['sha256']}", "",
            f"**Declared source:** {_escape(item['source'])}", "",
            _escape(item["description"]), "",
        ])
    return "\n".join(lines)
