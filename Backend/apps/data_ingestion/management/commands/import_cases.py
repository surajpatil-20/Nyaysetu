"""
management command: import_cases

Usage:
    python manage.py import_cases --file data/raw/demo_cases.csv
    python manage.py import_cases --file data/raw/demo_cases.json
    python manage.py import_cases --file data/raw/demo_cases.csv --dry-run
"""
import os
from django.core.management.base import BaseCommand, CommandError
from apps.data_ingestion.importers.csv_importer import import_csv
from apps.data_ingestion.importers.json_importer import import_json


class Command(BaseCommand):
    help = "Import judicial case records from a CSV or JSON file into NYAYASETU."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Path to the input file (CSV or JSON).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Validate and count records but do not write to the database.",
        )

    def handle(self, *args, **options):
        filepath = options["file"]
        dry_run = options["dry_run"]

        if not os.path.isfile(filepath):
            raise CommandError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            importer = import_csv
        elif ext == ".json":
            importer = import_json
        else:
            raise CommandError(f"Unsupported file type '{ext}'. Use .csv or .json")

        self.stdout.write(self.style.WARNING(
            f"[import_cases] {'DRY RUN — ' if dry_run else ''}Importing from: {filepath}"
        ))

        summary = importer(filepath, dry_run=dry_run)

        self.stdout.write(self.style.SUCCESS(
            f"\n[import_cases] Done!\n"
            f"  Total rows : {summary['total']}\n"
            f"  Created    : {summary['created']}\n"
            f"  Updated    : {summary['updated']}\n"
            f"  Skipped    : {summary['skipped']}\n"
            f"  Errors     : {summary['errors']}\n"
            f"  Dry run    : {summary['dry_run']}"
        ))

        if summary["errors"] > 0:
            self.stdout.write(self.style.ERROR(
                f"[import_cases] {summary['errors']} record(s) failed validation or import."
            ))

