"""
File: backend/common/constants.py
Purpose: Universal constants and nomenclature for entire Django project
Date Created: 2025-07-15 00:00:00 UTC
Version: 1.0.0 - Single Source of Truth

CONTAINS:
- Field names used across all apps
- Status codes and choices
- Error messages and response formats
- Security constants
- Cache patterns
- Universal method signatures
"""

from decimal import Decimal
from enum import Enum
from typing import Dict, List, Tuple

# =====================================
# UNIVERSAL FIELD NAMES & PATTERNS
# =====================================


class FieldNames:
    """Standardized field names used across all apps"""

    # Primary identification
    ID = "id"
    UUID = "uuid"
    SLUG = "slug"

    # User-related fields
    USER = "user"
    USER_ID = "user_id"
    EMAIL = "email"
    USERNAME = "username"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    FULL_NAME = "full_name"
    DISPLAY_NAME = "display_name"

    # Status fields
    IS_ACTIVE = "is_active"
    IS_VERIFIED = "is_verified"
    IS_APPROVED = "is_approved"
    IS_PUBLISHED = "is_published"
    IS_FEATURED = "is_featured"
    IS_DELETED = "is_deleted"
    STATUS = "status"

    # Role and permission fields
    ROLE = "role"
    PERMISSION_LEVEL = "permission_level"
    ACCESS_LEVEL = "access_level"

    # Timestamps (standardized across all models)
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DELETED_AT = "deleted_at"
    LAST_LOGIN = "last_login"
    LAST_ACTIVITY = "last_activity"
    EXPIRES_AT = "expires_at"
    STARTS_AT = "starts_at"
    ENDS_AT = "ends_at"

    # Content fields
    TITLE = "title"
    DESCRIPTION = "description"
    CONTENT = "content"
    SUMMARY = "summary"
    EXCERPT = "excerpt"

    # Media fields
    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    VIDEO_URL = "video_url"
    FILE_PATH = "file_path"
    FILE_SIZE = "file_size"
    FILE_TYPE = "file_type"

    # Numeric fields
    PRICE = "price"
    DISCOUNT = "discount"
    RATING = "rating"
    COUNT = "count"
    TOTAL = "total"
    DURATION = "duration"
    ORDER = "order"
    POSITION = "position"

    # Session fields
    SESSION_KEY = "session_key"
    IP_ADDRESS = "ip_address"
    USER_AGENT = "user_agent"
    DEVICE_TYPE = "device_type"
    LOGIN_METHOD = "login_method"

    # Security fields
    TOKEN = "token"
    FAILED_ATTEMPTS = "failed_attempts"
    LOCKOUT_UNTIL = "lockout_until"

    # Subscription fields
    TIER = "tier"
    SUBSCRIPTION_STATUS = "subscription_status"
    AUTO_RENEW = "auto_renew"


# =====================================
# UNIVERSAL STATUS CHOICES
# =====================================


class UserRoles:
    """Standardized user roles across all apps"""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    STAFF = "staff"
    MODERATOR = "moderator"

    CHOICES = [
        (STUDENT, "Student"),
        (INSTRUCTOR, "Instructor"),
        (ADMIN, "Administrator"),
        (STAFF, "Staff"),
        (MODERATOR, "Moderator"),
    ]

    # Role hierarchy for permission checking
    HIERARCHY = {
        STUDENT: 0,
        INSTRUCTOR: 1,
        MODERATOR: 2,
        STAFF: 3,
        ADMIN: 4,
    }


class SubscriptionTiers:
    """Standardized subscription tiers"""

    GUEST = "guest"
    REGISTERED = "registered"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

    CHOICES = [
        (GUEST, "Guest"),
        (REGISTERED, "Registered"),
        (PREMIUM, "Premium"),
        (ENTERPRISE, "Enterprise"),
    ]

    # Tier hierarchy for feature access
    HIERARCHY = {
        GUEST: 0,
        REGISTERED: 1,
        PREMIUM: 2,
        ENTERPRISE: 3,
    }


