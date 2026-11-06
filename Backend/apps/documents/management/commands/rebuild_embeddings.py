"""
management command: rebuild_embeddings

Regenerates 768-dim BAAI/bge-base-en-v1.5 embeddings for all DocumentChunks using batching.

Usage:
    python manage.py rebuild_embeddings
    python manage.py rebuild_embeddings --document-id 5
    python manage.py rebuild_embeddings --batch-size 64
"""
from django.core.management.base import BaseCommand
from apps.documents.models import Document, DocumentChunk
from apps.documents.services.embeddings import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    generate_embeddings_for_document,
    regenerate_all_embeddings,
)


class Command(BaseCommand):
    help = "Rebuild all DocumentChunk embeddings using BAAI/bge-base-en-v1.5."

    def add_arguments(self, parser):
        parser.add_argument("--document-id", type=int, default=None, help="Rebuild for a specific document only.")
        parser.add_argument("--batch-size", type=int, default=64, help="Batch size for embedding generation (default: 64).")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        doc_id = options["document_id"]

        self.stdout.write(self.style.WARNING(
            f"[rebuild_embeddings] Model: {EMBEDDING_MODEL_NAME} | Dimensions: {EMBEDDING_DIMENSION} | Batch size: {batch_size}"
        ))

        if doc_id:
            try:
                doc = Document.objects.get(pk=doc_id)
            except Document.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Document #{doc_id} not found."))
                return

            self.stdout.write(f"[rebuild_embeddings] Rebuilding for Document #{doc.pk}: {doc.title}...")
            summary = generate_embeddings_for_document(doc, force=True, batch_size=batch_size)
            self.stdout.write(self.style.SUCCESS(
                f"[rebuild_embeddings] Done: {summary['processed']} chunks embedded, {summary['errors']} errors."
            ))
            return

        def on_progress(done, total):
            pct = (done / total) * 100 if total else 0
            self.stdout.write(f"  → Embedded {done}/{total} chunks ({pct:.1f}%)...")

        summary = regenerate_all_embeddings(batch_size=batch_size, progress_callback=on_progress)
        self.stdout.write(self.style.SUCCESS(
            f"\n[rebuild_embeddings] Finished! Total: {summary['total']} | Processed: {summary['processed']} | Errors: {summary['errors']}"
        ))


