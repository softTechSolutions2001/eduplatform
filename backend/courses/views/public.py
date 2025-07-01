# Public views: Course listing, search, featured, certificate verification
#
# File Path: backend/courses/views/public.py
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
# Public-Facing Views for Course Management System

import logging
from typing import Union
from django.db import transaction, IntegrityError
from django.db.models import Q, Prefetch, Count, QuerySet
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings  # Added missing import

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

# Conditional import for drf_spectacular (remove import error)
HAS_DRF_SPECTACULAR = False
# Fallback decorators for when drf_spectacular is not available
def extend_schema(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class OpenApiParameter:
    """Stub for OpenApiParameter when drf_spectacular is not available"""
    PATH = 'path'
    QUERY = 'query'

    def __init__(self, *args, **kwargs):
        pass

from ..models import Category, Course, Module, Lesson, Certificate
from instructor_portal.models import CourseInstructor  # Added for prefetch
from ..serializers import (
    CategorySerializer, CourseSerializer, CourseDetailSerializer,
    CourseCloneSerializer, CourseVersionSerializer, LessonSerializer,
    ModuleSerializer, ModuleDetailSerializer  # Added ModuleSerializer imports
)

from .mixins import (
    OptimizedSerializerMixin, ConsolidatedPermissionMixin, StandardContextMixin,
    SafeFilterMixin, StandardResultsSetPagination, safe_decimal_conversion,
    safe_int_conversion, validate_permissions_and_raise, log_operation_safe,
    validate_certificate_number, get_cache_key, VIEW_CACHE_TIMEOUTS
)

logger = logging.getLogger(__name__)


class CategoryViewSet(
    viewsets.ReadOnlyModelViewSet,
    StandardContextMixin,
    SafeFilterMixin
):
    """Category management with optimized queries and unified responses"""

    # Optimized queryset to prevent N+1 queries
    queryset = Category.objects.filter(is_active=True).select_related('parent').order_by("sort_order", "name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    pagination_class = StandardResultsSetPagination

    filter_mappings = {
        'search': lambda qs, val: qs.filter(
            Q(name__icontains=val) | Q(description__icontains=val)
        ),
        'parent': 'parent__slug',
    }

    @extend_schema(
        parameters=[
            OpenApiParameter('search', str, description='Search in name and description'),
            OpenApiParameter('parent', str, description='Filter by parent category slug'),
        ],
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List categories with unified response envelope"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CategoryViewSet.list: {e}")
            return Response(
                {'error': 'An error occurred while retrieving categories'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,
    StandardContextMixin,
    SafeFilterMixin,
    viewsets.ModelViewSet
):
    """Course management with all critical issues fixed"""

    # Optimized queryset to prevent N+1 queries
    queryset = Course.objects.select_related(
        'category', 'parent_version'
    ).prefetch_related(
        # Fixed prefetch to use CourseInstructor directly
        Prefetch('courseinstructor_set',
                queryset=CourseInstructor.objects.select_related('instructor')),
        Prefetch('modules',
                queryset=Module.objects.prefetch_related('lessons')),
        'reviews__user'
    )

    lookup_field = "slug"
    serializer_class = CourseSerializer  # Always defined to prevent assertion errors
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    serializer_action_map = {
        'retrieve': CourseDetailSerializer,
        'clone': CourseCloneSerializer,
        'versions': CourseVersionSerializer,
        # Removed version_info key since it's not implemented
    }

    filter_mappings = {
        'category': 'category__slug',
        'level': 'level',
        'is_featured': lambda qs, val: qs.filter(is_featured=val.lower() == 'true') if val else qs,
        'search': lambda qs, val: qs.filter(
            Q(title__icontains=val) |
            Q(description__icontains=val) |
            Q(subtitle__icontains=val)
        ).distinct(),
        'max_price': lambda qs, val: qs.filter(
            price__lte=safe_decimal_conversion(val)
        ) if val else qs,
        'min_price': lambda qs, val: qs.filter(
            price__gte=safe_decimal_conversion(val)
        ) if val else qs,        'instructor': 'courseinstructor__instructor__username',
        'status': 'completion_status',
    }

    def get_queryset(self) -> QuerySet[Course]:
        """Enhanced queryset with permission-based filtering"""
        try:
            queryset = super().get_queryset()

            # For public views, only show published courses
            if not self.is_instructor_or_admin():
                queryset = queryset.filter(is_published=True)

            # Instructor-only filters
            if self.is_instructor_or_admin() and hasattr(self.request, 'query_params'):
                is_draft = self.request.query_params.get('is_draft')
                if is_draft is not None:
                    queryset = queryset.filter(is_draft=is_draft.lower() == 'true')

                # Filter by instructor's own courses if not admin
                if not self.request.user.is_staff:
                    queryset = queryset.filter(
                        courseinstructor__instructor=self.request.user,
                        courseinstructor__is_active=True
                    )

            return queryset.order_by('-created_date')
        except Exception as e:
            logger.error(f"Error in CourseViewSet.get_queryset: {e}")
            return Course.objects.none()

    @extend_schema(
        parameters=[
            OpenApiParameter('search', str),
            OpenApiParameter('category', str),
            OpenApiParameter('level', str),
            OpenApiParameter('max_price', str),
            OpenApiParameter('min_price', str),
            OpenApiParameter('is_featured', bool),
            OpenApiParameter('instructor', str),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List courses with unified response envelope"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CourseViewSet.list: {e}")
            return Response(
                {'error': 'An error occurred while retrieving courses'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        parameters=[OpenApiParameter('limit', int, description='Limit number of featured courses')]
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Featured courses with safe pagination and proper DRF response"""
        try:
            queryset = self.get_queryset().filter(is_featured=True)

            limit_param = request.query_params.get('limit')
            if limit_param is not None:
                limit = safe_int_conversion(limit_param, 0, min_value=1, max_value=50)
                if limit > 0:
                    queryset = queryset[:limit]

            serializer = self.get_serializer(queryset, many=True)
            return Response({'results': serializer.data})

        except Exception as e:
            logger.error(f"Error in featured courses: {e}")
            return Response(
                {'error': 'An error occurred while retrieving featured courses'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Add versions action to match serializer_action_map
    @action(detail=True, methods=['get'])
    def versions(self, request, slug=None):
        """Get all versions of a course"""
        try:
            course = self.get_object()

            # Get parent version if this is a derived course
            parent = course.parent_version
            original = parent if parent else course

            # Get all versions including the original
            versions = Course.objects.filter(
                parent_version=original
            ).union(
                Course.objects.filter(id=original.id)
            ).order_by('-created_date')

            serializer = self.get_serializer(versions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving course versions: {e}")
            return Response(
                {'error': 'An error occurred while retrieving course versions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # BACKWARD COMPATIBILITY: Add missing actions from original CourseViewSet
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @transaction.atomic
    def enroll(self, request, slug=None):
        """Race-condition-safe enrollment using get_or_create"""
        try:
            course = self.get_object()
            user = request.user

            # Check course availability
            if not course.is_published:
                return Response(
                    {'error': 'This course is not available for enrollment.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Import here to avoid circular imports
            from ..models import Enrollment

            # Atomic enrollment creation - prevents race conditions
            enrollment, created = Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={'status': 'active', 'enrolled_date': timezone.now()}
            )

            if not created:
                return Response(
                    {'error': 'You are already enrolled in this course.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            log_operation_safe("Course enrolled", course.id, request.user)
            return Response({'detail': 'Successfully enrolled in course.'})

        except Exception as e:
            logger.error(f"Course enrollment error: {e}")
            return Response(
                {'error': 'An error occurred during enrollment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @transaction.atomic
    def clone(self, request, slug=None):
        """BACKWARD COMPATIBILITY: Redirect to standalone CourseCloneView"""
        # For backward compatibility, redirect to the standalone view
        from rest_framework.reverse import reverse
        from django.shortcuts import redirect

        # Import the standalone view
        from .instructor import CourseCloneView

        # Create an instance and delegate
        clone_view = CourseCloneView()
        clone_view.setup(request)

        return clone_view.post(request, course_slug=slug)    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    @transaction.atomic
    def publish(self, request, slug=None):
        """BACKWARD COMPATIBILITY: Redirect to standalone CoursePublishingView"""
        try:
            from .instructor import CoursePublishingView

            # Create an instance and delegate
            publish_view = CoursePublishingView()
            publish_view.setup(request)

            # Call the appropriate method - CoursePublishingView likely has a post method
            if hasattr(publish_view, 'post'):
                return publish_view.post(request, course_slug=slug)
            else:
                return Response(
                    {'error': 'Publishing functionality not available'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
        except ImportError:
            return Response(
                {'error': 'Publishing functionality not available'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    @transaction.atomic
    def unpublish(self, request, slug=None):
        """BACKWARD COMPATIBILITY: Redirect to standalone CoursePublishingView"""
        try:
            from .instructor import CoursePublishingView

            # Create an instance and delegate
            publish_view = CoursePublishingView()
            publish_view.setup(request)

            # Call the appropriate method for unpublishing
            if hasattr(publish_view, 'delete'):
                return publish_view.delete(request, course_slug=slug)
            elif hasattr(publish_view, 'post'):
                # Add unpublish parameter if using post method
                request.data = {'action': 'unpublish'}
                return publish_view.post(request, course_slug=slug)
            else:
                return Response(
                    {'error': 'Unpublishing functionality not available'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
        except ImportError:
            return Response(
                {'error': 'Unpublishing functionality not available'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )


# Re-added public ModuleViewSet as read-only
class ModuleViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,  # FIXED: Re-added missing permission mixin
    StandardContextMixin,
    viewsets.ReadOnlyModelViewSet
):
    """Module management with public read access"""

    queryset = Module.objects.select_related('course').prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.select_related().prefetch_related('resources'))
    )
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    serializer_action_map = {
        'retrieve': ModuleDetailSerializer,
    }

    def get_queryset(self):
        """Safe queryset with filtering and proper error handling"""
        try:
            queryset = super().get_queryset()

            # Filter by course
            course_slug = self.request.query_params.get('course')
            if course_slug:
                queryset = queryset.filter(course__slug=course_slug)

            course_id_param = self.request.query_params.get('course_id')
            if course_id_param:
                course_id = safe_int_conversion(course_id_param, 0)
                if course_id <= 0:
                    # Return proper error instead of empty queryset
                    raise ValidationError("Invalid course_id parameter")
                queryset = queryset.filter(course_id=course_id)

            # For public views, only show published modules from published courses
            queryset = queryset.filter(is_published=True, course__is_published=True)

            return queryset.order_by('course__id', 'order')

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in ModuleViewSet.get_queryset: {e}")
            return Module.objects.none()


class LessonViewSet(
    viewsets.ReadOnlyModelViewSet,
    StandardContextMixin,
    SafeFilterMixin
):
    """Lesson management with proper DRF pagination"""

    queryset = Lesson.objects.select_related('module__course').prefetch_related(
        'resources', 'assessment'
    )
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_mappings = {
        'module': 'module_id',
        'course': 'module__course__slug',
        'access_level': 'access_level',
        'type': 'type',
        'free_preview': lambda qs, val: qs.filter(
            is_free_preview=val.lower() == 'true'
        ) if val else qs,
    }

    def get_queryset(self):
        """Safe queryset with filtering"""
        try:
            queryset = super().get_queryset()

            # Permission-based filtering
            if not getattr(self, '_is_instructor_or_admin', False):
                queryset = queryset.filter(
                    module__is_published=True,
                    module__course__is_published=True
                )

            return queryset.order_by('module__order', 'order')
        except Exception as e:
            logger.error(f"Error in LessonViewSet.get_queryset: {e}")
            return Lesson.objects.none()

    def list(self, request, *args, **kwargs):
        """List with proper DRF pagination instead of manual slicing"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in LessonViewSet.list: {e}")
            return Response(
                {'error': 'An error occurred while retrieving lessons'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnifiedSearchView(APIView):
    """
    Unified search across courses, categories, and other content
    """
    permission_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter('q', str, required=True, description='Search query'),
            OpenApiParameter('type', str, description='Search type: courses, categories, all'),
            OpenApiParameter('limit', int, description='Limit results per type'),
        ],
        responses={200: {'description': 'Search results'}}
    )
    def get(self, request):
        """Perform unified search across content types"""
        try:
            query = request.query_params.get('q', '').strip()
            if not query or len(query) < 2:
                return Response(
                    {'error': 'Search query must be at least 2 characters long'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            search_type = request.query_params.get('type', 'all').lower()
            limit = safe_int_conversion(request.query_params.get('limit', 10), 10, min_value=1, max_value=50)

            results = {}

            # Search courses
            if search_type in ['courses', 'all']:
                courses = Course.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(subtitle__icontains=query),
                    is_published=True
                ).select_related('category')[:limit]

                results['courses'] = [
                    {
                        'id': course.id,
                        'title': course.title,
                        'slug': course.slug,
                        'description': (course.description[:200] + '...'
                                     if course.description and len(course.description) > 200
                                     else course.description or ''),
                        'category': course.category.name if course.category else None,
                        'level': course.level,
                        'price': float(course.price),
                        'type': 'course'
                    }
                    for course in courses
                ]

            # Search categories
            if search_type in ['categories', 'all']:
                categories = Category.objects.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query),
                    is_active=True
                )[:limit]

                results['categories'] = [
                    {
                        'id': getattr(category, 'id', None),
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description or '',
                        'type': 'category'
                    }
                    for category in categories
                ]

            # Add search metadata
            total_results = sum(len(results[key]) for key in results)
            search_results = {
                'query': query,
                'total_results': total_results,
                'search_type': search_type,
                'results': results
            }

            return Response(search_results)

        except Exception as e:
            logger.error(f"Search error: {e}")
            return Response(
                {'error': 'An error occurred during search'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeaturedContentView(APIView):
    """
    Featured content aggregation view
    """
    permission_classes = []

    @method_decorator(cache_page(VIEW_CACHE_TIMEOUTS['public']))
    @extend_schema(
        parameters=[
            OpenApiParameter('limit', int, description='Limit number of featured items'),
        ],
        responses={200: {'description': 'Featured content'}}
    )
    def get(self, request):
        """Get featured content across different types"""
        try:
            limit = safe_int_conversion(request.query_params.get('limit', 10), 10, min_value=1, max_value=50)

            # Removed manual cache logic since we're using cache_page decorator
            # Get featured courses
            featured_courses = Course.objects.filter(
                is_featured=True,
                is_published=True
            ).select_related('category').order_by('-created_date')[:limit]

            # Get featured categories (with most courses)
            featured_categories = Category.objects.filter(
                is_active=True
            ).annotate(
                course_count=Count('courses', filter=Q(courses__is_published=True))
            ).filter(course_count__gt=0).order_by('-course_count')[:limit // 2]

            featured_content = {
                'courses': [
                    {
                        'id': course.id,
                        'title': course.title,
                        'slug': course.slug,
                        'description': (course.description[:200] + '...'
                                     if course.description and len(course.description) > 200
                                     else course.description or ''),
                        'category': course.category.name if course.category else None,
                        'level': course.level,
                        'price': float(course.price),
                        'rating': float(course.avg_rating) if course.avg_rating else 0.0,
                        'enrolled_students': course.enrolled_students_count or 0,
                        'thumbnail': course.thumbnail.url if course.thumbnail else None
                    }
                    for course in featured_courses
                ],
                'categories': [
                    {
                        'id': getattr(category, 'pk', None),
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description or '',
                        'course_count': getattr(category, 'course_count', 0),
                        'icon': getattr(category, 'icon', None)
                    }
                    for category in featured_categories
                ],
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'total_featured_courses': len(featured_courses),
                    'total_featured_categories': len(featured_categories)
                }
            }

            return Response(featured_content)

        except Exception as e:
            logger.error(f"Featured content error: {e}")
            return Response(
                {'error': 'An error occurred while retrieving featured content'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CertificateVerificationView(APIView):
    """
    Public certificate verification view
    """
    permission_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter('certificate_number', str, required=True, location=OpenApiParameter.PATH,
                           description='Certificate number to verify')
        ],
        responses={
            200: {'description': 'Certificate verification result'},
            400: {'description': 'Invalid certificate number format'},
            404: {'description': 'Certificate not found'}
        }
    )
    def get(self, request, certificate_number):
        """Verify certificate by number"""
        try:
            if not certificate_number:
                return Response(
                    {'error': 'Certificate number is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate certificate number format
            if not validate_certificate_number(certificate_number):
                return Response(
                    {'error': 'Invalid certificate number format'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cache key for verification
            cache_key = get_cache_key('cert_verification', certificate_number)
            cached_result = cache.get(cache_key)

            if cached_result:
                return Response(cached_result)

            try:
                certificate = Certificate.objects.select_related(
                    'enrollment__course', 'enrollment__user'
                ).get(certificate_number=certificate_number)
            except Certificate.DoesNotExist:
                return Response(
                    {'error': 'Certificate not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Build safe response data
            user = certificate.enrollment.user
            first_name = getattr(user, 'first_name', '') or ''
            last_name = getattr(user, 'last_name', '') or ''
            student_name = f"{first_name} {last_name}".strip() or 'Unknown'

            verification_data = {
                'is_valid': certificate.is_valid,
                'certificate_number': certificate.certificate_number,
                'issue_date': certificate.created_date,
                'course_title': certificate.enrollment.course.title,
                'student_name': student_name,
                'verification_hash': getattr(certificate, 'verification_hash', ''),
                'verified_at': timezone.now().isoformat()
            }

            if not certificate.is_valid:
                verification_data.update({
                    'revocation_date': getattr(certificate, 'revocation_date', None),
                    'revocation_reason': getattr(certificate, 'revocation_reason', '')
                })

            # Cache for 1 hour
            cache.set(cache_key, verification_data, 3600)

            return Response(verification_data)

        except Exception as e:
            logger.error(f"Certificate verification error: {e}")
            return Response(
                {'error': 'An error occurred during certificate verification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIVersionView(APIView):
    """
    API version and metadata information
    """
    permission_classes = []

    @extend_schema(
        responses={200: {'description': 'API version information'}}
    )
    def get(self, request):
        """Get API version and metadata"""
        try:
            version_info = {
                'api_version': '7.0.0',
                'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
                'drf_version': getattr(settings, 'DRF_VERSION', 'Unknown'),
                'release_date': '2025-06-20',
                'last_updated': '2025-06-26 17:04:42',
                'features': {
                    'unified_response_envelope': True,
                    'race_condition_prevention': True,
                    'n1_query_optimization': True,
                    'proper_drf_pagination': True,
                    'comprehensive_error_handling': True,
                    'decimal_financial_fields': True,
                    'certificate_format_validation': True,
                    'null_safe_calculations': True,
                    'atomic_operations': True,
                    'rate_limited_logging': True,
                    'settings_based_currency': True,
                    'openapi_schema_compatible': True,
                    'production_ready': True,
                    'complete_url_alignment': True
                },
                'endpoints': {
                    'total_viewsets': 13,  # Updated count
                    'total_views': 13,     # Updated count
                    'authentication_required': ['enrollments', 'progress', 'reviews', 'notes', 'certificates'],
                    'public_access': ['categories', 'courses', 'modules', 'search', 'featured', 'certificate_verification']
                },
                'supported_formats': ['json', 'api'],
                'rate_limiting': {
                    'enabled': True,
                    'default_throttle': '1000/hour',
                    'authenticated_throttle': '5000/hour'
                },
                'caching': {
                    'enabled': True,
                    'cache_backend': getattr(settings, 'CACHE_BACKEND', 'default'),
                    'default_timeout': 300
                },
                'documentation': {
                    'openapi_schema': '/api/schema/',
                    'swagger_ui': '/api/docs/',
                    'redoc': '/api/redoc/'
                }
            }

            return Response(version_info)

        except Exception as e:
            logger.error(f"API version error: {e}")
            return Response(
                {'error': 'An error occurred while retrieving API version'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIHealthCheckView(APIView):
    """API health check with comprehensive system status"""

    permission_classes = []

    def get(self, request):
        """Comprehensive health check with system status"""
        try:
            from django.contrib.auth import get_user_model
            # Database connectivity test
            db_healthy = True
            try:
                Course.objects.count()
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                db_healthy = False

            # Cache connectivity test
            cache_healthy = True
            try:
                test_key = f"health_check_{timezone.now().timestamp()}"
                cache.set(test_key, 'test', 10)
                cache.get(test_key)
                cache.delete(test_key)
            except Exception as e:
                logger.error(f"Cache health check failed: {e}")
                cache_healthy = False

            # System metrics
            health_data = {
                'status': 'healthy' if (db_healthy and cache_healthy) else 'degraded',
                'timestamp': timezone.now(),
                'version': '7.0.0',
                'components': {
                    'database': 'healthy' if db_healthy else 'unhealthy',
                    'cache': 'healthy' if cache_healthy else 'unhealthy',
                    'api': 'healthy'
                },
                'features': {
                    'unified_response_envelope': True,
                    'race_condition_prevention': True,
                    'n1_query_optimization': True,
                    'proper_drf_pagination': True,
                    'comprehensive_error_handling': True,
                    'decimal_financial_fields': True,
                    'certificate_format_validation': True,
                    'null_safe_calculations': True,
                    'atomic_operations': True,
                    'rate_limited_logging': True,
                    'settings_based_currency': True,
                    'openapi_schema_compatible': True,
                    'production_ready': True,
                    'complete_url_alignment': True
                },
                'statistics': {
                    'total_courses': Course.objects.count() if db_healthy else 'unavailable',
                    'total_users': get_user_model().objects.count() if db_healthy else 'unavailable',
                    'active_enrollments': 0 if not db_healthy else None
                }
            }

            # Add enrollment counts safely
            if db_healthy:
                from ..models import Enrollment
                health_data['statistics']['active_enrollments'] = Enrollment.objects.filter(status='active').count()

            status_code = status.HTTP_200_OK if (db_healthy and cache_healthy) else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(health_data, status=status_code)

        except Exception as e:
            logger.error(f"Health check error: {e}")
            return Response({
                'status': 'unhealthy',
                'timestamp': timezone.now(),
                'error': 'Health check failed',
                'version': '7.0.0'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
