#
# File Path: backend/courses/utils/__init__.py
# Folder Path: backend/courses/utils/
# Date Created: 2025-06-27 10:27:34
# Date Revised: 2025-07-01 04:41:11
# Current Date and Time (UTC): 2025-07-01 04:41:11
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-01 04:41:11 UTC
# User: cadsanthanamNew
# Version: 5.1.0
#
# Re-export utility functions for backward compatibility - AUDIT FIXES IMPLEMENTED
#
# Version 5.1.0 Changes - CRITICAL AUDIT FIXES:
# - FIXED 🔴: Enhanced exports with proper error handling
# - FIXED 🟡: Added missing constraint and validation helpers
# - ENHANCED: Comprehensive function availability checking
# - MAINTAINED: 100% backward compatibility with existing imports

# Re-export all utility functions from core module
from .core import (
    # Formatting utilities
    format_duration, format_filesize, format_time_spent, format_price,

    # Access control
    get_user_access_level, get_restricted_content_message,

    # Certificate utilities
    generate_certificate_number, generate_verification_hash, generate_unique_identifier,

    # Progress and analytics utilities
    calculate_completion_percentage, calculate_course_duration, calculate_course_progress,
    update_course_analytics, generate_unique_slug,

    # HTML and content utilities
    clean_html_content, extract_text_from_html, calculate_reading_time,

    # File and validation utilities
    get_file_extension, is_video_file, is_image_file, is_document_file,
    validate_file_security, validate_json_field,

    # Upload path generators
    upload_course_thumbnail, upload_lesson_resource,

    # Course management utilities
    get_course_stats, get_user_course_progress, check_lesson_access,
    clear_course_caches,

    # Constants
    COURSE_STATS_CACHE_TIMEOUT, ANALYTICS_CACHE_TIMEOUT, SLUG_CACHE_TIMEOUT,
    MAX_FILENAME_LENGTH, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS
)

# Re-export model utility functions from model_helpers module
from .model_helpers import (
    # Core field creation helpers
    create_meta_indexes, create_char_field, create_text_field,
    create_json_field, create_foreign_key, create_decimal_field,

    # ENHANCED: New constraint and index helpers
    create_check_constraint, create_unique_constraint, create_index,

    # Validation helpers
    validate_model_field_params
)

# Re-export validation functions from main validation module for backward compatibility
try:
    from ..validation import (
        get_unified_user_access_level as get_unified_access_level,
        can_user_access_content,
        validate_course_data,
        validate_lesson_data,
        sanitize_input,
        validate_content_security
    )
    _VALIDATION_AVAILABLE = True
except ImportError:
    # Graceful fallback if validation module is not available
    _VALIDATION_AVAILABLE = False
    get_unified_access_level = None
    can_user_access_content = None
    validate_course_data = None
    validate_lesson_data = None
    sanitize_input = None
    validate_content_security = None

# Define all export symbols for "from courses.utils import *"
__all__ = [
    # Formatting utilities
    'format_duration', 'format_filesize', 'format_time_spent', 'format_price',

    # Access control
    'get_user_access_level', 'get_restricted_content_message',

    # Certificate utilities
    'generate_certificate_number', 'generate_verification_hash', 'generate_unique_identifier',

    # Progress and analytics utilities
    'calculate_completion_percentage', 'calculate_course_duration', 'calculate_course_progress',
    'update_course_analytics', 'generate_unique_slug',

    # HTML and content utilities
    'clean_html_content', 'extract_text_from_html', 'calculate_reading_time',

    # File and validation utilities
    'get_file_extension', 'is_video_file', 'is_image_file', 'is_document_file',
    'validate_file_security', 'validate_json_field',

    # Upload path generators
    'upload_course_thumbnail', 'upload_lesson_resource',

    # Course management utilities
    'get_course_stats', 'get_user_course_progress', 'check_lesson_access',
    'clear_course_caches',

    # Model utility functions
    'create_meta_indexes', 'create_char_field', 'create_text_field',
    'create_json_field', 'create_foreign_key', 'create_decimal_field',

    # ENHANCED: New constraint and index helpers
    'create_check_constraint', 'create_unique_constraint', 'create_index',

    # Validation helpers
    'validate_model_field_params',

    # Constants
    'COURSE_STATS_CACHE_TIMEOUT', 'ANALYTICS_CACHE_TIMEOUT', 'SLUG_CACHE_TIMEOUT',
    'MAX_FILENAME_LENGTH', 'ALLOWED_IMAGE_EXTENSIONS', 'ALLOWED_VIDEO_EXTENSIONS',
    'ALLOWED_DOCUMENT_EXTENSIONS'
]

# ENHANCED: Add validation functions only if available
if _VALIDATION_AVAILABLE:
    __all__.extend([
        'get_unified_access_level', 'can_user_access_content',
        'validate_course_data', 'validate_lesson_data',
        'sanitize_input', 'validate_content_security'
    ])

# Version information for package
__version__ = '5.1.0'

# ENHANCED: Availability flags for optional modules
MODULE_AVAILABILITY = {
    'validation': _VALIDATION_AVAILABLE,
    'core_utils': True,
    'model_helpers': True,
}
