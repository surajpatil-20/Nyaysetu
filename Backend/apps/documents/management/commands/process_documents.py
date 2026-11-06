"""
management command: process_documents

Extracts text from PDF documents and runs chunking.

Usage:
    python manage.py process_documents
    python manage.py process_documents --document-id 5
    python manage.py process_documents --case-id 3
    python manage.py process_documents --limit 10
    python manage.py process_documents --dry-run
"""
from django.core.management.base import BaseCommand
from apps.documents.models import Document
from apps.documents.services.extraction import process_document
from apps.documents.services.chunking import chunk_document


class Command(BaseCommand):
    help = "Extract text from documents and chunk them for search and RAG."

    def add_arguments(self, parser):
        parser.add_argument("--document-id", type=int, default=None, help="Process a specific Document ID.")
        parser.add_argument("--case-id", type=int, default=None, help="Process all documents for a case.")
        parser.add_argument("--limit", type=int, default=None, help="Max number of documents to process.")
        parser.add_argument("--force", action="store_true", default=False, help="Re-process already-completed documents.")
        parser.add_argument("--dry-run", action="store_true", default=False, help="Show what would be processed without doing it.")

    def handle(self, *args, **options):
        qs = Document.objects.all()

        if options["document_id"]:
            qs = qs.filter(pk=options["document_id"])
        elif options["case_id"]:
            qs = qs.filter(case_id=options["case_id"])

        if not options["force"]:
            qs = qs.exclude(extraction_status=Document.ExtractionStatus.COMPLETED)

        if options["limit"]:
            qs = qs[:options["limit"]]

        docs = list(qs)
        self.stdout.write(f"[process_documents] Found {len(docs)} document(s) to process.")

        if options["dry_run"]:
            for doc in docs:
                self.stdout.write(f"  [DRY RUN] Would process: Document #{doc.pk} — {doc.title}")
            return

        ok = 0
        fail = 0
        for doc in docs:
            self.stdout.write(f"  Processing Document #{doc.pk}: {doc.title}")
            success = process_document(doc)
            if success:
                n = chunk_document(doc)
                self.stdout.write(self.style.SUCCESS(f"    ✓ Extracted & chunked into {n} chunk(s)"))
                ok += 1
            else:
                self.stdout.write(self.style.ERROR(f"    ✗ Extraction failed (see logs)"))
                fail += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n[process_documents] Done: {ok} succeeded, {fail} failed."
        ))

