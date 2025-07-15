# File Path: backend/courses/utils/core.py
# Folder Path: backend/courses/utils/
# Date Revised: 2025-06-30 17:33:14
# Current Date and Time (UTC): 2025-06-30 17:33:14
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-06-30 17:33:14 UTC
# User: cadsanthanamNew
# Version: 5.0.1
#
# Production-Ready Core Utility Functions for Course Management System
# Previously located in courses/utils.py - Moved for modular organization
#
# This module provides reusable utility functions with comprehensive fixes
# from three code reviews including security enhancements, performance
# optimizations, and production-ready error handling.

import hashlib
import uuid
import re
import html
import logging
import os
from datetime import timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal, InvalidOperation

from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db.models import Count, Avg, Q, Sum, F, Prefetch
from django.db import transaction, IntegrityError
from django.conf import settings

logger = logging.getLogger(__name__)

# Cache timeouts for performance optimization
COURSE_STATS_CACHE_TIMEOUT = 300  # 5 minutes
ANALYTICS_CACHE_TIMEOUT = 600    # 10 minutes
SLUG_CACHE_TIMEOUT = 1800       # 30 minutes

# Security constants
MAX_FILENAME_LENGTH = 255
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'm4v'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'}

# Content security patterns
DANGEROUS_HTML_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'<object[^>]*>.*?</object>',
    r'<embed[^>]*>.*?</embed>',
    r'<applet[^>]*>.*?</applet>',
    r'<form[^>]*>.*?</form>',
    r'<iframe[^>]*>.*?</iframe>',
    r'javascript:',
    r'vbscript:',
    r'data:text/html',
    r'onload\s*=',
    r'onerror\s*=',
    r'onclick\s*=',
    r'onmouseover\s*=',
]

COMPILED_DANGEROUS_PATTERNS = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in DANGEROUS_HTML_PATTERNS]

# Access Control Messages with enhanced security
DEFAULT_PREMIUM_CONTENT_MESSAGE = """
<div class="premium-content-notice" role="alert">
    <h2>{title} - Premium Content</h2>
    <p>This content requires a premium subscription.</p>
    <p><a href="/pricing" class="btn btn-primary">Upgrade Your Account</a></p>
</div>
"""

DEFAULT_REGISTERED_CONTENT_MESSAGE = """
<div class="preview-content" role="alert">
    <h2>{title} - Preview</h2>
    <p>Register for free to access this content.</p>
    <p><a href="/register" class="btn btn-primary">Register Now</a></p>
</div>
"""


# =====================================
# ENHANCED ACCESS CONTROL UTILITIES
# =====================================

def get_user_access_level(request):
    """
    DEPRECATED: Use get_unified_user_access_level from validation.py instead

    This function is maintained for backward compatibility but delegates
    to the consolidated access level logic in validation.py

    FIXED: Access control logic duplication (C-3)
    """
    try:
        from ..validation import get_unified_user_access_level
        user = request.user if request and hasattr(request, 'user') else None
        return get_unified_user_access_level(user)
    except ImportError:
        logger.error("Could not import get_unified_user_access_level from validation.py")
        # Fallback implementation
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return 'guest'
        return 'registered'


def get_restricted_content_message(title: str, access_level: str) -> str:
    """
    Get appropriate message for restricted content with enhanced security
    FIXED: XSS prevention and input validation
    """
    # Sanitize title input
    if not isinstance(title, str):
        title = "Content"

    # Remove dangerous characters and limit length
    title = re.sub(r'[<>"\']', '', title)[:100]

    if access_level == 'guest':
        return DEFAULT_REGISTERED_CONTENT_MESSAGE.format(title=title)
    else:
        return DEFAULT_PREMIUM_CONTENT_MESSAGE.format(title=title)


# =====================================
# ENHANCED FORMATTING UTILITIES
# =====================================