class CommonStatuses:
    """Generic status choices used across multiple models"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
        (ARCHIVED, "Archived"),
        (DELETED, "Deleted"),
        (SUSPENDED, "Suspended"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]


class DeviceTypes:
    """Standardized device type classifications"""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    BOT = "bot"
    TV = "tv"
    UNKNOWN = "unknown"

    CHOICES = [
        (DESKTOP, "Desktop"),
        (MOBILE, "Mobile"),
        (TABLET, "Tablet"),
        (BOT, "Bot"),
        (TV, "Smart TV"),
        (UNKNOWN, "Unknown"),
    ]


class LoginMethods:
    """Standardized authentication methods"""

    CREDENTIALS = "credentials"
    SOCIAL_GOOGLE = "social_google"
    SOCIAL_GITHUB = "social_github"
    SOCIAL_FACEBOOK = "social_facebook"
    SOCIAL_LINKEDIN = "social_linkedin"
    API_KEY = "api_key"
    SSO = "sso"
    MAGIC_LINK = "magic_link"

    CHOICES = [
        (CREDENTIALS, "Username/Password"),
        (SOCIAL_GOOGLE, "Google OAuth"),
        (SOCIAL_GITHUB, "GitHub OAuth"),
        (SOCIAL_FACEBOOK, "Facebook OAuth"),
        (SOCIAL_LINKEDIN, "LinkedIn OAuth"),
        (API_KEY, "API Key"),
        (SSO, "Single Sign-On"),
        (MAGIC_LINK, "Magic Link"),
    ]


# =====================================
# SECURITY CONSTANTS
# =====================================


class SecurityLimits:
    """Security-related limits and thresholds"""

    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    MAX_PASSWORD_LENGTH = 128
    PASSWORD_HISTORY_COUNT = 5

    # Login attempts and lockouts
    MAX_LOGIN_ATTEMPTS = 5
    EXTENDED_LOCKOUT_THRESHOLD = 10
    LOCKOUT_DURATION_MINUTES = 15
    EXTENDED_LOCKOUT_HOURS = 24

    # Session management
    SESSION_TIMEOUT_HOURS = 24
    SESSION_EXTENSION_HOURS = 24
    MAX_SESSION_EXTENSION_HOURS = 168  # 7 days
    SESSION_ACTIVITY_UPDATE_INTERVAL = 300  # 5 minutes
    MAX_CONCURRENT_SESSIONS = 10

    # Token lifetimes
    EMAIL_VERIFICATION_HOURS = 48
    PASSWORD_RESET_HOURS = 24
    API_TOKEN_HOURS = 8760  # 1 year
    REFRESH_TOKEN_DAYS = 14

    # Rate limiting
    REGISTRATION_RATE_LIMIT = "10/h"
    LOGIN_RATE_LIMIT = "20/h"
    PASSWORD_RESET_RATE_LIMIT = "5/h"
    EMAIL_VERIFY_RATE_LIMIT = "10/h"
    API_RATE_LIMIT = "1000/h"

    # File upload limits
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

    # Content limits
    MAX_USERNAME_LENGTH = 30
    MAX_EMAIL_LENGTH = 254
    MAX_NAME_LENGTH = 50
    MAX_BIO_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 1000


# =====================================
# CACHE PATTERNS
# =====================================


class CacheKeys:
    """Standardized cache key patterns"""

    # Cache key templates
    USER_PROFILE = "user:profile:{user_id}"
    USER_PERMISSIONS = "user:perms:{user_id}"
    USER_SESSIONS = "user:sessions:{user_id}"
    USER_SUBSCRIPTION = "user:subscription:{user_id}"

    # Permission caching
    PERMISSION_CHECK = "perm:{user_id}:{permission}"
    ROLE_PERMISSIONS = "role:perms:{role}"

    # Content caching
    COURSE_DETAIL = "course:detail:{course_id}"
    COURSE_LIST = "course:list:{filters_hash}"
    LESSON_CONTENT = "lesson:content:{lesson_id}"

    # Session caching
    SESSION_ACTIVITY = "session:activity:{session_key}"
    SESSION_DATA = "session:data:{session_key}"

    # Rate limiting
    RATE_LIMIT = "rate:{action}:{identifier}"

    # Health checks
    HEALTH_STATUS = "health:{service}:status"
    METRICS = "metrics:{service}:{timestamp}"

    @classmethod
    def generate_key(cls, template: str, **kwargs) -> str:
        """Generate cache key from template and parameters"""
        return template.format(**kwargs)


class CacheTimeouts:
    """Standardized cache timeout durations (in seconds)"""

    # Short-term caching
    MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    THIRTY_MINUTES = 1800

    # Medium-term caching
    HOUR = 3600
    THREE_HOURS = 10800
    SIX_HOURS = 21600
    TWELVE_HOURS = 43200

    # Long-term caching
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000

    # Specific use cases
    USER_PROFILE = HOUR
    PERMISSIONS = FIFTEEN_MINUTES
    SESSION_ACTIVITY = FIVE_MINUTES
    CONTENT = SIX_HOURS
    STATIC_DATA = DAY


# =====================================
# ERROR MESSAGES & RESPONSES
# =====================================


class ErrorMessages:
    """Standardized error messages"""

    # Authentication errors
    INVALID_CREDENTIALS = "Unable to log in with provided credentials."
    ACCOUNT_LOCKED = "Account temporarily locked. Try again in {minutes} minutes."
    EMAIL_NOT_VERIFIED = "Please verify your email address before logging in."
    TOKEN_EXPIRED = "Token has expired. Please request a new one."
    TOKEN_INVALID = "Invalid or malformed token."
    SESSION_EXPIRED = "Your session has expired. Please log in again."

    # Authorization errors
    PERMISSION_DENIED = "Permission denied."
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions for this action."
    ACCESS_DENIED = "Access denied to this resource."
    ROLE_REQUIRED = "This action requires {role} role or higher."

    # Validation errors
    REQUIRED_FIELD = "This field is required."
    INVALID_EMAIL_FORMAT = "Enter a valid email address."
    INVALID_USERNAME = (
        "Username can only contain letters, numbers, underscores, and hyphens."
    )
    WEAK_PASSWORD = "Password does not meet security requirements."
    PASSWORDS_DONT_MATCH = "Passwords do not match."
    EMAIL_ALREADY_EXISTS = "A user with this email already exists."
    USERNAME_ALREADY_EXISTS = "This username is already taken."

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later."
    LOGIN_ATTEMPTS_EXCEEDED = (
        "Too many login attempts. Please try again in {minutes} minutes."
    )

    # File upload errors
    FILE_TOO_LARGE = "File size exceeds maximum allowed size of {max_size}."
    INVALID_FILE_TYPE = "File type not allowed. Allowed types: {allowed_types}."
    UPLOAD_FAILED = "File upload failed. Please try again."

    # Content errors
    CONTENT_NOT_FOUND = "The requested content was not found."
    CONTENT_UNAVAILABLE = "This content is currently unavailable."
    SUBSCRIPTION_REQUIRED = "This feature requires a {tier} subscription or higher."

    # Generic errors
    SOMETHING_WENT_WRONG = "Something went wrong. Please try again."
    MAINTENANCE_MODE = "System is currently under maintenance. Please try again later."
    FEATURE_DISABLED = "This feature is currently disabled."


class SuccessMessages:
    """Standardized success messages"""

    # Authentication success
    LOGIN_SUCCESS = "Successfully logged in."
    LOGOUT_SUCCESS = "Successfully logged out."
    REGISTRATION_SUCCESS = (
        "Account created successfully. Please check your email to verify your account."
    )
    PASSWORD_CHANGED = "Password changed successfully."
    PASSWORD_RESET_SENT = (
        "If an account exists with this email, a password reset link has been sent."
    )

    # Email verification
    EMAIL_VERIFIED = "Email verified successfully."
    VERIFICATION_SENT = "Verification email has been sent."

    # Profile updates
    PROFILE_UPDATED = "Profile updated successfully."
    SETTINGS_SAVED = "Settings saved successfully."

    # Content operations
    CONTENT_CREATED = "Content created successfully."
    CONTENT_UPDATED = "Content updated successfully."
    CONTENT_DELETED = "Content deleted successfully."

    # Generic success
    OPERATION_COMPLETED = "Operation completed successfully."
    CHANGES_SAVED = "Changes saved successfully."


# =====================================
# HTTP STATUS CODES
# =====================================


class HTTPStatus:
    """Standardized HTTP status codes for consistent API responses"""

    # Success responses
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client error responses
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server error responses
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# =====================================
# API RESPONSE FORMATS
# =====================================


class ResponseFormats:
    """Standardized API response formats"""

    @staticmethod
    def success(data=None, message=None, status_code=HTTPStatus.OK, meta=None):
        """Standard success response format"""
        response = {
            "success": True,
            "status_code": status_code,
        }

        if data is not None:
            response["data"] = data

        if message:
            response["message"] = message

        if meta:
            response["meta"] = meta

        return response

    @staticmethod
    def error(
        error_message, details=None, status_code=HTTPStatus.BAD_REQUEST, error_code=None
    ):
        """Standard error response format"""
        response = {
            "success": False,
            "status_code": status_code,
            "error": {
                "message": error_message,
            },
        }

        if details:
            response["error"]["details"] = details

        if error_code:
            response["error"]["code"] = error_code

        return response

    @staticmethod
    def paginated(data, page, per_page, total, total_pages):
        """Standard paginated response format"""
        return {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }


# =====================================
# REGEX PATTERNS
# =====================================


class RegexPatterns:
    """Commonly used regex patterns"""

    # User data validation
    USERNAME = r"^[a-zA-Z0-9_-]+$"
    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE = r"^\+?1?\d{9,15}$"

    # Content validation
    SLUG = r"^[a-z0-9-]+$"
    URL_SAFE = r"^[a-zA-Z0-9\-._~:/?#[\]@!$&'()*+,;=%]+$"

    # File validation
    IMAGE_EXTENSIONS = r"\.(jpg|jpeg|png|gif|webp)$"
    VIDEO_EXTENSIONS = r"\.(mp4|avi|mov|wmv|webm)$"
    DOCUMENT_EXTENSIONS = r"\.(pdf|doc|docx|txt|rtf)$"

    # Security patterns
    PASSWORD_STRONG = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
    IP_ADDRESS = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    UUID_V4 = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"


# =====================================
# RESERVED KEYWORDS
# =====================================


class ReservedKeywords:
    """Reserved usernames, slugs, and other identifiers"""

    USERNAMES = [
        "admin",
        "administrator",
        "root",
        "api",
        "www",
        "mail",
        "email",
        "support",
        "help",
        "info",
        "contact",
        "about",
        "blog",
        "news",
        "user",
        "users",
        "account",
        "accounts",
        "profile",
        "profiles",
        "login",
        "logout",
        "register",
        "signup",
        "signin",
        "auth",
        "dashboard",
        "settings",
        "config",
        "system",
        "test",
        "demo",
    ]

    SLUGS = [
        "api",
        "admin",
        "www",
        "app",
        "mobile",
        "web",
        "static",
        "media",
        "assets",
        "cdn",
        "blog",
        "news",
        "about",
        "contact",
        "help",
        "terms",
        "privacy",
        "legal",
        "support",
        "docs",
        "documentation",
    ]

    EMAIL_DOMAINS = ["example.com", "test.com", "localhost", "127.0.0.1"]


# =====================================
# FILE TYPE CONFIGURATIONS
# =====================================


class FileTypes:
    """File type configurations and limits"""

    IMAGES = {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"],
        "max_size": 5 * 1024 * 1024,  # 5MB
    }

    VIDEOS = {
        "extensions": [".mp4", ".avi", ".mov", ".wmv", ".webm"],
        "mime_types": ["video/mp4", "video/avi", "video/quicktime", "video/webm"],
        "max_size": 100 * 1024 * 1024,  # 100MB
    }

    DOCUMENTS = {
        "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
        "mime_types": ["application/pdf", "application/msword", "text/plain"],
        "max_size": 10 * 1024 * 1024,  # 10MB
    }

    AUDIO = {
        "extensions": [".mp3", ".wav", ".ogg", ".m4a"],
        "mime_types": ["audio/mpeg", "audio/wav", "audio/ogg"],
        "max_size": 50 * 1024 * 1024,  # 50MB
    }


# =====================================
# UNIVERSAL UTILITY FUNCTIONS
# =====================================


def get_choice_display(choices_list: List[Tuple], value: str) -> str:
    """Get display value for a choice field"""
    choice_dict = dict(choices_list)
    return choice_dict.get(value, value)


def validate_role_hierarchy(user_role: str, required_role: str) -> bool:
    """Validate if user role meets minimum required role level"""
    user_level = UserRoles.HIERARCHY.get(user_role, 0)
    required_level = UserRoles.HIERARCHY.get(required_role, 0)
    return user_level >= required_level


def validate_subscription_tier(user_tier: str, required_tier: str) -> bool:
    """Validate if user subscription tier meets minimum required tier"""
    user_level = SubscriptionTiers.HIERARCHY.get(user_tier, 0)
    required_level = SubscriptionTiers.HIERARCHY.get(required_tier, 0)
    return user_level >= required_level


# =====================================
# EXPORT ALL CONSTANTS
# =====================================

__all__ = [
    "FieldNames",
    "UserRoles",
    "SubscriptionTiers",
    "CommonStatuses",
    "DeviceTypes",
    "LoginMethods",
    "SecurityLimits",
    "CacheKeys",
    "CacheTimeouts",
    "ErrorMessages",
    "SuccessMessages",
    "HTTPStatus",
    "ResponseFormats",
    "RegexPatterns",
    "ReservedKeywords",
    "FileTypes",
    "get_choice_display",
    "validate_role_hierarchy",
    "validate_subscription_tier",
]
