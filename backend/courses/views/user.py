# User views: Enrollment, progress, notes, assessments
#
# File Path: backend/courses/views/user.py
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
# User-Authenticated Views for Course Management System

import logging
from django.db import transaction
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..models import (
    Course, Enrollment, Progress, Certificate,
    Lesson, Review, Note, AssessmentAttempt
)
from ..serializers import (
    EnrollmentSerializer, ProgressSerializer, CertificateSerializer,
    ReviewSerializer, NoteSerializer, UserProgressStatsSerializer
)
from ..validation import get_unified_user_access_level

from .mixins import (
    StandardContextMixin, SafeFilterMixin, log_operation_safe,
    SecureAPIView, VIEW_CACHE_TIMEOUTS, ConsolidatedPermissionMixin
)

logger = logging.getLogger(__name__)


class EnrollmentViewSet(viewsets.ModelViewSet, StandardContextMixin):
    """Enrollment management with race condition prevention"""

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """User's enrollments with optimization"""
        try:
            return Enrollment.objects.select_related(
                'course__category', 'course'
            ).filter(
                user=self.request.user
            ).order_by('-created_date')
        except Exception as e:
            logger.error(f"Error in EnrollmentViewSet.get_queryset: {e}")
            return Enrollment.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Race-condition-safe enrollment creation using get_or_create"""
        try:
            course = serializer.validated_data['course']

            # Use get_or_create to prevent race conditions
            enrollment, created = Enrollment.objects.get_or_create(
                user=self.request.user,
                course=course,
                defaults={'status': 'active', 'enrolled_date': timezone.now()}
            )

            if not created:
                raise ValidationError("You are already enrolled in this course.")

            # Update analytics safely
            try:
                course.enrolled_students_count = course.enrollments.filter(status='active').count()
                course.save(update_fields=['enrolled_students_count'])
            except Exception as e:
                logger.warning(f"Analytics update failed for course {course.id}: {e}")

            log_operation_safe("Enrollment created", enrollment.id, self.request.user)
            return enrollment

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Enrollment creation error: {e}")
            raise ValidationError("An error occurred during enrollment.")

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def unenroll(self, request, pk=None):
        """Safe unenrollment"""
        try:
            enrollment = self.get_object()

            enrollment.status = 'unenrolled'
            enrollment.completion_date = timezone.now()
            enrollment.save(update_fields=['status', 'completion_date'])

            # Update analytics safely
            try:
                course = enrollment.course
                course.enrolled_students_count = course.enrollments.filter(status='active').count()
                course.save(update_fields=['enrolled_students_count'])
            except Exception as e:
                logger.warning(f"Analytics update failed: {e}")

            log_operation_safe("User unenrolled from course", enrollment.course.id, request.user)
            return Response({'detail': 'Successfully unenrolled from course.'})

        except Exception as e:
            logger.error(f"Unenrollment error: {e}")
            return Response(
                {'error': 'An error occurred during unenrollment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgressViewSet(viewsets.ModelViewSet, StandardContextMixin):
    """Progress tracking viewset with optimization"""
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            return Progress.objects.filter(enrollment__user=self.request.user).select_related(
                'lesson__module__course', 'enrollment'
            )
        except Exception as e:
            logger.error(f"Error in ProgressViewSet.get_queryset: {e}")
            return Progress.objects.none()


class ReviewViewSet(viewsets.ModelViewSet, StandardContextMixin):
    """Course review management with safe analytics"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            return Review.objects.filter(user=self.request.user).select_related('course')
        except Exception as e:
            logger.error(f"Error in ReviewViewSet.get_queryset: {e}")
            return Review.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Safe review creation with analytics update"""
        try:
            review = serializer.save(user=self.request.user)

            # Update analytics safely
            try:
                course = review.course
                course.update_analytics()
            except Exception as e:
                logger.warning(f"Analytics update failed for course {review.course.id}: {e}")

            log_operation_safe("Review created", review.id, self.request.user)
        except Exception as e:
            logger.error(f"Review creation error: {e}")
            raise ValidationError("An error occurred while creating the review.")


class NoteViewSet(viewsets.ModelViewSet, StandardContextMixin, SafeFilterMixin):
    """Student notes management with safe filtering"""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'lesson': 'lesson_id',
        'course': 'lesson__module__course_id',
        'search': lambda qs, val: qs.filter(content__icontains=val),
    }

    def get_queryset(self):
        try:
            return Note.objects.filter(user=self.request.user).select_related(
                'lesson__module__course'
            ).order_by('-created_date')
        except Exception as e:
            logger.error(f"Error in NoteViewSet.get_queryset: {e}")
            return Note.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Safe note creation"""
        try:
            note = serializer.save(user=self.request.user)
            log_operation_safe("Note created", note.id, self.request.user)
        except Exception as e:
            logger.error(f"Note creation error: {e}")
            raise ValidationError("An error occurred while creating the note.")


