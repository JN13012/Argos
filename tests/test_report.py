import copy
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from argos.report import render_report
from argos.storage import load_document
from argos.validation import validate_document


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "offline"


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.document = load_document(EXAMPLE / "assessment.json")

    def test_reference_report_and_repeated_runs_match(self):
        expected = (EXAMPLE / "report.md").read_text(encoding="utf-8")
        self.assertEqual(render_report(self.document), expected)
        self.assertEqual(render_report(self.document), render_report(copy.deepcopy(self.document)))

    def test_pending_and_rejected_findings_remain_visible(self):
        self.document["findings"][0]["review"] = {
            "decision": "rejected", "reviewer": "Demo reviewer", "reason": "Synthetic observation only.",
        }
        report = render_report(self.document)
        self.assertIn("Rejected: 1. Needs review: 1.", report)
        self.assertIn("**Review:** rejected", report)
        self.assertIn("**Review:** needs_review", report)
        self.assertIn("Synthetic observation only", report)
        self.assertNotIn("**Review:** confirmed", report)

    def test_markdown_html_and_linebreaks_are_escaped(self):
        self.document["findings"][0]["title"] = '<script>alert(1)</script>\n# Forged [link](https://example.test)'
        report = render_report(self.document)
        self.assertNotIn("<script>", report)
        self.assertNotIn("\n# Forged", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertIn(r"\[link\]", report)

    def test_no_findings_does_not_claim_security(self):
        self.document["findings"] = []
        self.document["evidence"] = []
        self.assertIn("does not establish the absence of vulnerabilities", render_report(self.document))

    def test_report_and_validation_do_not_use_network_or_embed_evidence(self):
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
            validate_document(self.document, EXAMPLE)
            report = render_report(self.document)
        self.assertNotIn("debug_mode=true", report)
        self.assertIn(self.document["evidence"][0]["sha256"], report)


if __name__ == "__main__":
    unittest.main()
