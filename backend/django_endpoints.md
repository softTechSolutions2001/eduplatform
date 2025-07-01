# 🚀 Django Project Endpoints

**Generated on:** 2025-06-30 15:49:09

**Total endpoints:** 306

**API endpoints:** 79
**Web endpoints:** 227

---

## API Endpoints

### Main API Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api` | **🟢 GET** | `APIRootView` | api-root |
| `/api/instructor/ai-course-builder` | **🟢 GET** | `AICourseBuilderDraftViewSet` | ai-course-builder-list |
| `/api/instructor/ai-course-builder/<pk>` | **🟢 GET** | `AICourseBuilderDraftViewSet` | ai-course-builder-detail |
| `/api/instructor/ai-course-builder/<pk>/finalize` | **🟢 GET** | `AICourseBuilderDraftViewSet` | ai-course-builder-finalize |
| `/api/instructor/ai-course-builder/<pk>/task-status/<task_id>` | **🟢 GET** | `AICourseBuilderDraftViewSet` | ai-course-builder-task-status |
| `/api/instructor/ai-course-builder/health` | **🟢 GET** | `AICourseBuilderHealthView` | ai-course-builder-health |
| `/api/instructor/ai-course-builder/initialize` | **🟢 GET** | `AICourseBuilderDraftViewSet` | ai-course-builder-initialize |
| `/api/statistics/instructor` | **🟢 GET** | `instructor_statistics` | instructor-statistics |
| `/api/statistics/platform` | **🟢 GET** | `platform_statistics` | platform-statistics |
| `/api/statistics/user/learning` | **🟢 GET** | `user_learning_statistics` | user-learning-statistics |
| `/api/system/db-stats` | **🟢 GET** | `db_stats` | db-stats |
| `/api/system/db-status` | **🟢 GET** | `db_status` | db-status |
| `/api/testimonials` | **🟢 GET** | `TestimonialViewSet` | testimonial-list |
| `/api/testimonials/<pk>` | **🟢 GET** | `TestimonialViewSet` | testimonial-detail |
| `/api/testimonials/featured` | **🟢 GET** | `FeaturedTestimonialsView` | featured-testimonials |
| `/api/token` | **🔵 POST** | `TokenObtainPairView` | token_obtain_pair |
| `/api/token/refresh` | **🔵 POST** | `TokenRefreshView` | token_refresh |
| `/api/user` | **🟢 GET** | `APIRootView` | api-root |
| `/api/user/email/verify` | **🔵 POST** | `EmailVerificationView` | email-verify |
| `/api/user/email/verify/resend` | **🔵 POST** | `ResendVerificationView` | email-verify-resend |
| `/api/user/login` | **🔵 POST** | `LoginView` | login |
| `/api/user/logout` | **🔵 POST** | `LogoutView` | logout |
| `/api/user/me` | 🟢 GET / 🟠 PATCH / 🟡 PUT | `UserView` | user-detail |
| `/api/user/password/change` | **🔵 POST** | `PasswordChangeView` | password-change |
| `/api/user/password/reset` | **🔵 POST** | `PasswordResetRequestView` | password-reset-request |
| `/api/user/password/reset/confirm` | **🔵 POST** | `PasswordResetConfirmView` | password-reset-confirm |
| `/api/user/profile` | 🟢 GET / 🟠 PATCH / 🟡 PUT | `ProfileView` | user-profile |
| `/api/user/profile/comprehensive` | **🟡 PUT** | `UpdateProfileView` | profile-comprehensive |
| `/api/user/register` | **🔵 POST** | `RegisterView` | register |
| `/api/user/sessions` | **🟢 GET** | `UserSessionViewSet` | user-sessions-list |
| `/api/user/sessions/<pk>` | **🟢 GET** | `UserSessionViewSet` | user-sessions-detail |
| `/api/user/social/complete` | **🔵 POST** | `SocialAuthCompleteView` | social-complete |
| `/api/user/social/error` | **🟢 GET** | `SocialAuthErrorView` | social-error |
| `/api/user/social/github` | **🟢 GET** | `SocialAuthGithubView` | social-github |
| `/api/user/social/google` | **🟢 GET** | `SocialAuthGoogleView` | social-google |
| `/api/user/subscription` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-list |
| `/api/user/subscription/<pk>` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-detail |
| `/api/user/subscription/cancel` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-cancel |
| `/api/user/subscription/current` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-current |
| `/api/user/subscription/downgrade` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-downgrade |
| `/api/user/subscription/upgrade` | **🟢 GET** | `SubscriptionViewSet` | user-subscription-upgrade |
| `/api/user/token` | **🔵 POST** | `TokenObtainPairView` | token_obtain_pair |
| `/api/user/token/refresh` | **🔵 POST** | `TokenRefreshView` | token_refresh |

