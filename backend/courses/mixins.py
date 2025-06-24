# File Path: backend/courses/mixins.py
# Folder Path: /backend/courses/mixins.py
# Date Created: 2025-06-15 06:41:03
# Date Revised: 2025-06-15 09:42:46
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 09:42:46 UTC
# User: sujibeautysalon
# Version: 1.1.0
#
# Abstract Mixins for DRY Architecture in Course Management System (Optimized)
#
# This module provides reusable abstract mixins to eliminate code duplication
# across models and provide consistent behavior patterns. Optimized using
# helper functions to reduce code size while maintaining functionality.
#
# Version 1.1.0 Changes:
# - OPTIMIZED: Used helper functions to reduce code size
# - CONSOLIDATED: Common patterns into reusable utilities
# - MAINTAINED: All original functionality and features

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone


# =====================================
# HELPER FUNCTIONS FOR CODE REDUCTION
# =====================================

def create_index_list(*field_names):
    """Helper to create multiple indexes efficiently"""
    return [models.Index(fields=list(fields)) for fields in field_names]


def format_size_units(size_bytes):
    """Helper to format file size with units"""
    if not size_bytes:
        return "Unknown"

    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def format_duration_units(minutes):
    """Helper to format duration with units"""
    if not minutes:
        return "N/A"

    hours, mins = divmod(minutes, 60)
    parts = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if mins:
        parts.append(f"{mins} minute{'s' if mins > 1 else ''}")

    return " ".join(parts) if parts else "N/A"


def safe_file_metadata_update(instance, file_obj):
    """Helper to safely update file metadata"""
    if not file_obj:
        return

    try:
        instance.file_size = file_obj.size
        if hasattr(file_obj, 'content_type'):
            instance.mime_type = file_obj.content_type
        instance.uploaded = True
    except (AttributeError, OSError):
        pass


# =====================================
# OPTIMIZED MIXINS
# =====================================

class TimeStampedMixin(models.Model):
    """Abstract mixin for consistent timestamp fields"""
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']
        indexes = create_index_list(['created_date'], ['updated_date'])


class OrderedMixin(models.Model):
    """Abstract mixin for automatic ordering functionality"""
    order = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True
        ordering = ['order']
        indexes = create_index_list(['order'])

    def get_next_order(self, parent_field):
        """Get next order value for parent field"""
        parent_value = getattr(self, parent_field)
        if not parent_value:
            return 1

        return (self.__class__.objects
                .filter(**{parent_field: parent_value})
                .aggregate(max_order=models.Max('order'))['max_order'] or 0) + 1

    def save(self, *args, **kwargs):
        """Auto-set order if not provided"""
        if not self.pk and self.order == 1 and hasattr(self.Meta, 'parent_field'):
            self.order = self.get_next_order(self.Meta.parent_field)
        super().save(*args, **kwargs)


class SlugMixin(models.Model):
    """Abstract mixin for automatic slug generation"""
    slug = models.SlugField(unique=True, blank=True, max_length=180)

    class Meta:
        abstract = True
        indexes = create_index_list(['slug'])

    def get_slug_source(self):
        """Get slug source field name"""
        return getattr(self, 'slug_source', 'title')

    def generate_unique_slug(self):
        """Generate unique slug with versioning support"""
        source_field = self.get_slug_source()
        base_slug = slugify(getattr(self, source_field))

        # Handle course versioning
        if all(hasattr(self, attr) for attr in ['version', 'is_draft']):
            if self.is_draft and getattr(self, 'parent_version', None):
                base_slug = f"{base_slug}-v{self.version}-draft"
            elif self.version > 1.0:
                base_slug = f"{base_slug}-v{str(self.version).replace('.', '-')}"

        # Ensure uniqueness
        slug, counter = base_slug, 1
        queryset = self.__class__.objects.filter(slug=slug)

        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            queryset = self.__class__.objects.filter(slug=slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        return slug

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)


class StateMixin(models.Model):
    """Abstract mixin for common state fields"""
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        indexes = create_index_list(['is_active'])


class DurationMixin(models.Model):
    """Abstract mixin for duration handling"""
    duration_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duration in minutes"
    )

    class Meta:
        abstract = True

    def clean(self):
        """Validate duration"""
        super().clean()
        if self.duration_minutes and self.duration_minutes < 0:
            raise ValidationError("Duration must be positive")

    @property
    def duration_display(self):
        """Human-readable duration format"""
        return format_duration_units(self.duration_minutes)


class PublishableMixin(models.Model):
    """Abstract mixin for publishable models"""
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        indexes = create_index_list(['is_published'], ['published_date'])

    def publish(self):
        """Publish with timestamp"""
        if not self.is_published:
            self.is_published = True
            if not self.published_date:
                self.published_date = timezone.now()
            self.save(update_fields=['is_published', 'published_date'])

    def unpublish(self):
        """Unpublish item"""
        if self.is_published:
            self.is_published = False
            self.save(update_fields=['is_published'])


class FileTrackingMixin(models.Model):
    """Abstract mixin for file upload tracking"""
    storage_key = models.CharField(
        max_length=512, blank=True, null=True,
        help_text="Cloud storage path/object name"
    )
    uploaded = models.BooleanField(
        default=False, help_text="Whether file uploaded successfully"
    )
    file_size = models.PositiveBigIntegerField(
        blank=True, null=True, help_text="File size in bytes"
    )
    mime_type = models.CharField(
        max_length=120, blank=True, null=True,
        help_text="MIME type of uploaded file"
    )

    class Meta:
        abstract = True
        indexes = create_index_list(['uploaded'], ['mime_type'])

    @property
    def file_size_display(self):
        """Human-readable file size"""
        return format_size_units(self.file_size)

    def update_file_metadata(self, file_obj):
        """Update file metadata from file object"""
        safe_file_metadata_update(self, file_obj)


class AnalyticsMixin(models.Model):
    """Abstract mixin for analytics tracking"""
    view_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = create_index_list(['view_count'], ['last_accessed'])

    def increment_view_count(self):
        """Increment view count"""
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])

    def reset_analytics(self):
        """Reset analytics to defaults"""
        self.view_count = 0
        self.save(update_fields=['view_count'])
