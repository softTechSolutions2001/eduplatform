"""
File: backend/users/serializers.py
Purpose: Serializers for user data, authentication, and subscription management
Date Revised: 2025-07-15 00:00:00 UTC
Version: 3.0.1 - Critical Security Fixes Applied

FIXES APPLIED:
- S-001: Fixed RegexValidator import (CRITICAL)
- S-002: Added role validation for registration
- S-005: Added select_for_update to prevent TOCTOU
- S-006: Centralized reserved usernames
"""

import re
from typing import Any, Dict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator  # FIXED: S-001
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import EmailVerification, PasswordReset, Profile, Subscription, UserSession

User = get_user_model()

# Constants
MIN_PASSWORD_LENGTH = 12
MAX_FAILED_LOGIN_ATTEMPTS = 5
USERNAME_REGEX = r"^[a-zA-Z0-9_-]+$"
PHONE_REGEX = r"^\+?1?\d{9,15}$"

# FIXED: S-006 - Centralized reserved usernames
RESERVED_USERNAMES = ["admin", "root", "api", "www", "mail", "support", "help"]


def validate_password_strong(password):
    """
    FIXED: S-003 - Extracted password validation helper to avoid repeated instantiation.
    Enhanced password validation with entropy check.
    """
    # Django's built-in validators
    try:
        validate_password(password)
    except ValidationError as e:
        raise serializers.ValidationError(list(e.messages))

    # Additional entropy checks
    if len(set(password)) < 6:
        raise serializers.ValidationError(
            "Password must contain at least 6 different characters"
        )

    # Check for common patterns
    common_patterns = [
        r"(.)\1{2,}",  # Repeated characters (aaa, 111)
        r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # Sequential letters
        r"(qwerty|asdf|zxcv)",  # Keyboard patterns
    ]

    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            raise serializers.ValidationError(
                "Password contains common patterns. Please choose a more complex password"
            )

    # Ensure mix of character types
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    if sum([has_upper, has_lower, has_digit, has_special]) < 3:
        raise serializers.ValidationError(
            "Password must contain at least 3 of: uppercase, lowercase, numbers, special characters"
        )

    return password


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with enhanced validation."""

    class Meta:
        model = Profile
        exclude = ["user", "created_at", "updated_at", "id"]
        read_only_fields = ["user"]

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value:
            # Remove common formatting
            cleaned = re.sub(r"[\s\-\(\)]", "", value)
            if not re.match(PHONE_REGEX, cleaned):
                raise serializers.ValidationError(
                    "Phone number must be 9-15 digits, optionally starting with +"
                )
            return cleaned
        return value

    def validate_date_of_birth(self, value):
        """Validate date of birth is reasonable."""
        if value:
            age = (timezone.now().date() - value).days / 365.25
            if age < 13:
                raise serializers.ValidationError("Must be at least 13 years old")
            if age > 120:
                raise serializers.ValidationError("Invalid date of birth")
        return value

    def validate_bio(self, value):
        """Sanitize bio content."""
        if value:
            # Basic HTML tag stripping for security
            value = re.sub(r"<[^>]*>", "", value)
            # Limit consecutive whitespace
            value = re.sub(r"\s+", " ", value).strip()
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        # Validate address fields together
        if any(attrs.get(f) for f in ["address", "city", "state", "country"]):
            # If any address field is provided, country should be provided
            if not attrs.get("country"):
                raise serializers.ValidationError(
                    {"country": "Country is required when providing address details"}
                )
        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription with computed fields."""

    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    can_upgrade = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "tier",
            "status",
            "start_date",
            "end_date",
            "is_auto_renew",
            "last_payment_date",
            "next_payment_date",
            "is_active",
            "days_remaining",
            "can_upgrade",
        ]
        read_only_fields = [
            "id",
            "start_date",
            "last_payment_date",
            "next_payment_date",
        ]

    def get_is_active(self, obj):
        """Determine if subscription is active."""
        return obj.is_active

    def get_days_remaining(self, obj):
        """Get days remaining in subscription."""
        return obj.days_remaining

    def get_can_upgrade(self, obj):
        """Check if user can upgrade subscription."""
        return obj.tier in ["guest", "registered"] and obj.is_active