### Courses API Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/categories` | **🟢 GET** | `CategoryViewSet` | category-list |
| `/api/categories/<slug>` | **🟢 GET** | `CategoryViewSet` | category-detail |
| `/api/certificates` | **🟢 GET** | `CertificateViewSet` | certificate-list |
| `/api/certificates/<pk>` | **🟢 GET** | `CertificateViewSet` | certificate-detail |
| `/api/certificates/verify/<slug>` | **🟢 GET** | `CertificateVerificationView` | verify-certificate |
| `/api/courses` | **🟢 GET** | `CourseViewSet` | course-list |
| `/api/courses/<slug>` | **🟢 GET** | `CourseViewSet` | course-detail |
| `/api/courses/<slug>/clone` | **🟢 GET** | `CourseViewSet` | course-clone |
| `/api/courses/<slug>/enroll` | **🟢 GET** | `CourseViewSet` | course-enroll |
| `/api/courses/<slug>/enrollment` | **🔵 POST** | `CourseEnrollmentView` | course-enrollment |
| `/api/courses/<slug>/progress` | **🟢 GET** | `CourseProgressView` | course-progress |
| `/api/courses/<slug>/versions` | **🟢 GET** | `CourseViewSet` | course-versions |
| `/api/courses/featured` | **🟢 GET** | `CourseViewSet` | course-featured |
| `/api/debug/cache-stats` | **🟢 GET** | `CacheStatsView` | debug-cache-stats |
| `/api/debug/url-patterns` | **🟢 GET** | `URLPatternsView` | debug-url-patterns |
| `/api/enrollments` | **🟢 GET** | `EnrollmentViewSet` | enrollment-list |
| `/api/enrollments/<pk>` | **🟢 GET** | `EnrollmentViewSet` | enrollment-detail |
| `/api/enrollments/<pk>/unenroll` | **🟢 GET** | `EnrollmentViewSet` | enrollment-unenroll |
| `/api/featured` | **🟢 GET** | `FeaturedContentView` | featured |
| `/api/health` | **🟢 GET** | `APIHealthCheckView` | api-health-check |
| `/api/instructor/courses/<slug>/analytics` | **🟢 GET** | `CourseAnalyticsView` | course-analytics |
| `/api/instructor/dashboard` | **🟢 GET** | `InstructorDashboardView` | instructor-dashboard |
| `/api/lessons` | **🟢 GET** | `LessonViewSet` | lesson-list |
| `/api/lessons/<pk>` | **🟢 GET** | `LessonViewSet` | lesson-detail |
| `/api/modules` | **🟢 GET** | `ModuleViewSet` | module-list |
| `/api/modules/<pk>` | **🟢 GET** | `ModuleViewSet` | module-detail |
| `/api/notes` | **🟢 GET** | `NoteViewSet` | note-list |
| `/api/notes/<pk>` | **🟢 GET** | `NoteViewSet` | note-detail |
| `/api/progress` | **🟢 GET** | `ProgressViewSet` | progress-list |
| `/api/progress/<pk>` | **🟢 GET** | `ProgressViewSet` | progress-detail |
| `/api/reviews` | **🟢 GET** | `ReviewViewSet` | review-list |
| `/api/reviews/<pk>` | **🟢 GET** | `ReviewViewSet` | review-detail |
| `/api/search` | **🟢 GET** | `UnifiedSearchView` | search |
| `/api/user/progress-stats` | **🟢 GET** | `UserProgressStatsView` | user-progress-stats-legacy |
| `/api/user/progress/stats` | **🟢 GET** | `UserProgressStatsView` | user-progress-stats |
| `/api/version` | **🟢 GET** | `APIVersionView` | api-version |

## Web Endpoints

