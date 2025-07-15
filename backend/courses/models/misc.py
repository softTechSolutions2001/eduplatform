# File Path: backend/courses/models/misc.py
# Folder Path: backend/courses/models/
# Date Created: 2025-06-26 15:30:12
# Date Revised: 2025-07-08 15:22:41
# Current Date and Time (UTC): 2025-07-08 15:22:41
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-08 15:22:41 UTC
# User: MohithaSanthanam2010
# Version: 6.1.0

import copy
import logging
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from ..utils.model_helpers import (
    create_char_field,
    create_json_field,
    create_text_field,
)
from .mixins import TimeStampedMixin

logger = logging.getLogger(__name__)


class Bookmark(TimeStampedMixin):
    """
    User bookmarks for quick access to courses, lessons, etc.
    FIXED: Enhanced with UUID support and comprehensive validation
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        db_index=True,
        help_text="User who created this bookmark",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        db_index=True,
        help_text="Type of content being bookmarked",
    )
    # FIXED: Added db_index=True for GenericForeignKey performance
    object_id = models.CharField(
        max_length=255,
        db_index=True,  # FIXED: Add index for faster lookups
        help_text="ID of the bookmarked object (supports both integer and UUID)",
    )
    # FIXED: Enhanced GenericForeignKey for proper content linking
    content_object = GenericForeignKey("content_type", "object_id")

    title = create_char_field(
        max_length=200,
        blank=True,
        default="",  # FIXED: Use default='' instead of null=True for consistency
        help_text="Custom title for the bookmark",
    )
    notes = create_text_field(
        blank=True, default="", help_text="Personal notes about the bookmarked content"
    )
    position = models.PositiveIntegerField(
        default=0, help_text="Order position for bookmark organization"
    )

    # Enhanced metadata
    is_favorite = models.BooleanField(
        default=False, help_text="Whether this bookmark is marked as favorite"
    )
    tags = create_json_field(
        default=list,
        max_items=10,
        min_str_len=2,
        help_text="Tags for organizing bookmarks",
    )

    def clean(self):
        """
        Enhanced validation for bookmark data
        FIXED: Added missing clean() method for validation
        """
        super().clean()

        # Validate title length if provided
        if self.title and len(self.title.strip()) < 2:
            raise ValidationError("Bookmark title must be at least 2 characters long")

        # Check for duplicate bookmarks for the same user and content
        if not self.pk:
            existing = Bookmark.objects.filter(
                user=self.user, content_type=self.content_type, object_id=self.object_id
            ).exists()

            if existing:
                raise ValidationError("You have already bookmarked this content")

        # Validate allowed content types (prevent spoofing)
        allowed_content_types = ["course", "lesson", "module", "resource", "assessment"]

        if (
            self.content_type
            and self.content_type.model.lower() not in allowed_content_types
        ):
            raise ValidationError(
                f"Content type '{self.content_type.model}' is not supported for bookmarks"
            )

        # Validate position
        if self.position < 0:
            raise ValidationError("Position must be non-negative")

    def save(self, *args, **kwargs):
        """
        Enhanced save with automatic title generation
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                # Auto-generate title if not provided
                if not self.title and self.content_object:
                    try:
                        # Try to get title from the content object
                        if hasattr(self.content_object, "title"):
                            self.title = self.content_object.title[
                                :200
                            ]  # Truncate to field limit
                        elif hasattr(self.content_object, "name"):
                            self.title = self.content_object.name[:200]
                        else:
                            self.title = f"{self.content_type.name.title()} Bookmark"
                    except Exception as e:
                        logger.warning(f"Error generating bookmark title: {e}")
                        self.title = f"{self.content_type.model.title()} Bookmark"

                # Set default position with atomic transaction to prevent race conditions
                if not self.pk and self.position == 0:
                    max_position = (
                        Bookmark.objects.select_for_update()
                        .filter(user=self.user)
                        .aggregate(max_pos=models.Max("position"))["max_pos"]
                        or 0
                    )
                    self.position = max_position + 1

                super().save(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error saving bookmark: {e}")
            raise

    def get_url(self):
        """Get the URL for the bookmarked content"""
        try:
            if hasattr(self.content_object, "get_absolute_url"):
                return self.content_object.get_absolute_url()
            return None
        except Exception as e:
            logger.debug(f"Error getting bookmark URL: {e}")
            return None

    def __str__(self):
        return f"Bookmark: {self.title or 'Untitled'} ({self.user.username})"

    class Meta:
        app_label = "courses"
        db_table = "courses_bookmark"
        verbose_name = _("Bookmark")
        verbose_name_plural = _("Bookmarks")
        ordering = ["position", "-created_date"]
        indexes = [
            models.Index(fields=["user", "position"]),
            models.Index(fields=["user", "is_favorite"]),
            # FIXED: Replaced deprecated index_together with indexes
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user", "content_type", "object_id"]),
        ]
        # REMOVED: Deprecated index_together - replaced with indexes above
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_bookmark_per_user",
                violation_error_message="You have already bookmarked this content",
            )
        ]


