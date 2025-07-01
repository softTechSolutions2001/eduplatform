#
# File Path: backend/courses/models/analytics.py
# Folder Path: backend/courses/models/analytics.py
# Date Created: 2025-06-26 09:53:34
# Date Revised: 2025-07-01 06:55:33
# Current Date and Time (UTC): 2025-07-01 06:55:33
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-01 06:55:33 UTC
# User: cadsanthanamNew
# Version: 5.0.0
#
# FIXED: Analytics and Assessment Models for Course Management System - ALL AUDIT ISSUES RESOLVED
#
# Version 5.0.0 Changes - CRITICAL PRODUCTION FIXES:
# - FIXED 🔴: Removed duplicate utility functions - now imports from model_helpers (P0 Critical)
# - FIXED 🔴: All broad exception handlers replaced with specific exceptions (P0 Critical)
# - FIXED 🟡: Answer.order default changed to None for proper OrderedMixin integration (P1 Important)
# - FIXED 🟡: AssessmentAttempt.save() race condition with proper _state.adding check (P1 Important)
# - ENHANCED: Production-grade error handling with specific exception types
# - MAINTAINED: 100% backward compatibility with existing field names

import logging
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, DatabaseError, OperationalError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from ..constants import (
    DEFAULT_MAX_ATTEMPTS, DEFAULT_PASSING_SCORE,
    QUESTION_TYPE_CHOICES,
)
from .mixins import (
    TimeStampedMixin, OrderedMixin
)
from ..validators import validate_percentage

# FIXED: Import from centralized model_helpers instead of duplicating
from ..utils.model_helpers import (
    create_meta_indexes, create_char_field, create_text_field,
    create_json_field, create_foreign_key
)

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================
# ASSESSMENT MODELS
# =====================================

class Assessment(TimeStampedMixin):
    """Enhanced assessment model with comprehensive configuration and validation"""

    lesson = models.OneToOneField(
        'Lesson', on_delete=models.CASCADE, related_name="assessment",
        help_text="Associated lesson"
    )
    title = create_char_field(255, min_len=2, help_text="Assessment title (minimum 2 characters)")
    description = models.TextField(blank=True, null=True, help_text="Assessment description or instructions")

    # Scoring and attempts
    passing_score = models.PositiveIntegerField(
        default=DEFAULT_PASSING_SCORE,
        validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Passing score percentage (0-100)"
    )
    max_attempts = models.PositiveIntegerField(
        default=DEFAULT_MAX_ATTEMPTS,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attempts allowed"
    )

    # Time management - maintain both field names for compatibility
    time_limit = models.PositiveIntegerField(
        default=0,
        help_text="Time limit in minutes, 0 means no limit"
    )
    time_limit_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Alias for time_limit for backward compatibility"
    )

    # Configuration options
    randomize_questions = models.BooleanField(
        default=False,
        help_text="Randomize question order for each attempt"
    )
    show_correct_answers = models.BooleanField(
        default=True,
        help_text="Show correct answers after completion"
    )
    show_results = models.BooleanField(
        default=True,
        help_text="Show results immediately after completion"
    )

    def save(self, *args, **kwargs):
        """Enhanced save with field synchronization for backward compatibility"""
        # Synchronize time_limit and time_limit_minutes fields
        if self.time_limit and not self.time_limit_minutes:
            self.time_limit_minutes = self.time_limit
        elif self.time_limit_minutes and not self.time_limit:
            self.time_limit = self.time_limit_minutes
        super().save(*args, **kwargs)

    def clean(self):
        """Enhanced validation for assessment data"""
        super().clean()
        if self.time_limit_minutes < 0:
            raise ValidationError("Time limit must be non-negative")
        if self.passing_score < 0 or self.passing_score > 100:
            raise ValidationError("Passing score must be between 0 and 100")

    def get_questions(self):
        """Get questions with optimization"""
        return self.questions.order_by('order')

    def get_max_score(self):
        """Calculate maximum possible score"""
        return sum(q.points for q in self.questions.all())

    def __str__(self):
        return f"Assessment: {self.title}"

    class Meta:
        app_label = 'courses'
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        indexes = [
            models.Index(fields=["lesson"]),
            models.Index(fields=["passing_score"]),
        ]


