# File Path: backend/courses/models/core.py
# Folder Path: backend/courses/models/core.py
# Date Created: 2025-06-26 09:31:25
# Date Revised: 2025-07-13 11:23:50
# Current Date and Time (UTC): 2025-07-13 11:23:50
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-13 11:23:50 UTC
# User: MohithaSanthanam2010
# Version: 5.1.2
#
# CHANGES: Updated to use enum classes directly from constants
# instead of pre-generated choice tuples for better schema generation


from __future__ import annotations

import logging
import re
import uuid
from decimal import Decimal
from typing import Optional

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ..constants import (  # Import the enum classes directly instead of pre-generated choice tuples; Keep value constants that aren't enums
    DEFAULT_COURSE_PRICE,
    AccessLevel,
    CompletionStatus,
    CourseLevel,
    CreationMethod,
    EnrollmentStatus,
    LessonType,
    ResourceType,
)

# Import all helper functions from utils to avoid duplication
from ..utils import (
    create_char_field,
    create_decimal_field,
    create_foreign_key,
    create_json_field,
    create_meta_indexes,
    create_text_field,
    generate_unique_slug,
)
from ..validators import (
    validate_course_requirements,
    validate_duration_minutes,
    validate_learning_objectives,
    validate_percentage,
    validate_price_range,
    validate_video_url,
)
from .mixins import (
    AnalyticsMixin,
    DurationMixin,
    FileTrackingMixin,
    OrderedMixin,
    PublishableMixin,
    SlugMixin,
    StateMixin,
    TimeStampedMixin,
)

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================
# ACTIVITY TYPE ENUMERATION
# =====================================


class ActivityType(models.TextChoices):
    """Types of learning activities users can perform"""

    VIDEO = "video", _("Video")
    READING = "reading", _("Reading")
    QUIZ = "quiz", _("Quiz")
    ASSIGNMENT = "assignment", _("Assignment")
    DISCUSSION = "discussion", _("Discussion")
    INTERACTIVE = "interactive", _("Interactive")
    LIVESTREAM = "livestream", _("Live Stream")
    OTHER = "other", _("Other")


# =====================================
# HELPER FUNCTION FOR CATEGORY MODEL
# =====================================


def get_default_category():
    """
    Get or create default category for courses
    FIXED: Returns Category instance instead of ID for direct FK assignment
    """
    try:
        # Check if any categories exist first
        if not Category.objects.exists():
            # Create a default category if none exist
            category = Category.objects.create(
                name="General",
                description="General category for uncategorized courses",
                is_active=True,
                sort_order=0,
            )
            logger.info("Created default 'General' category")
            return category  # ← Return instance, not ID

        # Find the default category by name first - most reliable approach
        default_category = Category.objects.filter(
            name__iexact="General", is_active=True
        ).first()

        # If a "General" category exists, use it
        if default_category:
            return default_category  # ← Return instance, not ID

        # Otherwise use any active category
        active_category = (
            Category.objects.filter(is_active=True).order_by("sort_order", "id").first()
        )
        if active_category:
            return active_category  # ← Return instance, not ID

        # As a last resort, use any category at all
        any_category = Category.objects.order_by("id").first()
        if any_category:
            return any_category  # ← Return instance, not ID

        # If we somehow got here with no categories, return None to make the field nullable
        logger.warning("No categories found when calling get_default_category()")
        return None

    except Exception as e:
        logger.error(f"Error getting default category: {e}")
        # Let the FK be nullable if absolutely no Category rows exist
        return None


# =====================================
# CATEGORY MODEL
# =====================================


