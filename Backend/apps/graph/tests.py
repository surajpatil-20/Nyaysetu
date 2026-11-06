"""
Tests for Judicial Knowledge Graph (apps.graph).
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.courts.models import Court, Judge
from apps.cases.models import Case, Party, CaseParty, CaseJudge, CaseCitation
from apps.documents.models import Document
from apps.graph.services import get_case_graph
from apps.graph.sync import sync_knowledge_graph

User = get_user_model()


class KnowledgeGraphTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.court = Court.objects.create(
            court_name="Supreme Court of India",
            court_type="SUPREME_COURT"
        )
        self.case = Case.objects.create(
            case_number="2023 INSC 599",
            case_title="Pradeep v. State of Haryana",
            court=self.court,
            status="DISPOSED"
        )
        self.judge = Judge.objects.create(
            name="Hon'ble Justice Test",
            current_court=self.court,
            designation="Judge"
        )
        self.case_judge = CaseJudge.objects.create(
            case=self.case,
            judge=self.judge,
            role="PRESIDING",
            bench_order=1
        )
        self.party = Party.objects.create(
            name="State of Haryana",
            party_type="STATE"
        )
        self.case_party = CaseParty.objects.create(
            case=self.case,
            party=self.party,
            role="RESPONDENT"
        )
        self.document = Document.objects.create(
            case=self.case,
            title="Judgment in Pradeep v State of Haryana",
            document_type="JUDGMENT",
            page_count=15
        )

    def test_get_case_graph_structure(self):
        graph = get_case_graph(self.case.id)
        self.assertIsNotNone(graph)
        self.assertEqual(graph["case_id"], self.case.id)
        self.assertEqual(graph["case_number"], "2023 INSC 599")
        self.assertIn("nodes", graph)
        self.assertIn("links", graph)
        self.assertIn("textual_relationships", graph)

        # Check nodes
        node_types = {n["type"] for n in graph["nodes"]}
        self.assertIn("Case", node_types)
        self.assertIn("Court", node_types)
        self.assertIn("Judge", node_types)
        self.assertIn("Party", node_types)
        self.assertIn("Document", node_types)

        # Check links
        link_types = {l["type"] for l in graph["links"]}
        self.assertIn("FILED_IN", link_types)
        self.assertIn("HEARD_BY", link_types)
        self.assertIn("HAS_PARTY", link_types)
        self.assertIn("HAS_DOCUMENT", link_types)

        # Check textual descriptions
        self.assertTrue(len(graph["textual_relationships"]) > 0)

    def test_case_graph_api_endpoint(self):
        response = self.client.get(f"/api/graph/cases/{self.case.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["case_id"], self.case.id)
        self.assertGreaterEqual(len(response.data["nodes"]), 5)

    def test_case_graph_api_not_found(self):
        response = self.client.get("/api/graph/cases/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_graph_status_endpoint(self):
        response = self.client.get("/api/graph/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("neo4j_connected", response.data)
        self.assertIn("architecture", response.data)

    def test_sync_knowledge_graph_dry_run(self):
        stats = sync_knowledge_graph(dry_run=True, case_id=self.case.id)
        self.assertEqual(stats["cases_synced"], 1)
        self.assertEqual(stats["courts_synced"], 1)
        self.assertEqual(stats["judges_synced"], 1)
        self.assertEqual(stats["parties_synced"], 1)
        self.assertEqual(stats["documents_synced"], 1)
        self.assertTrue(stats["dry_run"])