class Question(TimeStampedMixin, OrderedMixin):
    """
    Enhanced question model with comprehensive validation
    FIXED: Proper OrderedMixin integration with specific exceptions
    """

    assessment = create_foreign_key(
        Assessment,
        "questions",
        help_text="Parent assessment"
    )
    question_text = create_text_field(
        default="",  # Explicit default for migration compatibility
        help_text="Question text"
    )
    text = models.TextField(
        default="",  # Explicit default for backward compatibility
        help_text="Alias for question_text for backward compatibility"
    )
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('multiple_choice', _('Multiple Choice')),
            ('true_false', _('True/False')),
            ('short_answer', _('Short Answer')),
            ('essay', _('Essay')),
            ('matching', _('Matching')),
            ('fill_blank', _('Fill in the Blank')),
        ],
        default='multiple_choice',
        help_text="Type of question"
    )
    points = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Points awarded for correct answer"
    )
    order = models.PositiveIntegerField(default=0)  # FIXED: Changed to 0 for proper OrderedMixin logic
    explanation = models.TextField(
        blank=True,
        null=True,
        default="",  # Explicit default
        help_text="Explanation shown after answering"
    )
    feedback = create_text_field(
        blank=True,
        default="",  # Explicit default for backward compatibility
        help_text="Alias for explanation for backward compatibility"
    )

    def get_next_order(self, parent_field='assessment'):
        """
        Get next order number for this question's assessment
        FIXED: Override method to provide assessment-specific ordering
        """
        try:
            if not self.assessment:
                return 1

            last_order = Question.objects.filter(assessment=self.assessment).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error calculating next order for question: {e}")
            return 1
        except AttributeError as e:
            logger.error(f"Attribute error calculating next order for question: {e}")
            return 1

    def save(self, *args, **kwargs):
        """
        FIXED: Single save method with proper ordering and field synchronization
        """
        # Synchronize text and question_text fields for backward compatibility
        if self.question_text and not self.text:
            self.text = self.question_text
        elif self.text and not self.question_text:
            self.question_text = self.text

        # Ensure we have some question text content
        if not self.question_text and not self.text:
            self.question_text = "Default question text"
            self.text = "Default question text"

        # Synchronize explanation and feedback fields for backward compatibility
        if self.explanation and not self.feedback:
            self.feedback = self.explanation
        elif self.feedback and not self.explanation:
            self.explanation = self.feedback

        # FIXED: Set order if not provided using proper OrderedMixin logic
        if not self.pk and (not self.order or self.order == 0):
            self.order = self.get_next_order()

        super().save(*args, **kwargs)

    @property
    def text_property(self):
        """Property to always return question text"""
        return self.question_text or self.text

    @property
    def feedback_property(self):
        """Property to always return explanation/feedback"""
        return self.explanation or self.feedback

    def get_answers(self):
        """Get answers with optimization"""
        return self.answers.order_by('order')

    def __str__(self):
        return f"Question {self.order}: {self.text[:30]}..."

    class Meta:
        app_label = 'courses'
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["assessment", "order"]
        indexes = [
            models.Index(fields=["assessment", "order"]),
            models.Index(fields=["question_type"]),
            models.Index(fields=["points"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['assessment', 'order'], name='unique_question_order'),
        ]


class Answer(TimeStampedMixin, OrderedMixin):
    """
    Enhanced answer model with comprehensive validation
    FIXED: Single constraints declaration and proper field defaults with order = None
    """

    question = create_foreign_key(
        Question,
        "answers",
        help_text="Parent question"
    )
    answer_text = create_char_field(
        500,
        min_len=1,
        default="",  # Explicit default for migration compatibility
        help_text="Answer text (minimum 1 character)"
    )
    text = create_text_field(
        blank=True,
        default="",  # Explicit default for backward compatibility
        help_text="Alias for answer_text for backward compatibility"
    )
    is_correct = models.BooleanField(
        default=False,
        help_text="Whether this is the correct answer"
    )
    explanation = models.TextField(
        blank=True,
        null=True,
        default="",  # Explicit default
        help_text="Explanation for this answer choice"
    )
    # FIXED: Default to None for proper OrderedMixin integration and set in save()
    order = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Display order of this answer"
    )

    def get_next_order(self, parent_field='question'):
        """
        Get next order number for this answer's question
        FIXED: Override method to provide question-specific ordering
        """
        try:
            if not self.question:
                return 1

            last_order = Answer.objects.filter(question=self.question).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error calculating next order for answer: {e}")
            return 1
        except AttributeError as e:
            logger.error(f"Attribute error calculating next order for answer: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering and field synchronization"""
        # Synchronize text and answer_text fields for backward compatibility
        if self.answer_text and not self.text:
            self.text = self.answer_text
        elif self.text and not self.answer_text:
            self.answer_text = self.text

        # Ensure we have some text content
        if not self.answer_text and not self.text:
            self.answer_text = "Default answer text"
            self.text = "Default answer text"

        # FIXED: Set order if not provided using proper OrderedMixin logic
        if self._state.adding and self.order in (None, 0):
            self.order = self.get_next_order()

        super().save(*args, **kwargs)

    @property
    def text_property(self):
        """Property to always return answer text"""
        return self.answer_text or self.text or "Default answer text"

    def __str__(self):
        return f"Answer: {self.text_property[:30]}..."

    class Meta:
        app_label = 'courses'
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ["question", "order"]
        indexes = [
            models.Index(fields=["question", "order"]),
            models.Index(fields=["is_correct"]),
        ]
        # FIXED: Single constraints declaration with custom error message
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'order'],
                name='unique_answer_order',
                violation_error_message="Answer order must be unique per question"
            ),
        ]


