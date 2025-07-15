# File Path: backend/courses/models/enrolment.py
# Folder Path: backend/courses/models/enrolment.py
# Date Created: 2025-06-26 09:33:05
# Date Revised: 2025-07-02 10:54:34
# Current Date and Time (UTC): 2025-07-02 10:54:34
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-02 10:54:34 UTC
# User: cadsanthanamNew
# Version: 7.0.0

import logging
import re
from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import (
    DatabaseError,
    IntegrityError,
    OperationalError,
    models,
    transaction,
)
from django.utils import timezone

from ..constants import STATUS_CHOICES
from ..utils.core import generate_certificate_number, generate_verification_hash
from ..utils.model_helpers import create_decimal_field
from ..validators import validate_certificate_number, validate_percentage
from .mixins import TimeStampedMixin

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================
# ENROLLMENT MODEL
# =====================================


class Enrollment(TimeStampedMixin):
    """Enhanced enrollment model with analytics support and validation"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_enrollments",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="Enrolled student",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_index=True,
        help_text="Enrolled course",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Enrollment status",
    )
    completion_date = models.DateTimeField(
        blank=True, null=True, help_text="Date when course was completed"
    )
    # FIXED: Remove auto_now to reduce write amplification - update manually when accessed
    last_accessed = models.DateTimeField(
        blank=True, null=True, help_text="Last time student accessed the course"
    )
    enrolled_date = models.DateTimeField(
        auto_now_add=True, help_text="Date when student enrolled"
    )

    # Analytics fields
    total_time_spent = models.PositiveIntegerField(
        default=0, help_text="Total time spent in seconds"
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Enrollment progress percentage (0-100)",
    )
    last_lesson_accessed = models.ForeignKey(
        "Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_accessed_enrollments",
        help_text="Last lesson accessed by student",
    )

    def clean(self):
        """
        Enhanced validation for enrollment
        FIXED: Use unique constraint instead of extra query on every save
        """
        super().clean()
        # Note: Validation moved to unique constraint for performance
        # This prevents the N+1 query problem on every save
        pass

    def update_progress(self):
        """
        Update enrollment progress based on completed lessons
        FIXED: Deferred to Celery task to prevent synchronous DB scans
        """
        try:
            # FIXED: Send to Celery task for bulk progress update to avoid synchronous processing
            from django.conf import settings

            if (
                hasattr(settings, "CELERY_TASK_ALWAYS_EAGER")
                and settings.CELERY_TASK_ALWAYS_EAGER
            ):
                # Development mode - process synchronously
                self._update_progress_sync()
            else:
                # Production mode - use Celery task
                try:
                    from courses.tasks import update_enrollment_progress_task

                    # Check if task already queued to prevent duplicate tasks
                    from django.core.cache import cache

                    cache_key = f"progress_update_task_{self.id}"
                    if not cache.get(cache_key):
                        # Set a lock to prevent duplicate tasks
                        cache.set(cache_key, True, 60)  # 60 second lock
                        update_enrollment_progress_task.delay(self.id)
                    else:
                        logger.debug(
                            f"Skipping duplicate progress update for enrollment {self.id}"
                        )
                except ImportError:
                    # Fallback to synchronous if Celery not available
                    logger.warning(
                        "Celery tasks not available, processing progress update synchronously"
                    )
                    self._update_progress_sync()

        except (DatabaseError, OperationalError) as e:
            logger.error(
                f"Database error scheduling progress update for enrollment {self.id}: {e}"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error scheduling progress update for enrollment {self.id}: {e}"
            )

    def _update_progress_sync(self):
        """
        Synchronous progress update for development/fallback
        FIXED: Optimized to reduce O(n) database hits with aggregation
        """
        try:
            with transaction.atomic():
                Course = apps.get_model("courses", "Course")
                Lesson = apps.get_model("courses", "Lesson")

                # FIXED: Use denormalized lesson count on course model to avoid expensive queries
                # or cache the count for performance
                cache_key = f"course_{self.course.id}_lesson_count"
                from django.core.cache import cache

                total_lessons = cache.get(cache_key)
                if total_lessons is None:
                    # Calculate total lessons efficiently with a single query
                    total_lessons = Lesson.objects.filter(
                        module__course_id=self.course.id
                    ).count()

                    if total_lessons > 0:
                        # Only cache if we found lessons
                        cache.set(cache_key, total_lessons, 3600)  # Cache for 1 hour

                if total_lessons == 0:
                    self.progress_percentage = 0
                else:
                    # FIXED: Use aggregation instead of count() to avoid N+1 query
                    completed_lessons = (
                        Progress.objects.filter(
                            enrollment=self, is_completed=True
                        ).aggregate(count=models.Count("id"))["count"]
                        or 0
                    )

                    self.progress_percentage = int(
                        (completed_lessons / total_lessons) * 100
                    )

                # Determine completion status
                previous_status = self.status
                if self.progress_percentage == 100 and self.status == "active":
                    self.status = "completed"
                    self.completion_date = timezone.now()

                # Only save if fields have changed
                update_fields = ["progress_percentage"]
                if previous_status != self.status:
                    update_fields.extend(["status", "completion_date"])

                Enrollment.objects.filter(pk=self.pk).update(
                    progress_percentage=self.progress_percentage,
                    status=self.status,
                    completion_date=self.completion_date,
                )

                # Update course analytics if necessary (only on completion)
                if previous_status != self.status and self.status == "completed":
                    try:
                        self.course.update_analytics()
                    except Exception as e:
                        logger.error(
                            f"Error updating course analytics after enrollment completion: {e}"
                        )

                logger.debug(
                    f"Progress updated for enrollment {self.id}: {self.progress_percentage}%"
                )

        except (DatabaseError, OperationalError) as e:
            logger.error(
                f"Database error updating progress for enrollment {self.id}: {e}"
            )
            raise
        except AttributeError as e:
            logger.error(
                f"Attribute error updating progress for enrollment {self.id}: {e}"
            )

    def update_last_accessed(self):
        """
        Update last_accessed timestamp manually to reduce write amplification
        FIXED: Added throttling to prevent excessive updates
        """
        try:
            # Check if update is needed (don't update more than once per hour)
            from django.core.cache import cache

            cache_key = f"enrollment_last_accessed_{self.id}"

            if not cache.get(cache_key):
                now = timezone.now()
                self.last_accessed = now

                # Use direct update to avoid race conditions
                Enrollment.objects.filter(pk=self.pk).update(last_accessed=now)

                # Set cache to prevent frequent updates
                cache.set(cache_key, True, 3600)  # 1 hour throttle

                logger.debug(f"Updated last_accessed for enrollment {self.id}")
            else:
                logger.debug(
                    f"Skipped frequent last_accessed update for enrollment {self.id}"
                )
        except Exception as e:
            logger.error(f"Error updating last_accessed for enrollment {self.id}: {e}")

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in Enrollment.save() for ID {getattr(self, 'id', 'new')}: {e}"
            )
            raise

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        ordering = ["-created_date"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["course", "status"]),
            # Added partial index for active enrollment lookups
            models.Index(
                fields=["user", "course"],
                condition=models.Q(status="active"),
                name="idx_enrl_user_course_act",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=~models.Q(status="unenrolled"),
                name="unique_active_enrollment",
                violation_error_message="User is already enrolled in this course",
            ),
        ]


# =====================================
# PROGRESS MODEL
# =====================================


class Progress(TimeStampedMixin):
    """Enhanced progress model with comprehensive analytics and validation"""

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="progress",
        db_index=True,
        help_text="Associated enrollment",
    )
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="progress_records",
        db_index=True,
        help_text="Lesson being tracked",
    )
    is_completed = models.BooleanField(
        default=False, help_text="Whether lesson is completed"
    )
    completed_date = models.DateTimeField(
        blank=True, null=True, help_text="Date when lesson was completed"
    )
    time_spent = models.PositiveIntegerField(
        default=0, help_text="Time spent on this lesson in seconds"
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Progress within this specific lesson (0-100)",
    )
    notes = models.TextField(
        blank=True, default="", help_text="Student notes for this lesson"
    )
    # FIXED: Remove auto_now to reduce write amplification - update manually when accessed
    last_accessed = models.DateTimeField(
        blank=True, null=True, help_text="Last time lesson was accessed"
    )

    def save(self, *args, **kwargs):
        """
        Enhanced save with automatic completion date setting
        FIXED: Defer expensive aggregation to Celery task
        FIXED: Fixed indentation error
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                if self.is_completed and not self.completed_date:
                    self.completed_date = timezone.now()

                # Set last_accessed if not set
                if not self.last_accessed:
                    self.last_accessed = timezone.now()

                # Track if this is a new completion
                is_new_completion = False
                if "update_fields" not in kwargs and self.pk:
                    # Check if this is a completion status change
                    try:
                        old_progress = Progress.objects.get(pk=self.pk)
                        is_new_completion = (
                            not old_progress.is_completed and self.is_completed
                        )
                    except Progress.DoesNotExist:
                        pass
                elif not self.pk:
                    # New progress record
                    is_new_completion = self.is_completed

                super().save(*args, **kwargs)

                # FIXED: Only trigger progress update on completion status change
                if is_new_completion:
                    # FIXED: Defer expensive aggregation to Celery task to prevent N×DB hits in loops
                    try:
                        from django.conf import settings

                        if (
                            hasattr(settings, "CELERY_TASK_ALWAYS_EAGER")
                            and settings.CELERY_TASK_ALWAYS_EAGER
                        ):
                            # Development mode - process synchronously
                            self.enrollment.update_progress()
                        else:
                            # Production mode - use Celery task
                            try:
                                from courses.tasks import (
                                    update_enrollment_progress_task,
                                )
                                from django.core.cache import cache

                                # Prevent duplicate tasks
                                cache_key = f"progress_update_task_{self.enrollment.id}"
                                if not cache.get(cache_key):
                                    cache.set(cache_key, True, 60)  # 60 second lock
                                    update_enrollment_progress_task.delay(
                                        self.enrollment.id
                                    )
                            except ImportError:
                                logger.warning(
                                    "Celery tasks not available, processing progress update synchronously"
                                )
                                self.enrollment.update_progress()

                    except (DatabaseError, OperationalError) as e:
                        logger.error(
                            f"Database error updating enrollment progress from Progress {self.id}: {e}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Unexpected error updating enrollment progress from Progress {self.id}: {e}"
                        )
        except Exception as e:
            logger.error(
                f"Error in Progress.save() for ID {getattr(self, 'id', 'new')}: {e}"
            )
            raise

    def update_last_accessed(self):
        """
        Update last_accessed timestamp manually to reduce write amplification
        FIXED: Added throttling to prevent excessive updates
        """
        try:
            # Check if update is needed (don't update more than once per hour)
            from django.core.cache import cache

            cache_key = f"progress_last_accessed_{self.id}"

            if not cache.get(cache_key):
                now = timezone.now()
                self.last_accessed = now

                # Use direct update to avoid race conditions
                Progress.objects.filter(pk=self.pk).update(last_accessed=now)

                # Set cache to prevent frequent updates
                cache.set(cache_key, True, 3600)  # 1 hour throttle

                logger.debug(f"Updated last_accessed for progress {self.id}")
            else:
                logger.debug(
                    f"Skipped frequent last_accessed update for progress {self.id}"
                )
        except Exception as e:
            logger.error(f"Error updating last_accessed for progress {self.id}: {e}")

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title} progress"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Progress"
        verbose_name_plural = "Progress Records"
        ordering = ["-last_accessed"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["enrollment", "is_completed"]),
            models.Index(fields=["lesson", "is_completed"]),
            models.Index(fields=["enrollment", "lesson"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"], name="unique_progress_record"
            ),
        ]


