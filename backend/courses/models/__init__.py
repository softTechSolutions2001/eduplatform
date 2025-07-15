#
# File Path: backend/courses/models/__init__.py
# Folder Path: backend/courses/models/
# Date Created: 2025-06-26 15:27:42
# Date Revised: 2025-06-27 10:52:01
# Current Date and Time (UTC): 2025-06-27 10:52:01
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 10:52:01 UTC
# User: softTechSolutions2001
# Version: 4.1.0
#
# Re-exports all models to maintain backward compatibility

# Import and re-export utility functions from core.py
from .core import get_default_category, AnalyticsCourseMixin

# Import and re-export from core.py
from .core import (
    Category,
    Course,
    Module,
    Lesson,
    Resource,
    ActivityType
)

# Import and re-export from enrolment.py
from .enrolment import (
    Enrollment,
    Progress,
    Certificate,
    CourseProgress
)

# Import and re-export from analytics.py
from .analytics import (
    Review,
    UserActivity,
    CourseStats,
    UserStats,
    Notification,
    Assessment,
    Question,
    Answer,
    AttemptAnswer,
    Note,
    AssessmentAttempt
)

# Import and re-export from mixins.py
from .mixins import (
    BaseModelMixin,
    TimeStampedMixin,
    TimeStampedModelMixin,
    OrderedMixin,
    SlugMixin,
    SluggedModelMixin,
    StateMixin,
    DurationMixin,
    PublishableMixin,
    PublishableModelMixin,
    FileTrackingMixin,
    AnalyticsMixin,
    RateableModelMixin
)

# Import models from misc.py
from .misc import (
    Bookmark,
    UserPreference
)

# Define what gets exported when "from courses.models import *" is used
__all__ = [
    # Utility functions
    'get_default_category',
    'AnalyticsCourseMixin',

    # Core models
    'Category',
    'Course',
    'Module',
    'Lesson',
    'Resource',
    'ActivityType',

    # Enrollment models
    'Enrollment',
    'Progress',
    'Certificate',
    'CourseProgress',

    # Analytics models
    'Review',
    'UserActivity',
    'CourseStats',
    'UserStats',
    'Notification',
    'Assessment',
    'Question',
    'Answer',
    'AttemptAnswer',
    'Note',
    'AssessmentAttempt',

    # Mixins - include all variants for complete compatibility
    'BaseModelMixin',
    'TimeStampedMixin',
    'TimeStampedModelMixin',
    'OrderedMixin',
    'SlugMixin',
    'SluggedModelMixin',
    'StateMixin',
    'DurationMixin',
    'PublishableMixin',
    'PublishableModelMixin',
    'FileTrackingMixin',
    'AnalyticsMixin',
    'RateableModelMixin',

    # Misc models
    'Bookmark',
    'UserPreference'
]

# Log successful module initialization
import logging
logger = logging.getLogger(__name__)
logger.info("Enhanced courses models loaded successfully - v4.1.0")
logger.info(f"Total models: {len(__all__)}")
