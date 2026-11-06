"""
management command: validate_judicial_dataset

Validates judicial dataset manifest entries and local PDF integrity.

Usage:
    python manage.py validate_judicial_dataset
    python manage.py validate_judicial_dataset --manifest data/judicial/manifests/supreme_court_phase1.csv
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.data_ingestion.judicial_dataset.validator import validate_manifest


class Command(BaseCommand):
    help = "Validate judicial dataset manifest entries and local PDF integrity."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            type=str,
            default=None,
            help="Path to manifest CSV.",
        )

    def handle(self, *args, **options):
        default_manifest = os.path.join(
            settings.BASE_DIR, "data", "judicial", "manifests", "supreme_court_phase1.csv"
        )
        manifest_path = options["manifest"] or default_manifest

        if not os.path.isfile(manifest_path):
            raise CommandError(f"Manifest not found: {manifest_path}")

        self.stdout.write(f"[validate_judicial_dataset] Validating manifest: {manifest_path}")

        report = validate_manifest(manifest_path, base_dir=str(settings.BASE_DIR))

        self.stdout.write(
            f"\n[validate_judicial_dataset] Summary:\n"
            f"  Total records          : {report['total_records']}\n"
            f"  Valid metadata records : {report['valid_records']}\n"
            f"  Invalid metadata records: {report['invalid_records']}\n"
            f"  PDF present & valid    : {report['pdf_present_and_valid']}\n"
            f"  PDF missing or corrupt : {report['pdf_missing_or_corrupt']}\n"
            f"  Warnings count         : {len(report['warnings'])}\n"
            f"  Errors count           : {len(report['errors'])}"
        )

        if report["invalid_records"] == 0:
            self.stdout.write(self.style.SUCCESS("[validate_judicial_dataset] Metadata validation passed."))
        else:
            self.stdout.write(self.style.ERROR(f"[validate_judicial_dataset] Found {report['invalid_records']} invalid record(s)."))

