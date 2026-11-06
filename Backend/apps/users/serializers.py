from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from .models import User, EmailOTP
from .utils import print_otp_terminal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=False)
    confirmPassword = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'confirmPassword', 'role']
        extra_kwargs = {
            'role': {'default': User.Role.CITIZEN}
        }

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        confirm = attrs.get('password_confirm') or attrs.get('confirmPassword')
        if not confirm:
            raise serializers.ValidationError({"password_confirm": "Password confirmation is required."})

        if attrs['password'] != confirm:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        role = attrs.get('role', User.Role.CITIZEN)
        if role == User.Role.ADMIN or str(role).upper() == 'ADMIN':
            raise serializers.ValidationError({"role": "Registration as Administrator is not permitted."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        validated_data.pop('confirmPassword', None)
        role = validated_data.get('role', User.Role.CITIZEN)

        # Create user as inactive until OTP is successfully verified
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role,
            is_active=False
        )

        # Invalidate any lingering unverified OTPs for this email
        EmailOTP.objects.filter(email__iexact=user.email, is_verified=False).update(is_verified=True)

        # Generate a cryptographically secure 6-digit OTP
        otp_code = EmailOTP.generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=5)

        EmailOTP.objects.create(
            user=user,
            email=user.email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_verified=False
        )

        # Print OTP to terminal for development/testing
        print_otp_terminal(user.email, otp_code, expires_at)

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_otp(self, value):
        val = value.strip()
        if not val.isdigit() or len(val) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return val


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token Serializer that checks account activation status
    and ensures inactive/unverified users cannot authenticate.
    """
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()
        if user and not user.is_active:
            if user.check_password(password):
                raise exceptions.AuthenticationFailed(
                    "Account is not verified. Please verify your OTP before logging in."
                )

        return super().validate(attrs)
