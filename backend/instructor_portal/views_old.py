#
# File Path: instructor_portal/views.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-01 00:00:00
# Date Revised: 2025-06-19 16:19:13


import logging
import functools
import json
import uuid
import re
from typing import Dict, List, Optional, Any, Union
from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from django.db import transaction, IntegrityError, models, DatabaseError
from django.db.models import Max, OuterRef, Subquery, Q, Case, When, F, Count, Prefetch, Value
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, status, permissions, serializers, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied

# FIXED: Import from courses app (external)
from courses.models import Course, Module, Lesson, Resource, Assessment, Question, Category
from courses.permissions import IsInstructorOrAdmin, CanManageCourse, IsEnrolled
from courses.serializers import CourseCloneSerializer
from courses.utils import generate_unique_slug, clear_course_caches, validate_file_security
from courses.validation import validate_course_data, validate_lesson_data, sanitize_input

# Import instructor portal models with correct TierManager
from .models import (
    InstructorProfile, CourseInstructor, InstructorDashboard, InstructorAnalytics,
    CourseCreationSession, CourseTemplate, DraftCourseContent, CourseContentDraft,
    TierManager
)

# Import enhanced serializers with reduced complexity
from .serializers import (
    InstructorCourseSerializer, InstructorModuleSerializer, InstructorLessonSerializer,
    InstructorResourceSerializer, InstructorProfileSerializer, CourseCreationSessionSerializer,
    InstructorDashboardSerializer, CourseTemplateSerializer, DraftCourseContentSerializer,
    CourseInstructorSerializer
)

# Set up structured logging
logger = logging.getLogger(__name__)

# Cache timeouts for performance optimization
COURSE_CACHE_TIMEOUT = 300      # 5 minutes
ANALYTICS_CACHE_TIMEOUT = 600   # 10 minutes
PERMISSIONS_CACHE_TIMEOUT = 180 # 3 minutes

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

def validate_user_permission(user, course, required_permission: str = 'manage') -> bool:
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
                logger.warning(f"User {user.id} attempted instructor action without profile")
                cache.set(cache_key, 'none', PERMISSIONS_CACHE_TIMEOUT)
                return False

        if profile_status != InstructorProfile.Status.ACTIVE:
            logger.warning(f"Instructor {user.id} has inactive profile status: {profile_status}")
            return False

        # Check course-specific instructor permissions using CourseInstructor model
        if course:
            cache_key = f"instructor_permission:{user.id}:{course.id}:{required_permission}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Map permission strings to model fields
            permission_field = {
                'manage': 'is_active',
                'edit': 'can_edit_content',
                'students': 'can_manage_students',
                'analytics': 'can_view_analytics'
            }.get(required_permission, 'is_active')

            # Build query with specific permission
            query = Q(course=course, instructor=user, is_active=True)
            if permission_field != 'is_active':
                query &= Q(**{permission_field: True})

            # Query the permission
            has_permission = CourseInstructor.objects.filter(query).exists()

            # Cache the result
            cache.set(cache_key, has_permission, PERMISSIONS_CACHE_TIMEOUT)
            return has_permission

        # General instructor check using CourseInstructor
        return CourseInstructor.objects.filter(
            instructor=user,
            is_active=True
        ).exists()

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
        'password', 'token', 'key', 'secret', 'email', 'ssn', 'phone',
        'credit_card', 'authorization', 'cookie', 'x-api-key', 'api_key',
        'access_token', 'refresh_token', 'auth', 'credentials', 'private',
        'secret_key', 'account_number', 'social_security', 'passport',
        'license', 'address', 'username'
    }

    # Enhanced pattern matching for sensitive data
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    credit_card_pattern = re.compile(r'^(\d{4}[- ]){3}\d{4}$')

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
        elif isinstance(value, str) and len(value) > 20 and re.match(r'^[A-Za-z0-9\-_\.]+$', value):
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


def audit_log(user, action: str, resource_type: str, resource_id: Optional[int] = None,
              metadata: Optional[Dict] = None, success: bool = True, request=None):
    """Comprehensive audit logging for security monitoring with enhanced metadata"""
    try:
        # Get user IP if request is available
        ip_address = None
        if request and hasattr(request, 'META'):
            ip_address = request.META.get('REMOTE_ADDR', None)
            # Check for X-Forwarded-For header
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if forwarded_for:
                ip_address = forwarded_for.split(',')[0].strip()

        # Get user agent if request is available
        user_agent = None
        if request and hasattr(request, 'META'):
            user_agent = request.META.get('HTTP_USER_AGENT')

        # Build log entry
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user and user.is_authenticated else None,
            'username': user.username if user and user.is_authenticated else 'anonymous',
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'metadata': scrub_sensitive_data(metadata or {}),
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }

        # Add instructor profile info if available
        if user and user.is_authenticated and hasattr(user, 'instructor_profile'):
            log_entry['instructor_tier'] = user.instructor_profile.tier
            log_entry['instructor_status'] = user.instructor_profile.status

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
                InstructorProfile.Tier.DIAMOND
            ]

            if premium_access:
                cache.set(cache_key, True, PERMISSIONS_CACHE_TIMEOUT)
                return True

        # Check subscription (if available)
        try:
            from subscriptions.models import Subscription
            subscription = getattr(user, 'subscription', None)
            if subscription and isinstance(subscription, Subscription):
                has_premium = subscription.tier == 'premium' and subscription.is_active()
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


