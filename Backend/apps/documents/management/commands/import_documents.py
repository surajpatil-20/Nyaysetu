"""
management command: import_documents

Imports judicial PDF documents into NYAYASETU and links them to cases.
Can process files directly or parse a metadata manifest (CSV or JSON).

Usage examples:
    # Single file
    python manage.py import_documents --file data/documents/judgment_1234.pdf --case-number "W.P.(C) 1234/2023" --title "Final Judgment" --process --embed

    # Manifest file
    python manage.py import_documents --manifest data/documents/manifest.csv --process --embed
"""
import os
import csv
import json
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from apps.cases.models import Case
from apps.documents.models import Document
from apps.documents.services.extraction import process_document
from apps.documents.services.chunking import chunk_document
from apps.documents.services.embeddings import generate_embeddings_for_document


class Command(BaseCommand):
    help = "Import judicial PDF documents and link them to Cases."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Path to a single PDF document.")
        parser.add_argument("--case-number", help="Case docket number to associate with the document.")
        parser.add_argument("--title", help="Document title.")
        parser.add_argument("--document-type", default="JUDGMENT", help="JUDGMENT | FINAL_ORDER | INTERIM_ORDER | PETITION | OTHER")
        parser.add_argument("--source-name", default="DEMO SOURCE", help="Source repository caption.")
        parser.add_argument("--source-url", default="", help="Public source URL.")
        parser.add_argument("--manifest", help="Path to CSV or JSON manifest listing multiple documents.")
        parser.add_argument("--process", action="store_true", default=False, help="Automatically run text extraction and chunking.")
        parser.add_argument("--embed", action="store_true", default=False, help="Automatically generate embeddings after chunking.")
        parser.add_argument("--dry-run", action="store_true", default=False, help="Simulate without writing to database.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        auto_process = options["process"]
        auto_embed = options["embed"]

        if options["manifest"]:
            self._import_from_manifest(options["manifest"], dry_run, auto_process, auto_embed)
        elif options["file"]:
            if not options["case_number"]:
                raise CommandError("--case-number is required when using --file.")
            self._import_single_file(
                filepath=options["file"],
                case_number=options["case_number"],
                title=options.get("title"),
                doc_type=options.get("document_type", "JUDGMENT"),
                source_name=options.get("source_name", "DEMO SOURCE"),
                source_url=options.get("source_url", ""),
                dry_run=dry_run,
                auto_process=auto_process,
                auto_embed=auto_embed,
            )
        else:
            raise CommandError("Please specify either --file or --manifest.")

    def _import_single_file(self, filepath, case_number, title, doc_type, source_name, source_url, dry_run, auto_process, auto_embed):
        if not os.path.isfile(filepath):
            raise CommandError(f"File not found: {filepath}")

        try:
            case = Case.objects.get(case_number=case_number)
        except Case.DoesNotExist:
            raise CommandError(f"Case with number '{case_number}' not found. Please import cases first.")

        doc_title = title or os.path.basename(filepath)

        self.stdout.write(f"Importing '{filepath}' for Case #{case.case_number}...")

        if dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN] Would link document to case."))
            return

        with open(filepath, "rb") as fh:
            doc, created = Document.objects.get_or_create(
                case=case,
                title=doc_title,
                defaults={
                    "document_type": doc_type,
                    "source_name": source_name,
                    "source_url": source_url or None,
                }
            )
            doc.file.save(os.path.basename(filepath), File(fh), save=True)

        self.stdout.write(self.style.SUCCESS(f"  ✓ Document #{doc.pk} stored: {doc.title}"))

        if auto_process:
            self.stdout.write("  Extracting text and chunking...")
            if process_document(doc):
                n_chunks = chunk_document(doc)
                self.stdout.write(self.style.SUCCESS(f"    ✓ Extracted and created {n_chunks} chunk(s)"))
                if auto_embed:
                    self.stdout.write("    Generating embeddings...")
                    emb_summary = generate_embeddings_for_document(doc)
                    self.stdout.write(self.style.SUCCESS(f"    ✓ {emb_summary['processed']} chunks embedded"))
            else:
                self.stdout.write(self.style.ERROR("    ✗ Extraction failed"))

    def _import_from_manifest(self, manifest_path, dry_run, auto_process, auto_embed):
        if not os.path.isfile(manifest_path):
            raise CommandError(f"Manifest not found: {manifest_path}")

        records = []
        ext = os.path.splitext(manifest_path)[1].lower()
        if ext == ".csv":
            with open(manifest_path, newline="", encoding="utf-8") as fh:
                records = list(csv.DictReader(fh))
        elif ext == ".json":
            with open(manifest_path, encoding="utf-8") as fh:
                records = json.load(fh)
        else:
            raise CommandError("Manifest must be .csv or .json")

        self.stdout.write(f"Processing manifest with {len(records)} entries...")
        for row in records:
            fpath = row.get("file_path") or row.get("file")
            cnum = row.get("case_number")
            title = row.get("title")
            dtype = row.get("document_type", "JUDGMENT")
            sname = row.get("source_name", "DEMO SOURCE")
            surl = row.get("source_url", "")
            if not fpath or not cnum:
                self.stdout.write(self.style.WARNING(f"  Skipping row without file_path or case_number: {row}"))
                continue
            try:
                self._import_single_file(fpath, cnum, title, dtype, sname, surl, dry_run, auto_process, auto_embed)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  Error importing {fpath}: {exc}"))