# =====================================
# CERTIFICATE MODEL
# =====================================


class Certificate(TimeStampedMixin):
    """Enhanced certificate model with verification, validation, and security"""

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="certificate",
        help_text="Associated enrollment",
    )
    # FIXED: Add RegexValidator for certificate number format
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^CERT-\d{6}-\d{6}-\d{17}-[A-F0-9]{4}$",
                message="Certificate number must follow format: CERT-{course_id}-{user_id}-{17-digit-timestamp}-{uuid}",
                code="invalid_certificate_format",
            ),
            validate_certificate_number,
        ],
        help_text="Unique certificate number",
    )

    # Verification and validity
    is_valid = models.BooleanField(
        default=True, help_text="Whether certificate is valid"
    )
    revocation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when certificate was revoked"
    )
    revocation_reason = models.TextField(
        blank=True, default="", help_text="Reason for certificate revocation"
    )

    # Additional metadata
    verification_hash = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        help_text="SHA-256 hash for verification",
    )
    template_version = models.CharField(
        max_length=10, default="1.0", help_text="Certificate template version"
    )

    def clean(self):
        """Enhanced validation for certificate"""
        super().clean()
        if self.enrollment.status != "completed":
            raise ValidationError(
                "Certificate can only be issued for completed enrollments"
            )

    def save(self, *args, **kwargs):
        """
        Enhanced save with automatic generation of certificate data
        FIXED: Use transaction for atomicity and select_related to reduce queries
        """
        try:
            with transaction.atomic():
                if not self.certificate_number:
                    # Fetch enrollment with select_related to prevent additional queries
                    if not hasattr(self.enrollment, "course") or not hasattr(
                        self.enrollment, "user"
                    ):
                        enrollment = Enrollment.objects.select_related(
                            "course", "user"
                        ).get(pk=self.enrollment.pk)
                    else:
                        enrollment = self.enrollment

                    self.certificate_number = generate_certificate_number(
                        enrollment.course.id,
                        enrollment.user.id,
                        self.created_date or timezone.now(),
                    )

                if not self.verification_hash:
                    self.verification_hash = generate_verification_hash(
                        self.certificate_number,
                        self.enrollment.id,
                        self.created_date or timezone.now(),
                    )

                super().save(*args, **kwargs)
                logger.info(
                    f"Certificate issued: {self.certificate_number} for {self.enrollment.user.username}"
                )
        except Exception as e:
            logger.error(
                f"Error in Certificate.save() for ID {getattr(self, 'id', 'new')}: {e}"
            )
            raise

    def revoke(self, reason=None):
        """Revoke the certificate with atomic operation"""
        try:
            with transaction.atomic():
                self.is_valid = False
                self.revocation_date = timezone.now()
                self.revocation_reason = reason or "Certificate revoked"
                self.save(
                    update_fields=["is_valid", "revocation_date", "revocation_reason"]
                )

            logger.warning(f"Certificate revoked: {self.certificate_number} - {reason}")
        except (DatabaseError, OperationalError, IntegrityError) as e:
            logger.error(
                f"Database error revoking certificate {self.certificate_number}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error revoking certificate {self.certificate_number}: {e}"
            )
            raise

    def __str__(self):
        status = "REVOKED" if not self.is_valid else "VALID"
        return f"Certificate #{self.certificate_number} for {self.enrollment.user.username} - {self.enrollment.course.title} [{status}]"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
        ordering = ["-created_date"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["certificate_number"]),
            models.Index(fields=["verification_hash"]),
            models.Index(fields=["is_valid"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["certificate_number"], name="unique_certificate_number"
            ),
            models.UniqueConstraint(
                fields=["verification_hash"], name="unique_verification_hash"
            ),
        ]