class AssessmentAttempt(TimeStampedMixin):
    """Enhanced assessment attempt model with comprehensive tracking and validation"""

    user = create_foreign_key(
        settings.AUTH_USER_MODEL,
        "assessment_attempts",
        help_text="User taking the assessment"
    )
    assessment = create_foreign_key(
        Assessment,
        "attempts",
        help_text="Assessment being attempted"
    )

    # Timing
    start_time = models.DateTimeField(auto_now_add=True, help_text="When attempt was started")
    end_time = models.DateTimeField(blank=True, null=True, help_text="When attempt was completed")
    time_taken_seconds = models.PositiveIntegerField(default=0)

    # Scoring
    score = models.PositiveIntegerField(default=0, help_text="Raw score achieved")
    max_score = models.PositiveIntegerField(default=0)

    # Status - maintain both field names for compatibility
    is_completed = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False, help_text="Whether attempt passed the assessment")
    passed = models.BooleanField(default=False, help_text="Alias for is_passed for backward compatibility")
    attempt_number = models.PositiveIntegerField(default=1, help_text="Attempt number for this user/assessment combination")

    # Additional tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the user during attempt")
    user_agent = models.TextField(blank=True, null=True, help_text="User agent string during attempt")

    def save(self, *args, **kwargs):
        """
        FIXED: Enhanced save with field synchronization and proper assessment handling
        """
        # Synchronize is_passed and passed fields for backward compatibility
        if self.is_passed != self.passed:
            if hasattr(self, '_state') and self._state.adding:
                # New object, prioritize is_passed
                self.passed = self.is_passed
            else:
                # Existing object, sync both ways
                if self.is_passed and not self.passed:
                    self.passed = self.is_passed
                elif self.passed and not self.is_passed:
                    self.is_passed = self.passed

        # Handle new attempts with atomic operations
        if self._state.adding:  # FIXED: Only set max_score for new instances
            try:
                with transaction.atomic():
                    last_attempt = AssessmentAttempt.objects.select_for_update().filter(
                        user=self.user, assessment=self.assessment
                    ).order_by("-attempt_number").first()

                    self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1

                    if self.assessment.max_attempts > 0 and self.attempt_number > self.assessment.max_attempts:
                        raise ValidationError(f"Maximum attempts ({self.assessment.max_attempts}) exceeded")

                    # FIXED: Set max_score if not already set and assessment exists
                    if not self.max_score and self.assessment:
                        try:
                            self.max_score = self.assessment.get_max_score()
                        except (AttributeError, DatabaseError, OperationalError) as e:
                            logger.warning(f"Could not calculate max_score for attempt: {e}")
                            self.max_score = 0

            except (DatabaseError, OperationalError) as e:
                logger.error(f"Database error in AssessmentAttempt.save(): {e}")
                raise
            except ValidationError:
                raise

        # FIXED: Check if passed based on score percentage only if we have the required data
        try:
            if self.max_score > 0 and self.assessment:
                score_percentage = (self.score / self.max_score) * 100
                if score_percentage >= self.assessment.passing_score:
                    self.is_passed = True
                    self.passed = True
        except (AttributeError, ZeroDivisionError) as e:
            logger.warning(f"Could not calculate passing status for attempt: {e}")

        super().save(*args, **kwargs)

    @property
    def score_percentage(self):
        """Calculate score percentage - FIXED: Safe property access"""
        try:
            if self.max_score > 0:
                return round((self.score / self.max_score) * 100, 1)

            # Fallback to assessment questions if max_score not set
            if self.assessment and not hasattr(self, '_max_score'):
                self._max_score = self.assessment.questions.aggregate(
                    total_points=models.Sum('points')
                )['total_points'] or 0
                return round((self.score / self._max_score) * 100, 1) if self._max_score > 0 else 0

            return 0
        except (DatabaseError, OperationalError, AttributeError, ZeroDivisionError) as e:
            logger.error(f"Error calculating score percentage for attempt {self.id}: {e}")
            return 0

    @property
    def time_taken(self):
        """Calculate time taken for attempt in seconds"""
        if self.time_taken_seconds:
            return self.time_taken_seconds
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    def __str__(self):
        return f"{self.user.username}'s attempt #{self.attempt_number} for {self.assessment.title}"

    class Meta:
        app_label = 'courses'
        verbose_name = "Assessment Attempt"
        verbose_name_plural = "Assessment Attempts"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["user", "assessment"]),
            models.Index(fields=["assessment", "-created_date"]),
            models.Index(fields=["is_passed"]),
            models.Index(fields=["is_completed"]),
            models.Index(fields=["attempt_number"]),
        ]


