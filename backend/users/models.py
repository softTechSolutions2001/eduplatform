"""
File: backend/users/models.py
Purpose: User models with enhanced security logging and standardized properties
Date Revised: 2025-07-15 00:00:00 UTC
Version: 3.0.1 - Critical Security Fixes Applied

FIXES APPLIED:
- M-401: Fixed self-import in record_login_attempt
- M-402: Added note about PostgreSQL-only constraint
- M-403: Fixed subscription logic for cancelled guest tier
- M-404: Added upper-bound guard for session extension
- M-405: Simplified is_admin property logic
"""

import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import (
    EmailValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models, transaction
from django.db.models import CheckConstraint, F, Q, UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

# Constants
MAX_LOGIN_ATTEMPTS = 999
LOCKOUT_DURATION_MINUTES = 15
EXTENDED_LOCKOUT_HOURS = 24
LOCKOUT_THRESHOLD = 5
EXTENDED_LOCKOUT_THRESHOLD = 10
EMAIL_VERIFICATION_HOURS = 48
PASSWORD_RESET_HOURS = 24
SESSION_EXTENSION_HOURS = 24
DEFAULT_SUBSCRIPTION_DAYS = 30
MAX_SESSION_EXTENSION_HOURS = 168  # FIXED: M-404 - 7 days max


class LoginLog(models.Model):
    """
    Log of user login attempts.
    Used for security auditing and detecting suspicious activity.
    MOVED: This model definition moved before CustomUser to fix M-401
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="login_logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(max_length=500)
    successful = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = _("Login Log")
        verbose_name_plural = _("Login Logs")
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
            models.Index(fields=["successful", "timestamp"]),
            models.Index(fields=["user", "successful", "timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        status = "successful" if self.successful else "failed"
        return f"{status} login for {self.user.email} at {self.timestamp}"


class CustomUser(AbstractUser, PermissionsMixin):
    """
    Custom User model with email authentication and role-based permissions.
    This extends Django's AbstractUser with additional fields and functionality.
    """

    USER_ROLES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Administrator"),
        ("staff", "Staff"),
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        validators=[EmailValidator(message="Enter a valid email address")],
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        db_index=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r"^[a-zA-Z0-9_-]+$",
                message="Username can only contain letters, numbers, underscores, and hyphens",
            ),
        ],
    )
    role = models.CharField(
        max_length=20, choices=USER_ROLES, default="student", db_index=True
    )
    is_email_verified = models.BooleanField(default=False, db_index=True)
    date_joined = models.DateTimeField(default=timezone.now, db_index=True)
    last_login = models.DateTimeField(null=True, blank=True, db_index=True)

    # Security fields with proper constraints
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(MAX_LOGIN_ATTEMPTS)],
        help_text="Number of failed login attempts",
    )
    ban_expires_at = models.DateTimeField(
        null=True, blank=True, db_index=True, help_text="When temporary ban expires"
    )
    is_active = models.BooleanField(default=True, db_index=True)

    # Use email for authentication instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["is_email_verified"]),
            models.Index(fields=["ban_expires_at"]),
            models.Index(fields=["last_login"]),
            models.Index(fields=["date_joined"]),
        ]
        constraints = [
            CheckConstraint(
                check=Q(failed_login_attempts__gte=0)
                & Q(failed_login_attempts__lte=MAX_LOGIN_ATTEMPTS),
                name="valid_failed_login_attempts",
            ),
            # FIXED: M-402 - Added comment about PostgreSQL-only constraint
            # NOTE: This constraint only works on PostgreSQL. On SQLite/MySQL, it will be silently ignored.
            # For production deployments on other databases, implement this validation in clean() method.
            CheckConstraint(
                check=Q(
                    email__regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),
                name="valid_email_format",
            ),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def has_role(self, role):
        """Check if the user has a specific role."""
        return self.role == role

    @transaction.atomic
    def record_login_attempt(self, successful=False, request=None):
        """
        FIXED: M-401 - Record a login attempt without self-import.
        Using direct LoginLog reference since it's defined above.
        """
        # Extract IP and User-Agent from request if available
        ip_address = "0.0.0.0"
        user_agent = "Unknown"

        if request:
            # Simple extraction to avoid circular imports
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(",")[0].strip()
            else:
                ip_address = request.META.get("HTTP_X_REAL_IP", "") or request.META.get(
                    "REMOTE_ADDR", "0.0.0.0"
                )
            user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")[:500]

        # Record the login attempt
        LoginLog.objects.create(
            user=self,
            ip_address=ip_address,
            user_agent=user_agent,
            successful=successful,
        )

        if successful:
            # Reset failed attempts on successful login
            CustomUser.objects.filter(pk=self.pk).update(
                failed_login_attempts=0, ban_expires_at=None
            )
            return False

        # Handle failed login attempt with atomic increment
        CustomUser.objects.filter(pk=self.pk).update(
            failed_login_attempts=F("failed_login_attempts") + 1
        )

        # Refresh from DB to get updated value
        self.refresh_from_db(fields=["failed_login_attempts"])

        # Implement exponential backoff for repeated failed attempts
        ban_until = None
        if self.failed_login_attempts >= EXTENDED_LOCKOUT_THRESHOLD:
            # Ban for 24 hours after 10 failed attempts
            ban_until = timezone.now() + timedelta(hours=EXTENDED_LOCKOUT_HOURS)
        elif self.failed_login_attempts >= LOCKOUT_THRESHOLD:
            # Ban for 15 minutes after 5 failed attempts
            ban_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

        if ban_until:
            CustomUser.objects.filter(pk=self.pk).update(ban_expires_at=ban_until)
            self.ban_expires_at = ban_until

        return self.is_account_locked()

    def is_account_locked(self):
        """
        Check if the account is temporarily locked due to failed login attempts.
        """
        if not self.ban_expires_at:
            return False
        # Use timezone-aware comparison
        return self.ban_expires_at > timezone.now()

    def unlock_account(self):
        """
        Separate method to unlock account and reset failed attempts.
        """
        if self.ban_expires_at and self.ban_expires_at <= timezone.now():
            CustomUser.objects.filter(pk=self.pk).update(
                ban_expires_at=None, failed_login_attempts=0
            )
            self.ban_expires_at = None
            self.failed_login_attempts = 0
            return True
        return False

    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == "student"

    @property
    def is_instructor(self):
        """Check if user is an instructor."""
        return self.role == "instructor"

    @property
    def is_admin(self):
        """FIXED: M-405 - Simplified admin check."""
        return self.is_superuser or self.role == "admin"

    @property
    def is_staff_member(self):
        """Check if user is a staff member."""
        return self.role == "staff" or self.is_staff


class Profile(models.Model):
    """
    Extended user profile information.
    Contains additional user data beyond authentication needs.
    """

    PHONE_REGEX = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits.",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/%Y/%m/%d/", null=True, blank=True
    )
    bio = models.TextField(blank=True, max_length=500)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, validators=[PHONE_REGEX])
    address = models.TextField(blank=True, max_length=200)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)

    # Instructor-specific fields
    expertise = models.CharField(max_length=200, blank=True)
    teaching_experience = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(50)]
    )

    # Student-specific fields
    educational_background = models.TextField(blank=True, max_length=500)
    interests = models.TextField(blank=True, max_length=500)

    # Notification preferences
    receive_email_notifications = models.BooleanField(default=True)
    receive_marketing_emails = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"


class EmailVerification(models.Model):
    """
    Email verification token management.
    Used for verifying user email addresses during registration.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verifications",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = _("Email Verification")
        verbose_name_plural = _("Email Verifications")
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["user", "is_used", "expires_at"]),
        ]

    def __str__(self):
        return f"Email verification for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 48 hours from creation
            self.expires_at = timezone.now() + timedelta(hours=EMAIL_VERIFICATION_HOURS)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the verification token is still valid."""
        if self.is_used:
            return False
        return timezone.now() <= self.expires_at

    @transaction.atomic
    def use_token(self):
        """Mark the token as used and the user's email as verified."""
        if self.is_valid():
            self.is_used = True
            self.verified_at = timezone.now()
            self.save(update_fields=["is_used", "verified_at"])

            # Update user's email verification status
            CustomUser.objects.filter(pk=self.user_id).update(is_email_verified=True)
            return True
        return False


