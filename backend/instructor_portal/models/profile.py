
# InstructorProfile, TierManager models
#
# File Path: instructor_portal/models/profile.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 12:57:54
# Date Revised: 2025-06-26 12:57:54
# Current Date and Time (UTC): 2025-06-26 12:57:54
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 12:57:54 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# InstructorProfile model - Core instructor profile data
# Split from original models.py maintaining exact code compatibility

import logging
import uuid
from decimal import Decimal
from typing import Dict, Any, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import (
    TierManager, HTTPSURLValidator, validate_social_handle,
    generate_upload_path, generate_cover_upload_path,
    get_course_model, get_enrollment_model, get_review_model
)

logger = logging.getLogger(__name__)
User = get_user_model()


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
            # Import here to avoid circular imports
            from .dashboard import InstructorDashboard
            from .analytics import InstructorAnalytics

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
        # Import here to avoid circular imports
        from .course_link import CourseInstructor
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
