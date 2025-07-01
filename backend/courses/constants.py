#
# File Path: backend/courses/constants.py
# Folder Path: backend/courses/
# Date Created: 2025-06-15 06:41:03
# Date Revised: 2025-07-01 04:55:58
# Current Date and Time (UTC): 2025-07-01 04:55:58
# Current User's Login: cadsanthanamNew
# Author: sujibeautysalon
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-07-01 04:55:58 UTC
# User: cadsanthanamNew
# Version: 2.1.0
#
# Production-Ready Constants for Course Management System
#
# Version 2.1.0 Changes - CRITICAL AUDIT FIXES:
# - FIXED 🔴: Environment variable casting with proper validation (P0 Critical)
# - FIXED 🟡: Enhanced get_file_size_limit with comprehensive error handling
# - ENHANCED: All helper functions now use specific exception handling
# - MAINTAINED: 100% backward compatibility with all existing constants

import os
import logging
from decimal import Decimal, InvalidOperation
from enum import Enum, IntEnum
from typing import Dict, List, Tuple, Union, Final
from django.conf import settings

logger = logging.getLogger(__name__)

# =====================================
# TYPE-SAFE ENUMS - FIXED FOR PYTHON 3.13
# =====================================

class CourseLevel(Enum):
    """Type-safe course difficulty levels"""
    BEGINNER = ('beginner', 'Beginner')
    INTERMEDIATE = ('intermediate', 'Intermediate')
    ADVANCED = ('advanced', 'Advanced')
    ALL_LEVELS = ('all_levels', 'All Levels')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        """Get Django choices tuple"""
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        """Get all valid values"""
        return tuple(item.code for item in cls)


class CreationMethod(Enum):
    """Course creation methods with enhanced security"""
    BUILDER = ('builder', 'Drag & Drop Builder')
    WIZARD = ('wizard', 'Step-by-Step Wizard')
    AI_POWERED = ('ai', 'AI-Powered Builder')
    IMPORT = ('import', 'Imported Course')
    MANUAL = ('manual', 'Manual Creation')
    TEMPLATE = ('template', 'From Template')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(item.code for item in cls)


class CompletionStatus(Enum):
    """Course completion status with validation"""
    NOT_STARTED = ('not_started', 'Not Started')
    IN_PROGRESS = ('in_progress', 'In Progress')
    PARTIALLY_COMPLETE = ('partially_complete', 'Partially Complete')
    COMPLETE = ('complete', 'Complete')
    PUBLISHED = ('published', 'Published')
    ARCHIVED = ('archived', 'Archived')
    SUSPENDED = ('suspended', 'Suspended')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def active_statuses(cls) -> Tuple[str, ...]:
        """Get statuses that represent active courses"""
        return (cls.IN_PROGRESS.code, cls.PARTIALLY_COMPLETE.code, cls.PUBLISHED.code)

    @classmethod
    def completed_statuses(cls) -> Tuple[str, ...]:
        """Get statuses that represent completed courses"""
        return (cls.COMPLETE.code, cls.PUBLISHED.code)


class LessonType(Enum):
    """Lesson content types with validation"""
    VIDEO = ('video', 'Video')
    READING = ('reading', 'Reading')
    INTERACTIVE = ('interactive', 'Interactive')
    QUIZ = ('quiz', 'Quiz')
    LAB_EXERCISE = ('lab_exercise', 'Lab Exercise')
    ASSIGNMENT = ('assignment', 'Assignment')
    DISCUSSION = ('discussion', 'Discussion')
    LIVE_SESSION = ('live_session', 'Live Session')
    DOWNLOAD = ('download', 'Download')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def interactive_types(cls) -> Tuple[str, ...]:
        """Get types that require user interaction"""
        return (cls.INTERACTIVE.code, cls.QUIZ.code, cls.ASSIGNMENT.code, cls.DISCUSSION.code)


