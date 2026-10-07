import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from argos.storage import load_document


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "offline"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.work = Path(self.folder.name)

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, "-S", "-m", "argos", *map(str, arguments)],
                              cwd=ROOT, capture_output=True, text=True)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_report_from_clean_input_matches_reference(self):
        path = self.work / "report.md"
        result = self.run_cli("report", EXAMPLE / "assessment.json", "--output", path)
        self.assert_success(result)
        self.assertEqual(path.read_bytes(), (EXAMPLE / "report.md").read_bytes())
        self.assert_success(self.run_cli("validate", EXAMPLE / "assessment.json"))

    def test_init_import_review_report_preserves_sources(self):
        initial, imported, reviewed = [self.work / name for name in ("mission.json", "imported.json", "reviewed.json")]
        self.assert_success(self.run_cli("init", "--id", "demo-offline", "--title", "My demo",
                                        "--description", "Synthetic demonstration", "--scope", "training-fixtures",
                                        "--output", initial))
        before = initial.read_bytes()
        self.assert_success(self.run_cli("import", initial, "--from-file", EXAMPLE / "assessment.json",
                                        "--output", imported))
        imported_before = imported.read_bytes()
        self.assert_success(self.run_cli("review", imported, "--evidence-root", EXAMPLE,
                                        "--finding", "F-001", "--decision", "accepted",
                                        "--reviewer", "Demo reviewer", "--reason", "Accepted for demonstration only.",
                                        "--output", reviewed))
        result = self.run_cli("report", reviewed, "--evidence-root", EXAMPLE)
        self.assert_success(result)
        self.assertIn("Accepted: 1. Rejected: 0. Needs review: 1.", result.stdout)
        self.assertIn("Demo reviewer", result.stdout)
        self.assertEqual(initial.read_bytes(), before)
        self.assertEqual(imported.read_bytes(), imported_before)

    def test_import_collision_and_different_mission_are_rejected(self):
        for change, message in ((lambda d: None, "duplicate identifier"),
                                (lambda d: d["mission"].update(id="other-mission"), "same mission")):
            document = load_document(EXAMPLE / "assessment.json")
            change(document)
            path = self.work / "input.json"
            path.write_text(json.dumps(document))
            result = self.run_cli("import", path, "--from-file", EXAMPLE / "assessment.json",
                                  "--evidence-root", EXAMPLE, "--output", self.work / "bad.json")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn(message, result.stderr)
            self.assertFalse((self.work / "bad.json").exists())

    def test_import_cannot_produce_an_assessment_too_large_to_reload(self):
        paths = []
        for batch in (0, 1):
            document = load_document(EXAMPLE / "assessment.json")
            evidence = copy.deepcopy(document["evidence"][0])
            evidence["id"] = f"E-{batch}"
            document["evidence"] = [evidence]
            base = copy.deepcopy(document["findings"][0])
            base.update(description="d" * 4000, recommendation="r" * 4000,
                        evidence_ids=[evidence["id"]])
            document["findings"] = []
            for index in range(90):
                finding = copy.deepcopy(base)
                finding["id"] = f"F-{batch}-{index}"
                document["findings"].append(finding)
            path = self.work / f"batch-{batch}.json"
            path.write_text(json.dumps(document))
            paths.append(path)
        output = self.work / "merged.json"
        result = self.run_cli("import", paths[0], "--from-file", paths[1],
                              "--evidence-root", EXAMPLE, "--output", output)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("1 MiB", result.stderr)
        self.assertFalse(output.exists())

    def test_invalid_input_does_not_create_output_directory(self):
        document = load_document(EXAMPLE / "assessment.json")
        document["evidence"][0]["path"] = "evidence/missing.txt"
        path = self.work / "invalid.json"
        path.write_text(json.dumps(document))
        result = self.run_cli("report", path, "--evidence-root", EXAMPLE,
                              "--output", self.work / "new" / "report.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing", result.stderr)
        self.assertFalse((self.work / "new").exists())

    def test_unknown_finding_and_empty_review_reason_are_rejected(self):
        for identifier, reason in (("F-999", "Review"), ("F-001", " ")):
            result = self.run_cli("review", EXAMPLE / "assessment.json", "--finding", identifier,
                                  "--decision", "accepted", "--reviewer", "Demo", "--reason", reason,
                                  "--output", self.work / "review.json")
            self.assertEqual(result.returncode, 2)
            self.assertFalse((self.work / "review.json").exists())

    def test_overwrite_requires_force_and_never_changes_source_or_proof(self):
        report = self.work / "report.md"
        report.write_text("existing")
        args = ("report", EXAMPLE / "assessment.json", "--output", report)
        self.assertEqual(self.run_cli(*args).returncode, 2)
        self.assertEqual(report.read_text(), "existing")
        self.assert_success(self.run_cli(*args, "--force"))
        source = self.work / "source.json"
        original = (EXAMPLE / "assessment.json").read_bytes()
        source.write_bytes(original)
        result = self.run_cli("report", source, "--evidence-root", EXAMPLE, "--output", source, "--force")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(source.read_bytes(), original)
        proof = EXAMPLE / "evidence" / "configuration.txt"
        before = proof.read_bytes()
        result = self.run_cli("report", EXAMPLE / "assessment.json", "--output", proof, "--force")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(proof.read_bytes(), before)

    def test_symlink_and_hardlink_outputs_cannot_overwrite_source(self):
        source = self.work / "source.json"
        original = (EXAMPLE / "assessment.json").read_bytes()
        source.write_bytes(original)
        symlink = self.work / "symlink.md"
        symlink.symlink_to(source)
        hardlink = self.work / "hardlink.md"
        os.link(source, hardlink)
        for target in (symlink, hardlink):
            result = self.run_cli("report", source, "--evidence-root", EXAMPLE,
                                  "--output", target, "--force")
            self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(source.read_bytes(), original)

    def test_file_io_errors_are_distinct_from_validation_errors(self):
        result = self.run_cli("validate", self.work / "absent.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_version_and_help(self):
        result = self.run_cli("--version")
        self.assert_success(result)
        self.assertIn("Argos Core 0.1.0", result.stdout)
        self.assert_success(self.run_cli("--help"))


if __name__ == "__main__":
    unittest.main()
