"""
management command: download_judicial_dataset

Downloads PDFs corresponding to entries in the judicial dataset manifest CSV.

Usage:
    python manage.py download_judicial_dataset
    python manage.py download_judicial_dataset --limit 10
    python manage.py download_judicial_dataset --manifest data/judicial/manifests/supreme_court_phase1.csv
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.data_ingestion.judicial_dataset.downloader import download_manifest_pdfs


class Command(BaseCommand):
    help = "Download selected judicial judgment PDFs from public AWS S3 bucket."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            type=str,
            default=None,
            help="Path to manifest CSV (default: data/judicial/manifests/supreme_court_phase1.csv).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional limit on how many PDFs to download (useful for initial test run).",
        )

    def handle(self, *args, **options):
        default_manifest = os.path.join(
            settings.BASE_DIR, "data", "judicial", "manifests", "supreme_court_phase1.csv"
        )
        manifest_path = options["manifest"] or default_manifest
        limit = options["limit"]

        if not os.path.isfile(manifest_path):
            raise CommandError(
                f"Manifest file not found: {manifest_path}\n"
                "Run 'python manage.py discover_judicial_dataset' first to generate the manifest."
            )

        self.stdout.write(self.style.WARNING(
            f"[download_judicial_dataset] Downloading PDFs from manifest: {manifest_path} (limit={limit})"
        ))

        summary = download_manifest_pdfs(
            manifest_filepath=manifest_path,
            base_dir=str(settings.BASE_DIR),
            limit=limit,
        )

        self.stdout.write(self.style.SUCCESS(
            f"\n[download_judicial_dataset] Download completed:\n"
            f"  Target rows      : {summary['total']}\n"
            f"  Newly downloaded : {summary['downloaded']}\n"
            f"  Already existed  : {summary['already_existed']}\n"
            f"  Failed           : {summary['failed']}"
        ))