# =====================================
# COURSE PROGRESS MODEL
# =====================================


class CourseProgress(TimeStampedMixin):
    """Enhanced course-level progress tracking model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_progress_records",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="Student user",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="student_progress",
        db_index=True,
        help_text="Associated course",
    )

    # Progress tracking
    completion_percentage = create_decimal_field(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Course completion percentage (0.00 to 100.00)",
    )

    # Timestamps
    last_accessed = models.DateTimeField(
        blank=True, null=True, help_text="Last time the user accessed this course"
    )
    started_at = models.DateTimeField(
        auto_now_add=True, help_text="When the user first started this course"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When the user completed this course"
    )

    # Current position tracking
    current_lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_for_users",
        help_text="The lesson the user is currently on",
    )

    # Analytics
    total_time_spent = models.PositiveIntegerField(
        default=0, help_text="Total time spent on this course in seconds"
    )
    lessons_completed = models.PositiveIntegerField(
        default=0, help_text="Number of lessons completed"
    )
    assessments_passed = models.PositiveIntegerField(
        default=0, help_text="Number of assessments passed"
    )

    # Study streak tracking
    study_streak_days = models.PositiveIntegerField(
        default=0, help_text="Consecutive days of course activity"
    )
    last_study_date = models.DateField(
        null=True, blank=True, help_text="Last date the user studied this course"
    )

    def clean(self):
        """Enhanced validation for course progress"""
        super().clean()

        if self.completion_percentage < 0 or self.completion_percentage > 100:
            raise ValidationError("Completion percentage must be between 0 and 100")

        if self.completion_percentage >= 100 and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.completion_percentage < 100 and self.completed_at:
            self.completed_at = None

    def save(self, *args, **kwargs):
        """
        Enhanced save with automatic progress calculation
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                self._update_study_streak()

                if self.completion_percentage >= 100 and not self.completed_at:
                    self.completed_at = timezone.now()

                # Set last_accessed if not set
                if not self.last_accessed:
                    self.last_accessed = timezone.now()

                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in CourseProgress.save() for ID {getattr(self, 'id', 'new')}: {e}"
            )
            raise

    def _update_study_streak(self):
        """
        Update study streak based on activity
        FIXED: Safe handling of dates with proper timezone handling
        """
        today = timezone.now().date()

        if not self.last_study_date:
            self.study_streak_days = 1
            self.last_study_date = today
        elif self.last_study_date == today:
            # Already studied today, no change needed
            pass
        elif (today - self.last_study_date).days == 1:
            # Consecutive day (safely calculated)
            self.study_streak_days += 1
            self.last_study_date = today
        else:
            # Streak broken
            self.study_streak_days = 1
            self.last_study_date = today

    def update_from_lesson_progress(self):
        """
        Update course progress based on individual lesson progress
        FIXED: Optimized database queries with aggregation
        FIXED: Added transaction for atomicity
        """
        try:
            with transaction.atomic():
                # Fetch enrollment with select_related for efficiency
                enrollment = (
                    Enrollment.objects.select_related("user", "course")
                    .filter(user=self.user, course=self.course)
                    .first()
                )

                if not enrollment:
                    logger.warning(f"No enrollment found for CourseProgress {self.id}")
                    return

                # FIXED: Use cached or denormalized lesson count for performance
                cache_key = f"course_{self.course.id}_lesson_count"
                from django.core.cache import cache

                total_lessons = cache.get(cache_key)
                if total_lessons is None:
                    Lesson = apps.get_model("courses", "Lesson")
                    total_lessons = Lesson.objects.filter(
                        module__course=self.course
                    ).count()

                    if total_lessons > 0:
                        cache.set(cache_key, total_lessons, 3600)  # Cache for 1 hour

                if total_lessons == 0:
                    self.completion_percentage = Decimal("0.00")
                    self.lessons_completed = 0
                else:
                    # FIXED: Use aggregation for more efficient querying
                    completed_data = Progress.objects.filter(
                        enrollment=enrollment, is_completed=True
                    ).aggregate(
                        count=models.Count("id"), total_time=models.Sum("time_spent")
                    )

                    completed_lessons = completed_data["count"] or 0
                    total_time = completed_data["total_time"] or 0

                    self.lessons_completed = completed_lessons
                    self.completion_percentage = Decimal(
                        str(round((completed_lessons / total_lessons) * 100, 2))
                    )
                    self.total_time_spent = total_time

                # Import using apps.get_model to avoid circular imports
                AssessmentAttempt = apps.get_model("courses", "AssessmentAttempt")

                # FIXED: Use distinct with values for more efficient counting
                self.assessments_passed = (
                    AssessmentAttempt.objects.filter(
                        user=self.user,
                        assessment__lesson__module__course=self.course,
                        is_passed=True,
                    )
                    .values("assessment")
                    .distinct()
                    .count()
                )

                # FIXED: Find current lesson with efficient query
                current_progress = (
                    Progress.objects.filter(enrollment=enrollment, is_completed=False)
                    .select_related("lesson__module")
                    .order_by("lesson__module__order", "lesson__order")
                    .first()
                )

                if current_progress:
                    self.current_lesson = current_progress.lesson

                # Update last_accessed timestamp
                self.last_accessed = timezone.now()

                # Only save once with all updates
                self.save()

                logger.debug(
                    f"Course progress updated: {self.user.username} - {self.course.title} ({self.completion_percentage}%)"
                )

        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error updating course progress {self.id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating course progress {self.id}: {e}")

    def update_last_accessed(self):
        """
        Update last_accessed timestamp manually to reduce write amplification
        FIXED: Added throttling to prevent excessive updates
        """
        try:
            # Check if update is needed (don't update more than once per hour)
            from django.core.cache import cache

            cache_key = f"course_progress_last_accessed_{self.id}"

            if not cache.get(cache_key):
                now = timezone.now()
                self.last_accessed = now

                # Use direct update to avoid race conditions
                CourseProgress.objects.filter(pk=self.pk).update(last_accessed=now)

                # Set cache to prevent frequent updates
                cache.set(cache_key, True, 3600)  # 1 hour throttle

                logger.debug(f"Updated last_accessed for course progress {self.id}")
            else:
                logger.debug(
                    f"Skipped frequent last_accessed update for course progress {self.id}"
                )
        except Exception as e:
            logger.error(
                f"Error updating last_accessed for course progress {self.id}: {e}"
            )

    @property
    def is_completed(self):
        """Check if course is completed"""
        return self.completion_percentage >= 100

    @property
    def progress_percentage_float(self):
        """Get progress as float for compatibility"""
        return float(self.completion_percentage)

    def mark_completed(self):
        """
        Mark course as completed
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                self.completion_percentage = Decimal("100.00")
                self.completed_at = timezone.now()
                self.save(update_fields=["completion_percentage", "completed_at"])

                logger.info(
                    f"Course marked as completed: {self.user.username} - {self.course.title}"
                )
        except Exception as e:
            logger.error(
                f"Error marking course as completed for progress {self.id}: {e}"
            )
            raise

    def reset_progress(self):
        """
        Reset course progress
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                self.completion_percentage = Decimal("0.00")
                self.completed_at = None
                self.lessons_completed = 0
                self.assessments_passed = 0
                self.current_lesson = None
                self.study_streak_days = 0
                self.last_study_date = None
                self.save()

                logger.info(
                    f"Course progress reset: {self.user.username} - {self.course.title}"
                )
        except Exception as e:
            logger.error(f"Error resetting progress for course progress {self.id}: {e}")
            raise

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.completion_percentage}%)"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Course Progress"
        verbose_name_plural = "Course Progress Records"
        ordering = ["-last_accessed"]
        indexes = TimeStampedMixin.Meta.indexes + [
            # Use composite indexes for common query patterns
            models.Index(fields=["user", "course"]),
            models.Index(fields=["course", "completion_percentage"]),
            models.Index(fields=["user", "last_accessed"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_course_progress"
            ),
            # Updated CheckConstraints for Django 6 compatibility
            models.CheckConstraint(
                check=models.Q(completion_percentage__gte=0)
                & models.Q(completion_percentage__lte=100),
                name="course_progress_percentage_range",
            ),
            models.CheckConstraint(
                check=models.Q(lessons_completed__gte=0),
                name="course_progress_lessons_completed_positive",
            ),
            models.CheckConstraint(
                check=models.Q(assessments_passed__gte=0),
                name="course_progress_assessments_passed_positive",
            ),
            models.CheckConstraint(
                check=models.Q(study_streak_days__gte=0),
                name="course_progress_study_streak_positive",
            ),
        ]
