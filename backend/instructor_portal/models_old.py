#
# File Path: instructor_portal/models.py
#


import logging
import uuid
import os
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, List, Set, Tuple
from urllib.parse import urlparse

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.db import models, transaction, IntegrityError, DatabaseError
from django.db.models import Q, Avg, Count, Sum, F, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)
User = get_user_model()


def get_course_model():
    """Get Course model to avoid circular imports"""
    return apps.get_model('courses', 'Course')


def get_category_model():
    """Get Category model to avoid circular imports"""
    return apps.get_model('courses', 'Category')


def get_enrollment_model():
    """Get Enrollment model to avoid circular imports"""
    return apps.get_model('courses', 'Enrollment')


def get_review_model():
    """Get Review model to avoid circular imports"""
    return apps.get_model('courses', 'Review')


# ENHANCED: Custom validators for security
class HTTPSURLValidator(URLValidator):
    """Custom URL validator that enforces HTTPS for security"""

    def __call__(self, value):
        super().__call__(value)
        if value and not value.startswith('https://'):
            raise ValidationError(_('URL must use HTTPS protocol for security'))


def validate_social_handle(value):
    """Validate social media handles"""
    if value:
        # Normalize Twitter handle
        if not value.startswith('@'):
            value = f"@{value}"
        # Convert to lowercase for consistency
        return value.lower()
    return value


def generate_upload_path(instance, filename):
    """Generate sharded upload path to prevent filesystem bottlenecks"""
    # Use first 2 characters of UUID for sharding
    shard = str(instance.user.id)[:2] if hasattr(instance, 'user') else 'default'
    return f'instructor_profiles/{shard}/{filename}'


def generate_cover_upload_path(instance, filename):
    """Generate sharded upload path for cover images"""
    shard = str(instance.user.id)[:2] if hasattr(instance, 'user') else 'default'
    return f'instructor_covers/{shard}/{filename}'


# ENHANCED: Centralized tier logic with configuration support
class TierManager:
    """
    Centralized tier capability management with enhanced configuration support
    """

    # Made configurable through settings
    MAX_EXPERIENCE_YEARS = getattr(settings, 'MAX_INSTRUCTOR_EXPERIENCE_YEARS', 50)

    TIER_CAPABILITIES = {
        'bronze': {
            'max_courses': 3,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'can_clone_courses': False,
            'can_use_ai_builder': False,
            'analytics_history_days': 30,
            'max_instructors_per_course': 1,
            'max_resources_per_lesson': 10,
            'file_types_allowed': ['pdf', 'jpg', 'png', 'mp4'],
        },
        'silver': {
            'max_courses': 10,
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'can_clone_courses': True,
            'can_use_ai_builder': False,
            'analytics_history_days': 90,
            'max_instructors_per_course': 2,
            'max_resources_per_lesson': 20,
            'file_types_allowed': ['pdf', 'jpg', 'png', 'mp4', 'mp3', 'docx', 'xlsx'],
        },
        'gold': {
            'max_courses': 25,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'can_clone_courses': True,
            'can_use_ai_builder': True,
            'analytics_history_days': 180,
            'max_instructors_per_course': 5,
            'max_resources_per_lesson': 50,
            'file_types_allowed': ['pdf', 'jpg', 'png', 'mp4', 'mp3', 'docx', 'xlsx', 'pptx', 'zip'],
        },
        'platinum': {
            'max_courses': 100,
            'max_file_size': 500 * 1024 * 1024,  # 500MB
            'can_clone_courses': True,
            'can_use_ai_builder': True,
            'analytics_history_days': 365,
            'max_instructors_per_course': 10,
            'max_resources_per_lesson': 100,
            'file_types_allowed': ['pdf', 'jpg', 'png', 'mp4', 'mp3', 'docx', 'xlsx', 'pptx', 'zip', 'csv', 'json'],
        },
        'diamond': {
            'max_courses': 1000,
            'max_file_size': 1024 * 1024 * 1024,  # 1GB
            'can_clone_courses': True,
            'can_use_ai_builder': True,
            'analytics_history_days': 730,
            'max_instructors_per_course': -1,  # unlimited
            'max_resources_per_lesson': -1,  # unlimited
            'file_types_allowed': '*',  # all file types
        },
    }

    @staticmethod
    def get_tier_limits(tier: str) -> Dict[str, Any]:
        """Get all capabilities for a specific tier"""
        default_tier = 'bronze'
        tier_key = tier.lower() if isinstance(tier, str) else default_tier

        if tier_key not in TierManager.TIER_CAPABILITIES:
            logger.warning(f"Unknown instructor tier: {tier}, using {default_tier} capabilities")
            tier_key = default_tier

        return TierManager.TIER_CAPABILITIES[tier_key].copy()

    @staticmethod
    def can_perform_action(tier: str, action_name: str) -> bool:
        """Check if tier can perform a specific action"""
        capabilities = TierManager.get_tier_limits(tier)
        return capabilities.get(f"can_{action_name}", False)

    @staticmethod
    def check_file_size_limit(tier: str, file_size: int) -> bool:
        """Check if file size is within tier limits"""
        limits = TierManager.get_tier_limits(tier)
        max_size = limits.get('max_file_size', 10 * 1024 * 1024)
        return file_size <= max_size

    @staticmethod
    def check_courses_limit(tier: str, current_count: int) -> bool:
        """Check if courses count is within tier limits"""
        limits = TierManager.get_tier_limits(tier)
        max_courses = limits.get('max_courses', 3)
        return current_count < max_courses

    @staticmethod
    def is_file_type_allowed(tier: str, file_extension: str) -> bool:
        """Check if file type is allowed for the tier"""
        limits = TierManager.get_tier_limits(tier)
        allowed_types = limits.get('file_types_allowed', ['pdf'])

        if allowed_types == '*':
            return True

        return file_extension.lower().lstrip('.') in allowed_types


