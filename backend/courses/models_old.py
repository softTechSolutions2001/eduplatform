#
# File Path: backend/courses/models.py
# Folder Path: backend/courses/
# Date Created: 2025-06-01 00:00:00
# Date Revised: 2025-06-20 17:20:17
# Current Date and Time (UTC): 2025-06-20 17:20:17
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-20 17:20:17 UTC
# User: sujibeautysalon
# Version: 4.0.0 - REDUNDANCY REMOVED, ENTERPRISE OPTIMIZED
#
# Production-Ready Database Models - Redundancy Removed, Enterprise Optimized
#
# Version 4.0.0 Changes (ENTERPRISE OPTIMIZATION):
# - REMOVED: Redundant CourseInstructor model (replaced by instructor_portal.CourseInstructor)
# - ENHANCED: Cleaner model architecture with single source of truth
# - OPTIMIZED: Reduced model complexity while maintaining all functionality
# - IMPROVED: Better separation of concerns between apps
# - MAINTAINED: Full backward compatibility with existing code

from __future__ import annotations

import hashlib
import logging
import uuid
from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings

from .constants import (
    ACCESS_LEVEL_CHOICES, COMPLETION_STATUSES, CREATION_METHODS,
    DEFAULT_COURSE_PRICE, DEFAULT_MAX_ATTEMPTS, DEFAULT_PASSING_SCORE,
    LEVEL_CHOICES, LESSON_TYPE_CHOICES, QUESTION_TYPE_CHOICES,
    RESOURCE_TYPE_CHOICES, STATUS_CHOICES,
)
from .models.mixins import (
    AnalyticsMixin, DurationMixin, FileTrackingMixin, OrderedMixin,
    PublishableMixin, SlugMixin, StateMixin, TimeStampedMixin,
)
from .validators import (
    JSONListValidator, MinStrLenValidator, validate_course_requirements,
    validate_duration_minutes, validate_learning_objectives,
    validate_percentage, validate_price_range, validate_video_url,
)

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================
# PRODUCTION-READY HELPER FUNCTIONS
# =====================================

def create_meta_indexes(*base_metas):
    """Helper to combine indexes from multiple meta classes"""
    indexes = []
    for meta in base_metas:
        if hasattr(meta, 'indexes'):
            indexes.extend(meta.indexes)
    return indexes


def create_char_field(max_length, min_len=None, **kwargs):
    """Helper to create CharField with validation"""
    validators = []
    if min_len:
        validators.append(MinStrLenValidator(min_len))
    return models.CharField(max_length=max_length, validators=validators, **kwargs)


def create_text_field(min_len=None, **kwargs):
    """Helper to create TextField with validation"""
    validators = []
    if min_len:
        validators.append(MinStrLenValidator(min_len))
    return models.TextField(validators=validators, **kwargs)


def create_json_field(max_items=None, min_str_len=None, **kwargs):
    """Helper to create JSONField with validation and proper defaults"""
    validators = []
    if max_items or min_str_len:
        validators.append(JSONListValidator(max_items=max_items, min_str_len=min_str_len))

    defaults = {
        'default': list,
        'blank': True,
        'null': False,
        'validators': validators
    }
    defaults.update(kwargs)
    return models.JSONField(**defaults)


def create_foreign_key(model, related_name=None, **kwargs):
    """Helper to create ForeignKey with consistent settings"""
    return models.ForeignKey(
        model, on_delete=models.CASCADE,
        related_name=related_name, **kwargs
    )


def create_decimal_field(max_digits, decimal_places, **kwargs):
    """Helper to create DecimalField for financial/version data"""
    return models.DecimalField(
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs
    )


def generate_unique_slug(instance, base_slug: str, max_length: int = 50) -> str:
    """Generate unique slug with enhanced atomic race condition prevention"""
    base_slug = base_slug[:max_length-10]
    unique_slug = base_slug
    counter = 1

    model_class = instance.__class__

    while True:
        try:
            with transaction.atomic():
                queryset = model_class.objects.select_for_update().filter(
                    slug=unique_slug
                )

                if instance.pk:
                    queryset = queryset.exclude(pk=instance.pk)

                if not queryset.exists():
                    return unique_slug

                suffix = f"-{counter}"
                max_base_length = max_length - len(suffix)
                unique_slug = f"{base_slug[:max_base_length]}{suffix}"
                counter += 1

                if counter > 1000:
                    unique_slug = f"{base_slug[:max_length-13]}-{uuid.uuid4().hex[:12]}"
                    logger.warning(f"High slug collision count, using UUID: {unique_slug}")
                    return unique_slug

        except IntegrityError:
            counter += 1
            if counter > 1000:
                unique_slug = f"{base_slug[:max_length-13]}-{uuid.uuid4().hex[:12]}"
                logger.warning(f"IntegrityError in slug generation, using UUID: {unique_slug}")
                return unique_slug
            continue
        except Exception as e:
            logger.error(f"Unexpected error in slug generation: {e}")
            return f"{base_slug[:max_length-13]}-{uuid.uuid4().hex[:12]}"


def generate_certificate_number(course_id: int, user_id: int, timestamp) -> str:
    """Generate unique certificate number with timestamp and UUID component"""
    timestamp_str = timestamp.strftime('%Y%m%d%H%M%S')
    uuid_component = uuid.uuid4().hex[:4]
    return f"CERT-{course_id}-{user_id}-{timestamp_str}-{uuid_component}"


def generate_verification_hash(cert_number: str, enrollment_id: int, timestamp) -> str:
    """Generate SHA-256 verification hash for certificate"""
    data = f"{cert_number}-{enrollment_id}-{timestamp.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


# =====================================
# ENHANCED MODEL DEFINITIONS
# =====================================

