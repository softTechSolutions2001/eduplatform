# File Path: instructor_portal/models/analytics.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:01:07
# Date Revised: 2025-06-27 03:27:18
# Author: softTechSolutions2001
# Version: 1.0.1
#
# InstructorAnalytics models - Analytics and performance tracking
# Split from original models.py maintaining exact code compatibility

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import TierManager, get_course_model, get_enrollment_model, get_review_model
from .profile import InstructorProfile  # Import the actual class for signal registration

logger = logging.getLogger(__name__)
User = get_user_model()


# NEW: Separated analytics model for better organization
class InstructorAnalytics(models.Model):
    """
    Instructor analytics and performance metrics - separated for better organization
    ADDED: Comprehensive analytics tracking with caching and freshness checks
    """

    instructor = models.OneToOneField(
        'InstructorProfile',
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

            # Move cache.set into try block to ensure it's deleted on exception
            if cache.get(cache_key) and not force:
                return False

            try:
                cache.set(cache_key, True, timeout=300)  # 5 minute lock

                # Get related models
                Course = get_course_model()
                Enrollment = get_enrollment_model()
                Review = get_review_model()

                # Import here to avoid circular imports
                from .course_link import CourseInstructor

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

                logger.debug(f"Updated analytics for instructor {self.instructor.display_name}")
                return True
            finally:
                # Always clear cache lock, even on exception
                cache.delete(cache_key)

        except Exception as e:
            logger.error(f"Error updating instructor analytics for {self.instructor.id}: {e}")
            return False

    def _update_instructor_tier(self):
        """Update instructor tier based on performance metrics"""
        try:
            # Import here to avoid circular imports
            from .profile import InstructorProfile

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
        'InstructorProfile',
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
    def create_snapshot(cls, instructor_profile, data_type: str = 'daily'):
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


@receiver(post_save, sender=InstructorProfile, weak=False)
def create_instructor_analytics(sender, instance, created, **kwargs):
    """Create analytics record for new instructor profiles"""
    if created:
        try:
            InstructorAnalytics.objects.create(instructor=instance)
            logger.info(f"Created analytics for instructor {instance.display_name}")
        except Exception as e:
            logger.error(f"Error creating analytics for instructor {instance.id}: {e}")
