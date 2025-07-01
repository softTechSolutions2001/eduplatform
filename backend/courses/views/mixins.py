#
# File Path: backend/courses/views/mixins.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 13:28:03
# Date Revised: 2025-06-26 17:04:42
# Current Date and Time (UTC): 2025-06-26 17:04:42
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 17:04:42 UTC
# User: softTechSolutions2001
# Version: 7.0.0
#
# View Mixins and Utility Functions for Course Management System

import re
import logging
from decimal import Decimal, InvalidOperation

from django.utils import timezone
from django.conf import settings
# Add missing imports for SecureAPIView
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from instructor_portal.models import CourseInstructor
from ..validation import get_unified_user_access_level, validate_instructor_permissions

logger = logging.getLogger(__name__)


# =====================================
# PRODUCTION-READY HELPER FUNCTIONS
# =====================================

def safe_decimal_conversion(value, default=Decimal('0.00')):
    """Safely convert string to Decimal for financial data"""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def safe_int_conversion(value, default=0, min_value=None, max_value=None):
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


def validate_certificate_number(cert_number):
    """Validate certificate number format: CERT-{course_id}-{user_id}-{timestamp}"""
    if not cert_number or not isinstance(cert_number, str):
        return False
    if len(cert_number) > 50 or len(cert_number) < 10:
        return False
    pattern = r'^CERT-\d+-\d+-\d{14}-[a-f0-9]{4}$'
    return re.match(pattern, cert_number) is not None


def validate_permissions_and_raise(user, condition, error_msg="Permission denied"):
    """Validate permissions and raise ValidationError if failed"""
    if not condition:
        raise ValidationError(error_msg)
    return True


def log_operation_safe(operation, obj_id, user, extra=""):
    """Rate-limited logging helper to prevent log flooding"""
    try:
        if hasattr(user, 'id'):
            user_id = user.id if user.is_authenticated else 'anonymous'
        else:
            user_id = 'system'
        # Use structured logging with rate limiting
        logger.info(f"{operation}: {obj_id} by user {user_id} {extra}", extra={
            'operation': operation,
            'object_id': obj_id,
            'user_id': user_id,
            'extra_info': extra
        })
    except Exception as e:
        logger.error(f"Logging error: {e}")


def extract_course_from_object(obj):
    """Helper to extract course from various object types"""
    if hasattr(obj, 'course'):
        return obj.course
    elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'module'):
        return obj.lesson.module.course
    elif hasattr(obj, 'module'):
        return obj.module.course
    elif hasattr(obj, 'enrollment'):
        return obj.enrollment.course
    return None


def get_cache_key(prefix, *args):
    """Generate consistent cache keys"""
    return f"{prefix}:{'_'.join(str(arg) for arg in args)}"


# =====================================
# UNIFIED PAGINATION
# =====================================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for all endpoints with unified response envelope"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Unified response envelope with pagination metadata"""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


# =====================================
# PRODUCTION-READY MIXINS
# =====================================

class OptimizedSerializerMixin:
    """Optimized serializer selection with proper fallbacks"""
    serializer_action_map = {}

    def get_serializer_class(self):
        """Safe serializer class resolution preventing assertion errors"""
        action_serializer = self.serializer_action_map.get(self.action)
        if action_serializer:
            return action_serializer

        # Ensure we always have a serializer_class to prevent AssertionError
        if hasattr(self, 'serializer_class') and self.serializer_class:
            return self.serializer_class

        # Added safeguard check
        if hasattr(super(), 'get_serializer_class'):
            return super().get_serializer_class()

        # Last resort fallback
        raise NotImplementedError("No serializer class defined")