class Category(TimeStampedMixin, SlugMixin, StateMixin):
    """Enhanced course category model with atomic slug generation and name normalization"""

    name = create_char_field(100, min_len=2, unique=True, help_text="Category name (minimum 2 characters)")
    description = models.TextField(blank=True, null=True, help_text="Optional category description")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="CSS icon class")
    sort_order = models.PositiveIntegerField(default=0, help_text="Sort order for display")
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='children', help_text="Parent category for hierarchy"
    )

    slug_source = "name"

    def normalize_name(self, name):
        """Normalize category name for duplicate detection and consistency"""
        if not name:
            return ""

        normalized = name.strip()
        words = normalized.split()
        title_words = []

        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}

        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                title_words.append(word.capitalize())
            else:
                title_words.append(word.lower())

        normalized = ' '.join(title_words)

        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'[^\w\s\-&]', '', normalized)

        return normalized.strip()

    def save(self, *args, **kwargs):
        """Enhanced save with atomic slug generation and name normalization"""
        if self.name:
            self.name = self.normalize_name(self.name)

        if not self.slug:
            base_slug = slugify(getattr(self, self.slug_source))
            self.slug = generate_unique_slug(self, base_slug)

        super().save(*args, **kwargs)

    def get_course_count(self) -> int:
        """Get count of active courses in this category"""
        return self.courses.select_related('category').filter(is_published=True).count()

    def get_all_courses(self):
        """Get all courses in this category and its subcategories"""
        from django.db.models import Q

        descendant_ids = self._get_descendant_ids()

        return Course.objects.select_related(
            'category', 'parent_version'
        ).prefetch_related(
            'instructor_portal_relationships__instructor',  # UPDATED: Use instructor_portal relationship
            'modules__lessons'
        ).filter(
            Q(category_id__in=descendant_ids) | Q(category=self),
            is_published=True
        ).distinct()

    def _get_descendant_ids(self):
        """Get all descendant category IDs recursively"""
        descendant_ids = [self.id]
        children = list(self.children.filter(is_active=True).values_list('id', flat=True))

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
        indexes = create_meta_indexes(TimeStampedMixin.Meta, SlugMixin.Meta, StateMixin.Meta) + [
            models.Index(fields=["sort_order"]),
            models.Index(fields=["name"]),
            models.Index(fields=["parent"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_category_slug'),
            models.CheckConstraint(check=models.Q(sort_order__gte=0), name='category_sort_order_positive'),
        ]


def get_default_category():
    """Get or create default category for courses"""
    try:
        category, created = Category.objects.get_or_create(
            name="General",
            defaults={
                'description': 'General category for uncategorized courses',
                'is_active': True,
                'sort_order': 0
            }
        )
        if created:
            logger.info("Created default 'General' category")
        return category.id
    except Exception as e:
        logger.error(f"Error getting default category: {e}")
        return 1


class AnalyticsCourseMixin:
    """Mixin for course analytics functionality"""

    def update_analytics(self):
        """Update computed analytics fields"""
        try:
            with transaction.atomic():
                course = Course.objects.select_for_update().get(pk=self.pk)

                enrollment_count = course.enrollments.filter(status='active').count()

                review_stats = course.reviews.filter(is_approved=True).aggregate(
                    avg_rating=models.Avg('rating'),
                    total_count=models.Count('id')
                )

                avg_rating = review_stats['avg_rating'] or Decimal('0.0')
                total_reviews = review_stats['total_count'] or 0

                last_enrollment = course.enrollments.select_related('user').order_by('-created_date').first()
                last_enrollment_date = last_enrollment.created_date if last_enrollment else None

                Course.objects.filter(pk=self.pk).update(
                    enrolled_students_count=enrollment_count,
                    avg_rating=avg_rating,
                    total_reviews=total_reviews,
                    last_enrollment_date=last_enrollment_date
                )

                self.enrolled_students_count = enrollment_count
                self.avg_rating = avg_rating
                self.total_reviews = total_reviews
                self.last_enrollment_date = last_enrollment_date

                logger.debug(f"Analytics updated for course {self.id}: {enrollment_count} students, {avg_rating} rating")

        except Course.DoesNotExist:
            logger.error(f"Course {self.pk} not found during analytics update")
        except Exception as e:
            logger.error(f"Error updating analytics for course {self.pk}: {e}")


class Course(TimeStampedMixin, SlugMixin, DurationMixin, PublishableMixin, AnalyticsMixin, AnalyticsCourseMixin):
    """Enhanced course model with instructor_portal integration"""

    # Basic information
    title = create_char_field(160, min_len=3, help_text="Course title (minimum 3 characters)")
    subtitle = create_char_field(255, blank=True, null=True, help_text="Optional course subtitle")
    description = create_text_field(min_len=50, help_text="Course description (minimum 50 characters)")
    category = create_foreign_key(Category, "courses", default=get_default_category, help_text="Course category")

    # Media and pricing
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True, help_text="Course thumbnail")
    price = create_decimal_field(
        max_digits=8, decimal_places=2,
        default=Decimal(str(DEFAULT_COURSE_PRICE)),
        validators=[MinValueValidator(Decimal('0')), validate_price_range],
        help_text="Course price (decimal precision)"
    )
    discount_price = create_decimal_field(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), validate_price_range],
        help_text="Discounted price (optional, decimal precision)"
    )
    discount_ends = models.DateTimeField(null=True, blank=True, help_text="Discount expiration date")

    # Course metadata
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="all_levels",
        help_text="Course difficulty level",
    )

    # Features and content structure
    has_certificate = models.BooleanField(default=False, help_text="Whether course offers completion certificate")
    is_featured = models.BooleanField(default=False, help_text="Whether course is featured on homepage")

    # Course content metadata
    requirements = create_json_field(max_items=20, min_str_len=3, help_text="List of course requirements")
    skills = create_json_field(max_items=15, min_str_len=2, help_text="List of skills students will learn")
    learning_objectives = create_json_field(max_items=15, min_str_len=5, help_text="List of learning objectives")
    target_audience = models.TextField(blank=True, null=True, help_text="Description of target audience")

    # Creation and completion tracking
    creation_method = models.CharField(max_length=20, choices=CREATION_METHODS, default="builder", help_text="Method used to create course")
    completion_status = models.CharField(max_length=20, choices=COMPLETION_STATUSES, default="not_started", help_text="Course completion status")
    completion_percentage = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Completion percentage (0-100)"
    )

    # Versioning and draft management
    version = create_decimal_field(
        max_digits=4, decimal_places=1,
        default=Decimal('1.0'),
        help_text="Course version number (decimal precision)"
    )
    is_draft = models.BooleanField(default=True, help_text="Whether course is in draft state")
    parent_version = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="children", help_text="Parent course version for cloned courses"
    )

    # Analytics (computed fields for performance)
    enrolled_students_count = models.PositiveIntegerField(default=0, help_text="Cached count of enrolled students")
    avg_rating = create_decimal_field(
        max_digits=3, decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average rating from reviews (decimal precision)"
    )
    total_reviews = models.PositiveIntegerField(default=0, help_text="Total number of reviews")
    last_enrollment_date = models.DateTimeField(null=True, blank=True, help_text="Date of last student enrollment")

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
        if not self.slug:
            base_slug = slugify(getattr(self, self.slug_source))
            self.slug = generate_unique_slug(self, base_slug)

        if self.is_published and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

    @property
    def rating(self):
        """Compatibility property for existing code"""
        return float(self.avg_rating)

    @property
    def enrolled_students(self):
        """Compatibility property for existing code"""
        return self.enrolled_students_count

    def clone_version(self, creator, **kwargs):
        """Enhanced course cloning with comprehensive options"""
        clone_options = {
            'copy_modules': True,
            'copy_resources': True,
            'copy_assessments': True,
            'create_as_draft': True,
            **kwargs
        }

        try:
            with transaction.atomic():
                original_id, original_title = self.pk, self.title

                self.pk = self.id = None
                self.version = self._get_next_version_number()
                self.is_draft = clone_options['create_as_draft']
                self.is_published = False
                self.parent_version_id = original_id

                reset_fields = {
                    'completion_status': 'not_started',
                    'completion_percentage': 0,
                    'enrolled_students_count': 0,
                    'avg_rating': Decimal('0.00'),
                    'total_reviews': 0,
                    'published_date': None,
                    'last_enrollment_date': None
                }

                for field, value in reset_fields.items():
                    setattr(self, field, value)

                base_slug = slugify(self.title)
                self.slug = generate_unique_slug(self, base_slug)

                self.save()

                cloned_course = self
                original_course = Course.objects.select_related('category').prefetch_related(
                    'instructor_portal_relationships__instructor'  # UPDATED: Use instructor_portal relationship
                ).get(pk=original_id)

                # Copy instructor relationships - UPDATED: Use instructor_portal.CourseInstructor
                from instructor_portal.models import CourseInstructor

                instructor_relations = []
                for instructor_rel in original_course.instructor_portal_relationships.select_related('instructor').all():
                    instructor_relations.append(CourseInstructor(
                        course=cloned_course,
                        instructor=instructor_rel.instructor,
                        role=instructor_rel.role,
                        is_lead=instructor_rel.is_lead,
                        is_active=instructor_rel.is_active,
                        can_edit_content=instructor_rel.can_edit_content,
                        can_manage_students=instructor_rel.can_manage_students,
                        can_view_analytics=instructor_rel.can_view_analytics,
                        revenue_share_percentage=instructor_rel.revenue_share_percentage
                    ))

                CourseInstructor.objects.bulk_create(instructor_relations, ignore_conflicts=True)

                # Ensure creator is an instructor
                CourseInstructor.objects.get_or_create(
                    course=cloned_course,
                    instructor=creator,
                    defaults={
                        'role': CourseInstructor.Role.PRIMARY,
                        'is_lead': True,
                        'is_active': True,
                        'can_edit_content': True,
                        'can_manage_students': True,
                        'can_view_analytics': True
                    }
                )

                if clone_options['copy_modules']:
                    self._copy_modules(original_course, cloned_course, clone_options)

                logger.info(f"Course cloned: {original_title} -> {cloned_course.title} by {creator.username}")

            return cloned_course

        except Exception as e:
            logger.error(f"Error cloning course {self.id}: {e}")
            raise

    def _copy_modules(self, source_course, target_course, options):
        """Copy modules, lessons, and related content"""
        try:
            modules_to_create = []
            for module in source_course.modules.order_by('order'):
                modules_to_create.append(Module(
                    course=target_course,
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    duration_minutes=module.duration_minutes,
                    is_published=False
                ))

            created_modules = Module.objects.bulk_create(modules_to_create)

            module_mapping = {}
            for old_module, new_module in zip(source_course.modules.order_by('order'), created_modules):
                module_mapping[old_module.id] = new_module

            for old_module_id, new_module in module_mapping.items():
                old_module = Module.objects.get(id=old_module_id)
                lessons_to_create = []

                for lesson in old_module.lessons.order_by('order'):
                    lessons_to_create.append(Lesson(
                        module=new_module,
                        title=lesson.title,
                        content=lesson.content,
                        guest_content=lesson.guest_content,
                        registered_content=lesson.registered_content,
                        access_level=lesson.access_level,
                        duration_minutes=lesson.duration_minutes,
                        type=lesson.type,
                        order=lesson.order,
                        has_assessment=lesson.has_assessment,
                        has_lab=lesson.has_lab,
                        is_free_preview=lesson.is_free_preview,
                        video_url=getattr(lesson, 'video_url', ''),
                        transcript=getattr(lesson, 'transcript', '')
                    ))

                created_lessons = Lesson.objects.bulk_create(lessons_to_create)

                for old_lesson, new_lesson in zip(old_module.lessons.order_by('order'), created_lessons):
                    if options.get('copy_resources', True):
                        self._copy_resources(old_lesson, new_lesson)

                    if options.get('copy_assessments', True) and old_lesson.has_assessment:
                        self._copy_assessment(old_lesson, new_lesson)

        except Exception as e:
            logger.error(f"Error copying modules: {e}")
            raise

    def _copy_resources(self, source_lesson, target_lesson):
        """Copy lesson resources"""
        try:
            resources_to_create = []
            for resource in source_lesson.resources.order_by('order'):
                resources_to_create.append(Resource(
                    lesson=target_lesson,
                    title=resource.title,
                    type=resource.type,
                    url=resource.url,
                    description=resource.description,
                    premium=resource.premium,
                    order=resource.order,
                    file_size=resource.file_size,
                    duration_minutes=resource.duration_minutes
                ))

            if resources_to_create:
                Resource.objects.bulk_create(resources_to_create)

        except Exception as e:
            logger.warning(f"Error copying resources for lesson {source_lesson.id}: {e}")

    def _copy_assessment(self, source_lesson, target_lesson):
        """Copy assessment and related questions/answers"""
        try:
            if not hasattr(source_lesson, 'assessment'):
                return

            source_assessment = source_lesson.assessment
            cloned_assessment = Assessment.objects.create(
                lesson=target_lesson,
                title=source_assessment.title,
                description=source_assessment.description,
                time_limit=source_assessment.time_limit,
                passing_score=source_assessment.passing_score,
                max_attempts=source_assessment.max_attempts,
                randomize_questions=source_assessment.randomize_questions,
                show_results=source_assessment.show_results
            )

            questions_to_create = []
            for question in source_assessment.questions.order_by('order'):
                questions_to_create.append(Question(
                    assessment=cloned_assessment,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    order=question.order,
                    points=question.points,
                    explanation=question.explanation or ''
                ))

            created_questions = Question.objects.bulk_create(questions_to_create)

            for old_question, new_question in zip(source_assessment.questions.order_by('order'), created_questions):
                answers_to_create = []
                for answer in old_question.answers.all():
                    answers_to_create.append(Answer(
                        question=new_question,
                        answer_text=answer.answer_text,
                        is_correct=answer.is_correct,
                        explanation=answer.explanation or '',
                        order=answer.order
                    ))

                if answers_to_create:
                    Answer.objects.bulk_create(answers_to_create)

        except (AttributeError, Exception) as e:
            logger.warning(f"Assessment copying failed for lesson {source_lesson.id}: {e}")

    def _get_next_version_number(self):
        """Get next version number in the version family"""
        try:
            root_course = self.parent_version or self
            max_version_query = Course.objects.filter(
                models.Q(id=root_course.id) | models.Q(parent_version=root_course)
            ).aggregate(max_version=models.Max('version'))

            max_version = max_version_query['max_version'] or Decimal('1.0')
            return max_version + Decimal('0.1')

        except Exception as e:
            logger.error(f"Error calculating next version number: {e}")
            return Decimal('1.1')

    def get_instructors(self):
        """Get course instructors from instructor_portal app"""
        # UPDATED: Use instructor_portal.CourseInstructor relationship
        return self.instructor_portal_relationships.select_related('instructor').filter(
            is_active=True
        ).order_by('-is_lead', 'joined_date')

    def __str__(self):
        version_info = f" (v{self.version})" if self.version > Decimal('1.0') else ""
        draft_info = " [DRAFT]" if self.is_draft else ""
        return f"{self.title}{version_info}{draft_info}"

    class Meta(TimeStampedMixin.Meta, SlugMixin.Meta, DurationMixin.Meta, PublishableMixin.Meta, AnalyticsMixin.Meta):
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-created_date"]
        indexes = create_meta_indexes(
            TimeStampedMixin.Meta, SlugMixin.Meta, PublishableMixin.Meta, AnalyticsMixin.Meta
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
        ]
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_course_slug'),
            models.CheckConstraint(check=models.Q(price__gte=0), name='course_price_positive'),
            models.CheckConstraint(check=models.Q(discount_price__gte=0), name='course_discount_price_positive'),
            models.CheckConstraint(check=models.Q(version__gt=0), name='course_version_positive'),
            models.CheckConstraint(
                check=models.Q(discount_price__isnull=True) | models.Q(discount_price__lt=models.F('price')),
                name='course_discount_less_than_price'
            ),
        ]