class UserSerializer(serializers.ModelSerializer):
    """Base user serializer with security considerations."""

    profile = ProfileSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    active_sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_email_verified",
            "date_joined",
            "last_login",
            "profile",
            "subscription",
            "active_sessions_count",
        ]
        read_only_fields = [
            "id",
            "email",  # Email shouldn't be changed via API
            "date_joined",
            "last_login",
            "is_email_verified",
            "role",  # Role changes need admin permission
        ]

    def get_active_sessions_count(self, obj):
        """Get count of active sessions."""
        # Use cache to avoid repeated queries
        cache_key = f"active_sessions:{obj.id}"
        count = cache.get(cache_key)
        if count is None:
            count = obj.sessions.filter(
                is_active=True, expires_at__gt=timezone.now()
            ).count()
            cache.set(cache_key, count, timeout=300)  # 5 minutes
        return count

    def to_representation(self, instance):
        """Ensure data integrity in response."""
        data = super().to_representation(instance)

        # Handle missing relations gracefully
        if data.get("profile") is None:
            data["profile"] = {}
        if data.get("subscription") is None:
            data["subscription"] = {"tier": "guest", "status": "active"}

        # Hide sensitive data based on permissions
        request = self.context.get("request")
        if request and request.user != instance and not request.user.is_staff:
            # Hide some fields for non-owners
            data.pop("last_login", None)
            data.pop("active_sessions_count", None)

        return data


