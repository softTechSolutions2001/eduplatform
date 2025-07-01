# File Path: instructor_portal/models/notifications.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-27 03:27:18
# Date Revised: 2025-06-27 03:48:02
# Current Date and Time (UTC): 2025-06-27 03:48:02
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 03:48:02 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Instructor notifications model - Notification system for instructors
# Restored from original models.py to maintain backward compatibility

import logging
from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()


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
        'InstructorProfile',
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
    def create_notification(cls, instructor, notification_type: str,
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


@receiver(post_save, sender='instructor_portal.CourseInstructor')
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

        except (AttributeError, Exception) as e:
            logger.warning(f"Could not send notification - instructor profile not found: {e}")


@receiver(post_save, sender='instructor_portal.InstructorAnalytics')
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