class AccessLevel(Enum):
    """Content access levels with security validation"""
    GUEST = ('guest', 'Guest - Unregistered Users')
    REGISTERED = ('registered', 'Registered - Logged In Users')
    PREMIUM = ('premium', 'Premium - Paid Subscribers')
    ENTERPRISE = ('enterprise', 'Enterprise - Corporate Users')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def hierarchy(cls) -> Dict[str, int]:
        """Access level hierarchy for comparison"""
        return {
            cls.GUEST.code: 0,
            cls.REGISTERED.code: 1,
            cls.PREMIUM.code: 2,
            cls.ENTERPRISE.code: 3
        }

    @classmethod
    def can_access(cls, user_level: str, required_level: str) -> bool:
        """Check if user level can access required level"""
        hierarchy = cls.hierarchy()
        return hierarchy.get(user_level, 0) >= hierarchy.get(required_level, 0)


class ResourceType(Enum):
    """Resource file types with security validation"""
    DOCUMENT = ('document', 'Document')
    VIDEO = ('video', 'Video')
    AUDIO = ('audio', 'Audio')
    IMAGE = ('image', 'Image')
    LINK = ('link', 'External Link')
    CODE_SAMPLE = ('code_sample', 'Code Sample')
    TOOL_SOFTWARE = ('tool_software', 'Tool/Software')
    DATASET = ('dataset', 'Dataset')
    TEMPLATE = ('template', 'Template')
    ARCHIVE = ('archive', 'Archive/Zip')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def downloadable_types(cls) -> Tuple[str, ...]:
        """Get types that can be downloaded"""
        return (cls.DOCUMENT.code, cls.VIDEO.code, cls.AUDIO.code,
                cls.IMAGE.code, cls.CODE_SAMPLE.code, cls.DATASET.code,
                cls.TEMPLATE.code, cls.ARCHIVE.code)


class QuestionType(Enum):
    """Assessment question types with validation"""
    MULTIPLE_CHOICE = ('multiple_choice', 'Multiple Choice')
    TRUE_FALSE = ('true_false', 'True/False')
    SHORT_ANSWER = ('short_answer', 'Short Answer')
    ESSAY = ('essay', 'Essay')
    MATCHING = ('matching', 'Matching')
    FILL_BLANK = ('fill_blank', 'Fill in the Blank')
    DRAG_DROP = ('drag_drop', 'Drag and Drop')
    ORDERING = ('ordering', 'Ordering')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def auto_gradable(cls) -> Tuple[str, ...]:
        """Get question types that can be auto-graded"""
        return (cls.MULTIPLE_CHOICE.code, cls.TRUE_FALSE.code,
                cls.MATCHING.code, cls.FILL_BLANK.code, cls.ORDERING.code)


class EnrollmentStatus(Enum):
    """Enrollment status with business logic"""
    ACTIVE = ('active', 'Active')
    COMPLETED = ('completed', 'Completed')
    DROPPED = ('dropped', 'Dropped')
    SUSPENDED = ('suspended', 'Suspended')
    UNENROLLED = ('unenrolled', 'Unenrolled')
    EXPIRED = ('expired', 'Expired')
    PENDING = ('pending', 'Pending')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((item.code, item.label) for item in cls)

    @classmethod
    def active_statuses(cls) -> Tuple[str, ...]:
        """Get statuses that represent active enrollments"""
        return (cls.ACTIVE.code, cls.PENDING.code)