### Main Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/debug/courses` | **🟢 GET** | `debug_courses` | api-debug-courses |
| `/instructor/debug/courses` | **🟢 GET** | `debug_courses` | debug-courses-direct |
| `/instructor/debug/courses/simple` | **🟢 GET** | `debug_courses` | debug-courses-simple |
| `/media/<path>` | **🟢 GET** | `serve` | unnamed |
| `/static/<path>` | **🟢 GET** | `serve` | unnamed |
| `/test-admin-static` | **🟢 GET** | `test_admin_static` | test-admin-static |
| `/test-static` | **🟢 GET** | `test_static` | test-static |

### Djdt Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/__debug__/history_refresh` | **🟢 GET** | `history_refresh` | history_refresh |
| `/__debug__/history_sidebar` | **🟢 GET** | `history_sidebar` | history_sidebar |
| `/__debug__/render_panel` | **🟢 GET** | `render_panel` | render_panel |
| `/__debug__/sql_explain` | **🟢 GET** | `sql_explain` | sql_explain |
| `/__debug__/sql_profile` | **🟢 GET** | `sql_profile` | sql_profile |
| `/__debug__/sql_select` | **🟢 GET** | `sql_select` | sql_select |
| `/__debug__/template_source` | **🟢 GET** | `template_source` | template_source |

