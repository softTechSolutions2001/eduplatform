# User views: Enrollment, progress, notes, assessments
#
# File Path: backend/courses/views/user.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 13:28:03
# Date Revised: 2025-07-09 04:31:31
# Current Date and Time (UTC): 2025-07-09 04:31:31
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 04:31:31 UTC
# User: MohithaSanthanam2010
# Version: 7.1.0
#
# User-Authenticated Views for Course Management System
#
# Version 7.1.0 Changes:
# - FIXED 🔴: Unenroll now properly revokes premium certificates
# - FIXED 🔴: Cache key includes activity hash to prevent timing issues
# - ENHANCED: Better transaction management and error handling
# - ADDED: Proper certificate invalidation on unenrollment

import hashlib
import logging

from courses.serializers.utils import ProgressStatsSerializer
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Max, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from ..models import (
    AssessmentAttempt,
    Certificate,
    Course,
    Enrollment,
    Lesson,
    Note,
    Progress,
    Review,
)
from ..serializers import (
    CertificateSerializer,
    EnrollmentSerializer,
    NoteSerializer,
    ProgressSerializer,
    ReviewSerializer,
    UserProgressStatsSerializer,
)
from ..validation import get_unified_user_access_level
from .mixins import (
    VIEW_CACHE_TIMEOUTS,
    ConsolidatedPermissionMixin,
    SafeFilterMixin,
    SafeUserQuerysetMixin,
    SecureAPIView,
    StandardContextMixin,
    log_operation_safe,
)

logger = logging.getLogger(__name__)

# Update EnrollmentViewSet definition and get_queryset method


class EnrollmentViewSet(
    SafeUserQuerysetMixin, viewsets.ModelViewSet, StandardContextMixin
):
    """Enrollment management with race condition prevention and schema compatibility"""

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """User's enrollments with schema-compatible filtering"""
        try:
            base_queryset = Enrollment.objects.select_related(
                "course__category", "course"
            ).order_by("-created_date")
            return self._safe_user_filter(base_queryset)
        except Exception as e:
            logger.error(f"Error in EnrollmentViewSet.get_queryset: {e}")
            return Enrollment.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Race-condition-safe enrollment creation using get_or_create"""
        try:
            course = serializer.validated_data["course"]

            # Use get_or_create to prevent race conditions
            enrollment, created = Enrollment.objects.get_or_create(
                user=self.request.user,
                course=course,
                defaults={"status": "active", "enrolled_date": timezone.now()},
            )

            if not created:
                raise ValidationError("You are already enrolled in this course.")

            # Update analytics safely
            try:
                course.enrolled_students_count = course.enrollments.filter(
                    status="active"
                ).count()
                course.save(update_fields=["enrolled_students_count"])
            except Exception as e:
                logger.warning(f"Analytics update failed for course {course.id}: {e}")

            log_operation_safe("Enrollment created", enrollment.id, self.request.user)
            return enrollment

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Enrollment creation error: {e}")
            raise ValidationError("An error occurred during enrollment.")

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def unenroll(self, request, pk=None):
        """
        Safe unenrollment with certificate revocation
        FIXED: Now properly revokes premium certificates
        """
        try:
            enrollment = self.get_object()

            # FIXED: Revoke premium certificates on unenrollment
            user_access_level = get_unified_user_access_level(request.user)
            if user_access_level == "premium":
                # Invalidate any certificates for this enrollment
                Certificate.objects.filter(enrollment=enrollment, is_valid=True).update(
                    is_valid=False,
                    revocation_date=timezone.now(),
                    revocation_reason="User unenrolled from course",
                )

            enrollment.status = "unenrolled"
            enrollment.completion_date = timezone.now()
            enrollment.save(update_fields=["status", "completion_date"])

            # Update analytics safely
            try:
                course = enrollment.course
                course.enrolled_students_count = course.enrollments.filter(
                    status="active"
                ).count()
                course.save(update_fields=["enrolled_students_count"])
            except Exception as e:
                logger.warning(f"Analytics update failed: {e}")

            log_operation_safe(
                "User unenrolled from course", enrollment.course.id, request.user
            )
            return Response(
                {
                    "detail": "Successfully unenrolled from course. Any certificates have been revoked."
                }
            )

        except Exception as e:
            logger.error(f"Unenrollment error: {e}")
            return Response(
                {"error": "An error occurred during unenrollment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Update ProgressViewSet definition and get_queryset method


class ProgressViewSet(
    SafeUserQuerysetMixin, viewsets.ModelViewSet, StandardContextMixin
):
    """Progress tracking viewset with schema compatibility"""

    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Schema-compatible queryset filtering"""
        try:
            base_queryset = Progress.objects.select_related(
                "lesson__module__course", "enrollment"
            )
            return self._safe_user_filter(base_queryset, user_field="enrollment__user")
        except Exception as e:
            logger.error(f"Error in ProgressViewSet.get_queryset: {e}")
            return Progress.objects.none()


# Update ReviewViewSet definition and get_queryset method