def format_duration(minutes: Optional[Union[int, float, str]]) -> str:
    """
    Convert duration in minutes to human-readable format with enhanced validation
    FIXED: Input validation and type safety
    """
    if minutes is None:
        return "N/A"

    try:
        # Handle string inputs
        if isinstance(minutes, str):
            minutes = minutes.strip()
            if not minutes:
                return "N/A"
            minutes = float(minutes)

        # Convert to int for processing
        minutes = int(float(minutes))

        if minutes < 0:
            return "Invalid duration"

        if minutes == 0:
            return "0 minutes"

        hours, mins = divmod(minutes, 60)
        parts = []

        if hours:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if mins:
            parts.append(f"{mins} minute{'s' if mins > 1 else ''}")

        return " ".join(parts)

    except (ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Invalid duration value: {minutes}, error: {e}")
        return "Invalid duration"


def format_filesize(size: Optional[Union[int, float, str]]) -> str:
    """
    Convert file size in bytes to human-readable format with enhanced validation
    FIXED: Input validation and precision handling
    """
    if size is None:
        return "Unknown"

    try:
        # Handle string inputs
        if isinstance(size, str):
            size = size.strip()
            if not size:
                return "Unknown"
            size = float(size)

        # Convert to float for calculations
        file_size = float(size)

        if file_size < 0:
            return "Invalid size"

        if file_size == 0:
            return "0 B"

        # Use binary units (1024) for file sizes
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if file_size < 1024.0:
                if unit == 'B':
                    return f"{int(file_size)} {unit}"
                else:
                    return f"{file_size:.1f} {unit}"
            file_size /= 1024.0

        return f"{file_size:.1f} PB"

    except (ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Invalid file size value: {size}, error: {e}")
        return "Invalid size"


def format_time_spent(seconds: Optional[Union[int, float, str]]) -> str:
    """
    Convert time spent in seconds to human-readable format with enhanced validation
    FIXED: Input validation and edge case handling
    """
    if seconds is None:
        return "0 minutes"

    try:
        # Handle string inputs
        if isinstance(seconds, str):
            seconds = seconds.strip()
            if not seconds:
                return "0 minutes"
            seconds = float(seconds)

        # Convert to int for processing
        seconds = int(float(seconds))

        if seconds <= 0:
            return "0 minutes"

        if seconds < 60:
            return "Less than 1 minute"

        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []
        if hours:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

        return " ".join(parts)

    except (ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Invalid time value: {seconds}, error: {e}")
        return "Invalid time"


def format_price(price: Optional[Union[Decimal, float, int, str]], currency: str = "USD") -> str:
    """
    Format price with proper currency display and validation
    ADDED: Price formatting with currency support
    """
    if price is None:
        return "Free"

    try:
        # Handle string inputs
        if isinstance(price, str):
            price = price.strip()
            if not price:
                return "Free"
            price = Decimal(price)
        elif isinstance(price, (int, float)):
            price = Decimal(str(price))

        if price <= 0:
            return "Free"

        # Format based on currency
        if currency.upper() == "USD":
            return f"${price:,.2f}"
        else:
            return f"{price:,.2f} {currency}"

    except (ValueError, TypeError, InvalidOperation) as e:
        logger.warning(f"Invalid price value: {price}, error: {e}")
        return "Invalid price"


# =====================================
# ENHANCED CERTIFICATE UTILITIES
# =====================================

def generate_certificate_number(course_id: int, user_id: int, timestamp=None) -> str:
    """
    Generate a unique certificate number with enhanced validation
    FIXED: Input validation and collision prevention
    """
    try:
        # Validate inputs
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("Invalid course_id")
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user_id")

        if timestamp is None:
            timestamp = timezone.now()

        # Generate with microseconds for uniqueness
        timestamp_str = timestamp.strftime('%Y%m%d%H%M%S%f')[:17]  # Include microseconds
        uuid_component = uuid.uuid4().hex[:4]  # Added for additional uniqueness

        return f"CERT-{course_id:06d}-{user_id:06d}-{timestamp_str}-{uuid_component}"

    except Exception as e:
        logger.error(f"Error generating certificate number: {e}")
        # Fallback to UUID-based generation
        return f"CERT-{uuid.uuid4().hex[:16].upper()}"


def generate_verification_hash(certificate_number: str, enrollment_id: Optional[int] = None,
                             issue_date=None) -> str:
    """
    Generate a verification hash for certificate validation with enhanced security
    FIXED: Security enhancement and collision resistance
    """
    try:
        # Validate inputs
        if not isinstance(certificate_number, str) or not certificate_number.strip():
            raise ValueError("Invalid certificate_number")

        if issue_date is None:
            issue_date = timezone.now()

        # Create hash input with salt for security
        salt = getattr(settings, 'SECRET_KEY', 'default-salt')[:16]
        hash_components = [
            certificate_number.strip(),
            salt,
            str(issue_date.isoformat()),
        ]

        if enrollment_id is not None:
            hash_components.append(str(enrollment_id))

        hash_input = "-".join(hash_components)
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    except Exception as e:
        logger.error(f"Error generating verification hash: {e}")
        # Fallback to simple hash
        return hashlib.sha256(f"{certificate_number}-{timezone.now()}".encode()).hexdigest()


def generate_unique_identifier(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique identifier with enhanced validation
    FIXED: Input validation and collision prevention
    """
    try:
        # Validate inputs
        if not isinstance(prefix, str):
            prefix = ""
        if not isinstance(length, int) or length < 4 or length > 32:
            length = 8

        # Sanitize prefix
        prefix = re.sub(r'[^a-zA-Z0-9_-]', '', prefix)[:10]

        unique_part = str(uuid.uuid4()).replace('-', '')[:length]
        return f"{prefix}{unique_part}" if prefix else unique_part

    except Exception as e:
        logger.error(f"Error generating unique identifier: {e}")
        return str(uuid.uuid4()).replace('-', '')[:length]


# =====================================
# ENHANCED PROGRESS AND ANALYTICS
# =====================================

def calculate_completion_percentage(completed_items: int, total_items: int) -> int:
    """
    Calculate completion percentage with enhanced validation
    FIXED: Division by zero and input validation
    """
    try:
        # Validate inputs
        if not isinstance(completed_items, int) or not isinstance(total_items, int):
            completed_items = int(completed_items)
            total_items = int(total_items)

        if total_items <= 0:
            return 0

        if completed_items <= 0:
            return 0

        if completed_items >= total_items:
            return 100

        return min(100, max(0, int((completed_items / total_items) * 100)))

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"Error calculating completion percentage: {e}")
        return 0


def calculate_course_duration(course) -> int:
    """
    Calculate total course duration with optimized queries and caching
    FIXED: N+1 query problem and performance optimization
    """
    if not course:
        return 0

    cache_key = f"course_duration:{course.id}"
    cached_duration = cache.get(cache_key)
    if cached_duration is not None:
        return cached_duration

    try:
        # Optimized query with aggregation
        total_duration = course.modules.aggregate(
            total=Sum('lessons__duration_minutes')
        )['total'] or 0

        # Cache the result
        cache.set(cache_key, total_duration, COURSE_STATS_CACHE_TIMEOUT)
        return total_duration

    except Exception as e:
        logger.error(f"Error calculating course duration for course {course.id}: {e}")
        return 0


def calculate_course_progress(enrollment) -> float:
    """
    Calculate course progress with optimized queries and caching
    FIXED: Performance optimization and error handling
    """
    if not enrollment:
        return 0.0

    cache_key = f"course_progress:{enrollment.id}"
    cached_progress = cache.get(cache_key)
    if cached_progress is not None:
        return cached_progress

    try:
        # Optimized query using aggregation
        lesson_stats = enrollment.course.modules.aggregate(
            total_lessons=Count('lessons'),
            completed_lessons=Count(
                'lessons__progress',
                filter=Q(
                    lessons__progress__enrollment=enrollment,
                    lessons__progress__is_completed=True
                )
            )
        )

        total_lessons = lesson_stats['total_lessons'] or 0
        completed_lessons = lesson_stats['completed_lessons'] or 0

        if total_lessons == 0:
            progress = 0.0
        else:
            progress = round((completed_lessons / total_lessons) * 100, 2)

        # Cache the result
        cache.set(cache_key, progress, COURSE_STATS_CACHE_TIMEOUT)
        return progress

    except Exception as e:
        logger.error(f"Error calculating progress for enrollment {enrollment.id}: {e}")
        return 0.0


@transaction.atomic
def update_course_analytics(course):
    """
    Update course analytics with atomic operations and optimized queries
    FIXED: Race conditions and performance optimization
    """
    if not course:
        return

    try:
        # Use select_for_update to prevent race conditions
        course = course.__class__.objects.select_for_update().get(pk=course.pk)

        # Optimized aggregation queries
        enrollment_stats = course.enrollments.aggregate(
            active_count=Count('id', filter=Q(status='active')),
            total_count=Count('id')
        )

        review_stats = course.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        # Update fields
        course.enrolled_students_count = enrollment_stats['active_count'] or 0
        course.avg_rating = review_stats['avg_rating'] or Decimal('0.00')
        course.total_reviews = review_stats['total_reviews'] or 0

        # Update last enrollment date
        latest_enrollment = course.enrollments.order_by('-created_date').first()
        if latest_enrollment:
            course.last_enrollment_date = latest_enrollment.created_date

        # Update course duration
        course.duration_minutes = calculate_course_duration(course)

        # Save with specific fields to avoid conflicts
        course.save(update_fields=[
            'enrolled_students_count',
            'avg_rating',
            'total_reviews',
            'last_enrollment_date',
            'duration_minutes'
        ])

        # Clear related caches
        cache.delete(f"course_duration:{course.id}")
        cache.delete(f"course_stats:{course.id}")

        logger.debug(f"Updated analytics for course {course.id}")

    except Exception as e:
        logger.error(f"Error updating course analytics for course {course.id}: {e}")


def generate_unique_slug(title: str, model_class, max_length: int = 50,
                        slug_field: str = 'slug', instance=None) -> str:
    """
    Generate a unique slug with atomic operations and collision prevention.

    Args:
        title: The string to create a slug from
        model_class: The model class to check for slug uniqueness
        max_length: Maximum length for the slug
        slug_field: The field name for the slug in the model
        instance: Optional instance to exclude from uniqueness check

    Returns:
        A unique slug string for the given model class

    FIXED: Race conditions in slug generation
    """
    try:
        # Validate inputs
        if not isinstance(title, str) or not title.strip():
            title = "untitled"
        if not isinstance(max_length, int) or max_length < 10:
            max_length = 50

        # Sanitize title
        title = re.sub(r'[^\w\s-]', '', title.strip())
        base_slug = slugify(title)[:max_length-10]  # Reserve space for counter

        if not base_slug:
            base_slug = "item"

        slug = base_slug
        counter = 1

        # Use atomic operations to prevent race conditions
        while True:
            try:
                with transaction.atomic():
                    filter_kwargs = {slug_field: slug}
                    if instance and getattr(instance, 'pk', None):
                        queryset = model_class.objects.exclude(pk=instance.pk)
                    else:
                        queryset = model_class.objects.all()

                    # Use select_for_update to prevent races
                    exists = queryset.select_for_update().filter(**filter_kwargs).exists()

                    if not exists:
                        return slug

                    # Generate next candidate
                    suffix = f"-{counter}"
                    available_length = max_length - len(suffix)
                    slug = f"{base_slug[:available_length]}{suffix}"
                    counter += 1

                    # Prevent infinite loop
                    if counter > 1000:
                        random_suffix = uuid.uuid4().hex[:8]
                        available_length = max_length - len(random_suffix) - 1
                        slug = f"{base_slug[:available_length]}-{random_suffix}"
                        logger.warning(f"High slug collision count, using UUID: {slug}")
                        return slug

            except IntegrityError:
                # Another process created the same slug, try next
                counter += 1
                if counter > 1000:
                    random_suffix = uuid.uuid4().hex[:8]
                    available_length = max_length - len(random_suffix) - 1
                    slug = f"{base_slug[:available_length]}-{random_suffix}"
                    logger.warning(f"IntegrityError in slug generation, using UUID: {slug}")
                    return slug
                continue

    except Exception as e:
        logger.error(f"Error generating unique slug: {e}")
        return f"item-{uuid.uuid4().hex[:8]}"


# =====================================
# ENHANCED HTML AND CONTENT UTILITIES
# =====================================

def clean_html_content(content: str) -> str:
    """
    Clean and sanitize HTML content with enhanced security
    FIXED: XSS prevention and comprehensive sanitization
    """
    if not isinstance(content, str) or not content:
        return ""

    try:
        # Remove dangerous patterns
        cleaned_content = content
        for pattern in COMPILED_DANGEROUS_PATTERNS:
            cleaned_content = pattern.sub('', cleaned_content)

        # Remove dangerous attributes
        dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
        for attr in dangerous_attrs:
            cleaned_content = re.sub(
                f'{attr}\s*=\s*["\'][^"\']*["\']',
                '',
                cleaned_content,
                flags=re.IGNORECASE
            )

        # Clean up excessive whitespace
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
        cleaned_content = cleaned_content.strip()

        # Limit content length to prevent DoS
        max_content_length = getattr(settings, 'MAX_CONTENT_LENGTH', 50000)
        if len(cleaned_content) > max_content_length:
            cleaned_content = cleaned_content[:max_content_length] + "..."

        return cleaned_content

    except Exception as e:
        logger.error(f"Error cleaning HTML content: {e}")
        return ""


def extract_text_from_html(html_content: str) -> str:
    """
    Extract plain text from HTML content with enhanced validation
    FIXED: Input validation and security
    """
    if not isinstance(html_content, str) or not html_content:
        return ""

    try:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)

        # Decode HTML entities
        text = html.unescape(text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Limit length
        if len(text) > 10000:
            text = text[:10000]

        return text

    except Exception as e:
        logger.error(f"Error extracting text from HTML: {e}")
        return ""


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time with enhanced validation
    FIXED: Input validation and calculation accuracy
    """
    try:
        if not isinstance(text, str) or not text:
            return 0

        # Validate words per minute
        if not isinstance(words_per_minute, int) or words_per_minute <= 0:
            words_per_minute = 200

        # Extract plain text if HTML
        plain_text = extract_text_from_html(text)

        if not plain_text:
            return 0

        # Count words more accurately
        words = re.findall(r'\b\w+\b', plain_text)
        word_count = len(words)

        if word_count == 0:
            return 0

        # Calculate reading time
        reading_time = word_count / words_per_minute

        # Round up to nearest minute, minimum 1 minute for substantial content
        return max(1, int(reading_time + 0.5)) if word_count > 50 else 1

    except Exception as e:
        logger.error(f"Error calculating reading time: {e}")
        return 1


# =====================================
# ENHANCED FILE AND VALIDATION UTILITIES
# =====================================

def get_file_extension(filename: str) -> str:
    """
    Get file extension with enhanced validation and security
    FIXED: Input validation and security checks
    """
    try:
        if not isinstance(filename, str) or not filename:
            return ""

        # Remove path components for security
        filename = os.path.basename(filename)

        # Limit filename length
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[-MAX_FILENAME_LENGTH:]

        # Get extension
        if '.' not in filename:
            return ""

        extension = filename.split('.')[-1].lower()

        # Validate extension (alphanumeric only)
        if not re.match(r'^[a-z0-9]+$', extension):
            return ""

        return extension

    except Exception as e:
        logger.warning(f"Error getting file extension: {e}")
        return ""


def is_video_file(filename: str) -> bool:
    """
    Check if file is a video file with enhanced validation
    FIXED: Security validation and extension checking
    """
    try:
        extension = get_file_extension(filename)
        return extension in ALLOWED_VIDEO_EXTENSIONS
    except Exception:
        return False


def is_image_file(filename: str) -> bool:
    """
    Check if file is an image file with enhanced validation
    FIXED: Security validation and extension checking
    """
    try:
        extension = get_file_extension(filename)
        return extension in ALLOWED_IMAGE_EXTENSIONS
    except Exception:
        return False


def is_document_file(filename: str) -> bool:
    """
    Check if file is a document file with validation
    ADDED: Document file validation
    """
    try:
        extension = get_file_extension(filename)
        return extension in ALLOWED_DOCUMENT_EXTENSIONS
    except Exception:
        return False


def validate_file_security(filename: str, max_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Comprehensive file security validation
    ADDED: File security validation
    """
    result = {
        'is_valid': False,
        'errors': [],
        'warnings': [],
        'file_type': 'unknown'
    }

    try:
        if not isinstance(filename, str) or not filename:
            result['errors'].append("Invalid filename")
            return result

        # Check filename length
        if len(filename) > MAX_FILENAME_LENGTH:
            result['errors'].append(f"Filename too long (max {MAX_FILENAME_LENGTH} characters)")
            return result

        # Check for dangerous characters
        if re.search(r'[<>:"|?*\x00-\x1f]', filename):
            result['errors'].append("Filename contains dangerous characters")
            return result

        # Get extension
        extension = get_file_extension(filename)
        if not extension:
            result['errors'].append("File must have a valid extension")
            return result

        # Determine file type
        if is_image_file(filename):
            result['file_type'] = 'image'
        elif is_video_file(filename):
            result['file_type'] = 'video'
        elif is_document_file(filename):
            result['file_type'] = 'document'
        else:
            result['errors'].append(f"File type '{extension}' is not allowed")
            return result

        # File passed all checks
        result['is_valid'] = True

    except Exception as e:
        logger.error(f"Error validating file security: {e}")
        result['errors'].append("File validation failed")

    return result


def validate_json_field(value: Any, field_name: str, max_items: Optional[int] = None,
                       min_str_length: Optional[int] = None) -> None:
    """
    Validate JSON field structure with enhanced validation
    FIXED: Input validation and security
    """
    try:
        if not isinstance(value, list):
            raise ValidationError(f'{field_name} must be a list.')

        if max_items and len(value) > max_items:
            raise ValidationError(f'{field_name} cannot have more than {max_items} items.')

        if min_str_length:
            for i, item in enumerate(value):
                if not isinstance(item, str):
                    raise ValidationError(f'{field_name}[{i}] must be a string.')

                item_stripped = item.strip()
                if len(item_stripped) < min_str_length:
                    raise ValidationError(
                        f'Each {field_name.lower()} item must be at least {min_str_length} characters long.'
                    )

                # Check for dangerous content
                if any(pattern.search(item) for pattern in COMPILED_DANGEROUS_PATTERNS):
                    raise ValidationError(f'{field_name}[{i}] contains dangerous content.')

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error validating JSON field {field_name}: {e}")
        raise ValidationError(f'Validation failed for {field_name}.')


# =====================================
# ENHANCED UPLOAD PATH GENERATORS
# =====================================

def upload_course_thumbnail(instance, filename: str) -> str:
    """
    Generate secure upload path for course thumbnails
    FIXED: Path injection prevention and security
    """
    try:
        # Validate file
        security_result = validate_file_security(filename)
        if not security_result['is_valid'] or security_result['file_type'] != 'image':
            filename = "default.jpg"

        ext = get_file_extension(filename)
        new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}.jpg"

        course_id = getattr(instance, 'id', 'new')
        return f"course_thumbnails/{course_id}/{new_filename}"

    except Exception as e:
        logger.error(f"Error generating thumbnail upload path: {e}")
        return f"course_thumbnails/error/{uuid.uuid4().hex}.jpg"


def upload_lesson_resource(instance, filename: str) -> str:
    """
    Generate secure upload path for lesson resources
    FIXED: Path injection prevention and security
    """
    try:
        # Validate file
        security_result = validate_file_security(filename)
        if not security_result['is_valid']:
            filename = "resource.txt"

        ext = get_file_extension(filename)
        new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}.bin"

        lesson_id = getattr(instance.lesson, 'id', 'new') if hasattr(instance, 'lesson') else 'new'
        return f"lesson_resources/{lesson_id}/{new_filename}"

    except Exception as e:
        logger.error(f"Error generating resource upload path: {e}")
        return f"lesson_resources/error/{uuid.uuid4().hex}.bin"


# =====================================
# ENHANCED COURSE MANAGEMENT UTILITIES
# =====================================

def get_course_stats(course) -> Dict[str, Any]:
    """
    Get comprehensive course statistics with caching and optimization
    FIXED: Performance optimization and error handling
    """
    if not course:
        return {}

    cache_key = f"course_stats:{course.id}"
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return cached_stats

    try:
        # Optimized aggregation queries
        module_stats = course.modules.aggregate(
            total_modules=Count('id'),
            total_lessons=Count('lessons'),
            total_assessments=Count('lessons__assessment')
        )

        enrollment_stats = course.enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed'))
        )

        stats = {
            'total_modules': module_stats['total_modules'] or 0,
            'total_lessons': module_stats['total_lessons'] or 0,
            'total_assessments': module_stats['total_assessments'] or 0,
            'total_enrollments': enrollment_stats['total_enrollments'] or 0,
            'active_enrollments': enrollment_stats['active_enrollments'] or 0,
            'completed_enrollments': enrollment_stats['completed_enrollments'] or 0,
            'average_rating': float(course.avg_rating) if course.avg_rating else 0.0,
            'total_reviews': course.total_reviews or 0,
            'duration_minutes': course.duration_minutes or 0,
            'duration_formatted': format_duration(course.duration_minutes),
        }

        # Calculate completion rate
        if stats['total_enrollments'] > 0:
            stats['completion_rate'] = round(
                (stats['completed_enrollments'] / stats['total_enrollments']) * 100, 2
            )
        else:
            stats['completion_rate'] = 0.0

        # Cache the results
        cache.set(cache_key, stats, COURSE_STATS_CACHE_TIMEOUT)
        return stats

    except Exception as e:
        logger.error(f"Error calculating course stats for course {course.id}: {e}")
        return {'error': str(e)}


def get_user_course_progress(user, course) -> Dict[str, Any]:
    """
    Get detailed progress information with optimized queries
    FIXED: N+1 queries and performance optimization
    """
    try:
        if not user or not course:
            return {'enrolled': False}

        # Optimized enrollment query
        enrollment = course.enrollments.select_related('course').prefetch_related(
            Prefetch('progress', queryset=course.progress.select_related('lesson__module'))
        ).filter(user=user).first()

        if not enrollment:
            return {'enrolled': False}

        progress_data = {
            'enrolled': True,
            'enrollment_date': enrollment.created_date,
            'status': enrollment.status,
            'progress_percentage': enrollment.progress_percentage or 0,
            'total_time_spent': enrollment.total_time_spent or 0,
            'total_time_formatted': format_time_spent(enrollment.total_time_spent or 0),
            'last_accessed': enrollment.last_accessed,
            'completion_date': enrollment.completion_date,
            'has_certificate': hasattr(enrollment, 'certificate'),
        }

        # Get progress statistics
        progress_records = enrollment.progress.all()
        progress_data['completed_lessons'] = sum(1 for p in progress_records if p.is_completed)
        progress_data['total_lessons'] = len(progress_records)

        # Get last accessed lesson
        last_progress = progress_records.order_by('-last_accessed').first()
        if last_progress:
            progress_data['last_lesson'] = {
                'id': last_progress.lesson.id,
                'title': last_progress.lesson.title,
                'module': last_progress.lesson.module.title,
                'url': f"/courses/{course.slug}/lessons/{last_progress.lesson.id}/"
            }

        return progress_data

    except Exception as e:
        logger.error(f"Error getting user course progress: {e}")
        return {'enrolled': False, 'error': str(e)}


def check_lesson_access(user, lesson, request=None) -> Dict[str, Any]:
    """
    Check lesson access with consolidated access control logic
    FIXED: Access control logic duplication
    """
    try:
        # Use consolidated access level logic
        from ..validation import get_unified_user_access_level, can_user_access_content

        user_access_level = get_unified_user_access_level(user)
        lesson_access_level = getattr(lesson, 'access_level', 'registered')

        # Check basic access
        has_access = can_user_access_content(user_access_level, lesson_access_level)

        # Check enrollment
        is_enrolled = False
        if user and user.is_authenticated:
            is_enrolled = lesson.module.course.enrollments.filter(
                user=user,
                status='active'
            ).exists()

        # Free preview override
        if getattr(lesson, 'is_free_preview', False):
            has_access = True

        return {
            'has_access': has_access,
            'is_enrolled': is_enrolled,
            'user_access_level': user_access_level,
            'required_access_level': lesson_access_level,
            'is_free_preview': getattr(lesson, 'is_free_preview', False),
            'access_message': None if has_access else get_restricted_content_message(
                lesson.title, user_access_level
            )
        }

    except Exception as e:
        logger.error(f"Error checking lesson access: {e}")
        return {
            'has_access': False,
            'is_enrolled': False,
            'user_access_level': 'guest',
            'required_access_level': 'registered',
            'is_free_preview': False,
            'access_message': "Access check failed",
            'error': str(e)
        }


def clear_course_caches(course_id: int):
    """
    Clear all course-related caches
    ADDED: Cache management utility
    """
    try:
        cache_keys = [
            f"course_duration:{course_id}",
            f"course_stats:{course_id}",
            f"course_analytics:{course_id}",
        ]
        cache.delete_many(cache_keys)
        logger.debug(f"Cleared caches for course {course_id}")
    except Exception as e:
        logger.error(f"Error clearing course caches: {e}")
