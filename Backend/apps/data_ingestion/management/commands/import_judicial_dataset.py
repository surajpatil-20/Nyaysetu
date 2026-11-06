"""
management command: import_judicial_dataset

Imports judicial dataset entries from a manifest CSV into PostgreSQL.
Supports --dry-run, --process, and --embed.

Usage:
    # Dry run
    python manage.py import_judicial_dataset --dry-run
    # Import 10 cases with extraction and embeddings
    python manage.py import_judicial_dataset --limit 10 --process --embed
    # Full import
    python manage.py import_judicial_dataset --process --embed
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.data_ingestion.judicial_dataset.importer import import_judicial_dataset


class Command(BaseCommand):
    help = "Import judicial dataset records and PDFs into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            type=str,
            default=None,
            help="Path to manifest CSV.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of rows to import (e.g. for small test run).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Simulate import without modifying database.",
        )
        parser.add_argument(
            "--process",
            action="store_true",
            default=False,
            help="Automatically run text extraction and chunking for imported PDFs.",
        )
        parser.add_argument(
            "--embed",
            action="store_true",
            default=False,
            help="Automatically generate 768-dim embeddings after chunking.",
        )

    def handle(self, *args, **options):
        default_manifest = os.path.join(
            settings.BASE_DIR, "data", "judicial", "manifests", "supreme_court_phase1.csv"
        )
        manifest_path = options["manifest"] or default_manifest
        limit = options["limit"]
        dry_run = options["dry_run"]
        auto_process = options["process"]
        auto_embed = options["embed"]

        if not os.path.isfile(manifest_path):
            raise CommandError(
                f"Manifest file not found: {manifest_path}\n"
                "Run 'python manage.py discover_judicial_dataset' first to generate the manifest."
            )

        self.stdout.write(self.style.WARNING(
            f"[import_judicial_dataset] {'DRY RUN — ' if dry_run else ''}"
            f"Importing from {manifest_path} (limit={limit}, process={auto_process}, embed={auto_embed})"
        ))

        summary = import_judicial_dataset(
            manifest_filepath=manifest_path,
            base_dir=str(settings.BASE_DIR),
            limit=limit,
            dry_run=dry_run,
            auto_process=auto_process,
            auto_embed=auto_embed,
        )

        self.stdout.write(self.style.SUCCESS(
            f"\n[import_judicial_dataset] Done!\n"
            f"  Total processed  : {summary['total']}\n"
            f"  Created          : {summary['created']}\n"
            f"  Updated          : {summary['updated']}\n"
            f"  Documents linked : {summary['documents_linked']}\n"
            f"  Invalid metadata : {summary['invalid']}\n"
            f"  Dry run mode     : {summary['dry_run']}"
        ))

