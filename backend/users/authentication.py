"""
File: backend/users/authentication.py
Purpose: JWT authentication with session tracking and security enhancements
Date Revised: 2025-07-15 00:00:00 UTC
Version: 3.0.1 - Critical Security Fixes Applied

FIXES APPLIED:
- A-202: Added HSTS header, removed deprecated X-XSS-Protection
- A-203: Added cache.delete_pattern guard for compatibility
- A-204: Store ISO strings instead of datetime objects in cache
- A-205: Made ip_address and user_agent mandatory parameters
"""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken

from .models import UserSession

logger = logging.getLogger(__name__)

# Constants
SESSION_ACTIVITY_UPDATE_INTERVAL = 300  # 5 minutes
MAX_CONCURRENT_SESSIONS = 10
TOKEN_CLEANUP_BATCH_SIZE = 100


class SecurityError(Exception):
    """Raised for security-related authentication issues"""

    pass


class SessionValidationError(Exception):
    """Raised when session validation fails"""

    pass


class CustomJWTAuthentication(JWTAuthentication):
    """
    Enhanced JWT authentication with session tracking and security validation.
    FIXED: Session validation happens before user authentication.
    """

    def authenticate(self, request):
        """
        Authenticate request with proper session validation order.
        FIXED: Validate session BEFORE authenticating user.
        """
        # Get raw token first
        raw_token = self.get_raw_token(self.get_header(request))
        if raw_token is None:
            return None

        # Validate token and get payload
        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError:
            return None

        # Extract session key from token BEFORE getting user
        session_key = validated_token.payload.get("jti")
        if not session_key:
            logger.warning("JWT token missing session key (jti)")
            raise AuthenticationFailed("Invalid token format")

        # FIXED: Validate session BEFORE getting user
        try:
            session = self._validate_session(session_key)
        except SessionValidationError as e:
            raise AuthenticationFailed(str(e))

        # Now get the user from the validated token
        user = self.get_user(validated_token)
        if user is None:
            raise AuthenticationFailed("User not found")

        # Verify session belongs to this user
        if session.user_id != user.id:
            logger.warning(
                f"Session user mismatch: session user {session.user_id} != token user {user.id}"
            )
            raise AuthenticationFailed("Session authentication failed")

        # Check for account lockout
        if hasattr(user, "is_account_locked") and user.is_account_locked():
            session.invalidate()
            logger.warning(f"Locked account attempted access: user {user.id}")
            raise AuthenticationFailed("Account is temporarily locked")

        # Unlock account if ban period expired
        if hasattr(user, "unlock_account"):
            user.unlock_account()

        # Update session activity (throttled)
        self._update_session_activity(session)

        # Attach session to request for later use
        request.session_obj = session

        return (user, validated_token)

    def _validate_session(self, session_key: str) -> UserSession:
        """
        Validate session with proper locking.
        FIXED: Separated from main authenticate method for clarity.
        """
        with transaction.atomic():
            try:
                session = UserSession.objects.select_for_update().get(
                    session_key=session_key, is_active=True
                )
            except UserSession.DoesNotExist:
                logger.warning(f"Session not found: {session_key[:8]}...")
                raise SessionValidationError("Session not found or inactive")

            # Validate session expiry
            if not session.is_valid():
                session.invalidate()
                logger.info(f"Expired session invalidated: {session_key[:8]}...")
                raise SessionValidationError("Session has expired")

            return session

    def _update_session_activity(self, session: UserSession) -> None:
        """FIXED: A-204 - Update session activity with ISO string storage."""
        now = timezone.now()

        # Check if we need to update (throttled)
        cache_key = f"session_activity:{session.session_key}"
        last_update_str = cache.get(cache_key)

        if last_update_str:
            # Parse ISO string back to datetime for comparison
            try:
                from datetime import datetime

                last_update = datetime.fromisoformat(
                    last_update_str.replace("Z", "+00:00")
                )
                if (now - last_update).seconds <= SESSION_ACTIVITY_UPDATE_INTERVAL:
                    return
            except (ValueError, AttributeError):
                # If parsing fails, proceed with update
                pass

        session.last_activity = now
        session.save(update_fields=["last_activity"])
        # FIXED: A-204 - Store ISO string instead of datetime object
        cache.set(cache_key, now.isoformat(), timeout=SESSION_ACTIVITY_UPDATE_INTERVAL)


