# 🚀 Django Project Endpoints

**Generated on:** 2025-06-25 22:12:06

**Total endpoints:** 710

**API endpoints:** 364
**Web endpoints:** 346

---

## API Endpoints

### Main API Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `//api/instructor/ai-course-builder` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-list |
| `//api/instructor/ai-course-builder.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-list |
| `//api/instructor/ai-course-builder/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-detail |
| `//api/instructor/ai-course-builder/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-detail |
| `//api/instructor/ai-course-builder/<pk>/finalize` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-finalize |
| `//api/instructor/ai-course-builder/<pk>/finalize.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-finalize |
| `//api/instructor/ai-course-builder/<pk>/task-status/<task_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-task-status |
| `//api/instructor/ai-course-builder/<pk>/task-status/<task_id>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-task-status |
| `//api/instructor/ai-course-builder/initialize` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-initialize |
| `//api/instructor/ai-course-builder/initialize.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderDraftViewSet` | ai-course-builder-initialize |
| `/api//testimonials` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TestimonialViewSet` | testimonial-list |
| `/api//testimonials.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TestimonialViewSet` | testimonial-list |
| `/api//testimonials/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TestimonialViewSet` | testimonial-detail |
| `/api//testimonials/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TestimonialViewSet` | testimonial-detail |
| `/api/user//sessions` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserSessionViewSet` | user-sessions-list |
| `/api/user//sessions.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserSessionViewSet` | user-sessions-list |
| `/api/user//sessions/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserSessionViewSet` | user-sessions-detail |
| `/api/user//sessions/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserSessionViewSet` | user-sessions-detail |
| `/api/user//subscription` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-list |
| `/api/user//subscription.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-list |
| `/api/user//subscription/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-detail |
| `/api/user//subscription/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-detail |
| `/api/user//subscription/cancel` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-cancel |
| `/api/user//subscription/cancel.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-cancel |
| `/api/user//subscription/current` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-current |
| `/api/user//subscription/current.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-current |
| `/api/user//subscription/downgrade` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-downgrade |
| `/api/user//subscription/downgrade.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-downgrade |
| `/api/user//subscription/upgrade` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-upgrade |
| `/api/user//subscription/upgrade.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SubscriptionViewSet` | user-subscription-upgrade |

### Courses API Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api//categories` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CategoryViewSet` | category-list |
| `/api//categories.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CategoryViewSet` | category-list |
| `/api//categories/<slug>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CategoryViewSet` | category-detail |
| `/api//categories/<slug>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CategoryViewSet` | category-detail |
| `/api//certificates` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-list |
| `/api//certificates.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-list |
| `/api//certificates/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-detail |
| `/api//certificates/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-detail |
| `/api//certificates/verify` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-verify |
| `/api//certificates/verify.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateViewSet` | certificate-verify |
| `/api//courses` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-list |
| `/api//courses.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-list |
| `/api//courses/<slug>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-detail |
| `/api//courses/<slug>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-detail |
| `/api//courses/<slug>/clone` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-clone |
| `/api//courses/<slug>/clone.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-clone |
| `/api//courses/<slug>/enroll` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-enroll |
| `/api//courses/<slug>/enroll.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-enroll |
| `/api//courses/<slug>/publish` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-publish |
| `/api//courses/<slug>/publish.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-publish |
| `/api//courses/<slug>/unpublish` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-unpublish |
| `/api//courses/<slug>/unpublish.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-unpublish |
| `/api//courses/featured` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-featured |
| `/api//courses/featured.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseViewSet` | course-featured |
| `/api//enrollments` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-list |
| `/api//enrollments.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-list |
| `/api//enrollments/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-detail |
| `/api//enrollments/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-detail |
| `/api//enrollments/<pk>/unenroll` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-unenroll |
| `/api//enrollments/<pk>/unenroll.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EnrollmentViewSet` | enrollment-unenroll |
| `/api//lessons` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LessonViewSet` | lesson-list |
| `/api//lessons.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LessonViewSet` | lesson-list |
| `/api//lessons/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LessonViewSet` | lesson-detail |
| `/api//lessons/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LessonViewSet` | lesson-detail |
| `/api//modules` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ModuleViewSet` | module-list |
| `/api//modules.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ModuleViewSet` | module-list |
| `/api//modules/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ModuleViewSet` | module-detail |
| `/api//modules/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ModuleViewSet` | module-detail |
| `/api//notes` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `NoteViewSet` | note-list |
| `/api//notes.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `NoteViewSet` | note-list |
| `/api//notes/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `NoteViewSet` | note-detail |
| `/api//notes/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `NoteViewSet` | note-detail |
| `/api//progress` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ProgressViewSet` | progress-list |
| `/api//progress.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ProgressViewSet` | progress-list |
| `/api//progress/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ProgressViewSet` | progress-detail |
| `/api//progress/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ProgressViewSet` | progress-detail |
| `/api//reviews` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ReviewViewSet` | review-list |
| `/api//reviews.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ReviewViewSet` | review-list |
| `/api//reviews/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ReviewViewSet` | review-detail |
| `/api//reviews/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ReviewViewSet` | review-detail |