class Priority(IntEnum):
    """Priority levels for various operations"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


# =====================================
# ENHANCED ENVIRONMENT HELPERS
# =====================================

def get_file_size_limit(file_type: str, default_mb: int) -> int:
    """
    Get file size limit from environment or default with comprehensive validation
    FIXED: Proper error handling and validation for environment variables
    """
    env_key = f"MAX_{file_type.upper()}_FILE_SIZE_MB"

    try:
        # Get the environment variable value
        env_value = os.environ.get(env_key)

        if env_value is None:
            # Environment variable not set, use default
            mb_limit = default_mb
        else:
            # Try to convert environment variable to integer
            try:
                mb_limit = int(env_value)
                # Validate the parsed value
                if mb_limit <= 0:
                    logger.warning(f"Invalid {env_key} value: {env_value} (must be positive). Using default: {default_mb}")
                    mb_limit = default_mb
                elif mb_limit > 10000:  # 10GB limit for sanity check
                    logger.warning(f"Excessive {env_key} value: {env_value}MB (max 10GB). Using default: {default_mb}")
                    mb_limit = default_mb
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid {env_key} environment variable: {env_value}. Error: {e}. Using default: {default_mb}")
                mb_limit = default_mb

        return mb_limit * 1024 * 1024  # Convert to bytes

    except Exception as e:
        logger.error(f"Unexpected error getting file size limit for {file_type}: {e}. Using default: {default_mb}")
        return default_mb * 1024 * 1024


def get_env_decimal(key: str, default: Union[str, Decimal]) -> Decimal:
    """Get decimal value from environment with enhanced validation"""
    try:
        env_value = os.environ.get(key)
        if env_value is None:
            return Decimal(str(default))

        # Clean the environment value
        cleaned_value = env_value.strip()
        if not cleaned_value:
            return Decimal(str(default))

        return Decimal(cleaned_value)
    except (ValueError, TypeError, InvalidOperation) as e:
        logger.warning(f"Invalid decimal environment variable {key}: {os.environ.get(key)}. Error: {e}. Using default: {default}")
        return Decimal(str(default))
    except Exception as e:
        logger.error(f"Unexpected error parsing decimal environment variable {key}: {e}. Using default: {default}")
        return Decimal(str(default))


def get_env_int(key: str, default: int) -> int:
    """Get integer value from environment with enhanced validation"""
    try:
        env_value = os.environ.get(key)
        if env_value is None:
            return default

        # Clean and validate the environment value
        cleaned_value = env_value.strip()
        if not cleaned_value:
            return default

        parsed_value = int(cleaned_value)

        # Basic sanity checks for common integer settings
        if key.endswith('_TIMEOUT') and parsed_value < 0:
            logger.warning(f"Negative timeout value for {key}: {parsed_value}. Using default: {default}")
            return default
        elif key.endswith('_SIZE') and parsed_value < 0:
            logger.warning(f"Negative size value for {key}: {parsed_value}. Using default: {default}")
            return default
        elif key.endswith('_LIMIT') and parsed_value <= 0:
            logger.warning(f"Non-positive limit value for {key}: {parsed_value}. Using default: {default}")
            return default

        return parsed_value
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid integer environment variable {key}: {os.environ.get(key)}. Error: {e}. Using default: {default}")
        return default
    except Exception as e:
        logger.error(f"Unexpected error parsing integer environment variable {key}: {e}. Using default: {default}")
        return default


def get_env_bool(key: str, default: bool) -> bool:
    """Get boolean value from environment with enhanced validation"""
    try:
        env_value = os.environ.get(key)
        if env_value is None:
            return default

        cleaned_value = env_value.strip().lower()
        if not cleaned_value:
            return default

        # Support common boolean representations
        true_values = {'true', '1', 'yes', 'on', 'enable', 'enabled'}
        false_values = {'false', '0', 'no', 'off', 'disable', 'disabled'}

        if cleaned_value in true_values:
            return True
        elif cleaned_value in false_values:
            return False
        else:
            logger.warning(f"Invalid boolean environment variable {key}: {env_value}. Using default: {default}")
            return default
    except Exception as e:
        logger.error(f"Unexpected error parsing boolean environment variable {key}: {e}. Using default: {default}")
        return default


# =====================================
# SECURITY AND VALIDATION CONSTANTS
# =====================================

# File size limits with environment-aware configuration
MAX_FILE_SIZE: Final[Dict[str, int]] = {
    'image': get_file_size_limit('image', 5),
    'video': get_file_size_limit('video', 100),
    'document': get_file_size_limit('document', 10),
    'audio': get_file_size_limit('audio', 50),
    'archive': get_file_size_limit('archive', 25),
    'code': get_file_size_limit('code', 1)
}

# Content length limits
MAX_CONTENT_LENGTH: Final[Dict[str, int]] = {
    'title': 200,
    'short_description': 500,
    'description': 5000,
    'content': 50000,
    'guest_content': 1000,
    'name': 100,
    'slug': 50,
    'tag': 30,
    'skill': 50,
    'requirement': 200,
    'objective': 300
}

# Business rule constraints
BUSINESS_CONSTRAINTS: Final[Dict[str, Union[int, float, Decimal]]] = {
    'min_course_price': Decimal('0.00'),
    'max_course_price': Decimal('10000.00'),
    'min_discount_percentage': 0,
    'max_discount_percentage': 100,
    'min_lesson_duration': 0,  # minutes
    'max_lesson_duration': 1440,  # 24 hours
    'min_modules_per_course': 1,
    'max_modules_per_course': 50,
    'min_lessons_per_module': 1,
    'max_lessons_per_module': 100,
    'max_resources_per_lesson': 20,
    'max_questions_per_assessment': 100,
    'min_passing_score': 1,
    'max_passing_score': 100,
    'max_attempts_per_assessment': 10,
    'max_time_limit_minutes': 480  # 8 hours
}

# Security patterns for content validation
DANGEROUS_CONTENT_PATTERNS: Final[List[str]] = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'vbscript:',
    r'data:text/html',
    r'<iframe[^>]*>',
    r'<object[^>]*>',
    r'<embed[^>]*>',
    r'<applet[^>]*>',
    r'onload\s*=',
    r'onerror\s*=',
    r'onclick\s*=',
    r'onmouseover\s*='
]

# Allowed file extensions by type
ALLOWED_EXTENSIONS: Final[Dict[str, Tuple[str, ...]]] = {
    'image': ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'),
    'video': ('mp4', 'webm', 'ogg', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'm4v'),
    'audio': ('mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma'),
    'document': ('pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'),
    'code': ('py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'go', 'rs', 'sql'),
    'archive': ('zip', 'tar', 'gz', 'rar', '7z')
}

# MIME type validation
ALLOWED_MIME_TYPES: Final[Dict[str, Tuple[str, ...]]] = {
    'image': (
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
        'image/svg+xml', 'image/webp', 'image/x-icon'
    ),
    'video': (
        'video/mp4', 'video/webm', 'video/ogg', 'video/avi',
        'video/quicktime', 'video/x-msvideo', 'video/x-flv'
    ),
    'audio': (
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac',
        'audio/flac', 'audio/mp4', 'audio/x-ms-wma'
    ),
    'document': (
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'application/rtf', 'application/vnd.oasis.opendocument.text'
    )
}

# =====================================
# CONFIGURATION CONSTANTS
# =====================================

# Pricing and financial constants
DEFAULT_COURSE_PRICE: Final[Decimal] = get_env_decimal('DEFAULT_COURSE_PRICE', '49.99')
DEFAULT_CURRENCY: Final[str] = os.environ.get('DEFAULT_CURRENCY', 'USD')
SUPPORTED_CURRENCIES: Final[Tuple[str, ...]] = ('USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY')

# Rating system
MIN_RATING: Final[int] = 1
MAX_RATING: Final[int] = 5
RATING_PRECISION: Final[int] = 1  # Decimal places

# Assessment defaults
DEFAULT_PASSING_SCORE: Final[int] = get_env_int('DEFAULT_PASSING_SCORE', 70)
DEFAULT_MAX_ATTEMPTS: Final[int] = get_env_int('DEFAULT_MAX_ATTEMPTS', 3)
DEFAULT_TIME_LIMIT: Final[int] = get_env_int('DEFAULT_TIME_LIMIT', 0)  # 0 = unlimited

# Pagination and limits
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
MAX_SEARCH_RESULTS: Final[int] = 1000
MAX_BULK_OPERATIONS: Final[int] = 100

# Cache timeouts (seconds)
CACHE_TIMEOUTS: Final[Dict[str, int]] = {
    'course_list': get_env_int('CACHE_COURSE_LIST_TIMEOUT', 300),      # 5 minutes
    'course_detail': get_env_int('CACHE_COURSE_DETAIL_TIMEOUT', 600),    # 10 minutes
    'user_permissions': get_env_int('CACHE_USER_PERMISSIONS_TIMEOUT', 180), # 3 minutes
    'analytics': get_env_int('CACHE_ANALYTICS_TIMEOUT', 900),        # 15 minutes
    'search_results': get_env_int('CACHE_SEARCH_RESULTS_TIMEOUT', 300),   # 5 minutes
    'static_content': get_env_int('CACHE_STATIC_CONTENT_TIMEOUT', 3600)   # 1 hour
}

# Rate limiting
RATE_LIMITS: Final[Dict[str, str]] = {
    'api_general': '1000/hour',
    'api_upload': '50/hour',
    'api_bulk': '10/hour',
    'search': '100/hour',
    'auth': '20/minute'
}

# Certificate configuration
CERTIFICATE_TEMPLATE_VERSIONS: Final[Tuple[Tuple[str, str], ...]] = (
    ('1.0', 'Version 1.0 - Classic'),
    ('1.1', 'Version 1.1 - Enhanced'),
    ('2.0', 'Version 2.0 - Modern'),
    ('2.1', 'Version 2.1 - Premium')
)

DEFAULT_CERTIFICATE_VERSION: Final[str] = '2.1'

# Content versioning
CONTENT_VERSION_LIMIT: Final[int] = get_env_int('CONTENT_VERSION_LIMIT', 10)
AUTO_SAVE_INTERVAL: Final[int] = get_env_int('AUTO_SAVE_INTERVAL', 30)  # seconds

# Analytics and reporting
ANALYTICS_RETENTION_DAYS: Final[int] = get_env_int('ANALYTICS_RETENTION_DAYS', 365)
REPORT_GENERATION_TIMEOUT: Final[int] = get_env_int('REPORT_GENERATION_TIMEOUT', 300)  # seconds

# =====================================
# COMPUTED CONSTANTS
# =====================================

# All choice tuples for easy access
ALL_CHOICES: Final[Dict[str, Tuple[Tuple[str, str], ...]]] = {
    'course_level': CourseLevel.choices(),
    'creation_method': CreationMethod.choices(),
    'completion_status': CompletionStatus.choices(),
    'lesson_type': LessonType.choices(),
    'access_level': AccessLevel.choices(),
    'resource_type': ResourceType.choices(),
    'question_type': QuestionType.choices(),
    'enrollment_status': EnrollmentStatus.choices(),
    'certificate_version': CERTIFICATE_TEMPLATE_VERSIONS
}

# Validation sets for quick membership testing
VALID_VALUES: Final[Dict[str, Tuple[str, ...]]] = {
    'course_level': CourseLevel.values(),
    'creation_method': CreationMethod.values(),
    'completion_status': tuple(item.code for item in CompletionStatus),
    'lesson_type': tuple(item.code for item in LessonType),
    'access_level': tuple(item.code for item in AccessLevel),
    'resource_type': tuple(item.code for item in ResourceType),
    'question_type': tuple(item.code for item in QuestionType),
    'enrollment_status': tuple(item.code for item in EnrollmentStatus)
}

# =====================================
# UTILITY FUNCTIONS
# =====================================

def validate_file_type(filename: str, expected_type: str) -> bool:
    """Validate file type based on extension"""
    if not filename or '.' not in filename:
        return False

    extension = filename.split('.')[-1].lower()
    allowed = ALLOWED_EXTENSIONS.get(expected_type, ())
    return extension in allowed

def validate_file_size(size: int, file_type: str) -> bool:
    """Validate file size against limits"""
    max_size = MAX_FILE_SIZE.get(file_type, 0)
    return 0 < size <= max_size

def validate_content_length(content: str, content_type: str) -> bool:
    """Validate content length against limits"""
    max_length = MAX_CONTENT_LENGTH.get(content_type, 0)
    return len(content) <= max_length

def get_business_constraint(key: str, default=None):
    """Get business constraint value with fallback"""
    return BUSINESS_CONSTRAINTS.get(key, default)

def is_valid_choice(value: str, choice_type: str) -> bool:
    """Check if value is valid for given choice type"""
    return value in VALID_VALUES.get(choice_type, ())

def get_access_level_hierarchy() -> Dict[str, int]:
    """Get access level hierarchy for comparison"""
    return AccessLevel.hierarchy()

def can_user_access_content(user_level: str, required_level: str) -> bool:
    """Check if user can access content based on access levels"""
    return AccessLevel.can_access(user_level, required_level)

# =====================================
# DEPRECATED CONSTANTS (FOR MIGRATION)
# =====================================

# Legacy constants maintained for backward compatibility
# TODO: Remove these in version 3.0.0

LEVEL_CHOICES = CourseLevel.choices()  # DEPRECATED: Use CourseLevel.choices()
CREATION_METHODS = CreationMethod.choices()  # DEPRECATED: Use CreationMethod.choices()
COMPLETION_STATUSES = CompletionStatus.choices()  # DEPRECATED: Use CompletionStatus.choices()
LESSON_TYPE_CHOICES = LessonType.choices()  # DEPRECATED: Use LessonType.choices()
ACCESS_LEVEL_CHOICES = AccessLevel.choices()  # DEPRECATED: Use AccessLevel.choices()
RESOURCE_TYPE_CHOICES = ResourceType.choices()  # DEPRECATED: Use ResourceType.choices()
QUESTION_TYPE_CHOICES = QuestionType.choices()  # DEPRECATED: Use QuestionType.choices()
STATUS_CHOICES = EnrollmentStatus.choices()  # DEPRECATED: Use EnrollmentStatus.choices()

# Export all public constants and enums
__all__ = [
    # Enums
    'CourseLevel', 'CreationMethod', 'CompletionStatus', 'LessonType',
    'AccessLevel', 'ResourceType', 'QuestionType', 'EnrollmentStatus', 'Priority',

    # Validation constants
    'MAX_FILE_SIZE', 'MAX_CONTENT_LENGTH', 'BUSINESS_CONSTRAINTS',
    'ALLOWED_EXTENSIONS', 'ALLOWED_MIME_TYPES', 'DANGEROUS_CONTENT_PATTERNS',

    # Configuration constants
    'DEFAULT_COURSE_PRICE', 'DEFAULT_CURRENCY', 'SUPPORTED_CURRENCIES',
    'MIN_RATING', 'MAX_RATING', 'DEFAULT_PASSING_SCORE', 'DEFAULT_MAX_ATTEMPTS',
    'DEFAULT_TIME_LIMIT', 'CERTIFICATE_TEMPLATE_VERSIONS', 'CACHE_TIMEOUTS',
    'RATE_LIMITS', 'DEFAULT_PAGE_SIZE', 'MAX_PAGE_SIZE',

    # Computed constants
    'ALL_CHOICES', 'VALID_VALUES',

    # Utility functions
    'validate_file_type', 'validate_file_size', 'validate_content_length',
    'get_business_constraint', 'is_valid_choice', 'get_access_level_hierarchy',
    'can_user_access_content', 'get_file_size_limit',

    # Enhanced environment helpers
    'get_env_decimal', 'get_env_int', 'get_env_bool',

    # Legacy (deprecated)
    'LEVEL_CHOICES', 'CREATION_METHODS', 'COMPLETION_STATUSES',
    'LESSON_TYPE_CHOICES', 'ACCESS_LEVEL_CHOICES', 'RESOURCE_TYPE_CHOICES',
    'QUESTION_TYPE_CHOICES', 'STATUS_CHOICES'
]