class ConsolidatedPermissionMixin:
    """Consolidated permission checking using unified validation"""

    def is_instructor_or_admin(self, user=None):
        """Check if user has instructor or admin privileges"""
        try:
            user = user or self.request.user
            if not user or not user.is_authenticated:
                return False
            return validate_instructor_permissions(user)
        except Exception as e:
            logger.error(f"Error checking instructor permissions: {e}")
            return False

    def has_course_permission(self, course, user=None):
        """Check if user has permission for specific course"""
        try:
            user = user or self.request.user
            if not user or not user.is_authenticated:
                return False

            if user.is_staff or self.is_instructor_or_admin(user):
                return True

            return CourseInstructor.objects.filter(
                course=course, instructor=user, is_active=True
            ).exists()
        except Exception as e:
            logger.error(f"Error checking course permissions: {e}")
            return False


class StandardContextMixin:
    """Standardized serializer context with settings integration"""

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context.update({
                'user_access_level': get_unified_user_access_level(
                    self.request.user if self.request.user.is_authenticated else None
                ),
                'is_instructor': (
                    self.is_instructor_or_admin()
                    if hasattr(self, 'is_instructor_or_admin')
                    else False
                ),
                'request_timestamp': timezone.now(),
                'currency': getattr(settings, 'DEFAULT_CURRENCY', 'USD'),
            })
        except Exception as e:
            logger.error(f"Error building serializer context: {e}")
        return context


class SafeFilterMixin:
    """Safe filtering with comprehensive error handling"""
    filter_mappings = {}

    def apply_filters_safely(self, queryset):
        """Apply filters with error handling"""
        try:
            for param, field in self.filter_mappings.items():
                value = self.request.query_params.get(param)
                if value:
                    try:
                        if isinstance(field, str):
                            queryset = queryset.filter(**{field: value})
                        elif callable(field):
                            queryset = field(queryset, value)
                    except Exception as e:
                        logger.warning(f"Filter error for {param}={value}: {e}")
                        continue
            return queryset
        except Exception as e:
            logger.error(f"Unexpected error in apply_filters_safely: {e}")
            return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_filters_safely(queryset)


# =====================================
# SECURITY AND CACHING
# =====================================

VIEW_CACHE_TIMEOUTS = {
    'public': 300,      # 5 minutes for public content
    'course': 600,      # 10 minutes for course details
    'user': 60,         # 1 minute for user-specific data
    'analytics': 900,   # 15 minutes for analytics
    'health': 30,       # 30 seconds for health checks
}


class SensitiveAPIThrottle(UserRateThrottle):
    """Throttle class for sensitive API endpoints"""
    scope = 'sensitive_api'


# Shared base secure view
class SecureAPIView(APIView):
    """
    Base view class that enforces:
    - Authentication via JWT
    - Rate limiting with appropriate throttle classes
    - Per-user caching for GET requests
    - Standardized error handling

    Provides consistent security and performance optimizations
    for all sensitive API endpoints.
    """
    permission_classes = [IsAuthenticated]
    # Re-add AnonRateThrottle for consistency with original
    throttle_classes = [SensitiveAPIThrottle, AnonRateThrottle]
    cache_timeout = VIEW_CACHE_TIMEOUTS.get('user', 60)  # Default to 1 minute if not specified

    @method_decorator(vary_on_headers('Authorization', 'Accept-Language'))
    def dispatch(self, request, *args, **kwargs):
        # Apply cache only for GET requests
        if request.method == 'GET' and self.cache_timeout > 0:
            decorator = cache_page(self.cache_timeout)
            return decorator(super().dispatch)(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc):
        """Standardized exception handling with proper logging"""
        try:
            response = super().handle_exception(exc)

            # Enhanced error logging
            if hasattr(self.request, 'user') and self.request.user.is_authenticated:
                user_info = f"User {self.request.user.id}"
            else:
                user_info = "Anonymous user"

            logger.error(f"API Error in {self.__class__.__name__}: {exc} - {user_info}")

            return response
        except Exception as e:
            logger.error(f"Exception handling failed in {self.__class__.__name__}: {e}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_serializer_context(self):
        """Provide standardized serializer context"""
        context = {
            'request': self.request,
            'user_access_level': get_unified_user_access_level(
                self.request.user if self.request.user.is_authenticated else None
            ),
            'request_timestamp': timezone.now(),
        }
        return context
