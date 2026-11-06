from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, EmailOTP
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    CustomTokenObtainPairSerializer,
)
from .utils import print_otp_terminal


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Registration initiated. A 6-digit OTP has been generated for email verification.",
            "email": user.email,
            "username": user.username,
        }, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    """
    Verify the 6-digit OTP sent to the user's email.
    Upon verification, activates the user account.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].strip().lower()
        otp = serializer.validated_data['otp']

        # Find the latest unverified OTP for this email
        otp_record = EmailOTP.objects.filter(
            email__iexact=email,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            # Check if this OTP was already verified / used
            if EmailOTP.objects.filter(email__iexact=email, otp_code=otp, is_verified=True).exists():
                return Response(
                    {"error": "This OTP has already been used. Please request a new OTP."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": "Invalid OTP or no pending registration found for this email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry (5 minutes)
        if otp_record.is_expired():
            return Response(
                {"error": "OTP has expired. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check OTP match
        if otp_record.otp_code != otp:
            return Response(
                {"error": "Invalid OTP code. Please check and try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as verified/used
        otp_record.is_verified = True
        otp_record.save()

        # Invalidate any other pending OTPs for this email
        EmailOTP.objects.filter(email__iexact=email, is_verified=False).update(is_verified=True)

        # Activate the registered user account
        user = User.objects.filter(email__iexact=email).first()
        if user:
            user.is_active = True
            user.save()

        return Response({
            "message": "Account verified successfully. Please log in.",
            "email": email
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    Generate and display a new 6-digit OTP with a fresh 5-minute expiry.
    Includes a 30-second rate-limiting cooldown.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].strip().lower()

        # Find user
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                {"error": "No registration record found for this email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"error": "This account is already verified and active. Please log in directly."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cooldown check: 30 seconds
        recent_otp = EmailOTP.objects.filter(email__iexact=email).order_by('-created_at').first()
        if recent_otp:
            elapsed = (timezone.now() - recent_otp.created_at).total_seconds()
            if elapsed < 30:
                remaining = int(30 - elapsed)
                return Response(
                    {"error": f"Please wait {remaining} seconds before requesting a new OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Invalidate previous unverified OTPs
        EmailOTP.objects.filter(email__iexact=email, is_verified=False).update(is_verified=True)

        # Generate new 6-digit OTP
        new_otp_code = EmailOTP.generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=5)

        EmailOTP.objects.create(
            user=user,
            email=user.email,
            otp_code=new_otp_code,
            expires_at=expires_at,
            is_verified=False
        )

        # Print new OTP in terminal
        print_otp_terminal(user.email, new_otp_code, expires_at)

        return Response({
            "message": "A new verification OTP has been generated.",
            "email": user.email
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT token acquisition view that enforces verified account check.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