class SessionTokenAuthentication(BaseAuthentication):
    """
    Alternative authentication using session tokens for specific endpoints.
    Useful for long-lived connections or specific API operations.
    """

    def authenticate(self, request):
        """Authenticate using session token from header."""
        session_token = request.META.get("HTTP_X_SESSION_TOKEN")

        if not session_token:
            return None

        # Validate session token format
        if not self._validate_token_format(session_token):
            logger.warning("Invalid session token format")
            return None

        try:
            with transaction.atomic():
                session = UserSession.objects.select_for_update().get(
                    session_key=session_token, is_active=True
                )

                if not session.is_valid():
                    session.invalidate()
                    return None

                # Update activity
                self._update_session_activity(session)

                # Attach session to request
                request.session_obj = session

                return (session.user, session)

        except UserSession.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Session token authentication error: {str(e)}")
            return None

    def _validate_token_format(self, token: str) -> bool:
        """Validate session token format."""
        # Basic validation - adjust based on your token format
        return bool(token and len(token) >= 32 and token.replace("-", "").isalnum())

    def _update_session_activity(self, session: UserSession) -> None:
        """Update session activity with throttling."""
        now = timezone.now()
        if (
            not session.last_activity
            or (now - session.last_activity).seconds > SESSION_ACTIVITY_UPDATE_INTERVAL
        ):
            session.last_activity = now
            session.save(update_fields=["last_activity"])


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Custom response payload handler for JWT authentication.
    ENHANCED: Added security context and better error handling.
    """
    if not user:
        raise ValueError("User is required for JWT payload")

    payload = {
        "access": str(token),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_email_verified": user.is_email_verified,
            "is_active": user.is_active,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        },
        "issued_at": timezone.now().isoformat(),
    }

    # Add subscription info if available
    try:
        subscription = user.subscription
        payload["user"]["subscription"] = {
            "tier": subscription.tier,
            "status": subscription.status,
            "is_active": subscription.is_active,
            "days_remaining": subscription.days_remaining,
        }
    except Exception as e:
        logger.debug(f"Could not add subscription info: {str(e)}")
        payload["user"]["subscription"] = None

    # Add session info if available
    if hasattr(request, "session_obj") and request.session_obj:
        payload["session"] = {
            "id": request.session_obj.id,
            "device_type": request.session_obj.device_type,
            "created_at": request.session_obj.created_at.isoformat(),
        }

    return payload


class TokenRevocationService:
    """
    Service for handling token revocation and blacklisting.
    ENHANCED: Better error handling and batch operations.
    """

    @staticmethod
    @transaction.atomic
    def revoke_user_tokens(user, exclude_jti: Optional[str] = None) -> int:
        """
        Revoke all tokens for a user by invalidating sessions.
        Returns count of revoked tokens.
        """
        try:
            queryset = UserSession.objects.filter(user=user, is_active=True)

            if exclude_jti:
                queryset = queryset.exclude(session_key=exclude_jti)

            # Get count before update for accurate reporting
            count = queryset.count()

            # Check for max sessions limit
            if count > MAX_CONCURRENT_SESSIONS:
                logger.warning(
                    f"User {user.id} has {count} active sessions (limit: {MAX_CONCURRENT_SESSIONS})"
                )

            # Batch update for performance
            queryset.update(is_active=False)

            # FIXED: A-203 - Clear related caches with compatibility check
            if hasattr(cache, "delete_pattern"):
                cache_pattern = f"session_activity:{user.id}:*"
                cache.delete_pattern(cache_pattern)

            logger.info(f"Revoked {count} tokens for user {user.id}")
            return count

        except Exception as e:
            logger.error(f"Error revoking tokens for user {user.id}: {str(e)}")
            raise SecurityError(f"Failed to revoke tokens: {str(e)}")

    @staticmethod
    @transaction.atomic
    def revoke_token_by_jti(jti: str) -> bool:
        """Revoke specific token by JTI."""
        if not jti:
            raise ValueError("JTI is required")

        try:
            session = UserSession.objects.select_for_update().get(
                session_key=jti, is_active=True
            )
            session.invalidate()

            # Clear cache
            cache.delete(f"session_activity:{jti}")

            logger.info(f"Revoked token: {jti[:8]}...")
            return True

        except UserSession.DoesNotExist:
            logger.warning(f"Token not found for revocation: {jti[:8]}...")
            return False
        except Exception as e:
            logger.error(f"Error revoking token {jti[:8]}...: {str(e)}")
            raise SecurityError(f"Failed to revoke token: {str(e)}")

    @staticmethod
    @transaction.atomic
    def cleanup_expired_tokens() -> int:
        """
        Clean up expired tokens and sessions in batches.
        Returns count of cleaned tokens.
        """
        try:
            now = timezone.now()
            total_cleaned = 0

            # Process in batches to avoid locking too many rows
            while True:
                # Get batch of expired sessions
                expired_sessions = UserSession.objects.filter(
                    expires_at__lt=now, is_active=True
                ).values_list("id", flat=True)[:TOKEN_CLEANUP_BATCH_SIZE]

                if not expired_sessions:
                    break

                # Update batch
                count = UserSession.objects.filter(
                    id__in=list(expired_sessions)
                ).update(is_active=False)

                total_cleaned += count

                # Small delay between batches
                if count == TOKEN_CLEANUP_BATCH_SIZE:
                    import time

                    time.sleep(0.1)

            if total_cleaned > 0:
                logger.info(f"Cleaned up {total_cleaned} expired sessions")

            return total_cleaned

        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            raise SecurityError(f"Failed to cleanup tokens: {str(e)}")

    @staticmethod
    def get_active_session_count(user) -> int:
        """Get count of active sessions for a user."""
        try:
            return UserSession.objects.filter(
                user=user, is_active=True, expires_at__gt=timezone.now()
            ).count()
        except Exception as e:
            logger.error(f"Error getting session count for user {user.id}: {str(e)}")
            return 0


def get_jwt_settings() -> Dict[str, Any]:
    """
    Get JWT settings with security-first defaults.
    FIXED: Dedicated JWT signing key, secure defaults.
    """
    # Try to get dedicated JWT key, fall back to SECRET_KEY with warning
    jwt_signing_key = getattr(settings, "JWT_SIGNING_KEY", None)
    if not jwt_signing_key:
        logger.warning(
            "JWT_SIGNING_KEY not set, using SECRET_KEY. "
            "This is not recommended for production!"
        )
        jwt_signing_key = settings.SECRET_KEY

    return {
        "ACCESS_TOKEN_LIFETIME": getattr(
            settings, "JWT_ACCESS_TOKEN_LIFETIME", timedelta(hours=1)
        ),
        "REFRESH_TOKEN_LIFETIME": getattr(
            settings, "JWT_REFRESH_TOKEN_LIFETIME", timedelta(days=14)
        ),
        "ROTATE_REFRESH_TOKENS": getattr(settings, "JWT_ROTATE_REFRESH_TOKENS", True),
        "BLACKLIST_AFTER_ROTATION": getattr(
            settings, "JWT_BLACKLIST_AFTER_ROTATION", True
        ),
        "ALGORITHM": getattr(settings, "JWT_ALGORITHM", "HS256"),
        "SIGNING_KEY": jwt_signing_key,
        "VERIFYING_KEY": getattr(settings, "JWT_VERIFYING_KEY", None),
        "AUDIENCE": getattr(settings, "JWT_AUDIENCE", None),
        "ISSUER": getattr(settings, "JWT_ISSUER", None),
        "AUTH_HEADER_TYPES": getattr(settings, "JWT_AUTH_HEADER_TYPES", ("Bearer",)),
        "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
        "JTI_CLAIM": "jti",
        # Security settings
        "TOKEN_OBTAIN_SERIALIZER": "users.serializers.LoginSerializer",
        "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
        "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
        "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
        # Sliding tokens (optional)
        "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
        "SLIDING_TOKEN_LIFETIME": getattr(
            settings, "JWT_SLIDING_TOKEN_LIFETIME", timedelta(hours=1)
        ),
        "SLIDING_TOKEN_REFRESH_LIFETIME": getattr(
            settings, "JWT_SLIDING_TOKEN_REFRESH_LIFETIME", timedelta(days=14)
        ),
    }


class SecurityMiddleware:
    """
    Additional security middleware for JWT and session handling.
    ENHANCED: Better security headers and request validation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre-process security checks
        self._validate_request(request)

        # Get response
        response = self.get_response(request)

        # Add security headers
        self._add_security_headers(request, response)

        return response

    def _validate_request(self, request) -> None:
        """Validate incoming request for security issues."""
        # Check for suspicious headers
        suspicious_headers = [
            "X-Original-URL",
            "X-Rewrite-URL",
            "X-Forwarded-Host",
        ]

        for header in suspicious_headers:
            if header in request.META:
                logger.warning(
                    f"Suspicious header detected: {header} from {request.META.get('REMOTE_ADDR')}"
                )

        # Validate content type for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.content_type
            if content_type and "multipart" in content_type:
                # Additional validation for file uploads
                self._validate_file_upload(request)

    def _validate_file_upload(self, request) -> None:
        """Validate file upload requests."""
        if hasattr(request, "FILES"):
            for uploaded_file in request.FILES.values():
                # Check file size
                max_size = getattr(
                    settings, "MAX_UPLOAD_SIZE", 10 * 1024 * 1024
                )  # 10MB
                if uploaded_file.size > max_size:
                    logger.warning(
                        f"File upload too large: {uploaded_file.size} bytes from {request.META.get('REMOTE_ADDR')}"
                    )

    def _add_security_headers(self, request, response) -> None:
        """FIXED: A-202 - Add comprehensive security headers with HSTS."""
        # Only add headers for API responses
        if not request.path.startswith("/api/"):
            return

        # FIXED: A-202 - Updated security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",  # FIXED: A-202 - Added HSTS
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
        }
        # FIXED: A-202 - Removed deprecated X-XSS-Protection

        for header, value in security_headers.items():
            response[header] = value

        # Content Security Policy
        if not response.has_header("Content-Security-Policy"):
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self'",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response["Content-Security-Policy"] = "; ".join(csp_directives)

        # Cache control for authenticated responses
        if hasattr(request, "user") and request.user.is_authenticated:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        # Add request ID for tracing
        if hasattr(request, "id"):
            response["X-Request-ID"] = str(request.id)

    def process_exception(self, request, exception):
        """Log authentication-related exceptions with context."""
        if isinstance(exception, (InvalidToken, AuthenticationFailed)):
            logger.warning(
                f"Authentication exception on {request.path}: {str(exception)} "
                f"from {request.META.get('REMOTE_ADDR')}"
            )
        elif isinstance(exception, SecurityError):
            logger.error(
                f"Security exception on {request.path}: {str(exception)} "
                f"from {request.META.get('REMOTE_ADDR')}"
            )
        return None