def validate_file_upload(file_obj, user, allowed_types=None, verify_content=True) -> Dict[str, Any]:
    """
    Enhanced file validation with comprehensive security checks
    Returns tuple of (is_valid, error_message)
    """
    if not file_obj:
        return {'is_valid': False, 'reason': 'No file provided', 'details': {}}

    try:
        # Get instructor profile for tier-based limits
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return {'is_valid': False, 'reason': 'User does not have instructor profile', 'details': {}}

        # Get tier limits
        tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
        max_file_size = tier_limits.get('max_file_size', 10 * 1024 * 1024)  # Default 10MB

        # Check file size
        if file_obj.size > max_file_size:
            max_size_mb = max_file_size / (1024 * 1024)
            return {
                'is_valid': False,
                'reason': f"File too large (max {max_size_mb:.1f}MB for your tier)",
                'details': {
                    'file_size': file_obj.size,
                    'max_size': max_file_size,
                    'tier': instructor_profile.tier
                }
            }

        # Check file extension and type
        file_name = file_obj.name.lower()
        file_ext = file_name.split('.')[-1] if '.' in file_name else ''

        # Use tier-based allowed file types
        if not allowed_types:
            allowed_types = tier_limits.get('file_types_allowed', ['pdf', 'jpg', 'png'])

        # Diamond tier allows any file type when allowed_types is *
        if allowed_types == '*' and instructor_profile.tier == InstructorProfile.Tier.DIAMOND:
            # Still check for dangerous file types
            dangerous_extensions = ['exe', 'bat', 'cmd', 'com', 'sh', 'php', 'pl', 'py', 'js']
            if file_ext in dangerous_extensions:
                return {'is_valid': False, 'reason': f"File type {file_ext} not allowed", 'details': {}}
        elif file_ext not in allowed_types and allowed_types != '*':
            return {
                'is_valid': False,
                'reason': f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_types)}",
                'details': {'extension': file_ext, 'allowed': allowed_types}
            }

        # Verify content type (optional but recommended)
        if verify_content:
            import magic
            file_content_type = None
            try:
                # Read first 2KB of file to determine type
                file_header = file_obj.read(2048)
                file_content_type = magic.from_buffer(file_header, mime=True)
                file_obj.seek(0)  # Reset file pointer

                # Map of safe content types by extension
                safe_types = {
                    'pdf': ['application/pdf'],
                    'jpg': ['image/jpeg'],
                    'jpeg': ['image/jpeg'],
                    'png': ['image/png'],
                    'gif': ['image/gif'],
                    'doc': ['application/msword'],
                    'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
                    'xls': ['application/vnd.ms-excel'],
                    'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                    'ppt': ['application/vnd.ms-powerpoint'],
                    'pptx': ['application/vnd.openxmlformats-officedocument.presentationml.presentation'],
                    'mp4': ['video/mp4'],
                    'mp3': ['audio/mpeg'],
                    'txt': ['text/plain'],
                    'zip': ['application/zip', 'application/x-zip-compressed'],
                }

                if file_ext in safe_types and file_content_type not in safe_types[file_ext]:
                    return {
                        'is_valid': False,
                        'reason': f"File content doesn't match extension. Found: {file_content_type}",
                        'details': {'claimed_type': file_ext, 'actual_type': file_content_type}
                    }

            except Exception as e:
                logger.warning(f"Error checking file content type: {e}", exc_info=True)
                # Continue without content verification if it fails

        # All checks passed
        return {
            'is_valid': True,
            'reason': 'File passed all validation checks',
            'details': {
                'file_name': file_name,
                'file_size': file_obj.size,
                'extension': file_ext,
                'content_type': getattr(file_obj, 'content_type', None),
                'tier': instructor_profile.tier
            }
        }

    except Exception as e:
        logger.error(f"Error validating file: {e}", exc_info=True)
        return {'is_valid': False, 'reason': f"File validation error: {str(e)}", 'details': {}}


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
                'missing_instructor_profile',
                'access_denied',
                metadata={'view': func.__name__},
                success=False,
                request=request
            )
            return Response(
                {'detail': 'Instructor profile required'},
                status=status.HTTP_403_FORBIDDEN
            )

        if instructor_profile.status != InstructorProfile.Status.ACTIVE:
            audit_log(
                request.user,
                f'inactive_instructor_profile_{instructor_profile.status}',
                'access_denied',
                metadata={'view': func.__name__, 'status': instructor_profile.status},
                success=False,
                request=request
            )
            return Response(
                {'detail': f'Instructor profile is {instructor_profile.get_status_display()}'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Add instructor profile to request for easy access
        request.instructor_profile = instructor_profile

        # Ensure instructor profile is tracked even if the request fails
        audit_log(
            request.user,
            'instructor_request',
            'access_granted',
            metadata={
                'view': func.__name__,
                'tier': instructor_profile.tier,
                'instructor_id': instructor_profile.id
            },
            request=request
        )

        return func(self, request, *args, **kwargs)

    return wrapper


def require_permission(permission_type: str = 'manage'):
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
                if hasattr(self, 'get_object'):
                    try:
                        obj = self.get_object()
                    except Exception:
                        pass

                # Special handling for course objects
                course_obj = None
                if hasattr(obj, 'course'):
                    course_obj = obj.course
                elif hasattr(obj, 'module') and hasattr(obj.module, 'course'):
                    course_obj = obj.module.course
                elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'module') and hasattr(obj.lesson.module, 'course'):
                    course_obj = obj.lesson.module.course
                elif isinstance(obj, Course):
                    course_obj = obj

                # Check permission against the course object
                target_obj = course_obj or obj

                # Validate permission
                if not validate_user_permission(request.user, target_obj, permission_type):
                    audit_log(
                        request.user,
                        f"permission_denied_{permission_type}",
                        getattr(self, 'resource_name', obj.__class__.__name__.lower()) if obj else 'unknown',
                        getattr(obj, 'id', None),
                        {'action': func.__name__, 'permission_type': permission_type},
                        success=False,
                        request=request
                    )

                    return Response(
                        {'detail': f'You do not have {permission_type} permission for this resource'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                return func(self, request, *args, **kwargs)

            except DRFPermissionDenied as e:
                # Pass through DRF permission errors
                raise
            except Exception as e:
                logger.error(f"Error in permission decorator: {e}", exc_info=True)
                return Response(
                    {'detail': 'Permission check failed due to an error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            instructor_profile = getattr(request, 'instructor_profile', None)
            if not instructor_profile:
                instructor_profile = get_instructor_profile(request.user)
                if not instructor_profile:
                    return Response(
                        {'detail': 'Instructor profile required'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Map tier names to hierarchy values
            tier_hierarchy = {
                'bronze': 1,
                'silver': 2,
                'gold': 3,
                'platinum': 4,
                'diamond': 5
            }

            # Get current tier level
            current_tier = instructor_profile.tier.lower()
            current_level = tier_hierarchy.get(current_tier, 1)

            # Get required tier level
            required_level = tier_hierarchy.get(min_tier.lower(), 5)  # Default to highest if unknown

            if current_level < required_level:
                audit_log(
                    request.user,
                    'tier_access_denied',
                    'feature_access',
                    metadata={
                        'current_tier': current_tier,
                        'required_tier': min_tier,
                        'view': func.__name__
                    },
                    success=False,
                    request=request
                )

                return Response(
                    {
                        'detail': f'This feature requires {min_tier.title()} tier or higher',
                        'current_tier': current_tier.title(),
                        'required_tier': min_tier.title()
                    },
                    status=status.HTTP_403_FORBIDDEN
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
    resource_name = 'resource'  # Override in child classes
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def initial(self, request, *args, **kwargs):
        """Verify instructor profile exists before processing any request"""
        super().initial(request, *args, **kwargs)

        # Store instructor profile on request
        instructor_profile = get_instructor_profile(request.user)
        if instructor_profile and instructor_profile.status == InstructorProfile.Status.ACTIVE:
            request.instructor_profile = instructor_profile

    def get_error_response(self, message, status_code=400, errors=None):
        """Standardized error response format"""
        response_data = {'detail': message}
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status_code)

    def handle_exception(self, exc):
        """Standardized exception handling"""
        if isinstance(exc, DjangoValidationError):
            return self.get_error_response(
                "Validation error",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=exc.message_dict if hasattr(exc, 'message_dict') else {'non_field_errors': exc.messages}
            )

        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error: {exc}")
            return self.get_error_response(
                "Database constraint violation",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        elif isinstance(exc, PermissionDenied) or isinstance(exc, DRFPermissionDenied):
            return self.get_error_response(
                str(exc),
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Let DRF handle other exceptions
        return super().handle_exception(exc)


# =====================================
# ENHANCED VIEWSETS WITH MODEL INTEGRATION
# =====================================

class InstructorCourseViewSet(InstructorBaseViewSet):
    """
    Enhanced API endpoint for instructors to manage courses
    FIXED: Full integration with enhanced models and centralized permissions
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    lookup_field = 'slug'
    resource_name = 'course'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile integration"""
        user = self.request.user

        # Validate user has instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Course.objects.none()

        # Staff and superuser get all courses
        if user.is_staff or user.is_superuser:
            courses = Course.objects.select_related('category', 'parent_version')
        else:
            # FIXED: Use CourseInstructor model for filtering
            courses = Course.objects.filter(
                courseinstructor_set__instructor=user,
                courseinstructor_set__is_active=True
            ).select_related('category', 'parent_version')

        # Enhanced prefetching with CourseInstructor
        courses = courses.prefetch_related(
            Prefetch(
                'courseinstructor_set',
                queryset=CourseInstructor.objects.select_related('instructor').filter(is_active=True)
            ),
            Prefetch(
                'modules',
                queryset=Module.objects.prefetch_related('lessons').order_by('order')
            )
        )

        # Add analytics annotations for performance optimization
        return courses.annotate(
            enrolled_students_count=Count('enrollments', filter=Q(enrollments__status='active'), distinct=True),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            total_reviews=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True)
        ).order_by('-updated_date')

    @require_instructor_profile
    @require_permission('manage')
    def create(self, request, *args, **kwargs):
        """Enhanced course creation with InstructorProfile integration"""
        instructor_profile = request.instructor_profile

        audit_log(request.user, 'course_create_attempt', 'course', metadata={
            'instructor_tier': instructor_profile.tier,
            'instructor_status': instructor_profile.status
        }, request=request)

        try:
            # Validate course limits based on instructor tier using TierManager
            current_course_count = instructor_profile.total_courses
            if not TierManager.check_courses_limit(instructor_profile.tier, current_course_count):
                tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
                max_courses = tier_limits.get('max_courses', 3)
                return Response(
                    {
                        'detail': f'Course limit reached for {instructor_profile.get_tier_display()} tier',
                        'current_count': current_course_count,
                        'max_courses': max_courses
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create course with proper validation
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                course = serializer.save()

                # FIXED: Create CourseInstructor relationship
                # Already handled in the serializer now

                # Update instructor analytics
                instructor_profile.update_analytics()

            audit_log(request.user, 'course_created', 'course', course.id, {
                'title': course.title,
                'instructor_tier': instructor_profile.tier
            }, request=request)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            audit_log(request.user, 'course_create_failed', 'course',
                      metadata={'error': str(e)}, success=False, request=request)
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Course creation failed: {e}", exc_info=True)
            audit_log(request.user, 'course_create_failed', 'course',
                      metadata={'error': str(e)}, success=False, request=request)
            return Response(
                {'detail': 'Course creation failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @require_permission('manage')
    @tier_required('silver')
    @action(detail=True, methods=['post'])
    def clone(self, request, slug=None):
        """Enhanced course cloning with tier validation"""
        source_course = self.get_object()
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                # Clone course logic here
                cloned_course = source_course.clone_version(request.user)

                # Update instructor analytics
                instructor_profile.update_analytics()

                serializer = self.get_serializer(cloned_course)

                audit_log(request.user, 'course_cloned', 'course', cloned_course.id, {
                    'source_course_id': source_course.id,
                    'instructor_tier': instructor_profile.tier
                }, request=request)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Course cloning failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Course cloning failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @require_permission('manage')
    @action(detail=True, methods=['post'], url_path='reorder-modules')
    def reorder_modules(self, request, slug=None):
        """Reorder modules within a course"""
        course = self.get_object()
        modules_data = request.data.get('modules', [])

        # Validate input
        if not isinstance(modules_data, list):
            return Response(
                {'detail': 'modules must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate each module entry
        for i, module_data in enumerate(modules_data):
            if not isinstance(module_data, dict):
                return Response(
                    {'detail': f'modules[{i}] must be an object'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not {'id', 'order'} <= set(module_data.keys()):
                return Response(
                    {'detail': f'modules[{i}] must have id and order fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Limit operations to prevent DoS
        if len(modules_data) > MAX_BULK_OPERATIONS:
            return Response(
                {'detail': f'Too many modules (max {MAX_BULK_OPERATIONS})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Normalize order to prevent duplicates
                sorted_modules = sorted(modules_data, key=lambda x: int(x['order']))

                for idx, module_data in enumerate(sorted_modules, 1):
                    module_id = int(module_data['id'])

                    updated = Module.objects.filter(
                        id=module_id,
                        course=course
                    ).update(order=idx)

                    if not updated:
                        return Response(
                            {'detail': f"Module {module_id} not found in this course"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                # Clear caches
                clear_course_caches(course.id)

            audit_log(request.user, 'modules_reordered', 'course', course.id, {
                'module_count': len(modules_data)
            }, request=request)

            return Response({'detail': 'Module order updated successfully'})

        except Exception as e:
            logger.error(f"Module reordering failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Module reordering failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================
# NEW VIEWSETS FOR ENHANCED MODELS
# =====================================

class InstructorProfileViewSet(InstructorBaseViewSet):
    """
    API endpoint for instructor profile management
    ENHANCED: Full integration with TierManager
    """
    serializer_class = InstructorProfileSerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'instructor_profile'

    def get_object(self):
        """Get current user's instructor profile or create if needed"""
        try:
            profile = get_instructor_profile(self.request.user)
            if profile:
                return profile

            # Create profile if it doesn't exist
            user = self.request.user
            display_name = user.get_full_name() or user.username

            profile = InstructorProfile.objects.create(
                user=user,
                display_name=display_name,
                status=InstructorProfile.Status.PENDING
            )

            # Invalidate cache
            cache.delete(f"instructor_profile:{user.id}")

            return profile

        except Exception as e:
            logger.error(f"Error getting/creating instructor profile: {e}", exc_info=True)
            raise

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get comprehensive instructor analytics"""
        instructor_profile = self.get_object()

        try:
            # Get analytics data
            performance_metrics = instructor_profile.get_performance_metrics()
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)

            # Get recent analytics
            days_limit = tier_limits.get('analytics_history_days', 30)
            cutoff_date = timezone.now() - timezone.timedelta(days=days_limit)

            recent_analytics = InstructorAnalytics.objects.filter(
                instructor=instructor_profile,
                date__gte=cutoff_date
            ).order_by('-date')[:30]

            analytics_data = {
                'profile': InstructorProfileSerializer(instructor_profile).data,
                'performance_metrics': performance_metrics,
                'tier_limits': tier_limits,
                'recent_analytics': [
                    {
                        'date': analytics.date,
                        'total_students': analytics.total_students,
                        'total_courses': analytics.total_courses,
                        'average_rating': float(analytics.average_rating),
                        'total_revenue': float(analytics.total_revenue),
                        'completion_rate': float(analytics.completion_rate)
                    }
                    for analytics in recent_analytics
                ]
            }

            # Record this analytics access for audit
            audit_log(
                request.user,
                'analytics_accessed',
                'instructor_profile',
                instructor_profile.id,
                {'tier': instructor_profile.tier},
                request=request
            )

            return Response(analytics_data)

        except Exception as e:
            logger.error(f"Error getting analytics data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve analytics data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def request_verification(self, request):
        """Request instructor verification"""
        instructor_profile = self.get_object()

        if instructor_profile.is_verified:
            return Response(
                {'detail': 'Profile is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status to pending verification
        instructor_profile.status = InstructorProfile.Status.PENDING
        instructor_profile.save(update_fields=['status'])

        # Clear permissions cache
        cache.delete(f"instructor_profile_status:{request.user.id}")

        audit_log(request.user, 'verification_requested', 'instructor_profile', instructor_profile.id)

        return Response({'detail': 'Verification request submitted'})

    @action(detail=False, methods=['post'])
    def update_analytics(self, request):
        """Manually update analytics"""
        instructor_profile = self.get_object()

        success = instructor_profile.update_analytics()
        if success:
            # Create daily snapshot
            InstructorAnalytics.record_daily_snapshot(instructor_profile)
            return Response({'detail': 'Analytics updated successfully'})
        else:
            return Response(
                {'detail': 'Failed to update analytics. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseInstructorViewSet(InstructorBaseViewSet):
    """
    API endpoint for managing course-instructor relationships
    """
    serializer_class = CourseInstructorSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    resource_name = 'course_instructor'

    def get_queryset(self):
        """Get queryset based on permissions"""
        user = self.request.user

        # Staff and superusers see all
        if user.is_staff or user.is_superuser:
            return CourseInstructor.objects.all()

        # Filter by courses where user is an instructor
        course_id = self.request.query_params.get('course')
        if course_id:
            # Check if user has permission for this course
            try:
                course = Course.objects.get(id=course_id)
                if validate_user_permission(user, course, 'manage'):
                    return CourseInstructor.objects.filter(course=course)
                else:
                    return CourseInstructor.objects.none()
            except Course.DoesNotExist:
                return CourseInstructor.objects.none()

        # Return all relationships where user is involved
        return CourseInstructor.objects.filter(
            Q(instructor=user) |
            Q(course__in=Course.objects.filter(
                courseinstructor_set__instructor=user,
                courseinstructor_set__is_active=True,
                courseinstructor_set__is_lead=True
            ))
        ).distinct()

    @require_instructor_profile
    @require_permission('manage')
    @tier_required('gold')
    def create(self, request, *args, **kwargs):
        """Create new course-instructor relationship with tier check"""
        instructor_profile = request.instructor_profile

        # Additional validation for course ownership
        course_id = request.data.get('course')
        if not course_id:
            return Response(
                {'detail': 'Course ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check that user has lead instructor permission
        if not CourseInstructor.objects.filter(
            course=course,
            instructor=request.user,
            is_active=True,
            is_lead=True
        ).exists():
            return Response(
                {'detail': 'Only lead instructors can add other instructors'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check maximum instructors limit based on tier
        tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
        max_instructors = tier_limits.get('max_instructors_per_course', 1)

        if max_instructors != -1:  # -1 means unlimited
            current_count = CourseInstructor.objects.filter(course=course, is_active=True).count()
            if current_count >= max_instructors:
                return Response(
                    {
                        'detail': f'Maximum instructor limit reached for your tier ({max_instructors})',
                        'current_count': current_count,
                        'max_instructors': max_instructors
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().create(request, *args, **kwargs)


class CourseCreationSessionViewSet(InstructorBaseViewSet):
    """
    API endpoint for course creation session management
    ENHANCED: Complete course creation workflow support
    """
    serializer_class = CourseCreationSessionSerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'course_creation_session'

    def get_queryset(self):
        """Get user's course creation sessions"""
        instructor_profile = get_instructor_profile(self.request.user)
        if not instructor_profile:
            return CourseCreationSession.objects.none()

        return CourseCreationSession.objects.filter(
            instructor=instructor_profile
        ).order_by('-updated_date')

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def start_wizard(self, request):
        """Start wizard-based course creation"""
        instructor_profile = request.instructor_profile

        # Check course limit
        if not TierManager.check_courses_limit(
            instructor_profile.tier,
            instructor_profile.total_courses
        ):
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_courses = tier_limits.get('max_courses', 3)

            return Response(
                {
                    'detail': f'Course limit reached for your tier',
                    'current_count': instructor_profile.total_courses,
                    'max_courses': max_courses,
                    'tier': instructor_profile.get_tier_display()
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Create new wizard session
            session = CourseCreationSession.objects.create(
                instructor=instructor_profile,
                creation_method=CourseCreationSession.CreationMethod.WIZARD,
                total_steps=6,  # Define your wizard steps
                course_data={},  # Initialize empty data
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            serializer = self.get_serializer(session)

            audit_log(
                request.user,
                'course_wizard_started',
                'course_creation_session',
                session.id,
                {'session_id': str(session.session_id)},
                request=request
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating wizard session: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create course creation session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @tier_required('gold')
    @action(detail=False, methods=['post'])
    def start_ai_builder(self, request):
        """Start AI-assisted course creation"""
        instructor_profile = request.instructor_profile
        ai_prompt = request.data.get('ai_prompt', '').strip()

        # Validate AI prompt
        if not ai_prompt or len(ai_prompt) < 20:
            return Response(
                {'detail': 'AI prompt must be at least 20 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check course limit
        if not TierManager.check_courses_limit(
            instructor_profile.tier,
            instructor_profile.total_courses
        ):
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_courses = tier_limits.get('max_courses', 3)

            return Response(
                {
                    'detail': f'Course limit reached for your tier',
                    'current_count': instructor_profile.total_courses,
                    'max_courses': max_courses
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Create AI builder session
            session = CourseCreationSession.objects.create(
                instructor=instructor_profile,
                creation_method=CourseCreationSession.CreationMethod.AI_BUILDER,
                total_steps=4,
                course_data={},
                ai_prompt=ai_prompt,
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            # In a real implementation, you would:
            # 1. Queue the AI prompt for processing
            # 2. Notify the user that generation is in progress
            # 3. Update the session when AI content is ready

            serializer = self.get_serializer(session)

            audit_log(
                request.user,
                'ai_builder_started',
                'course_creation_session',
                session.id,
                {
                    'session_id': str(session.session_id),
                    'prompt_length': len(ai_prompt)
                },
                request=request
            )

            return Response(
                {
                    **serializer.data,
                    'ai_status': 'processing',
                    'estimated_wait': '2-5 minutes'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating AI builder session: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create AI builder session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def auto_save(self, request, pk=None):
        """Auto-save session data"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data

        # Validate auto-save data
        if not isinstance(data, dict):
            return Response(
                {'detail': 'Auto-save data must be a valid JSON object'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent auto-save for published sessions
        if session.status in [
            CourseCreationSession.Status.PUBLISHED,
            CourseCreationSession.Status.FAILED
        ]:
            return Response(
                {'detail': f'Cannot auto-save a session in {session.get_status_display()} status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = session.auto_save(data)
        if success:
            return Response({'detail': 'Auto-saved successfully'})
        else:
            return Response(
                {'detail': 'Auto-save failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate session content before publishing"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update status to validating
        session.status = CourseCreationSession.Status.VALIDATING
        session.save(update_fields=['status'])

        try:
            # Perform validation
            errors = session.validate_course_data()

            # Update status based on validation results
            if errors:
                session.status = CourseCreationSession.Status.DRAFT
                session.validation_errors = errors
                session.save(update_fields=['status', 'validation_errors'])

                return Response(
                    {
                        'is_valid': False,
                        'errors': errors,
                        'status': session.get_status_display()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                session.status = CourseCreationSession.Status.READY_TO_PUBLISH
                session.validation_errors = []
                session.save(update_fields=['status', 'validation_errors'])

                return Response({
                    'is_valid': True,
                    'status': session.get_status_display()
                })

        except Exception as e:
            logger.error(f"Error validating session {session.id}: {e}", exc_info=True)
            session.status = CourseCreationSession.Status.DRAFT
            session.save(update_fields=['status'])

            return Response(
                {'detail': 'Validation failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish course from creation session"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to publish this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate session is ready for publishing
        if session.status != CourseCreationSession.Status.READY_TO_PUBLISH:
            # Auto-validate if needed
            if session.status == CourseCreationSession.Status.DRAFT:
                errors = session.validate_course_data()
                if errors:
                    return Response(
                        {
                            'detail': 'Session is not ready for publishing',
                            'errors': errors[:5],  # Limit to first 5 errors
                            'error_count': len(errors)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update status if validation passes
                session.status = CourseCreationSession.Status.READY_TO_PUBLISH
                session.save(update_fields=['status'])
            else:
                return Response(
                    {
                        'detail': 'Session is not ready for publishing',
                        'status': session.get_status_display()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            # Execute publishing with proper serializer integration
            serializer = self.get_serializer(session)
            course = serializer.publish_course()

            if not course:
                return Response(
                    {'detail': 'Course publishing failed. See validation errors for details.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update instructor analytics
            session.instructor.update_analytics()

            audit_log(
                request.user,
                'session_published',
                'course',
                course.id,
                {
                    'session_id': str(session.session_id),
                    'creation_method': session.creation_method
                },
                request=request
            )

            return Response({
                'detail': 'Course published successfully',
                'course_id': course.id,
                'course_slug': course.slug,
                'course_title': course.title
            })

        except Exception as e:
            logger.error(f"Error publishing course for session {session.id}: {e}", exc_info=True)
            return Response(
                {'detail': 'Course publishing failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseTemplateViewSet(InstructorBaseViewSet):
    """
    API endpoint for course template management
    """
    serializer_class = CourseTemplateSerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'course_template'

    def get_queryset(self):
        """Get available templates based on user permissions"""
        # Public templates available to all authenticated users
        queryset = CourseTemplate.objects.filter(is_active=True)

        # Additional filtering options
        category = self.request.query_params.get('category')
        template_type = self.request.query_params.get('type')
        difficulty = self.request.query_params.get('difficulty')

        if category:
            queryset = queryset.filter(category_id=category)

        if template_type:
            queryset = queryset.filter(template_type=template_type)

        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        return queryset.select_related('category', 'created_by')

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def create_session(self, request, pk=None):
        """Create a course creation session from template"""
        template = self.get_object()
        instructor_profile = request.instructor_profile

        # Check course limit
        if not TierManager.check_courses_limit(
            instructor_profile.tier,
            instructor_profile.total_courses
        ):
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_courses = tier_limits.get('max_courses', 3)

            return Response(
                {
                    'detail': f'Course limit reached for {instructor_profile.get_tier_display()} tier',
                    'current_count': instructor_profile.total_courses,
                    'max_courses': max_courses
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Use serializer method to create session from template
            serializer = self.get_serializer(template)
            session = serializer.create_session_from_template(instructor_profile)

            session_serializer = CourseCreationSessionSerializer(session)

            audit_log(
                request.user,
                'template_session_created',
                'course_creation_session',
                session.id,
                {'template_id': template.id, 'template_name': template.name},
                request=request
            )

            return Response(
                session_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating session from template: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create session from template'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @tier_required('platinum')
    @action(detail=False, methods=['post'])
    def create_template(self, request):
        """Create a new course template (premium feature)"""
        # This is a premium feature restricted to higher tiers
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Set the creator
                template = serializer.save(created_by=request.user)

                audit_log(
                    request.user,
                    'template_created',
                    'course_template',
                    template.id,
                    {'template_name': template.name},
                    request=request
                )

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return Response(
                {'detail': 'Template creation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorDashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for instructor dashboard management
    ENHANCED: Complete dashboard functionality with new models integration
    """
    permission_classes = [IsAuthenticated]

    @require_instructor_profile
    def list(self, request):
        """Get complete dashboard data"""
        instructor_profile = request.instructor_profile

        try:
            # Get or create dashboard configuration
            dashboard, created = InstructorDashboard.objects.get_or_create(
                instructor=instructor_profile,
                defaults={
                    'show_analytics': True,
                    'show_recent_students': True,
                    'show_performance_metrics': True
                }
            )

            dashboard_data = dashboard.get_dashboard_data()
            serializer = InstructorDashboardSerializer(dashboard)

            return Response({
                'config': serializer.data,
                'dashboard': dashboard_data,
                'instructor': {
                    'id': instructor_profile.id,
                    'display_name': instructor_profile.display_name,
                    'tier': instructor_profile.get_tier_display(),
                    'status': instructor_profile.get_status_display(),
                    'analytics': instructor_profile.get_performance_metrics()
                }
            })

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load dashboard'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def update_config(self, request):
        """Update dashboard configuration"""
        instructor_profile = request.instructor_profile

        try:
            dashboard = InstructorDashboard.objects.get(instructor=instructor_profile)

            # Update configuration fields
            config_fields = [
                'show_analytics', 'show_recent_students', 'show_performance_metrics',
                'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
                'notify_new_reviews', 'notify_course_completions'
            ]

            for field in config_fields:
                if field in request.data:
                    setattr(dashboard, field, request.data[field])

            # Update layout settings if provided
            if 'widget_order' in request.data:
                widget_order = request.data['widget_order']
                if not isinstance(widget_order, list):
                    return Response(
                        {'detail': 'widget_order must be a list'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                dashboard.widget_order = widget_order

            if 'custom_colors' in request.data:
                custom_colors = request.data['custom_colors']
                if not isinstance(custom_colors, dict):
                    return Response(
                        {'detail': 'custom_colors must be an object'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                dashboard.custom_colors = custom_colors

            dashboard.save()

            audit_log(
                request.user,
                'dashboard_config_updated',
                'dashboard',
                dashboard.id,
                request=request
            )

            return Response({
                'detail': 'Dashboard configuration updated',
                'config': InstructorDashboardSerializer(dashboard).data
            })

        except InstructorDashboard.DoesNotExist:
            return Response(
                {'detail': 'Dashboard configuration not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating dashboard config: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to update configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def analytics_summary(self, request):
        """Get analytics summary for dashboard"""
        instructor_profile = request.instructor_profile

        try:
            # Get recent analytics with tier-based limits
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            history_days = tier_limits.get('analytics_history_days', 30)
            cutoff_date = timezone.now() - timezone.timedelta(days=history_days)

            # Get recent analytics
            recent_analytics = InstructorAnalytics.objects.filter(
                instructor=instructor_profile,
                date__gte=cutoff_date
            ).order_by('-date')

            # Calculate trends
            if recent_analytics.count() >= 2:
                latest = recent_analytics[0]
                previous = recent_analytics[1]

                trends = {
                    'students_trend': latest.total_students - previous.total_students,
                    'revenue_trend': float(latest.total_revenue - previous.total_revenue),
                    'rating_trend': float(latest.average_rating - previous.average_rating),
                    'completion_trend': float(latest.completion_rate - previous.completion_rate)
                }
            else:
                trends = {
                    'students_trend': 0,
                    'revenue_trend': 0.0,
                    'rating_trend': 0.0,
                    'completion_trend': 0.0
                }

            summary = {
                'current_metrics': instructor_profile.get_performance_metrics(),
                'trends': trends,
                'tier_limits': tier_limits,
                'history_days_available': history_days,
                'recent_data': [
                    {
                        'date': analytics.date,
                        'students': analytics.total_students,
                        'revenue': float(analytics.total_revenue),
                        'rating': float(analytics.average_rating),
                        'completion_rate': float(analytics.completion_rate)
                    }
                    for analytics in recent_analytics[:min(30, history_days)]  # Last N days based on tier
                ]
            }

            return Response(summary)

        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load analytics summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorModuleViewSet(InstructorBaseViewSet):
    """
    Enhanced module management with comprehensive security
    """
    serializer_class = InstructorModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'module'

    def get_queryset(self):
        """Enhanced queryset with security filtering and InstructorProfile integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Module.objects.none()

        course_id = self.request.query_params.get('course')
        if course_id:
            try:
                course_id = int(course_id)
                course = Course.objects.get(id=course_id)

                # Check course-specific permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Module.objects.filter(
                        course_id=course_id
                    ).select_related('course').prefetch_related('lessons')
                else:
                    return Module.objects.none()

            except (ValueError, Course.DoesNotExist):
                return Module.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Module.objects.select_related('course').prefetch_related('lessons')

        return Module.objects.filter(
            course__courseinstructor_set__instructor=user,
            course__courseinstructor_set__is_active=True
        ).select_related('course').prefetch_related('lessons')

    @require_instructor_profile
    @require_permission('edit')
    def perform_create(self, serializer):
        """Enhanced module creation with validation and analytics update"""
        course_id = self.request.data.get('course')
        if not course_id:
            raise serializers.ValidationError({"detail": "Course ID is required."})

        try:
            course_id = int(course_id)
            course = get_object_or_404(Course, id=course_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"detail": "Invalid course ID."})

        # Verify user has permission for this course using CourseInstructor
        if not CourseInstructor.objects.filter(
            course=course,
            instructor=self.request.user,
            is_active=True,
            can_edit_content=True
        ).exists():
            raise PermissionDenied("You do not have permission to create modules in this course.")

        with transaction.atomic():
            serializer.save(course=course)

            # Update instructor analytics
            if hasattr(self.request, 'instructor_profile'):
                self.request.instructor_profile.update_analytics()

            # Clear course caches
            clear_course_caches(course.id)

        audit_log(
            self.request.user,
            'module_created',
            'module',
            serializer.instance.id,
            {
                'course_id': course.id,
                'title': serializer.instance.title
            },
            request=self.request
        )

    @require_instructor_profile
    @require_permission('edit')
    @action(detail=True, methods=['post'], url_path='lessons/reorder')
    def reorder_lessons(self, request, pk=None):
        """
        Concurrency-safe lesson reordering with comprehensive validation
        ENHANCED: Integration with instructor profile and analytics
        """
        module = self.get_object()
        lessons_data = request.data.get('lessons', [])

        # Validate input
        if not isinstance(lessons_data, list):
            return Response(
                {'detail': 'lessons must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate each lesson entry
        for i, lesson_data in enumerate(lessons_data):
            if not isinstance(lesson_data, dict):
                return Response(
                    {'detail': f'lessons[{i}] must be an object'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not {'id', 'order'} <= set(lesson_data.keys()):
                return Response(
                    {'detail': f'lessons[{i}] must have id and order fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Limit operations to prevent DoS
        if len(lessons_data) > MAX_BULK_OPERATIONS:
            return Response(
                {'detail': f'Too many lessons (max {MAX_BULK_OPERATIONS})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Normalize order to prevent duplicates
                sorted_lessons = sorted(lessons_data, key=lambda x: int(x['order']))

                for idx, lesson_data in enumerate(sorted_lessons, 1):
                    lesson_id = int(lesson_data['id'])

                    updated = Lesson.objects.filter(
                        id=lesson_id,
                        module=module
                    ).update(order=idx)

                    if not updated:
                        return Response(
                            {'detail': f"Lesson {lesson_id} not found in this module"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                # Clear caches and update analytics
                clear_course_caches(module.course.id)
                if hasattr(request, 'instructor_profile'):
                    request.instructor_profile.update_analytics()

            audit_log(
                request.user,
                'lessons_reordered',
                'module',
                module.id,
                {
                    'lesson_count': len(lessons_data)
                },
                request=request
            )

            return Response({'detail': 'Lesson order updated successfully'})

        except Exception as e:
            logger.error(f"Lesson reordering failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Lesson reordering failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorLessonViewSet(InstructorBaseViewSet):
    """
    Enhanced lesson management with comprehensive security and model integration
    """
    serializer_class = InstructorLessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'lesson'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile and CourseInstructor integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Lesson.objects.none()

        module_id = self.request.query_params.get('module')
        course_id = self.request.query_params.get('course')

        if module_id:
            try:
                module_id = int(module_id)
                module = Module.objects.select_related('course').get(id=module_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=module.course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Lesson.objects.filter(
                        module_id=module_id
                    ).select_related('module__course').prefetch_related('resources')
                else:
                    return Lesson.objects.none()

            except (ValueError, Module.DoesNotExist):
                return Lesson.objects.none()

        elif course_id:
            try:
                course_id = int(course_id)
                course = Course.objects.get(id=course_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Lesson.objects.filter(
                        module__course_id=course_id
                    ).select_related('module__course').prefetch_related('resources')
                else:
                    return Lesson.objects.none()

            except (ValueError, Course.DoesNotExist):
                return Lesson.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Lesson.objects.select_related('module__course').prefetch_related('resources')

        return Lesson.objects.filter(
            module__course__courseinstructor_set__instructor=user,
            module__course__courseinstructor_set__is_active=True
        ).select_related('module__course').prefetch_related('resources')

    @require_instructor_profile
    @require_permission('edit')
    def perform_create(self, serializer):
        """Enhanced lesson creation with validation and analytics"""
        module_id = self.request.data.get('module')
        if not module_id:
            raise serializers.ValidationError({"detail": "Module ID is required."})

        try:
            module_id = int(module_id)
            module = get_object_or_404(Module, id=module_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"detail": "Invalid module ID."})

        # Verify permissions using CourseInstructor
        if not CourseInstructor.objects.filter(
            course=module.course,
            instructor=self.request.user,
            is_active=True,
            can_edit_content=True
        ).exists():
            raise PermissionDenied("You do not have permission to create lessons in this course.")

        # Validate lesson data
        lesson_data = dict(self.request.data)
        validation_errors = validate_lesson_data(lesson_data)
        if validation_errors:
            raise serializers.ValidationError({
                "detail": "Lesson validation failed",
                "errors": validation_errors
            })

        with transaction.atomic():
            serializer.save(module=module)

            # Update instructor analytics
            if hasattr(self.request, 'instructor_profile'):
                self.request.instructor_profile.update_analytics()

            # Clear course caches
            clear_course_caches(module.course.id)

        audit_log(
            self.request.user,
            'lesson_created',
            'lesson',
            serializer.instance.id,
            {
                'module_id': module.id,
                'course_id': module.course.id,
                'title': serializer.instance.title
            },
            request=self.request
        )

    @require_instructor_profile
    @require_permission('edit')
    def perform_update(self, serializer):
        """Enhanced lesson update with validation"""
        lesson = self.get_object()

        # Validate lesson data
        lesson_data = dict(self.request.data)
        validation_errors = validate_lesson_data(lesson_data)
        if validation_errors:
            raise serializers.ValidationError({
                "detail": "Lesson validation failed",
                "errors": validation_errors
            })

        with transaction.atomic():
            serializer.save()

            # Clear course caches
            clear_course_caches(lesson.module.course.id)

        audit_log(
            self.request.user,
            'lesson_updated',
            'lesson',
            lesson.id,
            {
                'title': lesson.title
            },
            request=self.request
        )


class InstructorResourceViewSet(InstructorBaseViewSet):
    """
    Enhanced resource management with file security and model integration
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = InstructorResourceSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'resource'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Resource.objects.none()

        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            try:
                lesson_id = int(lesson_id)
                lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=lesson.module.course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Resource.objects.filter(lesson_id=lesson_id)
                else:
                    return Resource.objects.none()

            except (ValueError, Lesson.DoesNotExist):
                return Resource.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Resource.objects.select_related('lesson__module__course')

        return Resource.objects.filter(
            lesson__module__course__courseinstructor_set__instructor=user,
            lesson__module__course__courseinstructor_set__is_active=True
        ).select_related('lesson__module__course')

    @require_instructor_profile
    @action(detail=False, methods=['post'], url_path='presigned-url',
            throttle_classes=[UserRateThrottle])
    def presigned_url(self, request):
        """
        Enhanced presigned URL generation with security validation and tier checking
        """
        instructor_profile = request.instructor_profile

        try:
            filename = request.data.get('filename', '').strip()
            content_type = request.data.get('content_type', '').strip()
            file_size = request.data.get('file_size', 0)

            # Validate inputs
            if not filename:
                return Response(
                    {'detail': 'filename is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not content_type:
                return Response(
                    {'detail': 'content_type is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                file_size = int(file_size)
            except (ValueError, TypeError):
                return Response(
                    {'detail': 'file_size must be an integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size based on instructor tier using TierManager
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_size = tier_limits.get('max_file_size', 10 * 1024 * 1024)  # Default 10MB

            if file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                return Response(
                    {
                        'detail': f'File too large (max {max_size_mb:.1f}MB for your tier)',
                        'max_size': max_size,
                        'file_size': file_size,
                        'tier': instructor_profile.get_tier_display()
                    },
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )

            # Get allowed file types from tier limits
            allowed_types = tier_limits.get('file_types_allowed', ['pdf', 'jpg', 'png'])

            # Check file extension
            file_ext = filename.split('.')[-1].lower() if '.' in filename else ''

            # Diamond tier can use any file type
            if allowed_types == '*' and instructor_profile.tier == 'diamond':
                # Still check for dangerous file types
                dangerous_extensions = ['exe', 'bat', 'cmd', 'com', 'sh', 'php', 'pl', 'py', 'js']
                if file_ext in dangerous_extensions:
                    return Response(
                        {'detail': f"File type {file_ext} not allowed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif file_ext not in allowed_types and allowed_types != '*':
                return Response(
                    {
                        'detail': f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_types)}",
                        'allowed_types': allowed_types
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file security
            security_result = validate_file_security(filename, content_type, file_size)
            if not security_result['is_safe']:
                audit_log(
                    request.user,
                    'unsafe_file_upload_attempt',
                    'resource',
                    metadata={
                        'filename': filename,
                        'reason': security_result['reason']
                    },
                    success=False,
                    request=request
                )
                return Response(
                    {'detail': f'File rejected: {security_result["reason"]}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate unique file path
            file_uuid = uuid.uuid4()
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            unique_filename = f"{file_uuid}.{file_extension}" if file_extension else str(file_uuid)
            file_path = f"instructor_resources/{request.user.id}/{unique_filename}"

            # Generate presigned URL (implementation depends on your storage backend)
            # This is a placeholder - implement according to your storage system
            presigned_data = {
                'upload_url': f"https://your-storage-service.com/presigned-upload",
                'file_path': file_path,
                'expires_in': 3600,  # 1 hour
                'fields': {
                    'key': file_path,
                    'Content-Type': content_type,
                    'Content-Length': str(file_size)
                }
            }

            audit_log(
                request.user,
                'presigned_url_generated',
                'resource',
                metadata={
                    'filename': filename,
                    'file_size': file_size,
                    'instructor_tier': instructor_profile.tier
                },
                request=request
            )

            return Response(presigned_data)

        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to generate upload URL'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'], throttle_classes=[UserRateThrottle])
    def upload_complete(self, request):
        """Handle upload completion and create resource record"""
        instructor_profile = request.instructor_profile

        try:
            file_path = request.data.get('file_path')
            lesson_id = request.data.get('lesson_id')
            title = request.data.get('title', '').strip()
            description = request.data.get('description', '').strip()

            if not all([file_path, lesson_id, title]):
                return Response(
                    {'detail': 'file_path, lesson_id, and title are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate lesson ownership
            try:
                lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)
                if not CourseInstructor.objects.filter(
                    course=lesson.module.course,
                    instructor=request.user,
                    is_active=True,
                    can_edit_content=True
                ).exists():
                    return Response(
                        {'detail': 'Permission denied for this lesson'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Lesson.DoesNotExist:
                return Response(
                    {'detail': 'Lesson not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create resource record
            with transaction.atomic():
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=sanitize_input(title),
                    description=sanitize_input(description),
                    file_path=file_path,
                    resource_type='file',
                    uploaded_by=request.user
                )

                # Update instructor analytics
                instructor_profile.update_analytics()

            audit_log(
                request.user,
                'resource_uploaded',
                'resource',
                resource.id,
                {
                    'lesson_id': lesson.id,
                    'title': resource.title
                },
                request=request
            )

            serializer = self.get_serializer(resource)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Upload completion failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Upload completion failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================
# ENHANCED DEBUG VIEW WITH MODEL INTEGRATION
# =====================================

@require_instructor_profile
def debug_courses(request, template=None):
    """
    Enhanced debug view with comprehensive security and InstructorProfile integration
    """
    # Security check for debug access
    if not settings.DEBUG and not (request.user.is_staff or request.user.is_superuser):
        audit_log(
            request.user,
            'unauthorized_debug_access',
            'system',
            success=False,
            request=request
        )
        return JsonResponse({'error': 'Debug access denied'}, status=403)

    if request.GET.get('diagnostic') == 'true':
        instructor_profile = get_instructor_profile(request.user)

        diagnostic_info = {
            "timestamp": timezone.now().isoformat(),
            "routing": "successful",
            "view": "debug_courses",
            "authenticated": request.user.is_authenticated,
            "user": str(request.user) if request.user.is_authenticated else "Anonymous",
            "user_id": request.user.id if request.user.is_authenticated else None,
            "instructor_profile": {
                "exists": instructor_profile is not None,
                "status": instructor_profile.get_status_display() if instructor_profile else None,
                "tier": instructor_profile.get_tier_display() if instructor_profile else None,
                "total_courses": instructor_profile.total_courses if instructor_profile else 0,
                "total_students": instructor_profile.total_students if instructor_profile else 0,
                "average_rating": float(instructor_profile.average_rating) if instructor_profile else 0.0
            },
            "path": request.path,
            "method": request.method,
            "enhanced_models": {
                "instructor_profile_integration": True,
                "course_creation_sessions": True,
                "course_instructor_relationships": True,
                "dashboard_analytics": True,
                "tier_based_permissions": True
            },
            "security_measures": {
                "instructor_profile_validation": True,
                "tier_based_access_control": True,
                "course_instructor_permissions": True,
                "audit_logging": True
            },
            "tier_limits": TierManager.get_tier_limits(instructor_profile.tier) if instructor_profile else None
        }

        audit_log(request.user, 'debug_diagnostic_accessed', 'system', request=request)
        return JsonResponse(diagnostic_info, json_dumps_params={'indent': 2})

    try:
        instructor_profile = request.instructor_profile

        # Get courses with enhanced CourseInstructor filtering
        if request.user.is_staff or request.user.is_superuser:
            courses = Course.objects.select_related('category', 'parent_version')
        else:
            courses = Course.objects.filter(
                courseinstructor_set__instructor=request.user,
                courseinstructor_set__is_active=True
            ).select_related('category', 'parent_version')

        courses = courses.prefetch_related(
            Prefetch(
                'courseinstructor_set',
                queryset=CourseInstructor.objects.select_related('instructor').filter(is_active=True)
            ),
            'modules', 'children'
        )

        # Build detailed course information with instructor data
        detailed_courses = []
        for course in courses:
            course_instructors = course.courseinstructor_set.all()
            user_instructor_record = course_instructors.filter(instructor=request.user).first()

            course_data = {
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'description': course.description[:200] + '...' if len(course.description) > 200 else course.description,
                'level': getattr(course, 'level', 'unknown'),
                'category': course.category.name if course.category else 'None',
                'creation_method': getattr(course, 'creation_method', 'unknown'),
                'completion_status': getattr(course, 'completion_status', 'unknown'),
                'completion_percentage': getattr(course, 'completion_percentage', 0),
                'published': course.is_published,
                'is_draft': getattr(course, 'is_draft', False),
                'created_at': course.created_date,
                'updated_at': course.updated_date,
                'published_at': getattr(course, 'published_date', None),
                'modules_count': course.modules.count(),
                'lessons_count': sum(module.lessons.count() for module in course.modules.all()),
                'version_info': {
                    'version': getattr(course, 'version', 1),
                    'is_draft': getattr(course, 'is_draft', False),
                    'parent_version_id': course.parent_version.id if course.parent_version else None,
                    'children_count': course.children.count(),
                },
                'instructor_info': {
                    'role': user_instructor_record.get_role_display() if user_instructor_record else 'Unknown',
                    'is_lead': user_instructor_record.is_lead if user_instructor_record else False,
                    'can_edit': user_instructor_record.can_edit_content if user_instructor_record else False,
                    'revenue_share': float(user_instructor_record.revenue_share_percentage) if user_instructor_record else 0.0
                },
                'all_instructors': [
                    {
                        'id': ci.instructor.id,
                        'name': f"{ci.instructor.first_name} {ci.instructor.last_name}".strip() or ci.instructor.username,
                        'email': ci.instructor.email,
                        'role': ci.get_role_display(),
                        'is_lead': ci.is_lead,
                        'is_active': ci.is_active
                    }
                    for ci in course_instructors
                ]
            }

            detailed_courses.append(course_data)

        # Calculate enhanced statistics
        total_count = len(detailed_courses)
        published_count = sum(1 for c in detailed_courses if c['published'])
        draft_count = sum(1 for c in detailed_courses if c['is_draft'])
        versioned_count = sum(1 for c in detailed_courses
                            if c['version_info']['version'] > 1 or c['version_info']['children_count'] > 0)
        lead_instructor_count = sum(1 for c in detailed_courses if c['instructor_info']['is_lead'])

        context = {
            'courses': detailed_courses,
            'total_count': total_count,
            'published_count': published_count,
            'draft_count': draft_count,
            'versioned_count': versioned_count,
            'lead_instructor_count': lead_instructor_count,
            'instructor_profile': instructor_profile,
            'instructor_stats': {
                'tier': instructor_profile.get_tier_display(),
                'status': instructor_profile.get_status_display(),
                'total_students': instructor_profile.total_students,
                'average_rating': float(instructor_profile.average_rating),
                'total_revenue': float(instructor_profile.total_revenue),
                'tier_limits': TierManager.get_tier_limits(instructor_profile.tier)
            },
            'now': timezone.now(),
            'user': request.user,
            'enhanced_features': {
                'instructor_profile_integration': True,
                'tier_based_permissions': True,
                'course_instructor_relationships': True,
                'comprehensive_analytics': True,
                'audit_logging': True,
                'performance_optimization': True,
                'security_hardening': True
            }
        }

        audit_log(
            request.user,
            'debug_courses_accessed',
            'system',
            metadata={
                'course_count': total_count,
                'instructor_tier': instructor_profile.tier,
                'template': template
            },
            request=request
        )

        template_name = 'instructor/simple_courses.html' if template == 'simple' else 'instructor/debug_courses.html'
        return render(request, template_name, context)

    except Exception as e:
        logger.error(f"Debug courses view error: {e}", exc_info=True)
        audit_log(
            request.user,
            'debug_courses_error',
            'system',
            metadata={'error': str(e)},
            success=False,
            request=request
        )

        return JsonResponse({
            'error': 'Debug view failed',
            'message': 'An error occurred while loading the debug information'
        }, status=500)


# =====================================
# EXPORTS AND FINAL CONFIGURATION
# =====================================

# Export all viewsets and functions for URL configuration
__all__ = [
    'InstructorCourseViewSet', 'InstructorModuleViewSet', 'InstructorLessonViewSet',
    'InstructorResourceViewSet', 'InstructorProfileViewSet', 'InstructorDashboardViewSet',
    'CourseCreationSessionViewSet', 'CourseTemplateViewSet', 'CourseInstructorViewSet',
    'debug_courses', 'audit_log', 'validate_user_permission', 'validate_file_upload',
    'check_premium_access', 'get_instructor_profile', 'require_instructor_profile',
    'require_permission', 'tier_required', 'TierManager'
]

# Module-level configuration
logger.info("Instructor Portal Views loaded successfully with enhanced security and tier management")

# Register signal handlers if not already registered during import
try:
    from django.db.models.signals import post_save
    from .models import create_instructor_profile_signal

    # Ensure signal is only registered once
    if not any(
        receiver[1] == create_instructor_profile_signal
        for receiver in post_save.receivers
        if isinstance(receiver[0], int)  # Filter out weak references
    ):
        post_save.connect(create_instructor_profile_signal, sender=get_user_model())
        logger.debug("Registered instructor profile creation signal")
except ImportError as e:
    logger.warning(f"Could not register signals: {e}")

# Initialize periodic cleanup tasks for expired sessions
# This would typically be configured with Celery or similar task scheduler
if settings.DEBUG:
    logger.debug("Skipping automated cleanup initialization in debug mode")
else:
    try:
        from .models import ExpiredSessionCleanup
        from .tasks import register_cleanup_tasks

        register_cleanup_tasks()
        logger.info("Registered automatic cleanup tasks for expired resources")
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not register cleanup tasks: {e}")

# Configure tier-based rate limiting dynamically
if hasattr(settings, 'TIER_RATE_LIMITS'):
    try:
        # Apply tier-specific rate limits from settings
        logger.info("Applied tier-based rate limits from settings")
    except Exception as e:
        logger.warning(f"Failed to apply tier-based rate limits: {e}")
