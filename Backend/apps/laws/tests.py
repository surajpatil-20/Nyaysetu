from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.courts.models import Court
from apps.cases.models import Case
from .models import LawCategory, LawAct, LawSection, LegalScenario


class LawsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category = LawCategory.objects.create(
            name="Consumer Protection & E-commerce",
            slug="consumer-protection",
            description="Rights against defective products, unfair trade practices, and refund refusals",
            icon="ShoppingBag",
            display_order=1
        )

        self.act = LawAct.objects.create(
            act_name="Consumer Protection Act, 2019",
            short_code="CPA 2019",
            act_year=2019,
            official_url="https://www.indiacode.nic.in/handle/123456789/15256"
        )

        self.section = LawSection.objects.create(
            act=self.act,
            section_number="Section 2(7)",
            title="Definition of Consumer",
            legal_text="A consumer is any person who buys any goods or hires or avails of any service...",
            simple_explanation="Covers buyers who purchase goods or services offline or online for personal use.",
            punishment_or_remedy="Right to file a statutory complaint before District Consumer Disputes Redressal Commission.",
            official_url="https://www.indiacode.nic.in/handle/123456789/15256"
        )

        self.court = Court.objects.create(
            court_name="Supreme Court of India",
            court_type=Court.CourtType.SUPREME_COURT,
        )
        self.test_case = Case.objects.create(
            case_number="2010 INSC 582",
            case_title="M/S. KRANTI ASSOCIATES PVT. LTD. & ANR. versus SH. MASOOD AHMED KHAN",
            court=self.court,
            status=Case.CaseStatus.DISPOSED,
            description="Consumer Protection Act and District Forum compensation principles."
        )

        self.scenario = LegalScenario.objects.create(
            category=self.category,
            title="E-commerce Seller Refuses Return or Refund for Defective Item",
            slug="defective-product-refund-refusal",
            situation_summary="You ordered an electronic item online which arrived defective, and the seller refused return.",
            what_to_do="1. Preserve invoice and unboxing photos.\n2. Raise dispute with seller.\n3. Call National Consumer Helpline at 1915 or lodge complaint on e-Jagriti.",
            official_portal_url="https://e-jagriti.gov.in/",
            helpline_number="1915",
            is_featured=True,
            display_order=1
        )
        self.scenario.sections.add(self.section)
        self.scenario.related_cases.add(self.test_case)

    def test_list_categories(self):
        response = self.client.get("/api/laws/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Consumer Protection & E-commerce")
        self.assertEqual(response.data[0]["scenario_count"], 1)

    def test_list_scenarios(self):
        response = self.client.get("/api/laws/scenarios/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "E-commerce Seller Refuses Return or Refund for Defective Item")
        self.assertEqual(results[0]["category_name"], "Consumer Protection & E-commerce")
        self.assertEqual(results[0]["sections_count"], 1)

    def test_filter_scenarios_by_category(self):
        response = self.client.get(f"/api/laws/scenarios/?category__slug={self.category.slug}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertEqual(len(results), 1)

    def test_get_scenario_detail(self):
        response = self.client.get(f"/api/laws/scenarios/{self.scenario.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.scenario.id)
        self.assertEqual(response.data["category"]["name"], "Consumer Protection & E-commerce")
        self.assertEqual(len(response.data["sections"]), 1)
        self.assertEqual(response.data["sections"][0]["section_number"], "Section 2(7)")
        self.assertEqual(response.data["sections"][0]["act"]["short_code"], "CPA 2019")
        self.assertEqual(response.data["helpline_number"], "1915")
        self.assertEqual(response.data["official_portal_url"], "https://e-jagriti.gov.in/")
        self.assertIn("related_cases", response.data)
        self.assertGreaterEqual(len(response.data["related_cases"]), 1)
        self.assertEqual(response.data["related_cases"][0]["case_number"], "2010 INSC 582")

    def test_get_scenario_related_cases_endpoint(self):
        response = self.client.get(f"/api/laws/scenarios/{self.scenario.id}/related-cases/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["scenario_id"], self.scenario.id)
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertEqual(response.data["related_cases"][0]["case_number"], "2010 INSC 582")

    def test_search_scenarios(self):
        response = self.client.get("/api/laws/scenarios/?search=defective")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertEqual(len(results), 1)
