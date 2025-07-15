"""
File: backend/users/services.py
Purpose: Business logic services for users app
Date Created: 2025-07-15 00:00:00 UTC
Version: 1.0.0 - Extracted from views to follow DRY principles

CONSOLIDATES:
- Email sending logic (was duplicated in views)
- Session management (was scattered)
- Security logging (was inconsistent)
- IP/User-Agent extraction utilities
"""

import hashlib
import logging
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from .models import UserSession

logger = logging.getLogger(__name__)


class SecurityService:
    """Centralized security logging and utilities."""

    @staticmethod
    def get_client_ip(request):
        """Extract real client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            return x_real_ip

        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    @staticmethod
    def get_user_agent(request):
        """Extract user agent string."""
        return request.META.get("HTTP_USER_AGENT", "Unknown")[:500]

    @staticmethod
    def get_device_type(user_agent):
        """Determine device type from user agent."""
        if not user_agent or user_agent == "Unknown":
            return "Unknown"

        user_agent_lower = user_agent.lower()

        mobile_keywords = [
            "mobile",
            "android",
            "iphone",
            "ipod",
            "blackberry",
            "windows phone",
        ]
        if any(keyword in user_agent_lower for keyword in mobile_keywords):
            return "Mobile"

        tablet_keywords = ["ipad", "tablet", "kindle"]
        if any(keyword in user_agent_lower for keyword in tablet_keywords):
            return "Tablet"

        return "Desktop"

    @staticmethod
    def get_masked_ip(ip_address):
        """Mask IP address for privacy-compliant logging."""
        if not ip_address or ip_address == "0.0.0.0":
            return "0.0.0.0"

        try:
            if "." in ip_address and ip_address.count(".") == 3:
                parts = ip_address.split(".")
                return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
            elif ":" in ip_address:
                parts = ip_address.split(":")
                return f"{':'.join(parts[:4])}:xxxx:xxxx:xxxx:xxxx"
        except Exception:
            pass

        return "masked"

    @staticmethod
    def sanitize_email_for_logging(email):
        """Sanitize email address for secure logging."""
        if not email:
            return "unknown"

        email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
        domain = email.split("@")[-1] if "@" in email else "unknown"
        return f"user_{email_hash}@{domain}"

    @classmethod
    def log_failed_registration(cls, request, errors):
        """Log failed registration attempt."""
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.warning(f"Registration validation failed from {ip_address}: {errors}")

    @classmethod
    def log_successful_registration(cls, request, user):
        """Log successful registration."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(
            f"User registration successful: {sanitized_email} from {ip_address}"
        )

    @classmethod
    def log_failed_login(cls, request, errors):
        """Log failed login attempt."""
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.warning(f"Login validation failed from {ip_address}")

    @classmethod
    def log_successful_login(cls, request, user):
        """Log successful login."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        device_type = cls.get_device_type(cls.get_user_agent(request))
        logger.info(
            f"Successful login: {sanitized_email} from {ip_address} using {device_type}"
        )

    @classmethod
    def log_successful_logout(cls, request):
        """Log successful logout."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(f"Successful logout: {sanitized_email} from {ip_address}")

    @classmethod
    def log_profile_update(cls, request):
        """Log profile update."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(f"Profile updated for {sanitized_email}")

    @classmethod
    def log_comprehensive_profile_update(cls, request):
        """Log comprehensive profile update."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(f"Comprehensive profile update for {sanitized_email}")

    @classmethod
    def log_password_change(cls, request):
        """Log password change."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(
            f"Password changed successfully for {sanitized_email} from {ip_address}"
        )

    @classmethod
    def log_password_reset_request(cls, request, user, success):
        """Log password reset request."""
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        if success and user:
            sanitized_email = cls.sanitize_email_for_logging(user.email)
            logger.info(
                f"Password reset requested for {sanitized_email} from {ip_address}"
            )
        else:
            logger.info(
                f"Password reset requested for non-existent email from {ip_address}"
            )

    @classmethod
    def log_password_reset_completion(cls, request, user):
        """Log password reset completion."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(f"Password reset completed for {sanitized_email} from {ip_address}")

    @classmethod
    def log_email_verification(cls, request, user, success):
        """Log email verification attempt."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        status = "successfully" if success else "failed"
        logger.info(f"Email verified {status}: {sanitized_email} from {ip_address}")

    @classmethod
    def log_verification_resend(cls, request, user):
        """Log verification email resend."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(f"Verification email resent to {sanitized_email} from {ip_address}")

    @classmethod
    def log_session_invalidation(cls, request, session):
        """Log session invalidation."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(f"Session manually invalidated for {sanitized_email}")

    @classmethod
    def log_subscription_upgrade(cls, request, subscription):
        """Log subscription upgrade."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(
            f"Subscription upgraded to {subscription.tier} tier for {sanitized_email}"
        )

    @classmethod
    def log_subscription_cancellation(cls, request, subscription):
        """Log subscription cancellation."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(
            f"Subscription cancelled for {sanitized_email} ({subscription.tier} tier)"
        )

    @classmethod
    def log_subscription_downgrade(cls, request, subscription):
        """Log subscription downgrade."""
        sanitized_email = cls.sanitize_email_for_logging(request.user.email)
        logger.info(
            f"Subscription downgraded to {subscription.tier} tier for {sanitized_email}"
        )

    @classmethod
    def log_oauth_initiation(cls, request, provider):
        """Log OAuth flow initiation."""
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.info(f"{provider.title()} OAuth flow initiated from {ip_address}")

    @classmethod
    def log_social_auth_success(cls, request, user, provider):
        """Log successful social authentication."""
        sanitized_email = cls.sanitize_email_for_logging(user.email)
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        device_type = cls.get_device_type(cls.get_user_agent(request))
        logger.info(
            f"Social authentication successful: {sanitized_email} via {provider} from {ip_address} using {device_type}"
        )

    @classmethod
    def log_social_auth_error(cls, request, error):
        """Log social authentication error."""
        ip_address = cls.get_masked_ip(cls.get_client_ip(request))
        logger.error(f"Social auth error from {ip_address}: {error}")


class EmailService:
    """Centralized email sending service."""

    @staticmethod
    def send_verification_email(user, token):
        """Send email verification email."""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            subject = "Verify your EduPlatform account"

            try:
                message = render_to_string(
                    "users/email_verification.html",
                    {
                        "user": user,
                        "verification_url": verification_url,
                        "valid_hours": 48,
                    },
                )
            except Exception as e:
                logger.error(f"Error rendering email template: {str(e)}")
                message = f"""
                Hello {user.first_name},

                Thank you for registering with EduPlatform. Please verify your email by clicking the link below:

                {verification_url}

                This link is valid for 48 hours.

                If you didn't register for an account, please ignore this email.

                Best regards,
                The EduPlatform Team
                """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message if "<html" in message else None,
            )

            sanitized_email = SecurityService.sanitize_email_for_logging(user.email)
            logger.info(f"Verification email sent to {sanitized_email}")

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise

    @staticmethod
    def send_password_reset_email(user, token):
        """Send password reset email."""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            subject = "Reset your EduPlatform password"

            try:
                message = render_to_string(
                    "users/password_reset_email.html",
                    {
                        "user": user,
                        "reset_url": reset_url,
                        "valid_hours": 24,
                    },
                )
            except Exception as e:
                logger.error(f"Error rendering password reset template: {str(e)}")
                message = f"""
                Hello {user.first_name},

                You requested to reset your password for EduPlatform. Click the link below to reset it:

                {reset_url}

                This link is valid for 24 hours.

                If you didn't request a password reset, please ignore this email.

                Best regards,
                The EduPlatform Team
                """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message if "<html" in message else None,
            )

            sanitized_email = SecurityService.sanitize_email_for_logging(user.email)
            logger.info(f"Password reset email sent to {sanitized_email}")

        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise


class SessionService:
    """Centralized session management service."""

    @staticmethod
    @transaction.atomic
    def create_session(user, session_key, request, expires_at, login_method=None):
        """Create a new user session."""
        session_data = {
            "user": user,
            "session_key": session_key,
            "ip_address": SecurityService.get_client_ip(request),
            "user_agent": SecurityService.get_user_agent(request),
            "expires_at": expires_at,
            "device_type": SecurityService.get_device_type(
                SecurityService.get_user_agent(request)
            ),
            "location": "Unknown",  # Could integrate with GeoIP service
        }

        if login_method:
            session_data["login_method"] = login_method

        return UserSession.objects.create(**session_data)

    @staticmethod
    @transaction.atomic
    def invalidate_user_sessions(user, exclude_current=True, exclude_session_key=None):
        """Invalidate user sessions with optional exclusions."""
        queryset = UserSession.objects.filter(user=user, is_active=True)

        if exclude_session_key:
            queryset = queryset.exclude(session_key=exclude_session_key)

        updated_count = queryset.update(is_active=False)
        logger.info(f"Invalidated {updated_count} sessions for user")

        return updated_count

    @staticmethod
    @transaction.atomic
    def invalidate_session_by_key(user, session_key):
        """Invalidate specific session by key."""
        try:
            session = UserSession.objects.get(
                user=user, session_key=session_key, is_active=True
            )
            session.invalidate()
            return True
        except UserSession.DoesNotExist:
            logger.warning(f"Session not found for invalidation: {session_key[:8]}...")
            return False

    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions (for background task)."""
        expired_count = UserSession.objects.filter(
            expires_at__lt=timezone.now(), is_active=True
        ).update(is_active=False)

        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")

        return expired_count