# =====================================
# REMAINING MODELS (Unchanged)
# =====================================

class Module(TimeStampedMixin, OrderedMixin, DurationMixin, PublishableMixin):
    """Enhanced module model with proper ordering and validation"""

    course = create_foreign_key(Course, "modules", help_text="Parent course")
    title = create_char_field(255, min_len=2, help_text="Module title (minimum 2 characters)")
    description = models.TextField(blank=True, null=True, help_text="Module description")

    def get_next_order(self, parent_field=None):
        """Get next order number for this module's course"""
        try:
            if not self.course:
                return 1

            last_order = Module.objects.filter(course=self.course).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for module: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        if not self.pk and (not self.order or self.order == 1):
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

    def get_lessons(self):
        """Get lessons with optimization"""
        return self.lessons.select_related('module').order_by('order')

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta(TimeStampedMixin.Meta, OrderedMixin.Meta, DurationMixin.Meta, PublishableMixin.Meta):
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
            models.UniqueConstraint(fields=['course', 'order'], name='unique_module_order'),
        ]


class Lesson(TimeStampedMixin, OrderedMixin, DurationMixin):
    """Enhanced lesson model with tiered content access and validation"""

    module = create_foreign_key(Module, "lessons", help_text="Parent module")
    title = create_char_field(255, min_len=2, help_text="Lesson title (minimum 2 characters)")

    # Content fields for tiered access
    content = create_text_field(min_len=10, help_text="Full content visible to authorized users (minimum 10 characters)")
    guest_content = models.TextField(blank=True, null=True, help_text="Preview content for unregistered users")
    registered_content = models.TextField(blank=True, null=True, help_text="Limited content for registered users")

    # Access control and metadata
    access_level = models.CharField(
        max_length=20, choices=ACCESS_LEVEL_CHOICES, default="registered",
        help_text="Minimum access level required to view this lesson"
    )
    type = models.CharField(
        max_length=20, choices=LESSON_TYPE_CHOICES, default="video",
        help_text="Type of lesson content"
    )

    # Lesson features
    has_assessment = models.BooleanField(default=False, help_text="Whether lesson includes an assessment")
    has_lab = models.BooleanField(default=False, help_text="Whether lesson includes a lab exercise")
    is_free_preview = models.BooleanField(default=False, help_text="Whether lesson is available as free preview")

    # Media content
    video_url = models.URLField(
        blank=True, null=True, validators=[validate_video_url],
        help_text="URL for video content"
    )
    transcript = models.TextField(blank=True, null=True, help_text="Video transcript or lesson transcript")

    def get_next_order(self, parent_field=None):
        """Get next order number for this lesson's module"""
        try:
            if not self.module:
                return 1

            last_order = Lesson.objects.filter(module=self.module).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for lesson: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        if not self.pk and (not self.order or self.order == 1):
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

    def get_resources(self):
        """Get resources with optimization"""
        return self.resources.order_by('order')

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
            models.Index(fields=["is_free_preview"]),
            models.Index(fields=["has_assessment"]),
            models.Index(fields=["has_lab"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['module', 'order'], name='unique_lesson_order'),
        ]


