import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        ADMIN = 'ADMIN', 'Administrator'

    email = models.EmailField(unique=True, verbose_name='Email Address')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN,
        help_text='Role in NYAYASETU platform'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class EmailOTP(models.Model):
    """
    Cryptographically secure 6-digit Email OTP for user registration & verification.
    Valid for 5 minutes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps',
        null=True,
        blank=True
    )
    email = models.EmailField(db_index=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'users_email_otp'
        ordering = ['-created_at']

    @classmethod
    def generate_otp_code(cls) -> str:
        """
        Generate a cryptographically secure 6-digit numeric OTP using secrets.
        """
        return f"{secrets.randbelow(900000) + 100000}"

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        status_str = "Verified" if self.is_verified else ("Expired" if self.is_expired() else "Pending")
        return f"OTP for {self.email} [{status_str}]"