### Admin Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/admin` | **🟢 GET** | `index` | index |
| `/admin/<app_label>` | **🟢 GET** | `app_index` | app_list |
| `/admin/<url>` | **🟢 GET** | `catch_all_view` | unnamed |
| `/admin/account/emailaddress` | **🟢 GET** | `changelist_view` | account_emailaddress_changelist |
| `/admin/account/emailaddress/<path:object_id>/change` | **🟢 GET** | `change_view` | account_emailaddress_change |
| `/admin/account/emailaddress/<path:object_id>/delete` | **🟢 GET** | `delete_view` | account_emailaddress_delete |
| `/admin/account/emailaddress/<path:object_id>/history` | **🟢 GET** | `history_view` | account_emailaddress_history |
| `/admin/account/emailaddress/add` | **🟢 GET** | `add_view` | account_emailaddress_add |
| `/admin/auth/group` | **🟢 GET** | `changelist_view` | auth_group_changelist |
| `/admin/auth/group/<path:object_id>/change` | **🟢 GET** | `change_view` | auth_group_change |
| `/admin/auth/group/<path:object_id>/delete` | **🟢 GET** | `delete_view` | auth_group_delete |
| `/admin/auth/group/<path:object_id>/history` | **🟢 GET** | `history_view` | auth_group_history |
| `/admin/auth/group/add` | **🟢 GET** | `add_view` | auth_group_add |
| `/admin/autocomplete` | **🟢 GET** | `autocomplete_view` | autocomplete |
| `/admin/content/instructorstatistics` | **🟢 GET** | `changelist_view` | content_instructorstatistics_changelist |
| `/admin/content/instructorstatistics/<path:object_id>/change` | **🟢 GET** | `change_view` | content_instructorstatistics_change |
| `/admin/content/instructorstatistics/<path:object_id>/delete` | **🟢 GET** | `delete_view` | content_instructorstatistics_delete |
| `/admin/content/instructorstatistics/<path:object_id>/history` | **🟢 GET** | `history_view` | content_instructorstatistics_history |
| `/admin/content/instructorstatistics/add` | **🟢 GET** | `add_view` | content_instructorstatistics_add |
| `/admin/content/platformstatistics` | **🟢 GET** | `changelist_view` | content_platformstatistics_changelist |
| `/admin/content/platformstatistics/<path:object_id>/change` | **🟢 GET** | `change_view` | content_platformstatistics_change |
| `/admin/content/platformstatistics/<path:object_id>/delete` | **🟢 GET** | `delete_view` | content_platformstatistics_delete |
| `/admin/content/platformstatistics/<path:object_id>/history` | **🟢 GET** | `history_view` | content_platformstatistics_history |
| `/admin/content/platformstatistics/add` | **🟢 GET** | `add_view` | content_platformstatistics_add |
| `/admin/content/testimonial` | **🟢 GET** | `changelist_view` | content_testimonial_changelist |
| `/admin/content/testimonial/<path:object_id>/change` | **🟢 GET** | `change_view` | content_testimonial_change |
| `/admin/content/testimonial/<path:object_id>/delete` | **🟢 GET** | `delete_view` | content_testimonial_delete |
| `/admin/content/testimonial/<path:object_id>/history` | **🟢 GET** | `history_view` | content_testimonial_history |
| `/admin/content/testimonial/add` | **🟢 GET** | `add_view` | content_testimonial_add |
| `/admin/content/userlearningstatistics` | **🟢 GET** | `changelist_view` | content_userlearningstatistics_changelist |
| `/admin/content/userlearningstatistics/<path:object_id>/change` | **🟢 GET** | `change_view` | content_userlearningstatistics_change |
| `/admin/content/userlearningstatistics/<path:object_id>/delete` | **🟢 GET** | `delete_view` | content_userlearningstatistics_delete |
| `/admin/content/userlearningstatistics/<path:object_id>/history` | **🟢 GET** | `history_view` | content_userlearningstatistics_history |
| `/admin/content/userlearningstatistics/add` | **🟢 GET** | `add_view` | content_userlearningstatistics_add |
| `/admin/courses/category` | **🟢 GET** | `changelist_view` | courses_category_changelist |
| `/admin/courses/category/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_category_change |
| `/admin/courses/category/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_category_delete |
| `/admin/courses/category/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_category_history |
| `/admin/courses/category/add` | **🟢 GET** | `add_view` | courses_category_add |
| `/admin/courses/course` | **🟢 GET** | `changelist_view` | courses_course_changelist |
| `/admin/courses/course/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_course_change |
| `/admin/courses/course/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_course_delete |
| `/admin/courses/course/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_course_history |
| `/admin/courses/course/add` | **🟢 GET** | `add_view` | courses_course_add |
| `/admin/courses/enrollment` | **🟢 GET** | `changelist_view` | courses_enrollment_changelist |
| `/admin/courses/enrollment/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_enrollment_change |
| `/admin/courses/enrollment/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_enrollment_delete |
| `/admin/courses/enrollment/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_enrollment_history |
| `/admin/courses/enrollment/add` | **🟢 GET** | `add_view` | courses_enrollment_add |
| `/admin/courses/lesson` | **🟢 GET** | `changelist_view` | courses_lesson_changelist |
| `/admin/courses/lesson/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_lesson_change |
| `/admin/courses/lesson/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_lesson_delete |
| `/admin/courses/lesson/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_lesson_history |
| `/admin/courses/lesson/add` | **🟢 GET** | `add_view` | courses_lesson_add |
| `/admin/courses/module` | **🟢 GET** | `changelist_view` | courses_module_changelist |
| `/admin/courses/module/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_module_change |
| `/admin/courses/module/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_module_delete |
| `/admin/courses/module/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_module_history |
| `/admin/courses/module/add` | **🟢 GET** | `add_view` | courses_module_add |
| `/admin/courses/resource` | **🟢 GET** | `changelist_view` | courses_resource_changelist |
| `/admin/courses/resource/<path:object_id>/change` | **🟢 GET** | `change_view` | courses_resource_change |
| `/admin/courses/resource/<path:object_id>/delete` | **🟢 GET** | `delete_view` | courses_resource_delete |
| `/admin/courses/resource/<path:object_id>/history` | **🟢 GET** | `history_view` | courses_resource_history |
| `/admin/courses/resource/add` | **🟢 GET** | `add_view` | courses_resource_add |
| `/admin/django_celery_beat/clockedschedule` | **🟢 GET** | `changelist_view` | django_celery_beat_clockedschedule_changelist |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/change` | **🟢 GET** | `change_view` | django_celery_beat_clockedschedule_change |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/delete` | **🟢 GET** | `delete_view` | django_celery_beat_clockedschedule_delete |
| `/admin/django_celery_beat/clockedschedule/<path:object_id>/history` | **🟢 GET** | `history_view` | django_celery_beat_clockedschedule_history |
| `/admin/django_celery_beat/clockedschedule/add` | **🟢 GET** | `add_view` | django_celery_beat_clockedschedule_add |
| `/admin/django_celery_beat/crontabschedule` | **🟢 GET** | `changelist_view` | django_celery_beat_crontabschedule_changelist |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/change` | **🟢 GET** | `change_view` | django_celery_beat_crontabschedule_change |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/delete` | **🟢 GET** | `delete_view` | django_celery_beat_crontabschedule_delete |
| `/admin/django_celery_beat/crontabschedule/<path:object_id>/history` | **🟢 GET** | `history_view` | django_celery_beat_crontabschedule_history |
| `/admin/django_celery_beat/crontabschedule/add` | **🟢 GET** | `add_view` | django_celery_beat_crontabschedule_add |
| `/admin/django_celery_beat/intervalschedule` | **🟢 GET** | `changelist_view` | django_celery_beat_intervalschedule_changelist |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/change` | **🟢 GET** | `change_view` | django_celery_beat_intervalschedule_change |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/delete` | **🟢 GET** | `delete_view` | django_celery_beat_intervalschedule_delete |
| `/admin/django_celery_beat/intervalschedule/<path:object_id>/history` | **🟢 GET** | `history_view` | django_celery_beat_intervalschedule_history |
| `/admin/django_celery_beat/intervalschedule/add` | **🟢 GET** | `add_view` | django_celery_beat_intervalschedule_add |
| `/admin/django_celery_beat/periodictask` | **🟢 GET** | `changelist_view` | django_celery_beat_periodictask_changelist |
| `/admin/django_celery_beat/periodictask/<path:object_id>/change` | **🟢 GET** | `change_view` | django_celery_beat_periodictask_change |
| `/admin/django_celery_beat/periodictask/<path:object_id>/delete` | **🟢 GET** | `delete_view` | django_celery_beat_periodictask_delete |
| `/admin/django_celery_beat/periodictask/<path:object_id>/history` | **🟢 GET** | `history_view` | django_celery_beat_periodictask_history |
| `/admin/django_celery_beat/periodictask/add` | **🟢 GET** | `add_view` | django_celery_beat_periodictask_add |
| `/admin/django_celery_beat/solarschedule` | **🟢 GET** | `changelist_view` | django_celery_beat_solarschedule_changelist |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/change` | **🟢 GET** | `change_view` | django_celery_beat_solarschedule_change |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/delete` | **🟢 GET** | `delete_view` | django_celery_beat_solarschedule_delete |
| `/admin/django_celery_beat/solarschedule/<path:object_id>/history` | **🟢 GET** | `history_view` | django_celery_beat_solarschedule_history |
| `/admin/django_celery_beat/solarschedule/add` | **🟢 GET** | `add_view` | django_celery_beat_solarschedule_add |
| `/admin/instructor_portal/coursecontentdraft` | **🟢 GET** | `changelist_view` | instructor_portal_coursecontentdraft_changelist |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_coursecontentdraft_change |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_coursecontentdraft_delete |
| `/admin/instructor_portal/coursecontentdraft/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_coursecontentdraft_history |
| `/admin/instructor_portal/coursecontentdraft/add` | **🟢 GET** | `add_view` | instructor_portal_coursecontentdraft_add |
| `/admin/instructor_portal/coursecreationsession` | **🟢 GET** | `changelist_view` | instructor_portal_coursecreationsession_changelist |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_coursecreationsession_change |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_coursecreationsession_delete |
| `/admin/instructor_portal/coursecreationsession/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_coursecreationsession_history |
| `/admin/instructor_portal/coursecreationsession/add` | **🟢 GET** | `add_view` | instructor_portal_coursecreationsession_add |
| `/admin/instructor_portal/courseinstructor` | **🟢 GET** | `changelist_view` | instructor_portal_courseinstructor_changelist |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_courseinstructor_change |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_courseinstructor_delete |
| `/admin/instructor_portal/courseinstructor/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_courseinstructor_history |
| `/admin/instructor_portal/courseinstructor/add` | **🟢 GET** | `add_view` | instructor_portal_courseinstructor_add |
| `/admin/instructor_portal/coursetemplate` | **🟢 GET** | `changelist_view` | instructor_portal_coursetemplate_changelist |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_coursetemplate_change |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_coursetemplate_delete |
| `/admin/instructor_portal/coursetemplate/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_coursetemplate_history |
| `/admin/instructor_portal/coursetemplate/add` | **🟢 GET** | `add_view` | instructor_portal_coursetemplate_add |
| `/admin/instructor_portal/draftcoursecontent` | **🟢 GET** | `changelist_view` | instructor_portal_draftcoursecontent_changelist |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_draftcoursecontent_change |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_draftcoursecontent_delete |
| `/admin/instructor_portal/draftcoursecontent/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_draftcoursecontent_history |
| `/admin/instructor_portal/draftcoursecontent/add` | **🟢 GET** | `add_view` | instructor_portal_draftcoursecontent_add |
| `/admin/instructor_portal/instructoranalytics` | **🟢 GET** | `changelist_view` | instructor_portal_instructoranalytics_changelist |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_instructoranalytics_change |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_instructoranalytics_delete |
| `/admin/instructor_portal/instructoranalytics/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_instructoranalytics_history |
| `/admin/instructor_portal/instructoranalytics/add` | **🟢 GET** | `add_view` | instructor_portal_instructoranalytics_add |
| `/admin/instructor_portal/instructordashboard` | **🟢 GET** | `changelist_view` | instructor_portal_instructordashboard_changelist |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_instructordashboard_change |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_instructordashboard_delete |
| `/admin/instructor_portal/instructordashboard/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_instructordashboard_history |
| `/admin/instructor_portal/instructordashboard/add` | **🟢 GET** | `add_view` | instructor_portal_instructordashboard_add |
| `/admin/instructor_portal/instructorprofile` | **🟢 GET** | `changelist_view` | instructor_portal_instructorprofile_changelist |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/change` | **🟢 GET** | `change_view` | instructor_portal_instructorprofile_change |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/delete` | **🟢 GET** | `delete_view` | instructor_portal_instructorprofile_delete |
| `/admin/instructor_portal/instructorprofile/<path:object_id>/history` | **🟢 GET** | `history_view` | instructor_portal_instructorprofile_history |
| `/admin/instructor_portal/instructorprofile/add` | **🟢 GET** | `add_view` | instructor_portal_instructorprofile_add |
| `/admin/jsi18n` | **🟢 GET** | `i18n_javascript` | jsi18n |
| `/admin/login` | **🟢 GET** | `login` | login |
| `/admin/logout` | **🟢 GET** | `logout` | logout |
| `/admin/password_change` | **🟢 GET** | `password_change` | password_change |
| `/admin/password_change/done` | **🟢 GET** | `password_change_done` | password_change_done |
| `/admin/r/<path:content_type_id>/<path:object_id>` | **🟢 GET** | `shortcut` | view_on_site |
| `/admin/sites/site` | **🟢 GET** | `changelist_view` | sites_site_changelist |
| `/admin/sites/site/<path:object_id>/change` | **🟢 GET** | `change_view` | sites_site_change |
| `/admin/sites/site/<path:object_id>/delete` | **🟢 GET** | `delete_view` | sites_site_delete |
| `/admin/sites/site/<path:object_id>/history` | **🟢 GET** | `history_view` | sites_site_history |
| `/admin/sites/site/add` | **🟢 GET** | `add_view` | sites_site_add |
| `/admin/social_django/association` | **🟢 GET** | `changelist_view` | social_django_association_changelist |
| `/admin/social_django/association/<path:object_id>/change` | **🟢 GET** | `change_view` | social_django_association_change |
| `/admin/social_django/association/<path:object_id>/delete` | **🟢 GET** | `delete_view` | social_django_association_delete |
| `/admin/social_django/association/<path:object_id>/history` | **🟢 GET** | `history_view` | social_django_association_history |
| `/admin/social_django/association/add` | **🟢 GET** | `add_view` | social_django_association_add |
| `/admin/social_django/nonce` | **🟢 GET** | `changelist_view` | social_django_nonce_changelist |
| `/admin/social_django/nonce/<path:object_id>/change` | **🟢 GET** | `change_view` | social_django_nonce_change |
| `/admin/social_django/nonce/<path:object_id>/delete` | **🟢 GET** | `delete_view` | social_django_nonce_delete |
| `/admin/social_django/nonce/<path:object_id>/history` | **🟢 GET** | `history_view` | social_django_nonce_history |
| `/admin/social_django/nonce/add` | **🟢 GET** | `add_view` | social_django_nonce_add |
| `/admin/social_django/usersocialauth` | **🟢 GET** | `changelist_view` | social_django_usersocialauth_changelist |
| `/admin/social_django/usersocialauth/<path:object_id>/change` | **🟢 GET** | `change_view` | social_django_usersocialauth_change |
| `/admin/social_django/usersocialauth/<path:object_id>/delete` | **🟢 GET** | `delete_view` | social_django_usersocialauth_delete |
| `/admin/social_django/usersocialauth/<path:object_id>/history` | **🟢 GET** | `history_view` | social_django_usersocialauth_history |
| `/admin/social_django/usersocialauth/add` | **🟢 GET** | `add_view` | social_django_usersocialauth_add |
| `/admin/socialaccount/socialaccount` | **🟢 GET** | `changelist_view` | socialaccount_socialaccount_changelist |
| `/admin/socialaccount/socialaccount/<path:object_id>/change` | **🟢 GET** | `change_view` | socialaccount_socialaccount_change |
| `/admin/socialaccount/socialaccount/<path:object_id>/delete` | **🟢 GET** | `delete_view` | socialaccount_socialaccount_delete |
| `/admin/socialaccount/socialaccount/<path:object_id>/history` | **🟢 GET** | `history_view` | socialaccount_socialaccount_history |
| `/admin/socialaccount/socialaccount/add` | **🟢 GET** | `add_view` | socialaccount_socialaccount_add |
| `/admin/socialaccount/socialapp` | **🟢 GET** | `changelist_view` | socialaccount_socialapp_changelist |
| `/admin/socialaccount/socialapp/<path:object_id>/change` | **🟢 GET** | `change_view` | socialaccount_socialapp_change |
| `/admin/socialaccount/socialapp/<path:object_id>/delete` | **🟢 GET** | `delete_view` | socialaccount_socialapp_delete |
| `/admin/socialaccount/socialapp/<path:object_id>/history` | **🟢 GET** | `history_view` | socialaccount_socialapp_history |
| `/admin/socialaccount/socialapp/add` | **🟢 GET** | `add_view` | socialaccount_socialapp_add |
| `/admin/socialaccount/socialtoken` | **🟢 GET** | `changelist_view` | socialaccount_socialtoken_changelist |
| `/admin/socialaccount/socialtoken/<path:object_id>/change` | **🟢 GET** | `change_view` | socialaccount_socialtoken_change |
| `/admin/socialaccount/socialtoken/<path:object_id>/delete` | **🟢 GET** | `delete_view` | socialaccount_socialtoken_delete |
| `/admin/socialaccount/socialtoken/<path:object_id>/history` | **🟢 GET** | `history_view` | socialaccount_socialtoken_history |
| `/admin/socialaccount/socialtoken/add` | **🟢 GET** | `add_view` | socialaccount_socialtoken_add |
| `/admin/token_blacklist/blacklistedtoken` | **🟢 GET** | `changelist_view` | token_blacklist_blacklistedtoken_changelist |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/change` | **🟢 GET** | `change_view` | token_blacklist_blacklistedtoken_change |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/delete` | **🟢 GET** | `delete_view` | token_blacklist_blacklistedtoken_delete |
| `/admin/token_blacklist/blacklistedtoken/<path:object_id>/history` | **🟢 GET** | `history_view` | token_blacklist_blacklistedtoken_history |
| `/admin/token_blacklist/blacklistedtoken/add` | **🟢 GET** | `add_view` | token_blacklist_blacklistedtoken_add |
| `/admin/token_blacklist/outstandingtoken` | **🟢 GET** | `changelist_view` | token_blacklist_outstandingtoken_changelist |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/change` | **🟢 GET** | `change_view` | token_blacklist_outstandingtoken_change |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/delete` | **🟢 GET** | `delete_view` | token_blacklist_outstandingtoken_delete |
| `/admin/token_blacklist/outstandingtoken/<path:object_id>/history` | **🟢 GET** | `history_view` | token_blacklist_outstandingtoken_history |
| `/admin/token_blacklist/outstandingtoken/add` | **🟢 GET** | `add_view` | token_blacklist_outstandingtoken_add |
| `/admin/users/customuser` | **🟢 GET** | `changelist_view` | users_customuser_changelist |
| `/admin/users/customuser/<id>/password` | **🟢 GET** | `user_change_password` | auth_user_password_change |
| `/admin/users/customuser/<path:object_id>/change` | **🟢 GET** | `change_view` | users_customuser_change |
| `/admin/users/customuser/<path:object_id>/delete` | **🟢 GET** | `delete_view` | users_customuser_delete |
| `/admin/users/customuser/<path:object_id>/history` | **🟢 GET** | `history_view` | users_customuser_history |
| `/admin/users/customuser/add` | **🟢 GET** | `add_view` | users_customuser_add |
| `/admin/users/emailverification` | **🟢 GET** | `changelist_view` | users_emailverification_changelist |
| `/admin/users/emailverification/<path:object_id>/change` | **🟢 GET** | `change_view` | users_emailverification_change |
| `/admin/users/emailverification/<path:object_id>/delete` | **🟢 GET** | `delete_view` | users_emailverification_delete |
| `/admin/users/emailverification/<path:object_id>/history` | **🟢 GET** | `history_view` | users_emailverification_history |
| `/admin/users/emailverification/add` | **🟢 GET** | `add_view` | users_emailverification_add |
| `/admin/users/loginlog` | **🟢 GET** | `changelist_view` | users_loginlog_changelist |
| `/admin/users/loginlog/<path:object_id>/change` | **🟢 GET** | `change_view` | users_loginlog_change |
| `/admin/users/loginlog/<path:object_id>/delete` | **🟢 GET** | `delete_view` | users_loginlog_delete |
| `/admin/users/loginlog/<path:object_id>/history` | **🟢 GET** | `history_view` | users_loginlog_history |
| `/admin/users/loginlog/add` | **🟢 GET** | `add_view` | users_loginlog_add |
| `/admin/users/passwordreset` | **🟢 GET** | `changelist_view` | users_passwordreset_changelist |
| `/admin/users/passwordreset/<path:object_id>/change` | **🟢 GET** | `change_view` | users_passwordreset_change |
| `/admin/users/passwordreset/<path:object_id>/delete` | **🟢 GET** | `delete_view` | users_passwordreset_delete |
| `/admin/users/passwordreset/<path:object_id>/history` | **🟢 GET** | `history_view` | users_passwordreset_history |
| `/admin/users/passwordreset/add` | **🟢 GET** | `add_view` | users_passwordreset_add |
| `/admin/users/usersession` | **🟢 GET** | `changelist_view` | users_usersession_changelist |
| `/admin/users/usersession/<path:object_id>/change` | **🟢 GET** | `change_view` | users_usersession_change |
| `/admin/users/usersession/<path:object_id>/delete` | **🟢 GET** | `delete_view` | users_usersession_delete |
| `/admin/users/usersession/<path:object_id>/history` | **🟢 GET** | `history_view` | users_usersession_history |
| `/admin/users/usersession/add` | **🟢 GET** | `add_view` | users_usersession_add |

