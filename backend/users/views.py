"""
File: backend/users/views.py
Purpose: User authentication and management views
Date Revised: 2025-07-15 00:00:00 UTC
Version: 3.0.1 - Critical Security Fixes Applied

FIXES APPLIED:
- V-302: Fixed password length validation inconsistency
- V-303: Added early return to prevent session invalidation on login failure
- V-304: Removed unused UserRateThrottle import
- V-305: Added stop_after_delay to prevent unbounded retry time
- V-306: Added FRONTEND_URL validation with urlparse
- V-307: Cleaned up unused imports
"""

import hashlib
import logging
import secrets
import time
import uuid
from datetime import timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlparse  # FIXED: V-306

import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from tenacity import stop_after_delay  # FIXED: V-305
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .models import EMAIL_VERIFICATION_HOURS, PASSWORD_RESET_HOURS
from .models import CustomUser as User
from .models import EmailVerification, PasswordReset, Profile, Subscription, UserSession
from .permissions import IsOwnerOrAdmin, IsUserOrAdmin
from .serializers import MIN_PASSWORD_LENGTH  # FIXED: V-302 - Import for consistency
from .serializers import RESERVED_USERNAMES  # Import centralized constant
from .serializers import (
    EmailVerificationSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    ResendVerificationSerializer,
    SubscriptionSerializer,
    UpdateProfileSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserSerializer,
    UserSessionSerializer,
)
from .services import EmailService, SecurityService, SessionService

logger = logging.getLogger(__name__)

# Constants
DEFAULT_SUBSCRIPTION_DAYS = 30
SUBSCRIPTION_PRICES = {
    "registered": 9.99,
    "premium": 19.99,
}

# Request timeout for external API calls
EXTERNAL_API_TIMEOUT = (3, 10)  # (connect_timeout, read_timeout)
MAX_EXTERNAL_API_RETRIES = 3
CONSTANT_TIME_DELAY = 0.25  # seconds for timing attack prevention

# Rate limiting constants
REGISTRATION_RATE_LIMIT = "10/h"
LOGIN_RATE_LIMIT = "20/h"
PASSWORD_RESET_RATE_LIMIT = "5/h"
EMAIL_VERIFY_RATE_LIMIT = "10/h"
API_KEY_HEADER = "X-API-Key"

# FIXED: V-306 - Allowed frontend URLs for SSRF protection
ALLOWED_FRONTEND_DOMAINS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    # Add your production domains here
]


# Custom exceptions
class ExternalAPIError(Exception):
    """Raised when external API calls fail"""

    pass


class SecurityError(Exception):
    """Raised for security-related issues"""

    pass


# Throttle classes
class LoginRateThrottle(AnonRateThrottle):
    scope = "login"
    rate = LOGIN_RATE_LIMIT


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = "password_reset"
    rate = PASSWORD_RESET_RATE_LIMIT


class EmailVerifyRateThrottle(AnonRateThrottle):
    scope = "email_verify"
    rate = EMAIL_VERIFY_RATE_LIMIT


def validate_frontend_url(url: str) -> bool:
    """FIXED: V-306 - Validate frontend URL to prevent SSRF."""
    try:
        parsed = urlparse(url)

        # Check if domain is in allowed list
        domain = parsed.hostname
        if domain not in ALLOWED_FRONTEND_DOMAINS:
            # Also check if it's a subdomain of allowed domains
            for allowed_domain in ALLOWED_FRONTEND_DOMAINS:
                if domain and domain.endswith(f".{allowed_domain}"):
                    return True
            return False

        # Only allow http/https schemes
        if parsed.scheme not in ["http", "https"]:
            return False

        return True
    except Exception:
        return False


