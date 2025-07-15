# File Path: backend/courses/models/analytics.py
# Folder Path: backend/courses/models/analytics.py
# Date Created: 2025-06-26 09:53:34
# Date Revised: 2025-07-02 13:19:30
# Current Date and Time (UTC): 2025-07-02 13:19:30
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-02 13:19:30 UTC
# User: cadsanthanamNew
# Version: 7.1.0
#
import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import DatabaseError, OperationalError, models, transaction
from django.utils.translation import gettext_lazy as _

from ..constants import (
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_PASSING_SCORE,
    QUESTION_TYPE_CHOICES,
)

# Keep import for backward compatibility
from ..utils.model_helpers import (
    create_char_field,
    create_json_field,
    create_text_field,
)
from ..validators import validate_percentage
from .mixins import OrderedMixin, TimeStampedMixin

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================
# ASSESSMENT MODELS
# =====================================


class Assessment(TimeStampedMixin):
    """Enhanced assessment model with comprehensive configuration and validation"""

    lesson = models.OneToOneField(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="assessment",
        db_index=True,
        help_text="Associated lesson",
    )
    title = models.CharField(
        max_length=255,
        blank=False,
        validators=[
            MinLengthValidator(2)
        ],  # FIXED: Changed from MinValueValidator to MinLengthValidator
        help_text="Assessment title (minimum 2 characters)",
    )
    description = models.TextField(
        blank=True, default="", help_text="Assessment description or instructions"
    )

    # Scoring and attempts
    passing_score = models.PositiveIntegerField(
        default=DEFAULT_PASSING_SCORE,
        validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Passing score percentage (0-100)",
    )
    max_attempts = models.PositiveIntegerField(
        default=DEFAULT_MAX_ATTEMPTS,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attempts allowed",
    )

    # Time management - maintain both field names for compatibility
    time_limit = models.PositiveIntegerField(
        default=0, help_text="Time limit in minutes, 0 means no limit"
    )
    time_limit_minutes = models.PositiveIntegerField(
        default=0, help_text="Alias for time_limit for backward compatibility"
    )

    # Configuration options
    randomize_questions = models.BooleanField(
        default=False, help_text="Randomize question order for each attempt"
    )
    show_correct_answers = models.BooleanField(
        default=True, help_text="Show correct answers after completion"
    )
    show_results = models.BooleanField(
        default=True, help_text="Show results immediately after completion"
    )

    def save(self, *args, **kwargs):
        """
        Enhanced save with field synchronization for backward compatibility

        Ensures time_limit and time_limit_minutes are synchronized for compatibility
        with legacy code that might use either field.
        """
        # Synchronize time_limit and time_limit_minutes fields
        if self.time_limit and not self.time_limit_minutes:
            self.time_limit_minutes = self.time_limit
        elif self.time_limit_minutes and not self.time_limit:
            self.time_limit = self.time_limit_minutes

        # Use transaction for atomicity
        with transaction.atomic():
            super().save(*args, **kwargs)

    def clean(self):
        """Enhanced validation for assessment data"""
        super().clean()
        if self.time_limit_minutes < 0:
            raise ValidationError("Time limit must be non-negative")
        if self.passing_score < 0 or self.passing_score > 100:
            raise ValidationError("Passing score must be between 0 and 100")

    def get_questions(self):
        """
        Get questions with optimization

        Uses select_related and prefetch_related to prevent N+1 queries
        when accessing question properties and their related answers.
        """
        return (
            self.questions.select_related("assessment")
            .prefetch_related("answers_question")
            .order_by("order")
        )

    def get_max_score(self):
        """
        Calculate maximum possible score

        Uses DB aggregation instead of Python loop to prevent N+1 query.
        Explicitly handles None result from empty aggregate.
        """
        max_score = self.questions.aggregate(total=models.Sum("points"))["total"]
        return max_score or 0

    def __str__(self):
        return f"Assessment: {self.title}"

    class Meta:
        app_label = "courses"
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        indexes = [
            # Keep only non-implicit indexes to avoid duplication
            models.Index(fields=["passing_score"]),
            # Add index for common query patterns
            models.Index(fields=["show_results", "show_correct_answers"]),
        ]


