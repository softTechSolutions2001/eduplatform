#
# File Path: backend/courses/models/mixins.py
# Folder Path: backend/courses/models/
# Date Created: 2025-06-15 06:41:03
# Date Revised: 2025-06-30 10:00:00
# Current Date and Time (UTC): 2025-06-30 10:00:00
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-30 10:00:00 UTC
# User: softTechSolutions2001
# Version: 1.4.0
#
# FIXED: Code Review Issues - Centralized Utils, N+1 Query Fix, Sharding Support
#
# This module provides reusable abstract mixins to eliminate code duplication
# across models and provide consistent behavior patterns.
#
# Version 1.4.0 Changes:
# - FIXED 🔴: SlugMixin now uses centralized utils.generate_unique_slug() to prevent drift
# - FIXED 🟡: OrderedMixin.get_next_order() optimized to prevent N+1 queries with caching
# - FIXED 🟢: create_index_list() now supports explicit db_tablespace for sharded setups
# - MAINTAINED: All existing functionality and backward compatibility
# - ENHANCED: Performance optimizations and better error handling

from django.db import models, transaction
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
import uuid
import logging

logger = logging.getLogger(__name__)

# =====================================
# CENTRALIZED UTILITY FUNCTIONS
# =====================================

def generate_unique_slug(instance, base_text, slug_field='slug', source_field='title'):
    """
    Centralized unique slug generation utility to prevent code drift

    Args:
        instance: Model instance
        base_text: Text to slugify
        slug_field: Field name for the slug (default: 'slug')
        source_field: Source field name (default: 'title')

    Returns:
        str: Unique slug
    """
    base_slug = slugify(base_text)

    # Handle course versioning if applicable
    if all(hasattr(instance, attr) for attr in ['version', 'is_draft']):
        if instance.is_draft and getattr(instance, 'parent_version', None):
            base_slug = f"{base_slug}-v{instance.version}-draft"
        elif instance.version > 1.0:
            base_slug = f"{base_slug}-v{str(instance.version).replace('.', '-')}"

    # Ensure uniqueness
    slug, counter = base_slug, 1
    queryset = instance.__class__.objects.filter(**{slug_field: slug})

    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        queryset = instance.__class__.objects.filter(**{slug_field: slug})
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

    return slug


def create_index_list(*field_names, db_tablespace=None):
    """
    Helper to create multiple indexes efficiently with optional tablespace support

    Args:
        *field_names: Variable number of field name tuples/lists
        db_tablespace: Optional tablespace name for sharded database setups

    Returns:
        list: List of Django Index objects
    """
    indexes = []
    for fields in field_names:
        index_kwargs = {'fields': list(fields)}
        if db_tablespace:
            index_kwargs['db_tablespace'] = db_tablespace
        indexes.append(models.Index(**index_kwargs))
    return indexes


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
# BASIC MIXINS
# =====================================