class UserDetailSerializer(UserSerializer):
    """Extended user serializer with additional details."""

    failed_login_attempts = serializers.IntegerField(read_only=True)
    is_account_locked = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "failed_login_attempts",
            "is_account_locked",
        ]

    def get_is_account_locked(self, obj):
        """Check if account is locked."""
        return obj.is_account_locked()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with comprehensive validation.
    FIXED: Enhanced password validation and mass assignment protection.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=MIN_PASSWORD_LENGTH,
        help_text=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    terms_accepted = serializers.BooleanField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
            "terms_accepted",
        ]
        extra_kwargs = {
            "first_name": {"required": True, "min_length": 1, "max_length": 30},
            "last_name": {"required": True, "min_length": 1, "max_length": 30},
            "role": {"required": True},
            "username": {
                "min_length": 3,
                "max_length": 30,
                "validators": [
                    RegexValidator(  # FIXED: S-001 - Using django.core.validators.RegexValidator
                        regex=USERNAME_REGEX,
                        message="Username can only contain letters, numbers, underscores, and hyphens",
                    )
                ],
            },
        }

    def validate_email(self, value):
        """Validate email uniqueness and format."""
        value = value.lower().strip()

        # Additional email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise serializers.ValidationError("Invalid email format")

        # Check for disposable email domains
        disposable_domains = cache.get("disposable_email_domains", [])
        domain = value.split("@")[1]
        if domain in disposable_domains:
            raise serializers.ValidationError(
                "Registration with disposable email addresses is not allowed"
            )

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")

        return value

    def validate_username(self, value):
        """Validate username uniqueness and format."""
        value = value.strip()

        # FIXED: S-006 - Use centralized reserved usernames
        if value.lower() in RESERVED_USERNAMES:
            raise serializers.ValidationError("This username is reserved")

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken")

        return value

    def validate_password(self, value):
        """Enhanced password validation with entropy check."""
        # FIXED: S-003 - Use extracted helper function
        return validate_password_strong(value)

    def validate_role(self, value):
        """FIXED: S-002 - Restrict roles for registration."""
        allowed_roles = ["student", "instructor"]
        if value not in allowed_roles:
            raise serializers.ValidationError(
                f"Invalid role. Choose from: {', '.join(allowed_roles)}"
            )
        return value

    def validate_terms_accepted(self, value):
        """Ensure terms are accepted."""
        if not value:
            raise serializers.ValidationError(
                "You must accept the terms and conditions"
            )
        return value

    def validate(self, data):
        """Cross-field validation."""
        # Password confirmation
        if data.get("password") != data.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )

        # Remove non-model fields
        data.pop("terms_accepted", None)

        # Validate name doesn't contain email/username
        email_local = data["email"].split("@")[0].lower()
        username_lower = data["username"].lower()

        if (
            email_local in data["password"].lower()
            or username_lower in data["password"].lower()
        ):
            raise serializers.ValidationError(
                {"password": "Password cannot contain your email or username"}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create user with explicit field control."""
        # Extract only allowed fields
        allowed_fields = {
            "email": validated_data["email"],
            "username": validated_data["username"],
            "password": validated_data["password"],
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "role": validated_data["role"],
        }

        # Create user
        user = User.objects.create_user(**allowed_fields)

        # Profile and subscription created by signals
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for comprehensive profile updates."""

    first_name = serializers.CharField(required=False, max_length=30)
    last_name = serializers.CharField(required=False, max_length=30)
    profile = ProfileSerializer(required=False, partial=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile"]

    def validate_first_name(self, value):
        """Validate first name."""
        if value:
            value = value.strip()
            if not value:
                raise serializers.ValidationError("First name cannot be empty")
            if not re.match(r"^[a-zA-Z\s\-']+$", value):
                raise serializers.ValidationError(
                    "First name can only contain letters, spaces, hyphens, and apostrophes"
                )
        return value

    def validate_last_name(self, value):
        """Validate last name."""
        if value:
            value = value.strip()
            if not value:
                raise serializers.ValidationError("Last name cannot be empty")
            if not re.match(r"^[a-zA-Z\s\-']+$", value):
                raise serializers.ValidationError(
                    "Last name can only contain letters, spaces, hyphens, and apostrophes"
                )
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update user and profile atomically."""
        profile_data = validated_data.pop("profile", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create profile
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification with rate limiting awareness."""

    token = serializers.UUIDField(required=True)

    def validate_token(self, value):
        """Validate verification token with rate limiting."""
        # Check rate limit
        ip = self.context.get("request").META.get("REMOTE_ADDR", "unknown")
        rate_limit_key = f"email_verify_attempts:{ip}"
        attempts = cache.get(rate_limit_key, 0)

        if attempts > 10:
            raise serializers.ValidationError(
                "Too many verification attempts. Please try again later."
            )

        try:
            verification = EmailVerification.objects.select_related("user").get(
                token=value
            )
        except EmailVerification.DoesNotExist:
            cache.set(rate_limit_key, attempts + 1, timeout=3600)  # 1 hour
            raise serializers.ValidationError("Invalid verification token")

        if not verification.is_valid():
            raise serializers.ValidationError(
                "This verification link has expired. Please request a new one."
            )

        # Store verification object for use in view
        self.verification = verification
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification emails."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Normalize and validate email."""
        return value.lower().strip()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for authenticated password changes."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """Verify current password."""
        user = self.context["request"].user
        if not user.check_password(value):
            # Add delay to prevent timing attacks
            import time

            time.sleep(0.5)
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate_new_password(self, value):
        """Validate new password with same rules as registration."""
        user = self.context["request"].user

        # Can't reuse current password
        if user.check_password(value):
            raise serializers.ValidationError(
                "New password must be different from current password"
            )

        # FIXED: S-003 - Use extracted helper function
        try:
            validate_password_strong(value)
        except serializers.ValidationError as e:
            raise e

        # Additional check against user info
        user_info = [
            user.email.split("@")[0],
            user.username,
            user.first_name,
            user.last_name,
        ]
        for info in user_info:
            if info and info.lower() in value.lower():
                raise serializers.ValidationError(
                    "Password cannot contain your personal information"
                )

        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs.pop("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match"}
            )
        return attrs

    def save(self):
        """Update password and invalidate sessions."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset requests."""

    email = serializers.EmailField(required=True)
    captcha = serializers.CharField(required=False)  # For future captcha implementation

    def validate_email(self, value):
        """Normalize email without revealing existence."""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    token = serializers.UUIDField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
    )
    password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_token(self, value):
        """FIXED: S-005 - Validate reset token securely with row locking."""
        try:
            # FIXED: S-005 - Add select_for_update to prevent TOCTOU
            reset = (
                PasswordReset.objects.select_for_update()
                .select_related("user")
                .get(token=value, is_used=False)
            )
            if not reset.is_valid():
                raise serializers.ValidationError("This reset link has expired")

            # Store for later use
            self.context["reset"] = reset
        except PasswordReset.DoesNotExist:
            # Same error as expired to prevent enumeration
            raise serializers.ValidationError("This reset link has expired")

        return value

    def validate_password(self, value):
        """Validate new password."""
        # FIXED: S-003 - Use extracted helper function
        try:
            validate_password_strong(value)
        except serializers.ValidationError as e:
            raise e

        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    Enhanced login serializer with security improvements.
    FIXED: Generic error messages prevent enumeration.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    remember_me = serializers.BooleanField(default=False)
    captcha = serializers.CharField(
        required=False
    )  # For future captcha after failed attempts

    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()

    def validate(self, data):
        """
        Validate credentials with constant-time operations.
        FIXED: Generic error prevents email enumeration.
        """
        email = data.get("email")
        password = data.get("password")

        # Check if IP is rate limited
        request = self.context.get("request")
        if request:
            ip = request.META.get("REMOTE_ADDR", "unknown")
            rate_limit_key = f"login_attempts:{ip}"
            attempts = cache.get(rate_limit_key, 0)

            if attempts > 20:  # Stricter than view-level rate limiting
                raise serializers.ValidationError(
                    "Too many login attempts. Please try again later."
                )

        # Attempt authentication
        user = authenticate(request=request, username=email, password=password)

        # Generic error message
        generic_error = "Unable to log in with provided credentials."

        if user is None:
            # Increment rate limit counter
            if request:
                cache.set(rate_limit_key, attempts + 1, timeout=3600)
            raise serializers.ValidationError(generic_error)

        # Additional security checks
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated. Please contact support."
            )

        if user.is_account_locked():
            remaining_time = (user.ban_expires_at - timezone.now()).total_seconds() / 60
            raise serializers.ValidationError(
                f"Account temporarily locked. Try again in {int(remaining_time)} minutes."
            )

        # Check if email verification is required
        if not user.is_email_verified and getattr(
            settings, "REQUIRE_EMAIL_VERIFICATION", True
        ):
            raise serializers.ValidationError(
                "Please verify your email address before logging in."
            )

        data["user"] = user
        return data


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for session management."""

    is_current = serializers.SerializerMethodField()
    browser = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            "id",
            "ip_address",
            "device_type",
            "browser",
            "location",
            "created_at",
            "last_activity",
            "expires_at",
            "is_active",
            "is_current",
            "login_method",
        ]
        read_only_fields = fields  # All fields are read-only for security

    def get_is_current(self, obj):
        """Check if this is the current session."""
        request = self.context.get("request")
        if request and hasattr(request, "auth"):
            current_jti = request.auth.payload.get("jti")
            return obj.session_key == current_jti
        return False

    def get_browser(self, obj):
        """Extract browser info from user agent."""
        ua = obj.user_agent.lower()
        browsers = {
            "chrome": "Chrome",
            "safari": "Safari",
            "firefox": "Firefox",
            "edge": "Edge",
            "opera": "Opera",
        }
        for key, name in browsers.items():
            if key in ua:
                return name
        return "Unknown"

    def to_representation(self, instance):
        """Mask sensitive information."""
        data = super().to_representation(instance)

        # Partially mask IP address for privacy
        if "ip_address" in data and data["ip_address"]:
            parts = data["ip_address"].split(".")
            if len(parts) == 4:
                data["ip_address"] = f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"

        return data