### Instructor_Portal API Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/instructor/ai/content-enhancement` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-enhance |
| `/api/instructor/ai/quality-check` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-quality |
| `/api/instructor/ai/suggestions` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-suggestions |
| `/api/instructor/analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-list |
| `/api/instructor/analytics.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-list |
| `/api/instructor/analytics/course_analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-course-analytics |
| `/api/instructor/analytics/course_analytics.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-course-analytics |
| `/api/instructor/analytics/engagement_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-engagement-report |
| `/api/instructor/analytics/engagement_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-engagement-report |
| `/api/instructor/analytics/performance_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-performance-report |
| `/api/instructor/analytics/performance_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-performance-report |
| `/api/instructor/analytics/revenue_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-revenue-report |
| `/api/instructor/analytics/revenue_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-revenue-report |
| `/api/instructor/api/v1/analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-list |
| `/api/instructor/api/v1/analytics.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-list |
| `/api/instructor/api/v1/analytics/course_analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-course-analytics |
| `/api/instructor/api/v1/analytics/course_analytics.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-course-analytics |
| `/api/instructor/api/v1/analytics/engagement_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-engagement-report |
| `/api/instructor/api/v1/analytics/engagement_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-engagement-report |
| `/api/instructor/api/v1/analytics/performance_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-performance-report |
| `/api/instructor/api/v1/analytics/performance_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-performance-report |
| `/api/instructor/api/v1/analytics/revenue_report` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-revenue-report |
| `/api/instructor/api/v1/analytics/revenue_report.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | instructor-analytics-revenue-report |
| `/api/instructor/api/v1/collaboration` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-list |
| `/api/instructor/api/v1/collaboration.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-list |
| `/api/instructor/api/v1/collaboration/invite` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-invite |
| `/api/instructor/api/v1/collaboration/invite.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-invite |
| `/api/instructor/api/v1/course-instructors` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-list |
| `/api/instructor/api/v1/course-instructors.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-list |
| `/api/instructor/api/v1/course-instructors/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-detail |
| `/api/instructor/api/v1/course-instructors/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-detail |
| `/api/instructor/api/v1/courses` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-list |
| `/api/instructor/api/v1/courses.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-list |
| `/api/instructor/api/v1/courses/<slug>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-detail |
| `/api/instructor/api/v1/courses/<slug>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-detail |
| `/api/instructor/api/v1/courses/<slug>/clone` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-clone |
| `/api/instructor/api/v1/courses/<slug>/clone.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-clone |
| `/api/instructor/api/v1/courses/<slug>/reorder-modules` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-reorder-modules |
| `/api/instructor/api/v1/courses/<slug>/reorder-modules.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-reorder-modules |
| `/api/instructor/api/v1/creation-sessions` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-list |
| `/api/instructor/api/v1/creation-sessions.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-list |
| `/api/instructor/api/v1/creation-sessions/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-detail |
| `/api/instructor/api/v1/creation-sessions/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-detail |
| `/api/instructor/api/v1/creation-sessions/start_wizard` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-start-wizard |
| `/api/instructor/api/v1/creation-sessions/start_wizard.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-start-wizard |
| `/api/instructor/api/v1/dashboard` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-list |
| `/api/instructor/api/v1/dashboard.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-list |
| `/api/instructor/api/v1/dashboard/get_config` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-get-config |
| `/api/instructor/api/v1/dashboard/get_config.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-get-config |
| `/api/instructor/api/v1/dashboard/health_check` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-health-check |
| `/api/instructor/api/v1/dashboard/health_check.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-health-check |
| `/api/instructor/api/v1/dashboard/update_config` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-update-config |
| `/api/instructor/api/v1/dashboard/update_config.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-update-config |
| `/api/instructor/api/v1/dnd/sessions/<session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-detail |
| `/api/instructor/api/v1/dnd/sessions/<session_id>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-detail |
| `/api/instructor/api/v1/dnd/sessions/<session_id>/publish` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-publish |
| `/api/instructor/api/v1/dnd/sessions/<session_id>/publish.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-publish |
| `/api/instructor/api/v1/dnd/sessions/start` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-start |
| `/api/instructor/api/v1/dnd/sessions/start.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-start |
| `/api/instructor/api/v1/draft-content` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-list |
| `/api/instructor/api/v1/draft-content.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-list |
| `/api/instructor/api/v1/draft-content/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-detail |
| `/api/instructor/api/v1/draft-content/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-detail |
| `/api/instructor/api/v1/draft-content/<pk>/auto_save` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-auto-save |
| `/api/instructor/api/v1/draft-content/<pk>/auto_save.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-auto-save |
| `/api/instructor/api/v1/draft-content/<pk>/validate_content` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-validate-content |
| `/api/instructor/api/v1/draft-content/<pk>/validate_content.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-validate-content |
| `/api/instructor/api/v1/draft_course_content` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-list |
| `/api/instructor/api/v1/draft_course_content.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-list |
| `/api/instructor/api/v1/draft_course_content/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-detail |
| `/api/instructor/api/v1/draft_course_content/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-detail |
| `/api/instructor/api/v1/draft_course_content/reorder` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-bulk-reorder |
| `/api/instructor/api/v1/draft_course_content/reorder.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-bulk-reorder |
| `/api/instructor/api/v1/lessons` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-list |
| `/api/instructor/api/v1/lessons.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-list |
| `/api/instructor/api/v1/lessons/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-detail |
| `/api/instructor/api/v1/lessons/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-detail |
| `/api/instructor/api/v1/modules` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-list |
| `/api/instructor/api/v1/modules.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-list |
| `/api/instructor/api/v1/modules/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-detail |
| `/api/instructor/api/v1/modules/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-detail |
| `/api/instructor/api/v1/modules/<pk>/lessons/reorder` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-reorder-lessons |
| `/api/instructor/api/v1/modules/<pk>/lessons/reorder.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-reorder-lessons |
| `/api/instructor/api/v1/profile` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-list |
| `/api/instructor/api/v1/profile.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-list |
| `/api/instructor/api/v1/profile/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-detail |
| `/api/instructor/api/v1/profile/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-detail |
| `/api/instructor/api/v1/profile/request_verification` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-request-verification |
| `/api/instructor/api/v1/profile/request_verification.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-request-verification |
| `/api/instructor/api/v1/profile/tier_info` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-tier-info |
| `/api/instructor/api/v1/profile/tier_info.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-tier-info |
| `/api/instructor/api/v1/resources` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-list |
| `/api/instructor/api/v1/resources.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-list |
| `/api/instructor/api/v1/resources/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-detail |
| `/api/instructor/api/v1/resources/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-detail |
| `/api/instructor/api/v1/resources/presigned-url` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-presigned-url |
| `/api/instructor/api/v1/resources/presigned-url.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-presigned-url |
| `/api/instructor/api/v1/resources/upload_complete` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-upload-complete |
| `/api/instructor/api/v1/resources/upload_complete.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-upload-complete |
| `/api/instructor/api/v1/sessions` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-list |
| `/api/instructor/api/v1/sessions.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-list |
| `/api/instructor/api/v1/sessions/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-detail |
| `/api/instructor/api/v1/sessions/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-detail |
| `/api/instructor/api/v1/sessions/start_wizard` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-start-wizard |
| `/api/instructor/api/v1/sessions/start_wizard.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-start-wizard |
| `/api/instructor/api/v1/settings/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-detail |
| `/api/instructor/api/v1/settings/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-detail |
| `/api/instructor/api/v1/settings/notifications` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-notifications |
| `/api/instructor/api/v1/settings/notifications.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-notifications |
| `/api/instructor/api/v1/settings/update_notifications` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-update-notifications |
| `/api/instructor/api/v1/settings/update_notifications.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-update-notifications |
| `/api/instructor/api/v1/templates` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-list |
| `/api/instructor/api/v1/templates.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-list |
| `/api/instructor/api/v1/templates/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-detail |
| `/api/instructor/api/v1/templates/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-detail |
| `/api/instructor/api/v1/templates/<pk>/create_session` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-create-session |
| `/api/instructor/api/v1/templates/<pk>/create_session.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-create-session |
| `/api/instructor/api/v1/templates/preview` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-preview |
| `/api/instructor/api/v1/templates/preview.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-preview |
| `/api/instructor/bulk/export` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | bulk-export |
| `/api/instructor/bulk/import` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | bulk-import |
| `/api/instructor/bulk/status/<uuid:task_id>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | bulk-status |
| `/api/instructor/collaboration` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-list |
| `/api/instructor/collaboration.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-list |
| `/api/instructor/collaboration/invite` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-invite |
| `/api/instructor/collaboration/invite.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-invite |
| `/api/instructor/course-instructors` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-list |
| `/api/instructor/course-instructors.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-list |
| `/api/instructor/course-instructors/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-detail |
| `/api/instructor/course-instructors/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseInstructorViewSet` | course-instructor-detail |
| `/api/instructor/courses` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-list |
| `/api/instructor/courses.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-list |
| `/api/instructor/courses/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-list |
| `/api/instructor/courses/<slug:slug>/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-detail |
| `/api/instructor/courses/<slug:slug>/analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | course-analytics |
| `/api/instructor/courses/<slug:slug>/clone` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-clone |
| `/api/instructor/courses/<slug:slug>/collaborate/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | course-collaborate |
| `/api/instructor/courses/<slug:slug>/collaborate/accept/<uuid:invitation_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | accept-invitation |
| `/api/instructor/courses/<slug:slug>/collaborate/invitations` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseCollaborationViewSet` | collaboration-invitations |
| `/api/instructor/courses/<slug:slug>/edit` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-edit |
| `/api/instructor/courses/<slug:slug>/lessons/<int:lesson_id>/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | lesson-detail |
| `/api/instructor/courses/<slug:slug>/lessons/<int:lesson_id>/resources` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | lesson-resources |
| `/api/instructor/courses/<slug:slug>/modules/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | course-modules |
| `/api/instructor/courses/<slug:slug>/modules/<int:module_id>/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | module-detail |
| `/api/instructor/courses/<slug:slug>/modules/<int:module_id>/lessons` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | module-lessons |
| `/api/instructor/courses/<slug:slug>/modules/<int:module_id>/lessons/reorder` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | lessons-reorder |
| `/api/instructor/courses/<slug:slug>/modules/reorder` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | modules-reorder |
| `/api/instructor/courses/<slug:slug>/publish` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-publish |
| `/api/instructor/courses/<slug:slug>/versions` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-versions |
| `/api/instructor/courses/<slug>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-detail |
| `/api/instructor/courses/<slug>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-detail |
| `/api/instructor/courses/<slug>/clone` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-clone |
| `/api/instructor/courses/<slug>/clone.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-clone |
| `/api/instructor/courses/<slug>/reorder-modules` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-reorder-modules |
| `/api/instructor/courses/<slug>/reorder-modules.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | instructor-course-reorder-modules |
| `/api/instructor/courses/create` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | course-quick-create |
| `/api/instructor/create/ai/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-start |
| `/api/instructor/create/ai/approve/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-approve |
| `/api/instructor/create/ai/refine/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-refine |
| `/api/instructor/create/ai/session/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | ai-session |
| `/api/instructor/create/dnd/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-start |
| `/api/instructor/create/dnd/content/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-content |
| `/api/instructor/create/dnd/reorder/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-reorder |
| `/api/instructor/create/dnd/session/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session |
| `/api/instructor/create/import/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ContentImportViewSet` | import-start |
| `/api/instructor/create/import/process/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ContentImportViewSet` | import-process |
| `/api/instructor/create/import/session/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ContentImportViewSet` | import-status |
| `/api/instructor/create/template/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TemplateBuilderViewSet` | template-list |
| `/api/instructor/create/template/<int:template_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TemplateBuilderViewSet` | template-use |
| `/api/instructor/create/template/session/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TemplateBuilderViewSet` | template-customize |
| `/api/instructor/create/wizard/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseWizardViewSet` | wizard-start |
| `/api/instructor/create/wizard/complete/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseWizardViewSet` | wizard-complete |
| `/api/instructor/create/wizard/resume/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseWizardViewSet` | wizard-resume |
| `/api/instructor/create/wizard/step/<int:step>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseWizardViewSet` | wizard-step |
| `/api/instructor/creation-sessions` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-list |
| `/api/instructor/creation-sessions.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-list |
| `/api/instructor/creation-sessions/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-detail |
| `/api/instructor/creation-sessions/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-detail |
| `/api/instructor/creation-sessions/start_wizard` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-start-wizard |
| `/api/instructor/creation-sessions/start_wizard.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | creation-sessions-start-wizard |
| `/api/instructor/dashboard` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-list |
| `/api/instructor/dashboard.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-list |
| `/api/instructor/dashboard/get_config` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-get-config |
| `/api/instructor/dashboard/get_config.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-get-config |
| `/api/instructor/dashboard/health_check` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-health-check |
| `/api/instructor/dashboard/health_check.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-health-check |
| `/api/instructor/dashboard/update_config` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-update-config |
| `/api/instructor/dashboard/update_config.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | instructor-dashboard-update-config |
| `/api/instructor/dev/clear-cache` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | dev-clear-cache |
| `/api/instructor/dev/mock-ai` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderlViewSet` | dev-mock-ai |
| `/api/instructor/dev/test-creation` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseWizardViewSet` | dev-test-creation |
| `/api/instructor/dnd/sessions/<session_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-detail |
| `/api/instructor/dnd/sessions/<session_id>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-detail |
| `/api/instructor/dnd/sessions/<session_id>/publish` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-publish |
| `/api/instructor/dnd/sessions/<session_id>/publish.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-publish |
| `/api/instructor/dnd/sessions/start` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-start |
| `/api/instructor/dnd/sessions/start.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DragDropBuilderViewSet` | dnd-session-start |
| `/api/instructor/draft-content` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-list |
| `/api/instructor/draft-content.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-list |
| `/api/instructor/draft-content/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-detail |
| `/api/instructor/draft-content/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-detail |
| `/api/instructor/draft-content/<pk>/auto_save` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-auto-save |
| `/api/instructor/draft-content/<pk>/auto_save.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-auto-save |
| `/api/instructor/draft-content/<pk>/validate_content` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-validate-content |
| `/api/instructor/draft-content/<pk>/validate_content.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-content-validate-content |
| `/api/instructor/draft_course_content` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-list |
| `/api/instructor/draft_course_content.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-list |
| `/api/instructor/draft_course_content/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-detail |
| `/api/instructor/draft_course_content/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-detail |
| `/api/instructor/draft_course_content/reorder` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-bulk-reorder |
| `/api/instructor/draft_course_content/reorder.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `DraftCourseContentViewSet` | draft-course-content-bulk-reorder |
| `/api/instructor/drafts/` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-list |
| `/api/instructor/drafts/<uuid:session_id>` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-detail |
| `/api/instructor/drafts/<uuid:session_id>/auto-save` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-auto-save |
| `/api/instructor/drafts/<uuid:session_id>/export` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | draft-export |
| `/api/instructor/health/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | health-check |
| `/api/instructor/health/detailed` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | detailed-health |
| `/api/instructor/lessons` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-list |
| `/api/instructor/lessons.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-list |
| `/api/instructor/lessons/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-detail |
| `/api/instructor/lessons/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorLessonViewSet` | instructor-lesson-detail |
| `/api/instructor/modules` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-list |
| `/api/instructor/modules.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-list |
| `/api/instructor/modules/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-detail |
| `/api/instructor/modules/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-detail |
| `/api/instructor/modules/<pk>/lessons/reorder` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-reorder-lessons |
| `/api/instructor/modules/<pk>/lessons/reorder.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorModuleViewSet` | instructor-module-reorder-lessons |
| `/api/instructor/profile` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-list |
| `/api/instructor/profile.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-list |
| `/api/instructor/profile/` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | profile-detail |
| `/api/instructor/profile/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-detail |
| `/api/instructor/profile/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-detail |
| `/api/instructor/profile/edit` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | profile-edit |
| `/api/instructor/profile/request_verification` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-request-verification |
| `/api/instructor/profile/request_verification.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-request-verification |
| `/api/instructor/profile/tier` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | profile-tier |
| `/api/instructor/profile/tier_info` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-tier-info |
| `/api/instructor/profile/tier_info.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | instructor-profile-tier-info |
| `/api/instructor/profile/verify` | **GET, POST, PUT, PATCH, DELETE** | `InstructorProfileViewSet` | profile-verify |
| `/api/instructor/reports/engagement` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | engagement-report |
| `/api/instructor/reports/export/<str:report_type>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | export-report |
| `/api/instructor/reports/performance` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | performance-report |
| `/api/instructor/reports/revenue` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsViewSet` | revenue-report |
| `/api/instructor/resources` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-list |
| `/api/instructor/resources.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-list |
| `/api/instructor/resources/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-detail |
| `/api/instructor/resources/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-detail |
| `/api/instructor/resources/presigned-url` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-presigned-url |
| `/api/instructor/resources/presigned-url.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-presigned-url |
| `/api/instructor/resources/upload_complete` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-upload-complete |
| `/api/instructor/resources/upload_complete.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | instructor-resource-upload-complete |
| `/api/instructor/sessions` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-list |
| `/api/instructor/sessions.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-list |
| `/api/instructor/sessions/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-detail |
| `/api/instructor/sessions/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-detail |
| `/api/instructor/sessions/start_wizard` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-start-wizard |
| `/api/instructor/sessions/start_wizard.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseCreationSessionViewSet` | course-creation-session-start-wizard |
| `/api/instructor/settings/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | settings-detail |
| `/api/instructor/settings/<pk>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-detail |
| `/api/instructor/settings/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-detail |
| `/api/instructor/settings/dashboard` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardViewSet` | dashboard-settings |
| `/api/instructor/settings/notifications` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | notification-settings |
| `/api/instructor/settings/notifications` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-notifications |
| `/api/instructor/settings/notifications.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-notifications |
| `/api/instructor/settings/update_notifications` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-update-notifications |
| `/api/instructor/settings/update_notifications.<format>/?` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorSettingsViewSet` | instructor-settings-update-notifications |
| `/api/instructor/templates` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-list |
| `/api/instructor/templates.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-list |
| `/api/instructor/templates/` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | template-list |
| `/api/instructor/templates/<int:template_id>` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | template-detail |
| `/api/instructor/templates/<int:template_id>/preview` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | template-preview |
| `/api/instructor/templates/<pk>` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-detail |
| `/api/instructor/templates/<pk>.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-detail |
| `/api/instructor/templates/<pk>/create_session` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-create-session |
| `/api/instructor/templates/<pk>/create_session.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-create-session |
| `/api/instructor/templates/create` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | template-create |
| `/api/instructor/templates/preview` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-preview |
| `/api/instructor/templates/preview.<format>/?` | **GET, POST, PUT, PATCH, DELETE** | `CourseTemplateViewSet` | course-template-preview |
| `/api/instructor/uploads/batch` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | upload-batch |
| `/api/instructor/uploads/complete` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | upload-complete |
| `/api/instructor/uploads/presigned-url` | **GET, POST, PUT, PATCH, DELETE** | `InstructorResourceViewSet` | upload-presigned-url |
| `/api/instructor/utils/check-title` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | check-title |
| `/api/instructor/utils/generate-slug` | **GET, POST, PUT, PATCH, DELETE** | `InstructorCourseViewSet` | generate-slug |
| `/api/instructor/utils/validate-content` | **GET, POST, PUT, PATCH, DELETE** | `DraftCourseContentViewSet` | validate-content |

## Web Endpoints

### Main Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `//api/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `//api/<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `//api/instructor/ai-course-builder/health` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `AICourseBuilderHealthView` | ai-course-builder-health |
| `/api//` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api//<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/debug/courses` | **GET** | `debug_courses` | api-debug-courses |
| `/api/statistics/instructor` | **GET** | `instructor_statistics` | instructor-statistics |
| `/api/statistics/platform` | **GET** | `platform_statistics` | platform-statistics |
| `/api/statistics/user/learning` | **GET** | `user_learning_statistics` | user-learning-statistics |
| `/api/system/db-stats` | **GET** | `db_stats` | db-stats |
| `/api/system/db-status` | **GET** | `db_status` | db-status |
| `/api/testimonials/featured` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `FeaturedTestimonialsView` | featured-testimonials |
| `/api/token` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TokenObtainPairView` | token_obtain_pair |
| `/api/token/refresh` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TokenRefreshView` | token_refresh |
| `/api/user//` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/user//<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/user/email/verify` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `EmailVerificationView` | email-verify |
| `/api/user/email/verify/resend` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ResendVerificationView` | email-verify-resend |
| `/api/user/login` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LoginView` | login |
| `/api/user/logout` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LogoutView` | logout |
| `/api/user/me` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserView` | user-detail |
| `/api/user/password/change` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `PasswordChangeView` | password-change |
| `/api/user/password/reset` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `PasswordResetRequestView` | password-reset-request |
| `/api/user/password/reset/confirm` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `PasswordResetConfirmView` | password-reset-confirm |
| `/api/user/profile` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `ProfileView` | user-profile |
| `/api/user/profile/comprehensive` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UpdateProfileView` | profile-comprehensive |
| `/api/user/register` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RegisterView` | register |
| `/api/user/social/complete` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SocialAuthCompleteView` | social-complete |
| `/api/user/social/error` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SocialAuthErrorView` | social-error |
| `/api/user/social/github` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SocialAuthGithubView` | social-github |
| `/api/user/social/google` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `SocialAuthGoogleView` | social-google |
| `/api/user/token` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TokenObtainPairView` | token_obtain_pair |
| `/api/user/token/refresh` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `TokenRefreshView` | token_refresh |
| `/instructor/debug/courses` | **GET** | `debug_courses` | debug-courses-direct |
| `/instructor/debug/courses/simple` | **GET** | `debug_courses` | debug-courses-simple |
| `/media/<path>` | **GET** | `serve` | unnamed |
| `/static/<path>` | **GET** | `serve` | unnamed |
| `/test-admin-static` | **GET** | `test_admin_static` | test-admin-static |
| `/test-static` | **GET** | `test_static` | test-static |

