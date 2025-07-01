#
# File Path: instructor_portal/serializers/__init__.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 14:07:20
# Date Revised: 2025-06-27 06:16:38
# Current Date and Time (UTC): 2025-06-27 06:16:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:16:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Central re-export hub for instructor_portal serializers
# Maintains 100% backward compatibility with existing imports

from typing import TYPE_CHECKING

# Import all utilities and shared components
from .mixins import JsonFieldMixin, validate_json_list
from .utils import (
    safe_decimal_conversion,
    validate_file_path_security,
    validate_instructor_tier_access,
    calculate_content_hash,
    MAX_BULK_OPERATION_SIZE,
    MAX_RESOURCE_FILE_SIZE,
    MAX_THUMBNAIL_SIZE,
    MAX_JSON_COMPRESSION_SIZE,
    PERMISSIONS_CACHE_TIMEOUT,
)

# Import creation method constants for backward compatibility
from ..models import CourseCreationSession

# Re-export CREATION_METHODS constants for backward compatibility
VALID_CREATION_METHODS = [choice[0] for choice in CourseCreationSession.CreationMethod.choices]

# Safely import all serializer classes
if TYPE_CHECKING:
    # For type checking only imports - prevents circular import issues
    from .profile import InstructorProfileSerializer
    from .course_management import (
        CourseInstructorSerializer,
        InstructorResourceSerializer,
        InstructorLessonSerializer,
        InstructorModuleSerializer,
        InstructorCourseSerializer,
    )
    from .creation import (
        CourseCreationSessionSerializer,
        CourseTemplateSerializer,
        DraftCourseContentSerializer,
        CourseContentDraftSerializer,
        DraftCoursePublishSerializer,
    )
    from .dashboard import InstructorDashboardSerializer
    from .analytics import InstructorAnalyticsSerializer
    from .settings import InstructorSettingsSerializer
else:
    # Runtime imports
    from .profile import InstructorProfileSerializer
    from .course_management import (
        CourseInstructorSerializer,
        InstructorResourceSerializer,
        InstructorLessonSerializer,
        InstructorModuleSerializer,
        InstructorCourseSerializer,
    )
    from .creation import (
        CourseCreationSessionSerializer,
        CourseTemplateSerializer,
        DraftCourseContentSerializer,
        CourseContentDraftSerializer,
        DraftCoursePublishSerializer,
    )
    from .dashboard import InstructorDashboardSerializer
    from .analytics import InstructorAnalyticsSerializer
    from .settings import InstructorSettingsSerializer

# Re-export all for backward compatibility
__all__ = [
    # Profile Serializers
    'InstructorProfileSerializer',

    # Course Management Serializers
    'CourseInstructorSerializer',
    'InstructorResourceSerializer',
    'InstructorLessonSerializer',
    'InstructorModuleSerializer',
    'InstructorCourseSerializer',

    # Creation and Session Serializers
    'CourseCreationSessionSerializer',
    'CourseTemplateSerializer',
    'DraftCourseContentSerializer',
    'CourseContentDraftSerializer',
    'DraftCoursePublishSerializer',

    # Dashboard Serializers
    'InstructorDashboardSerializer',

    # Analytics Serializers
    'InstructorAnalyticsSerializer',

    # Settings Serializers
    'InstructorSettingsSerializer',

    # Shared Utilities
    'JsonFieldMixin',
    'validate_json_list',  # Added per audit recommendation
    'safe_decimal_conversion',
    'validate_file_path_security',
    'validate_instructor_tier_access',
    'calculate_content_hash',

    # Constants
    'MAX_BULK_OPERATION_SIZE',
    'MAX_RESOURCE_FILE_SIZE',
    'MAX_THUMBNAIL_SIZE',
    'MAX_JSON_COMPRESSION_SIZE',
    'PERMISSIONS_CACHE_TIMEOUT',
    'VALID_CREATION_METHODS',  # Added per audit recommendation
]

# Serializer registry for dynamic discovery
SERIALIZER_REGISTRY = {
    'instructor_profile': InstructorProfileSerializer,
    'course_instructor': CourseInstructorSerializer,
    'instructor_dashboard': InstructorDashboardSerializer,
    'instructor_course': InstructorCourseSerializer,
    'instructor_module': InstructorModuleSerializer,
    'instructor_lesson': InstructorLessonSerializer,
    'instructor_resource': InstructorResourceSerializer,
    'course_creation_session': CourseCreationSessionSerializer,
    'course_template': CourseTemplateSerializer,
    'draft_course_content': DraftCourseContentSerializer,
    'course_content_draft': CourseContentDraftSerializer,
    'draft_course_publish': DraftCoursePublishSerializer,
    'instructor_analytics': InstructorAnalyticsSerializer,
    'instructor_settings': InstructorSettingsSerializer,
}

# Version and metadata information
VERSION = '1.0.1'
LAST_UPDATED = '2025-06-27 06:16:38'
AUTHOR = 'softTechSolutions2001'

# Add registry to __all__
__all__.extend([
    'SERIALIZER_REGISTRY',
    'VERSION',
    'LAST_UPDATED',
    'AUTHOR',
])
