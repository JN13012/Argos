"""Keep the bundled dashboard report tied to the original offline implementation."""

from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from argos.report import render_report
from argos.storage import load_document
from argos.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]


class DashboardReportTests(unittest.TestCase):
    def test_bundled_report_reproduces_the_displayed_dossier_offline(self):
        document = load_document(ROOT / "frontend/src/fixtures/workspace.json")
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
            validate_document(document, ROOT / "examples/offline")
            report = render_report(document)
        expected = (ROOT / "frontend/assets/mission-report.md").read_text(encoding="utf-8")
        self.assertEqual(report, expected)


if __name__ == "__main__":
    unittest.main()