### Admin Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/admin/` | **GET** | `index` | index |
| `/admin/<app_label>` | **GET** | `app_index` | app_list |
| `/admin/<url>` | **GET** | `catch_all_view` | unnamed |
| `/admin/account/emailaddress/` | **GET** | `changelist_view` | account_emailaddress_changelist |
| `/admin/account/emailaddress/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/account/emailaddress/<path:object_id>/change` | **GET** | `change_view` | account_emailaddress_change |
| `/admin/account/emailaddress/<path:object_id>/delete` | **GET** | `delete_view` | account_emailaddress_delete |
| `/admin/account/emailaddress/<path:object_id>/history` | **GET** | `history_view` | account_emailaddress_history |
| `/admin/account/emailaddress/add` | **GET** | `add_view` | account_emailaddress_add |
| `/admin/auth/group/` | **GET** | `changelist_view` | auth_group_changelist |
| `/admin/auth/group/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/auth/group/<path:object_id>/change` | **GET** | `change_view` | auth_group_change |
| `/admin/auth/group/<path:object_id>/delete` | **GET** | `delete_view` | auth_group_delete |
| `/admin/auth/group/<path:object_id>/history` | **GET** | `history_view` | auth_group_history |
| `/admin/auth/group/add` | **GET** | `add_view` | auth_group_add |
| `/admin/autocomplete` | **GET** | `autocomplete_view` | autocomplete |
| `/admin/content/instructorstatistics/` | **GET** | `changelist_view` | content_instructorstatistics_changelist |
| `/admin/content/instructorstatistics/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/content/instructorstatistics/<path:object_id>/change` | **GET** | `change_view` | content_instructorstatistics_change |
| `/admin/content/instructorstatistics/<path:object_id>/delete` | **GET** | `delete_view` | content_instructorstatistics_delete |
| `/admin/content/instructorstatistics/<path:object_id>/history` | **GET** | `history_view` | content_instructorstatistics_history |
| `/admin/content/instructorstatistics/add` | **GET** | `add_view` | content_instructorstatistics_add |
| `/admin/content/platformstatistics/` | **GET** | `changelist_view` | content_platformstatistics_changelist |
| `/admin/content/platformstatistics/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/content/platformstatistics/<path:object_id>/change` | **GET** | `change_view` | content_platformstatistics_change |
| `/admin/content/platformstatistics/<path:object_id>/delete` | **GET** | `delete_view` | content_platformstatistics_delete |
| `/admin/content/platformstatistics/<path:object_id>/history` | **GET** | `history_view` | content_platformstatistics_history |
| `/admin/content/platformstatistics/add` | **GET** | `add_view` | content_platformstatistics_add |
| `/admin/content/testimonial/` | **GET** | `changelist_view` | content_testimonial_changelist |
| `/admin/content/testimonial/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/content/testimonial/<path:object_id>/change` | **GET** | `change_view` | content_testimonial_change |
| `/admin/content/testimonial/<path:object_id>/delete` | **GET** | `delete_view` | content_testimonial_delete |
| `/admin/content/testimonial/<path:object_id>/history` | **GET** | `history_view` | content_testimonial_history |
| `/admin/content/testimonial/add` | **GET** | `add_view` | content_testimonial_add |
| `/admin/content/userlearningstatistics/` | **GET** | `changelist_view` | content_userlearningstatistics_changelist |
| `/admin/content/userlearningstatistics/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/content/userlearningstatistics/<path:object_id>/change` | **GET** | `change_view` | content_userlearningstatistics_change |
| `/admin/content/userlearningstatistics/<path:object_id>/delete` | **GET** | `delete_view` | content_userlearningstatistics_delete |
| `/admin/content/userlearningstatistics/<path:object_id>/history` | **GET** | `history_view` | content_userlearningstatistics_history |
| `/admin/content/userlearningstatistics/add` | **GET** | `add_view` | content_userlearningstatistics_add |
| `/admin/courses/category/` | **GET** | `changelist_view` | courses_category_changelist |
| `/admin/courses/category/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/category/<path:object_id>/change` | **GET** | `change_view` | courses_category_change |
| `/admin/courses/category/<path:object_id>/delete` | **GET** | `delete_view` | courses_category_delete |
| `/admin/courses/category/<path:object_id>/history` | **GET** | `history_view` | courses_category_history |
| `/admin/courses/category/add` | **GET** | `add_view` | courses_category_add |
| `/admin/courses/course/` | **GET** | `changelist_view` | courses_course_changelist |
| `/admin/courses/course/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/course/<path:object_id>/change` | **GET** | `change_view` | courses_course_change |
| `/admin/courses/course/<path:object_id>/delete` | **GET** | `delete_view` | courses_course_delete |
| `/admin/courses/course/<path:object_id>/history` | **GET** | `history_view` | courses_course_history |
| `/admin/courses/course/add` | **GET** | `add_view` | courses_course_add |
| `/admin/courses/enrollment/` | **GET** | `changelist_view` | courses_enrollment_changelist |
| `/admin/courses/enrollment/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/enrollment/<path:object_id>/change` | **GET** | `change_view` | courses_enrollment_change |
| `/admin/courses/enrollment/<path:object_id>/delete` | **GET** | `delete_view` | courses_enrollment_delete |
| `/admin/courses/enrollment/<path:object_id>/history` | **GET** | `history_view` | courses_enrollment_history |
| `/admin/courses/enrollment/add` | **GET** | `add_view` | courses_enrollment_add |
| `/admin/courses/lesson/` | **GET** | `changelist_view` | courses_lesson_changelist |
| `/admin/courses/lesson/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/lesson/<path:object_id>/change` | **GET** | `change_view` | courses_lesson_change |
| `/admin/courses/lesson/<path:object_id>/delete` | **GET** | `delete_view` | courses_lesson_delete |
| `/admin/courses/lesson/<path:object_id>/history` | **GET** | `history_view` | courses_lesson_history |
| `/admin/courses/lesson/add` | **GET** | `add_view` | courses_lesson_add |
| `/admin/courses/module/` | **GET** | `changelist_view` | courses_module_changelist |
| `/admin/courses/module/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/module/<path:object_id>/change` | **GET** | `change_view` | courses_module_change |
| `/admin/courses/module/<path:object_id>/delete` | **GET** | `delete_view` | courses_module_delete |
| `/admin/courses/module/<path:object_id>/history` | **GET** | `history_view` | courses_module_history |
| `/admin/courses/module/add` | **GET** | `add_view` | courses_module_add |
| `/admin/courses/resource/` | **GET** | `changelist_view` | courses_resource_changelist |
| `/admin/courses/resource/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/courses/resource/<path:object_id>/change` | **GET** | `change_view` | courses_resource_change |
| `/admin/courses/resource/<path:object_id>/delete` | **GET** | `delete_view` | courses_resource_delete |
| `/admin/courses/resource/<path:object_id>/history` | **GET** | `history_view` | courses_resource_history |
| `/admin/courses/resource/add` | **GET** | `add_view` | courses_resource_add |
| `/admin/django_celery_beat/clockedschedule/` | **GET** | `changelist_view` | django_celery_beat_clockedschedule_changelist |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/change` | **GET** | `change_view` | django_celery_beat_clockedschedule_change |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/delete` | **GET** | `delete_view` | django_celery_beat_clockedschedule_delete |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/history` | **GET** | `history_view` | django_celery_beat_clockedschedule_history |
| `/admin/django_celery_beat/clockedschedule/add` | **GET** | `add_view` | django_celery_beat_clockedschedule_add |
| `/admin/django_celery_beat/crontabschedule/` | **GET** | `changelist_view` | django_celery_beat_crontabschedule_changelist |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/change` | **GET** | `change_view` | django_celery_beat_crontabschedule_change |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/delete` | **GET** | `delete_view` | django_celery_beat_crontabschedule_delete |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/history` | **GET** | `history_view` | django_celery_beat_crontabschedule_history |
| `/admin/django_celery_beat/crontabschedule/add` | **GET** | `add_view` | django_celery_beat_crontabschedule_add |
| `/admin/django_celery_beat/intervalschedule/` | **GET** | `changelist_view` | django_celery_beat_intervalschedule_changelist |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/change` | **GET** | `change_view` | django_celery_beat_intervalschedule_change |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/delete` | **GET** | `delete_view` | django_celery_beat_intervalschedule_delete |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/history` | **GET** | `history_view` | django_celery_beat_intervalschedule_history |
| `/admin/django_celery_beat/intervalschedule/add` | **GET** | `add_view` | django_celery_beat_intervalschedule_add |
| `/admin/django_celery_beat/periodictask/` | **GET** | `changelist_view` | django_celery_beat_periodictask_changelist |
| `/admin/django_celery_beat/periodictask/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/django_celery_beat/periodictask/<path:object_id>/change` | **GET** | `change_view` | django_celery_beat_periodictask_change |
| `/admin/django_celery_beat/periodictask/<path:object_id>/delete` | **GET** | `delete_view` | django_celery_beat_periodictask_delete |
| `/admin/django_celery_beat/periodictask/<path:object_id>/history` | **GET** | `history_view` | django_celery_beat_periodictask_history |
| `/admin/django_celery_beat/periodictask/add` | **GET** | `add_view` | django_celery_beat_periodictask_add |
| `/admin/django_celery_beat/solarschedule/` | **GET** | `changelist_view` | django_celery_beat_solarschedule_changelist |
| `/admin/django_celery_beat/solarschedule/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/change` | **GET** | `change_view` | django_celery_beat_solarschedule_change |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/delete` | **GET** | `delete_view` | django_celery_beat_solarschedule_delete |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/history` | **GET** | `history_view` | django_celery_beat_solarschedule_history |
| `/admin/django_celery_beat/solarschedule/add` | **GET** | `add_view` | django_celery_beat_solarschedule_add |
| `/admin/instructor_portal/coursecontentdraft/` | **GET** | `changelist_view` | instructor_portal_coursecontentdraft_changelist |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_coursecontentdraft_change |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_coursecontentdraft_delete |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_coursecontentdraft_history |
| `/admin/instructor_portal/coursecontentdraft/add` | **GET** | `add_view` | instructor_portal_coursecontentdraft_add |
| `/admin/instructor_portal/coursecreationsession/` | **GET** | `changelist_view` | instructor_portal_coursecreationsession_changelist |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_coursecreationsession_change |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_coursecreationsession_delete |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_coursecreationsession_history |
| `/admin/instructor_portal/coursecreationsession/add` | **GET** | `add_view` | instructor_portal_coursecreationsession_add |
| `/admin/instructor_portal/courseinstructor/` | **GET** | `changelist_view` | instructor_portal_courseinstructor_changelist |
| `/admin/instructor_portal/courseinstructor/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_courseinstructor_change |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_courseinstructor_delete |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_courseinstructor_history |
| `/admin/instructor_portal/courseinstructor/add` | **GET** | `add_view` | instructor_portal_courseinstructor_add |
| `/admin/instructor_portal/coursetemplate/` | **GET** | `changelist_view` | instructor_portal_coursetemplate_changelist |
| `/admin/instructor_portal/coursetemplate/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_coursetemplate_change |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_coursetemplate_delete |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_coursetemplate_history |
| `/admin/instructor_portal/coursetemplate/add` | **GET** | `add_view` | instructor_portal_coursetemplate_add |
| `/admin/instructor_portal/draftcoursecontent/` | **GET** | `changelist_view` | instructor_portal_draftcoursecontent_changelist |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_draftcoursecontent_change |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_draftcoursecontent_delete |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_draftcoursecontent_history |
| `/admin/instructor_portal/draftcoursecontent/add` | **GET** | `add_view` | instructor_portal_draftcoursecontent_add |
| `/admin/instructor_portal/instructoranalytics/` | **GET** | `changelist_view` | instructor_portal_instructoranalytics_changelist |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructoranalytics_change |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructoranalytics_delete |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructoranalytics_history |
| `/admin/instructor_portal/instructoranalytics/add` | **GET** | `add_view` | instructor_portal_instructoranalytics_add |
| `/admin/instructor_portal/instructoranalyticshistory/` | **GET** | `changelist_view` | instructor_portal_instructoranalyticshistory_changelist |
| `/admin/instructor_portal/instructoranalyticshistory/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructoranalyticshistory/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructoranalyticshistory_change |
| `/admin/instructor_portal/instructoranalyticshistory/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructoranalyticshistory_delete |
| `/admin/instructor_portal/instructoranalyticshistory/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructoranalyticshistory_history |
| `/admin/instructor_portal/instructoranalyticshistory/add` | **GET** | `add_view` | instructor_portal_instructoranalyticshistory_add |
| `/admin/instructor_portal/instructordashboard/` | **GET** | `changelist_view` | instructor_portal_instructordashboard_changelist |
| `/admin/instructor_portal/instructordashboard/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructordashboard_change |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructordashboard_delete |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructordashboard_history |
| `/admin/instructor_portal/instructordashboard/add` | **GET** | `add_view` | instructor_portal_instructordashboard_add |
| `/admin/instructor_portal/instructornotification/` | **GET** | `changelist_view` | instructor_portal_instructornotification_changelist |
| `/admin/instructor_portal/instructornotification/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructornotification/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructornotification_change |
| `/admin/instructor_portal/instructornotification/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructornotification_delete |
| `/admin/instructor_portal/instructornotification/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructornotification_history |
| `/admin/instructor_portal/instructornotification/add` | **GET** | `add_view` | instructor_portal_instructornotification_add |
| `/admin/instructor_portal/instructorprofile/` | **GET** | `changelist_view` | instructor_portal_instructorprofile_changelist |
| `/admin/instructor_portal/instructorprofile/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructorprofile_change |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructorprofile_delete |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructorprofile_history |
| `/admin/instructor_portal/instructorprofile/add` | **GET** | `add_view` | instructor_portal_instructorprofile_add |
| `/admin/instructor_portal/instructorsession/` | **GET** | `changelist_view` | instructor_portal_instructorsession_changelist |
| `/admin/instructor_portal/instructorsession/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/instructor_portal/instructorsession/<path:object_id>/change` | **GET** | `change_view` | instructor_portal_instructorsession_change |
| `/admin/instructor_portal/instructorsession/<path:object_id>/delete` | **GET** | `delete_view` | instructor_portal_instructorsession_delete |
| `/admin/instructor_portal/instructorsession/<path:object_id>/history` | **GET** | `history_view` | instructor_portal_instructorsession_history |
| `/admin/instructor_portal/instructorsession/add` | **GET** | `add_view` | instructor_portal_instructorsession_add |
| `/admin/jsi18n` | **GET** | `i18n_javascript` | jsi18n |
| `/admin/login` | **GET** | `login` | login |
| `/admin/logout` | **GET** | `logout` | logout |
| `/admin/password_change` | **GET** | `password_change` | password_change |
| `/admin/password_change/done` | **GET** | `password_change_done` | password_change_done |
| `/admin/r/<path:content_type_id>/<path:object_id>` | **GET** | `shortcut` | view_on_site |
| `/admin/sites/site/` | **GET** | `changelist_view` | sites_site_changelist |
| `/admin/sites/site/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/sites/site/<path:object_id>/change` | **GET** | `change_view` | sites_site_change |
| `/admin/sites/site/<path:object_id>/delete` | **GET** | `delete_view` | sites_site_delete |
| `/admin/sites/site/<path:object_id>/history` | **GET** | `history_view` | sites_site_history |
| `/admin/sites/site/add` | **GET** | `add_view` | sites_site_add |
| `/admin/social_django/association/` | **GET** | `changelist_view` | social_django_association_changelist |
| `/admin/social_django/association/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/social_django/association/<path:object_id>/change` | **GET** | `change_view` | social_django_association_change |
| `/admin/social_django/association/<path:object_id>/delete` | **GET** | `delete_view` | social_django_association_delete |
| `/admin/social_django/association/<path:object_id>/history` | **GET** | `history_view` | social_django_association_history |
| `/admin/social_django/association/add` | **GET** | `add_view` | social_django_association_add |
| `/admin/social_django/nonce/` | **GET** | `changelist_view` | social_django_nonce_changelist |
| `/admin/social_django/nonce/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/social_django/nonce/<path:object_id>/change` | **GET** | `change_view` | social_django_nonce_change |
| `/admin/social_django/nonce/<path:object_id>/delete` | **GET** | `delete_view` | social_django_nonce_delete |
| `/admin/social_django/nonce/<path:object_id>/history` | **GET** | `history_view` | social_django_nonce_history |
| `/admin/social_django/nonce/add` | **GET** | `add_view` | social_django_nonce_add |
| `/admin/social_django/usersocialauth/` | **GET** | `changelist_view` | social_django_usersocialauth_changelist |
| `/admin/social_django/usersocialauth/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/social_django/usersocialauth/<path:object_id>/change` | **GET** | `change_view` | social_django_usersocialauth_change |
| `/admin/social_django/usersocialauth/<path:object_id>/delete` | **GET** | `delete_view` | social_django_usersocialauth_delete |
| `/admin/social_django/usersocialauth/<path:object_id>/history` | **GET** | `history_view` | social_django_usersocialauth_history |
| `/admin/social_django/usersocialauth/add` | **GET** | `add_view` | social_django_usersocialauth_add |
| `/admin/socialaccount/socialaccount/` | **GET** | `changelist_view` | socialaccount_socialaccount_changelist |
| `/admin/socialaccount/socialaccount/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/socialaccount/socialaccount/<path:object_id>/change` | **GET** | `change_view` | socialaccount_socialaccount_change |
| `/admin/socialaccount/socialaccount/<path:object_id>/delete` | **GET** | `delete_view` | socialaccount_socialaccount_delete |
| `/admin/socialaccount/socialaccount/<path:object_id>/history` | **GET** | `history_view` | socialaccount_socialaccount_history |
| `/admin/socialaccount/socialaccount/add` | **GET** | `add_view` | socialaccount_socialaccount_add |
| `/admin/socialaccount/socialapp/` | **GET** | `changelist_view` | socialaccount_socialapp_changelist |
| `/admin/socialaccount/socialapp/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/socialaccount/socialapp/<path:object_id>/change` | **GET** | `change_view` | socialaccount_socialapp_change |
| `/admin/socialaccount/socialapp/<path:object_id>/delete` | **GET** | `delete_view` | socialaccount_socialapp_delete |
| `/admin/socialaccount/socialapp/<path:object_id>/history` | **GET** | `history_view` | socialaccount_socialapp_history |
| `/admin/socialaccount/socialapp/add` | **GET** | `add_view` | socialaccount_socialapp_add |
| `/admin/socialaccount/socialtoken/` | **GET** | `changelist_view` | socialaccount_socialtoken_changelist |
| `/admin/socialaccount/socialtoken/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/socialaccount/socialtoken/<path:object_id>/change` | **GET** | `change_view` | socialaccount_socialtoken_change |
| `/admin/socialaccount/socialtoken/<path:object_id>/delete` | **GET** | `delete_view` | socialaccount_socialtoken_delete |
| `/admin/socialaccount/socialtoken/<path:object_id>/history` | **GET** | `history_view` | socialaccount_socialtoken_history |
| `/admin/socialaccount/socialtoken/add` | **GET** | `add_view` | socialaccount_socialtoken_add |
| `/admin/token_blacklist/blacklistedtoken/` | **GET** | `changelist_view` | token_blacklist_blacklistedtoken_changelist |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/change` | **GET** | `change_view` | token_blacklist_blacklistedtoken_change |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/delete` | **GET** | `delete_view` | token_blacklist_blacklistedtoken_delete |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/history` | **GET** | `history_view` | token_blacklist_blacklistedtoken_history |
| `/admin/token_blacklist/blacklistedtoken/add` | **GET** | `add_view` | token_blacklist_blacklistedtoken_add |
| `/admin/token_blacklist/outstandingtoken/` | **GET** | `changelist_view` | token_blacklist_outstandingtoken_changelist |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/change` | **GET** | `change_view` | token_blacklist_outstandingtoken_change |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/delete` | **GET** | `delete_view` | token_blacklist_outstandingtoken_delete |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/history` | **GET** | `history_view` | token_blacklist_outstandingtoken_history |
| `/admin/token_blacklist/outstandingtoken/add` | **GET** | `add_view` | token_blacklist_outstandingtoken_add |
| `/admin/users/customuser/` | **GET** | `changelist_view` | users_customuser_changelist |
| `/admin/users/customuser/<id>/password` | **GET** | `user_change_password` | auth_user_password_change |
| `/admin/users/customuser/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/users/customuser/<path:object_id>/change` | **GET** | `change_view` | users_customuser_change |
| `/admin/users/customuser/<path:object_id>/delete` | **GET** | `delete_view` | users_customuser_delete |
| `/admin/users/customuser/<path:object_id>/history` | **GET** | `history_view` | users_customuser_history |
| `/admin/users/customuser/add` | **GET** | `add_view` | users_customuser_add |
| `/admin/users/emailverification/` | **GET** | `changelist_view` | users_emailverification_changelist |
| `/admin/users/emailverification/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/users/emailverification/<path:object_id>/change` | **GET** | `change_view` | users_emailverification_change |
| `/admin/users/emailverification/<path:object_id>/delete` | **GET** | `delete_view` | users_emailverification_delete |
| `/admin/users/emailverification/<path:object_id>/history` | **GET** | `history_view` | users_emailverification_history |
| `/admin/users/emailverification/add` | **GET** | `add_view` | users_emailverification_add |
| `/admin/users/loginlog/` | **GET** | `changelist_view` | users_loginlog_changelist |
| `/admin/users/loginlog/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/users/loginlog/<path:object_id>/change` | **GET** | `change_view` | users_loginlog_change |
| `/admin/users/loginlog/<path:object_id>/delete` | **GET** | `delete_view` | users_loginlog_delete |
| `/admin/users/loginlog/<path:object_id>/history` | **GET** | `history_view` | users_loginlog_history |
| `/admin/users/loginlog/add` | **GET** | `add_view` | users_loginlog_add |
| `/admin/users/passwordreset/` | **GET** | `changelist_view` | users_passwordreset_changelist |
| `/admin/users/passwordreset/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/users/passwordreset/<path:object_id>/change` | **GET** | `change_view` | users_passwordreset_change |
| `/admin/users/passwordreset/<path:object_id>/delete` | **GET** | `delete_view` | users_passwordreset_delete |
| `/admin/users/passwordreset/<path:object_id>/history` | **GET** | `history_view` | users_passwordreset_history |
| `/admin/users/passwordreset/add` | **GET** | `add_view` | users_passwordreset_add |
| `/admin/users/usersession/` | **GET** | `changelist_view` | users_usersession_changelist |
| `/admin/users/usersession/<path:object_id>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RedirectView` | unnamed |
| `/admin/users/usersession/<path:object_id>/change` | **GET** | `change_view` | users_usersession_change |
| `/admin/users/usersession/<path:object_id>/delete` | **GET** | `delete_view` | users_usersession_delete |
| `/admin/users/usersession/<path:object_id>/history` | **GET** | `history_view` | users_usersession_history |
| `/admin/users/usersession/add` | **GET** | `add_view` | users_usersession_add |

### Courses Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api//` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api//<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/certificates/verify/<certificate_number>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CertificateVerificationView` | verify-certificate |
| `/api/courses/<course_slug>/enrollment` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseEnrollmentView` | course-enrollment |
| `/api/courses/<course_slug>/progress` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseProgressView` | course-progress |
| `/api/debug/cache-stats` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CacheStatsView` | debug-cache-stats |
| `/api/debug/url-patterns` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `URLPatternsView` | debug-url-patterns |
| `/api/featured` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `FeaturedContentView` | featured |
| `/api/health` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIHealthCheckView` | api-health-check |
| `/api/instructor/courses/<course_slug>/analytics` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `CourseAnalyticsView` | course-analytics |
| `/api/instructor/dashboard` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardView` | instructor-dashboard |
| `/api/search` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UnifiedSearchView` | search |
| `/api/user/progress/stats` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `UserProgressStatsView` | user-progress-stats |
| `/api/version` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIVersionView` | api-version |

### Djdt Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/__debug__/history_refresh` | **GET** | `history_refresh` | history_refresh |
| `/__debug__/history_sidebar` | **GET** | `history_sidebar` | history_sidebar |
| `/__debug__/render_panel` | **GET** | `render_panel` | render_panel |
| `/__debug__/sql_explain` | **GET** | `sql_explain` | sql_explain |
| `/__debug__/sql_profile` | **GET** | `sql_profile` | sql_profile |
| `/__debug__/sql_select` | **GET** | `sql_select` | sql_select |
| `/__debug__/template_source` | **GET** | `template_source` | template_source |

