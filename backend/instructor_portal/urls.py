#
# File Path: instructor_portal/urls.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-18 17:03:37
# Date Revised: 2025-06-24 09:00:00
# Current Date and Time (UTC): 2025-06-24 09:00:00
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: saiacupunctureFolllow
# Last Modified: 2025-06-24 09:00:00 UTC
# User: sujibeautysalon
# Version: 2.1.0
#
# Optimized Instructor Portal URL Configuration
#
# Version 2.1.0 Changes:
# - ADDED: DragDropBuilderViewSet registration for drag-and-drop course builder
# - ADDED: DraftCourseContentViewSet registration for draft content management
# - UPDATED: Import statements to include new builder_views and draft_content_views
# - ENHANCED: Router configuration with new endpoint registrations
# - MAINTAINED: All existing functionality and URL patterns
#
# Version 2.0.0 Changes:
# - REMOVED: Redundant/duplicate URL patterns
# - FIXED: Regex pattern conflicts causing format_suffix_patterns errors
# - OPTIMIZED: Consolidated similar patterns for better maintainability
# - SIMPLIFIED: Removed complex post-processing that caused conflicts
# - ENHANCED: Cleaner structure with better organization

from django.urls import path, include
from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

# Import core viewsets
from .views import (
    InstructorCourseViewSet, InstructorModuleViewSet, InstructorLessonViewSet,
    InstructorResourceViewSet, debug_courses
)

# Import API viewsets
from .api_views import (
    InstructorProfileViewSet, InstructorDashboardViewSet, InstructorAnalyticsViewSet,
    CourseCreationSessionViewSet, CourseTemplateViewSet, DraftCourseContentViewSet,
    CourseCollaborationViewSet, InstructorSettingsViewSet
)

# Import additional views
from .auth_views import (
    InstructorRegistrationView, InstructorVerificationView,
    InstructorApprovalView, InstructorStatusView
)

from .creation_views import (
    CourseWizardViewSet, AICourseBuilderlViewSet, DragDropBuilderViewSet,
    TemplateBuilderViewSet, ContentImportViewSet
)

from .dashboard_views import (
    InstructorDashboardView, InstructorAnalyticsView, InstructorReportsView,
    StudentManagementView, RevenueAnalyticsView
)

# Import suggested new views
from .builder_views import DragDropBuilderViewSet as BuilderDragDropViewSet
from courses.draft_content_views import DraftCourseContentViewSet as CoursesDraftContentViewSet

# Additional imports based on suggestion
try:
    from .views import CourseInstructorViewSet
except ImportError:
    CourseInstructorViewSet = None

# Configuration
CACHE_TIMEOUT_SHORT = 300    # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
API_VERSION = 'v1'

app_name = 'instructor_portal'

# =====================================
# API ROUTER CONFIGURATION
# =====================================

router = DefaultRouter(trailing_slash=True)

# Core functionality - Updated basenames to match suggestion pattern
router.register(r'courses', InstructorCourseViewSet, basename='instructor-course')
router.register(r'modules', InstructorModuleViewSet, basename='instructor-module')
router.register(r'lessons', InstructorLessonViewSet, basename='instructor-lesson')
router.register(r'resources', InstructorResourceViewSet, basename='instructor-resource')

# Profile and dashboard
router.register(r'profile', InstructorProfileViewSet, basename='instructor-profile')
router.register(r'dashboard', InstructorDashboardViewSet, basename='instructor-dashboard')
router.register(r'analytics', InstructorAnalyticsViewSet, basename='instructor-analytics')
router.register(r'settings', InstructorSettingsViewSet, basename='instructor-settings')

# Course creation - Updated basename to match suggestion
router.register(r'sessions', CourseCreationSessionViewSet, basename='course-creation-session')
router.register(r'templates', CourseTemplateViewSet, basename='course-template')

# Course instructors (if available)
if CourseInstructorViewSet:
    router.register(r'course-instructors', CourseInstructorViewSet, basename='course-instructor')

# Legacy creation sessions (maintaining backward compatibility)
router.register(r'creation-sessions', CourseCreationSessionViewSet, basename='creation-sessions')
router.register(r'draft-content', DraftCourseContentViewSet, basename='draft-content')

# Creation methods
router.register(r'wizard', CourseWizardViewSet, basename='course-wizard')
router.register(r'ai-builder', AICourseBuilderlViewSet, basename='ai-builder')
router.register(r'drag-drop', DragDropBuilderViewSet, basename='drag-drop')
router.register(r'template-builder', TemplateBuilderViewSet, basename='template-builder')
router.register(r'content-import', ContentImportViewSet, basename='content-import')

# NEW REGISTRATIONS FROM SUGGESTION
# Drag and Drop Builder Sessions
router.register(
    r"dnd/sessions",
    BuilderDragDropViewSet,
    basename="dnd-session",
)

