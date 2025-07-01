# File Path: backend/courses/utils/core.py
# Folder Path: backend/courses/utils/
# Date Created: 2025-06-30 17:33:14
# Date Revised: 2025-07-01 08:46:12
# Current Date and Time (UTC): 2025-07-01 08:46:12
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-01 08:46:12 UTC
# User: cadsanthanamNew
# Version: 6.0.0
#
# Production-Ready Core Utility Functions - COMPLETE REFACTORING
#
# Version 6.0.0 Changes:
# - REFACTORED: Complete redesign of utility organization
# - REMOVED: All deprecated and redundant functions
# - OPTIMIZED: Database operations and query performance
# - ENHANCED: Security hardening and validation
# - IMPROVED: Exception handling and logging
# - CONSOLIDATED: Related functionality into logical groups

import hashlib
import uuid
import re
import logging
import time
import random
from datetime import timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal

from django.utils import timezone
from django.utils.text import slugify
from django.core.cache import cache
from django.db.models import Count, Avg, Q, Sum, Prefetch, Coalesce, Value
from django.db import transaction, IntegrityError, DatabaseError, OperationalError
from django.conf import settings

# Import specialized utility modules
from .validation import get_unified_user_access_level, can_user_access_content
from .formatting import format_duration, format_filesize, format_time_spent, format_price
from .html_utils import clean_html_content, extract_text_from_html, calculate_reading_time
from .file_utils import (validate_file_security, get_file_extension,
                        is_image_file, is_video_file, is_document_file)

logger = logging.getLogger(__name__)

# Cache timeouts for performance optimization
COURSE_STATS_CACHE_TIMEOUT = 300  # 5 minutes
ANALYTICS_CACHE_TIMEOUT = 600    # 10 minutes
SLUG_CACHE_TIMEOUT = 1800       # 30 minutes

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
# CONTENT ACCESS UTILITIES
# =====================================

def get_restricted_content_message(title: str, access_level: str) -> str:
    """
    Get appropriate message for restricted content with enhanced security

    Args:
        title: The title of the content being restricted
        access_level: The current user's access level

    Returns:
        Formatted HTML message for restricted content
    """
    try:
        # Sanitize title input
        if not isinstance(title, str):
            title = "Content"

        # Remove dangerous characters and limit length
        title = re.sub(r'[<>"\']', '', title)[:100]

        if access_level == 'guest':
            return DEFAULT_REGISTERED_CONTENT_MESSAGE.format(title=title)
        else:
            return DEFAULT_PREMIUM_CONTENT_MESSAGE.format(title=title)
    except (TypeError, AttributeError) as e:
        logger.warning(f"Error generating restricted content message: {e}")
        return DEFAULT_REGISTERED_CONTENT_MESSAGE.format(title="Content")