@method_decorator(
    ratelimit(key="ip", rate=REGISTRATION_RATE_LIMIT, method="POST"), name="create"
)
class RegisterView(generics.CreateAPIView):
    """Register a new user with transaction safety and rate limiting."""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create user with atomic transaction and security measures."""
        # Validate request
        if not self._validate_registration_request(request):
            return Response(
                {"detail": "Invalid registration request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            SecurityService.log_failed_registration(request, serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()

            # Create email verification with secure token
            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=EMAIL_VERIFICATION_HOURS)
            verification = EmailVerification.objects.create(
                user=user, token=token, expires_at=expiry
            )

            # Create subscription
            Subscription.create_for_user(user)

            # Send verification email (non-blocking)
            try:
                EmailService.send_verification_email(user, verification.token)
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                # Continue registration even if email fails

            SecurityService.log_successful_registration(request, user)

            return Response(
                {
                    "detail": "User registered successfully. Please check your email to verify your account.",
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return Response(
                {"detail": "An error occurred during registration. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate_registration_request(self, request) -> bool:
        """FIXED: V-302 - Validate registration request with consistent password length."""
        # Check for required fields
        required_fields = ["email", "username", "password", "password_confirm"]
        for field in required_fields:
            if field not in request.data:
                return False

        # FIXED: V-302 - Use consistent password length check
        if len(request.data.get("password", "")) < MIN_PASSWORD_LENGTH:
            return False

        return True


@method_decorator(
    ratelimit(key="ip", rate=LOGIN_RATE_LIMIT, method="POST"), name="post"
)
class LoginView(views.APIView):
    """User login with enhanced security and session fixation prevention."""

    permission_classes = []
    throttle_classes = [LoginRateThrottle]
    serializer_class = LoginSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Handle user login with proper session management."""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            SecurityService.log_failed_login(request, serializer.errors)
            # Add constant time delay to prevent timing attacks
            time.sleep(CONSTANT_TIME_DELAY)

            # FIXED: V-303 - Early return to prevent session invalidation on login failure
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        remember_me = serializer.validated_data.get("remember_me", False)

        # FIXED: Invalidate old sessions BEFORE creating new one
        with transaction.atomic():
            # Invalidate existing sessions
            SessionService.invalidate_user_sessions(user, exclude_current=False)

            # Record successful login
            user.record_login_attempt(successful=True, request=request)

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # Create new session and tokens
            refresh = RefreshToken.for_user(user)
            if not remember_me:
                refresh.set_exp(lifetime=timedelta(hours=24))

            expires_at = timezone.now() + (
                timedelta(days=30) if remember_me else timedelta(hours=24)
            )

            # Create session with unique key
            session = SessionService.create_session(
                user=user,
                session_key=str(refresh.access_token["jti"]),
                request=request,
                expires_at=expires_at,
                login_method="credentials",
            )

        SecurityService.log_successful_login(request, user)

        # Get or create subscription
        try:
            subscription = user.subscription
        except Subscription.DoesNotExist:
            subscription = Subscription.create_for_user(user)

        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserDetailSerializer(user, context={"request": request}).data,
            "session_id": session.id,
        }

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    """User logout with comprehensive session cleanup."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle user logout with proper cleanup."""
        try:
            # Extract session key from JWT
            session_key = None
            if hasattr(request, "auth") and hasattr(request.auth, "payload"):
                session_key = request.auth.payload.get("jti")

            # Invalidate sessions
            if session_key:
                SessionService.invalidate_session_by_key(request.user, session_key)

            # Blacklist refresh token if provided
            refresh_token = request.data.get("refresh")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    logger.warning(f"Error blacklisting token: {str(e)}")

            SecurityService.log_successful_logout(request)

            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserView(generics.RetrieveUpdateAPIView):
    """View and update authenticated user's information."""

    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """Optimized queryset with related data."""
        return User.objects.select_related("profile", "subscription").prefetch_related(
            "sessions", "email_verifications"
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """View and update user profile with optimization."""

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrAdmin]

    def get_object(self):
        # Use select_related for optimization
        return get_object_or_404(
            Profile.objects.select_related("user"), user=self.request.user
        )

    def update(self, request, *args, **kwargs):
        """Update profile with logging."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        SecurityService.log_profile_update(request)

        # Invalidate profile cache
        cache.delete(f"profile:{request.user.id}")

        return Response(serializer.data)


class UpdateProfileView(generics.GenericAPIView):
    """Comprehensive profile update with validation."""

    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Update both user and profile data atomically."""
        serializer = self.get_serializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        SecurityService.log_comprehensive_profile_update(request)

        # Invalidate caches
        cache.delete(f"user:{request.user.id}")
        cache.delete(f"profile:{request.user.id}")

        return Response(
            UserDetailSerializer(request.user, context={"request": request}).data
        )


class PasswordChangeView(generics.GenericAPIView):
    """Change password with enhanced security."""

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Change password and invalidate other sessions."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Get current session key
        current_session_key = None
        if hasattr(request, "auth") and hasattr(request.auth, "payload"):
            current_session_key = request.auth.payload.get("jti")

        # Invalidate other sessions but keep current one
        SessionService.invalidate_user_sessions(
            request.user, exclude_session_key=current_session_key
        )

        # Clear permission cache
        from .permissions import clear_permission_cache

        clear_permission_cache(request.user.id)

        SecurityService.log_password_change(request)

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )


