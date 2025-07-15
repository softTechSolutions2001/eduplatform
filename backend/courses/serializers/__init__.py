# Serializers for courses app
#
# File Path: backend/courses/serializers/__init__.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:21:42
# Date Revised: 2025-06-26 10:21:42
# Current Date and Time (UTC): 2025-06-26 10:21:42
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 10:21:42 UTC
# User: softTechSolutions2001
# Version: 3.0.0
#
# Re-exports all serializers for backward compatibility

# Base mixins
from .mixins import (
    ContextPropagationMixin, OptimizedQueryMixin, EnhancedValidationMixin
)

# Core serializers
from .core import (
    CategorySerializer, ResourceSerializer, LessonSerializer,
    ModuleSerializer, ModuleDetailSerializer, CourseInstructorSerializer,
    CourseVersionSerializer, CourseSerializer, CourseDetailSerializer,
    CourseCloneSerializer
)

# Enrollment-related serializers
from .enrolment import (
    EnrollmentSerializer, ProgressSerializer, CertificateSerializer,
    UserProgressStatsSerializer
)

# Analytics-related serializers
from .analytics import (
    AnswerSerializer, QuestionSerializer, QuestionDetailSerializer,
    AssessmentSerializer, AssessmentAttemptSerializer, AttemptAnswerSerializer,
    ReviewSerializer, NoteSerializer
)

# Miscellaneous serializers
from .misc import (
    LessonNotesUploadSerializer, BulkEnrollmentSerializer, CourseFeedbackSerializer
)

# Re-export all serializers for easy importing
__all__ = [
    # Mixins
    'ContextPropagationMixin', 'OptimizedQueryMixin', 'EnhancedValidationMixin',

    # Core
    'CategorySerializer', 'ResourceSerializer', 'LessonSerializer',
    'ModuleSerializer', 'ModuleDetailSerializer', 'CourseInstructorSerializer',
    'CourseVersionSerializer', 'CourseSerializer', 'CourseDetailSerializer',
    'CourseCloneSerializer',

    # Enrollment
    'EnrollmentSerializer', 'ProgressSerializer', 'CertificateSerializer',
    'UserProgressStatsSerializer',

    # Analytics
    'AnswerSerializer', 'QuestionSerializer', 'QuestionDetailSerializer',
    'AssessmentSerializer', 'AssessmentAttemptSerializer', 'AttemptAnswerSerializer',
    'ReviewSerializer', 'NoteSerializer',

    # Misc
    'LessonNotesUploadSerializer', 'BulkEnrollmentSerializer', 'CourseFeedbackSerializer'
]
