# File Path: backend/courses/validators.py
# Folder Path: /backend/courses/
# Date Created: 2025-06-15 06:46:26
# Date Revised: 2025-06-15 11:55:45
# Current Date and Time (UTC): 2025-06-15 11:55:45
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 11:55:45 UTC
# Version: 1.4.0
#
# Django Model Field Validators (Complete Implementation)
#
# Version 1.4.0 Changes:
# - ADDED: Missing imports and dependencies for complete functionality
# - INCLUDED: PIL for image validation support
# - ADDED: File extension validation utilities
# - ENHANCED: Error handling and validation messages
# - COMPLETED: All validator functions for model field requirements

import re
import os
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, URLValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

# Optional imports for enhanced validation
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# =====================================
# CORE MIGRATION-SAFE VALIDATOR FUNCTIONS
# =====================================

def validator(value):
    """
    Generic validator function that was referenced in migration.
    This function provides basic slug validation for migration compatibility.
    """
    if not value:
        return

    # Basic slug validation - alphanumeric, hyphens, and underscores only
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError(
            _('Only alphanumeric characters, hyphens, and underscores are allowed.'),
            code='invalid_slug'
        )

    # Length validation
    if len(value) < 2:
        raise ValidationError(
            _('Value must be at least 2 characters long.'),
            code='too_short'
        )

    if len(value) > 100:
        raise ValidationError(
            _('Value must be no more than 100 characters long.'),
            code='too_long'
        )


def validate_slug_format(value):
    """
    Validate slug format for URL-friendly strings.
    Enhanced slug validation with additional checks.
    """
    if not value:
        return

    # Use the generic validator as base
    validator(value)

    # Additional slug-specific checks
    if value.startswith('-') or value.endswith('-'):
        raise ValidationError(
            _('Slug cannot start or end with a hyphen.'),
            code='invalid_slug_format'
        )

    if '--' in value:
        raise ValidationError(
            _('Slug cannot contain consecutive hyphens.'),
            code='invalid_slug_format'
        )


def validate_video_url(value):
    """
    Video URL validator for supported platforms.
    Validates YouTube, Vimeo, and direct video file URLs.
    """
    if not value:
        return

    # First check if it's a valid URL structure
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError(
            _('Enter a valid URL.'),
            code='invalid_url'
        )

    # Then check for supported video platforms
    video_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://(?:www\.)?youtu\.be/[\w-]+',
        r'https?://(?:www\.)?vimeo\.com/\d+',
        r'https?://player\.vimeo\.com/video/\d+',
        r'https?://.*\.(mp4|webm|ogg|avi|mov)$',
    ]

    if not any(re.match(pattern, value, re.IGNORECASE) for pattern in video_patterns):
        raise ValidationError(
            _('Enter a valid video URL (YouTube, Vimeo, or direct video file link).'),
            code='invalid_video_url'
        )


def validate_price_range(value):
    """
    Price range validator (0 to 10,000).
    Supports both integer and decimal values.
    """
    if value is None:
        return

    # Convert to Decimal for precise comparison
    if isinstance(value, (int, float)):
        value = Decimal(str(value))

    if value < 0:
        raise ValidationError(
            _('Price cannot be negative.'),
            code='negative_price'
        )
    if value > 10000:
        raise ValidationError(
            _('Price cannot exceed $10,000.'),
            code='price_too_high'
        )


def validate_percentage(value):
    """
    Percentage validator (0 to 100).
    """
    if value is None:
        return
    if value < 0:
        raise ValidationError(
            _('Percentage cannot be negative.'),
            code='negative_percentage'
        )
    if value > 100:
        raise ValidationError(
            _('Percentage cannot exceed 100.'),
            code='percentage_too_high'
        )


def validate_duration_minutes(value):
    """
    Duration validator in minutes (0 to 10,080 - one week).
    """
    if value is None:
        return
    if value < 0:
        raise ValidationError(
            _('Duration cannot be negative.'),
            code='negative_duration'
        )
    if value > 10080:  # 7 days * 24 hours * 60 minutes
        raise ValidationError(
            _('Duration cannot exceed one week (10,080 minutes).'),
            code='duration_too_long'
        )


def validate_course_requirements(value):
    """
    Course requirements list validator (max 20 items, min 3 chars each).
    """
    value = value or []
    if not isinstance(value, list):
        raise ValidationError(
            _('Requirements must be a list.'),
            code='invalid_list'
        )
    if len(value) > 20:
        raise ValidationError(
            _('Cannot have more than 20 requirements.'),
            code='too_many_items'
        )

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(
                _('Requirement %(index)d must be a string.') % {'index': i + 1},
                code='invalid_item_type'
            )
        if len(item.strip()) < 3:
            raise ValidationError(
                _('Requirement %(index)d must be at least 3 characters long.') % {'index': i + 1},
                code='item_too_short'
            )


