"""
File: backend/users/permissions.py
Purpose: Custom permission classes for role-based access control
Date Revised: 2025-07-15 00:00:00 UTC
Version: 2.1.0 - Enhanced Security and Consistency

FIXES APPLIED:
- Added proper error handling and logging
- Enhanced permission validation logic
- Added caching for performance
- Improved docstrings and type hints
- Added audit logging for permission checks
"""

import logging
from typing import Any, Optional

from django.core.cache import cache
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class BaseSecurePermission(permissions.BasePermission):
    """
    Base permission class with enhanced security and logging.
    ADDED: Common functionality for all permission classes.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Base permission check with logging."""
        if not request.user or not request.user.is_authenticated:
            self._log_permission_denied(request, "User not authenticated")
            return False

        return True

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Base object permission check."""
        return self.has_permission(request, view)

    def _log_permission_denied(self, request: Request, reason: str) -> None:
        """Log permission denial for security auditing."""
        user_id = getattr(request.user, "id", "anonymous")
        path = getattr(request, "path", "unknown")
        logger.warning(f"Permission denied: {reason} - User: {user_id}, Path: {path}")

    def _get_cache_key(self, user_id: int, permission_type: str) -> str:
        """Generate cache key for permission checks."""
        return f"permission:{permission_type}:{user_id}"


class IsOwnerOrAdmin(BaseSecurePermission):
    """
    Object-level permission to only allow owners or admins to access objects.
    ENHANCED: Better object attribute detection and caching.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Check if user owns object or is admin."""
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        # Admin bypass with caching
        if self._is_admin_cached(user):
            return True

        # Check ownership through various possible attributes
        owner_attributes = ["user", "owner", "created_by", "author"]

        for attr in owner_attributes:
            if hasattr(obj, attr):
                owner = getattr(obj, attr)
                if owner == user:
                    return True

        # If object is the user itself
        if obj == user:
            return True

        self._log_permission_denied(
            request, f"User {user.id} not owner of object {type(obj).__name__}"
        )
        return False

    def _is_admin_cached(self, user) -> bool:
        """Check admin status with caching."""
        cache_key = self._get_cache_key(user.id, "is_admin")
        is_admin = cache.get(cache_key)

        if is_admin is None:
            is_admin = user.is_admin or user.is_superuser
            cache.set(cache_key, is_admin, timeout=300)  # 5 minutes

        return is_admin


class IsUserOrAdmin(BaseSecurePermission):
    """
    Object-level permission for user-associated objects or admins.
    ENHANCED: Improved user association detection.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Check if user is associated with object or is admin."""
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        # Admin bypass
        if user.is_admin or user.is_superuser:
            return True

        # Check user association
        if hasattr(obj, "user") and obj.user == user:
            return True

        # If object is the user itself
        if obj == user:
            return True

        self._log_permission_denied(
            request, f"User {user.id} not associated with object"
        )
        return False


class IsInstructor(BaseSecurePermission):
    """
    Allow access only to users with instructor role.
    ENHANCED: Added role validation and caching.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is an instructor."""
        if not super().has_permission(request, view):
            return False

        user = request.user
        cache_key = self._get_cache_key(user.id, "is_instructor")
        is_instructor = cache.get(cache_key)

        if is_instructor is None:
            is_instructor = user.is_instructor
            cache.set(cache_key, is_instructor, timeout=300)  # 5 minutes

        if not is_instructor:
            self._log_permission_denied(request, f"User {user.id} not an instructor")

        return is_instructor


class IsStudent(BaseSecurePermission):
    """
    Allow access only to users with student role.
    ENHANCED: Added role validation and caching.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is a student."""
        if not super().has_permission(request, view):
            return False

        user = request.user
        cache_key = self._get_cache_key(user.id, "is_student")
        is_student = cache.get(cache_key)

        if is_student is None:
            is_student = user.is_student
            cache.set(cache_key, is_student, timeout=300)  # 5 minutes

        if not is_student:
            self._log_permission_denied(request, f"User {user.id} not a student")

        return is_student


class IsPlatformAdmin(BaseSecurePermission):
    """
    Allow access only to admin users.
    ENHANCED: Consolidated admin checking logic.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is a platform admin."""
        if not super().has_permission(request, view):
            return False

        user = request.user
        is_admin = user.is_admin or user.is_superuser

        if not is_admin:
            self._log_permission_denied(request, f"User {user.id} not a platform admin")

        return is_admin


class IsStaffMember(BaseSecurePermission):
    """
    Allow access only to staff members.
    ENHANCED: Better staff validation.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is a staff member."""
        if not super().has_permission(request, view):
            return False

        user = request.user
        is_staff = user.is_staff_member

        if not is_staff:
            self._log_permission_denied(request, f"User {user.id} not a staff member")

        return is_staff


class IsActivatedUser(BaseSecurePermission):
    """
    Allow access only to users with verified emails.
    ENHANCED: Added email verification caching.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has verified email."""
        if not super().has_permission(request, view):
            return False

        user = request.user
        cache_key = self._get_cache_key(user.id, "is_email_verified")
        is_verified = cache.get(cache_key)

        if is_verified is None:
            is_verified = user.is_email_verified
            cache.set(cache_key, is_verified, timeout=300)  # 5 minutes

        if not is_verified:
            self._log_permission_denied(request, f"User {user.id} email not verified")

        return is_verified


class IsOwner(BaseSecurePermission):
    """
    Object-level permission to only allow owners to access objects.
    ENHANCED: Simplified ownership checking.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Check if user owns the object."""
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        # Check ownership through various attributes
        owner_attributes = ["user", "owner", "created_by"]

        for attr in owner_attributes:
            if hasattr(obj, attr):
                if getattr(obj, attr) == user:
                    return True

        # If object is the user itself
        if obj == user:
            return True

        self._log_permission_denied(request, f"User {user.id} not owner of object")
        return False


class IsOwnerOrReadOnly(BaseSecurePermission):
    """
    Object-level permission to allow read access to everyone,
    but write access only to owners.
    ADDED: Read-only access pattern.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Allow read access to all, write access only to owners."""
        if not super().has_object_permission(request, view, obj):
            return False

        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owners
        return IsOwner().has_object_permission(request, view, obj)


class IsInstructorOrReadOnly(BaseSecurePermission):
    """
    Allow read access to all authenticated users,
    but write access only to instructors.
    ADDED: Instructor-specific write access.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Allow read access to all, write access only to instructors."""
        if not super().has_permission(request, view):
            return False

        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for instructors
        return IsInstructor().has_permission(request, view)


class SubscriptionRequiredPermission(BaseSecurePermission):
    """
    Permission that requires active subscription.
    ADDED: Subscription-based access control.
    """

    def __init__(self, required_tier: str = "registered"):
        """Initialize with required subscription tier."""
        self.required_tier = required_tier
        super().__init__()

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has required subscription tier."""
        if not super().has_permission(request, view):
            return False

        user = request.user

        try:
            subscription = user.subscription
            if not subscription.is_active:
                self._log_permission_denied(
                    request, f"User {user.id} subscription inactive"
                )
                return False

            # Define tier hierarchy
            tier_hierarchy = {"guest": 0, "registered": 1, "premium": 2}
            user_tier_level = tier_hierarchy.get(subscription.tier, 0)
            required_tier_level = tier_hierarchy.get(self.required_tier, 1)

            if user_tier_level < required_tier_level:
                self._log_permission_denied(
                    request, f"User {user.id} insufficient subscription tier"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Subscription check error for user {user.id}: {str(e)}")
            return False


# Utility functions for permission checking
def check_object_permission(user, obj, permission_type: str = "owner") -> bool:
    """
    Utility function to check object permissions programmatically.
    ADDED: Programmatic permission checking.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_admin or user.is_superuser:
        return True

    if permission_type == "owner":
        owner_attrs = ["user", "owner", "created_by"]
        for attr in owner_attrs:
            if hasattr(obj, attr) and getattr(obj, attr) == user:
                return True
        return obj == user

    return False


def clear_permission_cache(user_id: int) -> None:
    """
    Clear cached permissions for a user.
    ADDED: Cache management utility.
    """
    permission_types = ["is_admin", "is_instructor", "is_student", "is_email_verified"]
    for perm_type in permission_types:
        cache_key = f"permission:{perm_type}:{user_id}"
        cache.delete(cache_key)


# Export all permission classes
__all__ = [
    "BaseSecurePermission",
    "IsOwnerOrAdmin",
    "IsUserOrAdmin",
    "IsInstructor",
    "IsStudent",
    "IsPlatformAdmin",
    "IsStaffMember",
    "IsActivatedUser",
    "IsOwner",
    "IsOwnerOrReadOnly",
    "IsInstructorOrReadOnly",
    "SubscriptionRequiredPermission",
    "check_object_permission",
    "clear_permission_cache",
]