# REFACTORED: Separated core profile from analytics for better organization
class InstructorProfile(models.Model):
    """
    Core instructor profile model - streamlined and focused on profile data
    REFACTORED: Moved analytics to separate model for better separation of concerns
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Approval')
        ACTIVE = 'active', _('Active')
        SUSPENDED = 'suspended', _('Suspended')
        INACTIVE = 'inactive', _('Inactive')
        BANNED = 'banned', _('Banned')

    class Tier(models.TextChoices):
        BRONZE = 'bronze', _('Bronze Instructor')
        SILVER = 'silver', _('Silver Instructor')
        GOLD = 'gold', _('Gold Instructor')
        PLATINUM = 'platinum', _('Platinum Instructor')
        DIAMOND = 'diamond', _('Diamond Instructor')

    # Core Profile Information
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name=_('User Account'),
        db_index=True  # ADDED: Direct index for performance
    )

    # Professional Information
    display_name = models.CharField(
        max_length=100,
        verbose_name=_('Display Name'),
        help_text=_('Name shown to students')
    )

    bio = models.TextField(
        max_length=2000,
        blank=True,
        verbose_name=_('Biography'),
        help_text=_('Professional biography and background')
    )

    expertise_areas = models.ManyToManyField(
        'courses.Category',
        blank=True,
        related_name='expert_instructors',
        verbose_name=_('Areas of Expertise')
    )

    # Professional Details
    title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Professional Title'),
        help_text=_('e.g., Senior Software Engineer, PhD in Computer Science')
    )

    organization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Organization/Company')
    )

    years_experience = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(TierManager.MAX_EXPERIENCE_YEARS)],
        verbose_name=_('Years of Experience')
    )

    # Contact and Social Information - ENHANCED: Security validation
    website = models.URLField(
        blank=True,
        validators=[HTTPSURLValidator()],
        verbose_name=_('Website')
    )

    linkedin_profile = models.URLField(
        blank=True,
        validators=[HTTPSURLValidator()],
        verbose_name=_('LinkedIn Profile')
    )

    twitter_handle = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Twitter Handle')
    )

    # Profile Media - ENHANCED: Sharded upload paths
    profile_image = models.ImageField(
        upload_to=generate_upload_path,
        blank=True,
        null=True,
        verbose_name=_('Profile Image')
    )

    cover_image = models.ImageField(
        upload_to=generate_cover_upload_path,
        blank=True,
        null=True,
        verbose_name=_('Cover Image')
    )

    # Status and Verification
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status')
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified Instructor'),
        help_text=_('Identity and credentials verified')
    )

    tier = models.CharField(
        max_length=30,
        choices=Tier.choices,
        default=Tier.BRONZE,
        verbose_name=_('Instructor Tier')
    )

    # Settings and Preferences
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Email Notifications Enabled')
    )

    marketing_emails = models.BooleanField(
        default=False,
        verbose_name=_('Marketing Emails Enabled')
    )

    public_profile = models.BooleanField(
        default=True,
        verbose_name=_('Public Profile'),
        help_text=_('Allow students to view your profile')
    )

    # Administrative Fields
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_instructors',
        verbose_name=_('Approved By')
    )

    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approval Date')
    )

    suspension_reason = models.TextField(
        blank=True,
        verbose_name=_('Suspension Reason')
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

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Login')
    )

    class Meta:
        verbose_name = _('Instructor Profile')
        verbose_name_plural = _('Instructor Profiles')
        ordering = ['-created_date']
        indexes = [
            # OPTIMIZED: More strategic indexing based on common query patterns
            models.Index(fields=['status', 'is_verified'], name='instructor_status_verified_idx'),
            models.Index(fields=['tier', '-created_date'], name='instructor_tier_created_idx'),
            models.Index(fields=['status', 'tier'], name='instructor_status_tier_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(years_experience__gte=0) & Q(years_experience__lte=TierManager.MAX_EXPERIENCE_YEARS),
                name='valid_experience_years'
            ),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.get_status_display()})"

    def clean(self):
        """Enhanced validation for instructor profile"""
        super().clean()

        # Comprehensive validation rules
        if self.status == self.Status.ACTIVE:
            if len(self.bio) < 100:
                raise ValidationError(_('Active instructors need detailed bio (100+ characters)'))
            if not self.profile_image:
                raise ValidationError(_('Active instructors must upload profile image'))

        # Normalize and validate social media handles
        if self.twitter_handle:
            self.twitter_handle = validate_social_handle(self.twitter_handle)

    def save(self, *args, **kwargs):
        """Enhanced save with deferred analytics updates"""
        is_new = self.pk is None

        # Save first
        super().save(*args, **kwargs)

        # Initialize setup for new profiles
        if is_new:
            self.initialize_instructor_setup()

    def initialize_instructor_setup(self):
        """Initialize instructor setup after profile creation"""
        try:
            # Create instructor dashboard preferences
            InstructorDashboard.objects.get_or_create(
                instructor=self,
                defaults={
                    'show_analytics': True,
                    'show_recent_students': True,
                    'show_performance_metrics': True
                }
            )

            # Create initial analytics record
            InstructorAnalytics.objects.create(
                instructor=self,
                total_students=0,
                total_courses=0,
                average_rating=Decimal('0.00'),
                total_revenue=Decimal('0.00')
            )

            logger.info(f"Initialized instructor setup for {self.display_name}")

        except Exception as e:
            logger.error(f"Error initializing instructor setup for {self.id}: {e}")

    @property
    def instructed_courses(self):
        """Get courses where this user is an instructor"""
        Course = get_course_model()
        return Course.objects.filter(
            courseinstructor_set__instructor=self.user,
            courseinstructor_set__is_active=True
        )

    @property
    def active_students(self):
        """Get currently active students across all courses"""
        Enrollment = get_enrollment_model()
        return User.objects.filter(
            enrollments__course__in=self.instructed_courses,
            enrollments__status='active'
        ).distinct()

    def get_tier_capabilities(self) -> Dict[str, Any]:
        """Get tier capabilities for this instructor"""
        return TierManager.get_tier_limits(self.tier)


# NEW: Separated analytics model for better organization
class InstructorAnalytics(models.Model):
    """
    Instructor analytics and performance metrics - separated for better organization
    ADDED: Comprehensive analytics tracking with caching and freshness checks
    """

    instructor = models.OneToOneField(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_('Instructor')
    )

    # Core Analytics
    total_students = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Students Taught')
    )

    total_courses = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Courses Created')
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        verbose_name=_('Average Rating')
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Reviews')
    )

    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Total Revenue')
    )

    # Performance Metrics
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Course Completion Rate (%)')
    )

    student_satisfaction_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Student Satisfaction Rate (%)')
    )

    monthly_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Monthly Revenue')
    )

    # Caching and Performance
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )

    last_calculated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Calculated')
    )

    class Meta:
        verbose_name = _('Instructor Analytics')
        verbose_name_plural = _('Instructor Analytics')
        indexes = [
            models.Index(fields=['instructor', 'last_updated']),
            models.Index(fields=['total_students', 'average_rating']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(average_rating__gte=0) & Q(average_rating__lte=5),
                name='analytics_valid_rating'
            ),
            models.CheckConstraint(
                check=Q(total_revenue__gte=0),
                name='analytics_positive_revenue'
            ),
        ]

    def __str__(self):
        return f"Analytics for {self.instructor.display_name}"

    def should_update(self, force: bool = False) -> bool:
        """Check if analytics should be updated based on freshness"""
        if force:
            return True

        if not self.last_calculated:
            return True

        # Update if older than 1 hour
        threshold = timezone.now() - timezone.timedelta(hours=1)
        return self.last_calculated < threshold

    @transaction.atomic
    def update_analytics(self, force: bool = False):
        """
        Update analytics with proper caching and freshness checks
        ENHANCED: Added freshness checking to prevent redundant updates
        """
        if not self.should_update(force):
            logger.debug(f"Analytics for instructor {self.instructor.id} are fresh, skipping update")
            return False

        try:
            # Use cache locking to prevent concurrent updates
            cache_key = f"instructor_analytics_update:{self.instructor.pk}"
            if cache.get(cache_key) and not force:
                return False

            cache.set(cache_key, True, timeout=300)  # 5 minute lock

            # Get related models
            Course = get_course_model()
            Enrollment = get_enrollment_model()
            Review = get_review_model()

            # Calculate metrics efficiently
            courses = Course.objects.filter(
                courseinstructor_set__instructor=self.instructor.user,
                courseinstructor_set__is_active=True,
                is_published=True
            )

            total_courses = courses.count()

            # Student metrics
            enrollments = Enrollment.objects.filter(
                course__in=courses,
                status__in=['active', 'completed']
            )

            total_students = enrollments.values('user').distinct().count()
            completed_enrollments = enrollments.filter(status='completed').count()
            completion_rate = (completed_enrollments / enrollments.count() * 100) if enrollments.count() > 0 else 0

            # Review metrics
            reviews = Review.objects.filter(
                course__in=courses,
                is_approved=True
            )

            review_stats = reviews.aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id')
            )

            avg_rating = review_stats['avg_rating'] or Decimal('0.00')
            if avg_rating:
                avg_rating = avg_rating.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Satisfaction rate (4+ stars out of 5)
            satisfied_reviews = reviews.filter(rating__gte=4).count()
            satisfaction_rate = (satisfied_reviews / reviews.count() * 100) if reviews.count() > 0 else 0

            # Revenue calculation (placeholder - integrate with actual payment system)
            current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_enrollments = enrollments.filter(created_date__gte=current_month).count()
            monthly_revenue = Decimal(str(monthly_enrollments * 50))  # Estimate

            # Update all fields atomically
            InstructorAnalytics.objects.filter(pk=self.pk).update(
                total_courses=total_courses,
                total_students=total_students,
                average_rating=avg_rating,
                total_reviews=review_stats['total_reviews'] or 0,
                completion_rate=Decimal(str(completion_rate)).quantize(Decimal('0.01')),
                student_satisfaction_rate=Decimal(str(satisfaction_rate)).quantize(Decimal('0.01')),
                monthly_revenue=monthly_revenue,
                last_calculated=timezone.now()
            )

            # Refresh instance
            self.refresh_from_db()

            # Update instructor tier based on new metrics
            self._update_instructor_tier()

            # Clear cache lock
            cache.delete(cache_key)

            logger.debug(f"Updated analytics for instructor {self.instructor.display_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating instructor analytics for {self.instructor.id}: {e}")
            cache.delete(cache_key)
            return False

    def _update_instructor_tier(self):
        """Update instructor tier based on performance metrics"""
        try:
            # Tier calculation logic
            score = 0

            # Student count scoring
            if self.total_students >= 1000:
                score += 40
            elif self.total_students >= 500:
                score += 30
            elif self.total_students >= 100:
                score += 20
            elif self.total_students >= 50:
                score += 10

            # Course count scoring
            if self.total_courses >= 10:
                score += 30
            elif self.total_courses >= 5:
                score += 20
            elif self.total_courses >= 2:
                score += 10

            # Rating scoring
            if self.average_rating >= Decimal('4.5'):
                score += 30
            elif self.average_rating >= Decimal('4.0'):
                score += 20
            elif self.average_rating >= Decimal('3.5'):
                score += 10

            # Determine new tier
            old_tier = self.instructor.tier
            if score >= 80:
                new_tier = InstructorProfile.Tier.DIAMOND
            elif score >= 60:
                new_tier = InstructorProfile.Tier.PLATINUM
            elif score >= 40:
                new_tier = InstructorProfile.Tier.GOLD
            elif score >= 20:
                new_tier = InstructorProfile.Tier.SILVER
            else:
                new_tier = InstructorProfile.Tier.BRONZE

            # Update if changed
            if old_tier != new_tier:
                InstructorProfile.objects.filter(pk=self.instructor.pk).update(tier=new_tier)
                self.instructor.refresh_from_db(fields=['tier'])

                logger.info(f"Updated tier for {self.instructor.display_name}: {old_tier} → {new_tier}")

                # Clear related caches
                cache_keys = [f"instructor_permission:{self.instructor.user.id}:{course_id}"
                             for course_id in self.instructor.instructed_courses.values_list('id', flat=True)]
                if cache_keys:
                    cache.delete_many(cache_keys)

        except Exception as e:
            logger.error(f"Error updating instructor tier for {self.instructor.id}: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            'total_students': self.total_students,
            'total_courses': self.total_courses,
            'average_rating': float(self.average_rating),
            'total_reviews': self.total_reviews,
            'tier': self.instructor.get_tier_display(),
            'completion_rate': float(self.completion_rate),
            'monthly_revenue': float(self.monthly_revenue),
            'student_satisfaction': float(self.student_satisfaction_rate),
            'tier_limits': self.instructor.get_tier_capabilities()
        }


# NEW: Historical analytics for trend analysis
class InstructorAnalyticsHistory(models.Model):
    """
    Historical analytics data for trend analysis and reporting
    ADDED: Separate model for historical analytics tracking
    """

    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='analytics_history',
        verbose_name=_('Instructor')
    )

    # Snapshot data
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Snapshot Date')
    )

    total_students = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    # Metadata
    data_type = models.CharField(
        max_length=50,
        default='daily',
        verbose_name=_('Data Type'),
        help_text=_('Type of analytics snapshot (daily, weekly, monthly)')
    )

    additional_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Additional Data')
    )

    class Meta:
        verbose_name = _('Analytics History')
        verbose_name_plural = _('Analytics History')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['instructor', '-date']),
            models.Index(fields=['instructor', 'data_type', '-date']),
        ]

    def __str__(self):
        return f"Analytics History - {self.instructor.display_name} ({self.date.strftime('%Y-%m-%d')})"

    @classmethod
    def create_snapshot(cls, instructor_profile: InstructorProfile, data_type: str = 'daily'):
        """Create analytics snapshot"""
        try:
            analytics = instructor_profile.analytics
            cls.objects.create(
                instructor=instructor_profile,
                date=timezone.now(),
                total_students=analytics.total_students,
                total_courses=analytics.total_courses,
                average_rating=analytics.average_rating,
                total_revenue=analytics.total_revenue,
                completion_rate=analytics.completion_rate,
                data_type=data_type,
                additional_data={
                    'satisfaction_rate': float(analytics.student_satisfaction_rate),
                    'monthly_revenue': float(analytics.monthly_revenue),
                    'tier': instructor_profile.tier
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error creating analytics snapshot: {e}")
            return False

    @classmethod
    def cleanup_old_history(cls, instructor_tier: str = 'bronze'):
        """Clean up old analytics history based on tier"""
        try:
            days_to_keep = TierManager.get_tier_limits(instructor_tier)['analytics_history_days']
            cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)

            deleted_count = cls.objects.filter(date__lt=cutoff_date).delete()[0]
            logger.info(f"Cleaned up {deleted_count} old analytics history records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up analytics history: {e}")
            return 0


class CourseInstructor(models.Model):
    """
    Instructor-course relationship model with role-based permissions
    ENHANCED: Better permission management and validation
    """

    class Role(models.TextChoices):
        PRIMARY = 'primary', _('Primary Instructor')
        CO_INSTRUCTOR = 'co_instructor', _('Co-Instructor')
        ASSISTANT = 'assistant', _('Teaching Assistant')
        GUEST = 'guest', _('Guest Instructor')

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        verbose_name=_('Course')
    )

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Instructor')
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.PRIMARY,
        verbose_name=_('Role')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    is_lead = models.BooleanField(
        default=False,
        verbose_name=_('Is Lead Instructor')
    )

    # Permissions
    can_edit_content = models.BooleanField(default=True)
    can_manage_students = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=True)

    # Revenue sharing
    revenue_share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )

    # Timestamps
    joined_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course Instructor')
        verbose_name_plural = _('Course Instructors')
        unique_together = [['course', 'instructor']]
        ordering = ['course', '-is_lead', 'joined_date']
        indexes = [
            models.Index(fields=['course', 'is_active']),
            models.Index(fields=['instructor', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(revenue_share_percentage__gte=0) & Q(revenue_share_percentage__lte=100),
                name='valid_revenue_share_percentage'
            ),
        ]

    def __str__(self):
        return f"{self.instructor.get_full_name()} - {self.course.title} ({self.get_role_display()})"

    def clean(self):
        """Validate course instructor relationships"""
        super().clean()

        # Only one lead instructor per course
        if self.is_lead:
            existing_leads = CourseInstructor.objects.filter(
                course=self.course,
                is_lead=True,
                is_active=True
            ).exclude(pk=self.pk)

            if existing_leads.exists():
                raise ValidationError(_('Course can only have one lead instructor'))

    def save(self, *args, **kwargs):
        """Enhanced save with cache management"""
        is_new = self.pk is None
        permission_changed = not is_new and self._permission_fields_changed()

        super().save(*args, **kwargs)

        # Clear permission caches
        cache.delete(f"instructor_permission:{self.instructor.id}:{self.course.id}")

        # Update analytics if needed
        if is_new or permission_changed:
            try:
                instructor_profile = self.instructor.instructor_profile
                # Use async update to avoid blocking the save operation
                from django.db import transaction
                transaction.on_commit(
                    lambda: instructor_profile.analytics.update_analytics()
                )
            except (AttributeError, InstructorProfile.DoesNotExist, InstructorAnalytics.DoesNotExist):
                pass

    def _permission_fields_changed(self) -> bool:
        """Check if permission fields have changed"""
        try:
            old_obj = CourseInstructor.objects.get(pk=self.pk)
            permission_fields = ['can_edit_content', 'can_manage_students', 'can_view_analytics', 'is_active']
            return any(getattr(self, field) != getattr(old_obj, field) for field in permission_fields)
        except CourseInstructor.DoesNotExist:
            return True


class InstructorDashboard(models.Model):
    """
    Instructor dashboard configuration and preferences
    ENHANCED: Improved widget management and performance
    """

    instructor = models.OneToOneField(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='dashboard',
        verbose_name=_('Instructor')
    )

    # Display Preferences
    show_analytics = models.BooleanField(default=True)
    show_recent_students = models.BooleanField(default=True)
    show_performance_metrics = models.BooleanField(default=True)
    show_revenue_charts = models.BooleanField(default=True)
    show_course_progress = models.BooleanField(default=True)

    # Notification Preferences
    notify_new_enrollments = models.BooleanField(default=True)
    notify_new_reviews = models.BooleanField(default=True)
    notify_course_completions = models.BooleanField(default=True)

    # Layout Configuration
    widget_order = models.JSONField(default=list, blank=True)
    custom_colors = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Instructor Dashboard')
        verbose_name_plural = _('Instructor Dashboards')

    def __str__(self):
        return f"Dashboard - {self.instructor.display_name}"

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data with caching"""
        cache_key = f"instructor_dashboard:{self.instructor.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            data = {
                'recent_activity': self.get_recent_activity(),
                'instructor': {
                    'name': self.instructor.display_name,
                    'tier': self.instructor.get_tier_display(),
                    'status': self.instructor.get_status_display()
                },
                'widgets': self.get_enabled_widgets(),
                'notifications': {
                    'new_enrollments': self.notify_new_enrollments,
                    'new_reviews': self.notify_new_reviews,
                    'course_completions': self.notify_course_completions
                }
            }

            # Cache for 15 minutes
            cache.set(cache_key, data, timeout=900)
            return data

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'error': 'Failed to load dashboard data'}

    def get_enabled_widgets(self) -> List[Dict[str, Any]]:
        """Get enabled widgets in configured order"""
        available_widgets = [
            {'id': 'course_overview', 'name': 'Course Overview', 'enabled': True},
            {'id': 'recent_students', 'name': 'Recent Students', 'enabled': self.show_recent_students},
            {'id': 'analytics', 'name': 'Analytics', 'enabled': self.show_analytics},
            {'id': 'performance_metrics', 'name': 'Performance Metrics', 'enabled': self.show_performance_metrics},
            {'id': 'revenue_charts', 'name': 'Revenue Charts', 'enabled': self.show_revenue_charts},
            {'id': 'course_progress', 'name': 'Course Progress', 'enabled': self.show_course_progress}
        ]

        # Apply custom ordering if configured
        if self.widget_order:
            widget_lookup = {w['id']: w for w in available_widgets}
            ordered_widgets = []

            # Add widgets in custom order
            for widget_id in self.widget_order:
                if widget_id in widget_lookup and widget_lookup[widget_id]['enabled']:
                    ordered_widgets.append(widget_lookup[widget_id])

            # Add any remaining enabled widgets
            for widget in available_widgets:
                if widget['enabled'] and widget['id'] not in self.widget_order:
                    ordered_widgets.append(widget)

            return ordered_widgets
        else:
            return [w for w in available_widgets if w['enabled']]

    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent activity with optimized queries"""
        try:
            activities = []
            cutoff_date = timezone.now() - timezone.timedelta(days=7)

            # Get models
            Enrollment = get_enrollment_model()
            Review = get_review_model()

            # Recent enrollments - limit and optimize
            recent_enrollments = Enrollment.objects.filter(
                course__in=self.instructor.instructed_courses,
                created_date__gte=cutoff_date
            ).select_related('user', 'course').order_by('-created_date')[:15]

            for enrollment in recent_enrollments:
                activities.append({
                    'type': 'enrollment',
                    'message': f"{enrollment.user.get_full_name() or enrollment.user.username} enrolled in {enrollment.course.title}",
                    'date': enrollment.created_date,
                    'course_id': enrollment.course.id,
                })

            # Recent reviews - limit and optimize
            recent_reviews = Review.objects.filter(
                course__in=self.instructor.instructed_courses,
                created_date__gte=cutoff_date
            ).select_related('user', 'course').order_by('-created_date')[:15]

            for review in recent_reviews:
                activities.append({
                    'type': 'review',
                    'message': f"{review.user.get_full_name() or review.user.username} reviewed {review.course.title} ({review.rating}★)",
                    'date': review.created_date,
                    'course_id': review.course.id,
                    'rating': review.rating,
                })

            # Sort by date and return top 10
            activities.sort(key=lambda x: x['date'], reverse=True)
            return activities[:10]

        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []


class CourseCreationSession(models.Model):
    """
    Course creation session management with enhanced validation
    ENHANCED: Better session management and validation
    """

    class CreationMethod(models.TextChoices):
        WIZARD = 'wizard', _('Step-by-Step Wizard')
        AI_BUILDER = 'ai_builder', _('AI Course Builder')
        DRAG_DROP = 'drag_drop', _('Drag & Drop Builder')
        TEMPLATE = 'template', _('Template-Based')
        IMPORT = 'import', _('Content Import')

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft - In Progress')
        PAUSED = 'paused', _('Paused - Resumed Later')
        VALIDATING = 'validating', _('Validating Content')
        READY_TO_PUBLISH = 'ready_to_publish', _('Ready for Publishing')
        PUBLISHED = 'published', _('Published Successfully')
        FAILED = 'failed', _('Creation Failed')
        ABANDONED = 'abandoned', _('Abandoned Session')

    # Session identification
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='creation_sessions')

    # Creation details
    creation_method = models.CharField(max_length=30, choices=CreationMethod.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)

    # Course data
    course_data = models.JSONField(default=dict)

    # Progress tracking
    current_step = models.PositiveIntegerField(default=1)
    total_steps = models.PositiveIntegerField(default=0)
    completed_steps = models.JSONField(default=list)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    # Auto-save
    last_auto_save = models.DateTimeField(null=True, blank=True)
    auto_save_data = models.JSONField(default=dict)

    # Validation
    validation_errors = models.JSONField(default=list)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # AI-specific fields
    ai_prompt = models.TextField(blank=True)
    ai_suggestions = models.JSONField(default=list)

    # Template and references
    template_used = models.CharField(max_length=100, blank=True)
    reference_courses = models.ManyToManyField('courses.Course', blank=True, related_name='referenced_in_creation')

    # Course links
    draft_course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_sessions')
    published_course = models.OneToOneField('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='creation_session')

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _('Course Creation Session')
        verbose_name_plural = _('Course Creation Sessions')
        ordering = ['-updated_date']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at', 'status']),
        ]

    def __str__(self):
        return f"{self.instructor.display_name} - {self.get_creation_method_display()} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Enhanced save with expiry and progress calculation"""
        # Set expiry if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)

        # Calculate progress
        if self.total_steps > 0:
            progress = (len(self.completed_steps) / self.total_steps) * 100
            self.progress_percentage = Decimal(str(progress)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

    def validate_course_data(self) -> List[str]:
        """Validate course data comprehensively"""
        errors = []

        try:
            # Basic validation
            if not self.course_data.get('title'):
                errors.append("Course title is required")
            if not self.course_data.get('description'):
                errors.append("Course description is required")
            if not self.course_data.get('category_id'):
                errors.append("Course category is required")

            # Module validation
            modules = self.course_data.get('modules', [])
            if not modules:
                errors.append("At least one module is required")

            for i, module in enumerate(modules):
                if not module.get('title'):
                    errors.append(f"Module {i+1} title is required")

                lessons = module.get('lessons', [])
                if not lessons:
                    errors.append(f"Module {i+1} must have at least one lesson")

                for j, lesson in enumerate(lessons):
                    if not lesson.get('title'):
                        errors.append(f"Module {i+1}, Lesson {j+1} title is required")
                    if not lesson.get('content') and not lesson.get('video_url'):
                        errors.append(f"Module {i+1}, Lesson {j+1} must have content or video")

            # Update validation errors
            self.validation_errors = errors
            self.save(update_fields=['validation_errors'])

            return errors

        except Exception as e:
            logger.error(f"Error validating course data: {e}")
            return [f"Validation error: {str(e)}"]

    @transaction.atomic
    def publish_course(self):
        """Publish course from session data"""
        try:
            # Validate first
            errors = self.validate_course_data()
            if errors:
                self.status = self.Status.FAILED
                self.save(update_fields=['status'])
                return None

            # Get models
            Course = get_course_model()
            Category = get_category_model()

            course_data = self.course_data

            # Create course
            category = Category.objects.get(id=course_data['category_id'])
            title = course_data.get('title', 'Untitled Course')

            course = Course.objects.create(
                title=title,
                slug=slugify(title),
                description=course_data.get('description', ''),
                category=category,
                level=course_data.get('level', 'beginner'),
                price=Decimal(str(course_data.get('price', '0.00'))),
                is_published=course_data.get('is_published', False)
            )

            # Create instructor relationship
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
            self.completed_date = timezone.now()
            self.save(update_fields=['published_course', 'status', 'completed_date'])

            # Update instructor analytics
            self.instructor.analytics.update_analytics(force=True)

            logger.info(f"Successfully published course from session {self.session_id}")
            return course

        except Exception as e:
            logger.error(f"Error publishing course: {e}", exc_info=True)
            self.status = self.Status.FAILED
            self.validation_errors = [str(e)]
            self.save(update_fields=['status', 'validation_errors'])
            return None


class CourseTemplate(models.Model):
    """
    Course templates for quick course creation
    ENHANCED: Better template management and success tracking
    """

    class TemplateType(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner Course Template')
        INTERMEDIATE = 'intermediate', _('Intermediate Course Template')
        ADVANCED = 'advanced', _('Advanced Course Template')
        WORKSHOP = 'workshop', _('Workshop Template')
        MASTERCLASS = 'masterclass', _('Masterclass Template')
        CERTIFICATION = 'certification', _('Certification Course Template')

    name = models.CharField(max_length=100)
    description = models.TextField()
    template_type = models.CharField(max_length=30, choices=TemplateType.choices)
    category = models.ForeignKey('courses.Category', on_delete=models.CASCADE, related_name='templates')

    # Template structure
    template_data = models.JSONField()
    estimated_duration = models.PositiveIntegerField()
    difficulty_level = models.CharField(max_length=30, default='beginner')

    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    # Management
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course Template')
        verbose_name_plural = _('Course Templates')
        ordering = ['category', 'template_type', 'name']
        indexes = [
            models.Index(fields=['category', 'template_type']),
            models.Index(fields=['is_active', '-usage_count']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    @transaction.atomic
    def create_session_from_template(self, instructor: InstructorProfile) -> CourseCreationSession:
        """Create session from template"""
        try:
            session = CourseCreationSession.objects.create(
                instructor=instructor,
                creation_method=CourseCreationSession.CreationMethod.TEMPLATE,
                template_used=self.name,
                course_data=self.template_data.copy(),
                total_steps=len(self.template_data.get('steps', [])) or 4,
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            # Update usage count atomically
            CourseTemplate.objects.filter(pk=self.pk).update(usage_count=F('usage_count') + 1)
            self.refresh_from_db(fields=['usage_count'])

            logger.info(f"Created session from template {self.name}")
            return session

        except Exception as e:
            logger.error(f"Error creating session from template: {e}")
            raise


# ENHANCED: Signal handlers with better error handling
@receiver(post_save, sender=User)
def create_instructor_profile_signal(sender, instance, created, **kwargs):
    """Create instructor profile for eligible users"""
    if not created:
        return

    try:
        # Check if user should have instructor profile
        should_create = (
            instance.groups.filter(name='instructors').exists() or
            instance.user_permissions.filter(codename='add_course').exists()
        )

        if should_create and not hasattr(instance, 'instructor_profile'):
            display_name = getattr(instance, 'get_full_name', lambda: instance.username)()

            InstructorProfile.objects.create(
                user=instance,
                display_name=display_name or instance.username,
                status=InstructorProfile.Status.PENDING
            )
            logger.info(f"Created instructor profile for user {instance.username}")

    except Exception as e:
        logger.error(f"Error creating instructor profile for user {instance.id}: {e}")


@receiver(post_save, sender=InstructorProfile)
def create_instructor_analytics(sender, instance, created, **kwargs):
    """Create analytics record for new instructor profiles"""
    if created:
        try:
            InstructorAnalytics.objects.create(instructor=instance)
            logger.info(f"Created analytics for instructor {instance.display_name}")
        except Exception as e:
            logger.error(f"Error creating analytics for instructor {instance.id}: {e}")


# ADDED: Cleanup utility class
class InstructorPortalCleanup:
    """Utility class for cleanup operations"""

    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """Clean up expired course creation sessions"""
        try:
            cutoff_date = timezone.now()
            expired_sessions = CourseCreationSession.objects.filter(
                expires_at__lt=cutoff_date,
                status__in=[
                    CourseCreationSession.Status.DRAFT,
                    CourseCreationSession.Status.PAUSED,
                    CourseCreationSession.Status.ABANDONED
                ]
            )

            count = expired_sessions.count()
            if count > 0:
                expired_sessions.delete()
                logger.info(f"Cleaned up {count} expired course creation sessions")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    @classmethod
    def cleanup_old_analytics_history(cls) -> int:
        """Clean up old analytics history based on tier limits"""
        try:
            total_cleaned = 0

            for tier_name, limits in TierManager.TIER_CAPABILITIES.items():
                days_to_keep = limits['analytics_history_days']
                cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)

                # Get instructors with this tier
                instructors = InstructorProfile.objects.filter(tier=tier_name)

                for instructor in instructors:
                    deleted_count = InstructorAnalyticsHistory.objects.filter(
                        instructor=instructor,
                        date__lt=cutoff_date
                    ).delete()[0]
                    total_cleaned += deleted_count

            logger.info(f"Cleaned up {total_cleaned} old analytics history records")
            return total_cleaned

        except Exception as e:
            logger.error(f"Error cleaning up analytics history: {e}")
            return 0

    @classmethod
    def refresh_all_instructor_analytics(cls) -> int:
        """Refresh analytics for all active instructors"""
        try:
            active_instructors = InstructorProfile.objects.filter(
                status=InstructorProfile.Status.ACTIVE
            ).select_related('analytics')

            updated_count = 0
            for instructor in active_instructors:
                try:
                    if instructor.analytics.update_analytics(force=True):
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating analytics for instructor {instructor.id}: {e}")
                    continue

            logger.info(f"Updated analytics for {updated_count} instructors")
            return updated_count

        except Exception as e:
            logger.error(f"Error refreshing instructor analytics: {e}")
            return 0

    @classmethod
    def cleanup_orphaned_files(cls) -> int:
        """Clean up orphaned files not linked to any database records"""
        try:
            deleted_count = 0

            # Get all instructor profile image paths from database
            profile_image_paths = set(
                InstructorProfile.objects.exclude(profile_image='')
                .values_list('profile_image', flat=True)
            )

            cover_image_paths = set(
                InstructorProfile.objects.exclude(cover_image='')
                .values_list('cover_image', flat=True)
            )

            # Combine all valid paths
            valid_paths = profile_image_paths.union(cover_image_paths)

            # Check for orphaned files in storage
            storage_dirs = ['instructor_profiles', 'instructor_covers']

            for storage_dir in storage_dirs:
                try:
                    if default_storage.exists(storage_dir):
                        # List all files in the directory
                        dirs, files = default_storage.listdir(storage_dir)

                        # Check subdirectories (sharded paths)
                        for subdir in dirs:
                            subdir_path = f"{storage_dir}/{subdir}"
                            if default_storage.exists(subdir_path):
                                _, subfiles = default_storage.listdir(subdir_path)

                                for file in subfiles:
                                    file_path = f"{storage_dir}/{subdir}/{file}"

                                    # If file not in valid paths, it's orphaned
                                    if file_path not in valid_paths:
                                        try:
                                            default_storage.delete(file_path)
                                            deleted_count += 1
                                            logger.debug(f"Deleted orphaned file: {file_path}")
                                        except Exception as e:
                                            logger.error(f"Error deleting orphaned file {file_path}: {e}")

                        # Check files in root directory
                        for file in files:
                            file_path = f"{storage_dir}/{file}"
                            if file_path not in valid_paths:
                                try:
                                    default_storage.delete(file_path)
                                    deleted_count += 1
                                    logger.debug(f"Deleted orphaned file: {file_path}")
                                except Exception as e:
                                    logger.error(f"Error deleting orphaned file {file_path}: {e}")

                except Exception as e:
                    logger.error(f"Error processing storage directory {storage_dir}: {e}")
                    continue

            logger.info(f"Cleaned up {deleted_count} orphaned files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}")
            return 0

    @classmethod
    def generate_analytics_report(cls, instructor_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics report for instructor(s)"""
        try:
            if instructor_id:
                # Single instructor report
                instructor = InstructorProfile.objects.get(id=instructor_id)
                analytics = instructor.analytics

                report = {
                    'instructor': {
                        'id': instructor.id,
                        'name': instructor.display_name,
                        'tier': instructor.tier,
                        'status': instructor.status,
                        'created_date': instructor.created_date.isoformat(),
                    },
                    'current_metrics': analytics.get_performance_metrics(),
                    'tier_capabilities': instructor.get_tier_capabilities(),
                    'recent_history': []
                }

                # Add recent history
                recent_history = InstructorAnalyticsHistory.objects.filter(
                    instructor=instructor
                ).order_by('-date')[:30]

                for history in recent_history:
                    report['recent_history'].append({
                        'date': history.date.isoformat(),
                        'total_students': history.total_students,
                        'total_courses': history.total_courses,
                        'average_rating': float(history.average_rating),
                        'completion_rate': float(history.completion_rate),
                        'data_type': history.data_type
                    })

                return report

            else:
                # System-wide report
                total_instructors = InstructorProfile.objects.count()
                active_instructors = InstructorProfile.objects.filter(
                    status=InstructorProfile.Status.ACTIVE
                ).count()

                # Tier distribution
                tier_distribution = {}
                for tier in InstructorProfile.Tier.choices:
                    tier_count = InstructorProfile.objects.filter(tier=tier[0]).count()
                    tier_distribution[tier[1]] = tier_count

                # Top performers
                top_performers = InstructorAnalytics.objects.select_related('instructor').order_by(
                    '-average_rating', '-total_students'
                )[:10]

                report = {
                    'system_overview': {
                        'total_instructors': total_instructors,
                        'active_instructors': active_instructors,
                        'tier_distribution': tier_distribution,
                        'generated_at': timezone.now().isoformat()
                    },
                    'top_performers': [
                        {
                            'instructor_id': analytics.instructor.id,
                            'name': analytics.instructor.display_name,
                            'tier': analytics.instructor.tier,
                            'total_students': analytics.total_students,
                            'average_rating': float(analytics.average_rating),
                            'total_courses': analytics.total_courses
                        }
                        for analytics in top_performers
                    ]
                }

                return report

        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {'error': str(e)}

    @classmethod
    def bulk_update_instructor_tiers(cls) -> int:
        """Bulk update all instructor tiers based on current performance"""
        try:
            updated_count = 0

            # Get all instructors with analytics
            instructors = InstructorProfile.objects.filter(
                status=InstructorProfile.Status.ACTIVE
            ).select_related('analytics')

            for instructor in instructors:
                try:
                    old_tier = instructor.tier

                    # Force analytics update first
                    instructor.analytics.update_analytics(force=True)

                    # Refresh to get updated tier
                    instructor.refresh_from_db(fields=['tier'])

                    if old_tier != instructor.tier:
                        updated_count += 1
                        logger.info(f"Updated tier for {instructor.display_name}: {old_tier} → {instructor.tier}")

                except Exception as e:
                    logger.error(f"Error updating tier for instructor {instructor.id}: {e}")
                    continue

            logger.info(f"Bulk tier update completed. Updated {updated_count} instructors")
            return updated_count

        except Exception as e:
            logger.error(f"Error in bulk tier update: {e}")
            return 0


# ADDED: Course content draft models for enhanced content management
class DraftCourseContent(models.Model):
    """
    Temporary storage for course content during creation process
    ENHANCED: Versioning support for AI iteration and content refinement
    """

    class ContentType(models.TextChoices):
        COURSE_INFO = 'course_info', _('Course Information')
        MODULE = 'module', _('Module Content')
        LESSON = 'lesson', _('Lesson Content')
        ASSESSMENT = 'assessment', _('Assessment Content')
        RESOURCE = 'resource', _('Resource/Material')

    session = models.ForeignKey(
        CourseCreationSession,
        on_delete=models.CASCADE,
        related_name='draft_content',
        verbose_name=_('Creation Session')
    )

    content_type = models.CharField(
        max_length=30,
        choices=ContentType.choices,
        verbose_name=_('Content Type')
    )

    content_id = models.CharField(
        max_length=50,
        verbose_name=_('Content Identifier'),
        help_text=_('Unique identifier for this content piece')
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Content Version'),
        help_text=_('Version number for AI iteration support')
    )

    # Content Data
    content_data = models.JSONField(
        verbose_name=_('Content Data'),
        help_text=_('JSON structure containing the actual content')
    )

    # Content Metadata
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Content Title')
    )

    order = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Display Order')
    )

    # Status and Validation
    is_complete = models.BooleanField(
        default=False,
        verbose_name=_('Is Complete'),
        help_text=_('Whether this content piece is ready for publication')
    )

    validation_errors = models.JSONField(
        default=list,
        verbose_name=_('Validation Errors'),
        help_text=_('List of validation errors for this content')
    )

    # Auto-save tracking
    auto_save_version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Auto-save Version'),
        help_text=_('Internal version for auto-save functionality')
    )

    last_saved = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Saved')
    )

    # AI generation metadata
    ai_generated = models.BooleanField(
        default=False,
        verbose_name=_('AI Generated'),
        help_text=_('Whether this content was generated using AI')
    )

    ai_prompt = models.TextField(
        blank=True,
        verbose_name=_('AI Prompt'),
        help_text=_('Original AI prompt used to generate this content')
    )

    class Meta:
        verbose_name = _('Draft Course Content')
        verbose_name_plural = _('Draft Course Contents')
        unique_together = [['session', 'content_type', 'content_id', 'version']]
        ordering = ['order', 'version']
        indexes = [
            models.Index(fields=['session', 'content_type']),
            models.Index(fields=['session', 'order']),
            models.Index(fields=['session', 'content_type', 'version']),
            models.Index(fields=['is_complete', 'last_saved']),
        ]

    def __str__(self):
        return f"{self.session.session_id} - {self.get_content_type_display()}: {self.title} (v{self.version})"

    def create_new_version(self) -> 'DraftCourseContent':
        """Create a new version of this content for AI iteration"""
        try:
            # Get the latest version number
            latest_version = DraftCourseContent.objects.filter(
                session=self.session,
                content_type=self.content_type,
                content_id=self.content_id
            ).aggregate(max_version=models.Max('version'))['max_version'] or 0

            # Create new version
            new_version = DraftCourseContent.objects.create(
                session=self.session,
                content_type=self.content_type,
                content_id=self.content_id,
                version=latest_version + 1,
                content_data=self.content_data.copy(),
                title=self.title,
                order=self.order,
                is_complete=False,  # New version starts as incomplete
                auto_save_version=1,  # Reset auto-save version
                ai_generated=self.ai_generated,
                ai_prompt=self.ai_prompt
            )

            logger.info(f"Created new version {new_version.version} for content {self.content_id}")
            return new_version

        except Exception as e:
            logger.error(f"Error creating new version: {e}")
            raise

    def validate_content(self) -> List[str]:
        """Validate content and return list of errors"""
        errors = []

        try:
            # Basic validation based on content type
            if self.content_type == self.ContentType.COURSE_INFO:
                if not self.content_data.get('title'):
                    errors.append("Course title is required")
                if not self.content_data.get('description'):
                    errors.append("Course description is required")
                if not self.content_data.get('category_id'):
                    errors.append("Course category is required")

            elif self.content_type == self.ContentType.MODULE:
                if not self.title:
                    errors.append("Module title is required")
                if not self.content_data.get('description'):
                    errors.append("Module description is recommended")

            elif self.content_type == self.ContentType.LESSON:
                if not self.title:
                    errors.append("Lesson title is required")
                if not self.content_data.get('content') and not self.content_data.get('video_url'):
                    errors.append("Lesson must have content or video")

                # Duration validation
                duration = self.content_data.get('duration_minutes', 0)
                if duration < 1:
                    errors.append("Lesson duration must be at least 1 minute")

            elif self.content_type == self.ContentType.ASSESSMENT:
                if not self.content_data.get('questions'):
                    errors.append("Assessment must have at least one question")

                questions = self.content_data.get('questions', [])
                for i, question in enumerate(questions):
                    if not question.get('question_text'):
                        errors.append(f"Question {i+1} text is required")
                    if not question.get('options') or len(question.get('options', [])) < 2:
                        errors.append(f"Question {i+1} must have at least 2 options")

            elif self.content_type == self.ContentType.RESOURCE:
                if not self.content_data.get('resource_type'):
                    errors.append("Resource type is required")
                if not self.content_data.get('resource_url') and not self.content_data.get('file_path'):
                    errors.append("Resource must have a URL or file attachment")

            # Update validation errors in the model
            if errors != self.validation_errors:
                self.validation_errors = errors
                self.save(update_fields=['validation_errors'])

            return errors

        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return [f"Validation error: {str(e)}"]

    def mark_complete(self) -> bool:
        """Mark content as complete after validation"""
        try:
            errors = self.validate_content()
            if not errors:
                self.is_complete = True
                self.save(update_fields=['is_complete'])
                logger.info(f"Marked content {self.content_id} as complete")
                return True
            else:
                logger.warning(f"Cannot mark content {self.content_id} as complete due to validation errors: {errors}")
                return False
        except Exception as e:
            logger.error(f"Error marking content as complete: {e}")
            return False


class CourseContentDraft(models.Model):
    """
    Enhanced content management for course creation with file support
    ENHANCED: Complete file upload, processing, and versioning system
    """

    session = models.ForeignKey(
        CourseCreationSession,
        on_delete=models.CASCADE,
        related_name='content_drafts',
        verbose_name=_('Creation Session')
    )

    content_type = models.CharField(
        max_length=30,
        choices=DraftCourseContent.ContentType.choices,
        verbose_name=_('Content Type')
    )

    # File handling with sharded paths
    file_path = models.FileField(
        upload_to='course_drafts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Content File')
    )

    # Content versioning and integrity
    content_hash = models.CharField(
        max_length=64,
        verbose_name=_('Content Hash'),
        help_text=_('SHA-256 hash for content deduplication and integrity')
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Content Version')
    )

    # Processing status
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_('Is Processed'),
        help_text=_('Whether file has been processed and validated')
    )

    processing_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', _('Pending Processing')),
            ('processing', _('Processing')),
            ('completed', _('Processing Completed')),
            ('failed', _('Processing Failed')),
            ('virus_scan', _('Virus Scanning')),
            ('format_conversion', _('Format Conversion'))
        ],
        default='pending',
        verbose_name=_('Processing Status')
    )

    processing_error = models.TextField(
        blank=True,
        verbose_name=_('Processing Error'),
        help_text=_('Error message if processing failed')
    )

    # File metadata
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('File Size (bytes)')
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('MIME Type')
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Original Filename')
    )

    # Processing metadata
    processing_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Processing Metadata'),
        help_text=_('Additional metadata from processing (dimensions, duration, etc.)')
    )

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date')
    )

    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processed Date')
    )

    class Meta:
        verbose_name = _('Course Content Draft')
        verbose_name_plural = _('Course Content Drafts')
        unique_together = [['session', 'content_type', 'version']]
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['session', 'processing_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['is_processed', 'created_date']),
            models.Index(fields=['processing_status', 'created_date']),
        ]

    def __str__(self):
        return f"Content Draft - {self.session.session_id} ({self.get_content_type_display()} v{self.version})"

    def save(self, *args, **kwargs):
        """Enhanced save with content hash generation and metadata extraction"""
        if self.file_path and not self.content_hash:
            try:
                # Generate hash from file content
                with default_storage.open(self.file_path.name, 'rb') as f:
                    file_content = f.read()
                    self.content_hash = hashlib.sha256(file_content).hexdigest()

                # Extract file metadata
                self.file_size = self.file_path.size
                self.original_filename = os.path.basename(self.file_path.name)

                # Determine MIME type
                import mimetypes
                file_ext = os.path.splitext(self.file_path.name)[1].lower()
                self.mime_type = mimetypes.types_map.get(file_ext, 'application/octet-stream')

            except Exception as e:
                logger.error(f"Error generating file metadata: {e}")
                self.content_hash = f"error-{uuid.uuid4().hex[:8]}"

        super().save(*args, **kwargs)

    def process_file(self) -> bool:
        """Process uploaded file with comprehensive validation and metadata extraction"""
        if not self.file_path:
            self.processing_status = 'failed'
            self.processing_error = 'No file to process'
            self.save(update_fields=['processing_status', 'processing_error'])
            return False

        try:
            self.processing_status = 'processing'
            self.save(update_fields=['processing_status'])

            # Check file size limits based on instructor tier
            if self.file_size and self.session.instructor:
                tier = self.session.instructor.tier
                if not TierManager.check_file_size_limit(tier, self.file_size):
                    self.processing_status = 'failed'
                    self.processing_error = f'File size exceeds tier limit for {tier} instructors'
                    self.save(update_fields=['processing_status', 'processing_error'])
                    return False

            # Check file type permissions
            if self.session.instructor:
                tier = self.session.instructor.tier
                file_ext = os.path.splitext(self.original_filename)[1].lower().lstrip('.')
                if not TierManager.is_file_type_allowed(tier, file_ext):
                    self.processing_status = 'failed'
                    self.processing_error = f'File type .{file_ext} not allowed for {tier} instructors'
                    self.save(update_fields=['processing_status', 'processing_error'])
                    return False

            # Extract content-specific metadata
            metadata = {}

            if self.mime_type.startswith('image/'):
                metadata.update(self._extract_image_metadata())
            elif self.mime_type.startswith('video/'):
                metadata.update(self._extract_video_metadata())
            elif self.mime_type.startswith('audio/'):
                metadata.update(self._extract_audio_metadata())
            elif self.mime_type == 'application/pdf':
                metadata.update(self._extract_pdf_metadata())

            self.processing_metadata = metadata

            # Mark as processed
            self.is_processed = True
            self.processing_status = 'completed'
            self.processed_date = timezone.now()
            self.save(update_fields=[
                'is_processed', 'processing_status', 'processed_date', 'processing_metadata'
            ])

            logger.info(f"Successfully processed file {self.original_filename}")
            return True

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            self.processing_status = 'failed'
            self.processing_error = str(e)
            self.save(update_fields=['processing_status', 'processing_error'])
            return False

    def _extract_image_metadata(self) -> Dict[str, Any]:
        """Extract metadata from image files"""
        metadata = {}
        try:
            from PIL import Image
            with default_storage.open(self.file_path.name, 'rb') as f:
                with Image.open(f) as img:
                    metadata.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format,
                        'mode': img.mode
                    })
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_video_metadata(self) -> Dict[str, Any]:
        """Extract metadata from video files"""
        metadata = {}
        try:
            # Placeholder for video metadata extraction
            # You would integrate with libraries like ffmpeg-python here
            metadata.update({
                'extracted': False,
                'note': 'Video metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_audio_metadata(self) -> Dict[str, Any]:
        """Extract metadata from audio files"""
        metadata = {}
        try:
            # Placeholder for audio metadata extraction
            # You would integrate with libraries like mutagen here
            metadata.update({
                'extracted': False,
                'note': 'Audio metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_pdf_metadata(self) -> Dict[str, Any]:
        """Extract metadata from PDF files"""
        metadata = {}
        try:
            # Placeholder for PDF metadata extraction
            # You would integrate with libraries like PyPDF2 or pdfplumber here
            metadata.update({
                'extracted': False,
                'note': 'PDF metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def get_download_url(self) -> Optional[str]:
        """Get secure download URL for the file"""
        try:
            if self.file_path and self.is_processed:
                return default_storage.url(self.file_path.name)
            return None
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            return None

    def delete_file(self) -> bool:
        """Safely delete the associated file"""
        try:
            if self.file_path and default_storage.exists(self.file_path.name):
                default_storage.delete(self.file_path.name)
                logger.info(f"Deleted file {self.file_path.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


# ENHANCED: Additional signal handlers for content management
@receiver(pre_delete, sender=CourseContentDraft)
def cleanup_file_on_delete(sender, instance, **kwargs):
    """Clean up file when CourseContentDraft is deleted"""
    try:
        instance.delete_file()
    except Exception as e:
        logger.error(f"Error cleaning up file on delete: {e}")


@receiver(post_save, sender=CourseCreationSession)
def session_status_changed(sender, instance, created, **kwargs):
    """Handle session status changes"""
    if not created and instance.status == CourseCreationSession.Status.PUBLISHED:
        try:
            # Create analytics snapshot when course is published
            InstructorAnalyticsHistory.create_snapshot(
                instance.instructor,
                data_type='course_published'
            )
            logger.info(f"Created analytics snapshot for published course from session {instance.session_id}")
        except Exception as e:
            logger.error(f"Error creating analytics snapshot: {e}")

    # Handle session completion notifications
    if not created and instance.status in [
        CourseCreationSession.Status.PUBLISHED,
        CourseCreationSession.Status.FAILED
    ]:
        try:
            # Send notification to instructor about completion
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            if instance.instructor.email_notifications:
                subject = _('Course Creation Session Completed')

                if instance.status == CourseCreationSession.Status.PUBLISHED:
                    template = 'instructor_portal/emails/course_published.html'
                    context = {
                        'instructor': instance.instructor,
                        'course': instance.published_course,
                        'session': instance
                    }
                else:
                    template = 'instructor_portal/emails/course_creation_failed.html'
                    context = {
                        'instructor': instance.instructor,
                        'session': instance,
                        'errors': instance.validation_errors
                    }

                html_message = render_to_string(template, context)

                send_mail(
                    subject=subject,
                    message='',  # Plain text version can be added
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.instructor.user.email],
                    html_message=html_message,
                    fail_silently=True
                )

                logger.info(f"Sent completion notification to {instance.instructor.display_name}")

        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")

    # Update instructor dashboard cache when session status changes
    if not created:
        try:
            cache_key = f"instructor_dashboard:{instance.instructor.id}"
            cache.delete(cache_key)
            logger.debug(f"Cleared dashboard cache for instructor {instance.instructor.id}")
        except Exception as e:
            logger.error(f"Error clearing dashboard cache: {e}")


# ADDED: Instructor notification system
class InstructorNotification(models.Model):
    """
    Notification system for instructors
    ADDED: Comprehensive notification management for instructor portal
    """

    class NotificationType(models.TextChoices):
        COURSE_PUBLISHED = 'course_published', _('Course Published')
        COURSE_APPROVED = 'course_approved', _('Course Approved')
        COURSE_REJECTED = 'course_rejected', _('Course Rejected')
        NEW_ENROLLMENT = 'new_enrollment', _('New Enrollment')
        NEW_REVIEW = 'new_review', _('New Review')
        COURSE_COMPLETED = 'course_completed', _('Course Completed by Student')
        TIER_UPGRADED = 'tier_upgraded', _('Tier Upgraded')
        REVENUE_MILESTONE = 'revenue_milestone', _('Revenue Milestone Reached')
        SYSTEM_ANNOUNCEMENT = 'system_announcement', _('System Announcement')
        ACCOUNT_WARNING = 'account_warning', _('Account Warning')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low Priority')
        MEDIUM = 'medium', _('Medium Priority')
        HIGH = 'high', _('High Priority')
        URGENT = 'urgent', _('Urgent')

    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Instructor')
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name=_('Notification Type')
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_('Priority')
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_('Notification Title')
    )

    message = models.TextField(
        verbose_name=_('Notification Message')
    )

    # Rich content support
    action_url = models.URLField(
        blank=True,
        verbose_name=_('Action URL'),
        help_text=_('URL for the primary action button')
    )

    action_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Action Text'),
        help_text=_('Text for the primary action button')
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Additional Metadata'),
        help_text=_('Additional data related to the notification')
    )

    # Status tracking
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Is Read')
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Read At')
    )

    is_dismissed = models.BooleanField(
        default=False,
        verbose_name=_('Is Dismissed')
    )

    dismissed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Dismissed At')
    )

    # Email notification tracking
    email_sent = models.BooleanField(
        default=False,
        verbose_name=_('Email Sent')
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Email Sent At')
    )

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date')
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expires At'),
        help_text=_('When this notification should be automatically dismissed')
    )

    class Meta:
        verbose_name = _('Instructor Notification')
        verbose_name_plural = _('Instructor Notifications')
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['instructor', 'is_read', '-created_date']),
            models.Index(fields=['instructor', 'notification_type']),
            models.Index(fields=['priority', 'created_date']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Notification for {self.instructor.display_name}: {self.title}"

    def mark_as_read(self) -> bool:
        """Mark notification as read"""
        try:
            if not self.is_read:
                self.is_read = True
                self.read_at = timezone.now()
                self.save(update_fields=['is_read', 'read_at'])
                logger.debug(f"Marked notification {self.id} as read")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    def dismiss(self) -> bool:
        """Dismiss notification"""
        try:
            if not self.is_dismissed:
                self.is_dismissed = True
                self.dismissed_at = timezone.now()
                self.save(update_fields=['is_dismissed', 'dismissed_at'])
                logger.debug(f"Dismissed notification {self.id}")
            return True
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
            return False

    def send_email_notification(self) -> bool:
        """Send email notification if enabled"""
        try:
            if (self.email_sent or
                not self.instructor.email_notifications or
                not self.instructor.user.email):
                return False

            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            context = {
                'instructor': self.instructor,
                'notification': self,
                'action_url': self.action_url,
                'site_url': getattr(settings, 'SITE_URL', 'https://example.com')
            }

            # Choose template based on notification type
            template_map = {
                self.NotificationType.COURSE_PUBLISHED: 'emails/course_published_notification.html',
                self.NotificationType.NEW_ENROLLMENT: 'emails/new_enrollment_notification.html',
                self.NotificationType.NEW_REVIEW: 'emails/new_review_notification.html',
                self.NotificationType.TIER_UPGRADED: 'emails/tier_upgraded_notification.html',
            }

            template = template_map.get(
                self.notification_type,
                'emails/generic_notification.html'
            )

            html_message = render_to_string(f'instructor_portal/{template}', context)

            send_mail(
                subject=f"[Instructor Portal] {self.title}",
                message=self.message,  # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.instructor.user.email],
                html_message=html_message,
                fail_silently=True
            )

            self.email_sent = True
            self.email_sent_at = timezone.now()
            self.save(update_fields=['email_sent', 'email_sent_at'])

            logger.info(f"Sent email notification to {self.instructor.display_name}")
            return True

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    @classmethod
    def create_notification(cls, instructor: InstructorProfile, notification_type: str,
                          title: str, message: str, **kwargs) -> 'InstructorNotification':
        """Create a new notification"""
        try:
            notification = cls.objects.create(
                instructor=instructor,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=kwargs.get('priority', cls.Priority.MEDIUM),
                action_url=kwargs.get('action_url', ''),
                action_text=kwargs.get('action_text', ''),
                metadata=kwargs.get('metadata', {}),
                expires_at=kwargs.get('expires_at')
            )

            # Send email notification if enabled
            if kwargs.get('send_email', True):
                notification.send_email_notification()

            logger.info(f"Created notification for {instructor.display_name}: {title}")
            return notification

        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise

    @classmethod
    def cleanup_expired_notifications(cls) -> int:
        """Clean up expired notifications"""
        try:
            cutoff_date = timezone.now()
            expired_notifications = cls.objects.filter(
                expires_at__lt=cutoff_date,
                is_dismissed=False
            )

            count = expired_notifications.count()
            if count > 0:
                expired_notifications.update(
                    is_dismissed=True,
                    dismissed_at=cutoff_date
                )
                logger.info(f"Auto-dismissed {count} expired notifications")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {e}")
            return 0


# ADDED: Instructor session management
class InstructorSession(models.Model):
    """
    Track instructor login sessions for security and analytics
    ADDED: Enhanced session tracking for security monitoring
    """

    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('Instructor')
    )

    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_('Session Key')
    )

    # Device and location information
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address')
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )

    device_type = models.CharField(
        max_length=20,
        choices=[
            ('desktop', _('Desktop')),
            ('mobile', _('Mobile')),
            ('tablet', _('Tablet')),
            ('unknown', _('Unknown'))
        ],
        default='unknown',
        verbose_name=_('Device Type')
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Location'),
        help_text=_('Approximate location based on IP')
    )

    # Session tracking
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Login Time')
    )

    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Activity')
    )

    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Logout Time')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    # Security flags
    is_suspicious = models.BooleanField(
        default=False,
        verbose_name=_('Is Suspicious'),
        help_text=_('Flagged for suspicious activity')
    )

    security_notes = models.TextField(
        blank=True,
        verbose_name=_('Security Notes')
    )

    class Meta:
        verbose_name = _('Instructor Session')
        verbose_name_plural = _('Instructor Sessions')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['instructor', '-login_time']),
            models.Index(fields=['session_key']),
            models.Index(fields=['ip_address', 'login_time']),
            models.Index(fields=['is_active', 'last_activity']),
        ]

    def __str__(self):
        return f"Session for {self.instructor.display_name} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def create_session(cls, instructor: InstructorProfile, request) -> 'InstructorSession':
        """Create a new instructor session"""
        try:
            # Extract device and location information
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = cls._get_client_ip(request)
            device_type = cls._get_device_type(user_agent)
            location = cls._get_location_from_ip(ip_address)

            session = cls.objects.create(
                instructor=instructor,
                session_key=request.session.session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                location=location
            )

            # Update instructor last login
            instructor.last_login = timezone.now()
            instructor.save(update_fields=['last_login'])

            logger.info(f"Created session for {instructor.display_name} from {ip_address}")
            return session

        except Exception as e:
            logger.error(f"Error creating instructor session: {e}")
            raise

    @staticmethod
    def _get_client_ip(request) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

    @staticmethod
    def _get_device_type(user_agent: str) -> str:
        """Determine device type from user agent"""
        ua_lower = user_agent.lower()

        mobile_indicators = ['mobile', 'android', 'iphone']
        tablet_indicators = ['tablet', 'ipad']

        if any(indicator in ua_lower for indicator in mobile_indicators):
            return 'mobile'
        elif any(indicator in ua_lower for indicator in tablet_indicators):
            return 'tablet'
        elif user_agent:
            return 'desktop'
        else:
            return 'unknown'

    @staticmethod
    def _get_location_from_ip(ip_address: str) -> str:
        """Get approximate location from IP address"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except Exception:
            return 'Unknown'

    def end_session(self) -> bool:
        """End the instructor session"""
        try:
            if self.is_active:
                self.is_active = False
                self.logout_time = timezone.now()
                self.save(update_fields=['is_active', 'logout_time'])
                logger.debug(f"Ended session {self.session_key}")
            return True
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False

    @classmethod
    def cleanup_expired_sessions(cls, days_old: int = 30) -> int:
        """Clean up old inactive sessions"""
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
            old_sessions = cls.objects.filter(
                last_activity__lt=cutoff_date,
                is_active=False
            )

            count = old_sessions.count()
            if count > 0:
                old_sessions.delete()
                logger.info(f"Cleaned up {count} old instructor sessions")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    @classmethod
    def detect_suspicious_activity(cls) -> List['InstructorSession']:
        """Detect potentially suspicious session activity"""
        suspicious_sessions = []

        try:
            # Check for multiple concurrent sessions from different IPs
            recent_time = timezone.now() - timezone.timedelta(hours=1)

            instructors_with_multiple_ips = cls.objects.filter(
                login_time__gte=recent_time,
                is_active=True
            ).values('instructor').annotate(
                ip_count=Count('ip_address', distinct=True)
            ).filter(ip_count__gt=1)

            for item in instructors_with_multiple_ips:
                sessions = cls.objects.filter(
                    instructor_id=item['instructor'],
                    login_time__gte=recent_time,
                    is_active=True
                )

                for session in sessions:
                    if not session.is_suspicious:
                        session.is_suspicious = True
                        session.security_notes = 'Multiple concurrent sessions from different IPs detected'
                        session.save(update_fields=['is_suspicious', 'security_notes'])
                        suspicious_sessions.append(session)

            logger.info(f"Detected {len(suspicious_sessions)} suspicious sessions")
            return suspicious_sessions

        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return []


# ADDED: Additional signal handlers for notification system
@receiver(post_save, sender=CourseInstructor)
def course_instructor_added(sender, instance, created, **kwargs):
    """Send notification when instructor is added to a course"""
    if created:
        try:
            instructor_profile = instance.instructor.instructor_profile

            # Create notification for the instructor
            InstructorNotification.create_notification(
                instructor=instructor_profile,
                notification_type=InstructorNotification.NotificationType.COURSE_APPROVED,
                title=_('Added to Course'),
                message=_('You have been added as an instructor to "{course_title}".').format(
                    course_title=instance.course.title
                ),
                action_url=f'/instructor/courses/{instance.course.id}/',
                action_text=_('View Course'),
                metadata={
                    'course_id': instance.course.id,
                    'role': instance.role
                }
            )

        except (AttributeError, InstructorProfile.DoesNotExist):
            logger.warning(f"Could not send notification - instructor profile not found for user {instance.instructor.id}")
        except Exception as e:
            logger.error(f"Error sending course instructor notification: {e}")


@receiver(post_save, sender=InstructorAnalytics)
def analytics_tier_change_notification(sender, instance, created, **kwargs):
    """Send notification when instructor tier is upgraded"""
    if not created:
        try:
            # Check if tier changed by comparing with previous version
            old_instance = sender.objects.get(pk=instance.pk)

            if hasattr(old_instance, '_state') and old_instance._state.adding:
                return  # Skip if this is the initial save

            # Get current tier from instructor profile
            current_tier = instance.instructor.tier

            # This is a simplified check - in practice you'd want to track tier changes more precisely
            if hasattr(instance, '_original_tier') and instance._original_tier != current_tier:
                InstructorNotification.create_notification(
                    instructor=instance.instructor,
                    notification_type=InstructorNotification.NotificationType.TIER_UPGRADED,
                    title=_('Tier Upgraded!'),
                    message=_('Congratulations! You have been upgraded to {new_tier} tier.').format(
                        new_tier=instance.instructor.get_tier_display()
                    ),
                    priority=InstructorNotification.Priority.HIGH,
                    action_url='/instructor/dashboard/',
                    action_text=_('View Dashboard'),
                    metadata={
                        'old_tier': getattr(instance, '_original_tier', 'unknown'),
                        'new_tier': current_tier,
                        'upgrade_date': timezone.now().isoformat()
                    }
                )

        except Exception as e:
            logger.error(f"Error sending tier upgrade notification: {e}")


# FINAL: Management command utilities and system health checks
class InstructorPortalSystemHealth:
    """
    System health monitoring and maintenance utilities
    ADDED: Comprehensive system health monitoring for instructor portal
    """

    @classmethod
    def run_health_check(cls) -> Dict[str, Any]:
        """Run comprehensive health check on instructor portal"""
        health_report = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        try:
            # Database connectivity check
            health_report['checks']['database'] = cls._check_database_health()

            # Cache connectivity check
            health_report['checks']['cache'] = cls._check_cache_health()

            # File storage check
            health_report['checks']['storage'] = cls._check_storage_health()

            # Data integrity checks
            health_report['checks']['data_integrity'] = cls._check_data_integrity()

            # Performance metrics
            health_report['checks']['performance'] = cls._check_performance_metrics()

            # Determine overall status
            failed_checks = [check for check in health_report['checks'].values() if not check['status']]
            if failed_checks:
                health_report['overall_status'] = 'degraded' if len(failed_checks) == 1 else 'unhealthy'

            logger.info(f"Health check completed - Status: {health_report['overall_status']}")
            return health_report

        except Exception as e:
            logger.error(f"Error running health check: {e}")
            health_report['overall_status'] = 'error'
            health_report['error'] = str(e)
            return health_report

    @staticmethod
    def _check_database_health() -> Dict[str, Any]:
        """Check database connectivity and basic operations"""
        try:
            # Test basic database operations
            count = InstructorProfile.objects.count()
            analytics_count = InstructorAnalytics.objects.count()

            return {
                'status': True,
                'message': 'Database is accessible',
                'details': {
                    'instructor_profiles': count,
                    'analytics_records': analytics_count
                }
            }
        except Exception as e:
            return {
                'status': False,
                'message': f'Database check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_cache_health() -> Dict[str, Any]:
        """Check cache connectivity and operations"""
        try:
            # Test cache operations
            test_key = 'health_check_test'
            test_value = 'test_data'

            cache.set(test_key, test_value, timeout=60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)

            if retrieved_value == test_value:
                return {
                    'status': True,
                    'message': 'Cache is working properly',
                    'details': {}
                }
            else:
                return {
                    'status': False,
                    'message': 'Cache test failed - value mismatch',
                    'details': {}
                }

        except Exception as e:
            return {
                'status': False,
                'message': f'Cache check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_storage_health() -> Dict[str, Any]:
        """Check file storage accessibility"""
        try:
            # Test storage operations
            test_filename = 'health_check_test.txt'
            test_content = b'Health check test file'

            # Save test file
            from django.core.files.base import ContentFile
            test_file = ContentFile(test_content)
            saved_path = default_storage.save(test_filename, test_file)

            # Verify file exists
            if default_storage.exists(saved_path):
                # Clean up test file
                default_storage.delete(saved_path)

                return {
                    'status': True,
                    'message': 'Storage is accessible',
                    'details': {}
                }
            else:
                return {
                    'status': False,
                    'message': 'Storage test failed - file not found after save',
                    'details': {}
                }

        except Exception as e:
            return {
                'status': False,
                'message': f'Storage check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_data_integrity() -> Dict[str, Any]:
        """Check data integrity across related models"""
        try:
            issues = []

            # Check for instructors without analytics
            instructors_without_analytics = InstructorProfile.objects.filter(
                analytics__isnull=True
            ).count()

            if instructors_without_analytics > 0:
                issues.append(f'{instructors_without_analytics} instructors without analytics records')

            # Check for orphaned sessions
            expired_sessions = CourseCreationSession.objects.filter(
                expires_at__lt=timezone.now(),
                status__in=['draft', 'paused']
            ).count()

            if expired_sessions > 10:  # Threshold for concern
                issues.append(f'{expired_sessions} expired sessions need cleanup')

            # Check for inconsistent analytics
            inconsistent_analytics = InstructorAnalytics.objects.filter(
                total_courses__gt=0,
                total_students=0
            ).count()

            if inconsistent_analytics > 0:
                issues.append(f'{inconsistent_analytics} analytics records with inconsistent data')

            return {
                'status': len(issues) == 0,
                'message': 'Data integrity check completed' if len(issues) == 0 else f'Found {len(issues)} issues',
                'details': {'issues': issues}
            }

        except Exception as e:
            return {
                'status': False,
                'message': f'Data integrity check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_performance_metrics() -> Dict[str, Any]:
        """Check system performance metrics"""
        try:
            from django.db import connection

            # Get query count
            query_count = len(connection.queries) if hasattr(connection, 'queries') else 0

            # Check for slow operations (simplified)
            slow_analytics_updates = InstructorAnalytics.objects.filter(
                last_calculated__lt=timezone.now() - timezone.timedelta(hours=24)
            ).count()

            return {
                'status': slow_analytics_updates < 10,  # Threshold
                'message': 'Performance check completed',
                'details': {
                    'query_count': query_count,
                    'stale_analytics': slow_analytics_updates
                }
            }

        except Exception as e:
            return {
                'status': False,
                'message': f'Performance check failed: {str(e)}',
                'details': {}
            }

    @classmethod
    def run_maintenance_tasks(cls) -> Dict[str, Any]:
        """Run routine maintenance tasks"""
        maintenance_report = {
            'timestamp': timezone.now().isoformat(),
            'tasks_completed': {}
        }

        try:
            # Clean up expired sessions
            expired_sessions = InstructorPortalCleanup.cleanup_expired_sessions()
            maintenance_report['tasks_completed']['expired_sessions_cleanup'] = expired_sessions

            # Clean up old analytics history
            old_analytics = InstructorPortalCleanup.cleanup_old_analytics_history()
            maintenance_report['tasks_completed']['analytics_history_cleanup'] = old_analytics

            # Clean up expired notifications
            expired_notifications = InstructorNotification.cleanup_expired_notifications()
            maintenance_report['tasks_completed']['notifications_cleanup'] = expired_notifications

            # Clean up old instructor sessions
            old_sessions = InstructorSession.cleanup_expired_sessions()
            maintenance_report['tasks_completed']['instructor_sessions_cleanup'] = old_sessions

            # Clean up orphaned files
            orphaned_files = InstructorPortalCleanup.cleanup_orphaned_files()
            maintenance_report['tasks_completed']['orphaned_files_cleanup'] = orphaned_files

            # Detect suspicious activity
            suspicious_sessions = InstructorSession.detect_suspicious_activity()
            maintenance_report['tasks_completed']['suspicious_activity_detection'] = len(suspicious_sessions)

            logger.info(f"Maintenance tasks completed: {maintenance_report}")
            return maintenance_report

        except Exception as e:
            logger.error(f"Error running maintenance tasks: {e}")
            maintenance_report['error'] = str(e)
            return maintenance_report

# Export all models for easier imports
__all__ = [
    # Core Profile Models
    'TierManager',
    'InstructorProfile',

    # Analytics Models
    'InstructorAnalytics',
    'InstructorAnalyticsHistory',

    # Course Management Models
    'CourseInstructor',
    'CourseCreationSession',
    'CourseTemplate',

    # Content Management Models
    'DraftCourseContent',
    'CourseContentDraft',

    # Dashboard and UI Models
    'InstructorDashboard',

    # Communication Models
    'InstructorNotification',

    # Security and Session Models
    'InstructorSession',

    # Utility Classes
    'InstructorPortalCleanup',
    'InstructorPortalSystemHealth',

    # Helper Functions
    'get_course_model',
    'get_category_model',
    'get_enrollment_model',
    'get_review_model',
    'generate_upload_path',
    'generate_cover_upload_path',
    'validate_social_handle',

    # Custom Validators
    'HTTPSURLValidator',
]

# Model registry for dynamic imports and API discovery
MODEL_REGISTRY = {
    'profile': InstructorProfile,
    'analytics': InstructorAnalytics,
    'analytics_history': InstructorAnalyticsHistory,
    'course_instructor': CourseInstructor,
    'dashboard': InstructorDashboard,
    'creation_session': CourseCreationSession,
    'template': CourseTemplate,
    'draft_content': DraftCourseContent,
    'content_draft': CourseContentDraft,
    'notification': InstructorNotification,
    'session': InstructorSession,
}

# Version and metadata information
VERSION = '4.0.0'
LAST_UPDATED = '2025-06-20 04:09:08'
AUTHOR = 'sujibeautysalon'

# Feature flags for progressive rollout
FEATURE_FLAGS = {
    'enhanced_analytics': True,
    'notification_system': True,
    'session_tracking': True,
    'ai_content_generation': True,
    'advanced_security': True,
    'performance_monitoring': True,
}

# Configuration constants
ANALYTICS_UPDATE_INTERVAL_HOURS = 1
SESSION_CLEANUP_DAYS = 30
NOTIFICATION_EXPIRE_DAYS = 7
FILE_CLEANUP_BATCH_SIZE = 100
HEALTH_CHECK_CACHE_TIMEOUT = 300  # 5 minutes

# Model relationship helpers for external apps
def get_instructor_profile_for_user(user):
    """Helper function to get instructor profile for a user"""
    try:
        return user.instructor_profile
    except (AttributeError, InstructorProfile.DoesNotExist):
        return None

def get_instructor_analytics(instructor_profile):
    """Helper function to get analytics for an instructor"""
    try:
        return instructor_profile.analytics
    except (AttributeError, InstructorAnalytics.DoesNotExist):
        return None

def get_instructor_dashboard(instructor_profile):
    """Helper function to get dashboard for an instructor"""
    try:
        return instructor_profile.dashboard
    except (AttributeError, InstructorDashboard.DoesNotExist):
        return None

# Add helper functions to __all__
__all__.extend([
    'MODEL_REGISTRY',
    'VERSION',
    'LAST_UPDATED',
    'AUTHOR',
    'FEATURE_FLAGS',
    'get_instructor_profile_for_user',
    'get_instructor_analytics',
    'get_instructor_dashboard',
])
