"""
Tests for data_ingestion: validators, csv_importer, json_importer.
"""
import json
import os
import tempfile
from django.test import TestCase
from apps.data_ingestion.validators import validate_case_record, validate_csv_row
from apps.data_ingestion.importers.csv_importer import import_csv
from apps.data_ingestion.importers.json_importer import import_json
from apps.cases.models import Case


VALID_RECORD = {
    "case_number": "W.P.(C) 999/2024",
    "case_title": "Test Petitioner v. Test Respondent",
    "court_name": "Test High Court",
    "court_type": "HIGH_COURT",
    "court_state": "Test State",
    "cnr_number": "",
    "case_type": "Writ Petition",
    "filing_date": "2024-01-01",
    "decision_date": "",
    "status": "PENDING",
    "description": "[DEMO DATA — NOT REAL JUDICIAL RECORD] Test description.",
    "source_url": "",
    "source_name": "TEST SOURCE",
    "petitioner": "Test Petitioner",
    "respondent": "Test Respondent",
    "judge_name": "Justice Test",
    "judge_designation": "Puisne Judge",
}


class ValidatorsTest(TestCase):
    def test_valid_record_passes(self):
        vr = validate_case_record(VALID_RECORD)
        self.assertTrue(vr.is_valid, msg=str([e.message for e in vr.errors]))

    def test_missing_case_number_fails(self):
        record = {**VALID_RECORD, "case_number": ""}
        vr = validate_case_record(record)
        self.assertFalse(vr.is_valid)
        fields = [e.field for e in vr.errors]
        self.assertIn("case_number", fields)

    def test_missing_case_title_fails(self):
        record = {**VALID_RECORD, "case_title": ""}
        vr = validate_case_record(record)
        self.assertFalse(vr.is_valid)
        fields = [e.field for e in vr.errors]
        self.assertIn("case_title", fields)

    def test_missing_court_name_fails(self):
        record = {**VALID_RECORD, "court_name": ""}
        vr = validate_case_record(record)
        self.assertFalse(vr.is_valid)
        fields = [e.field for e in vr.errors]
        self.assertIn("court_name", fields)

    def test_invalid_status_gives_warning(self):
        record = {**VALID_RECORD, "status": "GARBAGE_STATUS"}
        vr = validate_case_record(record)
        self.assertTrue(vr.is_valid)   # warning not error
        warn_fields = [w.field for w in vr.warnings]
        self.assertIn("status", warn_fields)


class CsvImporterTest(TestCase):
    def _write_csv(self, rows: list[dict]) -> str:
        import csv
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=VALID_RECORD.keys())
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_valid_csv_creates_case(self):
        path = self._write_csv([VALID_RECORD])
        summary = import_csv(path)
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["errors"], 0)
        self.assertEqual(summary["created"], 1)
        self.assertEqual(Case.objects.filter(case_number="W.P.(C) 999/2024").count(), 1)

    def test_duplicate_import_updates_not_duplicates(self):
        path = self._write_csv([VALID_RECORD])
        import_csv(path)
        summary = import_csv(path)   # second import
        self.assertEqual(summary["updated"], 1)
        self.assertEqual(Case.objects.filter(case_number="W.P.(C) 999/2024").count(), 1)

    def test_invalid_row_counted_as_error(self):
        bad = {**VALID_RECORD, "case_number": "", "case_title": ""}
        path = self._write_csv([bad])
        summary = import_csv(path)
        self.assertEqual(summary["errors"], 1)
        self.assertEqual(summary["created"], 0)

    def test_dry_run_does_not_create(self):
        path = self._write_csv([VALID_RECORD])
        summary = import_csv(path, dry_run=True)
        self.assertTrue(summary["dry_run"])
        self.assertEqual(Case.objects.filter(case_number="W.P.(C) 999/2024").count(), 0)


class JsonImporterTest(TestCase):
    def _write_json(self, records: list[dict]) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(records, fh)
        return path

    def test_valid_json_creates_case(self):
        path = self._write_json([VALID_RECORD])
        summary = import_json(path)
        self.assertEqual(summary["created"], 1)
        self.assertEqual(summary["errors"], 0)

    def test_invalid_json_errors(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write("NOT JSON {{{{")
        summary = import_json(path)
        self.assertGreater(summary["errors"], 0)