# Fixed to inherit ConsolidatedPermissionMixin
class CourseEnrollmentView(APIView, ConsolidatedPermissionMixin, StandardContextMixin):
    """
    Standalone course enrollment view to match URL pattern expectations
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={},
        responses={
            201: EnrollmentSerializer,
            400: {'description': 'Bad Request'},
            404: {'description': 'Course not found'}
        }
    )
    @transaction.atomic
    def post(self, request, course_slug):
        """Enroll user in course by slug"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Check course availability
            if not course.is_published:
                # Check if user has special permissions - now using self. since we inherit the mixin
                if not self.has_course_permission(course, request.user):
                    return Response(
                        {'error': 'This course is not available for enrollment.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Atomic enrollment creation - prevents race conditions
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={'status': 'active', 'enrolled_date': timezone.now()}
            )

            if not created:
                return Response(
                    {'error': 'You are already enrolled in this course.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update analytics in same transaction
            try:
                course.enrolled_students_count = course.enrollments.filter(status='active').count()
                course.save(update_fields=['enrolled_students_count'])
            except Exception as e:
                logger.warning(f"Analytics update failed for course {course.id}: {e}")

            log_operation_safe("User enrolled in course", course.id, request.user)

            serializer = EnrollmentSerializer(enrollment, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Enrollment error: {e}")
            return Response(
                {'error': 'An error occurred during enrollment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseProgressView(APIView, StandardContextMixin):
    """
    Course progress view for tracking user progress in a specific course
    """
    permission_classes = [IsAuthenticated]

    # Using method_decorator instead of manually checking cache
    @method_decorator(cache_page(VIEW_CACHE_TIMEOUTS['user']))
    @extend_schema(
        responses={
            200: {'description': 'Course progress data'},
            404: {'description': 'Course or enrollment not found'}
        }
    )
    def get(self, request, course_slug):
        """Get user's progress in a specific course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Check if user is enrolled
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=course)
            except Enrollment.DoesNotExist:
                return Response(
                    {'error': 'You are not enrolled in this course.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get progress data
            progress_records = Progress.objects.filter(
                enrollment=enrollment
            ).select_related('lesson__module')

            total_lessons = Lesson.objects.filter(module__course=course).count()
            completed_lessons = progress_records.filter(is_completed=True).count()

            # Calculate progress percentage
            progress_percentage = 0
            if total_lessons > 0:
                progress_percentage = (completed_lessons / total_lessons) * 100

            # Get current lesson (next incomplete lesson)
            current_lesson = None
            incomplete_progress = progress_records.filter(is_completed=False).first()
            if incomplete_progress:
                current_lesson = {
                    'id': incomplete_progress.lesson.id,
                    'title': incomplete_progress.lesson.title,
                    'module_title': incomplete_progress.lesson.module.title
                }

            progress_data = {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug
                },
                'enrollment': {
                    'id': enrollment.id,
                    'status': enrollment.status,
                    'enrolled_date': enrollment.enrolled_date,
                    'last_accessed': enrollment.last_accessed
                },
                'progress': {
                    'total_lessons': total_lessons,
                    'completed_lessons': completed_lessons,
                    'progress_percentage': round(progress_percentage, 1),
                    'current_lesson': current_lesson,
                    'total_time_spent': enrollment.total_time_spent or 0
                }
            }

            return Response(progress_data)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Course progress error: {e}")
            return Response(
                {'error': 'An error occurred while retrieving course progress'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CertificateViewSet(viewsets.ReadOnlyModelViewSet, StandardContextMixin):
    """Certificate management with enhanced security"""

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Premium user certificates only"""
        try:
            user_access_level = get_unified_user_access_level(self.request.user)
            if user_access_level != 'premium':
                return Certificate.objects.none()

            return Certificate.objects.filter(
                enrollment__user=self.request.user,
                is_valid=True
            ).select_related('enrollment__course').order_by('-created_date')
        except Exception as e:
            logger.error(f"Error in CertificateViewSet.get_queryset: {e}")
            return Certificate.objects.none()


class UserProgressStatsView(APIView):
    """
    API endpoint to retrieve consolidated user progress statistics

    Provides comprehensive statistics on course progress, time spent,
    certificates earned, and other metrics for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Enhanced progress statistics with comprehensive error handling"""
        try:
            user = request.user

            # Build cache key specific to this user
            cache_key = f"user_progress_stats:{user.id}:{timezone.now().date()}"
            cached_stats = cache.get(cache_key)

            if cached_stats:
                return Response(cached_stats)

            # Get all enrollments for the user with optimized query
            enrollments = Enrollment.objects.filter(user=user).select_related('course__category')

            # Calculate core statistics
            total_courses = enrollments.count()
            courses_completed = enrollments.filter(status='completed').count()
            courses_in_progress = enrollments.filter(status='active').count()

            # Get progress records for more detailed stats
            progress_records = Progress.objects.filter(
                enrollment__user=user
            ).select_related('lesson__module', 'enrollment')

            # Calculate lessons statistics with null safety
            total_lessons = progress_records.count()
            completed_lessons = progress_records.filter(is_completed=True).count()
            completion_pct = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

            # Calculate time spent with null safety
            total_seconds = progress_records.aggregate(
                total=Sum('time_spent')
            )['total'] or 0
            hours_spent = round(total_seconds / 3600, 2)

            # Null-safe time calculation from enrollments
            total_time_spent = sum(
                getattr(enrollment, 'total_time_spent', 0) or 0
                for enrollment in enrollments
                if isinstance(getattr(enrollment, 'total_time_spent', 0), (int, float))
            )

            # Get assessment attempts if the model exists
            assessments_completed = 0
            avg_score = 0
            try:
                assessment_attempts = AssessmentAttempt.objects.filter(user=user)
                # Use 'passed' field instead of non-existent 'is_completed'
                assessments_completed = assessment_attempts.filter(passed=True).count()

                # Calculate average scores with null safety
                avg_score_data = assessment_attempts.aggregate(avg=Avg('score'))
                avg_score = avg_score_data['avg'] or 0
            except Exception as e:
                logger.warning(f"Error calculating assessment stats: {e}")

            # Safe certificate count for premium users
            certificates_earned = 0
            try:
                user_access_level = get_unified_user_access_level(user)
                if user_access_level == 'premium':
                    certificates_earned = Certificate.objects.filter(
                        enrollment__user=user, is_valid=True
                    ).count()
            except Exception as e:
                logger.warning(f"Error counting certificates for user {user.id}: {e}")

            # Get recent activity
            recent_activity = []
            try:
                recent_progress = progress_records.filter(
                    is_completed=True
                ).order_by('-completed_date')[:10]

                for progress in recent_progress:
                    try:
                        recent_activity.append({
                            'course': progress.enrollment.course.title,
                            'lesson': progress.lesson.title,
                            'completed_date': progress.completed_date.isoformat() if progress.completed_date else None,
                            'module': progress.lesson.module.title if hasattr(progress.lesson, 'module') and progress.lesson.module else None
                        })
                    except Exception as e:
                        logger.warning(f"Error processing recent activity item: {e}")
            except Exception as e:
                logger.warning(f"Error retrieving recent activity: {e}")

            # Create stats data dict - using standard field names
            stats_data = {
                'totalCourses': total_courses,
                'coursesCompleted': courses_completed,
                'coursesInProgress': courses_in_progress,
                'totalLessons': total_lessons,
                'completedLessons': completed_lessons,
                'completionPercentage': round(completion_pct, 1),
                'hoursSpent': hours_spent,
                'totalTimeSpent': total_time_spent,
                'assessmentsCompleted': assessments_completed,
                'averageScore': round(avg_score, 1),
                'certificatesEarned': certificates_earned,
                'recentActivity': recent_activity,
                'generatedAt': timezone.now()
            }

            # Cache the result for this user
            cache.set(cache_key, stats_data, 60 * 5)  # Cache for 5 minutes

            log_operation_safe("Progress stats retrieved", "user_stats", user)
            return Response(stats_data)

        except Exception as e:
            logger.error(f"Error in UserProgressStatsView: {e}", exc_info=True)
            return Response(
                {'error': 'An error occurred while retrieving progress statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
