# File Path: instructor_portal/models/creation.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:09:54
# Date Revised: 2025-06-27 03:27:18
# Author: softTechSolutions2001
# Version: 1.0.1
#
# Course Creation models - Course creation sessions and templates
# Split from original models.py maintaining exact code compatibility

import logging
import uuid
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from .utils import TierManager, get_course_model, get_category_model

logger = logging.getLogger(__name__)
User = get_user_model()


class CourseCreationSession(models.Model):
    """
    Course creation session for tracking multi-step course creation process
    ENHANCED: Better session management and state tracking
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        IN_PROGRESS = 'in_progress', _('In Progress')
        PAUSED = 'paused', _('Paused')
        COMPLETED = 'completed', _('Completed')
        PUBLISHED = 'published', _('Published')
        FAILED = 'failed', _('Failed')
        ABANDONED = 'abandoned', _('Abandoned')

    class CreationMethod(models.TextChoices):
        WIZARD = 'wizard', _('Step-by-Step Wizard')
        TEMPLATE = 'template', _('From Template')
        AI_ASSISTED = 'ai_assisted', _('AI-Assisted Creation')
        BULK_IMPORT = 'bulk_import', _('Bulk Import')
        CLONE = 'clone', _('Clone Existing Course')

    # Session Identification
    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name=_('Session ID')
    )

    instructor = models.ForeignKey(
        'InstructorProfile',
        on_delete=models.CASCADE,
        related_name='creation_sessions',
        verbose_name=_('Instructor')
    )

    # Creation Configuration
    creation_method = models.CharField(
        max_length=30,
        choices=CreationMethod.choices,
        default=CreationMethod.WIZARD,
        verbose_name=_('Creation Method')
    )

    template = models.ForeignKey(
        'CourseTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Template Used')
    )

    # Session State
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('Status')
    )

    current_step = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Current Step')
    )

    total_steps = models.PositiveIntegerField(
        default=6,
        verbose_name=_('Total Steps')
    )

    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Completion Percentage')
    )

    # Content Data
    course_data = models.JSONField(
        default=dict,
        verbose_name=_('Course Data'),
        help_text=_('Course information and content being created')
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Session Metadata'),
        help_text=_('Additional session information and tracking data')
    )

    # Progress Tracking
    steps_completed = models.JSONField(
        default=list,
        verbose_name=_('Completed Steps')
    )

    validation_errors = models.JSONField(
        default=list,
        verbose_name=_('Validation Errors')
    )

    # Template and AI tracking
    template_used = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Template Name Used')
    )

    ai_prompts_used = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('AI Prompts Used')
    )

    # Session Management
    expires_at = models.DateTimeField(
        verbose_name=_('Expires At'),
        help_text=_('When this session expires if not completed')
    )

    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Activity')
    )

    # Relationships
    published_course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='creation_session',
        verbose_name=_('Published Course')
    )

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date')
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated Date')
    )

    class Meta:
        verbose_name = _('Course Creation Session')
        verbose_name_plural = _('Course Creation Sessions')
        ordering = ['-updated_date']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['creation_method', 'status']),
        ]

    def __str__(self):
        return f"Creation Session - {self.instructor.display_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Enhanced save with tier validation and session management"""
        # Validate tier limits for new sessions
        if self.pk is None:  # New session
            if not self.can_create_session():
                raise ValidationError(_('Instructor tier does not allow new course creation sessions'))

        # Update completion percentage based on completed steps
        if self.steps_completed and self.total_steps > 0:
            # FIX: Use Decimal instead of float for completion_percentage
            progress = (len(self.steps_completed) / self.total_steps) * 100
            self.completion_percentage = Decimal(str(progress)).quantize(Decimal('0.01'))

        # Set expiry if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)

        super().save(*args, **kwargs)

        # Clear cache when session is updated
        cache.delete(f"creation_session:{self.session_id}")

    def can_create_session(self) -> bool:
        """Check if instructor can create a new course creation session"""
        try:
            # Check tier limits
            tier_limits = TierManager.get_tier_limits(self.instructor.tier)
            max_courses = tier_limits.get('max_courses', 3)

            # Count current active courses
            current_courses = self.instructor.user.instructed_courses.filter(is_published=True).count()

            if current_courses >= max_courses:
                logger.warning(f"Instructor {self.instructor.id} exceeded course limit: {current_courses}/{max_courses}")
                return False

            # Check for existing active sessions
            active_sessions = CourseCreationSession.objects.filter(
                instructor=self.instructor,
                status__in=[self.Status.DRAFT, self.Status.IN_PROGRESS, self.Status.PAUSED]
            ).count()

            # Limit concurrent sessions based on tier
            max_concurrent = 2 if self.instructor.tier in ['gold', 'platinum', 'diamond'] else 1

            if active_sessions >= max_concurrent:
                logger.warning(f"Instructor {self.instructor.id} has too many active sessions: {active_sessions}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking session creation permission: {e}")
            return False

    def update_progress(self, step: int, data: Dict[str, Any] = None) -> bool:
        """Update session progress and data"""
        try:
            with transaction.atomic():
                # Update current step
                self.current_step = step

                # Add to completed steps if not already there
                if step not in self.steps_completed:
                    self.steps_completed.append(step)

                # Update course data if provided
                if data:
                    self.course_data.update(data)

                # Update status based on progress
                if len(self.steps_completed) == self.total_steps:
                    self.status = self.Status.COMPLETED
                elif len(self.steps_completed) > 0:
                    self.status = self.Status.IN_PROGRESS

                self.save()

                logger.info(f"Updated session {self.session_id} progress to step {step}")
                return True

        except Exception as e:
            logger.error(f"Error updating session progress: {e}")
            return False

    def validate_session_data(self) -> List[str]:
        """Validate session data and return errors"""
        errors = []

        try:
            # Basic course information validation
            course_data = self.course_data
            if not course_data.get('title'):
                errors.append(_('Course title is required'))

            if not course_data.get('description'):
                errors.append(_('Course description is required'))

            if not course_data.get('category_id'):
                errors.append(_('Course category is required'))

            # Validate modules and lessons if present
            modules = course_data.get('modules', [])
            if not modules:
                errors.append(_('At least one module is required'))

            for i, module in enumerate(modules):
                if not module.get('title'):
                    # FIX: Pre-format strings outside translation function
                    module_num = i + 1
                    errors.append(_('Module {} title is required').format(module_num))

                lessons = module.get('lessons', [])
                if not lessons:
                    # FIX: Pre-format strings outside translation function
                    module_num = i + 1
                    errors.append(_('Module {} must have at least one lesson').format(module_num))

            # Update validation errors
            self.validation_errors = errors
            self.save(update_fields=['validation_errors'])

            return errors

        except Exception as e:
            logger.error(f"Error validating session data: {e}")
            return [str(e)]

    def publish_course(self) -> Optional['Course']:
        """Publish course from session data"""
        try:
            # Validate before publishing
            errors = self.validate_session_data()
            if errors:
                logger.warning(f"Cannot publish course with validation errors: {errors}")
                return None

            Course = get_course_model()
            Category = get_category_model()

            with transaction.atomic():
                course_data = self.course_data

                # Create course
                course = Course.objects.create(
                    title=course_data['title'],
                    description=course_data['description'],
                    category_id=course_data['category_id'],
                    instructor=self.instructor.user,
                    is_published=True,
                    # Add other fields as needed
                )

                # Create course instructor relationship
                from .course_link import CourseInstructor
                CourseInstructor.objects.create(
                    course=course,
                    instructor=self.instructor.user,
                    role=CourseInstructor.Role.PRIMARY,
                    is_lead=True,
                    is_active=True
                )

                # Update session
                self.published_course = course
                self.status = self.Status.PUBLISHED
                self.save()

                logger.info(f"Published course {course.id} from session {self.session_id}")
                return course

        except Exception as e:
            logger.error(f"Error publishing course from session {self.session_id}: {e}")
            self.status = self.Status.FAILED
            self.save()
            return None

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return timezone.now() > self.expires_at

    def extend_expiry(self, days: int = 30) -> bool:
        """Extend session expiry"""
        try:
            self.expires_at = timezone.now() + timezone.timedelta(days=days)
            self.save(update_fields=['expires_at'])
            return True
        except Exception as e:
            logger.error(f"Error extending session expiry: {e}")
            return False