class AttemptAnswer(TimeStampedMixin):
    """Enhanced attempt answer model with comprehensive validation"""

    attempt = create_foreign_key(
        AssessmentAttempt,
        "answers",
        help_text="Associated assessment attempt"
    )
    question = create_foreign_key(
        Question,
        'user_answers',
        help_text="Question being answered"
    )
    # Maintain both field names for compatibility
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='user_selections_legacy',
        blank=True,
        null=True,
        help_text="Selected answer for multiple choice questions"
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='user_selections',
        blank=True,
        null=True,
        help_text="Alias for selected_answer for compatibility"
    )
    text_answer = models.TextField(blank=True, null=True, help_text="Text answer for open-ended questions")
    text_response = create_text_field(blank=True, help_text="Alias for text_answer for compatibility")
    is_correct = models.BooleanField(default=False, help_text="Whether the answer is correct")
    points_earned = models.PositiveIntegerField(default=0, help_text="Points earned for this answer")
    feedback = models.TextField(blank=True, null=True, help_text="Instructor feedback for this answer")
    answered_at = models.DateTimeField(auto_now_add=True, help_text="When answer was submitted")

    def save(self, *args, **kwargs):
        """Enhanced save with field synchronization and automatic correctness checking"""
        # Synchronize selected_answer and answer fields for backward compatibility
        if self.selected_answer and not self.answer:
            self.answer = self.selected_answer
        elif self.answer and not self.selected_answer:
            self.selected_answer = self.answer

        # Synchronize text_answer and text_response fields for backward compatibility
        if self.text_answer and not self.text_response:
            self.text_response = self.text_answer
        elif self.text_response and not self.text_answer:
            self.text_answer = self.text_response

        # Automatic correctness checking for multiple choice questions
        if self.answer and self.question.question_type in ["multiple_choice", "true_false"]:
            self.is_correct = self.answer.is_correct
            self.points_earned = self.question.points if self.is_correct else 0

        super().save(*args, **kwargs)

    def clean(self):
        """Enhanced validation for attempt answer"""
        super().clean()
        if self.question.question_type in ["multiple_choice", "true_false"]:
            if not self.answer:
                raise ValidationError("Selected answer is required for this question type")
        elif self.question.question_type in ["short_answer", "essay"]:
            if not self.text_response:
                raise ValidationError("Text answer is required for this question type")

    def __str__(self):
        return f"Answer to {self.question} in {self.attempt}"

    class Meta:
        app_label = 'courses'
        verbose_name = "Attempt Answer"
        verbose_name_plural = "Attempt Answers"
        ordering = ["attempt", "question"]
        indexes = [
            models.Index(fields=["attempt", "question"]),
            models.Index(fields=["is_correct"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['attempt', 'question'], name='unique_attempt_answer'),
        ]


# =====================================
# REVIEW MODEL
# =====================================

class Review(TimeStampedMixin):
    """Enhanced review model with comprehensive validation and moderation"""

    user = create_foreign_key(
        settings.AUTH_USER_MODEL,
        "course_reviews",
        help_text="User who wrote the review"
    )
    course = create_foreign_key(
        'Course',
        "reviews",
        help_text="Course being reviewed"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Review title")
    content = create_text_field(min_len=10, help_text="Review content (minimum 10 characters)")
    helpful_count = models.PositiveIntegerField(default=0, help_text="Number of users who found this review helpful")

    # Moderation fields
    is_verified_purchase = models.BooleanField(default=False, help_text="Whether reviewer is enrolled in the course")
    is_approved = models.BooleanField(default=True, help_text="Whether review is approved for display")
    is_featured = models.BooleanField(default=False, help_text="Whether review is featured")
    moderation_notes = models.TextField(blank=True, null=True, help_text="Internal moderation notes")

    def save(self, *args, **kwargs):
        """Enhanced save with verification check and analytics update"""
        if not self.pk:
            # Import using apps.get_model to avoid circular imports
            try:
                Enrollment = apps.get_model('courses', 'Enrollment')
                self.is_verified_purchase = Enrollment.objects.filter(
                    user=self.user, course=self.course
                ).exists()
            except (DatabaseError, OperationalError) as e:
                logger.error(f"Database error checking enrollment for review: {e}")
                self.is_verified_purchase = False

        super().save(*args, **kwargs)

        try:
            self.course.update_analytics()
        except (AttributeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error updating course analytics from review {self.id}: {e}")

        logger.info(f"Review created: {self.user.username} rated {self.course.title} {self.rating}/5")

    def __str__(self):
        return f"{self.user.username}'s review for {self.course.title}"

    class Meta:
        app_label = 'courses'
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["course", "-created_date"]),
            models.Index(fields=["user", "-created_date"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["is_approved", "is_featured"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_review'),
        ]


# =====================================
# NOTE MODEL
# =====================================

class Note(TimeStampedMixin):
    """Enhanced note model with comprehensive organization and validation"""

    user = create_foreign_key(
        settings.AUTH_USER_MODEL,
        "notes",
        help_text="User who created the note"
    )
    lesson = create_foreign_key(
        'Lesson',
        "notes",
        help_text="Lesson the note is associated with"
    )
    content = create_text_field(min_len=1, help_text="Note content")
    timestamp_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Timestamp in seconds for video notes"
    )
    is_private = models.BooleanField(default=True, help_text="Whether this note is private to the user")
    tags = create_json_field(max_items=10, min_str_len=2, help_text="Tags for organizing notes")

    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.user.username}'s note on {self.lesson.title}: {content_preview}"

    class Meta:
        app_label = 'courses'
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["user", "lesson"]),
            models.Index(fields=["lesson", "is_private"]),
            models.Index(fields=["is_private"]),
        ]


