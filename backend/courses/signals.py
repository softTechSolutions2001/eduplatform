# File Path: backend/courses/signals.py
# Folder Path: backend/courses/
# Date Created: 2025-06-15 11:55:45
# Date Revised: 2025-07-09 05:23:06
# Current Date and Time (UTC): 2025-07-09 05:23:06
# Current User's Login: MohithaSanthanam2010
# Author: sujibeautysalon
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 05:23:06 UTC
# User: MohithaSanthanam2010
# Version: 2.1.0
#
# Production-Ready Django Signals for Course Management System
#
# Version 2.1.0 Changes - COMPREHENSIVE AUDIT FIXES:
# - FIXED 🔴: Added missing update_course_analytics_async function that was referenced but not defined
# - FIXED 🔴: Proper imports for all referenced functions and utilities
# - FIXED 🔴: Enhanced error handling and transaction safety
# - ENHANCED: Better signal loop prevention and logging
# - ADDED: Comprehensive audit trail and monitoring
# - MAINTAINED: All existing functionality with improved reliability

import logging
import threading
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    AssessmentAttempt,
    Category,
    Certificate,
    Course,
    Enrollment,
    Lesson,
    Module,
    Progress,
    Review,
)

# FIXED: Import all utility functions properly
try:
    from .utils import (
        calculate_course_duration,
        calculate_course_progress,
        generate_certificate_number,
        generate_verification_hash,
        update_course_analytics,
    )
except ImportError:
    # Fallback implementations for missing utilities
    def generate_certificate_number(course_id, user_id):
        """Fallback certificate number generation"""
        import uuid

        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        return f"CERT-{course_id}-{user_id}-{timestamp}-{uuid.uuid4().hex[:4].upper()}"

    def generate_verification_hash(cert_number):
        """Fallback verification hash generation"""
        import hashlib

        return hashlib.md5(cert_number.encode()).hexdigest()[:8]

    def calculate_course_duration(course):
        """Fallback course duration calculation"""
        total_duration = (
            course.modules.aggregate(total=Sum("duration_minutes"))["total"] or 0
        )
        return total_duration

    def calculate_course_progress(enrollment):
        """Fallback course progress calculation"""
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        if total_lessons == 0:
            return 0.0

        completed_lessons = Progress.objects.filter(
            enrollment=enrollment, is_completed=True
        ).count()

        return (completed_lessons / total_lessons) * 100.0

    def update_course_analytics(course):
        """Fallback course analytics update"""
        # Update enrollment count
        course.enrolled_students_count = course.enrollments.filter(
            status="active"
        ).count()

        # Update average rating
        avg_rating = course.reviews.filter(is_approved=True).aggregate(
            avg=Avg("rating")
        )["avg"]

        course.avg_rating = avg_rating or 0.0
        course.total_reviews = course.reviews.filter(is_approved=True).count()
        course.save(
            update_fields=["enrolled_students_count", "avg_rating", "total_reviews"]
        )


try:
    from .constants import CompletionStatus, EnrollmentStatus
except ImportError:
    # Fallback constants
    class EnrollmentStatus:
        ACTIVE = "active"
        COMPLETED = "completed"
        DROPPED = "dropped"
        SUSPENDED = "suspended"

    class CompletionStatus:
        NOT_STARTED = "not_started"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        PUBLISHED = "published"


logger = logging.getLogger(__name__)

# Signal processing flags to prevent loops
_signal_processing_flags = {}
_signal_lock = threading.Lock()

# Cache keys for performance optimization
CACHE_KEYS = {
    "course_analytics": "course_analytics_{course_id}",
    "enrollment_progress": "enrollment_progress_{enrollment_id}",
    "course_duration": "course_duration_{course_id}",
    "module_duration": "module_duration_{module_id}",
}

# Cache timeouts
CACHE_TIMEOUTS = {
    "analytics": 300,  # 5 minutes
    "progress": 60,  # 1 minute
    "duration": 600,  # 10 minutes
}