### Rest_Framework Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api-auth/login` | 🟢 GET / 🔵 POST / 🟡 PUT | `LoginView` | login |
| `/api-auth/logout` | **🔵 POST** | `LogoutView` | logout |

### Instructor_Portal Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/instructor/debug` | **🟢 GET** | `basic_debug_view` | debug |

### Social Web Endpoints

| URL | Methods | View | Name |
|-----|---------|------|------|
| `/api/user/social-auth/complete/<str>` | **🟢 GET** | `complete` | complete |
| `/api/user/social-auth/disconnect/<str>` | **🟢 GET** | `disconnect` | disconnect |
| `/api/user/social-auth/disconnect/<str>/<int>` | **🟢 GET** | `disconnect` | disconnect_individual |
| `/api/user/social-auth/login/<str>` | **🟢 GET** | `auth` | begin |

## 📊 Analysis

### HTTP Methods Distribution

- **GET**: 290 endpoints
- **PATCH**: 2 endpoints
- **POST**: 16 endpoints
- **PUT**: 4 endpoints

### View Types

- **Function-based Views**: 230 endpoints
- **Class-based Views**: 76 endpoints

### Namespace Distribution

- **Main**: 50 endpoints
- **admin**: 206 endpoints
- **courses**: 36 endpoints
- **djdt**: 7 endpoints
- **instructor_portal**: 1 endpoints
- **rest_framework**: 2 endpoints
- **social**: 4 endpoints


---

*Generated by Enhanced Django Endpoints Extractor*