class Category(TimeStampedMixin, SlugMixin, StateMixin):
    """Enhanced course category model with atomic slug generation and name normalization"""

    name = create_char_field(
        100, min_len=2, unique=True, help_text="Category name (minimum 2 characters)"
    )
    description = models.TextField(
        blank=True, default="", help_text="Optional category description"
    )
    icon = models.CharField(
        max_length=50, blank=True, default="", help_text="CSS icon class"
    )
    sort_order = models.PositiveIntegerField(
        default=0, help_text="Sort order for display"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="category_children",
        help_text="Parent category for hierarchy",
    )
    featured = models.BooleanField(
        default=False, help_text="Whether category is featured on homepage"
    )

    slug_source = "name"

    def normalize_name(self, name):
        """Normalize category name for duplicate detection and consistency"""
        if not name:
            return ""

        normalized = name.strip()
        words = normalized.split()
        title_words = []

        lowercase_words = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
        }

        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                title_words.append(word.capitalize())
            else:
                title_words.append(word.lower())

        normalized = " ".join(title_words)

        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"[^\w\s\-&]", "", normalized)

        return normalized.strip()

    def save(self, *args, **kwargs):
        """Enhanced save with atomic slug generation and name normalization"""
        if self.name:
            self.name = self.normalize_name(self.name)

        if not self.slug:
            base_slug = slugify(getattr(self, self.slug_source))
            self.slug = generate_unique_slug(self, base_slug)

        # Use transaction for atomicity
        with transaction.atomic():
            super().save(*args, **kwargs)

    def get_course_count(self) -> int:
        """Get count of active courses in this category"""
        return self.courses.select_related("category").filter(is_published=True).count()

    def get_all_courses(self):
        """Get all courses in this category and its subcategories"""
        from django.db.models import Q

        descendant_ids = self._get_descendant_ids()

        return (
            Course.objects.select_related("category", "parent_version")
            .prefetch_related(
                "instructor_portal_relationships__instructor", "modules__lessons"
            )
            .filter(
                Q(category_id__in=descendant_ids) | Q(category=self), is_published=True
            )
            .distinct()
        )

    def _get_descendant_ids(self):
        """Get all descendant category IDs recursively"""
        descendant_ids = [self.id]
        children = list(
            self.category_children.filter(is_active=True).values_list("id", flat=True)
        )

        for child_id in children:
            try:
                child = Category.objects.get(id=child_id)
                descendant_ids.extend(child._get_descendant_ids())
            except Category.DoesNotExist:
                continue

        return descendant_ids

    def __str__(self) -> str:
        return self.name

    class Meta(TimeStampedMixin.Meta, SlugMixin.Meta, StateMixin.Meta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["sort_order", "name"]
        indexes = create_meta_indexes(
            TimeStampedMixin.Meta, SlugMixin.Meta, StateMixin.Meta
        ) + [
            models.Index(fields=["sort_order"]),
            models.Index(fields=["name"]),
            models.Index(fields=["parent"]),
            # FIXED: Renamed slug index to avoid collision
            models.Index(fields=["slug"], name="category_slug_idx"),
            models.Index(fields=["is_active", "featured"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_category_slug"),
            models.CheckConstraint(
                check=models.Q(sort_order__gte=0), name="category_sort_order_positive"
            ),
        ]


# =====================================
# COURSE MODEL AND RELATED
# =====================================


class AnalyticsCourseMixin:
    """Mixin for course analytics functionality"""

    def update_analytics(self):
        """Update computed analytics fields"""
        try:
            with transaction.atomic():
                course = Course.objects.select_for_update().get(pk=self.pk)

                enrollment_count = course.enrollments.filter(status="active").count()

                review_stats = course.reviews.filter(is_approved=True).aggregate(
                    avg_rating=models.Avg("rating"), total_count=models.Count("id")
                )

                avg_rating = review_stats["avg_rating"] or Decimal("0.0")
                total_reviews = review_stats["total_count"] or 0

                last_enrollment = (
                    course.enrollments.select_related("user")
                    .order_by("-created_date")
                    .first()
                )
                last_enrollment_date = (
                    last_enrollment.created_date if last_enrollment else None
                )

                Course.objects.filter(pk=self.pk).update(
                    enrolled_students_count=enrollment_count,
                    avg_rating=avg_rating,
                    total_reviews=total_reviews,
                    last_enrollment_date=last_enrollment_date,
                )

                self.enrolled_students_count = enrollment_count
                self.avg_rating = avg_rating
                self.total_reviews = total_reviews
                self.last_enrollment_date = last_enrollment_date

                logger.debug(
                    f"Analytics updated for course {self.id}: {enrollment_count} students, {avg_rating} rating"
                )

        except Course.DoesNotExist:
            logger.error(f"Course {self.pk} not found during analytics update")
        except Exception as e:
            logger.error(f"Error updating analytics for course {self.pk}: {e}")


class Course(
    TimeStampedMixin,
    SlugMixin,
    DurationMixin,
    PublishableMixin,
    AnalyticsMixin,
    AnalyticsCourseMixin,
):
    """Enhanced course model with instructor_portal integration"""

    # Basic information
    title = create_char_field(
        160, min_len=3, help_text="Course title (minimum 3 characters)"
    )
    subtitle = create_char_field(
        255, blank=True, default="", help_text="Optional course subtitle"
    )
    description = create_text_field(
        min_len=50, help_text="Course description (minimum 50 characters)"
    )
    category = create_foreign_key(
        Category,
        "courses",
        default=get_default_category,
        null=True,
        help_text="Course category",
    )

    # Media and pricing
    thumbnail = models.ImageField(
        upload_to="course_thumbnails/",
        blank=True,
        null=True,
        help_text="Course thumbnail",
    )
    price = create_decimal_field(
        max_digits=8,
        decimal_places=2,
        default=Decimal(str(DEFAULT_COURSE_PRICE)),
        validators=[MinValueValidator(Decimal("0")), validate_price_range],
        help_text="Course price (decimal precision)",
    )
    discount_price = create_decimal_field(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), validate_price_range],
        help_text="Discounted price (optional, decimal precision)",
    )
    discount_ends = models.DateTimeField(
        null=True, blank=True, help_text="Discount expiration date"
    )

    # Course metadata
    level = models.CharField(
        max_length=20,
        choices=CourseLevel.choices(),  # Updated to use enum class directly
        default=CourseLevel.ALL_LEVELS.code,
        help_text="Course difficulty level",
    )

    # Features and content structure
    has_certificate = models.BooleanField(
        default=False, help_text="Whether course offers completion certificate"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Whether course is featured on homepage"
    )

    # Course content metadata
    requirements = create_json_field(
        max_items=20, min_str_len=3, help_text="List of course requirements"
    )
    skills = create_json_field(
        max_items=15, min_str_len=2, help_text="List of skills students will learn"
    )
    learning_objectives = create_json_field(
        max_items=15, min_str_len=5, help_text="List of learning objectives"
    )
    target_audience = models.TextField(
        blank=True, default="", help_text="Description of target audience"
    )

    # Creation and completion tracking
    creation_method = models.CharField(
        max_length=20,
        choices=CreationMethod.choices(),  # Updated to use enum class directly
        default=CreationMethod.BUILDER.code,
        help_text="Method used to create course",
    )
    completion_status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices(),  # Updated to use enum class directly
        default=CompletionStatus.NOT_STARTED.code,
        help_text="Course completion status",
    )
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Completion percentage (0-100)",
    )

    # Versioning and draft management
    version = create_decimal_field(
        max_digits=4,
        decimal_places=1,
        default=Decimal("1.0"),
        help_text="Course version number (decimal precision)",
    )
    is_draft = models.BooleanField(
        default=True, help_text="Whether course is in draft state"
    )
    parent_version = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="course_versions",
        help_text="Parent course version for cloned courses",
    )

    # SEO and meta fields
    meta_keywords = create_char_field(
        max_length=255, blank=True, default="", help_text="SEO meta keywords"
    )
    meta_description = create_text_field(
        blank=True, default="", help_text="SEO meta description"
    )

    # For sorting in catalog listings
    sort_order = models.PositiveIntegerField(
        default=0, help_text="Sort order for catalog display"
    )

    # Analytics (computed fields for performance)
    enrolled_students_count = models.PositiveIntegerField(
        default=0, help_text="Cached count of enrolled students"
    )
    avg_rating = create_decimal_field(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Average rating from reviews (decimal precision)",
    )
    total_reviews = models.PositiveIntegerField(
        default=0, help_text="Total number of reviews"
    )
    last_enrollment_date = models.DateTimeField(
        null=True, blank=True, help_text="Date of last student enrollment"
    )

    slug_source = "title"

    def clean(self):
        """Enhanced validation for course data"""
        super().clean()

        if self.discount_price and self.price and self.discount_price >= self.price:
            raise ValidationError("Discount price must be less than regular price")

        if self.version <= 0:
            raise ValidationError("Version must be greater than 0")

        if self.learning_objectives:
            validate_learning_objectives(self.learning_objectives)

        if self.requirements:
            validate_course_requirements(self.requirements)

    def save(self, *args, **kwargs):
        """Enhanced save with atomic slug generation and validation"""
        try:
            with transaction.atomic():
                if not self.slug:
                    base_slug = slugify(getattr(self, self.slug_source))
                    self.slug = generate_unique_slug(self, base_slug)

                if self.is_published and not self.published_date:
                    self.published_date = timezone.now()

                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving course {getattr(self, 'id', 'new')}: {e}")
            raise

    @property
    def rating(self):
        """Compatibility property for existing code"""
        return float(self.avg_rating)

    @property
    def enrolled_students(self):
        """Compatibility property for existing code"""
        return self.enrolled_students_count

    def get_effective_price(self):
        """Return the current effective price accounting for sales"""
        if self.discount_price and (
            self.discount_ends is None or self.discount_ends > timezone.now()
        ):
            return self.discount_price
        return self.price

    def clone_version(self, creator, **kwargs):
        """Enhanced course cloning with comprehensive options"""
        clone_options = {
            "copy_modules": True,
            "copy_resources": True,
            "copy_assessments": True,
            "create_as_draft": True,
            **kwargs,
        }

        try:
            with transaction.atomic():
                original_id, original_title = self.pk, self.title

                self.pk = self.id = None
                self.version = self._get_next_version_number()
                self.is_draft = clone_options["create_as_draft"]
                self.is_published = False
                self.parent_version_id = original_id

                reset_fields = {
                    "completion_status": CompletionStatus.NOT_STARTED.code,  # Updated to use enum
                    "completion_percentage": 0,
                    "enrolled_students_count": 0,
                    "avg_rating": Decimal("0.00"),
                    "total_reviews": 0,
                    "published_date": None,
                    "last_enrollment_date": None,
                }

                for field, value in reset_fields.items():
                    setattr(self, field, value)

                base_slug = slugify(self.title)
                self.slug = generate_unique_slug(self, base_slug)

                self.save()

                cloned_course = self
                original_course = (
                    Course.objects.select_related("category")
                    .prefetch_related(
                        "instructor_portal_relationships__instructor"  # UPDATED: Use instructor_portal relationship
                    )
                    .get(pk=original_id)
                )

                # Copy instructor relationships - UPDATED: Use instructor_portal.CourseInstructor
                from instructor_portal.models import CourseInstructor

                instructor_relations = []
                for (
                    instructor_rel
                ) in original_course.instructor_portal_relationships.select_related(
                    "instructor"
                ).all():
                    instructor_relations.append(
                        CourseInstructor(
                            course=cloned_course,
                            instructor=instructor_rel.instructor,
                            role=instructor_rel.role,
                            is_lead=instructor_rel.is_lead,
                            is_active=instructor_rel.is_active,
                            can_edit_content=instructor_rel.can_edit_content,
                            can_manage_students=instructor_rel.can_manage_students,
                            can_view_analytics=instructor_rel.can_view_analytics,
                            revenue_share_percentage=instructor_rel.revenue_share_percentage,
                        )
                    )

                CourseInstructor.objects.bulk_create(
                    instructor_relations, ignore_conflicts=True
                )

                # Ensure creator is an instructor
                CourseInstructor.objects.get_or_create(
                    course=cloned_course,
                    instructor=creator,
                    defaults={
                        "role": CourseInstructor.Role.PRIMARY,
                        "is_lead": True,
                        "is_active": True,
                        "can_edit_content": True,
                        "can_manage_students": True,
                        "can_view_analytics": True,
                    },
                )

                if clone_options["copy_modules"]:
                    self._copy_modules(original_course, cloned_course, clone_options)

                logger.info(
                    f"Course cloned: {original_title} -> {cloned_course.title} by {creator.username}"
                )

            return cloned_course

        except Exception as e:
            logger.error(f"Error cloning course {self.id}: {e}")
            raise

    def _copy_modules(self, source_course, target_course, options):
        """Copy modules, lessons, and related content"""
        try:
            modules_to_create = []
            for module in source_course.modules.order_by("order"):
                modules_to_create.append(
                    Module(
                        course=target_course,
                        title=module.title,
                        description=module.description,
                        order=module.order,
                        duration_minutes=module.duration_minutes,
                        is_published=False,
                    )
                )

            created_modules = Module.objects.bulk_create(modules_to_create)

            module_mapping = {}
            for old_module, new_module in zip(
                source_course.modules.order_by("order"), created_modules
            ):
                module_mapping[old_module.id] = new_module

            for old_module_id, new_module in module_mapping.items():
                old_module = Module.objects.get(id=old_module_id)
                lessons_to_create = []

                for lesson in old_module.lessons.order_by("order"):
                    lessons_to_create.append(
                        Lesson(
                            module=new_module,
                            title=lesson.title,
                            content=lesson.content,
                            guest_content=lesson.guest_content or "",
                            registered_content=lesson.registered_content or "",
                            access_level=lesson.access_level,
                            duration_minutes=lesson.duration_minutes,
                            type=lesson.type,
                            order=lesson.order,
                            has_assessment=lesson.has_assessment,
                            has_lab=lesson.has_lab,
                            is_free_preview=lesson.is_free_preview,
                            video_url=getattr(lesson, "video_url", "") or "",
                            transcript=getattr(lesson, "transcript", "") or "",
                        )
                    )

                created_lessons = Lesson.objects.bulk_create(lessons_to_create)

                for old_lesson, new_lesson in zip(
                    old_module.lessons.order_by("order"), created_lessons
                ):
                    if options.get("copy_resources", True):
                        self._copy_resources(old_lesson, new_lesson)

                    if (
                        options.get("copy_assessments", True)
                        and old_lesson.has_assessment
                    ):
                        self._copy_assessment(old_lesson, new_lesson)

        except Exception as e:
            logger.error(f"Error copying modules: {e}")
            raise

    def _copy_resources(self, source_lesson, target_lesson):
        """Copy lesson resources"""
        try:
            resources_to_create = []
            for resource in source_lesson.resources.order_by("order"):
                resources_to_create.append(
                    Resource(
                        lesson=target_lesson,
                        title=resource.title,
                        type=resource.type,
                        url=resource.url or "",
                        description=resource.description or "",
                        premium=resource.premium,
                        order=resource.order,
                        file_size=resource.file_size,
                        duration_minutes=resource.duration_minutes,
                    )
                )

            if resources_to_create:
                Resource.objects.bulk_create(resources_to_create)

        except Exception as e:
            logger.warning(
                f"Error copying resources for lesson {source_lesson.id}: {e}"
            )

    def _copy_assessment(self, source_lesson, target_lesson):
        """Copy assessment and related questions/answers using apps.get_model to avoid circular imports"""
        try:
            # Use apps.get_model to avoid circular imports
            Assessment = apps.get_model("courses", "Assessment")
            Question = apps.get_model("courses", "Question")
            Answer = apps.get_model("courses", "Answer")

            if hasattr(source_lesson, "assessment"):
                source_assessment = source_lesson.assessment

                cloned_assessment = Assessment.objects.create(
                    lesson=target_lesson,
                    title=source_assessment.title,
                    description=source_assessment.description or "",
                    passing_score=source_assessment.passing_score,
                    max_attempts=source_assessment.max_attempts,
                    time_limit_minutes=getattr(
                        source_assessment,
                        "time_limit_minutes",
                        getattr(source_assessment, "time_limit", 0),
                    ),
                    randomize_questions=getattr(
                        source_assessment, "randomize_questions", False
                    ),
                    show_results=getattr(source_assessment, "show_results", True),
                )

                questions_to_create = []
                for question in source_assessment.questions.order_by("order"):
                    questions_to_create.append(
                        Question(
                            assessment=cloned_assessment,
                            text=getattr(
                                question, "text", getattr(question, "question_text", "")
                            )
                            or "",
                            question_type=getattr(
                                question,
                                "question_type",
                                getattr(question, "type", "multiple_choice"),
                            ),
                            order=question.order,
                            points=getattr(question, "points", 1),
                            feedback=getattr(
                                question,
                                "feedback",
                                getattr(question, "explanation", ""),
                            )
                            or "",
                        )
                    )

                created_questions = Question.objects.bulk_create(questions_to_create)

                for old_question, new_question in zip(
                    source_assessment.questions.order_by("order"), created_questions
                ):
                    answers_to_create = []
                    for answer in old_question.answers_question.all():
                        answers_to_create.append(
                            Answer(
                                question=new_question,
                                text=getattr(
                                    answer, "text", getattr(answer, "answer_text", "")
                                )
                                or "",
                                is_correct=answer.is_correct,
                                explanation=getattr(answer, "explanation", "") or "",
                                order=getattr(answer, "order", 0),
                            )
                        )

                    if answers_to_create:
                        Answer.objects.bulk_create(answers_to_create)

        except (AttributeError, Exception) as e:
            logger.warning(
                f"Assessment copying failed for lesson {source_lesson.id}: {e}"
            )

    def _get_next_version_number(self):
        """Get next version number in the version family"""
        try:
            root_course = self.parent_version or self
            max_version_query = Course.objects.filter(
                models.Q(id=root_course.id) | models.Q(parent_version=root_course)
            ).aggregate(max_version=models.Max("version"))

            max_version = max_version_query["max_version"] or Decimal("1.0")
            return max_version + Decimal("0.1")

        except Exception as e:
            logger.error(f"Error calculating next version number: {e}")
            return Decimal("1.1")

    def get_instructors(self):
        """Get course instructors from instructor_portal app"""
        # UPDATED: Use instructor_portal.CourseInstructor relationship
        return (
            self.instructor_portal_relationships.select_related("instructor")
            .filter(is_active=True)
            .order_by("-is_lead", "joined_date")
        )

    def clone(self, title=None, creator=None, draft=True):
        """Create a clone of this course with a simpler API for external use"""
        # Delegate to the more comprehensive clone_version method
        clone_title = title or f"{self.title} (Copy)"
        return self.clone_version(
            creator=creator,
            title=clone_title,
            create_as_draft=draft,
            copy_modules=True,
            copy_resources=True,
            copy_assessments=True,
        )

    def __str__(self):
        version_info = f" (v{self.version})" if self.version > Decimal("1.0") else ""
        draft_info = " [DRAFT]" if self.is_draft else ""
        return f"{self.title}{version_info}{draft_info}"

    class Meta(
        TimeStampedMixin.Meta,
        SlugMixin.Meta,
        DurationMixin.Meta,
        PublishableMixin.Meta,
        AnalyticsMixin.Meta,
    ):
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-created_date"]
        indexes = create_meta_indexes(
            TimeStampedMixin.Meta,
            SlugMixin.Meta,
            PublishableMixin.Meta,
            AnalyticsMixin.Meta,
        ) + [
            models.Index(fields=["category", "is_published"]),
            models.Index(fields=["is_featured", "is_published"]),
            models.Index(fields=["level", "is_published"]),
            models.Index(fields=["parent_version", "version"]),
            models.Index(fields=["creation_method"]),
            models.Index(fields=["completion_status"]),
            models.Index(fields=["is_draft"]),
            models.Index(fields=["price"]),
            models.Index(fields=["avg_rating"]),
            # FIXED: Renamed slug index to avoid collision
            models.Index(fields=["slug"], name="course_slug_idx"),
            # FIXED: Added proper index names for compound indexes
            models.Index(
                fields=["is_published", "completion_status"],
                name="idx_course_pub_status",
            ),
            models.Index(
                fields=["is_featured", "sort_order"], name="idx_course_feat_sort"
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_course_slug"),
            models.CheckConstraint(
                check=models.Q(price__gte=0), name="course_price_positive"
            ),
            models.CheckConstraint(
                check=models.Q(discount_price__gte=0)
                | models.Q(discount_price__isnull=True),
                name="course_discount_price_positive",
            ),
            models.CheckConstraint(
                check=models.Q(version__gt=0), name="course_version_positive"
            ),
            models.CheckConstraint(
                check=models.Q(discount_price__isnull=True)
                | models.Q(discount_price__lt=models.F("price")),
                name="course_discount_less_than_price",
            ),
        ]


# =====================================
# MODULE MODEL
# =====================================


class Module(TimeStampedMixin, OrderedMixin, DurationMixin, PublishableMixin):
    """
    Enhanced module model with proper ordering and validation
    FIXED: Removed invalid parent_field from Meta class
    """

    course = create_foreign_key(Course, "modules", help_text="Parent course")
    title = create_char_field(
        255, min_len=2, help_text="Module title (minimum 2 characters)"
    )
    description = models.TextField(
        blank=True, default="", help_text="Module description"
    )

    def get_next_order(self, parent_field=None):
        """
        Get next order number for this module's course
        FIXED: Override method to provide course-specific ordering
        """
        try:
            if not self.course:
                return 1

            with transaction.atomic():
                last_order = (
                    Module.objects.select_for_update()
                    .filter(course=self.course)
                    .aggregate(max_order=models.Max("order"))["max_order"]
                    or 0
                )
                return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for module: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        try:
            with transaction.atomic():
                if not self.pk and (not self.order or self.order == 0):
                    self.order = self.get_next_order()
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving module {getattr(self, 'id', 'new')}: {e}")
            raise

    def get_lessons(self):
        """Get lessons with optimization"""
        return self.lessons.select_related("module").order_by("order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta(
        TimeStampedMixin.Meta,
        OrderedMixin.Meta,
        DurationMixin.Meta,
        PublishableMixin.Meta,
    ):
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ["course", "order"]
        indexes = create_meta_indexes(
            TimeStampedMixin.Meta, OrderedMixin.Meta, PublishableMixin.Meta
        ) + [
            models.Index(fields=["course", "order"]),
            models.Index(fields=["course", "is_published"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"], name="unique_module_order"
            ),
        ]


# =====================================
# LESSON MODEL
# =====================================


class Lesson(TimeStampedMixin, OrderedMixin, DurationMixin):
    """
    Enhanced lesson model with tiered content access and validation
    FIXED: Removed invalid parent_field from Meta class
    """

    module = create_foreign_key(Module, "lessons", help_text="Parent module")
    title = create_char_field(
        255, min_len=2, help_text="Lesson title (minimum 2 characters)"
    )

    # Content fields for tiered access
    content = create_text_field(
        min_len=10,
        help_text="Full content visible to authorized users (minimum 10 characters)",
    )
    guest_content = models.TextField(
        blank=True, default="", help_text="Preview content for unregistered users"
    )
    registered_content = models.TextField(
        blank=True, default="", help_text="Limited content for registered users"
    )

    # Access control and metadata
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices(),  # Updated to use enum class directly
        default=AccessLevel.REGISTERED.code,
        help_text="Minimum access level required to view this lesson",
    )
    type = models.CharField(
        max_length=20,
        choices=LessonType.choices(),  # Updated to use enum class directly
        default=LessonType.VIDEO.code,
        help_text="Type of lesson content",
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.VIDEO,
        help_text="Type of learning activity in this lesson",
    )

    # Lesson features
    has_assessment = models.BooleanField(
        default=False, help_text="Whether lesson includes an assessment"
    )
    has_lab = models.BooleanField(
        default=False, help_text="Whether lesson includes a lab exercise"
    )
    is_free_preview = models.BooleanField(
        default=False, help_text="Whether lesson is available as free preview"
    )

    # Media content
    video_url = models.URLField(
        blank=True,
        default="",
        validators=[validate_video_url],
        help_text="URL for video content",
    )
    transcript = models.TextField(
        blank=True, default="", help_text="Video transcript or lesson transcript"
    )

    def get_next_order(self, parent_field=None):
        """
        Get next order number for this lesson's module
        FIXED: Override method to provide module-specific ordering
        """
        try:
            if not self.module:
                return 1

            with transaction.atomic():
                last_order = (
                    Lesson.objects.select_for_update()
                    .filter(module=self.module)
                    .aggregate(max_order=models.Max("order"))["max_order"]
                    or 0
                )
                return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for lesson: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        try:
            with transaction.atomic():
                if not self.pk and (not self.order or self.order == 0):
                    self.order = self.get_next_order()
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving lesson {getattr(self, 'id', 'new')}: {e}")
            raise

    def get_resources(self):
        """Get resources with optimization"""
        return self.resources.order_by("order")

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    class Meta(TimeStampedMixin.Meta, OrderedMixin.Meta, DurationMixin.Meta):
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ["module", "order"]
        indexes = create_meta_indexes(TimeStampedMixin.Meta, OrderedMixin.Meta) + [
            models.Index(fields=["module", "order"]),
            models.Index(fields=["access_level"]),
            models.Index(fields=["type"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["is_free_preview"]),
            models.Index(fields=["has_assessment"]),
            models.Index(fields=["has_lab"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"], name="unique_lesson_order"
            ),
        ]


# =====================================
# RESOURCE MODEL
# =====================================


class Resource(TimeStampedMixin, OrderedMixin, DurationMixin, FileTrackingMixin):
    """
    Enhanced resource model with comprehensive tracking and validation
    FIXED: Removed invalid parent_field from Meta class
    """

    lesson = create_foreign_key(Lesson, "resources", help_text="Parent lesson")
    title = create_char_field(
        255, min_len=2, help_text="Resource title (minimum 2 characters)"
    )
    type = models.CharField(
        max_length=20,
        choices=ResourceType.choices(),  # Updated to use enum class directly
        help_text="Type of resource",
    )
    description = models.TextField(
        blank=True, default="", help_text="Resource description"
    )

    # File and URL fields
    file = models.FileField(
        upload_to="lesson_resources/",
        blank=True,
        null=True,
        help_text="Uploaded file resource",
    )
    url = models.URLField(blank=True, default="", help_text="External URL resource")
    premium = models.BooleanField(
        default=False, help_text="Whether this resource requires premium subscription"
    )
    download_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this resource was downloaded"
    )

    def get_next_order(self, parent_field=None):
        """
        Get next order number for this resource's lesson
        FIXED: Override method to provide lesson-specific ordering
        """
        try:
            if not self.lesson:
                return 1

            with transaction.atomic():
                last_order = (
                    Resource.objects.select_for_update()
                    .filter(lesson=self.lesson)
                    .aggregate(max_order=models.Max("order"))["max_order"]
                    or 0
                )
                return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for resource: {e}")
            return 1

    def clean(self):
        """Enhanced validation for resource data"""
        super().clean()
        if self.type == ResourceType.LINK.code and not self.url:
            raise ValidationError("URL is required for link-type resources")

        file_types_requiring_file = [
            ResourceType.DOCUMENT.code,
            ResourceType.VIDEO.code,
            ResourceType.AUDIO.code,
            ResourceType.IMAGE.code,
        ]
        if self.type in file_types_requiring_file and not (self.file or self.url):
            raise ValidationError(
                f"Resource type '{self.type}' requires an uploaded file or an external URL."
            )

    def save(self, *args, **kwargs):
        """Enhanced save with automatic file metadata extraction"""
        try:
            with transaction.atomic():
                if self.file:
                    self.update_file_metadata(self.file)

                if not self.pk and (not self.order or self.order == 0):
                    self.order = self.get_next_order()

                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving resource {getattr(self, 'id', 'new')}: {e}")
            raise

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    class Meta(
        TimeStampedMixin.Meta,
        OrderedMixin.Meta,
        DurationMixin.Meta,
        FileTrackingMixin.Meta,
    ):
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        ordering = ["lesson", "order"]
        indexes = create_meta_indexes(
            TimeStampedMixin.Meta, OrderedMixin.Meta, FileTrackingMixin.Meta
        ) + [
            models.Index(fields=["lesson", "order"]),
            models.Index(fields=["type"]),
            models.Index(fields=["premium"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"], name="unique_resource_order"
            ),
        ]