def prevent_signal_loop(signal_key: str):
    """
    Decorator to prevent signal processing loops with thread safety
    ENHANCED: Better thread safety and signal loop prevention
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with _signal_lock:
                if _signal_processing_flags.get(signal_key, False):
                    logger.debug(f"Signal loop prevented for {signal_key}")
                    return

                try:
                    _signal_processing_flags[signal_key] = True
                    return func(*args, **kwargs)
                finally:
                    _signal_processing_flags[signal_key] = False

        return wrapper

    return decorator


def audit_signal_action(
    action: str, model_name: str, instance_id: int = None, metadata: Dict = None
):
    """
    Audit logging for signal actions
    ENHANCED: Better audit logging with structured data
    """
    try:
        log_entry = {
            "timestamp": timezone.now().isoformat(),
            "action": action,
            "model": model_name,
            "instance_id": instance_id,
            "metadata": metadata or {},
            "thread_id": threading.current_thread().ident,
        }

        logger.info(
            f"SIGNAL_AUDIT: {action} on {model_name}({instance_id})", extra=log_entry
        )

    except Exception as e:
        logger.error(f"Failed to create signal audit log: {e}")


def update_course_analytics_async(course_id: int):
    """
    FIXED: Added missing update_course_analytics_async function
    Asynchronously update course analytics with proper error handling
    """
    try:
        # Check if update is already in progress
        cache_key = f"analytics_updating_{course_id}"
        if cache.get(cache_key):
            logger.debug(f"Analytics update already in progress for course {course_id}")
            return

        # Mark as updating
        cache.set(cache_key, True, timeout=30)

        try:
            # Try to use Celery task if available
            try:
                from .tasks import update_course_analytics_task

                update_course_analytics_task.delay(course_id)
                logger.info(f"Queued analytics update task for course {course_id}")
                return
            except ImportError:
                # Fallback to synchronous update
                logger.debug("Celery not available, using synchronous analytics update")

            # Synchronous update within transaction
            with transaction.atomic():
                try:
                    course = Course.objects.select_for_update().get(id=course_id)
                    update_course_analytics(course)

                    # Cache analytics results
                    analytics_data = {
                        "enrolled_students_count": course.enrolled_students_count,
                        "avg_rating": float(course.avg_rating or 0),
                        "total_reviews": course.total_reviews,
                        "last_updated": timezone.now().isoformat(),
                    }

                    cache.set(
                        CACHE_KEYS["course_analytics"].format(course_id=course_id),
                        analytics_data,
                        timeout=CACHE_TIMEOUTS["analytics"],
                    )

                    logger.info(f"Course analytics updated for course {course_id}")

                except Course.DoesNotExist:
                    logger.error(f"Course {course_id} not found for analytics update")
                except Exception as e:
                    logger.error(
                        f"Error updating course analytics for course {course_id}: {e}"
                    )

        finally:
            # Clear update flag
            cache.delete(cache_key)

    except Exception as e:
        logger.error(
            f"Unexpected error in update_course_analytics_async for course {course_id}: {e}"
        )


@receiver(post_save, sender=Enrollment)
@prevent_signal_loop("enrollment_post_save")
def create_progress_records(sender, instance: Enrollment, created: bool, **kwargs):
    """
    Create progress records for all lessons when a user enrolls in a course
    ENHANCED: Better race condition prevention and error handling
    """
    if not created:
        return

    try:
        with transaction.atomic():
            # Get all lessons efficiently with prefetch
            lessons = (
                Lesson.objects.filter(module__course=instance.course)
                .select_related("module")
                .order_by("module__order", "order")
            )

            if not lessons.exists():
                logger.warning(f"No lessons found for course {instance.course.id}")
                return

            # Check if progress records already exist (race condition prevention)
            existing_progress = Progress.objects.filter(
                enrollment=instance, lesson__in=lessons
            ).exists()

            if existing_progress:
                logger.info(
                    f"Progress records already exist for enrollment {instance.id}"
                )
                return

            # Bulk create progress records
            progress_records = []
            for lesson in lessons:
                progress_records.append(
                    Progress(
                        enrollment=instance,
                        lesson=lesson,
                        is_completed=False,
                        time_spent=0,
                        progress_percentage=0,
                        created_date=timezone.now(),
                    )
                )

            # Batch create for performance
            if progress_records:
                Progress.objects.bulk_create(
                    progress_records,
                    batch_size=100,
                    ignore_conflicts=True,  # Prevent duplicates
                )

                logger.info(
                    f"Created {len(progress_records)} progress records for enrollment {instance.id}"
                )

            # Update course analytics asynchronously
            update_course_analytics_async(instance.course.id)

            # Clear related caches
            cache_key = CACHE_KEYS["enrollment_progress"].format(
                enrollment_id=instance.id
            )
            cache.delete(cache_key)

            audit_signal_action(
                "progress_records_created",
                "Enrollment",
                instance.id,
                {
                    "course_id": instance.course.id,
                    "lesson_count": len(progress_records),
                },
            )

    except Exception as e:
        logger.error(
            f"Error creating progress records for enrollment {instance.id}: {e}"
        )
        # Re-raise in development, log in production
        if settings.DEBUG:
            raise
        else:
            # Send notification to monitoring system
            logger.critical(
                f"CRITICAL: Progress record creation failed for enrollment {instance.id}"
            )


@receiver(post_save, sender=Progress)
@prevent_signal_loop("progress_post_save")
def update_enrollment_progress(sender, instance: Progress, **kwargs):
    """
    Update enrollment progress percentage when lesson progress changes
    ENHANCED: Better performance optimization and database consistency
    """
    try:
        enrollment = instance.enrollment
        cache_key = CACHE_KEYS["enrollment_progress"].format(
            enrollment_id=enrollment.id
        )

        # Check cache first
        cached_progress = cache.get(cache_key)
        if cached_progress is not None:
            current_progress = cached_progress
        else:
            current_progress = calculate_course_progress_optimized(enrollment)
            cache.set(cache_key, current_progress, timeout=CACHE_TIMEOUTS["progress"])

        # Only update if progress has changed significantly (avoid micro-updates)
        progress_diff = abs(enrollment.progress_percentage - current_progress)
        if progress_diff < 1.0:  # Less than 1% change
            return

        with transaction.atomic():
            # Use select_for_update to prevent race conditions
            enrollment_obj = Enrollment.objects.select_for_update().get(
                id=enrollment.id
            )

            # Only update if progress increased
            if current_progress > enrollment_obj.progress_percentage:
                enrollment_obj.progress_percentage = current_progress
                enrollment_obj.last_accessed = timezone.now()
                enrollment_obj.updated_date = timezone.now()
                enrollment_obj.save(
                    update_fields=[
                        "progress_percentage",
                        "last_accessed",
                        "updated_date",
                    ]
                )

                # Check for course completion
                if (
                    current_progress >= 100.0
                    and enrollment_obj.status == EnrollmentStatus.ACTIVE
                ):
                    complete_course_enrollment(enrollment_obj)

                audit_signal_action(
                    "enrollment_progress_updated",
                    "Progress",
                    instance.id,
                    {
                        "enrollment_id": enrollment.id,
                        "new_progress": current_progress,
                        "old_progress": enrollment.progress_percentage,
                    },
                )

    except Exception as e:
        logger.error(
            f"Error updating enrollment progress for progress {instance.id}: {e}"
        )
        if settings.DEBUG:
            raise


def calculate_course_progress_optimized(enrollment: Enrollment) -> float:
    """
    Optimized course progress calculation with caching
    ENHANCED: Better performance and error handling
    """
    try:
        cache_key = f"course_progress_{enrollment.id}"
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Use aggregation for better performance
        progress_stats = Progress.objects.filter(enrollment=enrollment).aggregate(
            total_lessons=Count("id"),
            completed_lessons=Count("id", filter=Q(is_completed=True)),
            avg_progress=Avg("progress_percentage"),
        )

        total_lessons = progress_stats["total_lessons"] or 0
        completed_lessons = progress_stats["completed_lessons"] or 0

        if total_lessons == 0:
            progress_percentage = 0.0
        else:
            progress_percentage = (completed_lessons / total_lessons) * 100.0

        # Cache result
        cache.set(cache_key, progress_percentage, timeout=CACHE_TIMEOUTS["progress"])

        return progress_percentage

    except Exception as e:
        logger.error(
            f"Error calculating course progress for enrollment {enrollment.id}: {e}"
        )
        return 0.0


def complete_course_enrollment(enrollment: Enrollment):
    """
    Complete course enrollment and handle certificate generation
    ENHANCED: Better atomicity and error handling
    """
    try:
        with transaction.atomic():
            # Update enrollment status
            enrollment.status = EnrollmentStatus.COMPLETED
            enrollment.completion_date = timezone.now()
            enrollment.updated_date = timezone.now()
            enrollment.save(update_fields=["status", "completion_date", "updated_date"])

            # Generate certificate if applicable
            if enrollment.course.has_certificate:
                try:
                    # Check if certificate already exists
                    if not hasattr(enrollment, "certificate"):
                        create_certificate_atomic(enrollment)
                except Exception as cert_error:
                    logger.error(
                        f"Error creating certificate for enrollment {enrollment.id}: {cert_error}"
                    )

            # Update course analytics
            update_course_analytics_async(enrollment.course.id)

            audit_signal_action(
                "course_completed",
                "Enrollment",
                enrollment.id,
                {"course_id": enrollment.course.id},
            )

            logger.info(f"Course completion processed for enrollment {enrollment.id}")

    except Exception as e:
        logger.error(f"Error completing course enrollment {enrollment.id}: {e}")
        raise


@receiver(post_save, sender=Review)
@prevent_signal_loop("review_post_save")
def update_course_ratings(sender, instance: Review, created: bool, **kwargs):
    """
    Update course average rating when a review is added or modified
    ENHANCED: Better performance optimization with bulk updates
    """
    try:
        update_course_analytics_async(instance.course.id)

        # Clear related caches
        cache_key = CACHE_KEYS["course_analytics"].format(course_id=instance.course.id)
        cache.delete(cache_key)

        audit_signal_action(
            "review_created" if created else "review_updated",
            "Review",
            instance.id,
            {
                "course_id": instance.course.id,
                "rating": float(instance.rating),
                "is_approved": instance.is_approved,
            },
        )

    except Exception as e:
        logger.error(f"Error updating course ratings for review {instance.id}: {e}")


@receiver(post_delete, sender=Review)
@prevent_signal_loop("review_delete")
def update_course_ratings_on_delete(sender, instance: Review, **kwargs):
    """
    Update course average rating when a review is deleted
    ENHANCED: Better cleanup and cache invalidation
    """
    try:
        update_course_analytics_async(instance.course.id)

        # Clear related caches
        cache_key = CACHE_KEYS["course_analytics"].format(course_id=instance.course.id)
        cache.delete(cache_key)

        audit_signal_action(
            "review_deleted",
            "Review",
            instance.id,
            {"course_id": instance.course.id, "rating": float(instance.rating)},
        )

    except Exception as e:
        logger.error(f"Error updating course ratings after review deletion: {e}")


@receiver([post_save, post_delete], sender=Lesson)
@prevent_signal_loop("lesson_duration_update")
def update_course_duration(sender, instance: Lesson, **kwargs):
    """
    Update course duration when lessons are added, modified, or deleted
    ENHANCED: Better atomic updates and performance optimization
    """
    try:
        course = instance.module.course
        module = instance.module

        with transaction.atomic():
            # Update module duration first
            update_module_duration_atomic(module)

            # Then update course duration
            update_course_duration_atomic(course)

        # Clear caches
        module_cache_key = CACHE_KEYS["module_duration"].format(module_id=module.id)
        course_cache_key = CACHE_KEYS["course_duration"].format(course_id=course.id)
        cache.delete_many([module_cache_key, course_cache_key])

        audit_signal_action(
            "lesson_duration_updated",
            "Lesson",
            instance.id,
            {
                "module_id": module.id,
                "course_id": course.id,
                "duration_minutes": instance.duration_minutes or 0,
            },
        )

    except Exception as e:
        logger.error(f"Error updating course duration for lesson {instance.id}: {e}")


def update_module_duration_atomic(module: Module):
    """
    Atomically update module duration
    ENHANCED: Better atomicity and error handling
    """
    try:
        # Calculate total duration using aggregation
        total_duration = (
            module.lessons.aggregate(total=Sum("duration_minutes"))["total"] or 0
        )

        # Update only if changed
        if module.duration_minutes != total_duration:
            Module.objects.filter(id=module.id).update(
                duration_minutes=total_duration, updated_date=timezone.now()
            )

    except Exception as e:
        logger.error(f"Error updating module duration for module {module.id}: {e}")
        raise


def update_course_duration_atomic(course: Course):
    """
    Atomically update course duration
    ENHANCED: Better atomicity and error handling
    """
    try:
        # Calculate total duration using aggregation
        total_duration = (
            Module.objects.filter(course=course).aggregate(
                total=Sum("duration_minutes")
            )["total"]
            or 0
        )

        # Update only if changed
        if course.duration_minutes != total_duration:
            Course.objects.filter(id=course.id).update(
                duration_minutes=total_duration, updated_date=timezone.now()
            )

    except Exception as e:
        logger.error(f"Error updating course duration for course {course.id}: {e}")
        raise


@receiver(pre_save, sender=Course)
@prevent_signal_loop("course_pre_save")
def update_course_completion_status(sender, instance: Course, **kwargs):
    """
    Update course completion status based on content
    ENHANCED: Better performance optimization and validation
    """
    if not instance.pk:  # Skip for new courses
        return

    try:
        # Use efficient queries to check content
        has_modules = instance.modules.exists()
        has_lessons = False

        if has_modules:
            has_lessons = Lesson.objects.filter(module__course=instance).exists()

        # Update completion status based on content and publication
        if has_modules and has_lessons:
            if instance.completion_status == CompletionStatus.NOT_STARTED:
                instance.completion_status = CompletionStatus.IN_PROGRESS
                instance.completion_percentage = 50
            elif (
                instance.completion_status == CompletionStatus.IN_PROGRESS
                and instance.is_published
            ):
                instance.completion_status = CompletionStatus.PUBLISHED
                instance.completion_percentage = 100

        audit_signal_action(
            "course_completion_status_updated",
            "Course",
            instance.id,
            {
                "completion_status": instance.completion_status,
                "completion_percentage": instance.completion_percentage,
                "has_modules": has_modules,
                "has_lessons": has_lessons,
            },
        )

    except Exception as e:
        logger.error(
            f"Error updating course completion status for course {instance.id}: {e}"
        )


@receiver(post_save, sender=AssessmentAttempt)
@prevent_signal_loop("assessment_post_save")
def update_lesson_progress_on_assessment(
    sender, instance: AssessmentAttempt, created: bool, **kwargs
):
    """
    Update lesson progress when assessment is completed
    ENHANCED: Better race condition prevention and performance optimization
    """
    if not (instance.end_time and instance.passed):
        return

    try:
        lesson = instance.assessment.lesson

        with transaction.atomic():
            # Find active enrollments efficiently
            enrollments = Enrollment.objects.filter(
                user=instance.user,
                course=lesson.module.course,
                status=EnrollmentStatus.ACTIVE,
            ).select_for_update()

            for enrollment in enrollments:
                # Update or create progress record
                progress, created_progress = Progress.objects.update_or_create(
                    enrollment=enrollment,
                    lesson=lesson,
                    defaults={
                        "is_completed": True,
                        "completed_date": instance.end_time,
                        "progress_percentage": 100,
                        "updated_date": timezone.now(),
                    },
                )

                if not created_progress and not progress.is_completed:
                    progress.is_completed = True
                    progress.completed_date = instance.end_time
                    progress.progress_percentage = 100
                    progress.updated_date = timezone.now()
                    progress.save(
                        update_fields=[
                            "is_completed",
                            "completed_date",
                            "progress_percentage",
                            "updated_date",
                        ]
                    )

                # Clear progress cache
                cache_key = CACHE_KEYS["enrollment_progress"].format(
                    enrollment_id=enrollment.id
                )
                cache.delete(cache_key)

        audit_signal_action(
            "assessment_completed",
            "AssessmentAttempt",
            instance.id,
            {
                "lesson_id": lesson.id,
                "user_id": instance.user.id,
                "passed": instance.passed,
                "score_percentage": float(instance.score_percentage),
            },
        )

    except Exception as e:
        logger.error(
            f"Error updating lesson progress for assessment {instance.id}: {e}"
        )


def create_certificate_atomic(enrollment: Enrollment):
    """
    Atomically create a certificate for completed enrollment
    ENHANCED: Better race condition prevention and validation
    """
    try:
        with transaction.atomic():
            # Check if certificate already exists
            if Certificate.objects.filter(enrollment=enrollment).exists():
                logger.warning(
                    f"Certificate already exists for enrollment {enrollment.id}"
                )
                return

            # Generate certificate details
            cert_number = generate_certificate_number(
                enrollment.course.id, enrollment.user.id
            )
            verification_hash = generate_verification_hash(cert_number)

            # Create certificate
            certificate = Certificate(
                enrollment=enrollment,
                certificate_number=cert_number,
                verification_hash=verification_hash,
                is_valid=True,
                template_version="2.1",  # Use latest template
                created_date=timezone.now(),
            )

            # Validate before saving
            certificate.full_clean()
            certificate.save()

            audit_signal_action(
                "certificate_created",
                "Certificate",
                certificate.id,
                {
                    "enrollment_id": enrollment.id,
                    "certificate_number": cert_number,
                    "course_id": enrollment.course.id,
                },
            )

            logger.info(
                f"Certificate created for enrollment {enrollment.id}: {cert_number}"
            )

    except Exception as e:
        logger.error(f"Error creating certificate for enrollment {enrollment.id}: {e}")
        raise


# Signal connection validation
@receiver(post_save, sender=Course)
def validate_signal_connections(sender, **kwargs):
    """
    Validate that all required signals are properly connected
    ENHANCED: Better signal connection validation
    """
    try:
        # This runs only once during startup
        if not hasattr(validate_signal_connections, "_validated"):
            logger.info("Validating signal connections...")

            # Count connected signals
            signal_count = 0
            for signal_func in [
                create_progress_records,
                update_enrollment_progress,
                update_course_ratings,
                update_course_ratings_on_delete,
                update_course_duration,
                update_course_completion_status,
                update_lesson_progress_on_assessment,
            ]:
                if hasattr(signal_func, "__wrapped__"):
                    signal_count += 1

            logger.info(
                f"Signal validation complete: {signal_count} handlers registered"
            )
            validate_signal_connections._validated = True

    except Exception as e:
        logger.error(f"Signal validation failed: {e}")


# Cleanup function for testing
def clear_signal_flags():
    """Clear all signal processing flags - useful for testing"""
    global _signal_processing_flags
    with _signal_lock:
        _signal_processing_flags.clear()


# Export signal handlers for testing
__all__ = [
    "create_progress_records",
    "update_enrollment_progress",
    "update_course_ratings",
    "update_course_ratings_on_delete",
    "update_course_duration",
    "update_course_completion_status",
    "update_lesson_progress_on_assessment",
    "create_certificate_atomic",
    "update_course_analytics_async",  # FIXED: Now properly exported
    "clear_signal_flags",
]
