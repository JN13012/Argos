import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from argos.storage import MAX_DOCUMENT_BYTES, ValidationError, load_document
from argos.validation import MAX_EVIDENCE_BYTES, validate_document


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "offline"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.document = load_document(EXAMPLE / "assessment.json")

    def test_synthetic_assessment_passes(self):
        validate_document(self.document, EXAMPLE)

    def test_invalid_structures_are_rejected(self):
        cases = [
            ("boolean version", lambda d: d.update(schema_version=True)),
            ("unsupported version", lambda d: d.update(schema_version=2)),
            ("unknown field", lambda d: d["mission"].update(extra=True)),
            ("blank title", lambda d: d["mission"].update(title=" \n")),
            ("invalid identifier", lambda d: d["mission"].update(id="../mission")),
            ("empty scope", lambda d: d["mission"].update(scope=[])),
            ("duplicate scope", lambda d: d["mission"]["scope"].append("training-fixtures")),
            ("duplicate finding", lambda d: d["findings"].append(copy.deepcopy(d["findings"][0]))),
            ("duplicate evidence", lambda d: d["evidence"].append(copy.deepcopy(d["evidence"][0]))),
            ("unknown reference", lambda d: d["findings"][0].update(evidence_ids=["E-999"])),
            ("duplicate reference", lambda d: d["findings"][0].update(evidence_ids=["E-001", "E-001"])),
            ("missing reference", lambda d: d["findings"][0].update(evidence_ids=[])),
            ("out of scope", lambda d: d["findings"][0].update(asset="another-asset")),
            ("unknown severity", lambda d: d["findings"][0].update(severity="urgent")),
            ("missing reviewer", lambda d: d["findings"][0].update(review={"decision": "accepted", "reviewer": "", "reason": "Review"})),
            ("unknown decision", lambda d: d["findings"][0].update(review={"decision": "confirmed", "reviewer": "Demo", "reason": "Review"})),
            ("control character", lambda d: d["findings"][0].update(description="text\x1b")),
            ("unpaired surrogate", lambda d: d["mission"].update(title="\ud800")),
        ]
        for name, change in cases:
            with self.subTest(name=name):
                document = copy.deepcopy(self.document)
                change(document)
                with self.assertRaises(ValidationError):
                    validate_document(document, EXAMPLE)
        for value in ([], None, "assessment", 1):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_document(value, EXAMPLE)

    def test_missing_file_and_hash_mismatch_are_rejected(self):
        for field, value, message in (("path", "evidence/missing.txt", "missing"),
                                       ("sha256", "0" * 64, "does not match")):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                document["evidence"][0][field] = value
                with self.assertRaisesRegex(ValidationError, message):
                    validate_document(document, EXAMPLE)

    def test_modified_evidence_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(EXAMPLE / "evidence", root / "evidence")
            validate_document(self.document, root)
            (root / "evidence" / "configuration.txt").write_text("modified evidence")
            with self.assertRaisesRegex(ValidationError, "does not match"):
                validate_document(self.document, root)

    def test_absolute_and_traversal_paths_are_rejected(self):
        for path in ("../assessment.json", "/etc/passwd", "C:/private.txt",
                     "C:\\private.txt", "//server/share/file", ".", "evidence/../../file"):
            with self.subTest(path=path):
                document = copy.deepcopy(self.document)
                document["evidence"][0]["path"] = path
                with self.assertRaisesRegex(ValidationError, "relative file path"):
                    validate_document(document, EXAMPLE)

    def test_symlink_outside_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "root"
            root.mkdir()
            outside = Path(folder) / "outside.txt"
            outside.write_text("outside")
            (root / "link.txt").symlink_to(outside)
            document = copy.deepcopy(self.document)
            document["evidence"][0]["path"] = "link.txt"
            with self.assertRaisesRegex(ValidationError, "escapes its root"):
                validate_document(document, root)

    def test_large_evidence_is_rejected_before_hashing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with (root / "large.txt").open("wb") as stream:
                stream.truncate(MAX_EVIDENCE_BYTES + 1)
            document = copy.deepcopy(self.document)
            document["evidence"][0]["path"] = "large.txt"
            with self.assertRaisesRegex(ValidationError, "5 MiB"):
                validate_document(document, root)

    def test_json_duplicate_keys_invalid_encoding_and_numbers_are_rejected(self):
        for raw in (b'{"id":1,"id":2}', b'{"mission":{"id":1,"id":2}}',
                    b'{"value":NaN}', b'{"value":Infinity}', b'{"value":\xff}', b'{invalid'):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "invalid.json"
                path.write_bytes(raw)
                with self.assertRaises(ValidationError):
                    load_document(path)

    def test_large_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "large.json"
            path.write_bytes(b" " * (MAX_DOCUMENT_BYTES + 1))
            with self.assertRaisesRegex(ValidationError, "1 MiB"):
                load_document(path)


if __name__ == "__main__":
    unittest.main()