class Resource(TimeStampedMixin, OrderedMixin, DurationMixin, FileTrackingMixin):
    """Enhanced resource model with comprehensive tracking and validation"""

    lesson = create_foreign_key(Lesson, "resources", help_text="Parent lesson")
    title = create_char_field(255, min_len=2, help_text="Resource title (minimum 2 characters)")
    type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, help_text="Type of resource")
    description = models.TextField(blank=True, null=True, help_text="Resource description")

    # File and URL fields
    file = models.FileField(upload_to="lesson_resources/", blank=True, null=True, help_text="Uploaded file resource")
    url = models.URLField(blank=True, null=True, help_text="External URL resource")
    premium = models.BooleanField(default=False, help_text="Whether this resource requires premium subscription")

    def get_next_order(self, parent_field=None):
        """Get next order number for this resource's lesson"""
        try:
            if not self.lesson:
                return 1

            last_order = Resource.objects.filter(lesson=self.lesson).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for resource: {e}")
            return 1

    def clean(self):
        """Enhanced validation for resource data"""
        super().clean()
        if self.type == "link" and not self.url:
            raise ValidationError("URL is required for link-type resources")

        file_types_requiring_file = ["document", "video", "audio", "image"]
        if self.type in file_types_requiring_file and not (self.file or self.url):
            raise ValidationError(
                f"Resource type '{self.type}' requires an uploaded file or an external URL."
            )

    def save(self, *args, **kwargs):
        """Enhanced save with automatic file metadata extraction"""
        if self.file:
            self.update_file_metadata(self.file)

        if not self.pk and (not self.order or self.order == 1):
            self.order = self.get_next_order()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    class Meta(TimeStampedMixin.Meta, OrderedMixin.Meta, DurationMixin.Meta, FileTrackingMixin.Meta):
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
            models.UniqueConstraint(fields=['lesson', 'order'], name='unique_resource_order'),
        ]