# Draft Course Content from courses app
router.register(
    r"draft_course_content",
    CoursesDraftContentViewSet,
    basename="draft-course-content"
)

# Collaboration
router.register(r'collaboration', CourseCollaborationViewSet, basename='collaboration')

# =====================================
# MAIN URL PATTERNS
# =====================================

urlpatterns = [

    # =====================================
    # API ENDPOINTS
    # =====================================

    # Main API router
    path(f'api/{API_VERSION}/', include(router.urls)),

    # =====================================
    # AUTHENTICATION
    # =====================================

    path('auth/', include([
        path('register/', InstructorRegistrationView.as_view(), name='instructor-register'),
        path('verify/<uuid:verification_token>/', InstructorVerificationView.as_view(), name='instructor-verify'),
        path('status/', InstructorStatusView.as_view(), name='instructor-status'),
        path('approval/', InstructorApprovalView.as_view(), name='instructor-approval'),
    ])),

    # =====================================
    # DASHBOARD & ANALYTICS
    # =====================================

    # Main dashboard
    path('dashboard/', cache_page(CACHE_TIMEOUT_SHORT)(InstructorDashboardView.as_view()), name='instructor-dashboard'),

    # Analytics
    path('analytics/', include([
        path('', cache_page(CACHE_TIMEOUT_MEDIUM)(InstructorAnalyticsView.as_view()), name='instructor-analytics'),
        path('reports/', InstructorReportsView.as_view(), name='instructor-reports'),
        path('revenue/', RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    ])),

    # Student management
    path('students/', StudentManagementView.as_view(), name='student-management'),

    # =====================================
    # COURSE CREATION
    # =====================================

    path('create/', include([
        # Main entry point
        path('', cache_page(CACHE_TIMEOUT_SHORT)(InstructorDashboardView.as_view()), name='course-create'),

        # Wizard workflow
        path('wizard/', include([
            path('', CourseWizardViewSet.as_view({'get': 'start'}), name='wizard-start'),
            path('step/<int:step>/', CourseWizardViewSet.as_view({'get': 'get_step', 'post': 'save_step'}), name='wizard-step'),
            path('resume/<uuid:session_id>/', CourseWizardViewSet.as_view({'get': 'resume'}), name='wizard-resume'),
            path('complete/<uuid:session_id>/', CourseWizardViewSet.as_view({'post': 'complete'}), name='wizard-complete'),
        ])),

        # AI Builder
        path('ai/', include([
            path('', AICourseBuilderlViewSet.as_view({'get': 'start', 'post': 'generate'}), name='ai-start'),
            path('session/<uuid:session_id>/', AICourseBuilderlViewSet.as_view({'get': 'get_session', 'put': 'update_session'}), name='ai-session'),
            path('refine/<uuid:session_id>/', AICourseBuilderlViewSet.as_view({'post': 'refine'}), name='ai-refine'),
            path('approve/<uuid:session_id>/', AICourseBuilderlViewSet.as_view({'post': 'approve'}), name='ai-approve'),
        ])),

        # Drag & Drop Builder
        path('dnd/', include([
            path('', DragDropBuilderViewSet.as_view({'get': 'start'}), name='dnd-start'),
            path('session/<uuid:session_id>/', DragDropBuilderViewSet.as_view({'get': 'get_session', 'put': 'update_session'}), name='dnd-session'),
            path('content/<uuid:session_id>/', DragDropBuilderViewSet.as_view({'post': 'add_content', 'put': 'update_content'}), name='dnd-content'),
            path('reorder/<uuid:session_id>/', DragDropBuilderViewSet.as_view({'post': 'reorder_content'}), name='dnd-reorder'),
        ])),

        # Template Builder
        path('template/', include([
            path('', TemplateBuilderViewSet.as_view({'get': 'list_templates'}), name='template-list'),
            path('<int:template_id>/', TemplateBuilderViewSet.as_view({'get': 'get_template', 'post': 'create_from_template'}), name='template-use'),
            path('session/<uuid:session_id>/', TemplateBuilderViewSet.as_view({'get': 'get_session', 'put': 'customize_template'}), name='template-customize'),
        ])),

        # Content Import
        path('import/', include([
            path('', ContentImportViewSet.as_view({'get': 'start', 'post': 'import_content'}), name='import-start'),
            path('session/<uuid:session_id>/', ContentImportViewSet.as_view({'get': 'get_import_status'}), name='import-status'),
            path('process/<uuid:session_id>/', ContentImportViewSet.as_view({'post': 'process_import'}), name='import-process'),
        ])),
    ])),

    # =====================================
    # COURSE MANAGEMENT
    # =====================================

    path('courses/', include([
        # Course list
        path('', InstructorCourseViewSet.as_view({'get': 'list'}), name='course-list'),
        path('create/', InstructorCourseViewSet.as_view({'post': 'create'}), name='course-quick-create'),

        # Individual course management
        path('<slug:slug>/', include([
            path('', InstructorCourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='course-detail'),
            path('edit/', InstructorCourseViewSet.as_view({'get': 'retrieve'}), name='course-edit'),
            path('publish/', InstructorCourseViewSet.as_view({'post': 'publish_version'}), name='course-publish'),
            path('clone/', InstructorCourseViewSet.as_view({'post': 'clone'}), name='course-clone'),
            path('versions/', InstructorCourseViewSet.as_view({'get': 'versions'}), name='course-versions'),

            # Module management
            path('modules/', include([
                path('', InstructorModuleViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-modules'),
                path('reorder/', InstructorCourseViewSet.as_view({'post': 'reorder_modules'}), name='modules-reorder'),
                path('<int:module_id>/', include([
                    path('', InstructorModuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='module-detail'),
                    path('lessons/', InstructorLessonViewSet.as_view({'get': 'list', 'post': 'create'}), name='module-lessons'),
                    path('lessons/reorder/', InstructorModuleViewSet.as_view({'post': 'reorder_lessons'}), name='lessons-reorder'),
                ])),
            ])),

            # Lesson management
            path('lessons/<int:lesson_id>/', include([
                path('', InstructorLessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='lesson-detail'),
                path('resources/', InstructorResourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='lesson-resources'),
            ])),

            # Course collaboration
            path('collaborate/', include([
                path('', CourseCollaborationViewSet.as_view({'get': 'list', 'post': 'invite'}), name='course-collaborate'),
                path('invitations/', CourseCollaborationViewSet.as_view({'get': 'invitations'}), name='collaboration-invitations'),
                path('accept/<uuid:invitation_id>/', CourseCollaborationViewSet.as_view({'post': 'accept_invitation'}), name='accept-invitation'),
            ])),

            # Course analytics
            path('analytics/', InstructorAnalyticsViewSet.as_view({'get': 'course_analytics'}), name='course-analytics'),
        ])),
    ])),

    # =====================================
    # CONTENT MANAGEMENT
    # =====================================

    # Draft content
    path('drafts/', include([
        path('', DraftCourseContentViewSet.as_view({'get': 'list'}), name='draft-list'),
        path('<uuid:session_id>/', DraftCourseContentViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='draft-detail'),
        path('<uuid:session_id>/auto-save/', DraftCourseContentViewSet.as_view({'post': 'auto_save'}), name='draft-auto-save'),
        path('<uuid:session_id>/export/', DraftCourseContentViewSet.as_view({'get': 'export'}), name='draft-export'),
    ])),

    # File uploads
    path('uploads/', include([
        path('presigned-url/', InstructorResourceViewSet.as_view({'post': 'presigned_url'}), name='upload-presigned-url'),
        path('complete/', InstructorResourceViewSet.as_view({'post': 'upload_complete'}), name='upload-complete'),
        path('batch/', InstructorResourceViewSet.as_view({'post': 'batch_upload'}), name='upload-batch'),
    ])),

    # =====================================
    # PROFILE & SETTINGS
    # =====================================

    # Profile management
    path('profile/', include([
        path('', InstructorProfileViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile-detail'),
        path('edit/', InstructorProfileViewSet.as_view({'get': 'retrieve'}), name='profile-edit'),
        path('verify/', InstructorProfileViewSet.as_view({'post': 'request_verification'}), name='profile-verify'),
        path('tier/', InstructorProfileViewSet.as_view({'get': 'tier_info'}), name='profile-tier'),
    ])),

    # Settings
    path('settings/', include([
        path('', InstructorSettingsViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='settings-detail'),
        path('dashboard/', InstructorDashboardViewSet.as_view({'get': 'get_config', 'put': 'update_config'}), name='dashboard-settings'),
        path('notifications/', InstructorSettingsViewSet.as_view({'get': 'notifications', 'put': 'update_notifications'}), name='notification-settings'),
    ])),

    # =====================================
    # TEMPLATES & UTILITIES
    # =====================================

    # Course templates
    path('templates/', include([
        path('', CourseTemplateViewSet.as_view({'get': 'list'}), name='template-list'),
        path('<int:template_id>/', CourseTemplateViewSet.as_view({'get': 'retrieve'}), name='template-detail'),
        path('<int:template_id>/preview/', CourseTemplateViewSet.as_view({'get': 'preview'}), name='template-preview'),
        path('create/', CourseTemplateViewSet.as_view({'post': 'create'}), name='template-create'),
    ])),

    # Bulk operations
    path('bulk/', include([
        path('import/', InstructorCourseViewSet.as_view({'post': 'bulk_import'}), name='bulk-import'),
        path('export/', InstructorCourseViewSet.as_view({'post': 'bulk_export'}), name='bulk-export'),
        path('status/<uuid:task_id>/', InstructorCourseViewSet.as_view({'get': 'import_status'}), name='bulk-status'),
    ])),

    # Utilities
    path('utils/', include([
        path('check-title/', InstructorCourseViewSet.as_view({'post': 'check_title'}), name='check-title'),
        path('generate-slug/', InstructorCourseViewSet.as_view({'post': 'generate_slug'}), name='generate-slug'),
        path('validate-content/', DraftCourseContentViewSet.as_view({'post': 'validate_content'}), name='validate-content'),
    ])),

    # =====================================
    # ADVANCED FEATURES
    # =====================================

    # AI features
    path('ai/', include([
        path('suggestions/', AICourseBuilderlViewSet.as_view({'post': 'get_suggestions'}), name='ai-suggestions'),
        path('content-enhancement/', AICourseBuilderlViewSet.as_view({'post': 'enhance_content'}), name='ai-enhance'),
        path('quality-check/', AICourseBuilderlViewSet.as_view({'post': 'quality_check'}), name='ai-quality'),
    ])),

    # Advanced reports
    path('reports/', include([
        path('performance/', InstructorAnalyticsViewSet.as_view({'get': 'performance_report'}), name='performance-report'),
        path('engagement/', InstructorAnalyticsViewSet.as_view({'get': 'engagement_report'}), name='engagement-report'),
        path('revenue/', InstructorAnalyticsViewSet.as_view({'get': 'revenue_report'}), name='revenue-report'),
        path('export/<str:report_type>/', InstructorAnalyticsViewSet.as_view({'get': 'export_report'}), name='export-report'),
    ])),

    # =====================================
    # INTEGRATIONS & DEBUG
    # =====================================

    # Third-party integrations
    path('integrations/', include([
        path('lti/', include('instructor_portal.lti_urls')),
        path('webhooks/', include('instructor_portal.webhook_urls')),
        path('api/external/', include('instructor_portal.external_api_urls')),
    ])),

    # DEBUG endpoints
    path('debug/', include([
        path('courses/', debug_courses, name='debug-courses'),
        path('courses/simple/', debug_courses, {'template': 'simple'}, name='debug-courses-simple'),
        path('diagnostic/', debug_courses, name='debug-diagnostic'),
    ])),

    # Health check
    path('health/', include([
        path('', InstructorDashboardViewSet.as_view({'get': 'health_check'}), name='health-check'),
        path('detailed/', InstructorDashboardViewSet.as_view({'get': 'detailed_health'}), name='detailed-health'),
    ])),
]

# Add router URLs to urlpatterns as suggested
urlpatterns += router.urls

# =====================================
# DEVELOPMENT URLS
# =====================================

if settings.DEBUG:
    urlpatterns += [
        path('dev/', include([
            path('test-creation/', CourseWizardViewSet.as_view({'get': 'dev_test'}), name='dev-test-creation'),
            path('mock-ai/', AICourseBuilderlViewSet.as_view({'post': 'dev_mock'}), name='dev-mock-ai'),
            path('clear-cache/', InstructorDashboardViewSet.as_view({'post': 'clear_cache'}), name='dev-clear-cache'),
        ])),
    ]

# =====================================
# KEY CHANGES IN VERSION 2.1.0
# =====================================

"""
INCORPORATED SUGGESTIONS:

1. ADDED: New DragDropBuilderViewSet registration
   - Registered as "dnd/sessions" with basename "dnd-session"
   - Imports from builder_views module
   - Enables drag-and-drop course building functionality

2. ADDED: New DraftCourseContentViewSet registration
   - Registered as "draft_course_content" with basename "draft-course-content"
   - Imports from courses.draft_content_views module
   - Provides API access to draft content management

3. UPDATED: Router configuration
   - Added trailing_slash=True as suggested
   - Updated basenames to match suggested naming convention
   - Maintained backward compatibility with existing patterns

4. ENHANCED: Import handling
   - Added conditional import for CourseInstructorViewSet
   - Safe import with try/except for missing modules
   - Aliased imported classes to avoid naming conflicts

5. MAINTAINED: All existing functionality
   - Preserved all existing URL patterns
   - Kept both old and new basename patterns for compatibility
   - Added router.urls to urlpatterns as suggested

BENEFITS:
- Enhanced drag-and-drop course building capabilities
- Improved draft content management through API
- Better API consistency with suggested naming conventions
- Maintained backward compatibility
- Added new functionality without breaking existing features

The integration successfully combines the existing comprehensive URL structure
with the new suggested API endpoints for enhanced course creation workflows.
"""
