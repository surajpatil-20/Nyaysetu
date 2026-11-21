"""
Unit and integration tests for NYAYASETU Assistant app.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.courts.models import Court
from apps.cases.models import Case
from apps.documents.models import Document, DocumentChunk
from apps.assistant.services import AssistantService
from apps.assistant.prompts import (
    DISCLAIMER_TEXT,
    INSUFFICIENT_EVIDENCE_MESSAGE,
    build_rag_prompt,
    build_evidence_context,
)
from apps.assistant.llm.mock import MockLLMProvider


def create_assistant_test_data():
    court, _ = Court.objects.get_or_create(
        court_name="Delhi High Court",
        defaults={"court_type": Court.CourtType.HIGH_COURT, "state": "Delhi"}
    )
    case, _ = Case.objects.get_or_create(
        case_number="W.P.(C) 1234/2023",
        defaults={
            "case_title": "Ramesh Kumar v. Union of India",
            "court": court,
            "status": Case.CaseStatus.DISPOSED,
            "case_type": "Writ Petition (Civil)",
        }
    )
    doc, _ = Document.objects.get_or_create(
        case=case,
        title="Final Judgment in W.P. 1234/2023",
        defaults={
            "document_type": Document.DocumentType.JUDGMENT,
            "extraction_status": Document.ExtractionStatus.COMPLETED,
            "extracted_text": (
                "The petitioner Ramesh Kumar challenged the arbitrary denial of promotion benefits. "
                "The court examined the scope of Article 14 of the Constitution guaranteeing equality before law. "
                "The respondents are directed to reconsider the petitioner's claim within 8 weeks."
            ),
            "page_count": 1,
            "source_name": "Delhi High Court Official Portal",
            "source_url": "https://delhihighcourt.nic.in/demo/1234",
        }
    )
    chunk, _ = DocumentChunk.objects.get_or_create(
        document=doc,
        chunk_index=0,
        defaults={
            "case": case,
            "content": (
                "The court examined the scope of Article 14 of the Constitution guaranteeing equality before law. "
                "The respondents are directed to reconsider the petitioner's claim within 8 weeks."
            ),
            "page_number": 1,
            "token_count": 28,
            "embedding": [0.05] * 768,
        }
    )
    return court, case, doc, chunk


class AssistantPromptAndContextTest(TestCase):
    def test_build_evidence_context_empty(self):
        ctx = build_evidence_context([])
        self.assertIn("No judicial evidence", ctx)

    def test_build_rag_prompt_contains_disclaimer_instructions(self):
        prompt = build_rag_prompt("What is Article 14?", [])
        self.assertIn("USER QUESTION: What is Article 14?", prompt)
        self.assertIn("RETRIEVED JUDICIAL EVIDENCE EXCERPTS:", prompt)


class MockLLMProviderTest(TestCase):
    def test_mock_returns_insufficient_when_no_evidence(self):
        provider = MockLLMProvider()
        out = provider.generate("system prompt", "USER QUESTION: foo\n\nNo judicial evidence excerpts available.")
        self.assertEqual(out, INSUFFICIENT_EVIDENCE_MESSAGE)

    def test_mock_returns_grounded_answer_with_evidence(self):
        provider = MockLLMProvider()
        sample_prompt = (
            "USER QUESTION: equality\n\n"
            "RETRIEVED JUDICIAL EVIDENCE EXCERPTS:\n"
            "--- [Evidence 1] ---\n"
            "Case: Ramesh Kumar v. UOI (W.P. 1234)\n"
            "Document: Judgment | Page 1 | Source: Portal\n"
            "Excerpt:\nArticle 14 guarantees equality before law.\n\n"
            "INSTRUCTIONS FOR YOUR RESPONSE:\n"
        )
        out = provider.generate("system", sample_prompt)
        self.assertIn("[Evidence 1]", out)
        self.assertIn("Article 14 guarantees equality", out)


class AssistantServiceTest(TestCase):
    def setUp(self):
        self.court, self.case, self.doc, self.chunk = create_assistant_test_data()

    def test_successful_grounded_answer(self):
        resp = AssistantService.answer_question(query="equality before law Article 14")
        self.assertTrue(resp["has_sufficient_evidence"])
        self.assertGreater(resp["evidence_count"], 0)
        self.assertIn("[Evidence 1]", resp["answer"])
        self.assertEqual(resp["disclaimer"], DISCLAIMER_TEXT)

        # Check source metadata
        first_source = resp["sources"][0]
        self.assertEqual(first_source["case_number"], "W.P.(C) 1234/2023")
        self.assertEqual(first_source["case_title"], "Ramesh Kumar v. Union of India")
        self.assertEqual(first_source["document_title"], "Final Judgment in W.P. 1234/2023")
        self.assertEqual(first_source["page_number"], 1)

    def test_insufficient_evidence_for_unrelated_query(self):
        resp = AssistantService.answer_question(query="unobtainium interplanetary spacecraft propulsion 987654")
        self.assertFalse(resp["has_sufficient_evidence"])
        self.assertEqual(resp["evidence_count"], 0)
        self.assertEqual(resp["sources"], [])
        self.assertEqual(resp["answer"], INSUFFICIENT_EVIDENCE_MESSAGE)
        self.assertEqual(resp["disclaimer"], DISCLAIMER_TEXT)

    def test_empty_query(self):
        resp = AssistantService.answer_question(query="")
        self.assertFalse(resp["has_sufficient_evidence"])


from apps.users.models import User


class AssistantAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.court, self.case, self.doc, self.chunk = create_assistant_test_data()
        self.user = User.objects.create_user(
            username="assistant_tester",
            email="assistant_test@example.com",
            password="StrongPassword123!",
            role="CITIZEN",
            is_active=True
        )

    def test_unauthenticated_post_returns_401(self):
        payload = {"query": "Article 14 equality", "top_k": 3}
        resp = self.client.post("/api/assistant/", payload, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_unauthenticated_get_returns_401(self):
        resp = self.client.get("/api/assistant/")
        self.assertEqual(resp.status_code, 401)

    def test_authenticated_get_assistant_guide(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/assistant/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("disclaimer", data)
        self.assertEqual(data["service"], "NYAYASETU AI Judicial Assistant")

    def test_authenticated_post_query_success(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "query": "Article 14 equality",
            "top_k": 3,
            "alpha": 0.5
        }
        resp = self.client.post("/api/assistant/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertIn("disclaimer", data)
        self.assertTrue(data["has_sufficient_evidence"])

    def test_authenticated_post_missing_query_returns_400(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/assistant/", {}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("query", resp.json())

    def test_case_identification_via_api(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "query": "Tell me about Ramesh Kumar v. Union of India",
            "top_k": 3,
        }
        resp = self.client.post("/api/assistant/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["identified_case"])
        self.assertEqual(data["identified_case"]["id"], self.case.id)
        self.assertFalse(data["needs_clarification"])

    def test_contextual_continuity_via_api(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "query": "what happened in this case?",
            "case_id": self.case.id,
            "top_k": 3,
        }
        resp = self.client.post("/api/assistant/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["identified_case"])
        self.assertEqual(data["identified_case"]["id"], self.case.id)


class CaseIdentificationUnitTest(TestCase):
    def setUp(self):
        self.court, self.case, self.doc, self.chunk = create_assistant_test_data()

    def test_identify_case_by_caption(self):
        resp = AssistantService.answer_question("Tell me about Ramesh Kumar v. Union of India")
        self.assertIsNotNone(resp.get("identified_case"))
        self.assertEqual(resp["identified_case"]["id"], self.case.id)
        self.assertFalse(resp["needs_clarification"])

    def test_contextual_questions_use_active_case(self):
        resp = AssistantService.answer_question("who were the judges in this case?", case_id=self.case.id)
        self.assertIsNotNone(resp.get("identified_case"))
        self.assertEqual(resp["identified_case"]["id"], self.case.id)

    def test_general_question_falls_back_to_general_rag(self):
        resp = AssistantService.answer_question("equality before law Article 14")
        self.assertIsNone(resp.get("identified_case"))
        self.assertFalse(resp["needs_clarification"])
        self.assertTrue(resp["has_sufficient_evidence"])