class ReviewViewSet(SafeUserQuerysetMixin, viewsets.ModelViewSet, StandardContextMixin):
    """Course review management with schema compatibility"""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Schema-compatible queryset filtering"""
        try:
            base_queryset = Review.objects.select_related("course")
            return self._safe_user_filter(base_queryset)
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
                logger.warning(
                    f"Analytics update failed for course {review.course.id}: {e}"
                )

            log_operation_safe("Review created", review.id, self.request.user)
        except Exception as e:
            logger.error(f"Review creation error: {e}")
            raise ValidationError("An error occurred while creating the review.")


# Update NoteViewSet definition and get_queryset method


class NoteViewSet(
    SafeUserQuerysetMixin, viewsets.ModelViewSet, StandardContextMixin, SafeFilterMixin
):
    """Student notes management with schema compatibility"""

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        "lesson": "lesson_id",
        "course": "lesson__module__course_id",
        "search": lambda qs, val: qs.filter(content__icontains=val),
    }

    def get_queryset(self):
        """Schema-compatible queryset filtering"""
        try:
            base_queryset = Note.objects.select_related(
                "lesson__module__course"
            ).order_by("-created_date")
            return self._safe_user_filter(base_queryset)
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


class CourseEnrollmentView(APIView, ConsolidatedPermissionMixin, StandardContextMixin):
    """
    Standalone course enrollment view to match URL pattern expectations
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={},
        responses={
            201: EnrollmentSerializer,
            400: {"description": "Bad Request"},
            404: {"description": "Course not found"},
        },
    )
    @transaction.atomic
    def post(self, request, course_slug):
        """Enroll user in course by slug"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Check course availability
            if not course.is_published:
                if not self.has_course_permission(course, request.user):
                    return Response(
                        {"error": "This course is not available for enrollment."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Atomic enrollment creation - prevents race conditions
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={"status": "active", "enrolled_date": timezone.now()},
            )

            if not created:
                return Response(
                    {"error": "You are already enrolled in this course."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update analytics in same transaction
            try:
                course.enrolled_students_count = course.enrollments.filter(
                    status="active"
                ).count()
                course.save(update_fields=["enrolled_students_count"])
            except Exception as e:
                logger.warning(f"Analytics update failed for course {course.id}: {e}")

            log_operation_safe("User enrolled in course", course.id, request.user)

            serializer = EnrollmentSerializer(
                enrollment, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Enrollment error: {e}")
            return Response(
                {"error": "An error occurred during enrollment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CourseProgressView(APIView, StandardContextMixin):
    """
    Course progress view for tracking user progress in a specific course
    FIXED: Cache key now includes activity hash to prevent timing issues
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {"description": "Course progress data"},
            404: {"description": "Course or enrollment not found"},
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
                    {"error": "You are not enrolled in this course."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # FIXED: Build cache key with activity hash to prevent timing issues
            last_activity = Progress.objects.filter(enrollment=enrollment).aggregate(
                max_updated=Max("updated_date")
            )["max_updated"]

            activity_hash = ""
            if last_activity:
                activity_hash = hashlib.md5(
                    f"{enrollment.id}_{last_activity}".encode()
                ).hexdigest()[:8]

            cache_key = f"course_progress:{request.user.id}:{course.id}:{activity_hash}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data)

            # Get progress data
            progress_records = Progress.objects.filter(
                enrollment=enrollment
            ).select_related("lesson__module")

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
                    "id": incomplete_progress.lesson.id,
                    "title": incomplete_progress.lesson.title,
                    "module_title": incomplete_progress.lesson.module.title,
                }

            progress_data = {
                "course": {"id": course.id, "title": course.title, "slug": course.slug},
                "enrollment": {
                    "id": enrollment.id,
                    "status": enrollment.status,
                    "enrolled_date": enrollment.enrolled_date,
                    "last_accessed": enrollment.last_accessed,
                },
                "progress": {
                    "total_lessons": total_lessons,
                    "completed_lessons": completed_lessons,
                    "progress_percentage": round(progress_percentage, 1),
                    "current_lesson": current_lesson,
                    "total_time_spent": enrollment.total_time_spent or 0,
                },
            }

            # Cache for 5 minutes
            cache.set(cache_key, progress_data, 300)

            return Response(progress_data)

        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Course progress error: {e}")
            return Response(
                {"error": "An error occurred while retrieving course progress"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Update CertificateViewSet definition and get_queryset method


class CertificateViewSet(
    SafeUserQuerysetMixin, viewsets.ReadOnlyModelViewSet, StandardContextMixin
):
    """Certificate management with schema compatibility"""

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Schema-compatible premium user certificates"""
        try:
            user = getattr(self.request, "user", None)
            if not user or not getattr(user, "is_authenticated", False):
                return Certificate.objects.none()

            user_access_level = get_unified_user_access_level(user)
            if user_access_level != "premium":
                return Certificate.objects.none()

            base_queryset = (
                Certificate.objects.filter(is_valid=True)
                .select_related("enrollment__course")
                .order_by("-created_date")
            )
            return self._safe_user_filter(base_queryset, user_field="enrollment__user")
        except Exception as e:
            logger.error(f"Error in CertificateViewSet.get_queryset: {e}")
            return Certificate.objects.none()


class UserProgressStatsView(APIView):
    """
    API endpoint to retrieve consolidated user progress statistics
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProgressStatsSerializer  # Add this line

    # Add this method to use a unique operation_id
    @extend_schema(
        operation_id="user_progress_stats_detailed",
        responses={200: "User progress statistics"},
    )
    def get(self, request, *args, **kwargs):
        """Enhanced progress statistics with improved caching"""
        try:
            user = request.user

            # FIXED: Build cache key with activity hash
            last_progress_update = Progress.objects.filter(
                enrollment__user=user
            ).aggregate(max_updated=Max("updated_date"))["max_updated"]

            activity_hash = ""
            if last_progress_update:
                activity_hash = hashlib.md5(
                    f"{user.id}_{last_progress_update}".encode()
                ).hexdigest()[:8]

            cache_key = (
                f"user_progress_stats:{user.id}:{timezone.now().date()}:{activity_hash}"
            )
            cached_stats = cache.get(cache_key)

            if cached_stats:
                return Response(cached_stats)

            # Get all enrollments for the user with optimized query
            enrollments = Enrollment.objects.filter(user=user).select_related(
                "course__category"
            )

            # Calculate core statistics
            total_courses = enrollments.count()
            courses_completed = enrollments.filter(status="completed").count()
            courses_in_progress = enrollments.filter(status="active").count()

            # Get progress records for more detailed stats
            progress_records = Progress.objects.filter(
                enrollment__user=user
            ).select_related("lesson__module", "enrollment")

            # Calculate lessons statistics with null safety
            total_lessons = progress_records.count()
            completed_lessons = progress_records.filter(is_completed=True).count()
            completion_pct = (
                (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            )

            # Calculate time spent with null safety
            total_seconds = (
                progress_records.aggregate(total=Sum("time_spent"))["total"] or 0
            )
            hours_spent = round(total_seconds / 3600, 2)

            # Null-safe time calculation from enrollments
            total_time_spent = sum(
                getattr(enrollment, "total_time_spent", 0) or 0
                for enrollment in enrollments
                if isinstance(getattr(enrollment, "total_time_spent", 0), (int, float))
            )

            # Get assessment attempts if the model exists
            assessments_completed = 0
            avg_score = 0
            try:
                assessment_attempts = AssessmentAttempt.objects.filter(user=user)
                assessments_completed = assessment_attempts.filter(passed=True).count()

                # Calculate average scores with null safety
                avg_score_data = assessment_attempts.aggregate(avg=Avg("score"))
                avg_score = avg_score_data["avg"] or 0
            except Exception as e:
                logger.warning(f"Error calculating assessment stats: {e}")

            # Safe certificate count for premium users
            certificates_earned = 0
            try:
                user_access_level = get_unified_user_access_level(user)
                if user_access_level == "premium":
                    certificates_earned = Certificate.objects.filter(
                        enrollment__user=user, is_valid=True
                    ).count()
            except Exception as e:
                logger.warning(f"Error counting certificates for user {user.id}: {e}")

            # Get recent activity
            recent_activity = []
            try:
                recent_progress = progress_records.filter(is_completed=True).order_by(
                    "-completed_date"
                )[:10]

                for progress in recent_progress:
                    try:
                        recent_activity.append(
                            {
                                "course": progress.enrollment.course.title,
                                "lesson": progress.lesson.title,
                                "completed_date": (
                                    progress.completed_date.isoformat()
                                    if progress.completed_date
                                    else None
                                ),
                                "module": (
                                    progress.lesson.module.title
                                    if hasattr(progress.lesson, "module")
                                    and progress.lesson.module
                                    else None
                                ),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Error processing recent activity item: {e}")
            except Exception as e:
                logger.warning(f"Error retrieving recent activity: {e}")

            # Create stats data dict
            stats_data = {
                "totalCourses": total_courses,
                "coursesCompleted": courses_completed,
                "coursesInProgress": courses_in_progress,
                "totalLessons": total_lessons,
                "completedLessons": completed_lessons,
                "completionPercentage": round(completion_pct, 1),
                "hoursSpent": hours_spent,
                "totalTimeSpent": total_time_spent,
                "assessmentsCompleted": assessments_completed,
                "averageScore": round(avg_score, 1),
                "certificatesEarned": certificates_earned,
                "recentActivity": recent_activity,
                "generatedAt": timezone.now(),
            }

            # Cache the result for this user (5 minutes)
            cache.set(cache_key, stats_data, 300)

            log_operation_safe("Progress stats retrieved", "user_stats", user)
            return Response(stats_data)

        except Exception as e:
            logger.error(f"Error in UserProgressStatsView: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred while retrieving progress statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LegacyUserProgressStatsView(UserProgressStatsView):
    """Legacy endpoint with same functionality but different operation ID"""

    @extend_schema(
        operation_id="user_progress_stats_legacy",
        responses={200: ProgressStatsSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
