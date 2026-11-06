"""
Tests for Judicial Dataset Acquisition and Controlled Ingestion Pipeline.
"""
import os
import tempfile
import csv
from django.test import TestCase
from apps.cases.models import Case, Party, CaseParty, CaseJudge
from apps.courts.models import Court, Judge
from apps.documents.models import Document
from apps.sources.models import Source
from apps.data_ingestion.judicial_dataset.downloader import is_valid_pdf
from apps.data_ingestion.judicial_dataset.importer import import_manifest_row, import_judicial_dataset
from apps.data_ingestion.judicial_dataset.validator import validate_manifest


SAMPLE_MANIFEST_RECORD = {
    "case_id": "1950 INSC 99",
    "title": "State of Test versus Rameshwar Lal",
    "petitioner": "State of Test",
    "respondent": "Rameshwar Lal",
    "judge": "Justice Test Kumar, Justice Alpha Sen",
    "citation": "[1950] 1 S.C.R. 999",
    "cnr": "ESCR010000991950",
    "decision_date": "15-10-1950",
    "disposal_nature": "Appeal dismissed",
    "court": "Supreme Court of India",
    "available_languages": "ENG",
    "source_path": "data/pdf/year=1950/english/test_EN.pdf",
    "source_url": "https://indian-supreme-court-judgments.s3.amazonaws.com/data/pdf/year=1950/english/test_EN.pdf",
    "dataset_name": "Indian Supreme Court Judgments Open Dataset",
    "dataset_license": "CC BY 4.0",
    "retrieved_at": "2026-11-06T00:00:00Z",
    "local_pdf_path": "",
    "download_status": "PENDING",
    "validation_status": "PENDING",
}


class JudicialDatasetDownloaderTest(TestCase):
    def test_invalid_pdf_detection(self):
        # Empty file
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        self.assertFalse(is_valid_pdf(path))
        os.remove(path)

        # Non-pdf file
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "wb") as fh:
            fh.write(b"Hello world, not a pdf file at all." * 50)
        self.assertFalse(is_valid_pdf(path))
        os.remove(path)

    def test_valid_pdf_magic_bytes(self):
        fd, path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, "wb") as fh:
            fh.write(b"%PDF-1.4\n" + b"x" * 600)
        self.assertTrue(is_valid_pdf(path))
        os.remove(path)


class JudicialDatasetImporterTest(TestCase):
    def setUp(self):
        self.court, _ = Court.objects.get_or_create(
            court_name="Supreme Court of India",
            defaults={"court_type": Court.CourtType.SUPREME_COURT, "court_code": "SCI"}
        )
        self.source, _ = Source.objects.get_or_create(
            source_name="Indian Supreme Court Judgments Open Dataset",
            defaults={"source_type": Source.SourceType.PUBLIC_ARCHIVE}
        )

    def test_import_manifest_row_creates_entities(self):
        action, case, doc = import_manifest_row(
            row=SAMPLE_MANIFEST_RECORD,
            base_dir="",
            court=self.court,
            source=self.source,
            dry_run=False,
        )
        self.assertEqual(action, "created")
        self.assertIsNotNone(case)
        self.assertEqual(case.case_number, "1950 INSC 99")
        self.assertEqual(case.cnr_number, "ESCR010000991950")
        self.assertEqual(case.court, self.court)
        self.assertEqual(case.source_name, "Indian Supreme Court Judgments Open Dataset")
        self.assertEqual(str(case.decision_date), "1950-10-15")

        # Verify parties
        self.assertEqual(CaseParty.objects.filter(case=case).count(), 2)

        # Verify judges
        self.assertEqual(CaseJudge.objects.filter(case=case).count(), 2)

    def test_idempotency_prevents_duplicate_cases(self):
        # First import
        import_manifest_row(SAMPLE_MANIFEST_RECORD, "", self.court, self.source, dry_run=False)
        # Second import of identical record
        action, case, _ = import_manifest_row(SAMPLE_MANIFEST_RECORD, "", self.court, self.source, dry_run=False)
        self.assertEqual(action, "updated")
        self.assertEqual(Case.objects.filter(cnr_number="ESCR010000991950").count(), 1)

    def test_dry_run_does_not_modify_database(self):
        action, case, doc = import_manifest_row(
            row=SAMPLE_MANIFEST_RECORD,
            base_dir="",
            court=self.court,
            source=self.source,
            dry_run=True,
        )
        self.assertEqual(action, "would_create")
        self.assertEqual(Case.objects.filter(case_number="1950 INSC 99").count(), 0)

    def test_manifest_validation(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=SAMPLE_MANIFEST_RECORD.keys())
            writer.writeheader()
            writer.writerow(SAMPLE_MANIFEST_RECORD)

        report = validate_manifest(path, base_dir="")
        self.assertEqual(report["total_records"], 1)
        self.assertEqual(report["valid_records"], 1)
        self.assertEqual(report["invalid_records"], 0)
        os.remove(path)

