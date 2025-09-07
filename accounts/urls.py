# airbnb-clone-project/accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import (
    PasswordTokenCheckAPI,
    RequestPasswordResetEmail,
    SetNewPasswordAPIView,
    UserRegistrationView,
    VerifyEmailView,
)

app_name = "accounts"

urlpatterns = [
    # User registration
    path("register/", UserRegistrationView.as_view(), name="register"),
    # Email verification
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    # Password reset
    path(
        "password-reset-email/",
        RequestPasswordResetEmail.as_view(),
        name="password-reset-email",
    ),
    # Password reset token check
    path(
        "password-reset/<str:uidb64>/<str:token>/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    # Set new password
    path(
        "password-reset-complete/",
        SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    # JWT Token endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