# =====================================
# ANALYTICS AND TRACKING MODELS
# =====================================

class UserActivity(TimeStampedMixin):
    """Track user activities in courses"""

    user = create_foreign_key(
        settings.AUTH_USER_MODEL,
        'course_activities'
    )
    activity_type = create_char_field(
        choices=[
            ('view_course', _('View Course')),
            ('start_lesson', _('Start Lesson')),
            ('complete_lesson', _('Complete Lesson')),
            ('download_resource', _('Download Resource')),
            ('take_quiz', _('Take Quiz')),
            ('post_comment', _('Post Comment')),
            ('give_review', _('Give Review')),
        ]
    )
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    data = create_json_field(default=dict)

    class Meta:
        app_label = 'courses'
        ordering = ['-created_date']
        verbose_name_plural = 'User activities'
        indexes = [
            models.Index(fields=['user', '-created_date']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['course', '-created_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_date}"


class CourseStats(TimeStampedMixin):
    """Aggregate statistics for courses"""

    course = models.OneToOneField('Course', on_delete=models.CASCADE, related_name='stats')
    total_students = models.PositiveIntegerField(default=0)
    active_students = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    average_completion_days = models.PositiveIntegerField(default=0)
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assessment_stats = create_json_field(default=dict)
    revenue_data = create_json_field(default=dict)

    class Meta:
        app_label = 'courses'
        verbose_name_plural = 'Course stats'

    def __str__(self):
        return f"Stats for {self.course.title}"


class UserStats(TimeStampedMixin):
    """Aggregate statistics for users"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_stats')
    courses_enrolled = models.PositiveIntegerField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    total_time_spent_seconds = models.PositiveBigIntegerField(default=0)
    assessment_avg_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    activity_streak = models.PositiveIntegerField(default=0)
    learning_habits = create_json_field(default=dict)

    class Meta:
        app_label = 'courses'
        verbose_name_plural = 'User stats'

    def __str__(self):
        return f"Stats for {self.user.username}"


class Notification(TimeStampedMixin):
    """Course-related notifications for users"""

    user = create_foreign_key(settings.AUTH_USER_MODEL, 'course_notifications')
    title = create_char_field()
    message = create_text_field()
    notification_type = create_char_field(
        choices=[
            ('course_update', _('Course Update')),
            ('reminder', _('Reminder')),
            ('achievement', _('Achievement')),
            ('announcement', _('Announcement')),
            ('feedback', _('Feedback Request')),
            ('custom', _('Custom'))
        ],
        default='announcement'
    )
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)

    class Meta:
        app_label = 'courses'
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['user', '-created_date']),
            models.Index(fields=['is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}: {self.title}"