class UserPreference(TimeStampedMixin):
    """
    User preferences for the learning platform
    FIXED: Enhanced with comprehensive validation and settings organization
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_preferences",
        help_text="User these preferences belong to",
    )

    # Notification preferences
    email_notifications = models.BooleanField(
        default=True, help_text="Receive email notifications for course updates"
    )
    push_notifications = models.BooleanField(
        default=True, help_text="Receive push notifications on supported devices"
    )
    reminder_frequency = create_char_field(
        max_length=20,
        choices=[
            ("never", _("Never")),
            ("daily", _("Daily")),
            ("weekly", _("Weekly")),
            ("biweekly", _("Bi-weekly")),
            ("monthly", _("Monthly")),
        ],
        default="weekly",
        help_text="How often to receive study reminders",
    )

    # Display preferences
    theme = create_char_field(
        max_length=20,
        choices=[
            ("system", _("System Default")),
            ("light", _("Light")),
            ("dark", _("Dark")),
            ("high_contrast", _("High Contrast")),
        ],
        default="system",
        help_text="Visual theme preference",
    )
    language = create_char_field(
        max_length=10, default="en", help_text="Preferred language code (ISO 639-1)"
    )
    timezone = create_char_field(
        max_length=50, blank=True, default="", help_text="User's preferred timezone"
    )

    # Learning preferences
    autoplay_videos = models.BooleanField(
        default=True, help_text="Automatically play videos when starting lessons"
    )
    video_playback_speed = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text="Default video playback speed (0.25 to 3.00)",
    )
    auto_advance_lessons = models.BooleanField(
        default=False, help_text="Automatically advance to next lesson after completion"
    )

    # Content filtering and accessibility
    content_filters = create_json_field(
        default=dict, help_text="Content filtering preferences as JSON"
    )
    accessibility = create_json_field(
        default=dict, help_text="Accessibility settings as JSON"
    )

    # Privacy preferences
    profile_visibility = create_char_field(
        max_length=20,
        choices=[
            ("public", _("Public")),
            ("students_only", _("Students Only")),
            ("private", _("Private")),
        ],
        default="students_only",
        help_text="Who can view your profile and progress",
    )
    show_progress_to_instructors = models.BooleanField(
        default=True, help_text="Allow instructors to see your detailed progress"
    )

    def clean(self):
        """
        Enhanced validation for user preferences
        FIXED: Added comprehensive validation
        """
        super().clean()

        # Validate video playback speed
        if self.video_playback_speed < 0.25 or self.video_playback_speed > 3.00:
            raise ValidationError("Video playback speed must be between 0.25 and 3.00")

        # Validate language code format
        if self.language and not self.language.isalpha():
            raise ValidationError("Language must be a valid language code")

        # Validate timezone if provided
        if self.timezone:
            try:
                import pytz

                if self.timezone not in pytz.all_timezones:
                    raise ValidationError("Invalid timezone")
            except ImportError:
                # If pytz is not available, just check basic format
                if len(self.timezone) > 50:
                    raise ValidationError("Timezone name too long")

        # Validate JSON fields
        if not isinstance(self.content_filters, dict):
            self.content_filters = {}

        if not isinstance(self.accessibility, dict):
            self.accessibility = {}

    def save(self, *args, **kwargs):
        """
        Enhanced save with transaction for atomicity
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in UserPreference.save() for user {self.user.username}: {e}"
            )
            raise

    def get_effective_theme(self):
        """Get the effective theme based on system preference"""
        if self.theme == "system":
            # In a real implementation, this would detect system theme
            return "light"  # Default fallback
        return self.theme

    def get_notification_settings(self):
        """Get consolidated notification settings"""
        return {
            "email": self.email_notifications,
            "push": self.push_notifications,
            "reminder_frequency": self.reminder_frequency,
        }

    def update_content_filter(self, filter_name, value):
        """
        Update a specific content filter setting
        FIXED: Work on a copy to avoid race conditions and use transaction
        """
        try:
            with transaction.atomic():
                # Work on a copy to avoid race conditions
                tmp = (
                    copy.deepcopy(self.content_filters) if self.content_filters else {}
                )
                tmp[filter_name] = value

                # Update directly in the database to avoid race conditions
                UserPreference.objects.filter(pk=self.pk).update(content_filters=tmp)

                # Update instance to reflect changes
                self.content_filters = tmp

                logger.debug(
                    f"Updated content filter {filter_name} for user {self.user.username}"
                )
        except Exception as e:
            logger.error(
                f"Error updating content filter for user {self.user.username}: {e}"
            )
            raise

    def update_accessibility_setting(self, setting_name, value):
        """
        Update a specific accessibility setting
        FIXED: Work on a copy to avoid race conditions and use transaction
        """
        try:
            with transaction.atomic():
                # Work on a copy to avoid race conditions
                tmp = copy.deepcopy(self.accessibility) if self.accessibility else {}
                tmp[setting_name] = value

                # Update directly in the database to avoid race conditions
                UserPreference.objects.filter(pk=self.pk).update(accessibility=tmp)

                # Update instance to reflect changes
                self.accessibility = tmp

                logger.debug(
                    f"Updated accessibility setting {setting_name} for user {self.user.username}"
                )
        except Exception as e:
            logger.error(
                f"Error updating accessibility setting for user {self.user.username}: {e}"
            )
            raise

    def reset_to_defaults(self):
        """
        Reset all preferences to default values
        FIXED: Use transaction for atomicity
        """
        try:
            with transaction.atomic():
                self.email_notifications = True
                self.push_notifications = True
                self.reminder_frequency = "weekly"
                self.theme = "system"
                self.language = "en"
                self.timezone = ""
                self.autoplay_videos = True
                self.video_playback_speed = 1.00
                self.auto_advance_lessons = False
                self.content_filters = {}
                self.accessibility = {}
                self.profile_visibility = "students_only"
                self.show_progress_to_instructors = True
                self.save()

                logger.info(
                    f"Reset preferences to defaults for user {self.user.username}"
                )
        except Exception as e:
            logger.error(
                f"Error resetting preferences for user {self.user.username}: {e}"
            )
            raise

    def __str__(self):
        return f"Preferences: {self.user.username}"

    class Meta:
        app_label = "courses"
        db_table = "courses_userpreference"
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences")
        indexes = [
            models.Index(fields=["theme"]),
            models.Index(fields=["language"]),
            models.Index(fields=["profile_visibility"]),
            # user field already has implicit index as OneToOneField
        ]