@method_decorator(
    ratelimit(key="ip", rate=PASSWORD_RESET_RATE_LIMIT, method="POST"), name="post"
)
class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset with timing attack prevention."""

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request, *args, **kwargs):
        """Send password reset email with constant time."""
        start_time = time.time()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Always perform the same operations regardless of user existence
        email_hash = hashlib.sha256(email.encode()).hexdigest()

        try:
            user = User.objects.get(email=email)
            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=PASSWORD_RESET_HOURS)

            PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=expiry,
                ip_address=SecurityService.get_client_ip(request),
            )

            EmailService.send_password_reset_email(user, token)
            SecurityService.log_password_reset_request(request, user, success=True)

        except User.DoesNotExist:
            # Perform dummy operations to maintain constant time
            _ = uuid.uuid4()
            _ = timezone.now() + timedelta(hours=PASSWORD_RESET_HOURS)
            SecurityService.log_password_reset_request(request, None, success=False)

        # Ensure constant response time
        elapsed = time.time() - start_time
        if elapsed < CONSTANT_TIME_DELAY:
            time.sleep(CONSTANT_TIME_DELAY - elapsed)

        # Always return same message for security
        return Response(
            {
                "detail": "If an account exists with this email, a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset with enhanced validation."""

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Reset password using valid token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            password = serializer.validated_data["password"]
            reset = serializer.context.get("reset")

            if not reset:
                return Response(
                    {"detail": "Invalid reset token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = reset.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset.use_token()

            # Invalidate all sessions for security
            SessionService.invalidate_user_sessions(user)

            # Clear caches
            from .permissions import clear_permission_cache

            clear_permission_cache(user.id)
            cache.delete(f"user:{user.id}")

            SecurityService.log_password_reset_completion(request, user)

            return Response(
                {
                    "detail": "Password has been reset successfully. You can now log in with your new password."
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {"detail": "Password reset failed."}, status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(
    ratelimit(key="ip", rate=EMAIL_VERIFY_RATE_LIMIT, method="POST"), name="post"
)
class EmailVerificationView(generics.GenericAPIView):
    """Verify email address with rate limiting."""

    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Verify email with token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = serializer.validated_data["token"]
            verification = get_object_or_404(EmailVerification, token=token)

            if not verification.is_valid():
                return Response(
                    {
                        "detail": "This verification link has expired or already been used."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if verification.use_token():
                # Clear cache
                cache.delete(f"user:{verification.user.id}")

                SecurityService.log_email_verification(
                    request, verification.user, success=True
                )
                return Response(
                    {"detail": "Email verified successfully. You can now log in."},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"detail": "Email verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response(
                {"detail": "Email verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(
    ratelimit(key="ip", rate=EMAIL_VERIFY_RATE_LIMIT, method="POST"), name="post"
)
class ResendVerificationView(generics.GenericAPIView):
    """Resend email verification with rate limiting."""

    serializer_class = ResendVerificationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]

    def post(self, request, *args, **kwargs):
        """Resend verification email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = get_object_or_404(User, email=email)

            if user.is_email_verified:
                return Response(
                    {"detail": "Email address is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Invalidate old verification tokens
            EmailVerification.objects.filter(user=user, is_used=False).update(
                is_used=True
            )

            # Create new token
            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=EMAIL_VERIFICATION_HOURS)

            EmailVerification.objects.create(user=user, token=token, expires_at=expiry)

            EmailService.send_verification_email(user, token)
            SecurityService.log_verification_resend(request, user)

            return Response(
                {"detail": "Verification email has been sent."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            return Response(
                {"detail": "Failed to resend verification email."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserSessionViewSet(viewsets.ModelViewSet):
    """Manage user sessions with security controls."""

    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Get active sessions for current user."""
        return UserSession.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("user")

    def destroy(self, request, *args, **kwargs):
        """Invalidate session securely."""
        instance = self.get_object()

        # Verify ownership
        if instance.user != request.user and not request.user.is_admin:
            return Response(
                {"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        instance.invalidate()

        SecurityService.log_session_invalidation(request, instance)
        return Response(
            {"detail": "Session invalidated successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def invalidate_all(self, request):
        """Invalidate all sessions except current."""
        current_session_key = None
        if hasattr(request, "auth") and hasattr(request.auth, "payload"):
            current_session_key = request.auth.payload.get("jti")

        count = SessionService.invalidate_user_sessions(
            request.user, exclude_session_key=current_session_key
        )

        return Response(
            {"detail": f"Invalidated {count} sessions."}, status=status.HTTP_200_OK
        )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage user subscriptions with validation."""

    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related(
            "user"
        )

    def get_object(self):
        try:
            return Subscription.objects.get(user=self.request.user)
        except Subscription.DoesNotExist:
            return Subscription.create_for_user(self.request.user)

    @action(detail=False, methods=["get"])
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def current(self, request):
        """Get current subscription."""
        subscription = self.get_object()
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def upgrade(self, request):
        """Upgrade subscription with validation."""
        subscription = self.get_object()
        tier = request.data.get("tier")

        if tier not in ["registered", "premium"]:
            return Response(
                {
                    "detail": "Invalid subscription tier. Choose from: registered, premium"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate upgrade path
        if subscription.tier == "premium" and tier != "premium":
            return Response(
                {"detail": "Cannot downgrade through upgrade endpoint"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.tier = tier
        subscription.status = "active"
        subscription.end_date = timezone.now() + timedelta(
            days=DEFAULT_SUBSCRIPTION_DAYS
        )
        subscription.last_payment_date = timezone.now()
        subscription.is_auto_renew = request.data.get("auto_renew", True)
        subscription.payment_method = request.data.get("payment_method", "demo")
        subscription.amount_paid = SUBSCRIPTION_PRICES.get(tier, 0)
        subscription.save()

        # Clear cache
        cache.delete(f"subscription:{request.user.id}")

        SecurityService.log_subscription_upgrade(request, subscription)
        return Response(self.get_serializer(subscription).data)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def cancel(self, request):
        """Cancel subscription safely."""
        subscription = self.get_object()

        if subscription.tier == "guest":
            return Response(
                {"detail": "Cannot cancel a guest tier subscription"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.cancel_subscription()

        # Clear cache
        cache.delete(f"subscription:{request.user.id}")

        SecurityService.log_subscription_cancellation(request, subscription)
        return Response(self.get_serializer(subscription).data)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def downgrade(self, request):
        """Downgrade subscription with validation."""
        subscription = self.get_object()

        if subscription.tier == "guest":
            return Response(
                {"detail": "Already on guest tier"}, status=status.HTTP_400_BAD_REQUEST
            )

        if subscription.tier == "premium":
            new_tier = request.data.get("tier", "registered")
            if new_tier not in ["registered", "guest"]:
                return Response(
                    {
                        "detail": "Invalid downgrade tier. Choose from: registered, guest"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription.tier = new_tier
        else:
            subscription.tier = "guest"
            subscription.end_date = None

        subscription.save()

        # Clear cache
        cache.delete(f"subscription:{request.user.id}")

        SecurityService.log_subscription_downgrade(request, subscription)
        return Response(self.get_serializer(subscription).data)


class SocialAuthGoogleView(views.APIView):
    """Initiate Google OAuth flow with security controls."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Generate secure Google OAuth URL."""
        required_settings = [
            "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
            "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
            "FRONTEND_URL",
        ]

        # Validate configuration
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                logger.error(f"Missing required setting: {setting}")
                return Response(
                    {"detail": "OAuth configuration error. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # FIXED: V-306 - Validate FRONTEND_URL to prevent SSRF
        if not validate_frontend_url(settings.FRONTEND_URL):
            logger.error(f"Invalid FRONTEND_URL configured: {settings.FRONTEND_URL}")
            return Response(
                {"detail": "OAuth configuration error. Please contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        cache.set(f"oauth_state:{state}", True, timeout=600)  # 10 minutes

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/google/callback"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=email%20profile"
            f"&access_type=offline"
            f"&prompt=consent"
            f"&state={state}"
        )

        # Add PKCE if provided
        code_challenge = request.GET.get("code_challenge")
        if code_challenge and self._validate_pkce_challenge(code_challenge):
            auth_url += f"&code_challenge={code_challenge}&code_challenge_method=S256"

        SecurityService.log_oauth_initiation(request, "google")
        return Response({"authorizationUrl": auth_url, "state": state})

    def _validate_pkce_challenge(self, challenge: str) -> bool:
        """Validate PKCE code challenge format."""
        # Base64url encoded string of 43-128 characters
        return bool(
            challenge
            and 43 <= len(challenge) <= 128
            and all(
                c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
                for c in challenge
            )
        )


class SocialAuthGithubView(views.APIView):
    """Initiate GitHub OAuth flow with security controls."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Generate secure GitHub OAuth URL."""
        required_settings = [
            "SOCIAL_AUTH_GITHUB_KEY",
            "SOCIAL_AUTH_GITHUB_SECRET",
            "FRONTEND_URL",
        ]

        # Validate configuration
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                logger.error(f"Missing required setting: {setting}")
                return Response(
                    {"detail": "OAuth configuration error. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # FIXED: V-306 - Validate FRONTEND_URL to prevent SSRF
        if not validate_frontend_url(settings.FRONTEND_URL):
            logger.error(f"Invalid FRONTEND_URL configured: {settings.FRONTEND_URL}")
            return Response(
                {"detail": "OAuth configuration error. Please contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        cache.set(f"oauth_state:{state}", True, timeout=600)  # 10 minutes

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/github/callback"
        auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.SOCIAL_AUTH_GITHUB_KEY}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=user:email"
            f"&state={state}"
        )

        SecurityService.log_oauth_initiation(request, "github")
        return Response({"authorizationUrl": auth_url, "state": state})


class SocialAuthCompleteView(views.APIView):
    """Complete OAuth flow with enhanced security."""

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        """Complete social authentication securely."""
        try:
            code = request.data.get("code")
            provider = request.data.get("provider")
            state = request.data.get("state")
            code_verifier = request.data.get("code_verifier")

            # Validate inputs
            if not code or provider not in ["google", "github"]:
                return Response(
                    {"detail": "Valid code and provider are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate state parameter
            if state and not cache.get(f"oauth_state:{state}"):
                return Response(
                    {"detail": "Invalid or expired state parameter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete state from cache after validation
            if state:
                cache.delete(f"oauth_state:{state}")

            # Exchange code for user info with retry logic
            if provider == "google":
                user_info = self._exchange_google_code(code, code_verifier)
            else:  # github
                user_info = self._exchange_github_code(code, code_verifier)

            # Validate email
            email = user_info.get("email")
            if not email or not self._validate_email(email):
                return Response(
                    {"detail": f"Could not get valid email from {provider}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Find or create user
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                # Create new user for social auth
                user_data = {
                    "email": email,
                    "username": self._generate_unique_username(email),
                    "first_name": user_info.get(
                        "given_name" if provider == "google" else "first_name", ""
                    )[:30],
                    "last_name": user_info.get(
                        "family_name" if provider == "google" else "last_name", ""
                    )[:30],
                    "is_active": True,
                    "is_email_verified": True,
                    "role": "student",
                }

                user = User.objects.create_user(**user_data)
                Profile.objects.get_or_create(user=user)
                Subscription.create_for_user(user)
                created = True

            # Invalidate old sessions before creating new one
            SessionService.invalidate_user_sessions(user, exclude_current=False)

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # Create session and tokens
            refresh = RefreshToken.for_user(user)
            expires_at = timezone.now() + timedelta(days=14)

            session = SessionService.create_session(
                user=user,
                session_key=str(refresh.access_token["jti"]),
                request=request,
                expires_at=expires_at,
                login_method=f"social_{provider}",
            )

            SecurityService.log_social_auth_success(request, user, provider)

            data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserDetailSerializer(user, context={"request": request}).data,
                "created": created,
            }

            return Response(data, status=status.HTTP_200_OK)

        except ExternalAPIError as e:
            SecurityService.log_social_auth_error(request, str(e))
            return Response(
                {"detail": "Failed to communicate with authentication provider."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            SecurityService.log_social_auth_error(request, str(e))
            return Response(
                {"detail": f"Authentication failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @retry(
        stop=stop_after_attempt(MAX_EXTERNAL_API_RETRIES)
        | stop_after_delay(30),  # FIXED: V-305 - Added bounded total runtime
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def _exchange_google_code(
        self, code: str, code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange Google authorization code with retry logic."""
        token_url = "https://oauth2.googleapis.com/token"

        # FIXED: V-306 - Validate redirect_uri
        if not validate_frontend_url(settings.FRONTEND_URL):
            raise ExternalAPIError("Invalid frontend URL configuration")

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/google/callback"

        token_payload = {
            "code": code,
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        if code_verifier:
            token_payload["code_verifier"] = code_verifier

        try:
            token_response = requests.post(
                token_url, data=token_payload, timeout=EXTERNAL_API_TIMEOUT
            )
            token_response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Google token exchange failed: {str(e)}")
            raise ExternalAPIError("Failed to exchange Google code")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise ExternalAPIError("No access token received from Google")

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            userinfo_response = requests.get(
                userinfo_url, headers=headers, timeout=EXTERNAL_API_TIMEOUT
            )
            userinfo_response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Google userinfo request failed: {str(e)}")
            raise ExternalAPIError("Failed to get Google user info")

        return userinfo_response.json()

    @retry(
        stop=stop_after_attempt(MAX_EXTERNAL_API_RETRIES)
        | stop_after_delay(30),  # FIXED: V-305 - Added bounded total runtime
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def _exchange_github_code(
        self, code: str, code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange GitHub authorization code with retry logic."""
        token_url = "https://github.com/login/oauth/access_token"

        # FIXED: V-306 - Validate redirect_uri
        if not validate_frontend_url(settings.FRONTEND_URL):
            raise ExternalAPIError("Invalid frontend URL configuration")

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/github/callback"

        token_payload = {
            "code": code,
            "client_id": settings.SOCIAL_AUTH_GITHUB_KEY,
            "client_secret": settings.SOCIAL_AUTH_GITHUB_SECRET,
            "redirect_uri": redirect_uri,
        }

        headers = {"Accept": "application/json"}

        try:
            token_response = requests.post(
                token_url,
                data=token_payload,
                headers=headers,
                timeout=EXTERNAL_API_TIMEOUT,
            )
            token_response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"GitHub token exchange failed: {str(e)}")
            raise ExternalAPIError("Failed to exchange GitHub code")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            error = token_data.get("error_description", "Unknown error")
            raise ExternalAPIError(f"GitHub OAuth error: {error}")

        # Get user info
        api_headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            user_response = requests.get(
                "https://api.github.com/user",
                headers=api_headers,
                timeout=EXTERNAL_API_TIMEOUT,
            )
            user_response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"GitHub user request failed: {str(e)}")
            raise ExternalAPIError("Failed to get GitHub user info")

        user_data = user_response.json()

        # Get primary email if not in profile
        email = user_data.get("email")
        if not email:
            try:
                emails_response = requests.get(
                    "https://api.github.com/user/emails",
                    headers=api_headers,
                    timeout=EXTERNAL_API_TIMEOUT,
                )
                emails_response.raise_for_status()

                emails = emails_response.json()
                primary_email = next(
                    (e for e in emails if e.get("primary") and e.get("verified")), None
                )
                if primary_email:
                    email = primary_email.get("email")
            except requests.RequestException:
                pass

        if not email:
            raise ExternalAPIError("Could not retrieve verified email from GitHub")

        # Parse name safely
        full_name = user_data.get("name", "")
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]

        return {
            "email": email,
            "first_name": name_parts[0][:30],
            "last_name": (name_parts[1] if len(name_parts) > 1 else "")[:30],
            "avatar_url": user_data.get("avatar_url", ""),
            "id": user_data.get("id"),
        }

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _generate_unique_username(self, email: str) -> str:
        """Generate unique username from email."""
        base = email.split("@")[0]
        # Remove special characters
        base = "".join(c for c in base if c.isalnum() or c in "_-")[:20]

        # Ensure uniqueness
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        return username


class SocialAuthErrorView(views.APIView):
    """Handle social auth errors gracefully."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Handle OAuth errors."""
        error = request.GET.get("error", "Unknown error")
        error_description = request.GET.get("error_description", "")
        state = request.GET.get("state", "")

        SecurityService.log_social_auth_error(request, f"{error}: {error_description}")

        # Validate state if provided
        if state:
            cache.delete(f"oauth_state:{state}")

        if not hasattr(settings, "FRONTEND_URL"):
            return Response(
                {"detail": "Frontend URL is not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # FIXED: V-306 - Validate frontend URL before redirect
        if not validate_frontend_url(settings.FRONTEND_URL):
            logger.error(
                f"Invalid FRONTEND_URL for error redirect: {settings.FRONTEND_URL}"
            )
            return Response(
                {"detail": "OAuth configuration error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        error_message = f"{error}: {error_description}" if error_description else error
        redirect_url = f"{settings.FRONTEND_URL}/login?error={error_message}"

        if state:
            redirect_url += f"&state={state}"

        return redirect(redirect_url)