class Assessment(TimeStampedMixin):
    """Enhanced assessment model with comprehensive configuration and validation"""

    lesson = models.OneToOneField(
        Lesson, on_delete=models.CASCADE, related_name="assessment",
        help_text="Associated lesson"
    )
    title = create_char_field(255, min_len=2, help_text="Assessment title (minimum 2 characters)")
    description = models.TextField(blank=True, null=True, help_text="Assessment description or instructions")
    time_limit = models.PositiveIntegerField(default=0, help_text="Time limit in minutes, 0 means no limit")
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
    randomize_questions = models.BooleanField(default=False, help_text="Randomize question order for each attempt")
    show_results = models.BooleanField(default=True, help_text="Show results immediately after completion")

    def clean(self):
        """Enhanced validation for assessment data"""
        super().clean()
        if self.time_limit < 0:
            raise ValidationError("Time limit must be non-negative")
        if self.passing_score < 0 or self.passing_score > 100:
            raise ValidationError("Passing score must be between 0 and 100")

    def get_questions(self):
        """Get questions with optimization"""
        return self.questions.order_by('order')

    def __str__(self):
        return f"Assessment for {self.lesson.title}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["lesson"]),
            models.Index(fields=["passing_score"]),
        ]


class Question(TimeStampedMixin, OrderedMixin):
    """Enhanced question model with comprehensive validation"""

    assessment = create_foreign_key(Assessment, "questions", help_text="Parent assessment")
    question_text = create_text_field(min_len=5, help_text="Question text (minimum 5 characters)")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, help_text="Type of question")
    points = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)],
        help_text="Points awarded for correct answer"
    )
    explanation = models.TextField(blank=True, null=True, help_text="Explanation shown after answering")

    def get_next_order(self, parent_field=None):
        """Get next order number for this question's assessment"""
        try:
            if not self.assessment:
                return 1

            last_order = Question.objects.filter(assessment=self.assessment).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for question: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        if not self.pk and (not self.order or self.order == 1):
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

    def get_answers(self):
        """Get answers with optimization"""
        return self.answers.order_by('order')

    def __str__(self):
        return f"Question {self.order} for {self.assessment.title}"

    class Meta(TimeStampedMixin.Meta, OrderedMixin.Meta):
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["assessment", "order"]
        indexes = create_meta_indexes(TimeStampedMixin.Meta, OrderedMixin.Meta) + [
            models.Index(fields=["assessment", "order"]),
            models.Index(fields=["question_type"]),
            models.Index(fields=["points"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['assessment', 'order'], name='unique_question_order'),
        ]


class Answer(TimeStampedMixin, OrderedMixin):
    """Enhanced answer model with comprehensive validation"""

    question = create_foreign_key(Question, "answers", help_text="Parent question")
    answer_text = create_char_field(500, min_len=1, help_text="Answer text (minimum 1 character)")
    is_correct = models.BooleanField(default=False, help_text="Whether this is the correct answer")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for this answer choice")

    def get_next_order(self, parent_field=None):
        """Get next order number for this answer's question"""
        try:
            if not self.question:
                return 1

            last_order = Answer.objects.filter(question=self.question).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            return last_order + 1
        except Exception as e:
            logger.error(f"Error calculating next order for answer: {e}")
            return 1

    def save(self, *args, **kwargs):
        """Enhanced save with proper ordering"""
        if not self.pk and (not self.order or self.order == 1):
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}..."

    class Meta(TimeStampedMixin.Meta, OrderedMixin.Meta):
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ["question", "order"]
        indexes = create_meta_indexes(TimeStampedMixin.Meta, OrderedMixin.Meta) + [
            models.Index(fields=["question", "order"]),
            models.Index(fields=["is_correct"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['question', 'order'], name='unique_answer_order'),
        ]


class Enrollment(TimeStampedMixin):
    """Enhanced enrollment model with analytics support and validation"""

    user = create_foreign_key(User, "enrollments", help_text="Enrolled student")
    course = create_foreign_key(Course, "enrollments", help_text="Enrolled course")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", help_text="Enrollment status")
    completion_date = models.DateTimeField(blank=True, null=True, help_text="Date when course was completed")
    last_accessed = models.DateTimeField(auto_now=True, help_text="Last time student accessed the course")
    enrolled_date = models.DateTimeField(auto_now_add=True, help_text="Date when student enrolled")

    # Analytics fields
    total_time_spent = models.PositiveIntegerField(default=0, help_text="Total time spent in seconds")
    progress_percentage = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Progress percentage (0-100)"
    )
    last_lesson_accessed = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="last_accessed_enrollments", help_text="Last lesson accessed by student"
    )

    def clean(self):
        """Enhanced validation for enrollment"""
        super().clean()
        if not self.pk:
            existing = Enrollment.objects.filter(
                user=self.user, course=self.course
            ).exclude(status="unenrolled")
            if existing.exists():
                raise ValidationError("User is already enrolled in this course")

    def update_progress(self):
        """Update enrollment progress based on completed lessons"""
        try:
            with transaction.atomic():
                total_lessons = Lesson.objects.filter(
                    module__course=self.course
                ).count()

                if total_lessons == 0:
                    self.progress_percentage = 0
                else:
                    completed_lessons = Progress.objects.filter(
                        enrollment=self, is_completed=True
                    ).count()
                    self.progress_percentage = int((completed_lessons / total_lessons) * 100)

                if self.progress_percentage == 100 and self.status == "active":
                    self.status = "completed"
                    self.completion_date = timezone.now()

                self.save(update_fields=["progress_percentage", "status", "completion_date"])

                self.course.update_analytics()

                logger.debug(f"Progress updated for enrollment {self.id}: {self.progress_percentage}%")

        except Exception as e:
            logger.error(f"Error updating progress for enrollment {self.id}: {e}")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        ordering = ["-created_date"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["completion_date"]),
            models.Index(fields=["progress_percentage"]),
            models.Index(fields=["enrolled_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                condition=~models.Q(status='unenrolled'),
                name='unique_active_enrollment'
            ),
        ]


