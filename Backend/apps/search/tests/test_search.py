"""
Tests for Hybrid Search.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from apps.courts.models import Court
from apps.cases.models import Case
from apps.documents.models import Document, DocumentChunk
from apps.search.services import _semantic_vector_search, hybrid_search


def setup_search_data():
    court, _ = Court.objects.get_or_create(
        court_name="Search Test Court",
        defaults={"court_type": Court.CourtType.HIGH_COURT}
    )
    case, _ = Case.objects.get_or_create(
        case_number="SRCH/001/2024",
        defaults={
            "case_title": "Article 14 Equality Test Case",
            "court": court,
            "status": Case.CaseStatus.DISPOSED,
            "case_type": "Writ Petition",
        }
    )
    doc, _ = Document.objects.get_or_create(
        case=case,
        title="Test Judgment",
        defaults={
            "document_type": Document.DocumentType.JUDGMENT,
            "extraction_status": Document.ExtractionStatus.COMPLETED,
            "extracted_text": "Article 14 guarantees equality before law to all citizens.",
        }
    )
    chunk, _ = DocumentChunk.objects.get_or_create(
        document=doc,
        chunk_index=0,
        defaults={
            "case": case,
            "content": "Article 14 guarantees equality before law to all citizens of India.",
            "page_number": 1,
            "token_count": 13,
            "embedding": [0.1] * 768,
        }
    )
    return court, case, doc, chunk


class HybridSearchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.court, self.case, self.doc, self.chunk = setup_search_data()

    def test_search_returns_results(self):
        resp = self.client.get("/api/search/", {"q": "equality"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertGreater(data["count"], 0)

    def test_search_missing_query_returns_400(self):
        resp = self.client.get("/api/search/")
        self.assertEqual(resp.status_code, 400)

    def test_search_empty_returns_empty(self):
        resp = self.client.get("/api/search/", {"q": "xyzzy_nonexistent_term_12345"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 0)

    def test_search_result_has_required_fields(self):
        resp = self.client.get("/api/search/", {"q": "Article 14"})
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["results"]
        if results:
            first = results[0]
            for field in ["chunk_id", "case_id", "case_title", "document_id", "snippet", "hybrid_score"]:
                self.assertIn(field, first, msg=f"Missing field: {field}")

    def test_search_with_court_filter(self):
        resp = self.client.get("/api/search/", {"q": "equality", "court_id": self.court.pk})
        self.assertEqual(resp.status_code, 200)

    def test_timeline_returns_events(self):
        resp = self.client.get(f"/api/search/cases/{self.case.pk}/timeline/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["case_id"], self.case.pk)
        self.assertIn("timeline", data)

    def test_timeline_case_not_found(self):
        resp = self.client.get("/api/search/cases/999999/timeline/")
        self.assertEqual(resp.status_code, 404)

    def test_pgvector_database_cosine_distance_search(self):
        query_vec = [0.1] * 768
        hits = _semantic_vector_search(query_vec, filters={}, top_k=5)
        self.assertGreater(len(hits), 0)
        chunk, score = hits[0]
        self.assertEqual(chunk.pk, self.chunk.pk)
        # Cosine distance to identical vector [0.1]*768 is ~0, so score is ~1.0
        self.assertAlmostEqual(score, 1.0, places=2)

    def test_pure_semantic_hybrid_search(self):
        from unittest.mock import patch
        with patch("apps.documents.services.embeddings.embed_single", return_value=[0.1] * 768):
            results = hybrid_search("equality", top_k=5, alpha=0.0)
            self.assertGreater(len(results), 0)
            self.assertGreater(results[0].semantic_score, 0.0)