def validate_learning_objectives(value):
    """
    Learning objectives list validator (max 15 items, min 5 chars each).
    """
    value = value or []
    if not isinstance(value, list):
        raise ValidationError(
            _('Learning objectives must be a list.'),
            code='invalid_list'
        )
    if len(value) > 15:
        raise ValidationError(
            _('Cannot have more than 15 learning objectives.'),
            code='too_many_items'
        )

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(
                _('Learning objective %(index)d must be a string.') % {'index': i + 1},
                code='invalid_item_type'
            )
        if len(item.strip()) < 5:
            raise ValidationError(
                _('Learning objective %(index)d must be at least 5 characters long.') % {'index': i + 1},
                code='item_too_short'
            )


def validate_certificate_number(value):
    """
    Certificate number format validator.
    Expected format: CERT-{course_id}-{user_id}-{timestamp}
    """
    if not value:
        return

    if not re.match(r'^CERT-\d+-\d+-\d{14}$', value):
        raise ValidationError(
            _('Certificate number must follow format: CERT-{course_id}-{user_id}-{timestamp}'),
            code='invalid_certificate_format'
        )


def validate_tags(value):
    """
    Tags validator with format checking (max 10 items, min 2 chars each).
    """
    value = value or []
    if not isinstance(value, list):
        raise ValidationError(
            _('Tags must be a list.'),
            code='invalid_list'
        )
    if len(value) > 10:
        raise ValidationError(
            _('Cannot have more than 10 tags.'),
            code='too_many_tags'
        )

    for i, tag in enumerate(value):
        if not isinstance(tag, str):
            raise ValidationError(
                _('Tag %(index)d must be a string.') % {'index': i + 1},
                code='invalid_tag_type'
            )
        if len(tag.strip()) < 2:
            raise ValidationError(
                _('Tag %(index)d must be at least 2 characters long.') % {'index': i + 1},
                code='tag_too_short'
            )
        if not re.match(r'^[a-zA-Z0-9\s-_]+$', tag):
            raise ValidationError(
                _('Tag %(index)d contains invalid characters. Only letters, numbers, spaces, hyphens, and underscores are allowed.') % {'index': i + 1},
                code='invalid_tag_characters'
            )


def validate_phone_number(value):
    """
    Validate phone number format.
    Accepts formats like: +1234567890, (123) 456-7890, 123-456-7890, etc.
    """
    if not value:
        return

    # Remove common formatting characters
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', value)

    # Check if it's all digits and within valid length
    if not re.match(r'^\d{10,15}$', clean_phone):
        raise ValidationError(
            _('Phone number must be 10-15 digits long and may include formatting characters like +, -, (), and spaces.'),
            code='invalid_phone'
        )


def validate_rating(value):
    """
    Validate rating to be between 1 and 5.
    """
    if value is None:
        return
    if not (1 <= value <= 5):
        raise ValidationError(
            _('Rating must be between 1 and 5.'),
            code='invalid_rating'
        )


def validate_course_level(value):
    """
    Validate course level.
    """
    if not value:
        return
    valid_levels = ['beginner', 'intermediate', 'advanced']
    if value not in valid_levels:
        raise ValidationError(
            _('Course level must be one of: %(levels)s.') % {'levels': ', '.join(valid_levels)},
            code='invalid_course_level'
        )


def validate_enrollment_status(value):
    """
    Validate enrollment status.
    """
    if not value:
        return
    valid_statuses = ['active', 'completed', 'dropped', 'suspended']
    if value not in valid_statuses:
        raise ValidationError(
            _('Enrollment status must be one of: %(statuses)s.') % {'statuses': ', '.join(valid_statuses)},
            code='invalid_enrollment_status'
        )


def validate_lesson_type(value):
    """
    Validate lesson type.
    """
    if not value:
        return
    valid_types = ['video', 'text', 'quiz', 'assignment', 'lab', 'discussion']
    if value not in valid_types:
        raise ValidationError(
            _('Lesson type must be one of: %(types)s.') % {'types': ', '.join(valid_types)},
            code='invalid_lesson_type'
        )


def validate_access_level(value):
    """
    Validate access level for lessons.
    """
    if not value:
        return
    valid_levels = ['guest', 'registered', 'premium']
    if value not in valid_levels:
        raise ValidationError(
            _('Access level must be one of: %(levels)s.') % {'levels': ', '.join(valid_levels)},
            code='invalid_access_level'
        )


def validate_resource_type(value):
    """
    Validate resource type.
    """
    if not value:
        return
    valid_types = ['pdf', 'video', 'audio', 'image', 'zip', 'link', 'code', 'presentation']
    if value not in valid_types:
        raise ValidationError(
            _('Resource type must be one of: %(types)s.') % {'types': ', '.join(valid_types)},
            code='invalid_resource_type'
        )


def validate_question_type(value):
    """
    Validate question type for assessments.
    """
    if not value:
        return
    valid_types = ['multiple_choice', 'true_false', 'short_answer', 'essay', 'fill_blank']
    if value not in valid_types:
        raise ValidationError(
            _('Question type must be one of: %(types)s.') % {'types': ', '.join(valid_types)},
            code='invalid_question_type'
        )