class Progress(TimeStampedMixin):
    """Enhanced progress model with comprehensive analytics and validation"""

    enrollment = create_foreign_key(Enrollment, "progress", help_text="Associated enrollment")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, help_text="Lesson being tracked")
    is_completed = models.BooleanField(default=False, help_text="Whether lesson is completed")
    completed_date = models.DateTimeField(blank=True, null=True, help_text="Date when lesson was completed")
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent on this lesson in seconds")
    progress_percentage = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100), validate_percentage],
        help_text="Progress within this specific lesson (0-100)"
    )
    notes = models.TextField(blank=True, null=True, help_text="Student notes for this lesson")
    last_accessed = models.DateTimeField(auto_now=True, help_text="Last time lesson was accessed")

    def save(self, *args, **kwargs):
        """Enhanced save with automatic completion date setting"""
        if self.is_completed and not self.completed_date:
            self.completed_date = timezone.now()
        super().save(*args, **kwargs)

        try:
            self.enrollment.update_progress()
        except Exception as e:
            logger.error(f"Error updating enrollment progress from Progress {self.id}: {e}")

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title} progress"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Progress"
        verbose_name_plural = "Progress Records"
        ordering = ["-last_accessed"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["enrollment", "is_completed"]),
            models.Index(fields=["lesson", "is_completed"]),
            models.Index(fields=["completed_date"]),
            models.Index(fields=["progress_percentage"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['enrollment', 'lesson'], name='unique_progress_record'),
        ]