class Question(TimeStampedMixin, OrderedMixin):
    """
    Enhanced question model with comprehensive validation
    FIXED: Proper OrderedMixin integration with specific exceptions
    """

    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.CASCADE,
        related_name="questions",
        db_index=True,
        help_text="Parent assessment",
    )
    question_text = models.TextField(
        blank=True,
        default="",  # Explicit default for migration compatibility
        help_text="Question text",
    )
    text = models.TextField(
        blank=True,
        default="",  # Explicit default for backward compatibility
        help_text="Alias for question_text for backward compatibility",
    )
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("multiple_choice", _("Multiple Choice")),
            ("true_false", _("True/False")),
            ("short_answer", _("Short Answer")),
            ("essay", _("Essay")),
            ("matching", _("Matching")),
            ("fill_blank", _("Fill in the Blank")),
        ],
        default="multiple_choice",
        help_text="Type of question",
    )
    points = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Points awarded for correct answer",
    )
    # Set default to 1 since "first child becomes 1" (per mixins.py comment)
    order = models.PositiveIntegerField(
        default=1
    )  # FIXED: Changed to 1 for consistency with comment
    explanation = models.TextField(
        blank=True,
        default="",  # Explicit default
        help_text="Explanation shown after answering",
    )
    feedback = models.TextField(
        blank=True,
        default="",  # Explicit default for backward compatibility
        help_text="Alias for explanation for backward compatibility",
    )

    def get_next_order(self, parent_field="assessment"):
        """
        Get next order number for this question's assessment
        FIXED: Override method to provide assessment-specific ordering
        """
        try:
            if not self.assessment:
                return 1

            # Use select_for_update to prevent duplicate orders in race conditions
            with transaction.atomic():
                last_order = (
                    Question.objects.select_for_update()
                    .filter(assessment=self.assessment)
                    .aggregate(max_order=models.Max("order"))["max_order"]
                    or 0
                )
                return last_order + 1
        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error calculating next order for question: {e}")
            return 1
        except AttributeError as e:
            logger.error(f"Attribute error calculating next order for question: {e}")
            return 1

    def save(self, *args, **kwargs):
        """
        Save the question with field synchronization and automatic ordering

        Synchronizes:
        - text and question_text fields for backward compatibility
        - explanation and feedback fields for backward compatibility
        - Sets order if not provided using OrderedMixin logic
        """
        # Use transaction for atomicity
        try:
            with transaction.atomic():
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

                # FIXED: Set order if not provided using proper OrderedMixin logic with atomic transaction
                if not self.pk and (not self.order or self.order == 0):
                    try:
                        self.order = self.get_next_order()
                    except Exception as e:
                        logger.warning(f"Could not auto-set order for Question: {e}")
                        self.order = 1

                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Question.save(): {e}")
            raise

    @property
    def answers(self):
        """
        Backward compatibility alias for answers_question relation.

        FIXED: Provides compatibility for legacy code that calls question.answers
        instead of question.answers_question.all()
        """
        return self.answers_question.all()

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
        return self.answers_question.select_related("question").order_by("order")

    def __str__(self):
        return f"Question {self.order}: {self.text[:30]}..."

    class Meta:
        app_label = "courses"
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["assessment", "order"]
        indexes = [
            # Use composite index for common query patterns
            models.Index(fields=["assessment", "order"]),
            models.Index(fields=["question_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "order"],
                name="unique_question_order",
                violation_error_message="Question order must be unique per assessment",
            ),
        ]


class Answer(TimeStampedMixin, OrderedMixin):
    """
    Enhanced answer model with comprehensive validation
    FIXED: Single constraints declaration and proper field defaults with order = 1
    """

    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answers_question",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="Parent question",
    )
    answer_text = models.CharField(
        max_length=500,
        validators=[
            MinLengthValidator(1)
        ],  # FIXED: Changed from MinValueValidator to MinLengthValidator
        blank=True,
        default="",  # Explicit default for migration compatibility
        help_text="Answer text (minimum 1 character)",
    )
    text = models.TextField(
        blank=True,
        default="",  # Explicit default for backward compatibility
        help_text="Alias for answer_text for backward compatibility",
    )
    is_correct = models.BooleanField(
        default=False, help_text="Whether this is the correct answer"
    )
    explanation = models.TextField(
        blank=True,
        default="",  # Explicit default
        help_text="Explanation for this answer choice",
    )
    # FIXED: Use default=1 to match OrderedMixin expected behavior
    order = models.PositiveIntegerField(
        default=1, help_text="Display order of this answer"
    )

    def get_next_order(self, parent_field="question"):
        """
        Get next order number for this answer's question
        FIXED: Override method to provide question-specific ordering with locking
        """
        try:
            if not self.question:
                return 1

            # Use select_for_update to prevent duplicate orders in race conditions
            with transaction.atomic():
                last_order = (
                    Answer.objects.select_for_update()
                    .filter(question=self.question)
                    .aggregate(max_order=models.Max("order"))["max_order"]
                    or 0
                )
                return last_order + 1
        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error calculating next order for answer: {e}")
            return 1
        except AttributeError as e:
            logger.error(f"Attribute error calculating next order for answer: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering and field synchronization"""
        try:
            with transaction.atomic():
                # Synchronize text and answer_text fields for backward compatibility
                if self.answer_text and not self.text:
                    self.text = self.answer_text
                elif self.text and not self.answer_text:
                    self.answer_text = self.text

                # Ensure we have some text content
                if not self.answer_text and not self.text:
                    self.answer_text = "Default answer text"
                    self.text = "Default answer text"

                # FIXED: Set order if not provided using proper OrderedMixin logic with atomic transaction
                if (
                    hasattr(self, "_state")
                    and self._state.adding
                    and (self.order in (None, 0))
                ):
                    try:
                        self.order = self.get_next_order()
                    except Exception as e:
                        logger.warning(f"Could not auto-set order for Answer: {e}")
                        self.order = 1

                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Answer.save(): {e}")
            raise

    @property
    def text_property(self):
        """Property to always return answer text"""
        return self.answer_text or self.text or "Default answer text"

    def __str__(self):
        return f"Answer: {self.text_property[:30]}..."

    class Meta:
        app_label = "courses"
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ["question", "order"]
        indexes = [
            # Use composite index for common query patterns
            models.Index(fields=["question", "order"]),
            models.Index(fields=["is_correct"]),
        ]
        # FIXED: Single constraints declaration with custom error message
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_answer_order",
                violation_error_message="Answer order must be unique per question",
            ),
        ]


