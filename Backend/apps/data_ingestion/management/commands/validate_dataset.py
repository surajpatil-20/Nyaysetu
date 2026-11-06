"""
management command: validate_dataset

Usage:
    python manage.py validate_dataset --file data/raw/demo_cases.csv
    python manage.py validate_dataset --file data/raw/demo_cases.json
"""
import csv
import json
import os
from django.core.management.base import BaseCommand, CommandError
from apps.data_ingestion.validators import validate_csv_row, validate_case_record


class Command(BaseCommand):
    help = "Validate a dataset file (CSV or JSON) without writing to the database."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to CSV or JSON file.")

    def handle(self, *args, **options):
        filepath = options["file"]
        if not os.path.isfile(filepath):
            raise CommandError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        total = 0
        valid_count = 0
        invalid_count = 0
        warnings_count = 0

        self.stdout.write(f"[validate_dataset] Validating: {filepath}\n")

        if ext == ".csv":
            with open(filepath, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row_num, row in enumerate(reader, start=2):
                    total += 1
                    vr = validate_csv_row(row, row_num)
                    if vr.is_valid:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        for err in vr.errors:
                            self.stdout.write(self.style.ERROR(f"  ERROR [{err.field}]: {err.message}"))
                    for warn in vr.warnings:
                        warnings_count += 1
                        self.stdout.write(self.style.WARNING(f"  WARN  [{warn.field}]: {warn.message}"))

        elif ext == ".json":
            with open(filepath, encoding="utf-8") as fh:
                try:
                    records = json.load(fh)
                except json.JSONDecodeError as exc:
                    raise CommandError(f"Invalid JSON: {exc}")
            if not isinstance(records, list):
                raise CommandError("JSON must be a top-level list of objects.")
            for row_num, record in enumerate(records, start=1):
                total += 1
                vr = validate_case_record(record)
                if vr.is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    for err in vr.errors:
                        self.stdout.write(self.style.ERROR(f"  ERROR [record {row_num}] [{err.field}]: {err.message}"))
                for warn in vr.warnings:
                    warnings_count += 1
                    self.stdout.write(self.style.WARNING(f"  WARN  [record {row_num}] [{warn.field}]: {warn.message}"))
        else:
            raise CommandError(f"Unsupported file type '{ext}'. Use .csv or .json")

        self.stdout.write(
            f"\n[validate_dataset] Summary:\n"
            f"  Total      : {total}\n"
            f"  Valid      : {valid_count}\n"
            f"  Invalid    : {invalid_count}\n"
            f"  Warnings   : {warnings_count}"
        )

        if invalid_count == 0:
            self.stdout.write(self.style.SUCCESS("[validate_dataset] All records passed validation."))
        else:
            self.stdout.write(self.style.ERROR(f"[validate_dataset] {invalid_count} record(s) failed validation."))

