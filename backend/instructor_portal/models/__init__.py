# File Path: instructor_portal/models/__init__.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:09:54
# Date Revised: 2025-06-27 04:03:52
# Current Date and Time (UTC): 2025-06-27 04:03:52
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 04:03:52 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Central re-export hub for instructor_portal models
# Maintains 100% backward compatibility with existing imports

# Import all utilities and shared components
from .utils import (
    TierManager,
    HTTPSURLValidator,
    validate_social_handle,
    generate_upload_path,
    generate_cover_upload_path,
    get_course_model,
    get_category_model,
    get_enrollment_model,
    get_review_model,
)

# Import all model classes
from .profile import InstructorProfile
from .analytics import InstructorAnalytics, InstructorAnalyticsHistory
from .course_link import CourseInstructor
from .dashboard import InstructorDashboard
from .creation import CourseCreationSession, CourseTemplate
from .drafts import DraftCourseContent, CourseContentDraft
from .notifications import InstructorNotification  # Restored class
from .security import InstructorSession  # Restored class
from .maintenance import InstructorPortalCleanup, InstructorPortalSystemHealth  # Restored classes

# Re-export all for backward compatibility
__all__ = [
    # Core Profile Models
    'TierManager',
    'InstructorProfile',

    # Analytics Models
    'InstructorAnalytics',
    'InstructorAnalyticsHistory',

    # Course Management Models
    'CourseInstructor',
    'CourseCreationSession',
    'CourseTemplate',

    # Content Management Models
    'DraftCourseContent',
    'CourseContentDraft',

    # Dashboard and UI Models
    'InstructorDashboard',

    # Notification and Security Models (restored)
    'InstructorNotification',
    'InstructorSession',

    # Maintenance Utilities (restored)
    'InstructorPortalCleanup',
    'InstructorPortalSystemHealth',

    # Helper Functions
    'get_course_model',
    'get_category_model',
    'get_enrollment_model',
    'get_review_model',
    'generate_upload_path',
    'generate_cover_upload_path',
    'validate_social_handle',

    # Custom Validators
    'HTTPSURLValidator',
]

# Model registry for dynamic imports and API discovery
MODEL_REGISTRY = {
    'profile': InstructorProfile,
    'analytics': InstructorAnalytics,
    'analytics_history': InstructorAnalyticsHistory,
    'course_instructor': CourseInstructor,
    'dashboard': InstructorDashboard,
    'creation_session': CourseCreationSession,
    'template': CourseTemplate,
    'draft_content': DraftCourseContent,
    'content_draft': CourseContentDraft,
    'notification': InstructorNotification,  # Added back
    'session': InstructorSession,  # Added back
}

# Version and metadata information
VERSION = '4.0.0'
LAST_UPDATED = '2025-06-27 04:03:52'
AUTHOR = 'softTechSolutions2001'

# Feature flags for progressive rollout
FEATURE_FLAGS = {
    'enhanced_analytics': True,
    'notification_system': True,
    'session_tracking': True,
    'ai_content_generation': True,
    'advanced_security': True,
    'performance_monitoring': True,
}

# Configuration constants
ANALYTICS_UPDATE_INTERVAL_HOURS = 1
SESSION_CLEANUP_DAYS = 30
NOTIFICATION_EXPIRE_DAYS = 7
FILE_CLEANUP_BATCH_SIZE = 100
HEALTH_CHECK_CACHE_TIMEOUT = 300  # 5 minutes

# Model relationship helpers for external apps
def get_instructor_profile_for_user(user):
    """Helper function to get instructor profile for a user"""
    try:
        return user.instructor_profile
    except (AttributeError, InstructorProfile.DoesNotExist):
        return None

def get_instructor_analytics(instructor_profile):
    """Helper function to get analytics for an instructor"""
    try:
        return instructor_profile.analytics
    except (AttributeError, InstructorAnalytics.DoesNotExist):
        return None

def get_instructor_dashboard(instructor_profile):
    """Helper function to get dashboard for an instructor"""
    try:
        return instructor_profile.dashboard
    except (AttributeError, InstructorDashboard.DoesNotExist):
        return None

# Add additional helper functions preserved from original code
def get_instructor_notifications(instructor_profile):
    """Helper function to get notifications for an instructor"""
    try:
        return instructor_profile.notifications.filter(is_dismissed=False).order_by('-created_date')
    except (AttributeError, Exception):
        return []

def get_instructor_sessions(instructor_profile):
    """Helper function to get active sessions for an instructor"""
    try:
        return instructor_profile.sessions.filter(is_active=True).order_by('-login_time')
    except (AttributeError, Exception):
        return []

# Add helper functions to __all__
__all__.extend([
    'MODEL_REGISTRY',
    'VERSION',
    'LAST_UPDATED',
    'AUTHOR',
    'FEATURE_FLAGS',
    'ANALYTICS_UPDATE_INTERVAL_HOURS',
    'SESSION_CLEANUP_DAYS',
    'NOTIFICATION_EXPIRE_DAYS',
    'FILE_CLEANUP_BATCH_SIZE',
    'HEALTH_CHECK_CACHE_TIMEOUT',
    'get_instructor_profile_for_user',
    'get_instructor_analytics',
    'get_instructor_dashboard',
    'get_instructor_notifications',
    'get_instructor_sessions',
])