class AssessmentAttempt(TimeStampedMixin):
    """Enhanced assessment attempt model with comprehensive tracking and validation"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
        db_index=True,
        help_text="User taking the assessment",
    )
    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.CASCADE,
        related_name="attempts",
        db_index=True,
        help_text="Assessment being attempted",
    )

    # Timing
    start_time = models.DateTimeField(
        auto_now_add=True, help_text="When attempt was started"
    )
    end_time = models.DateTimeField(
        blank=True, null=True, help_text="When attempt was completed"
    )
    time_taken_seconds = models.PositiveIntegerField(default=0)

    # Scoring
    score = models.PositiveIntegerField(default=0, help_text="Raw score achieved")
    max_score = models.PositiveIntegerField(default=0)

    # Status - maintain both field names for compatibility
    is_completed = models.BooleanField(default=False)
    is_passed = models.BooleanField(
        default=False, help_text="Whether attempt passed the assessment"
    )
    passed = models.BooleanField(
        default=False, help_text="Alias for is_passed for backward compatibility"
    )
    attempt_number = models.PositiveIntegerField(
        default=1, help_text="Attempt number for this user/assessment combination"
    )

    # Additional tracking
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of the user during attempt"
    )
    user_agent = models.TextField(
        blank=True, default="", help_text="User agent string during attempt"
    )

    def save(self, *args, **kwargs):
        """
        Enhanced save with proper atomic transactions and field synchronization

        Ensures atomic operations for critical updates like attempt numbering
        and synchronizes is_passed and passed fields for backward compatibility.
        """
        try:
            with transaction.atomic():
                # Fields that might be updated
                updated_fields = []

                # Synchronize is_passed and passed fields for backward compatibility
                if self.is_passed != self.passed:
                    if hasattr(self, "_state") and self._state.adding:
                        # New object, prioritize is_passed
                        self.passed = self.is_passed
                        updated_fields.extend(["passed"])
                    else:
                        # Existing object, sync both ways
                        if self.is_passed and not self.passed:
                            self.passed = self.is_passed
                            updated_fields.extend(["passed"])
                        elif self.passed and not self.is_passed:
                            self.is_passed = self.passed
                            updated_fields.extend(["is_passed"])

                # Handle new object creation
                if hasattr(self, "_state") and self._state.adding:
                    # Get last attempt number with select_for_update to prevent race conditions
                    last_attempt = (
                        AssessmentAttempt.objects.select_for_update()
                        .filter(user=self.user, assessment=self.assessment)
                        .order_by("-attempt_number")
                        .first()
                    )

                    self.attempt_number = (
                        (last_attempt.attempt_number + 1) if last_attempt else 1
                    )
                    updated_fields.append("attempt_number")

                    # Check max attempts limit
                    if (
                        self.assessment.max_attempts > 0
                        and self.attempt_number > self.assessment.max_attempts
                    ):
                        raise ValidationError(
                            f"Maximum attempts ({self.assessment.max_attempts}) exceeded"
                        )

                    # Set max_score using DB aggregation
                    if not self.max_score and self.assessment:
                        try:
                            self.max_score = self.assessment.get_max_score()
                            updated_fields.append("max_score")
                        except (AttributeError, DatabaseError, OperationalError) as e:
                            logger.warning(
                                f"Could not calculate max_score for attempt: {e}"
                            )
                            self.max_score = 0
                            updated_fields.append("max_score")

                # Check if passed based on score percentage
                try:
                    if self.max_score > 0 and self.assessment and self.score > 0:
                        score_percentage = (self.score / self.max_score) * 100
                        was_passed = self.is_passed

                        if score_percentage >= self.assessment.passing_score:
                            self.is_passed = True
                            self.passed = True
                            if not was_passed:
                                updated_fields.extend(["is_passed", "passed"])
                except (AttributeError, ZeroDivisionError) as e:
                    logger.warning(
                        f"Could not calculate passing status for attempt: {e}"
                    )

                # Call super().save() with update_fields if we're updating specific fields
                if updated_fields and not self._state.adding:
                    kwargs["update_fields"] = list(
                        set(updated_fields + kwargs.get("update_fields", []))
                    )

                super().save(*args, **kwargs)

        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error in AssessmentAttempt.save(): {e}")
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AssessmentAttempt.save(): {e}")
            raise

    @property
    def score_percentage(self):
        """
        Calculate score percentage with caching

        Uses cached value if available to avoid repeated calculations
        and DB queries. Includes fallbacks for error conditions.
        """
        # Return cached value if available
        if hasattr(self, "_score_percentage_cache"):
            return self._score_percentage_cache

        try:
            if self.max_score > 0:
                result = round((self.score / self.max_score) * 100, 1)
                self._score_percentage_cache = result
                return result

            # Fallback to assessment questions if max_score not set
            if self.assessment and not hasattr(self, "_max_score"):
                self._max_score = (
                    self.assessment.questions.aggregate(
                        total_points=models.Sum("points")
                    )["total_points"]
                    or 0
                )

                if self._max_score > 0:
                    result = round((self.score / self._max_score) * 100, 1)
                    self._score_percentage_cache = result
                    return result

                self._score_percentage_cache = 0
                return 0

            self._score_percentage_cache = 0
            return 0
        except (
            DatabaseError,
            OperationalError,
            AttributeError,
            ZeroDivisionError,
        ) as e:
            logger.error(
                f"Error calculating score percentage for attempt {self.id}: {e}"
            )
            self._score_percentage_cache = 0
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
        app_label = "courses"
        verbose_name = "Assessment Attempt"
        verbose_name_plural = "Assessment Attempts"
        ordering = ["-created_date"]
        indexes = [
            # Use composite indexes that include filtering columns
            models.Index(fields=["user", "assessment"]),
            models.Index(fields=["assessment", "-created_date"]),
            # Add index for is_completed status
            models.Index(fields=["is_completed", "is_passed"]),
        ]


class AttemptAnswer(TimeStampedMixin):
    """Enhanced attempt answer model with comprehensive validation"""

    attempt = models.ForeignKey(
        "AssessmentAttempt",
        on_delete=models.CASCADE,
        related_name="answers_attempt",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="Associated assessment attempt",
    )
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="user_answers",
        db_index=True,
        help_text="Question being answered",
    )
    # FIXED: Maintain only one DB field and expose the other as a property
    selected_answer = models.ForeignKey(
        "Answer",
        on_delete=models.CASCADE,
        related_name="user_selections",
        blank=True,
        null=True,
        help_text="Selected answer for multiple choice questions",
    )

    # FIXED: Property instead of duplicate field
    @property
    def answer(self):
        return self.selected_answer

    @answer.setter
    def answer(self, value):
        self.selected_answer = value

    text_answer = models.TextField(
        blank=True, default="", help_text="Text answer for open-ended questions"
    )

    # FIXED: Property instead of duplicate field
    @property
    def text_response(self):
        return self.text_answer

    @text_response.setter
    def text_response(self, value):
        self.text_answer = value

    is_correct = models.BooleanField(
        default=False, help_text="Whether the answer is correct"
    )
    points_earned = models.PositiveIntegerField(
        default=0, help_text="Points earned for this answer"
    )
    feedback = models.TextField(
        blank=True, default="", help_text="Instructor feedback for this answer"
    )
    answered_at = models.DateTimeField(
        auto_now_add=True, help_text="When answer was submitted"
    )

    def save(self, *args, **kwargs):
        """
        Enhanced save with automatic correctness checking

        Uses transaction to ensure atomicity and select_related to prevent
        N+1 queries when checking question types and correctness.
        """
        try:
            with transaction.atomic():
                # Fetch question with select_related if needed
                if self.selected_answer:
                    # Check if question is already loaded
                    if not hasattr(self, "question") or not hasattr(
                        self.question, "question_type"
                    ):
                        # Fetch question with select_related to prevent N+1 query
                        question = Question.objects.select_related().get(
                            id=self.question_id
                        )
                    else:
                        question = self.question

                    # Automatic correctness checking for multiple choice questions
                    if question.question_type in ["multiple_choice", "true_false"]:
                        self.is_correct = self.selected_answer.is_correct
                        self.points_earned = question.points if self.is_correct else 0

                super().save(*args, **kwargs)
        except (DatabaseError, OperationalError) as e:
            logger.error(f"Database error in AttemptAnswer.save(): {e}")
            raise
        except Exception as e:
            logger.error(f"Error in AttemptAnswer.save(): {e}")
            raise

    def clean(self):
        """Enhanced validation for attempt answer"""
        super().clean()
        if self.question.question_type in ["multiple_choice", "true_false"]:
            if not self.selected_answer:
                raise ValidationError(
                    "Selected answer is required for this question type"
                )
        elif self.question.question_type in ["short_answer", "essay"]:
            if not self.text_answer:
                raise ValidationError("Text answer is required for this question type")

    def __str__(self):
        return f"Answer to {self.question} in {self.attempt}"

    class Meta:
        app_label = "courses"
        verbose_name = "Attempt Answer"
        verbose_name_plural = "Attempt Answers"
        ordering = ["attempt", "question"]
        indexes = [
            # Use composite index for common query patterns
            models.Index(fields=["attempt", "question"]),
            models.Index(fields=["is_correct"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"], name="unique_attempt_answer"
            ),
        ]


# =====================================
# REVIEW MODEL
# =====================================


class Review(TimeStampedMixin):
    """Enhanced review model with comprehensive validation and moderation"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        db_index=True,
        help_text="User who wrote the review",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
        help_text="Course being reviewed",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars",
    )
    # FIXED: Use default='' instead of null=True for character fields
    title = models.CharField(
        max_length=255, blank=True, default="", help_text="Review title"
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(10)
        ],  # FIXED: Changed from MinValueValidator to MinLengthValidator
        help_text="Review content (minimum 10 characters)",
    )
    helpful_count = models.PositiveIntegerField(
        default=0, help_text="Number of users who found this review helpful"
    )

    # Moderation fields
    is_verified_purchase = models.BooleanField(
        default=False, help_text="Whether reviewer is enrolled in the course"
    )
    is_approved = models.BooleanField(
        default=True, help_text="Whether review is approved for display"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Whether review is featured"
    )
    moderation_notes = models.TextField(
        blank=True, default="", help_text="Internal moderation notes"
    )

    def save(self, *args, **kwargs):
        """
        Enhanced save with verification check and analytics update

        Only triggers analytics updates when the review is new or rating has changed.
        """
        is_new = not self.pk
        update_analytics = is_new
        old_rating = None

        if not is_new:
            # Check if rating changed on existing review
            try:
                old_review = Review.objects.get(pk=self.pk)
                if old_review.rating != self.rating:
                    update_analytics = True
                    old_rating = old_review.rating
            except (Review.DoesNotExist, DatabaseError, OperationalError) as e:
                logger.warning(f"Could not check for rating change: {e}")
                update_analytics = True

        if is_new:
            # Import using apps.get_model to avoid circular imports
            try:
                Enrollment = apps.get_model("courses", "Enrollment")
                self.is_verified_purchase = Enrollment.objects.filter(
                    user=self.user, course=self.course
                ).exists()
            except (DatabaseError, OperationalError) as e:
                logger.error(f"Database error checking enrollment for review: {e}")
                self.is_verified_purchase = False

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving review: {e}")
            raise

        # Only update analytics when needed
        if update_analytics:
            try:
                self.course.update_analytics()
                if is_new:
                    logger.info(
                        f"Review created: {self.user.username} rated {self.course.title} {self.rating}/5"
                    )
                elif old_rating:
                    logger.info(
                        f"Review updated: {self.user.username} changed rating from {old_rating} to {self.rating}/5"
                    )
            except (AttributeError, DatabaseError, OperationalError) as e:
                logger.error(
                    f"Error updating course analytics from review {self.id}: {e}"
                )

    def __str__(self):
        return f"{self.user.username}'s review for {self.course.title}"

    class Meta:
        app_label = "courses"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_date"]
        indexes = [
            # Use composite indexes for common query patterns
            models.Index(fields=["course", "-created_date"]),
            models.Index(fields=["user", "-created_date"]),
            models.Index(fields=["is_approved", "is_featured"]),
            # Keep rating for potential sorting
            models.Index(fields=["rating"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_user_course_review"
            ),
        ]


# =====================================
# NOTE MODEL
# =====================================


class Note(TimeStampedMixin):
    """Enhanced note model with comprehensive organization and validation"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_notes",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="User who created the note",
    )
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="lesson_notes",  # FIXED: Renamed to avoid collision
        db_index=True,
        help_text="Lesson the note is associated with",
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1)
        ],  # FIXED: Changed from MinValueValidator to MinLengthValidator
        help_text="Note content",
    )
    timestamp_seconds = models.PositiveIntegerField(
        default=0, help_text="Timestamp in seconds for video notes"
    )
    is_private = models.BooleanField(
        default=True, help_text="Whether this note is private to the user"
    )
    tags = create_json_field(
        max_items=10, min_str_len=2, help_text="Tags for organizing notes"
    )

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Note.save(): {e}")
            raise

    def __str__(self):
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"{self.user.username}'s note on {self.lesson.title}: {content_preview}"

    class Meta:
        app_label = "courses"
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-created_date"]
        indexes = [
            # Use composite indexes for common query patterns
            models.Index(fields=["user", "lesson"]),
            models.Index(fields=["lesson", "is_private"]),
            # Remove redundant single-column indexes already covered by composite ones
        ]


# =====================================
# ANALYTICS AND TRACKING MODELS
# =====================================


class UserActivity(TimeStampedMixin):
    """Track user activities in courses"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_activities",
        db_index=True,
    )
    activity_type = models.CharField(
        max_length=255,
        choices=[
            ("view_course", _("View Course")),
            ("start_lesson", _("Start Lesson")),
            ("complete_lesson", _("Complete Lesson")),
            ("download_resource", _("Download Resource")),
            ("take_quiz", _("Take Quiz")),
            ("post_comment", _("Post Comment")),
            ("give_review", _("Give Review")),
        ],
    )
    # FIXED: Renamed related_name to avoid collisions
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="course_activities",
        null=True,
        blank=True,
    )
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="lesson_activities",
        null=True,
        blank=True,
    )
    resource = models.ForeignKey(
        "Resource",
        on_delete=models.CASCADE,
        related_name="resource_activities",
        null=True,
        blank=True,
    )
    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.CASCADE,
        related_name="assessment_activities",
        null=True,
        blank=True,
    )
    data = create_json_field(default=dict)

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in UserActivity.save(): {e}")
            raise

    class Meta:
        app_label = "courses"
        ordering = ["-created_date"]
        verbose_name_plural = "User activities"
        indexes = [
            # Use composite indexes for common query patterns
            models.Index(fields=["user", "-created_date"]),
            models.Index(fields=["course", "-created_date"]),
            # Keep activity_type for potential filtering
            models.Index(fields=["activity_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_date}"


class CourseStats(TimeStampedMixin):
    """Aggregate statistics for courses"""

    course = models.OneToOneField(
        "Course", on_delete=models.CASCADE, related_name="stats"
    )
    total_students = models.PositiveIntegerField(default=0)
    active_students = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    average_completion_days = models.PositiveIntegerField(default=0)
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assessment_stats = create_json_field(default=dict)
    revenue_data = create_json_field(default=dict)

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CourseStats.save(): {e}")
            raise

    class Meta:
        app_label = "courses"
        verbose_name_plural = "Course stats"
        indexes = [
            # Add index for course lookup
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"Stats for {self.course.title}"


class UserStats(TimeStampedMixin):
    """Aggregate statistics for users"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_stats"
    )
    courses_enrolled = models.PositiveIntegerField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    total_time_spent_seconds = models.PositiveBigIntegerField(default=0)
    assessment_avg_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    last_activity = models.DateTimeField(null=True, blank=True)
    activity_streak = models.PositiveIntegerField(default=0)
    learning_habits = create_json_field(default=dict)

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in UserStats.save(): {e}")
            raise

    class Meta:
        app_label = "courses"
        verbose_name_plural = "User stats"
        indexes = [
            # Add index for user lookup
            models.Index(fields=["user"]),
            # Add index for activity streak/date querying
            models.Index(fields=["activity_streak", "last_activity"]),
        ]

    def __str__(self):
        return f"Stats for {self.user.username}"


class Notification(TimeStampedMixin):
    """Course-related notifications for users"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_notifications",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=255,
        choices=[
            ("course_update", _("Course Update")),
            ("reminder", _("Reminder")),
            ("achievement", _("Achievement")),
            ("announcement", _("Announcement")),
            ("feedback", _("Feedback Request")),
            ("custom", _("Custom")),
        ],
        default="announcement",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="course_notifications",
        null=True,
        blank=True,
    )
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        """Enhanced save with transaction for atomicity"""
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Notification.save(): {e}")
            raise

    class Meta:
        app_label = "courses"
        ordering = ["-created_date"]
        indexes = [
            # Use composite indexes for common query patterns
            models.Index(fields=["user", "-created_date"]),
            # Keep single-column indexes for commonly filtered fields
            models.Index(fields=["is_read"]),
            models.Index(fields=["notification_type"]),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}: {self.title}"
