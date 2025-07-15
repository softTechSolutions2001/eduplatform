#
# File Path: instructor_portal/views/mixins.py
# Folder Path: instructor_portal/views/
# Date Created: 2025-06-27 06:34:12
# Date Revised: 2025-06-27 06:34:12
# Current Date and Time (UTC): 2025-06-27 06:34:12
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:34:12 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Core mixins, decorators, and utility functions for instructor_portal
# Contains all base functionality extracted from original monolithic views.py

import functools
import json
import logging
import re
import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

# FIXED: Import from courses app (external)
from courses.models import (
    Assessment,
    Category,
    Course,
    Lesson,
    Module,
    Question,
    Resource,
)
from courses.serializers import CourseCloneSerializer
from courses.utils import (
    clear_course_caches,
    generate_unique_slug,
    validate_file_security,
)
from courses.validation import (
    sanitize_input,
    validate_course_data,
    validate_lesson_data,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError, IntegrityError, models, transaction
from django.db.models import (
    Avg,
    Case,
    Count,
    F,
    Max,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Value,
    When,
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

# Import instructor portal models with correct TierManager
from ..models import (
    CourseContentDraft,
    CourseCreationSession,
    CourseInstructor,
    CourseTemplate,
    DraftCourseContent,
    InstructorAnalytics,
    InstructorDashboard,
    InstructorProfile,
    TierManager,
)


def _course_permissions():
    # late import to prevent circular dependency
    from courses.permissions import CanManageCourse, IsEnrolled, IsInstructorOrAdmin

    return IsInstructorOrAdmin, CanManageCourse, IsEnrolled


# Set up structured logging
logger = logging.getLogger(__name__)

# Cache timeouts for performance optimization
COURSE_CACHE_TIMEOUT = 300  # 5 minutes
ANALYTICS_CACHE_TIMEOUT = 600  # 10 minutes
PERMISSIONS_CACHE_TIMEOUT = 180  # 3 minutes

# Security constants
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
MAX_BULK_OPERATIONS = 100
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000

# Rate limiting constants - vary by tier
UPLOAD_RATE_LIMIT = "50/hour"
BULK_IMPORT_RATE_LIMIT = "10/hour"
API_RATE_LIMIT = "1000/hour"

# =====================================
# ENHANCED SECURITY FUNCTIONS WITH INSTRUCTOR PROFILE INTEGRATION
# =====================================


def validate_user_permission(user, course, required_permission: str = "manage") -> bool:
    """
    Enhanced user permission validation with InstructorProfile integration
    Includes proper caching and standard permission checking
    """
    try:
        if not user or not user.is_authenticated:
            return False

        # Staff and superuser always have access
        if user.is_staff or user.is_superuser:
            return True

        # ENHANCED: Check InstructorProfile first with cache
        cache_key = f"instructor_profile_status:{user.id}"
        profile_status = cache.get(cache_key)

        if profile_status is None:
            try:
                instructor_profile = user.instructor_profile
                profile_status = instructor_profile.status
                cache.set(cache_key, profile_status, PERMISSIONS_CACHE_TIMEOUT)
            except InstructorProfile.DoesNotExist:
                # User doesn't have instructor profile
                logger.warning(
                    f"User {user.id} attempted instructor action without profile"
                )
                cache.set(cache_key, "none", PERMISSIONS_CACHE_TIMEOUT)
                return False

        if profile_status != InstructorProfile.Status.ACTIVE:
            logger.warning(
                f"Instructor {user.id} has inactive profile status: {profile_status}"
            )
            return False

        # Check course-specific instructor permissions using CourseInstructor model
        if course:
            cache_key = (
                f"instructor_permission:{user.id}:{course.id}:{required_permission}"
            )
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Map permission strings to model fields
            permission_field = {
                "manage": "is_active",
                "edit": "can_edit_content",
                "students": "can_manage_students",
                "analytics": "can_view_analytics",
            }.get(required_permission, "is_active")

            # Build query with specific permission
            query = Q(course=course, instructor=user, is_active=True)
            if permission_field != "is_active":
                query &= Q(**{permission_field: True})

            # Query the permission
            has_permission = CourseInstructor.objects.filter(query).exists()

            # Cache the result
            cache.set(cache_key, has_permission, PERMISSIONS_CACHE_TIMEOUT)
            return has_permission

        # General instructor check using CourseInstructor
        return CourseInstructor.objects.filter(instructor=user, is_active=True).exists()

    except Exception as e:
        logger.error(f"Error validating user permission: {e}", exc_info=True)
        return False


def get_instructor_profile(user) -> Optional[InstructorProfile]:
    """
    Get instructor profile with caching and error handling
    """
    if not user or not user.is_authenticated:
        return None

    cache_key = f"instructor_profile:{user.id}"
    profile = cache.get(cache_key)

    if profile is None:
        try:
            profile = user.instructor_profile
            cache.set(cache_key, profile, PERMISSIONS_CACHE_TIMEOUT)
        except InstructorProfile.DoesNotExist:
            cache.set(cache_key, None, PERMISSIONS_CACHE_TIMEOUT)
            return None
        except Exception as e:
            logger.error(f"Error getting instructor profile: {e}")
            return None

    return profile


def scrub_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from data for logging with enhanced pattern matching"""
    if not isinstance(data, dict):
        return {}

    sensitive_fields = {
        "password",
        "token",
        "key",
        "secret",
        "email",
        "ssn",
        "phone",
        "credit_card",
        "authorization",
        "cookie",
        "x-api-key",
        "api_key",
        "access_token",
        "refresh_token",
        "auth",
        "credentials",
        "private",
        "secret_key",
        "account_number",
        "social_security",
        "passport",
        "license",
        "address",
        "username",
    }

    # Enhanced pattern matching for sensitive data
    email_pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    credit_card_pattern = re.compile(r"^(\d{4}[- ]){3}\d{4}$")

    scrubbed = {}
    for key, value in data.items():
        key_lower = key.lower()

        # Check if key contains sensitive field names
        if any(sensitive in key_lower for sensitive in sensitive_fields):
            scrubbed[key] = "<redacted>"

        # Check for email pattern
        elif isinstance(value, str) and email_pattern.match(value):
            scrubbed[key] = "<redacted:email>"

        # Check for credit card pattern
        elif isinstance(value, str) and credit_card_pattern.match(value):
            scrubbed[key] = "<redacted:credit-card>"

        # Check for potential auth token pattern (long alphanumeric string)
        elif (
            isinstance(value, str)
            and len(value) > 20
            and re.match(r"^[A-Za-z0-9\-_\.]+$", value)
        ):
            scrubbed[key] = "<redacted:potential-token>"

        # Recursively handle nested dictionaries
        elif isinstance(value, dict):
            scrubbed[key] = scrub_sensitive_data(value)

        # Handle lists with potential sensitive data
        elif isinstance(value, list):
            scrubbed[key] = [
                scrub_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            scrubbed[key] = value

    return scrubbed


def audit_log(
    user,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    metadata: Optional[Dict] = None,
    success: bool = True,
    request=None,
):
    """Comprehensive audit logging for security monitoring with enhanced metadata"""
    try:
        # Get user IP if request is available
        ip_address = None
        if request and hasattr(request, "META"):
            ip_address = request.META.get("REMOTE_ADDR", None)
            # Check for X-Forwarded-For header
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if forwarded_for:
                ip_address = forwarded_for.split(",")[0].strip()

        # Get user agent if request is available
        user_agent = None
        if request and hasattr(request, "META"):
            user_agent = request.META.get("HTTP_USER_AGENT")

        # Build log entry
        log_entry = {
            "timestamp": timezone.now().isoformat(),
            "user_id": user.id if user and user.is_authenticated else None,
            "username": (
                user.username if user and user.is_authenticated else "anonymous"
            ),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": scrub_sensitive_data(metadata or {}),
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # Add instructor profile info if available
        if user and user.is_authenticated and hasattr(user, "instructor_profile"):
            log_entry["instructor_tier"] = user.instructor_profile.tier
            log_entry["instructor_status"] = user.instructor_profile.status

        logger.info(f"AUDIT: {json.dumps(log_entry)}")

    except Exception as e:
        logger.error(f"Failed to create audit log: {e}", exc_info=True)


def check_premium_access(user) -> bool:
    """Enhanced premium access checking with InstructorProfile integration and caching"""
    try:
        if not user or not user.is_authenticated:
            return False

        # Check cache first
        cache_key = f"premium_access:{user.id}"
        has_premium = cache.get(cache_key)
        if has_premium is not None:
            return has_premium

        # Staff and admin always have premium access
        if user.is_staff or user.is_superuser:
            cache.set(cache_key, True, PERMISSIONS_CACHE_TIMEOUT)
            return True

        # ENHANCED: Check instructor profile tier
        instructor_profile = get_instructor_profile(user)
        if instructor_profile:
            # Gold, Platinum, Diamond tiers get premium access
            premium_access = instructor_profile.tier in [
                InstructorProfile.Tier.GOLD,
                InstructorProfile.Tier.PLATINUM,
                InstructorProfile.Tier.DIAMOND,
            ]

            if premium_access:
                cache.set(cache_key, True, PERMISSIONS_CACHE_TIMEOUT)
                return True

        # Check subscription (if available)
        try:
            from subscriptions.models import Subscription

            subscription = getattr(user, "subscription", None)
            if subscription and isinstance(subscription, Subscription):
                has_premium = (
                    subscription.tier == "premium" and subscription.is_active()
                )
                cache.set(cache_key, has_premium, PERMISSIONS_CACHE_TIMEOUT)
                return has_premium
        except ImportError:
            logger.debug("Subscription model not available")

        # Default: no premium access
        cache.set(cache_key, False, PERMISSIONS_CACHE_TIMEOUT)
        return False

    except Exception as e:
        logger.error(f"Error checking premium access for user {user.id}: {e}")
        return False


def validate_file_upload(
    file_obj, user, allowed_types=None, verify_content=True
) -> Dict[str, Any]:
    """
    Enhanced file validation with comprehensive security checks
    Returns dict with validation results
    """
    if not file_obj:
        return {"is_valid": False, "reason": "No file provided", "details": {}}

    try:
        # Get instructor profile for tier-based limits
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return {
                "is_valid": False,
                "reason": "User does not have instructor profile",
                "details": {},
            }

        # Get tier limits
        tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
        max_file_size = tier_limits.get(
            "max_file_size", 10 * 1024 * 1024
        )  # Default 10MB

        # Check file size
        if file_obj.size > max_file_size:
            max_size_mb = max_file_size / (1024 * 1024)
            return {
                "is_valid": False,
                "reason": f"File too large (max {max_size_mb:.1f}MB for your tier)",
                "details": {
                    "file_size": file_obj.size,
                    "max_size": max_file_size,
                    "tier": instructor_profile.tier,
                },
            }

        # Check file extension and type
        file_name = file_obj.name.lower()
        file_ext = file_name.split(".")[-1] if "." in file_name else ""

        # Use tier-based allowed file types
        if not allowed_types:
            allowed_types = tier_limits.get("file_types_allowed", ["pdf", "jpg", "png"])

        # Diamond tier allows any file type when allowed_types is *
        if (
            allowed_types == "*"
            and instructor_profile.tier == InstructorProfile.Tier.DIAMOND
        ):
            # Still check for dangerous file types
            dangerous_extensions = [
                "exe",
                "bat",
                "cmd",
                "com",
                "sh",
                "php",
                "pl",
                "py",
                "js",
            ]
            if file_ext in dangerous_extensions:
                return {
                    "is_valid": False,
                    "reason": f"File type {file_ext} not allowed",
                    "details": {},
                }
        elif file_ext not in allowed_types and allowed_types != "*":
            return {
                "is_valid": False,
                "reason": f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_types)}",
                "details": {"extension": file_ext, "allowed": allowed_types},
            }

        # Verify content type (optional but recommended)
        if verify_content:
            try:
                import magic

                # Read first 2KB of file to determine type
                file_header = file_obj.read(2048)
                file_content_type = magic.from_buffer(file_header, mime=True)
                file_obj.seek(0)  # Reset file pointer

                # Map of safe content types by extension
                safe_types = {
                    "pdf": ["application/pdf"],
                    "jpg": ["image/jpeg"],
                    "jpeg": ["image/jpeg"],
                    "png": ["image/png"],
                    "gif": ["image/gif"],
                    "doc": ["application/msword"],
                    "docx": [
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ],
                    "xls": ["application/vnd.ms-excel"],
                    "xlsx": [
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ],
                    "ppt": ["application/vnd.ms-powerpoint"],
                    "pptx": [
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    ],
                    "mp4": ["video/mp4"],
                    "mp3": ["audio/mpeg"],
                    "txt": ["text/plain"],
                    "zip": ["application/zip", "application/x-zip-compressed"],
                }

                if (
                    file_ext in safe_types
                    and file_content_type not in safe_types[file_ext]
                ):
                    return {
                        "is_valid": False,
                        "reason": f"File content doesn't match extension. Found: {file_content_type}",
                        "details": {
                            "claimed_type": file_ext,
                            "actual_type": file_content_type,
                        },
                    }

            except Exception as e:
                logger.warning(f"Error checking file content type: {e}", exc_info=True)
                # Continue without content verification if it fails

        # All checks passed
        return {
            "is_valid": True,
            "reason": "File passed all validation checks",
            "details": {
                "file_name": file_name,
                "file_size": file_obj.size,
                "extension": file_ext,
                "content_type": getattr(file_obj, "content_type", None),
                "tier": instructor_profile.tier,
            },
        }

    except Exception as e:
        logger.error(f"Error validating file: {e}", exc_info=True)
        return {
            "is_valid": False,
            "reason": f"File validation error: {str(e)}",
            "details": {},
        }


# =====================================
# ENHANCED DECORATORS
# =====================================


def require_instructor_profile(func):
    """
    Decorator to ensure user has active instructor profile
    ENHANCED: Better error handling and audit logging
    """

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        instructor_profile = get_instructor_profile(request.user)

        if not instructor_profile:
            audit_log(
                request.user,
                "missing_instructor_profile",
                "access_denied",
                metadata={"view": func.__name__},
                success=False,
                request=request,
            )
            return Response(
                {"detail": "Instructor profile required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if instructor_profile.status != InstructorProfile.Status.ACTIVE:
            audit_log(
                request.user,
                f"inactive_instructor_profile_{instructor_profile.status}",
                "access_denied",
                metadata={"view": func.__name__, "status": instructor_profile.status},
                success=False,
                request=request,
            )
            return Response(
                {
                    "detail": f"Instructor profile is {instructor_profile.get_status_display()}"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Add instructor profile to request for easy access
        request.instructor_profile = instructor_profile

        # Ensure instructor profile is tracked even if the request fails
        audit_log(
            request.user,
            "instructor_request",
            "access_granted",
            metadata={
                "view": func.__name__,
                "tier": instructor_profile.tier,
                "instructor_id": instructor_profile.id,
            },
            request=request,
        )

        return func(self, request, *args, **kwargs)

    return wrapper


def require_permission(permission_type: str = "manage"):
    """
    Enhanced permission checking with instructor profile integration
    and standardized error handling
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # Get the object if this is an object-level action
                obj = None
                if hasattr(self, "get_object"):
                    try:
                        obj = self.get_object()
                    except Exception:
                        pass

                # Special handling for course objects
                course_obj = None
                if hasattr(obj, "course"):
                    course_obj = obj.course
                elif hasattr(obj, "module") and hasattr(obj.module, "course"):
                    course_obj = obj.module.course
                elif (
                    hasattr(obj, "lesson")
                    and hasattr(obj.lesson, "module")
                    and hasattr(obj.lesson.module, "course")
                ):
                    course_obj = obj.lesson.module.course
                elif isinstance(obj, Course):
                    course_obj = obj

                # Check permission against the course object
                target_obj = course_obj or obj

                # Validate permission
                if not validate_user_permission(
                    request.user, target_obj, permission_type
                ):
                    audit_log(
                        request.user,
                        f"permission_denied_{permission_type}",
                        (
                            getattr(
                                self, "resource_name", obj.__class__.__name__.lower()
                            )
                            if obj
                            else "unknown"
                        ),
                        getattr(obj, "id", None),
                        {"action": func.__name__, "permission_type": permission_type},
                        success=False,
                        request=request,
                    )

                    return Response(
                        {
                            "detail": f"You do not have {permission_type} permission for this resource"
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                return func(self, request, *args, **kwargs)

            except DRFPermissionDenied as e:
                # Pass through DRF permission errors
                raise
            except Exception as e:
                logger.error(f"Error in permission decorator: {e}", exc_info=True)
                return Response(
                    {"detail": "Permission check failed due to an error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return wrapper

    return decorator


def tier_required(min_tier: str):
    """
    Decorator to require minimum instructor tier
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            instructor_profile = getattr(request, "instructor_profile", None)
            if not instructor_profile:
                instructor_profile = get_instructor_profile(request.user)
                if not instructor_profile:
                    return Response(
                        {"detail": "Instructor profile required"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Map tier names to hierarchy values
            tier_hierarchy = {
                "bronze": 1,
                "silver": 2,
                "gold": 3,
                "platinum": 4,
                "diamond": 5,
            }

            # Get current tier level
            current_tier = instructor_profile.tier.lower()
            current_level = tier_hierarchy.get(current_tier, 1)

            # Get required tier level
            required_level = tier_hierarchy.get(
                min_tier.lower(), 5
            )  # Default to highest if unknown

            if current_level < required_level:
                audit_log(
                    request.user,
                    "tier_access_denied",
                    "feature_access",
                    metadata={
                        "current_tier": current_tier,
                        "required_tier": min_tier,
                        "view": func.__name__,
                    },
                    success=False,
                    request=request,
                )

                return Response(
                    {
                        "detail": f"This feature requires {min_tier.title()} tier or higher",
                        "current_tier": current_tier.title(),
                        "required_tier": min_tier.title(),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator


# =====================================
# BASE VIEWSET FOR STANDARDIZATION
# =====================================


class InstructorBaseViewSet(viewsets.ModelViewSet):
    """
    Base viewset with standardized permission and error handling
    """

    resource_name = "resource"  # Override in child classes
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def initial(self, request, *args, **kwargs):
        """Verify instructor profile exists before processing any request"""
        super().initial(request, *args, **kwargs)

        # Store instructor profile on request
        instructor_profile = get_instructor_profile(request.user)
        if (
            instructor_profile
            and instructor_profile.status == InstructorProfile.Status.ACTIVE
        ):
            request.instructor_profile = instructor_profile

    def get_error_response(self, message, status_code=400, errors=None):
        """Standardized error response format"""
        response_data = {"detail": message}
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status_code)

    def handle_exception(self, exc):
        """Standardized exception handling"""
        if isinstance(exc, DjangoValidationError):
            return self.get_error_response(
                "Validation error",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=(
                    exc.message_dict
                    if hasattr(exc, "message_dict")
                    else {"non_field_errors": exc.messages}
                ),
            )

        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error: {exc}")
            return self.get_error_response(
                "Database constraint violation", status_code=status.HTTP_400_BAD_REQUEST
            )

        elif isinstance(exc, PermissionDenied) or isinstance(exc, DRFPermissionDenied):
            return self.get_error_response(
                str(exc), status_code=status.HTTP_403_FORBIDDEN
            )

        # Let DRF handle other exceptions
        return super().handle_exception(exc)
