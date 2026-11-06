"""
management command: discover_judicial_dataset

Discovers and selects a balanced multi-year subset of judgments from the
public Indian Supreme Court Judgments Open Dataset on AWS Open Data.

Usage:
    python manage.py discover_judicial_dataset
    python manage.py discover_judicial_dataset --limit 100
    python manage.py discover_judicial_dataset --limit 10 --years 1950,1960,1970
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.data_ingestion.judicial_dataset.discovery import (
    discover_supreme_court_subset,
    write_manifest_csv,
    DEFAULT_SAMPLE_YEARS,
)


class Command(BaseCommand):
    help = "Discover and select a controlled subset of Supreme Court judgments from AWS Open Data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Total number of judgments to select (default: 100).",
        )
        parser.add_argument(
            "--years",
            type=str,
            default=None,
            help="Comma-separated years to sample from, e.g. '1950,1960,1970'.",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Custom path for manifest CSV output.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for reproducible selection.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        seed = options["seed"]
        years_opt = options["years"]
        if years_opt:
            years = [int(y.strip()) for y in years_opt.split(",") if y.strip().isdigit()]
        else:
            years = DEFAULT_SAMPLE_YEARS

        default_out = os.path.join(
            settings.BASE_DIR, "data", "judicial", "manifests", "supreme_court_phase1.csv"
        )
        output_file = options["output"] or default_out
        cache_dir = os.path.join(settings.BASE_DIR, "data", "judicial", "raw", "metadata")

        self.stdout.write(self.style.WARNING(
            f"[discover_judicial_dataset] Sampling target: {limit} cases across years: {years}"
        ))

        records = discover_supreme_court_subset(
            target_count=limit,
            years=years,
            cache_dir=cache_dir,
            random_seed=seed,
        )

        write_manifest_csv(records, output_file)

        self.stdout.write(self.style.SUCCESS(
            f"[discover_judicial_dataset] Successfully selected {len(records)} judgments.\n"
            f"Manifest saved to: {output_file}"
        ))

