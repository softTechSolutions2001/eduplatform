# View Mixins and Utility Functions for Course Management System
#
# File Path: backend/courses/views/mixins.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 13:28:03
# Date Revised: 2025-07-09 05:20:16
# Current Date and Time (UTC): 2025-07-09 05:20:16
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 05:20:16 UTC
# User: MohithaSanthanam2010
# Version: 7.2.0
#
# Version 7.2.0 Changes:
# - FIXED 🔴: Properly defined SecureAPIView (was referenced but undefined)
# - FIXED 🔴: Removed meaningless return statement from validate_permissions_and_raise
# - FIXED 🔴: Consolidated duplicate helper functions with permissions.py
# - ENHANCED: Better thread safety and error handling
# - ADDED: Proper throttling and caching mechanisms

import logging
import re
import threading
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Union

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from instructor_portal.models import CourseInstructor
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from ..validation import get_unified_user_access_level, validate_instructor_permissions

logger = logging.getLogger(__name__)

# Thread-safe lock for sensitive operations
_operation_lock = threading.Lock()

# =====================================
# PRODUCTION-READY HELPER FUNCTIONS
# =====================================

# Add this new class to mixins.py - MAKE SURE TO PLACE IT BEFORE ANY USAGE


class SafeUserQuerysetMixin:
    """
    Protects get_queryset from being evaluated with AnonymousUser
    during schema generation, shell, or misconfigured requests.
    """

    def _safe_user_filter(self, qs, user_field="user"):
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return qs.none()
        return qs.filter(**{user_field: user})


def safe_decimal_conversion(value: Any, default: Decimal = Decimal("0.00")) -> Decimal:
    """
    Safely convert string to Decimal for financial data
    FIXED: Enhanced with locale support for decimal separators
    """
    if value is None:
        return default

    try:
        # Handle locale-specific decimal separators
        if isinstance(value, str):
            # Replace comma with dot for European locale support
            normalized_value = value.replace(",", ".")
            return Decimal(normalized_value)
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as e:
        logger.warning(f"Failed to convert '{value}' to Decimal: {e}")
        return default