class AssessmentAttempt(TimeStampedMixin):
    """Enhanced assessment attempt model with comprehensive tracking and validation"""

    user = create_foreign_key(User, "assessment_attempts", help_text="User taking the assessment")
    assessment = create_foreign_key(Assessment, "attempts", help_text="Assessment being attempted")
    start_time = models.DateTimeField(auto_now_add=True, help_text="When attempt was started")
    end_time = models.DateTimeField(blank=True, null=True, help_text="When attempt was completed")
    score = models.PositiveIntegerField(default=0, help_text="Raw score achieved")
    passed = models.BooleanField(default=False, help_text="Whether attempt passed the assessment")
    attempt_number = models.PositiveIntegerField(default=1, help_text="Attempt number for this user/assessment combination")

    # Additional tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the user during attempt")
    user_agent = models.TextField(blank=True, null=True, help_text="User agent string during attempt")

    @property
    def score_percentage(self):
        """Calculate score percentage"""
        try:
            if not hasattr(self, '_max_score'):
                self._max_score = self.assessment.questions.aggregate(
                    total_points=models.Sum('points')
                )['total_points'] or 0

            return round((self.score / self._max_score) * 100, 1) if self._max_score > 0 else 0
        except Exception as e:
            logger.error(f"Error calculating score percentage for attempt {self.id}: {e}")
            return 0

    @property
    def time_taken(self):
        """Calculate time taken for attempt in seconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    def save(self, *args, **kwargs):
        """Enhanced save with automatic attempt numbering and validation"""
        if not self.pk:
            with transaction.atomic():
                last_attempt = AssessmentAttempt.objects.select_for_update().filter(
                    user=self.user, assessment=self.assessment
                ).order_by("-attempt_number").first()

                self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1

                if self.attempt_number > self.assessment.max_attempts:
                    raise ValidationError(f"Maximum attempts ({self.assessment.max_attempts}) exceeded")

        if self.score_percentage >= self.assessment.passing_score:
            self.passed = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} attempt #{self.attempt_number} at {self.assessment.title}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Assessment Attempt"
        verbose_name_plural = "Assessment Attempts"
        ordering = ["-start_time"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["user", "assessment"]),
            models.Index(fields=["assessment", "-start_time"]),
            models.Index(fields=["passed"]),
            models.Index(fields=["attempt_number"]),
        ]


class AttemptAnswer(models.Model):
    """Enhanced attempt answer model with comprehensive validation"""

    attempt = create_foreign_key(AssessmentAttempt, "answers", help_text="Associated assessment attempt")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, help_text="Question being answered")
    selected_answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, blank=True, null=True,
        help_text="Selected answer for multiple choice questions"
    )
    text_answer = models.TextField(blank=True, null=True, help_text="Text answer for open-ended questions")
    is_correct = models.BooleanField(default=False, help_text="Whether the answer is correct")
    points_earned = models.PositiveIntegerField(default=0, help_text="Points earned for this answer")
    feedback = models.TextField(blank=True, null=True, help_text="Instructor feedback for this answer")
    answered_at = models.DateTimeField(auto_now_add=True, help_text="When answer was submitted")

    def clean(self):
        """Enhanced validation for attempt answer"""
        super().clean()
        if self.question.question_type in ["multiple_choice", "true_false"]:
            if not self.selected_answer:
                raise ValidationError("Selected answer is required for this question type")
        elif self.question.question_type in ["short_answer", "essay"]:
            if not self.text_answer:
                raise ValidationError("Text answer is required for this question type")

    def save(self, *args, **kwargs):
        """Enhanced save with automatic correctness checking"""
        if self.selected_answer and self.question.question_type in ["multiple_choice", "true_false"]:
            self.is_correct = self.selected_answer.is_correct
            self.points_earned = self.question.points if self.is_correct else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}... in {self.attempt}"

    class Meta:
        verbose_name = "Attempt Answer"
        verbose_name_plural = "Attempt Answers"
        ordering = ["answered_at"]
        indexes = [
            models.Index(fields=["attempt", "question"]),
            models.Index(fields=["is_correct"]),
            models.Index(fields=["answered_at"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['attempt', 'question'], name='unique_attempt_answer'),
        ]


class Review(TimeStampedMixin):
    """Enhanced review model with comprehensive validation and moderation"""

    user = create_foreign_key(User, "reviews", help_text="User who wrote the review")
    course = create_foreign_key(Course, "reviews", help_text="Course being reviewed")
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
    moderation_notes = models.TextField(blank=True, null=True, help_text="Internal moderation notes")

    def save(self, *args, **kwargs):
        """Enhanced save with verification check and analytics update"""
        if not self.pk:
            self.is_verified_purchase = Enrollment.objects.filter(
                user=self.user, course=self.course
            ).exists()

        super().save(*args, **kwargs)

        try:
            self.course.update_analytics()
        except Exception as e:
            logger.error(f"Error updating course analytics from review {self.id}: {e}")

        logger.info(f"Review created: {self.user.username} rated {self.course.title} {self.rating}/5")

    def __str__(self):
        return f"{self.user.username}'s review on {self.course.title} ({self.rating}/5)"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_date"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["course", "-created_date"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["is_approved"]),
            models.Index(fields=["is_verified_purchase"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_review'),
        ]


class Note(TimeStampedMixin):
    """Enhanced note model with comprehensive organization and validation"""

    user = create_foreign_key(User, "notes", help_text="User who created the note")
    lesson = create_foreign_key(Lesson, "notes", help_text="Lesson the note is associated with")
    content = create_text_field(min_len=1, help_text="Note content")
    is_private = models.BooleanField(default=True, help_text="Whether this note is private to the user")
    tags = create_json_field(max_items=10, min_str_len=2, help_text="Tags for organizing notes")

    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.user.username}'s note on {self.lesson.title}: {content_preview}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-created_date"]
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["user", "lesson"]),
            models.Index(fields=["lesson", "is_private"]),
            models.Index(fields=["is_private"]),
        ]


class Certificate(TimeStampedMixin):
    """Enhanced certificate model with verification, validation, and security"""

    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="certificate",
        help_text="Associated enrollment"
    )
    certificate_number = models.CharField(max_length=50, unique=True, help_text="Unique certificate number")

    # Verification and validity
    is_valid = models.BooleanField(default=True, help_text="Whether certificate is valid")
    revocation_date = models.DateTimeField(null=True, blank=True, help_text="Date when certificate was revoked")
    revocation_reason = models.TextField(blank=True, null=True, help_text="Reason for certificate revocation")

    # Additional metadata
    verification_hash = models.CharField(max_length=64, unique=True, blank=True, help_text="SHA-256 hash for verification")
    template_version = models.CharField(max_length=10, default="1.0", help_text="Certificate template version")

    def clean(self):
        """Enhanced validation for certificate"""
        super().clean()
        if self.enrollment.status != "completed":
            raise ValidationError("Certificate can only be issued for completed enrollments")

    def save(self, *args, **kwargs):
        """Enhanced save with automatic generation of certificate data"""
        if not self.certificate_number:
            self.certificate_number = generate_certificate_number(
                self.enrollment.course.id,
                self.enrollment.user.id,
                self.created_date or timezone.now()
            )

        if not self.verification_hash:
            self.verification_hash = generate_verification_hash(
                self.certificate_number,
                self.enrollment.id,
                self.created_date or timezone.now()
            )

        super().save(*args, **kwargs)
        logger.info(f"Certificate issued: {self.certificate_number} for {self.enrollment.user.username}")

    def revoke(self, reason=None):
        """Revoke the certificate with atomic operation"""
        try:
            with transaction.atomic():
                self.is_valid = False
                self.revocation_date = timezone.now()
                self.revocation_reason = reason or "Certificate revoked"
                self.save(update_fields=["is_valid", "revocation_date", "revocation_reason"])

            logger.warning(f"Certificate revoked: {self.certificate_number} - {reason}")
        except Exception as e:
            logger.error(f"Error revoking certificate {self.certificate_number}: {e}")
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
            models.Index(fields=["revocation_date"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['certificate_number'], name='unique_certificate_number'),
            models.UniqueConstraint(fields=['verification_hash'], name='unique_verification_hash'),
        ]


class CourseProgress(TimeStampedMixin):
    """Enhanced course-level progress tracking model"""

    user = create_foreign_key(User, "course_progress", help_text="Student user")
    course = create_foreign_key(Course, "student_progress", help_text="Associated course")

    # Progress tracking
    completion_percentage = create_decimal_field(
        max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Course completion percentage (0.00 to 100.00)"
    )

    # Timestamps
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text="Last time the user accessed this course"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user first started this course"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the user completed this course"
    )

    # Current position tracking
    current_lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='current_for_users',
        help_text="The lesson the user is currently on"
    )

    # Analytics
    total_time_spent = models.PositiveIntegerField(
        default=0,
        help_text="Total time spent on this course in seconds"
    )
    lessons_completed = models.PositiveIntegerField(
        default=0,
        help_text="Number of lessons completed"
    )
    assessments_passed = models.PositiveIntegerField(
        default=0,
        help_text="Number of assessments passed"
    )

    # Study streak tracking
    study_streak_days = models.PositiveIntegerField(
        default=0,
        help_text="Consecutive days of course activity"
    )
    last_study_date = models.DateField(
        null=True, blank=True,
        help_text="Last date the user studied this course"
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
        """Enhanced save with automatic progress calculation"""
        self._update_study_streak()

        if self.completion_percentage >= 100 and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def _update_study_streak(self):
        """Update study streak based on activity"""
        today = timezone.now().date()

        if not self.last_study_date:
            self.study_streak_days = 1
            self.last_study_date = today
        elif self.last_study_date == today:
            # Already studied today, no change needed
            pass
        elif self.last_study_date == today - timezone.timedelta(days=1):
            # Consecutive day
            self.study_streak_days += 1
            self.last_study_date = today
        else:
            # Streak broken
            self.study_streak_days = 1
            self.last_study_date = today

    def update_from_lesson_progress(self):
        """Update course progress based on individual lesson progress"""
        try:
            with transaction.atomic():
                enrollment = Enrollment.objects.filter(
                    user=self.user, course=self.course
                ).first()

                if not enrollment:
                    logger.warning(f"No enrollment found for CourseProgress {self.id}")
                    return

                total_lessons = Lesson.objects.filter(
                    module__course=self.course
                ).count()

                if total_lessons == 0:
                    self.completion_percentage = Decimal('0.00')
                    self.lessons_completed = 0
                else:
                    completed_lessons = Progress.objects.filter(
                        enrollment=enrollment,
                        is_completed=True
                    ).count()

                    self.lessons_completed = completed_lessons
                    self.completion_percentage = Decimal(
                        str(round((completed_lessons / total_lessons) * 100, 2))
                    )

                self.assessments_passed = AssessmentAttempt.objects.filter(
                    user=self.user,
                    assessment__lesson__module__course=self.course,
                    passed=True
                ).values('assessment').distinct().count()

                if hasattr(enrollment, 'total_time_spent'):
                    self.total_time_spent = enrollment.total_time_spent

                current_progress = Progress.objects.filter(
                    enrollment=enrollment,
                    is_completed=False
                ).order_by('lesson__module__order', 'lesson__order').first()

                if current_progress:
                    self.current_lesson = current_progress.lesson

                self.save()

                logger.debug(f"Course progress updated: {self.user.username} - {self.course.title} ({self.completion_percentage}%)")

        except Exception as e:
            logger.error(f"Error updating course progress {self.id}: {e}")

    @property
    def is_completed(self):
        """Check if course is completed"""
        return self.completion_percentage >= 100

    @property
    def progress_percentage_float(self):
        """Get progress as float for compatibility"""
        return float(self.completion_percentage)

    def mark_completed(self):
        """Mark course as completed"""
        self.completion_percentage = Decimal('100.00')
        self.completed_at = timezone.now()
        self.save()

    def reset_progress(self):
        """Reset course progress"""
        self.completion_percentage = Decimal('0.00')
        self.completed_at = None
        self.lessons_completed = 0
        self.assessments_passed = 0
        self.current_lesson = None
        self.study_streak_days = 0
        self.last_study_date = None
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.completion_percentage}%)"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = "Course Progress"
        verbose_name_plural = "Course Progress Records"
        ordering = ['-last_accessed']
        indexes = TimeStampedMixin.Meta.indexes + [
            models.Index(fields=["user", "course"]),
            models.Index(fields=["course", "completion_percentage"]),
            models.Index(fields=["user", "last_accessed"]),
            models.Index(fields=["completion_percentage"]),
            models.Index(fields=["completed_at"]),
            models.Index(fields=["study_streak_days"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_course_progress'),
            models.CheckConstraint(
                check=models.Q(completion_percentage__gte=0) & models.Q(completion_percentage__lte=100),
                name='course_progress_percentage_range'
            ),
            models.CheckConstraint(
                check=models.Q(lessons_completed__gte=0),
                name='course_progress_lessons_completed_positive'
            ),
            models.CheckConstraint(
                check=models.Q(assessments_passed__gte=0),
                name='course_progress_assessments_passed_positive'
            ),
            models.CheckConstraint(
                check=models.Q(study_streak_days__gte=0),
                name='course_progress_study_streak_positive'
            ),
        ]
