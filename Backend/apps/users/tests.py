from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User, EmailOTP


class UserAuthenticationAndOTPTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reg_data = {
            "username": "citizen_test",
            "email": "citizen@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "role": "CITIZEN"
        }

    def test_registration_success_generates_otp(self):
        resp = self.client.post("/api/auth/register/", self.reg_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()

        # OTP must NOT be exposed in the API response
        self.assertNotIn("otp", data)
        self.assertNotIn("otp_code", data)
        self.assertIn("message", data)
        self.assertEqual(data["email"], "citizen@example.com")

        # Account must be created as inactive pending OTP verification
        user = User.objects.get(email="citizen@example.com")
        self.assertFalse(user.is_active)
        self.assertEqual(user.role, User.Role.CITIZEN)

        # OTP must exist in database
        otp_record = EmailOTP.objects.filter(email="citizen@example.com").first()
        self.assertIsNotNone(otp_record)
        self.assertEqual(len(otp_record.otp_code), 6)
        self.assertTrue(otp_record.otp_code.isdigit())
        self.assertFalse(otp_record.is_verified)
        self.assertFalse(otp_record.is_expired())

    def test_registration_duplicate_email(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        # Attempt second registration with duplicate email
        duplicate_data = {
            "username": "another_user",
            "email": "citizen@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }
        resp = self.client.post("/api/auth/register/", duplicate_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", resp.json())

    def test_registration_duplicate_username(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        # Attempt second registration with duplicate username
        duplicate_data = {
            "username": "citizen_test",
            "email": "different@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }
        resp = self.client.post("/api/auth/register/", duplicate_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", resp.json())

    def test_registration_cannot_register_as_admin(self):
        admin_reg = dict(self.reg_data)
        admin_reg["role"] = "ADMIN"
        admin_reg["username"] = "wannabe_admin"
        admin_reg["email"] = "admin_attempt@example.com"
        resp = self.client.post("/api/auth/register/", admin_reg, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", resp.json())

    def test_registration_password_mismatch(self):
        bad_data = dict(self.reg_data)
        bad_data["password_confirm"] = "DifferentPassword999!"
        resp = self.client.post("/api/auth/register/", bad_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.json())

    def test_otp_generation_format_and_expiry(self):
        code = EmailOTP.generate_otp_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
        self.assertGreaterEqual(int(code), 100000)
        self.assertLessEqual(int(code), 999999)

    def test_correct_otp_verification(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        otp_record = EmailOTP.objects.filter(email="citizen@example.com").first()

        verify_payload = {
            "email": "citizen@example.com",
            "otp": otp_record.otp_code
        }
        resp = self.client.post("/api/auth/verify-otp/", verify_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("Account verified successfully", resp.json()["message"])

        # User must now be active
        user = User.objects.get(email="citizen@example.com")
        self.assertTrue(user.is_active)

        # OTP record must now be marked verified
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_verified)

    def test_incorrect_otp_verification(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        verify_payload = {
            "email": "citizen@example.com",
            "otp": "000000"  # incorrect
        }
        resp = self.client.post("/api/auth/verify-otp/", verify_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.json())

        # User must remain inactive
        user = User.objects.get(email="citizen@example.com")
        self.assertFalse(user.is_active)

    def test_expired_otp_verification(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        otp_record = EmailOTP.objects.filter(email="citizen@example.com").first()
        # Fast-forward OTP expiry to the past
        otp_record.expires_at = timezone.now() - timedelta(minutes=1)
        otp_record.save()

        verify_payload = {
            "email": "citizen@example.com",
            "otp": otp_record.otp_code
        }
        resp = self.client.post("/api/auth/verify-otp/", verify_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", resp.json()["error"].lower())

        # User must remain inactive
        user = User.objects.get(email="citizen@example.com")
        self.assertFalse(user.is_active)

    def test_reused_otp_verification(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        otp_record = EmailOTP.objects.filter(email="citizen@example.com").first()

        verify_payload = {
            "email": "citizen@example.com",
            "otp": otp_record.otp_code
        }
        # First verification succeeds
        resp1 = self.client.post("/api/auth/verify-otp/", verify_payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)

        # Second verification with same OTP must fail
        resp2 = self.client.post("/api/auth/verify-otp/", verify_payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been used", resp2.json().get("error", ""))

    def test_resend_otp_success(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        first_otp = EmailOTP.objects.filter(email="citizen@example.com").first()

        # Age the first OTP by 35 seconds to bypass the 30-second cooldown
        first_otp.created_at = timezone.now() - timedelta(seconds=35)
        first_otp.save()

        resp = self.client.post("/api/auth/resend-otp/", {"email": "citizen@example.com"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("message", resp.json())
        self.assertNotIn("otp", resp.json())

        # Previous OTP must be marked verified/invalidated
        first_otp.refresh_from_db()
        self.assertTrue(first_otp.is_verified)

        # A new valid unverified OTP must be created
        new_otp = EmailOTP.objects.filter(email="citizen@example.com", is_verified=False).first()
        self.assertIsNotNone(new_otp)
        self.assertNotEqual(new_otp.id, first_otp.id)
        self.assertEqual(len(new_otp.otp_code), 6)

    def test_resend_otp_cooldown_abuse_prevention(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        # Immediately requesting resend should hit the 30s cooldown
        resp = self.client.post("/api/auth/resend-otp/", {"email": "citizen@example.com"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("wait", resp.json()["error"].lower())

    def test_login_before_verification_fails(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")

        login_payload = {
            "username": "citizen_test",
            "password": "StrongPassword123!"
        }
        resp = self.client.post("/api/auth/login/", login_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", resp.json())

    def test_login_after_verification_succeeds(self):
        self.client.post("/api/auth/register/", self.reg_data, format="json")
        otp_record = EmailOTP.objects.filter(email="citizen@example.com").first()

        # Verify OTP
        self.client.post("/api/auth/verify-otp/", {
            "email": "citizen@example.com",
            "otp": otp_record.otp_code
        }, format="json")

        # Now login must succeed and return JWT tokens
        login_payload = {
            "username": "citizen_test",
            "password": "StrongPassword123!"
        }
        resp = self.client.post("/api/auth/login/", login_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