class CourseTemplate(models.Model):
    """
    Course templates for quick course creation
    ENHANCED: Better template management and usage tracking
    """

    class TemplateType(models.TextChoices):
        ACADEMIC = 'academic', _('Academic Course')
        PROFESSIONAL = 'professional', _('Professional Training')
        CREATIVE = 'creative', _('Creative Skills')
        TECHNICAL = 'technical', _('Technical Training')
        BUSINESS = 'business', _('Business Skills')
        LANGUAGE = 'language', _('Language Learning')

    # Template Information
    name = models.CharField(
        max_length=200,
        verbose_name=_('Template Name')
    )

    description = models.TextField(
        verbose_name=_('Template Description')
    )

    template_type = models.CharField(
        max_length=30,
        choices=TemplateType.choices,
        verbose_name=_('Template Type')
    )

    # Template Configuration
    template_data = models.JSONField(
        verbose_name=_('Template Data'),
        help_text=_('JSON structure for the course template')
    )

    # Access Control
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    is_premium = models.BooleanField(
        default=False,
        verbose_name=_('Premium Template'),
        help_text=_('Only available to higher tier instructors')
    )

    required_tier = models.CharField(
        max_length=30,
        choices=[
            ('bronze', _('Bronze')),
            ('silver', _('Silver')),
            ('gold', _('Gold')),
            ('platinum', _('Platinum')),
            ('diamond', _('Diamond')),
        ],
        default='bronze',
        verbose_name=_('Required Tier')
    )

    # Usage Statistics
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Usage Count')
    )

    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Success Rate (%)')
    )

    # Template Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Created By')
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Tags')
    )

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date')
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated Date')
    )

    class Meta:
        verbose_name = _('Course Template')
        verbose_name_plural = _('Course Templates')
        ordering = ['name']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['is_active', 'required_tier']),
            models.Index(fields=['usage_count']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def is_accessible_to_tier(self, tier: str) -> bool:
        """Check if template is accessible to instructor tier"""
        tier_hierarchy = ['bronze', 'silver', 'gold', 'platinum', 'diamond']
        try:
            tier_index = tier_hierarchy.index(tier.lower())
            required_index = tier_hierarchy.index(self.required_tier.lower())
            return tier_index >= required_index
        except ValueError:
            return False

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])

    def update_success_rate(self):
        """Update success rate based on completed sessions"""
        try:
            total_uses = CourseCreationSession.objects.filter(
                template=self
            ).count()

            successful_uses = CourseCreationSession.objects.filter(
                template=self,
                status=CourseCreationSession.Status.PUBLISHED
            ).count()

            if total_uses > 0:
                self.success_rate = (successful_uses / total_uses) * 100
                self.save(update_fields=['success_rate'])

        except Exception as e:
            logger.error(f"Error updating template success rate: {e}")
