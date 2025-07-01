#
# File Path: instructor_portal/models/utils.py
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
# Shared utilities, validators, and TierManager for instructor_portal models
# Split from original models.py maintaining exact code compatibility

import logging
import os
import hashlib
from decimal import Decimal
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

logger = logging.getLogger(__name__)

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
    def get_tier_limits(tier: str) -> dict:
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


def get_course_model():
    """Get Course model to avoid circular imports"""
    from django.apps import apps
    return apps.get_model('courses', 'Course')


def get_category_model():
    """Get Category model to avoid circular imports"""
    from django.apps import apps
    return apps.get_model('courses', 'Category')


def get_enrollment_model():
    """Get Enrollment model to avoid circular imports"""
    from django.apps import apps
    return apps.get_model('courses', 'Enrollment')


def get_review_model():
    """Get Review model to avoid circular imports"""
    from django.apps import apps
    return apps.get_model('courses', 'Review')