# Utility functions
def create_token_for_user(
    user, session_type: str = "web", ip_address: str = None, user_agent: str = None
) -> Dict[str, str]:
    """
    FIXED: A-205 - Create JWT tokens for a user with mandatory IP and user-agent.
    """
    from .services import SessionService

    # FIXED: A-205 - Make ip_address and user_agent mandatory
    if ip_address is None:
        raise ValueError("ip_address is required for audit trail")
    if user_agent is None:
        raise ValueError("user_agent is required for audit trail")

    try:
        # Create tokens
        refresh = RefreshToken.for_user(user)

        # Set appropriate expiry based on session type
        if session_type == "mobile":
            expires_at = timezone.now() + timedelta(days=30)
        elif session_type == "api":
            expires_at = timezone.now() + timedelta(days=365)
        else:  # web
            expires_at = timezone.now() + timedelta(days=14)

        # Create session
        session = UserSession.objects.create(
            user=user,
            session_key=str(refresh.access_token["jti"]),
            ip_address=ip_address,  # FIXED: A-205 - Now properly set
            user_agent=user_agent,  # FIXED: A-205 - Now properly set
            expires_at=expires_at,
            device_type=session_type,
            login_method="api",
        )

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "session_id": session.id,
            "expires_at": expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error creating token for user {user.id}: {str(e)}")
        raise SecurityError("Failed to create authentication token")


# Export authentication classes and utilities
__all__ = [
    "CustomJWTAuthentication",
    "SessionTokenAuthentication",
    "TokenRevocationService",
    "jwt_response_payload_handler",
    "get_jwt_settings",
    "SecurityMiddleware",
    "create_token_for_user",
    "SecurityError",
    "SessionValidationError",
]