# =====================================
# ENHANCED SLUG GENERATION
# =====================================

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
        max_retries = 1000  # Hard limit to prevent infinite loops

        # Use atomic operations with exponential backoff to prevent race conditions
        while counter <= max_retries:
            try:
                with transaction.atomic(using='default'):
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

            except IntegrityError:
                # Exponential backoff for race condition handling
                backoff_time = min(0.1 * (2 ** min(counter // 100, 5)), 1.0)  # Max 1 second backoff
                time.sleep(backoff_time + random.uniform(0, 0.1))  # Add jitter
                counter += 1
                continue
            except (DatabaseError, OperationalError) as e:
                logger.warning(f"Database error in slug generation attempt {counter}: {e}")
                time.sleep(0.1 * counter)  # Simple backoff
                counter += 1
                continue

        # Hard limit reached, use UUID fallback
        random_suffix = uuid.uuid4().hex[:8]
        available_length = max_length - len(random_suffix) - 1
        final_slug = f"{base_slug[:available_length]}-{random_suffix}"
        logger.warning(f"Slug generation reached max retries ({max_retries}), using UUID fallback: {final_slug}")
        return final_slug

    except (TypeError, AttributeError) as e:
        logger.error(f"Error generating unique slug: {e}")
        return f"item-{uuid.uuid4().hex[:8]}"


# =====================================
# COURSE STATISTICS AND ANALYTICS
# =====================================

def calculate_completion_percentage(completed_items: int, total_items: int) -> int:
    """
    Calculate completion percentage with enhanced validation

    Args:
        completed_items: Number of completed items
        total_items: Total number of items

    Returns:
        Integer percentage from 0-100
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

    Args:
        course: Course object to calculate duration for

    Returns:
        Total duration in minutes
    """
    if not course:
        return 0

    cache_key = f"course_duration:{course.id}"
    cached_duration = cache.get(cache_key)
    if cached_duration is not None:
        return cached_duration

    try:
        # Use Coalesce to handle NULL duration_minutes values
        total_duration = course.modules.aggregate(
            total=Sum(Coalesce('lessons__duration_minutes', Value(0)))
        )['total'] or 0

        # Cache the result
        cache.set(cache_key, total_duration, COURSE_STATS_CACHE_TIMEOUT)
        return total_duration

    except (DatabaseError, OperationalError) as e:
        logger.error(f"Database error calculating course duration for course {course.id}: {e}")
        return 0
    except AttributeError as e:
        logger.error(f"Attribute error calculating course duration for course {course.id}: {e}")
        return 0


def calculate_course_progress(enrollment) -> float:
    """
    Calculate course progress with optimized queries and caching

    Args:
        enrollment: Enrollment object to calculate progress for

    Returns:
        Progress as a percentage (0-100)
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

    except (DatabaseError, OperationalError) as e:
        logger.error(f"Database error calculating progress for enrollment {enrollment.id}: {e}")
        return 0.0
    except AttributeError as e:
        logger.error(f"Attribute error calculating progress for enrollment {enrollment.id}: {e}")
        return 0.0


@transaction.atomic
def update_course_analytics(course):
    """
    Update course analytics with atomic operations and optimized queries

    Args:
        course: Course object to update analytics for
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
        clear_course_caches(course.id)

        logger.debug(f"Updated analytics for course {course.id}")

    except (DatabaseError, OperationalError) as e:
        logger.error(f"Database error updating course analytics for course {course.id}: {e}")
        raise
    except AttributeError as e:
        logger.error(f"Attribute error updating course analytics for course {course.id}: {e}")


def get_course_stats(course) -> Dict[str, Any]:
    """
    Get comprehensive course statistics with caching and optimization

    Args:
        course: Course object to get statistics for

    Returns:
        Dictionary with course statistics
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

    except (DatabaseError, OperationalError) as e:
        logger.error(f"Database error calculating course stats for course {course.id}: {e}")
        return {'error': str(e)}
    except AttributeError as e:
        logger.error(f"Attribute error calculating course stats for course {course.id}: {e}")
        return {'error': str(e)}


def get_user_course_progress(user, course) -> Dict[str, Any]:
    """
    Get detailed progress information with optimized queries

    Args:
        user: User object to get progress for
        course: Course object to get progress for

    Returns:
        Dictionary with progress information
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
        progress_data['total_lessons'] = course.modules.aggregate(
            total_lessons=Count('lessons')
        )['total_lessons'] or 0

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

    except (DatabaseError, OperationalError, AttributeError) as e:
        logger.error(f"Error getting user course progress: {e}")
        return {'enrolled': False, 'error': str(e)}


def check_lesson_access(user, lesson, request=None) -> Dict[str, Any]:
    """
    Check lesson access with consolidated access control logic

    Args:
        user: User object to check access for
        lesson: Lesson object to check access for
        request: Optional request object

    Returns:
        Dictionary with access information
    """
    try:
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

    except ImportError as e:
        logger.error(f"Import error checking lesson access: {e}")
        return {
            'has_access': False,
            'is_enrolled': False,
            'user_access_level': 'guest',
            'required_access_level': 'registered',
            'is_free_preview': False,
            'access_message': "Access check failed",
            'error': str(e)
        }
    except (DatabaseError, OperationalError, AttributeError) as e:
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

    Args:
        course_id: ID of the course to clear caches for
    """
    try:
        cache_keys = [
            f"course_duration:{course_id}",
            f"course_stats:{course_id}",
            f"course_analytics:{course_id}",
        ]
        cache.delete_many(cache_keys)
        logger.debug(f"Cleared caches for course {course_id}")
    except (TypeError, AttributeError) as e:
        logger.error(f"Error clearing course caches: {e}")


# =====================================
# UPLOAD PATH GENERATORS
# =====================================

def upload_course_thumbnail(instance, filename: str) -> str:
    """
    Generate secure upload path for course thumbnails

    Args:
        instance: Course instance for the thumbnail
        filename: Original filename

    Returns:
        Secure path for the uploaded file
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

    except (TypeError, AttributeError) as e:
        logger.error(f"Error generating thumbnail upload path: {e}")
        return f"course_thumbnails/error/{uuid.uuid4().hex}.jpg"


def upload_lesson_resource(instance, filename: str) -> str:
    """
    Generate secure upload path for lesson resources

    Args:
        instance: Resource instance
        filename: Original filename

    Returns:
        Secure path for the uploaded file
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

    except (TypeError, AttributeError) as e:
        logger.error(f"Error generating resource upload path: {e}")
        return f"lesson_resources/error/{uuid.uuid4().hex}.bin"


# Export only non-deprecated functions for backward compatibility
__all__ = [
    # Course statistics and analytics
    'calculate_course_duration',
    'calculate_course_progress',
    'calculate_completion_percentage',
    'update_course_analytics',
    'get_course_stats',
    'get_user_course_progress',

    # Access control
    'check_lesson_access',
    'get_restricted_content_message',

    # Slug generation
    'generate_unique_slug',

    # Cache management
    'clear_course_caches',

    # Upload paths
    'upload_course_thumbnail',
    'upload_lesson_resource',
]
