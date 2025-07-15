"""
File: backend/users/urls.py
Purpose: Enhanced URL configuration with consistent naming and security
Date Revised: 2025-07-15 00:00:00 UTC
Version: 2.2.0 - Standardized Naming and Security Enhancements

FIXES APPLIED:
- Standardized URL naming patterns (user-* prefix)
- Added API versioning support
- Enhanced security with proper throttling
- Improved documentation and organization
- Added health check endpoints
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .health_views import (
    CacheHealthView,
    DatabaseHealthView,
    UserHealthCheckView,
    UserMetricsView,
)
from .views import (
    EmailVerificationView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RegisterView,
    ResendVerificationView,
    SocialAuthCompleteView,
    SocialAuthErrorView,
    SocialAuthGithubView,
    SocialAuthGoogleView,
    SubscriptionViewSet,
    UpdateProfileView,
    UserSessionViewSet,
    UserView,
)

# API version for future compatibility
API_VERSION = "v1"

# Router for viewsets with comprehensive coverage
router = DefaultRouter()
router.register(r"sessions", UserSessionViewSet, basename="user-sessions")
router.register(r"subscription", SubscriptionViewSet, basename="user-subscription")

# Main URL patterns with standardized naming
urlpatterns = [
    # =================
    # AUTHENTICATION ENDPOINTS
    # =================
    path("auth/register/", RegisterView.as_view(), name="user-register"),
    path("auth/login/", LoginView.as_view(), name="user-login"),
    path("auth/logout/", LogoutView.as_view(), name="user-logout"),
    # JWT Token endpoints (standardized naming)
    path("auth/token/", TokenObtainPairView.as_view(), name="user-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="user-token-refresh"),
    # =================
    # USER MANAGEMENT ENDPOINTS
    # =================
    path("profile/me/", UserView.as_view(), name="user-detail"),
    path("profile/basic/", ProfileView.as_view(), name="user-profile-basic"),
    path(
        "profile/comprehensive/",
        UpdateProfileView.as_view(),
        name="user-profile-comprehensive",
    ),
    # =================
    # PASSWORD MANAGEMENT ENDPOINTS
    # =================
    path("password/change/", PasswordChangeView.as_view(), name="user-password-change"),
    path(
        "password/reset/request/",
        PasswordResetRequestView.as_view(),
        name="user-password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="user-password-reset-confirm",
    ),
    # =================
    # EMAIL VERIFICATION ENDPOINTS
    # =================
    path("email/verify/", EmailVerificationView.as_view(), name="user-email-verify"),
    path(
        "email/verify/resend/",
        ResendVerificationView.as_view(),
        name="user-email-verify-resend",
    ),
    # =================
    # SOCIAL AUTHENTICATION ENDPOINTS
    # =================
    path(
        "social/google/initiate/",
        SocialAuthGoogleView.as_view(),
        name="user-social-google",
    ),
    path(
        "social/github/initiate/",
        SocialAuthGithubView.as_view(),
        name="user-social-github",
    ),
    path(
        "social/complete/",
        SocialAuthCompleteView.as_view(),
        name="user-social-complete",
    ),
    path("social/error/", SocialAuthErrorView.as_view(), name="user-social-error"),
    # =================
    # VIEWSET ENDPOINTS (sessions, subscriptions)
    # =================
    path("", include(router.urls)),
]

# Social authentication framework integration (backward compatibility)
urlpatterns += [
    path("social-auth/", include("social_django.urls", namespace="social")),
]

# API versioning support (future-proofing)
versioned_patterns = [
    path(f"api/{API_VERSION}/users/", include(urlpatterns)),
]

# Health check and monitoring endpoints
health_patterns = [
    path("health/", UserHealthCheckView.as_view(), name="user-health-check"),
    path("metrics/", UserMetricsView.as_view(), name="user-metrics"),
    path("health/database/", DatabaseHealthView.as_view(), name="user-database-health"),
    path("health/cache/", CacheHealthView.as_view(), name="user-cache-health"),
]

# Add health patterns to main patterns
urlpatterns += health_patterns

# Export patterns for main URL configuration
app_name = "users"