def validate_file_extension(value, allowed_extensions):
    """
    Generic file extension validator.
    """
    if not value:
        return

    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _('File extension %(ext)s is not allowed. Allowed extensions: %(allowed)s') % {
                'ext': ext,
                'allowed': ', '.join(allowed_extensions)
            },
            code='invalid_extension'
        )


def validate_image_file(value):
    """
    Validate image file format and basic properties.
    """
    if not value:
        return

    # Check file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    validate_file_extension(value, valid_extensions)

    # Check file size (10MB max for images)
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError(
            _('Image size cannot exceed 10MB.'),
            code='image_too_large'
        )

    # If PIL is available, validate image format
    if HAS_PIL:
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise ValidationError(
                _('Invalid image file or corrupted image.'),
                code='invalid_image'
            )


def validate_video_file(value):
    """
    Validate video file format.
    """
    if not value:
        return

    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    validate_file_extension(value, valid_extensions)

    # Check file size (500MB max for videos)
    max_size = 500 * 1024 * 1024  # 500MB
    if value.size > max_size:
        raise ValidationError(
            _('Video size cannot exceed 500MB.'),
            code='video_too_large'
        )


def validate_document_file(value):
    """
    Validate document file format.
    """
    if not value:
        return

    # Check file extension
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
    validate_file_extension(value, valid_extensions)

    # Check file size (50MB max for documents)
    max_size = 50 * 1024 * 1024  # 50MB
    if value.size > max_size:
        raise ValidationError(
            _('Document size cannot exceed 50MB.'),
            code='document_too_large'
        )


# =====================================
# CLASS-BASED VALIDATORS
# =====================================

@deconstructible
class MinStrLenValidator(BaseValidator):
    """Minimum string length validator after stripping whitespace"""
    message = _('Ensure this value has at least %(limit_value)d characters (it has %(show_value)d).')
    code = 'min_length'

    def compare(self, a, b):
        return a < b

    def clean(self, x):
        return len(x.strip()) if x else 0

    def __call__(self, value):
        cleaned = self.clean(value)
        if self.compare(cleaned, self.limit_value):
            raise ValidationError(
                self.message,
                code=self.code,
                params={'limit_value': self.limit_value, 'show_value': cleaned}
            )


@deconstructible
class FileSizeValidator:
    """File size validator with configurable maximum size"""
    message = _('File size must be no more than %(max_size).1f MB.')
    code = 'file_too_large'

    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        if hasattr(value, 'size') and value.size > self.max_size:
            raise ValidationError(
                self.message % {'max_size': self.max_size / (1024 * 1024)},
                code=self.code
            )

    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_size == other.max_size


@deconstructible
class JSONListValidator:
    """Generic JSON list validator with comprehensive checking"""
    def __init__(self, max_items=None, min_str_len=None, item_type=str, allow_empty=True):
        self.max_items = max_items
        self.min_str_len = min_str_len
        self.item_type = item_type
        self.allow_empty = allow_empty

    def __call__(self, value):
        value = value or []

        if not isinstance(value, list):
            raise ValidationError(
                _('Value must be a list.'),
                code='invalid_list'
            )

        if not self.allow_empty and len(value) == 0:
            raise ValidationError(
                _('List cannot be empty.'),
                code='empty_list'
            )

        if self.max_items and len(value) > self.max_items:
            raise ValidationError(
                _('Cannot have more than %(max_items)d items.') % {'max_items': self.max_items},
                code='too_many_items'
            )

        if self.min_str_len and self.item_type == str:
            for i, item in enumerate(value):
                if not isinstance(item, str):
                    raise ValidationError(
                        _('Item %(index)d must be a string.') % {'index': i + 1},
                        code='invalid_item_type'
                    )
                if len(item.strip()) < self.min_str_len:
                    raise ValidationError(
                        _('Item %(index)d must be at least %(min_len)d characters long.') % {
                            'index': i + 1,
                            'min_len': self.min_str_len
                        },
                        code='item_too_short'
                    )

    def __eq__(self, other):
        return (isinstance(other, JSONListValidator) and
                all(getattr(self, attr) == getattr(other, attr)
                    for attr in ['max_items', 'min_str_len', 'item_type', 'allow_empty']))


# =====================================
# MIGRATION-SAFE VALIDATOR EXPORTS
# =====================================

__all__ = [
    # Core validators
    'validator',
    'validate_slug_format',

    # Media validators
    'validate_video_url',
    'validate_image_file',
    'validate_video_file',
    'validate_document_file',
    'validate_file_extension',

    # Numeric validators
    'validate_price_range',
    'validate_percentage',
    'validate_duration_minutes',
    'validate_rating',

    # List validators
    'validate_course_requirements',
    'validate_learning_objectives',
    'validate_tags',

    # Format validators
    'validate_certificate_number',
    'validate_phone_number',

    # Choice validators
    'validate_course_level',
    'validate_enrollment_status',
    'validate_lesson_type',
    'validate_access_level',
    'validate_resource_type',
    'validate_question_type',

    # Class-based validators
    'MinStrLenValidator',
    'FileSizeValidator',
    'JSONListValidator',
]
