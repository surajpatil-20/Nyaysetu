"""
Tests for documents: extraction, chunking, embeddings.
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.documents.services.extraction import _clean_text, extract_text_from_file
from apps.documents.services.chunking import _split_into_paragraphs, _build_chunks, chunk_document
from apps.documents.services.embeddings import embed_texts, generate_embeddings_for_document
from apps.courts.models import Court
from apps.cases.models import Case
from apps.documents.models import Document, DocumentChunk
from pgvector.django import VectorField


def make_test_case():
    court, _ = Court.objects.get_or_create(
        court_name="Test Court",
        defaults={"court_type": Court.CourtType.OTHER}
    )
    case, _ = Case.objects.get_or_create(
        case_number="TEST/001/2024",
        defaults={
            "case_title": "Test v. Test",
            "court": court,
            "status": Case.CaseStatus.PENDING,
        }
    )
    return case


def make_test_document(case, text="[Page 1]\nThis is the first paragraph of a legal document.\n\nThis is the second paragraph discussing the matter further.\n\nThird paragraph with additional details about the proceedings.\n"):
    doc = Document.objects.create(
        case=case,
        title="Test Judgment",
        document_type=Document.DocumentType.JUDGMENT,
        extracted_text=text,
        extraction_status=Document.ExtractionStatus.COMPLETED,
        page_count=1,
    )
    return doc


class TextCleaningTest(TestCase):
    def test_clean_text_removes_extra_whitespace(self):
        raw = "Hello   world\n\n\n\nSecond line"
        cleaned = _clean_text(raw)
        self.assertNotIn("   ", cleaned)
        self.assertNotIn("\n\n\n\n", cleaned)

    def test_clean_text_preserves_content(self):
        raw = "Article 14 guarantees equality before law."
        cleaned = _clean_text(raw)
        self.assertIn("Article 14", cleaned)


class ChunkingTest(TestCase):
    def setUp(self):
        self.case = make_test_case()

    def test_paragraphs_extracted(self):
        text = "[Page 1]\nFirst paragraph.\n\n[Page 2]\nSecond paragraph."
        paras = _split_into_paragraphs(text)
        self.assertGreater(len(paras), 0)

    def test_chunks_created(self):
        case = self.case
        doc = make_test_document(case)
        n = chunk_document(doc)
        self.assertGreater(n, 0)
        self.assertEqual(DocumentChunk.objects.filter(document=doc).count(), n)

    def test_chunks_ordered(self):
        case = self.case
        doc = make_test_document(case)
        chunk_document(doc)
        indices = list(DocumentChunk.objects.filter(document=doc).values_list("chunk_index", flat=True))
        self.assertEqual(indices, sorted(indices))

    def test_rechunk_idempotent(self):
        case = self.case
        doc = make_test_document(case)
        n1 = chunk_document(doc)
        n2 = chunk_document(doc, force_rechunk=True)
        self.assertEqual(n1, n2)
        self.assertEqual(DocumentChunk.objects.filter(document=doc).count(), n2)

    def test_no_text_returns_zero(self):
        case = self.case
        doc = Document.objects.create(
            case=case,
            title="Empty Doc",
            document_type=Document.DocumentType.OTHER,
            extracted_text=None,
            extraction_status=Document.ExtractionStatus.PENDING,
        )
        n = chunk_document(doc)
        self.assertEqual(n, 0)


class EmbeddingTest(TestCase):
    def test_embed_texts_returns_correct_dimension(self):
        texts = ["The court held that the petitioner is entitled to relief."]
        vectors = embed_texts(texts)
        self.assertEqual(len(vectors), 1)
        self.assertEqual(len(vectors[0]), 768)

    def test_embed_empty_list(self):
        result = embed_texts([])
        self.assertEqual(result, [])

    def test_generate_embeddings_for_document(self):
        case = make_test_case()
        doc = make_test_document(case)
        chunk_document(doc)
        summary = generate_embeddings_for_document(doc)
        self.assertGreater(summary["processed"], 0)
        self.assertEqual(summary["errors"], 0)
        # All chunks should now have embeddings
        for chunk in DocumentChunk.objects.filter(document=doc):
            self.assertIsNotNone(chunk.embedding)
            self.assertEqual(len(chunk.embedding), 768)

    def test_embedding_is_vector_field(self):
        field = DocumentChunk._meta.get_field("embedding")
        self.assertIsInstance(field, VectorField)
        self.assertEqual(field.dimensions, 768)

    def test_vector_field_direct_assignment(self):
        case = make_test_case()
        doc = make_test_document(case)
        chunk = DocumentChunk.objects.create(
            document=doc,
            case=case,
            chunk_index=99,
            content="Direct vector assignment test",
            embedding=[0.01] * 768
        )
        saved = DocumentChunk.objects.get(pk=chunk.pk)
        self.assertEqual(len(saved.embedding), 768)