### Instructor_Portal Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/instructor/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/instructor/<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/instructor/analytics/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorAnalyticsView` | instructor-analytics |
| `/api/instructor/analytics/reports` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorReportsView` | instructor-reports |
| `/api/instructor/analytics/revenue` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `RevenueAnalyticsView` | revenue-analytics |
| `/api/instructor/api/v1/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/instructor/api/v1/<drf_format_suffix:format>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `APIRootView` | api-root |
| `/api/instructor/auth/approval` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorApprovalView` | instructor-approval |
| `/api/instructor/auth/register` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorRegistrationView` | instructor-register |
| `/api/instructor/auth/status` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorStatusView` | instructor-status |
| `/api/instructor/auth/verify/<uuid:verification_token>` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorVerificationView` | instructor-verify |
| `/api/instructor/create/` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardView` | course-create |
| `/api/instructor/dashboard` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `InstructorDashboardView` | instructor-dashboard |
| `/api/instructor/debug/courses` | **GET** | `debug_courses` | debug-courses |
| `/api/instructor/debug/courses/simple` | **GET** | `debug_courses` | debug-courses-simple |
| `/api/instructor/debug/diagnostic` | **GET** | `debug_courses` | debug-diagnostic |
| `/api/instructor/students` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `StudentManagementView` | student-management |

### Rest_Framework Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api-auth/login` | **GET, POST, PUT, PATCH, DELETE, TRACE** | `LoginView` | login |
| `/api-auth/logout` | **POST** | `LogoutView` | logout |

### Social Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/user/social-auth/complete/<str:backend>` | **GET** | `complete` | complete |
| `/api/user/social-auth/disconnect/<str:backend>` | **GET** | `disconnect` | disconnect |
| `/api/user/social-auth/disconnect/<str:backend>/<int:association_id>` | **GET** | `disconnect` | disconnect_individual |
| `/api/user/social-auth/login/<str:backend>` | **GET** | `auth` | begin |

## 📊 Analysis

### HTTP Methods Distribution

- **DELETE**: 462 endpoints
- **GET**: 709 endpoints
- **PATCH**: 462 endpoints
- **POST**: 463 endpoints
- **PUT**: 462 endpoints
- **TRACE**: 295 endpoints

### View Types

- **Class-based Views**: 463 endpoints
- **Function-based Views**: 247 endpoints

### Namespace Distribution

- **Main**: 69 endpoints
- **admin**: 263 endpoints
- **courses**: 64 endpoints
- **djdt**: 7 endpoints
- **instructor_portal**: 301 endpoints
- **rest_framework**: 2 endpoints
- **social**: 4 endpoints


---

*Generated by Enhanced Django Endpoints Extractor*