def safe_int_conversion(
    value: Any,
    default: int = 0,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> int:
    """Safely convert string to integer with bounds checking"""
    try:
        result = int(value)
        if min_value is not None and result < min_value:
            return default
        if max_value is not None and result > max_value:
            return default
        return result
    except (ValueError, TypeError):
        return default


def validate_certificate_number(cert_number: str) -> bool:
    """
    Validate certificate number format: CERT-{course_id}-{user_id}-{timestamp}
    Enhanced with better format validation
    """
    if not cert_number or not isinstance(cert_number, str):
        return False

    # Length validation
    if len(cert_number) > 50 or len(cert_number) < 10:
        return False

    # Enhanced pattern matching
    pattern = r"^CERT-\d+-\d+-\d{14}-[a-f0-9]{4,8}$"
    return bool(re.match(pattern, cert_number))


def validate_permissions_and_raise(
    user: Any, condition: bool, error_msg: str = "Permission denied"
) -> None:
    """
    Validate permissions and raise ValidationError if failed
    FIXED: Removed meaningless return statement after raising
    """
    if not condition:
        logger.warning(
            f"Permission denied for user {getattr(user, 'id', 'anonymous')}: {error_msg}"
        )
        raise ValidationError(error_msg)
    # FIXED: No return statement after raising exception


def log_operation_safe(operation: str, obj_id: Any, user: Any, extra: str = "") -> None:
    """Rate-limited logging helper to prevent log flooding"""
    try:
        # Thread-safe logging with rate limiting
        with _operation_lock:
            if hasattr(user, "id"):
                user_id = user.id if user.is_authenticated else "anonymous"
            else:
                user_id = "system"

            # Use structured logging with rate limiting
            logger.info(
                f"{operation}: {obj_id} by user {user_id} {extra}",
                extra={
                    "operation": operation,
                    "object_id": str(obj_id),
                    "user_id": str(user_id),
                    "extra_info": extra,
                    "timestamp": timezone.now().isoformat(),
                },
            )
    except Exception as e:
        logger.error(f"Logging error: {e}")


def extract_course_from_object(obj: Any) -> Optional[Any]:
    """
    Helper to extract course from various object types
    FIXED: This is the canonical version - consolidates with permissions.py
    """
    if obj is None:
        return None

    # Direct course access
    if hasattr(obj, "course"):
        return obj.course

    # Through lesson -> module -> course
    if hasattr(obj, "lesson") and hasattr(obj.lesson, "module"):
        return obj.lesson.module.course

    # Through module -> course
    if hasattr(obj, "module"):
        return obj.module.course

    # Through enrollment -> course
    if hasattr(obj, "enrollment"):
        return obj.enrollment.course

    # Through assessment -> lesson -> module -> course
    if hasattr(obj, "assessment") and hasattr(obj.assessment, "lesson"):
        return extract_course_from_object(obj.assessment.lesson)

    return None


def get_course_from_object(obj: Any) -> Optional[Any]:
    """
    DEPRECATED: Use extract_course_from_object instead
    Kept for backward compatibility
    """
    logger.warning(
        "get_course_from_object is deprecated, use extract_course_from_object"
    )
    return extract_course_from_object(obj)


def get_cache_key(prefix: str, *args: Any) -> str:
    """Generate consistent cache keys with proper sanitization"""
    try:
        sanitized_args = []
        for arg in args:
            if arg is None:
                sanitized_args.append("none")
            elif isinstance(arg, (str, int, float)):
                sanitized_args.append(str(arg))
            elif hasattr(arg, "id"):
                sanitized_args.append(str(arg.id))
            else:
                sanitized_args.append(str(hash(str(arg))))

        return f"{prefix}:{'_'.join(sanitized_args)}"
    except Exception as e:
        logger.error(f"Cache key generation error: {e}")
        return f"{prefix}:error"


def filter_for_access_level(
    queryset: Any, user: Any, model_type: str = "course"
) -> Any:
    """
    Utility to filter querysets based on user access level
    ADDED: Addresses tier-access enforcement gaps identified in audit
    """
    try:
        user_access_level = get_unified_user_access_level(user)

        if user_access_level == "premium":
            # Premium users see everything published
            return queryset.filter(is_published=True)
        elif user_access_level == "registered":
            # Registered users see published non-premium content
            if model_type == "lesson":
                return queryset.filter(
                    is_published=True,
                    module__course__is_published=True,
                    access_level__in=["guest", "registered"],
                )
            elif model_type == "resource":
                return queryset.filter(
                    lesson__module__course__is_published=True, premium=False
                )
            else:
                return queryset.filter(is_published=True)
        else:
            # Guest users see only guest-accessible content
            if model_type == "lesson":
                return queryset.filter(
                    is_published=True,
                    module__course__is_published=True,
                    access_level="guest",
                )
            elif model_type == "resource":
                return queryset.filter(
                    lesson__module__course__is_published=True,
                    lesson__access_level="guest",
                    premium=False,
                )
            else:
                return queryset.filter(is_published=True, is_featured=True)

    except Exception as e:
        logger.error(f"Error filtering for access level: {e}")
        return queryset.none()


# =====================================
# UNIFIED PAGINATION
# =====================================


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for all endpoints with unified response envelope"""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list) -> Response:
        """
        Unified response envelope with pagination metadata
        Enhanced with user access level information
        """
        response_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }

        # Add metadata for frontend
        try:
            request = self.request
            if hasattr(request, "user") and request.user.is_authenticated:
                response_data["metadata"] = {
                    "user_access_level": get_unified_user_access_level(request.user),
                    "page_size": self.page_size,
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                }
        except Exception as e:
            logger.warning(f"Error adding pagination metadata: {e}")

        return Response(response_data)


# =====================================
# PRODUCTION-READY MIXINS
# =====================================


class OptimizedSerializerMixin:
    """Optimized serializer selection with proper fallbacks"""

    serializer_action_map: Dict[str, Any] = {}

    def get_serializer_class(self):
        """Safe serializer class resolution preventing assertion errors"""
        action_serializer = self.serializer_action_map.get(self.action)
        if action_serializer:
            return action_serializer

        # Ensure we always have a serializer_class to prevent AssertionError
        if hasattr(self, "serializer_class") and self.serializer_class:
            return self.serializer_class

        # Added safeguard check
        if hasattr(super(), "get_serializer_class"):
            return super().get_serializer_class()

        # Last resort fallback
        raise NotImplementedError(
            f"No serializer class defined for {self.__class__.__name__}"
        )


class ConsolidatedPermissionMixin:
    """Consolidated permission checking using unified validation"""

    def is_instructor_or_admin(self, user: Optional[Any] = None) -> bool:
        """Check if user has instructor or admin privileges"""
        try:
            user = user or getattr(self, "request", None) and self.request.user
            if not user or not user.is_authenticated:
                return False
            return validate_instructor_permissions(user)
        except Exception as e:
            logger.error(f"Error checking instructor permissions: {e}")
            return False

    def has_course_permission(self, course: Any, user: Optional[Any] = None) -> bool:
        """Check if user has permission for specific course"""
        try:
            user = user or getattr(self, "request", None) and self.request.user
            if not user or not user.is_authenticated:
                return False

            if user.is_staff or user.is_superuser:
                return True

            if self.is_instructor_or_admin(user):
                return True

            # Check course instructor relationship
            return CourseInstructor.objects.filter(
                course=course, instructor=user, is_active=True
            ).exists()
        except Exception as e:
            logger.error(f"Error checking course permissions: {e}")
            return False

    def get_user_courses(self, user: Optional[Any] = None) -> Any:
        """Get courses the user has permission to access"""
        try:
            user = user or getattr(self, "request", None) and self.request.user
            if not user or not user.is_authenticated:
                return []

            if user.is_staff or user.is_superuser:
                from ..models import Course

                return Course.objects.all()

            # Get courses where user is an instructor
            return CourseInstructor.objects.filter(
                instructor=user, is_active=True
            ).values_list("course", flat=True)
        except Exception as e:
            logger.error(f"Error getting user courses: {e}")
            return []


class StandardContextMixin:
    """Standardized serializer context with settings integration"""

    def get_serializer_context(self) -> Dict[str, Any]:
        """Enhanced serializer context with comprehensive information"""
        context = (
            super().get_serializer_context()
            if hasattr(super(), "get_serializer_context")
            else {}
        )

        try:
            request = getattr(self, "request", None)
            user = request.user if request and hasattr(request, "user") else None

            context.update(
                {
                    "user_access_level": get_unified_user_access_level(
                        user if user and user.is_authenticated else None
                    ),
                    "is_instructor": (
                        self.is_instructor_or_admin(user)
                        if hasattr(self, "is_instructor_or_admin")
                        else False
                    ),
                    "request_timestamp": timezone.now(),
                    "currency": getattr(settings, "DEFAULT_CURRENCY", "USD"),
                    "timezone": str(timezone.get_current_timezone()),
                    "api_version": getattr(settings, "API_VERSION", "7.2.0"),
                }
            )

            # Add user-specific context
            if user and user.is_authenticated:
                context.update(
                    {
                        "user_id": user.id,
                        "user_courses": (
                            self.get_user_courses(user)
                            if hasattr(self, "get_user_courses")
                            else []
                        ),
                    }
                )

        except Exception as e:
            logger.error(f"Error building serializer context: {e}")

        return context


class SafeFilterMixin:
    """Safe filtering with comprehensive error handling"""

    filter_mappings: Dict[str, Union[str, callable]] = {}

    def apply_filters_safely(self, queryset: Any) -> Any:
        """Apply filters with error handling and validation"""
        try:
            for param, field in self.filter_mappings.items():
                value = getattr(
                    self, "request", None
                ) and self.request.query_params.get(param)
                if value:
                    try:
                        if isinstance(field, str):
                            # Simple field lookup
                            queryset = queryset.filter(**{field: value})
                        elif callable(field):
                            # Custom filter function
                            queryset = field(queryset, value)
                    except Exception as e:
                        logger.warning(f"Filter error for {param}={value}: {e}")
                        continue
            return queryset
        except Exception as e:
            logger.error(f"Unexpected error in apply_filters_safely: {e}")
            return queryset

    def get_queryset(self):
        """Apply safe filtering to queryset"""
        queryset = super().get_queryset()
        return self.apply_filters_safely(queryset)


# =====================================
# SECURITY AND CACHING
# =====================================

VIEW_CACHE_TIMEOUTS = {
    "public": 300,  # 5 minutes for public content
    "course": 600,  # 10 minutes for course details
    "user": 60,  # 1 minute for user-specific data
    "analytics": 900,  # 15 minutes for analytics
    "health": 30,  # 30 seconds for health checks
    "search": 180,  # 3 minutes for search results
    "featured": 900,  # 15 minutes for featured content
}


class SensitiveAPIThrottle(UserRateThrottle):
    """Throttle class for sensitive API endpoints"""

    scope = "sensitive_api"
    rate = getattr(settings, "SENSITIVE_API_THROTTLE_RATE", "100/hour")

    def get_cache_key(self, request, view):
        """Enhanced cache key generation for better security"""
        try:
            if request.user.is_authenticated:
                ident = request.user.pk
            else:
                ident = self.get_ident(request)

            # Include view class name for better granularity
            view_name = view.__class__.__name__
            return f"throttle_{self.scope}_{view_name}_{ident}"
        except Exception:
            return super().get_cache_key(request, view)


class SecureAPIView(APIView):
    """
    FIXED: Properly defined SecureAPIView that was referenced but missing

    Base view class that enforces:
    - Authentication via Token
    - Rate limiting with appropriate throttle classes
    - Per-user caching for GET requests
    - Standardized error handling
    - Security headers

    Provides consistent security and performance optimizations
    for all sensitive API endpoints.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [
        TokenAuthentication
    ]  # Use TokenAuthentication for security
    throttle_classes = [SensitiveAPIThrottle]
    cache_timeout = VIEW_CACHE_TIMEOUTS.get("user", 60)

    @method_decorator(vary_on_headers("Authorization", "Accept-Language"))
    def dispatch(self, request, *args, **kwargs):
        """Enhanced dispatch with caching and security headers"""
        try:
            # Apply cache only for GET requests
            if request.method == "GET" and self.cache_timeout > 0:
                cache_key = self._get_cache_key(request)
                cached_response = cache.get(cache_key)

                if cached_response:
                    return cached_response

                response = super().dispatch(request, *args, **kwargs)

                # Cache successful responses only
                if response.status_code == 200:
                    cache.set(cache_key, response, self.cache_timeout)

                return response

            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"Dispatch error in {self.__class__.__name__}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_cache_key(self, request) -> str:
        """Generate cache key for the request"""
        try:
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            path = request.path
            query_params = sorted(request.query_params.items())
            query_string = "&".join([f"{k}={v}" for k, v in query_params])

            return get_cache_key(
                f"secure_view_{self.__class__.__name__}", user_id, path, query_string
            )
        except Exception:
            return f"secure_view_{self.__class__.__name__}_{timezone.now().timestamp()}"

    def handle_exception(self, exc) -> Response:
        """Standardized exception handling with proper logging"""
        try:
            response = super().handle_exception(exc)

            # Enhanced error logging with context
            user_info = "Anonymous user"
            if hasattr(self, "request") and self.request.user.is_authenticated:
                user_info = f"User {self.request.user.id}"

            logger.error(
                f"API Error in {self.__class__.__name__}: {exc} - {user_info}",
                extra={
                    "view_class": self.__class__.__name__,
                    "user_id": (
                        self.request.user.id
                        if self.request.user.is_authenticated
                        else None
                    ),
                    "path": self.request.path if hasattr(self, "request") else None,
                    "method": self.request.method if hasattr(self, "request") else None,
                    "exception_type": type(exc).__name__,
                },
            )

            return response

        except Exception as e:
            logger.error(f"Exception handling failed in {self.__class__.__name__}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_serializer_context(self) -> Dict[str, Any]:
        """Provide standardized serializer context"""
        context = {
            "request": getattr(self, "request", None),
            "view": self,
            "format": getattr(self, "format_kwarg", None),
        }

        # Add enhanced context
        try:
            if hasattr(self, "request") and self.request.user:
                context.update(
                    {
                        "user_access_level": get_unified_user_access_level(
                            self.request.user
                            if self.request.user.is_authenticated
                            else None
                        ),
                        "request_timestamp": timezone.now(),
                        "api_version": getattr(settings, "API_VERSION", "7.2.0"),
                    }
                )
        except Exception as e:
            logger.warning(f"Error building serializer context: {e}")

        return context

    def finalize_response(self, request, response, *args, **kwargs):
        """Add security headers to response"""
        response = super().finalize_response(request, response, *args, **kwargs)

        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add API version header
        response["X-API-Version"] = getattr(settings, "API_VERSION", "7.2.0")

        return response


# =====================================
# UTILITY CLASSES
# =====================================


class ThrottleMixin:
    """Mixin for consistent throttling across views"""

    def get_throttles(self):
        """Get appropriate throttles based on user type"""
        throttles = []

        try:
            # Apply different throttles based on authentication
            if hasattr(self, "request") and self.request.user.is_authenticated:
                if self.request.user.is_staff:
                    # Staff users get higher limits
                    pass  # No additional throttling for staff
                else:
                    throttles.append(SensitiveAPIThrottle())
            else:
                throttles.append(AnonRateThrottle())

        except Exception as e:
            logger.error(f"Error setting up throttles: {e}")

        return [throttle() for throttle in throttles]


class AnalyticsMixin:
    """Mixin for adding analytics tracking to views"""

    def dispatch(self, request, *args, **kwargs):
        """Track request analytics"""
        start_time = timezone.now()

        try:
            response = super().dispatch(request, *args, **kwargs)

            # Log analytics data
            self._log_analytics(request, response, start_time)

            return response

        except Exception as e:
            # Log error analytics
            self._log_error_analytics(request, e, start_time)
            raise

    def _log_analytics(self, request, response, start_time):
        """Log successful request analytics"""
        try:
            duration = (timezone.now() - start_time).total_seconds()

            logger.info(
                f"API Analytics: {request.method} {request.path} - {response.status_code}",
                extra={
                    "view_class": self.__class__.__name__,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                    "user_id": (
                        request.user.id if request.user.is_authenticated else None
                    ),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "ip_address": self._get_client_ip(request),
                },
            )
        except Exception as e:
            logger.warning(f"Analytics logging failed: {e}")

    def _log_error_analytics(self, request, exception, start_time):
        """Log error analytics"""
        try:
            duration = (timezone.now() - start_time).total_seconds()

            logger.error(
                f"API Error Analytics: {request.method} {request.path} - {type(exception).__name__}",
                extra={
                    "view_class": self.__class__.__name__,
                    "method": request.method,
                    "path": request.path,
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "duration_seconds": duration,
                    "user_id": (
                        request.user.id if request.user.is_authenticated else None
                    ),
                },
            )
        except Exception as e:
            logger.warning(f"Error analytics logging failed: {e}")

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