class BaseModelMixin(models.Model):
    """Base mixin with UUID primary key for all models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """Abstract mixin for consistent timestamp fields"""
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']
        indexes = create_index_list(['created_date'], ['updated_date'])


class TimeStampedModelMixin(models.Model):
    """Alias for TimeStampedMixin for backward compatibility"""
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']
        indexes = create_index_list(['created_date'], ['updated_date'])


# =====================================
# OPTIMIZED MIXINS
# =====================================

class OrderedMixin(models.Model):
    """
    Abstract mixin for automatic ordering functionality
    FIXED: Optimized to prevent N+1 queries with intelligent caching
    """
    # Use 0 to signal "unset" so first child becomes 1
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['order']
        indexes = create_index_list(['order'])

    def get_next_order(self, parent_field=None, use_cache=True):
        """
        Get next order value for parent field with caching to prevent N+1 queries

        Args:
            parent_field: Field name to filter by. Should be provided by the calling model.
            use_cache: Whether to use caching for performance (default: True)

        Returns:
            int: Next order value
        """
        try:
            # If no parent field provided, default to order 1
            if parent_field is None:
                logger.debug(f"No parent_field provided for {self.__class__.__name__}.get_next_order() - using default order 1")
                return 1

            parent_value = getattr(self, parent_field, None)
            if not parent_value:
                return 1

            # Create cache key for this parent-child relationship
            cache_key = f"max_order_{self.__class__.__name__}_{parent_field}_{parent_value}"

            if use_cache:
                # Try to get cached max order first
                cached_max_order = cache.get(cache_key)
                if cached_max_order is not None:
                    return cached_max_order + 1

            # Query database for max order
            max_order = (self.__class__.objects
                        .filter(**{parent_field: parent_value})
                        .aggregate(max_order=models.Max('order'))['max_order'] or 0)

            # Cache the result for 5 minutes to prevent repeated queries
            if use_cache:
                cache.set(cache_key, max_order, 300)  # 5 minutes

            return max_order + 1

        except (AttributeError, ValueError) as e:
            logger.error(f"Error in {self.__class__.__name__}.get_next_order(): {e}")
            return 1  # Safe default if something goes wrong

    def save(self, *args, **kwargs):
        """
        Auto-set order if not provided
        FIXED: No longer relies on Meta.parent_field
        """
        if not self.pk and (self.order in (None, 0)):
            # Each model that uses OrderedMixin should override get_next_order()
            # with its specific parent_field or implement custom ordering logic
            try:
                # Try to call the model's specific get_next_order implementation
                with transaction.atomic():
                    self.order = self.get_next_order()
            except Exception as e:
                logger.warning(f"Could not auto-set order for {self.__class__.__name__}: {e}")
                # Keep default order of 1
                self.order = 1
        super().save(*args, **kwargs)

    def invalidate_order_cache(self, parent_field=None):
        """
        Invalidate cached order values when order changes

        Args:
            parent_field: Field name to clear cache for
        """
        if parent_field:
            parent_value = getattr(self, parent_field, None)
            if parent_value:
                cache_key = f"max_order_{self.__class__.__name__}_{parent_field}_{parent_value}"
                cache.delete(cache_key)


class SlugMixin(models.Model):
    """
    Abstract mixin for automatic slug generation
    FIXED: Now uses centralized generate_unique_slug utility to prevent code drift
    """
    slug = models.SlugField(unique=True, blank=True, max_length=180)

    class Meta:
        abstract = True
        indexes = create_index_list(['slug'])

    def get_slug_source(self):
        """Get slug source field name"""
        return getattr(self, 'slug_source', 'title')

    def generate_unique_slug(self):
        """
        Generate unique slug using centralized utility
        FIXED: Delegates to centralized utils.generate_unique_slug to prevent code drift
        """
        source_field = self.get_slug_source()
        source_text = getattr(self, source_field, '')

        return generate_unique_slug(
            instance=self,
            base_text=source_text,
            slug_field='slug',
            source_field=source_field
        )

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)


class SluggedModelMixin(SlugMixin):
    """Alias for SlugMixin for backward compatibility"""
    class Meta(SlugMixin.Meta):
        abstract = True


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


class PublishableModelMixin(PublishableMixin):
    """Alias for PublishableMixin for backward compatibility"""
    class Meta(PublishableMixin.Meta):
        abstract = True


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


class RateableModelMixin(models.Model):
    """Mixin for models that can be rated by users"""
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0,
        help_text="Average rating (0-5)"
    )
    ratings_count = models.PositiveIntegerField(
        default=0, help_text="Number of ratings received"
    )

    class Meta:
        abstract = True
        indexes = create_index_list(['average_rating'])

    def update_rating_stats(self):
        """Update rating statistics based on related reviews"""
        # To be implemented by child classes based on their rating relationship
        pass


# =====================================
# SHARDED DATABASE HELPER MIXINS
# =====================================

class ShardedIndexMixin:
    """
    Helper mixin for models that need sharded database index support
    FIXED: Provides explicit db_tablespace support for create_index_list
    """

    @classmethod
    def get_sharded_indexes(cls, tablespace_name=None):
        """
        Get indexes with optional tablespace for sharded setups

        Args:
            tablespace_name: Name of the tablespace for sharded databases

        Returns:
            list: Indexes with tablespace configuration
        """
        # Get base indexes from Meta if they exist
        base_indexes = getattr(cls.Meta, 'indexes', [])

        if not tablespace_name:
            return base_indexes

        # Create new indexes with tablespace
        sharded_indexes = []
        for index in base_indexes:
            if hasattr(index, 'fields'):
                sharded_indexes.append(
                    models.Index(fields=index.fields, db_tablespace=tablespace_name)
                )

        return sharded_indexes