class PasswordReset(models.Model):
    """
    Password reset token management.
    Used for secure password reset functionality.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_resets",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = _("Password Reset")
        verbose_name_plural = _("Password Resets")
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 24 hours from creation
            self.expires_at = timezone.now() + timedelta(hours=PASSWORD_RESET_HOURS)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the password reset token is still valid."""
        if self.is_used:
            return False
        return timezone.now() <= self.expires_at

    @transaction.atomic
    def use_token(self):
        """Mark the token as used."""
        if self.is_valid():
            self.is_used = True
            self.used_at = timezone.now()
            self.save(update_fields=["is_used", "used_at"])
            return True
        return False


class UserSession(models.Model):
    """
    Track active user sessions.
    Useful for managing concurrent logins and session invalidation.
    """

    DEVICE_CHOICES = [
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
        ("bot", "Bot"),
        ("unknown", "Unknown"),
    ]

    LOGIN_METHODS = [
        ("credentials", "Username/Password"),
        ("social_google", "Google OAuth"),
        ("social_github", "GitHub OAuth"),
        ("api_key", "API Key"),
        ("sso", "Single Sign-On"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions"
    )
    session_key = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    device_type = models.CharField(
        max_length=50, choices=DEVICE_CHOICES, default="unknown"
    )
    location = models.CharField(max_length=100, blank=True)
    login_method = models.CharField(
        max_length=50, choices=LOGIN_METHODS, default="credentials"
    )

    class Meta:
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["session_key"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["last_activity"]),
            models.Index(fields=["user", "is_active", "expires_at"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"

    def is_valid(self):
        """Check if session is still valid."""
        return self.is_active and timezone.now() <= self.expires_at

    def extend_session(self, duration_hours=SESSION_EXTENSION_HOURS):
        """FIXED: M-404 - Extend the session expiration time with upper bound."""
        # FIXED: M-404 - Add upper-bound guard to prevent indefinite extension
        max_extension = timedelta(hours=MAX_SESSION_EXTENSION_HOURS)
        requested_extension = timedelta(hours=duration_hours)

        # Calculate new expiry time
        now = timezone.now()
        new_expiry = now + requested_extension
        max_allowed_expiry = now + max_extension

        # Cap at maximum allowed extension
        if new_expiry > max_allowed_expiry:
            self.expires_at = max_allowed_expiry
        else:
            self.expires_at = new_expiry

        self.save(update_fields=["expires_at", "last_activity"])

    @transaction.atomic
    def invalidate(self):
        """Invalidate this session."""
        self.is_active = False
        self.save(update_fields=["is_active"])


class Subscription(models.Model):
    """
    Subscription model for tracking user subscription status.
    """

    SUBSCRIPTION_TIERS = [
        ("guest", "Guest"),
        ("registered", "Registered"),
        ("premium", "Premium"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),
    ]

    PAYMENT_METHODS = [
        ("card", "Credit/Debit Card"),
        ("paypal", "PayPal"),
        ("bank", "Bank Transfer"),
        ("crypto", "Cryptocurrency"),
        ("demo", "Demo/Trial"),
    ]

    user = models.OneToOneField(
        "users.CustomUser", on_delete=models.CASCADE, related_name="subscription"
    )
    tier = models.CharField(
        max_length=20, choices=SUBSCRIPTION_TIERS, default="registered", db_index=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True
    )
    start_date = models.DateTimeField(auto_now_add=True, db_index=True)
    end_date = models.DateTimeField(null=True, blank=True, db_index=True)
    is_auto_renew = models.BooleanField(default=False)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)

    # Payment details
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHODS, blank=True, null=True
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["tier", "status"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["status", "end_date"]),
        ]
        constraints = [
            UniqueConstraint(fields=["user"], name="unique_user_subscription"),
            CheckConstraint(
                check=Q(amount_paid__gte=Decimal("0.00")) | Q(amount_paid__isnull=True),
                name="valid_amount_paid",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.tier} ({self.status})"

    @property
    def is_active(self):
        """FIXED: M-403 - Check if subscription is active with proper status validation."""
        # FIXED: M-403 - For guest tier, must also check status
        if self.tier == "guest":
            return self.status == "active"

        if self.status != "active":
            return False

        if self.end_date and self.end_date < timezone.now():
            return False

        return True

    @property
    def days_remaining(self):
        """Calculate days remaining in subscription."""
        if self.tier == "guest" or not self.end_date:
            return None

        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    @classmethod
    @transaction.atomic
    def create_for_user(cls, user, tier="registered", days=DEFAULT_SUBSCRIPTION_DAYS):
        """Create a new subscription for user."""
        end_date = None
        if tier not in ["guest"]:
            end_date = timezone.now() + timedelta(days=days)

        subscription, created = cls.objects.get_or_create(
            user=user, defaults={"tier": tier, "status": "active", "end_date": end_date}
        )
        return subscription

    def extend_subscription(self, days):
        """Extend subscription by specified days."""
        if self.end_date:
            # If already has end date, extend from that
            self.end_date += timedelta(days=days)
        else:
            # Otherwise extend from now
            self.end_date = timezone.now() + timedelta(days=days)
        self.save(update_fields=["end_date", "updated_at"])

    def cancel_subscription(self):
        """Cancel subscription and stop auto-renewal."""
        self.status = "cancelled"
        self.is_auto_renew = False
        self.save(update_fields=["status", "is_auto_renew", "updated_at"])
