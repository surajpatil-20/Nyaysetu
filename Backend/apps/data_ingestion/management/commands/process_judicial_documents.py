"""
management command: process_judicial_documents

Processes judicial documents: text extraction, OCR fallback, paragraph chunking,
and dense 768-dim BGE embeddings.

Usage:
    python manage.py process_judicial_documents
    python manage.py process_judicial_documents --limit 10 --embed
"""
from django.core.management.base import BaseCommand
from apps.documents.models import Document
from apps.documents.services.chunking import chunk_document
from apps.documents.services.embeddings import generate_embeddings_for_document
from apps.documents.services.extraction import process_document


class Command(BaseCommand):
    help = "Run extraction, OCR fallback, chunking, and embeddings for judicial documents."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None, help="Max documents to process.")
        parser.add_argument("--embed", action="store_true", default=False, help="Generate embeddings after chunking.")
        parser.add_argument("--force", action="store_true", default=False, help="Force re-extraction of already completed docs.")

    def handle(self, *args, **options):
        qs = Document.objects.filter(source_name="Indian Supreme Court Judgments Open Dataset")
        if not options["force"]:
            qs = qs.exclude(extraction_status=Document.ExtractionStatus.COMPLETED)

        if options["limit"]:
            qs = qs[:options["limit"]]

        docs = list(qs)
        self.stdout.write(f"[process_judicial_documents] Found {len(docs)} document(s) to process.")

        success_count = 0
        fail_count = 0
        total_chunks = 0
        total_embeddings = 0

        for doc in docs:
            self.stdout.write(f"  Processing Doc #{doc.pk}: {doc.title[:80]}...")
            if process_document(doc):
                chunks = chunk_document(doc, force_rechunk=options["force"])
                total_chunks += chunks
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"    ✓ Extracted and chunked ({chunks} chunks)"))

                if options["embed"]:
                    emb = generate_embeddings_for_document(doc, force=options["force"])
                    total_embeddings += emb["processed"]
                    self.stdout.write(self.style.SUCCESS(f"    ✓ {emb['processed']} embeddings generated"))
            else:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"    ✗ Extraction failed for Doc #{doc.pk}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n[process_judicial_documents] Complete:\n"
            f"  Succeeded : {success_count}\n"
            f"  Failed    : {fail_count}\n"
            f"  Chunks    : {total_chunks}\n"
            f"  Embeddings: {total_embeddings}"
        ))

