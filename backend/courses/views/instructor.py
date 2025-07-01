# Instructor views: dashboard, analytics, DnD draft views
#
# File Path: backend/courses/views/instructor.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 13:28:03
# Date Revised: 2025-06-26 17:16:34
# Current Date and Time (UTC): 2025-06-26 17:16:34
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 17:16:34 UTC
# User: softTechSolutions2001
# Version: 7.0.0
#
# Instructor-Related Views for Course Management System

import logging
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch, Avg, Count, Q, Sum

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..models import (
    Course, Module, Lesson, Progress, Enrollment
)
from ..serializers import (
    ModuleSerializer, ModuleDetailSerializer, CourseCloneSerializer,
    CourseDetailSerializer
)

from .mixins import (
    OptimizedSerializerMixin, ConsolidatedPermissionMixin, StandardContextMixin,
    validate_permissions_and_raise, log_operation_safe, SensitiveAPIThrottle
)

logger = logging.getLogger(__name__)


# Renamed to InstructorModuleViewSet to avoid collision with public ModuleViewSet
class InstructorModuleViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,
    StandardContextMixin,
    viewsets.ModelViewSet
):
    """Module management with optimized queries and error handling - Instructor version"""

    queryset = Module.objects.select_related('course').prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.select_related().prefetch_related('resources'))
    )
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

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
                from .mixins import safe_int_conversion
                course_id = safe_int_conversion(course_id_param, 0)
                if course_id <= 0:
                    # Return proper error instead of empty queryset
                    raise ValidationError("Invalid course_id parameter")
                queryset = queryset.filter(course_id=course_id)

            # For instructor views, filter by instructor's courses
            if not self.is_instructor_or_admin():
                return Module.objects.none()

            # If user is not staff/admin, filter to only show modules from their courses
            if not self.request.user.is_staff:
                queryset = queryset.filter(
                    course__courseinstructor__instructor=self.request.user,
                    course__courseinstructor__is_active=True
                )

            return queryset.order_by('course__id', 'order')

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in InstructorModuleViewSet.get_queryset: {e}")
            return Module.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Safe module creation"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Verify permissions
            course = serializer.validated_data.get('course')
            if course and not self.has_course_permission(course):
                return Response(
                    {'error': 'You do not have permission to add modules to this course.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            module = serializer.save()
            log_operation_safe("Module created", module.id, request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Module creation error: {e}")
            return Response(
                {'error': 'An error occurred while creating the module.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorDashboardView(APIView, ConsolidatedPermissionMixin, StandardContextMixin):
    """
    Instructor dashboard with analytics and course management
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

    @extend_schema(
        responses={
            200: {'description': 'Instructor dashboard data'},
            403: {'description': 'Permission denied - instructor access required'}
        }
    )
    def get(self, request):
        """Get instructor dashboard data"""
        try:
            if not self.is_instructor_or_admin(request.user):
                return Response(
                    {'error': 'Instructor access required'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get instructor's courses
            instructor_courses = Course.objects.filter(
                courseinstructor__instructor=request.user,
                courseinstructor__is_active=True
            ).select_related('category').prefetch_related('enrollments')

            # Calculate analytics
            total_courses = instructor_courses.count()
            total_students = sum(
                course.enrollments.filter(status='active').count()
                for course in instructor_courses
            )

            # Revenue calculation (simplified)
            total_revenue = sum(
                course.enrollments.filter(status__in=['active', 'completed']).count() * float(course.price)
                for course in instructor_courses
            )

            # Recent activity
            recent_enrollments = Enrollment.objects.filter(
                course__in=instructor_courses
            ).select_related('user', 'course').order_by('-created_date')[:10]

            # Course performance
            course_stats = []
            for course in instructor_courses[:10]:  # Limit to top 10 courses
                enrollments = course.enrollments.filter(status='active').count()
                rating = float(course.avg_rating) if course.avg_rating else 0.0

                course_stats.append({
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'enrollments': enrollments,
                    'rating': rating,
                    'revenue': enrollments * float(course.price),
                    'status': 'published' if course.is_published else 'draft'
                })

            dashboard_data = {
                'overview': {
                    'total_courses': total_courses,
                    'total_students': total_students,
                    'total_revenue': total_revenue,
                    'avg_rating': float(instructor_courses.aggregate(
                        avg_rating=Avg('avg_rating')
                    )['avg_rating'] or 0)
                },
                'recent_enrollments': [
                    {
                        'id': enrollment.id,
                        'student_name': f"{enrollment.user.first_name} {enrollment.user.last_name}".strip() or enrollment.user.username,
                        'course_title': enrollment.course.title,
                        'enrolled_date': enrollment.enrolled_date
                    }
                    for enrollment in recent_enrollments
                ],
                'course_performance': course_stats,
                'generated_at': timezone.now().isoformat()
            }

            return Response(dashboard_data)

        except Exception as e:
            logger.error(f"Instructor dashboard error: {e}")
            return Response(
                {'error': 'An error occurred while loading dashboard'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseAnalyticsView(APIView, ConsolidatedPermissionMixin, StandardContextMixin):
    """
    Detailed course analytics for instructors
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

    @extend_schema(
        parameters=[
            OpenApiParameter('course_slug', str, required=True, location=OpenApiParameter.PATH,
                           description='Course slug')
        ],
        responses={
            200: {'description': 'Course analytics data'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Course not found'}
        }
    )
    def get(self, request, course_slug):
        """Get detailed analytics for a specific course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Check permissions
            if not self.has_course_permission(course, request.user):
                return Response(
                    {'error': 'You do not have permission to view analytics for this course'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Enrollment analytics
            enrollments = course.enrollments.all()
            enrollment_stats = {
                'total_enrolled': enrollments.count(),
                'active_students': enrollments.filter(status='active').count(),
                'completed_students': enrollments.filter(status='completed').count(),
                'dropped_students': enrollments.filter(status='dropped').count()
            }

            # Progress analytics
            all_lessons = Lesson.objects.filter(module__course=course).count()
            if all_lessons > 0:
                progress_records = Progress.objects.filter(
                    enrollment__course=course
                ).aggregate(
                    avg_progress=Avg('progress_percentage'),
                    total_time=Sum('time_spent')
                )

                completion_rate = (enrollment_stats['completed_students'] / enrollment_stats['total_enrolled'] * 100) if enrollment_stats['total_enrolled'] > 0 else 0
            else:
                progress_records = {'avg_progress': 0, 'total_time': 0}
                completion_rate = 0

            # Revenue analytics
            revenue_data = {
                'total_revenue': enrollment_stats['total_enrolled'] * float(course.price),
                'avg_revenue_per_student': float(course.price),
                'potential_revenue': (enrollment_stats['active_students'] + enrollment_stats['completed_students']) * float(course.price)
            }

            # Review analytics
            reviews = course.reviews.filter(is_approved=True)
            review_stats = {
                'total_reviews': reviews.count(),
                'avg_rating': float(course.avg_rating) if course.avg_rating else 0.0,
                'rating_distribution': {}
            }

            # Calculate rating distribution
            for rating in [1, 2, 3, 4, 5]:
                count = reviews.filter(rating=rating).count()
                review_stats['rating_distribution'][str(rating)] = count

            analytics_data = {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'created_date': course.created_date,
                    'published_date': course.published_date
                },
                'enrollment_analytics': enrollment_stats,
                'progress_analytics': {
                    'avg_progress_percentage': round(progress_records['avg_progress'] or 0, 1),
                    'completion_rate': round(completion_rate, 1),
                    'total_study_time_hours': round((progress_records['total_time'] or 0) / 3600, 1)
                },
                'revenue_analytics': revenue_data,
                'review_analytics': review_stats,
                'generated_at': timezone.now().isoformat()
            }

            return Response(analytics_data)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Course analytics error: {e}")
            return Response(
                {'error': 'An error occurred while generating analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CoursePublishingView(APIView, ConsolidatedPermissionMixin):
    """
    Course publishing controls for instructors
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

    @transaction.atomic
    @extend_schema(
        responses={
            200: {'description': 'Course published successfully'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Course not found'}
        }
    )
    def post(self, request, course_slug):
        """Publish a course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                self.has_course_permission(course),
                "You do not have permission to publish this course."
            )

            # Atomic publish operation
            course.is_published = True
            course.is_draft = False
            course.completion_status = 'published'
            course.completion_percentage = 100
            course.published_date = timezone.now()
            course.save(update_fields=['is_published', 'is_draft', 'completion_status',
                                     'completion_percentage', 'published_date'])

            log_operation_safe("Course published", course.id, request.user)

            return Response({
                'detail': 'Course published successfully.',
                'course_id': course.id,
                'course_slug': course.slug,
                'published_date': course.published_date
            })

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Course publishing error: {e}")
            return Response(
                {'error': 'An error occurred while publishing the course.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    @extend_schema(
        responses={
            200: {'description': 'Course unpublished successfully'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Course not found'}
        }
    )
    def delete(self, request, course_slug):
        """Unpublish a course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                self.has_course_permission(course),
                "You do not have permission to unpublish this course."
            )

            # Atomic unpublish operation
            course.is_published = False
            course.is_draft = True
            course.completion_status = 'complete'
            course.save(update_fields=['is_published', 'is_draft', 'completion_status'])

            log_operation_safe("Course unpublished", course.id, request.user)

            return Response({
                'detail': 'Course unpublished successfully.',
                'course_id': course.id,
                'course_slug': course.slug
            })

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Course unpublishing error: {e}")
            return Response(
                {'error': 'An error occurred while unpublishing the course.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseCloneView(APIView, ConsolidatedPermissionMixin, StandardContextMixin):
    """
    Clone an existing course
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

    @transaction.atomic
    @extend_schema(
        request=CourseCloneSerializer,
        responses={
            201: CourseDetailSerializer,
            403: {'description': 'Permission denied'},
            404: {'description': 'Course not found'},
            409: {'description': 'Clone operation failed due to data conflict'}
        }
    )
    def post(self, request, course_slug):
        """Clone a course"""
        try:
            source_course = get_object_or_404(Course, slug=course_slug)

            validate_permissions_and_raise(
                request.user,
                self.has_course_permission(source_course),
                "You do not have permission to clone this course."
            )

            # Validate and sanitize clone options
            serializer = CourseCloneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            clone_options = {
                'copy_modules': serializer.validated_data.get('copy_modules', True),
                'copy_resources': serializer.validated_data.get('copy_resources', True),
                'copy_assessments': serializer.validated_data.get('copy_assessments', True),
                'create_as_draft': serializer.validated_data.get('create_as_draft', True),
            }

            # Set current user as creator
            cloned_course = source_course.clone_version(request.user, **clone_options)

            # Handle custom title
            new_title = serializer.validated_data.get('title')
            if new_title and isinstance(new_title, str) and new_title.strip():
                cloned_course.title = new_title.strip()[:200]  # Respect max_length
                cloned_course.save(update_fields=['title'])

            log_operation_safe("Course cloned", f"{source_course.id} -> {cloned_course.id}", request.user)

            response_serializer = CourseDetailSerializer(
                cloned_course, context=self.get_serializer_context()
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as e:
            logger.error(f"Course clone integrity error: {e}")
            return Response(
                {'error': 'Clone operation failed due to data conflict. Please try again.'},
                status=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            logger.error(f"Course cloning error: {e}")
            return Response(
                {'error': 'An error occurred while cloning the course.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
