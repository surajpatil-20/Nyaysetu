"""
management command: generate_embeddings

Generates 768-dim sentence embeddings for all un-embedded DocumentChunks.

Usage:
    python manage.py generate_embeddings
    python manage.py generate_embeddings --document-id 5
    python manage.py generate_embeddings --limit 100
    python manage.py generate_embeddings --force
"""
from django.core.management.base import BaseCommand
from apps.documents.models import Document, DocumentChunk
from apps.documents.services.embeddings import generate_embeddings_for_document


class Command(BaseCommand):
    help = "Generate sentence embeddings for DocumentChunks."

    def add_arguments(self, parser):
        parser.add_argument("--document-id", type=int, default=None, help="Generate for a specific document.")
        parser.add_argument("--limit", type=int, default=None, help="Max number of documents to process.")
        parser.add_argument("--force", action="store_true", default=False, help="Re-embed already-embedded chunks.")

    def handle(self, *args, **options):
        qs = Document.objects.filter(extraction_status="COMPLETED")

        if options["document_id"]:
            qs = qs.filter(pk=options["document_id"])

        if options["limit"]:
            qs = qs[:options["limit"]]

        docs = list(qs)
        self.stdout.write(f"[generate_embeddings] Processing {len(docs)} document(s).")

        total = {"processed": 0, "skipped": 0, "errors": 0}
        for doc in docs:
            self.stdout.write(f"  Document #{doc.pk}: {doc.title}")
            summary = generate_embeddings_for_document(doc, force=options["force"])
            total["processed"] += summary["processed"]
            total["errors"] += summary["errors"]
            self.stdout.write(f"    → {summary['processed']} embedded, {summary['errors']} errors")

        self.stdout.write(self.style.SUCCESS(
            f"\n[generate_embeddings] Done: {total['processed']} chunks embedded, {total['errors']} errors."
        ))



