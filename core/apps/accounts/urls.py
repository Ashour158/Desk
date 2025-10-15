"""
Authentication URLs for helpdesk platform.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

urlpatterns = [
    # JWT Authentication
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    # User registration and management
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    # Password reset
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Two-factor authentication
    path("2fa/setup/", views.TwoFactorSetupView.as_view(), name="2fa_setup"),
    path("2fa/verify/", views.TwoFactorVerifyView.as_view(), name="2fa_verify"),
    path("2fa/disable/", views.TwoFactorDisableView.as_view(), name="2fa_disable"),
]
