"""
Tests for Cases app (apps.cases) including Related Cases, Case Detail, and Admin Stats.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.courts.models import Court, Judge
from apps.cases.models import Case, Party, CaseParty, CaseJudge, CaseCitation

User = get_user_model()


class CaseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@nyaysetu.gov.in",
            password="adminpassword123",
            role="ADMIN"
        )
        self.citizen_user = User.objects.create_user(
            username="citizen1",
            email="citizen1@example.com",
            password="citizenpassword123",
            role="CITIZEN"
        )
        self.court = Court.objects.create(
            court_name="Supreme Court of India",
            court_type="SUPREME_COURT"
        )
        self.case1 = Case.objects.create(
            case_number="2023 INSC 599",
            case_title="Pradeep v. State of Haryana",
            court=self.court,
            status="DISPOSED"
        )
        self.case2 = Case.objects.create(
            case_number="AIR 1973 SC 225",
            case_title="Kesavananda Bharati v. State of Kerala",
            court=self.court,
            status="DISPOSED"
        )
        self.citation = CaseCitation.objects.create(
            source_case=self.case1,
            cited_case=self.case2,
            citation_text="(1973) 4 SCC 225"
        )
        self.judge = Judge.objects.create(
            name="Hon'ble Justice Chandrachud",
            current_court=self.court
        )
        CaseJudge.objects.create(
            case=self.case1,
            judge=self.judge,
            role="PRESIDING"
        )
        CaseJudge.objects.create(
            case=self.case2,
            judge=self.judge,
            role="MEMBER"
        )

    def test_case_detail_api(self):
        response = self.client.get(f"/api/cases/cases/{self.case1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["case_number"], "2023 INSC 599")
        self.assertIn("court", response.data)
        self.assertIn("case_judges", response.data)
        self.assertIn("citations_made", response.data)

    def test_related_cases_api(self):
        response = self.client.get(f"/api/cases/cases/{self.case1.id}/related/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["case_id"], self.case1.id)
        related = response.data["related_cases"]
        self.assertTrue(len(related) > 0)
        # Should contain case2 via CITES relation
        cited_relations = [r for r in related if r["id"] == self.case2.id]
        self.assertTrue(len(cited_relations) > 0)

    def test_admin_stats_unauthorized_for_anonymous(self):
        response = self.client.get("/api/cases/admin/stats/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_admin_stats_forbidden_for_citizen(self):
        self.client.force_authenticate(user=self.citizen_user)
        response = self.client.get("/api/cases/admin/stats/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_stats_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/cases/admin/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cases", response.data)
        self.assertIn("courts", response.data)
        self.assertIn("judges", response.data)
        self.assertIn("users", response.data)
