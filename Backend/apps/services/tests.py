"""
Tests for Services app (apps.services).
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.services.models import Service


class ServicesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.s1 = Service.objects.create(
            service_name="NALSA Free Legal Aid",
            category="LEGAL_AID",
            description="Free legal aid for eligible citizens",
            official_url="https://nalsa.gov.in/"
        )
        self.s2 = Service.objects.create(
            service_name="eCourts Portal",
            category="CASE_STATUS",
            description="Check case status across courts",
            official_url="https://ecourts.gov.in/"
        )

    def test_list_services(self):
        response = self.client.get("/api/services/services/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results is paginated or list
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)

    def test_filter_services_by_category(self):
        response = self.client.get("/api/services/services/?category=LEGAL_AID")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["service_name"], "NALSA Free Legal Aid")

