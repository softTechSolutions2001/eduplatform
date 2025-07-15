"""
File: backend/users/managers.py
Purpose: Custom user manager implementation
Date Revised: 2025-07-15 00:00:00 UTC
Version: 2.0.0 - Consolidated and Fixed

FIXES APPLIED:
- Consolidated single CustomUserManager (removed duplication)
- Added proper error handling and validation
- Fixed circular import by moving Profile creation to signals
- Added consistent feature set for superuser creation
"""

import re

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    FIXED: Single source of truth for user creation logic.
    """

    def _validate_email(self, email):
        """Validate email format and domain."""
        if not email:
            raise ValueError(_("The Email field must be set"))

        # Basic email format validation
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            raise ValidationError(_("Invalid email format"))

        return self.normalize_email(email)

    def _validate_username(self, username):
        """Validate username format."""
        if not username:
            raise ValueError(_("The Username field must be set"))

        # Username should be alphanumeric with underscores/hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise ValidationError(
                _(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )
            )

        if len(username) < 3:
            raise ValidationError(_("Username must be at least 3 characters long"))

        return username

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a user with the given email, username and password.
        FIXED: Proper validation and error handling.
        """
        # Validate inputs
        email = self._validate_email(email)
        username = self._validate_username(username)

        # Set default values
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", False)

        # Create user
        user = self.model(email=email, username=username, **extra_fields)

        if password:
            user.set_password(password)

        user.full_clean()  # Run model validation
        user.save(using=self._db)

        # Profile creation is now handled by signals to avoid circular import

        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email, username and password.
        FIXED: Consistent feature set and proper validation.
        """
        # Set required superuser fields
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault(
            "is_email_verified", True
        )  # Superusers are pre-verified

        # Validate required fields
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if not password:
            raise ValueError(_("Superuser must have a password."))

        return self.create_user(email, username, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Override to use email as natural key."""
        return self.get(email=username)

    def active_users(self):
        """Return queryset of active users."""
        return self.filter(is_active=True)

    def verified_users(self):
        """Return queryset of email-verified users."""
        return self.filter(is_email_verified=True)

    def users_by_role(self, role):
        """Return queryset of users with specific role."""
        return self.filter(role=role, is_active=True)
