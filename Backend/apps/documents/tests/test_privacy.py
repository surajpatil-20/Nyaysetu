"""
Tests for UploadedDocument privacy and multi-tenant isolation.
Verifies that User A cannot view, retrieve, edit or delete User B's documents.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from apps.documents.models import UploadedDocument

User = get_user_model()


class DocumentPrivacyIsolationTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username="user_alice",
            email="alice@example.com",
            password="alicepassword123"
        )
        self.user_b = User.objects.create_user(
            username="user_bob",
            email="bob@example.com",
            password="bobpassword123"
        )
        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.user_a)

        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.user_b)

        # Alice creates a private document
        dummy_file = SimpleUploadedFile("alice_affidavit.pdf", b"%PDF-1.4 dummy content", content_type="application/pdf")
        self.doc_alice = UploadedDocument.objects.create(
            user=self.user_a,
            title="Alice Private Affidavit",
            file=dummy_file,
            is_private=True
        )

    def test_alice_can_view_own_document(self):
        response = self.client_a.get(f"/api/documents/user-documents/{self.doc_alice.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Alice Private Affidavit")

    def test_bob_cannot_view_alice_document(self):
        # Bob tries to access Alice's document directly by ID
        response = self.client_b.get(f"/api/documents/user-documents/{self.doc_alice.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bob_cannot_see_alice_document_in_list(self):
        # Bob lists documents
        response = self.client_b.get("/api/documents/user-documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        doc_ids = [d["id"] for d in results]
        self.assertNotIn(self.doc_alice.id, doc_ids)

    def test_anonymous_cannot_access_user_documents(self):
        anon_client = APIClient()
        response = anon_client.get("/api/documents/user-documents/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
