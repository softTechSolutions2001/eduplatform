"""
File: backend/users/urls.py
Path: backend/users/urls.py
Date Created: 2025-06-20
Date Revised: 2025-06-20 14:45:02 UTC
Revised By: sujibeautysalon
Author: AI Assistant for sujibeautysalon
Purpose: Enhanced URL configuration for user management and authentication in EduPlatform
Environment: Production
Version: 2.1.0 - Complete Field/Method/Property Continuity

Changes in this version:
- Added missing UpdateProfileView mapping at 'profile/comprehensive/'
- Achieved 100% view-to-URL mapping coverage (17/17 views)
- Maintained complete backward compatibility with existing URLs
- Enhanced URL naming conventions for enterprise standards
- Complete field/method/property continuity tracking implemented

Previous Version: 2.0.0 (Initial production version)

This file maps URLs to view functions for the following operations:
- User registration and account creation
- User authentication (login and logout)
- Password management (change, reset)
- Email verification
- User profile management (basic and comprehensive)
- User session management
- Subscription management with tiered access
- Social authentication (Google, GitHub) with dual implementation

Field/Method/Property Continuity Tracking:
✅ RegisterView.create() → register/
✅ LoginView.post() → login/
✅ LogoutView.post() → logout/
✅ UserView.get()/put()/patch() → me/
✅ ProfileView.get()/put()/patch() → profile/
✅ UpdateProfileView.put() → profile/comprehensive/ [NEWLY ADDED]
✅ PasswordChangeView.post() → password/change/
✅ PasswordResetRequestView.post() → password/reset/
✅ PasswordResetConfirmView.post() → password/reset/confirm/
✅ EmailVerificationView.post() → email/verify/
✅ ResendVerificationView.post() → email/verify/resend/
✅ UserSessionViewSet (all CRUD) → sessions/ [Router-managed]
✅ SubscriptionViewSet (all CRUD + custom actions) → subscription/ [Router-managed]
✅ SocialAuthGoogleView.get() → social/google/
✅ SocialAuthGithubView.get() → social/github/
✅ SocialAuthCompleteView.post() → social/complete/
✅ SocialAuthErrorView.get() → social/error/

Custom ViewSet Actions Auto-Routed:
✅ SubscriptionViewSet.current() → subscription/current/
✅ SubscriptionViewSet.upgrade() → subscription/upgrade/
✅ SubscriptionViewSet.cancel() → subscription/cancel/
✅ SubscriptionViewSet.downgrade() → subscription/downgrade/

Connected files:
1. backend/users/views.py - All 17 view classes and methods
2. backend/users/serializers.py - API serializers for user data
3. backend/users/models.py - User models and profile management
4. backend/users/permissions.py - Custom permission classes
5. backend/educore/urls.py - Main project URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import (
    RegisterView, LoginView, LogoutView, UserView,
    ProfileView, UpdateProfileView, PasswordChangeView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerificationView, ResendVerificationView,
    UserSessionViewSet, SubscriptionViewSet,
    SocialAuthGoogleView, SocialAuthGithubView,
    SocialAuthCompleteView, SocialAuthErrorView
)

# Router for viewsets with complete method coverage
router = DefaultRouter()
router.register(r'sessions', UserSessionViewSet, basename='user-sessions')
router.register(r'subscription', SubscriptionViewSet, basename='user-subscription')

# URL patterns with complete field/method/property continuity
urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User management endpoints
    path('me/', UserView.as_view(), name='user-detail'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('profile/comprehensive/', UpdateProfileView.as_view(), name='profile-comprehensive'),


    # Password management endpoints
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Email verification endpoints
    path('email/verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('email/verify/resend/', ResendVerificationView.as_view(), name='email-verify-resend'),

    # Social authentication endpoints (custom implementation)
    path('social/google/', SocialAuthGoogleView.as_view(), name='social-google'),
    path('social/github/', SocialAuthGithubView.as_view(), name='social-github'),
    path('social/complete/', SocialAuthCompleteView.as_view(), name='social-complete'),
    path('social/error/', SocialAuthErrorView.as_view(), name='social-error'),

    # Include router URLs for ViewSets (sessions, subscription management)
    path('', include(router.urls)),
]

# Social authentication framework integration (dual implementation)
urlpatterns += [
    path('social-auth/', include('social_django.urls', namespace='social')),
]
