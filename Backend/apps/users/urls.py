from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    ResendOTPView,
    CustomTokenObtainPairView,
    UserProfileView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='auth_verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='auth_resend_otp'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
]
