# Django Backend Analysis Report
- Generated for: backend
- Date: 2025-06-20 19:53:49

## Table of Contents
1. [Frontend Data](#frontend-data)
   1. [API Endpoints](#api-endpoints)
   2. [Data Models](#data-models)
   3. [Serializers](#serializers)
   4. [Entity-Relationship Diagram](#entity-relationship-diagram)
   5. [Authentication](#authentication)
   6. [Security Matrix](#security-matrix)
2. [Backend Compatibility](#backend-compatibility)
   1. [Issues](#issues)
   2. [Component Mappings](#component-mappings)

---

<a id='frontend-data'></a>
# FRONT END DATA

<a id='api-endpoints'></a>
## API Endpoints

### Path: `admin`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `admin/` | admin.site.urls | - | - | - |

### Path: `test-static`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `test-static/` | test_static | - | - | - |

### Path: `test-admin-static`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `test-admin-static/` | test_admin_static | - | - | - |

### Path: `instructor/debug/courses`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `instructor/debug/courses/` | debug_courses | - | - | - |

### Path: `instructor/debug/courses/simple`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `instructor/debug/courses/simple/` | debug_courses | - | - | - |

### Path: `api`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/` | include | - | - | - |

### Path: `api/token`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/token/` | TokenObtainPairView | - | - | - |

### Path: `api/token/refresh`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/token/refresh/` | TokenRefreshView | - | - | - |

### Path: `api/system/db-status`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/system/db-status/` | db_status | - | - | - |

### Path: `api/system/db-stats`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/system/db-stats/` | db_stats | - | - | - |

### Path: `api/user`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/user/` | include | - | - | - |

### Path: `api/instructor`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/instructor/` | include | - | - | - |

### Path: `api/debug/courses`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/debug/courses/` | debug_courses | - | - | - |

### Path: `api-auth`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api-auth/` | include | - | - | - |

### Path: `JoinedStr`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `JoinedStr` | include | - | - | - |

### Path: `auth/register`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `auth/register/` | InstructorRegistrationView | - | - | - |

### Path: `auth/verify`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `auth/verify/<uuid:verification_token>/` | InstructorVerificationView | - | - | - |

### Path: `auth/status`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `auth/status/` | InstructorStatusView | - | - | - |

### Path: `auth/approval`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `auth/approval/` | InstructorApprovalView | - | - | - |

### Path: `analytics/reports`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `analytics/reports/` | InstructorReportsView | - | - | - |

### Path: `analytics/revenue`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `analytics/revenue/` | RevenueAnalyticsView | - | - | - |

### Path: `students`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `students/` | StudentManagementView | - | - | - |

### Path: `create/wizard`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `create/wizard/` | include | - | - | - |

### Path: `create/ai`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `create/ai/` | include | - | - | - |

### Path: `create/dnd`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `create/dnd/` | include | - | - | - |

### Path: `create/template`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `create/template/` | include | - | - | - |

### Path: `create/import`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `create/import/` | include | - | - | - |

### Path: `courses`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `courses/` | include | - | - | - |

### Path: `drafts`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `drafts/` | include | - | - | - |

### Path: `uploads`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `uploads/` | include | - | - | - |

### Path: `profile`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `profile/` | include | - | - | - |

### Path: `settings`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `settings/` | include | - | - | - |

### Path: `templates`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `templates/` | include | - | - | - |

### Path: `bulk`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `bulk/` | include | - | - | - |

### Path: `utils`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `utils/` | include | - | - | - |

### Path: `ai`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `ai/` | include | - | - | - |

### Path: `reports`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `reports/` | include | - | - | - |

### Path: `integrations`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `integrations/` | include | - | - | - |

### Path: `debug`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `debug/` | include | - | - | - |

### Path: `health`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `health/` | include | - | - | - |

### Path: `api/instructor/ai-course-builder/health`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `api/instructor/ai-course-builder/health/` | AICourseBuilderHealthView | - | - | IsAuthenticated |

### Path: `register`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `register/` | RegisterView | UserCreateSerializer | User | AllowAny |

### Path: `login`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `login/` | LoginView | LoginSerializer | - | AllowAny |

### Path: `logout`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `logout/` | LogoutView | - | - | IsAuthenticated |

### Path: `token`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `token/` | TokenObtainPairView | - | - | - |

### Path: `token/refresh`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `token/refresh/` | TokenRefreshView | - | - | - |

### Path: `me`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `me/` | UserView | UserDetailSerializer | - | IsAuthenticated, IsOwnerOrAdmin |

### Path: `password/change`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `password/change/` | PasswordChangeView | PasswordChangeSerializer | - | IsAuthenticated |

### Path: `password/reset`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `password/reset/` | PasswordResetRequestView | PasswordResetRequestSerializer | - | AllowAny |

### Path: `password/reset/confirm`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `password/reset/confirm/` | PasswordResetConfirmView | PasswordResetConfirmSerializer | - | AllowAny |

### Path: `email/verify`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `email/verify/` | EmailVerificationView | EmailVerificationSerializer | - | AllowAny |

### Path: `email/verify/resend`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| POST | `email/verify/resend/` | ResendVerificationView | - | - | AllowAny |

### Path: `testimonials/featured`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `testimonials/featured/` | FeaturedTestimonialsView | TestimonialSerializer | - | AllowAny |

### Path: `statistics/platform`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `statistics/platform/` | views.platform_statistics | - | - | - |

### Path: `statistics/user/learning`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `statistics/user/learning/` | views.user_learning_statistics | - | - | - |

### Path: `statistics/instructor`

| Method | Full Path | View | Serializer | Model | Permissions |
| --- | --- | --- | --- | --- | --- |
| GET | `statistics/instructor/` | views.instructor_statistics | - | - | - |

### Common API Conventions

- **GET /resource/**: List all resources
- **POST /resource/**: Create a new resource
- **GET /resource/{id}/**: Retrieve a specific resource
- **PUT /resource/{id}/**: Update a specific resource (full update)
- **PATCH /resource/{id}/**: Update a specific resource (partial update)
- **DELETE /resource/{id}/**: Delete a specific resource


<a id='data-models'></a>
## Data Models

### App: instructor_portal

#### InstructorProfile

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['-created_date']
- indexes: ['Call', 'Call', 'Call']
- constraints: ['Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | OneToOneField | on_delete=Attribute, related_name=instructor_profile, verbose_name=Call, db_index=True, to=Name |
| display_name | CharField | max_length=100, verbose_name=Call, help_text=Call |
| bio | TextField | max_length=2000, blank=True, verbose_name=Call, help_text=Call |
| expertise_areas | ManyToManyField | blank=True, related_name=expert_instructors, verbose_name=Call, to=courses.Category |
| title | CharField | max_length=150, blank=True, verbose_name=Call, help_text=Call |
| organization | CharField | max_length=200, blank=True, verbose_name=Call |
| years_experience | PositiveIntegerField | default=0, validators=['Call'], verbose_name=Call |
| website | URLField | blank=True, validators=['Call'], verbose_name=Call |
| linkedin_profile | URLField | blank=True, validators=['Call'], verbose_name=Call |
| twitter_handle | CharField | max_length=50, blank=True, verbose_name=Call |
| profile_image | ImageField | upload_to=Name, blank=True, null=True, verbose_name=Call |
| cover_image | ImageField | upload_to=Name, blank=True, null=True, verbose_name=Call |
| status | CharField | max_length=30, choices=Attribute, default=Attribute, verbose_name=Call |
| is_verified | BooleanField | default=False, verbose_name=Call, help_text=Call |
| tier | CharField | max_length=30, choices=Attribute, default=Attribute, verbose_name=Call |
| email_notifications | BooleanField | default=True, verbose_name=Call |
| marketing_emails | BooleanField | default=False, verbose_name=Call |
| public_profile | BooleanField | default=True, verbose_name=Call, help_text=Call |
| approved_by | ForeignKey | on_delete=Attribute, null=True, blank=True, related_name=approved_instructors, verbose_name=Call, to=Name |
| approval_date | DateTimeField | null=True, blank=True, verbose_name=Call |
| suspension_reason | TextField | blank=True, verbose_name=Call |
| created_date | DateTimeField | auto_now_add=True, verbose_name=Call |
| updated_date | DateTimeField | auto_now=True, verbose_name=Call |
| last_login | DateTimeField | null=True, blank=True, verbose_name=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | OneToOneField | Name | instructor_profile |
| expertise_areas | ManyToManyField | courses.Category | expert_instructors |
| approved_by | ForeignKey | Name | approved_instructors |

**Frontend Usage Notes:**

- Use the model name `InstructorProfile` for component naming (e.g., `InstructorProfileList`, `InstructorProfileDetail`)
- Primary API endpoint will likely follow REST conventions for `instructorprofile`
- Contains image fields - frontend should handle image uploads and display
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorAnalytics

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- indexes: ['Call', 'Call']
- constraints: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| instructor | OneToOneField | on_delete=Attribute, related_name=analytics, verbose_name=Call, to=Name |
| total_students | PositiveIntegerField | default=0, verbose_name=Call |
| total_courses | PositiveIntegerField | default=0, verbose_name=Call |
| average_rating | DecimalField | max_digits=3, decimal_places=2, default=Call, validators=['Call', 'Call'], verbose_name=Call |
| total_reviews | PositiveIntegerField | default=0, verbose_name=Call |
| total_revenue | DecimalField | max_digits=12, decimal_places=2, default=Call, validators=['Call'], verbose_name=Call |
| completion_rate | DecimalField | max_digits=5, decimal_places=2, default=Call, verbose_name=Call |
| student_satisfaction_rate | DecimalField | max_digits=5, decimal_places=2, default=Call, verbose_name=Call |
| monthly_revenue | DecimalField | max_digits=12, decimal_places=2, default=Call, verbose_name=Call |
| last_updated | DateTimeField | auto_now=True, verbose_name=Call |
| last_calculated | DateTimeField | null=True, blank=True, verbose_name=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | OneToOneField | Name | analytics |

**Frontend Usage Notes:**

- Use the model name `InstructorAnalytics` for component naming (e.g., `InstructorAnalyticsList`, `InstructorAnalyticsDetail`)
- Primary API endpoint will likely follow REST conventions for `instructoranalytics`
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorAnalyticsHistory

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['-date']
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| instructor | ForeignKey | on_delete=Attribute, related_name=analytics_history, verbose_name=Call, to=Name |
| date | DateTimeField | default=Attribute, verbose_name=Call |
| total_students | PositiveIntegerField | default=0 |
| total_courses | PositiveIntegerField | default=0 |
| average_rating | DecimalField | max_digits=3, decimal_places=2, default=Call |
| total_revenue | DecimalField | max_digits=12, decimal_places=2, default=Call |
| completion_rate | DecimalField | max_digits=5, decimal_places=2, default=Call |
| data_type | CharField | max_length=50, default=daily, verbose_name=Call, help_text=Call |
| additional_data | JSONField | default=Name, blank=True, verbose_name=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | ForeignKey | Name | analytics_history |

**Frontend Usage Notes:**

- Use the model name `InstructorAnalyticsHistory` for component naming (e.g., `InstructorAnalyticsHistoryList`, `InstructorAnalyticsHistoryDetail`)
- Primary API endpoint will likely follow REST conventions for `instructoranalyticshistory`
- Contains date/time fields - use appropriate date pickers and formatting

#### CourseInstructor

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- unique_together: [['course', 'instructor']]
- ordering: ['course', '-is_lead', 'joined_date']
- indexes: ['Call', 'Call', 'Call']
- constraints: ['Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| course | ForeignKey | on_delete=Attribute, verbose_name=Call, to=courses.Course |
| instructor | ForeignKey | on_delete=Attribute, verbose_name=Call, to=Name |
| role | CharField | max_length=30, choices=Attribute, default=Attribute, verbose_name=Call |
| is_active | BooleanField | default=True, verbose_name=Call |
| is_lead | BooleanField | default=False, verbose_name=Call |
| can_edit_content | BooleanField | default=True |
| can_manage_students | BooleanField | default=True |
| can_view_analytics | BooleanField | default=True |
| revenue_share_percentage | DecimalField | max_digits=5, decimal_places=2, default=Call, validators=['Call', 'Call'] |
| joined_date | DateTimeField | auto_now_add=True |
| updated_date | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| course | ForeignKey | courses.Course | - |
| instructor | ForeignKey | Name | - |

**Frontend Usage Notes:**

- Use the model name `CourseInstructor` for component naming (e.g., `CourseInstructorList`, `CourseInstructorDetail`)
- Primary API endpoint will likely follow REST conventions for `courseinstructor`
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorDashboard

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| instructor | OneToOneField | on_delete=Attribute, related_name=dashboard, verbose_name=Call, to=Name |
| show_analytics | BooleanField | default=True |
| show_recent_students | BooleanField | default=True |
| show_performance_metrics | BooleanField | default=True |
| show_revenue_charts | BooleanField | default=True |
| show_course_progress | BooleanField | default=True |
| notify_new_enrollments | BooleanField | default=True |
| notify_new_reviews | BooleanField | default=True |
| notify_course_completions | BooleanField | default=True |
| widget_order | JSONField | default=Name, blank=True |
| custom_colors | JSONField | default=Name, blank=True |
| created_date | DateTimeField | auto_now_add=True |
| updated_date | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | OneToOneField | Name | dashboard |

**Frontend Usage Notes:**

- Use the model name `InstructorDashboard` for component naming (e.g., `InstructorDashboardList`, `InstructorDashboardDetail`)
- Primary API endpoint will likely follow REST conventions for `instructordashboard`
- Contains date/time fields - use appropriate date pickers and formatting

#### CourseCreationSession

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['-updated_date']
- indexes: ['Call', 'Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| session_id | UUIDField | default=Attribute, unique=True |
| instructor | ForeignKey | on_delete=Attribute, related_name=creation_sessions, to=Name |
| creation_method | CharField | max_length=30, choices=Attribute |
| status | CharField | max_length=30, choices=Attribute, default=Attribute |
| course_data | JSONField | default=Name |
| current_step | PositiveIntegerField | default=1 |
| total_steps | PositiveIntegerField | default=0 |
| completed_steps | JSONField | default=Name |
| progress_percentage | DecimalField | max_digits=5, decimal_places=2, default=Call |
| last_auto_save | DateTimeField | null=True, blank=True |
| auto_save_data | JSONField | default=Name |
| validation_errors | JSONField | default=Name |
| quality_score | DecimalField | max_digits=5, decimal_places=2, null=True, blank=True |
| ai_prompt | TextField | blank=True |
| ai_suggestions | JSONField | default=Name |
| template_used | CharField | max_length=100, blank=True |
| reference_courses | ManyToManyField | blank=True, related_name=referenced_in_creation, to=courses.Course |
| draft_course | ForeignKey | on_delete=Attribute, null=True, blank=True, related_name=active_sessions, to=courses.Course |
| published_course | OneToOneField | on_delete=Attribute, null=True, blank=True, related_name=creation_session, to=courses.Course |
| created_date | DateTimeField | auto_now_add=True |
| updated_date | DateTimeField | auto_now=True |
| completed_date | DateTimeField | null=True, blank=True |
| expires_at | DateTimeField | - |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | ForeignKey | Name | creation_sessions |
| reference_courses | ManyToManyField | courses.Course | referenced_in_creation |
| draft_course | ForeignKey | courses.Course | active_sessions |
| published_course | OneToOneField | courses.Course | creation_session |

**Frontend Usage Notes:**

- Use the model name `CourseCreationSession` for component naming (e.g., `CourseCreationSessionList`, `CourseCreationSessionDetail`)
- Primary API endpoint will likely follow REST conventions for `coursecreationsession`
- Contains date/time fields - use appropriate date pickers and formatting

#### CourseTemplate

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['category', 'template_type', 'name']
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| name | CharField | max_length=100 |
| description | TextField | - |
| template_type | CharField | max_length=30, choices=Attribute |
| category | ForeignKey | on_delete=Attribute, related_name=templates, to=courses.Category |
| template_data | JSONField | - |
| estimated_duration | PositiveIntegerField | - |
| difficulty_level | CharField | max_length=30, default=beginner |
| usage_count | PositiveIntegerField | default=0 |
| success_rate | DecimalField | max_digits=5, decimal_places=2, default=Call |
| is_active | BooleanField | default=True |
| created_by | ForeignKey | on_delete=Attribute, null=True, related_name=created_templates, to=Name |
| created_date | DateTimeField | auto_now_add=True |
| updated_date | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| category | ForeignKey | courses.Category | templates |
| created_by | ForeignKey | Name | created_templates |

**Frontend Usage Notes:**

- Use the model name `CourseTemplate` for component naming (e.g., `CourseTemplateList`, `CourseTemplateDetail`)
- Primary API endpoint will likely follow REST conventions for `coursetemplate`
- Contains date/time fields - use appropriate date pickers and formatting

#### DraftCourseContent

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- unique_together: [['session', 'content_type', 'content_id', 'version']]
- ordering: ['order', 'version']
- indexes: ['Call', 'Call', 'Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| session | ForeignKey | on_delete=Attribute, related_name=draft_content, verbose_name=Call, to=Name |
| content_type | CharField | max_length=30, choices=Attribute, verbose_name=Call |
| content_id | CharField | max_length=50, verbose_name=Call, help_text=Call |
| version | PositiveIntegerField | default=1, verbose_name=Call, help_text=Call |
| content_data | JSONField | verbose_name=Call, help_text=Call |
| title | CharField | max_length=200, blank=True, verbose_name=Call |
| order | PositiveIntegerField | default=1, verbose_name=Call |
| is_complete | BooleanField | default=False, verbose_name=Call, help_text=Call |
| validation_errors | JSONField | default=Name, verbose_name=Call, help_text=Call |
| auto_save_version | PositiveIntegerField | default=1, verbose_name=Call, help_text=Call |
| last_saved | DateTimeField | auto_now=True, verbose_name=Call |
| ai_generated | BooleanField | default=False, verbose_name=Call, help_text=Call |
| ai_prompt | TextField | blank=True, verbose_name=Call, help_text=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| session | ForeignKey | Name | draft_content |

**Frontend Usage Notes:**

- Use the model name `DraftCourseContent` for component naming (e.g., `DraftCourseContentList`, `DraftCourseContentDetail`)
- Primary API endpoint will likely follow REST conventions for `draftcoursecontent`
- Contains date/time fields - use appropriate date pickers and formatting

#### CourseContentDraft

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- unique_together: [['session', 'content_type', 'version']]
- ordering: ['-created_date']
- indexes: ['Call', 'Call', 'Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| session | ForeignKey | on_delete=Attribute, related_name=content_drafts, verbose_name=Call, to=Name |
| content_type | CharField | max_length=30, choices=Attribute, verbose_name=Call |
| file_path | FileField | upload_to=course_drafts/%Y/%m/%d/, null=True, blank=True, verbose_name=Call |
| content_hash | CharField | max_length=64, verbose_name=Call, help_text=Call |
| version | PositiveIntegerField | default=1, verbose_name=Call |
| is_processed | BooleanField | default=False, verbose_name=Call, help_text=Call |
| processing_status | CharField | max_length=30, choices=[('pending', 'Call'), ('processing', 'Call'), ('completed', 'Call'), ('failed', 'Call'), ('virus_scan', 'Call'), ('format_conversion', 'Call')], default=pending, verbose_name=Call |
| processing_error | TextField | blank=True, verbose_name=Call, help_text=Call |
| file_size | PositiveIntegerField | null=True, blank=True, verbose_name=Call |
| mime_type | CharField | max_length=100, blank=True, verbose_name=Call |
| original_filename | CharField | max_length=255, blank=True, verbose_name=Call |
| processing_metadata | JSONField | default=Name, blank=True, verbose_name=Call, help_text=Call |
| created_date | DateTimeField | auto_now_add=True, verbose_name=Call |
| processed_date | DateTimeField | null=True, blank=True, verbose_name=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| session | ForeignKey | Name | content_drafts |

**Frontend Usage Notes:**

- Use the model name `CourseContentDraft` for component naming (e.g., `CourseContentDraftList`, `CourseContentDraftDetail`)
- Primary API endpoint will likely follow REST conventions for `coursecontentdraft`
- Contains file fields - frontend should handle file uploads and downloads
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorNotification

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['-created_date']
- indexes: ['Call', 'Call', 'Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| instructor | ForeignKey | on_delete=Attribute, related_name=notifications, verbose_name=Call, to=Name |
| notification_type | CharField | max_length=30, choices=Attribute, verbose_name=Call |
| priority | CharField | max_length=20, choices=Attribute, default=Attribute, verbose_name=Call |
| title | CharField | max_length=200, verbose_name=Call |
| message | TextField | verbose_name=Call |
| action_url | URLField | blank=True, verbose_name=Call, help_text=Call |
| action_text | CharField | max_length=50, blank=True, verbose_name=Call, help_text=Call |
| metadata | JSONField | default=Name, blank=True, verbose_name=Call, help_text=Call |
| is_read | BooleanField | default=False, verbose_name=Call |
| read_at | DateTimeField | null=True, blank=True, verbose_name=Call |
| is_dismissed | BooleanField | default=False, verbose_name=Call |
| dismissed_at | DateTimeField | null=True, blank=True, verbose_name=Call |
| email_sent | BooleanField | default=False, verbose_name=Call |
| email_sent_at | DateTimeField | null=True, blank=True, verbose_name=Call |
| created_date | DateTimeField | auto_now_add=True, verbose_name=Call |
| expires_at | DateTimeField | null=True, blank=True, verbose_name=Call, help_text=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | ForeignKey | Name | notifications |

**Frontend Usage Notes:**

- Use the model name `InstructorNotification` for component naming (e.g., `InstructorNotificationList`, `InstructorNotificationDetail`)
- Primary API endpoint will likely follow REST conventions for `instructornotification`
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorSession

**Meta Options:**
- verbose_name: Call
- verbose_name_plural: Call
- ordering: ['-login_time']
- indexes: ['Call', 'Call', 'Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| instructor | ForeignKey | on_delete=Attribute, related_name=sessions, verbose_name=Call, to=Name |
| session_key | CharField | max_length=40, unique=True, verbose_name=Call |
| ip_address | GenericIPAddressField | verbose_name=Call |
| user_agent | TextField | blank=True, verbose_name=Call |
| device_type | CharField | max_length=20, choices=[('desktop', 'Call'), ('mobile', 'Call'), ('tablet', 'Call'), ('unknown', 'Call')], default=unknown, verbose_name=Call |
| location | CharField | max_length=100, blank=True, verbose_name=Call, help_text=Call |
| login_time | DateTimeField | auto_now_add=True, verbose_name=Call |
| last_activity | DateTimeField | auto_now=True, verbose_name=Call |
| logout_time | DateTimeField | null=True, blank=True, verbose_name=Call |
| is_active | BooleanField | default=True, verbose_name=Call |
| is_suspicious | BooleanField | default=False, verbose_name=Call, help_text=Call |
| security_notes | TextField | blank=True, verbose_name=Call |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | ForeignKey | Name | sessions |

**Frontend Usage Notes:**

- Use the model name `InstructorSession` for component naming (e.g., `InstructorSessionList`, `InstructorSessionDetail`)
- Primary API endpoint will likely follow REST conventions for `instructorsession`
- Contains date/time fields - use appropriate date pickers and formatting

### App: ai_course_builder

#### AICourseBuilderDraft

**Meta Options:**
- verbose_name: AI Course Builder Draft
- verbose_name_plural: AI Course Builder Drafts
- ordering: ['-updated_at']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| STATUS_CHOICES | Unknown | - |
| LEVEL_CHOICES | Unknown | - |
| instructor | ForeignKey | on_delete=Attribute, related_name=ai_course_drafts, to=Name |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |
| status | CharField | max_length=20, choices=Name, default=DRAFT |
| title | CharField | max_length=255, null=True, blank=True |
| description | TextField | null=True, blank=True |
| course_objectives | JSONField | default=Name, blank=True, null=True |
| target_audience | JSONField | default=Name, blank=True, null=True |
| difficulty_level | CharField | max_length=20, choices=Name, default=all_levels, null=True, blank=True |
| duration_minutes | PositiveIntegerField | null=True, blank=True |
| price | DecimalField | max_digits=10, decimal_places=2, null=True, blank=True |
| outline | JSONField | default=Name, blank=True, null=True |
| content | JSONField | default=Name, blank=True, null=True |
| assessments | JSONField | default=Name, blank=True, null=True |
| has_outline | BooleanField | default=False |
| has_modules | BooleanField | default=False |
| has_lessons | BooleanField | default=False |
| has_assessments | BooleanField | default=False |
| generation_metadata | JSONField | default=Name, blank=True, null=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| instructor | ForeignKey | Name | ai_course_drafts |

**Frontend Usage Notes:**

- Use the model name `AICourseBuilderDraft` for component naming (e.g., `AICourseBuilderDraftList`, `AICourseBuilderDraftDetail`)
- Primary API endpoint will likely follow REST conventions for `aicoursebuilderdraft`
- Contains date/time fields - use appropriate date pickers and formatting

### App: users

#### Profile

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | OneToOneField | on_delete=Attribute, related_name=profile, to=Attribute |
| profile_picture | ImageField | upload_to=profile_pictures/, null=True, blank=True |
| bio | TextField | blank=True |
| date_of_birth | DateField | null=True, blank=True |
| phone_number | CharField | max_length=20, blank=True |
| address | TextField | blank=True |
| city | CharField | max_length=100, blank=True |
| state | CharField | max_length=100, blank=True |
| country | CharField | max_length=100, blank=True |
| postal_code | CharField | max_length=20, blank=True |
| website | URLField | blank=True |
| linkedin | URLField | blank=True |
| twitter | CharField | max_length=100, blank=True |
| github | CharField | max_length=100, blank=True |
| expertise | CharField | max_length=200, blank=True |
| teaching_experience | PositiveIntegerField | default=0 |
| educational_background | TextField | blank=True |
| interests | TextField | blank=True |
| receive_email_notifications | BooleanField | default=True |
| receive_marketing_emails | BooleanField | default=False |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | OneToOneField | Attribute | profile |

**Frontend Usage Notes:**

- Use the model name `Profile` for component naming (e.g., `ProfileList`, `ProfileDetail`)
- Primary API endpoint will likely follow REST conventions for `profile`
- Contains image fields - frontend should handle image uploads and display
- Contains date/time fields - use appropriate date pickers and formatting

#### EmailVerification

**Meta Options:**
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | ForeignKey | on_delete=Attribute, related_name=email_verifications, to=Attribute |
| token | UUIDField | default=Attribute, editable=False, unique=True |
| created_at | DateTimeField | auto_now_add=True |
| expires_at | DateTimeField | - |
| verified_at | DateTimeField | null=True, blank=True |
| is_used | BooleanField | default=False |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | ForeignKey | Attribute | email_verifications |

**Frontend Usage Notes:**

- Use the model name `EmailVerification` for component naming (e.g., `EmailVerificationList`, `EmailVerificationDetail`)
- Primary API endpoint will likely follow REST conventions for `emailverification`
- Contains date/time fields - use appropriate date pickers and formatting

#### PasswordReset

**Meta Options:**
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | ForeignKey | on_delete=Attribute, related_name=password_resets, to=Attribute |
| token | UUIDField | default=Attribute, editable=False, unique=True |
| created_at | DateTimeField | auto_now_add=True |
| expires_at | DateTimeField | - |
| used_at | DateTimeField | null=True, blank=True |
| is_used | BooleanField | default=False |
| ip_address | GenericIPAddressField | null=True, blank=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | ForeignKey | Attribute | password_resets |

**Frontend Usage Notes:**

- Use the model name `PasswordReset` for component naming (e.g., `PasswordResetList`, `PasswordResetDetail`)
- Primary API endpoint will likely follow REST conventions for `passwordreset`
- Contains date/time fields - use appropriate date pickers and formatting

#### LoginLog

**Meta Options:**
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | ForeignKey | on_delete=Attribute, related_name=login_logs, to=Attribute |
| timestamp | DateTimeField | auto_now_add=True |
| ip_address | GenericIPAddressField | - |
| user_agent | TextField | - |
| successful | BooleanField | default=False |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | ForeignKey | Attribute | login_logs |

**Frontend Usage Notes:**

- Use the model name `LoginLog` for component naming (e.g., `LoginLogList`, `LoginLogDetail`)
- Primary API endpoint will likely follow REST conventions for `loginlog`
- Contains date/time fields - use appropriate date pickers and formatting

#### UserSession

**Meta Options:**
- indexes: ['Call', 'Call']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | ForeignKey | on_delete=Attribute, related_name=sessions, to=Attribute |
| session_key | CharField | max_length=255 |
| ip_address | GenericIPAddressField | - |
| user_agent | TextField | - |
| created_at | DateTimeField | auto_now_add=True |
| expires_at | DateTimeField | - |
| last_activity | DateTimeField | auto_now=True |
| is_active | BooleanField | default=True |
| device_type | CharField | max_length=50, blank=True |
| location | CharField | max_length=100, blank=True |
| login_method | CharField | max_length=50, blank=True, null=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | ForeignKey | Attribute | sessions |

**Frontend Usage Notes:**

- Use the model name `UserSession` for component naming (e.g., `UserSessionList`, `UserSessionDetail`)
- Primary API endpoint will likely follow REST conventions for `usersession`
- Contains date/time fields - use appropriate date pickers and formatting

#### Subscription

**Meta Options:**
- verbose_name: Subscription
- verbose_name_plural: Subscriptions

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| SUBSCRIPTION_TIERS | Unknown | - |
| STATUS_CHOICES | Unknown | - |
| user | OneToOneField | on_delete=Attribute, related_name=subscription, to=users.CustomUser |
| tier | CharField | max_length=20, choices=Name, default=registered |
| status | CharField | max_length=20, choices=Name, default=active |
| start_date | DateTimeField | auto_now_add=True |
| end_date | DateTimeField | null=True, blank=True |
| is_auto_renew | BooleanField | default=False |
| last_payment_date | DateTimeField | null=True, blank=True |
| payment_method | CharField | max_length=50, blank=True, null=True |
| payment_id | CharField | max_length=100, blank=True, null=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | OneToOneField | users.CustomUser | subscription |

**Frontend Usage Notes:**

- Use the model name `Subscription` for component naming (e.g., `SubscriptionList`, `SubscriptionDetail`)
- Primary API endpoint will likely follow REST conventions for `subscription`
- Contains date/time fields - use appropriate date pickers and formatting

### App: content

#### Testimonial

**Meta Options:**
- ordering: ['-featured', '-created_at']

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| name | CharField | max_length=100 |
| role | CharField | max_length=100 |
| content | TextField | - |
| rating | IntegerField | validators=['Call', 'Call'], default=5 |
| avatar | ImageField | upload_to=testimonials/, null=True, blank=True |
| featured | BooleanField | default=False |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

**Frontend Usage Notes:**

- Use the model name `Testimonial` for component naming (e.g., `TestimonialList`, `TestimonialDetail`)
- Primary API endpoint will likely follow REST conventions for `testimonial`
- Contains image fields - frontend should handle image uploads and display
- Contains date/time fields - use appropriate date pickers and formatting

#### PlatformStatistics

**Meta Options:**
- verbose_name: Platform Statistics
- verbose_name_plural: Platform Statistics

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| total_courses | PositiveIntegerField | default=0 |
| total_students | PositiveIntegerField | default=0 |
| total_instructors | PositiveIntegerField | default=0 |
| total_lessons_completed | PositiveIntegerField | default=0 |
| total_certificates_issued | PositiveIntegerField | default=0 |
| last_updated | DateTimeField | auto_now=True |

**Frontend Usage Notes:**

- Use the model name `PlatformStatistics` for component naming (e.g., `PlatformStatisticsList`, `PlatformStatisticsDetail`)
- Primary API endpoint will likely follow REST conventions for `platformstatistics`
- Contains date/time fields - use appropriate date pickers and formatting

#### UserLearningStatistics

**Meta Options:**
- verbose_name: User Learning Statistics
- verbose_name_plural: User Learning Statistics

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | OneToOneField | on_delete=Attribute, related_name=learning_stats, to=Name |
| courses_completed | PositiveIntegerField | default=0 |
| hours_spent | PositiveIntegerField | default=0 |
| average_score | FloatField | default=0.0 |
| last_updated | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | OneToOneField | Name | learning_stats |

**Frontend Usage Notes:**

- Use the model name `UserLearningStatistics` for component naming (e.g., `UserLearningStatisticsList`, `UserLearningStatisticsDetail`)
- Primary API endpoint will likely follow REST conventions for `userlearningstatistics`
- Contains date/time fields - use appropriate date pickers and formatting

#### InstructorStatistics

**Meta Options:**
- verbose_name: Instructor Statistics
- verbose_name_plural: Instructor Statistics

**Fields:**

| Field Name | Field Type | Options |
| --- | --- | --- |
| user | OneToOneField | on_delete=Attribute, related_name=instructor_stats, to=Name |
| courses_created | PositiveIntegerField | default=0 |
| total_students | PositiveIntegerField | default=0 |
| average_rating | FloatField | default=0.0 |
| last_updated | DateTimeField | auto_now=True |

**Relationships:**

| Field Name | Relation Type | Related Model | Related Name |
| --- | --- | --- | --- |
| user | OneToOneField | Name | instructor_stats |

**Frontend Usage Notes:**

- Use the model name `InstructorStatistics` for component naming (e.g., `InstructorStatisticsList`, `InstructorStatisticsDetail`)
- Primary API endpoint will likely follow REST conventions for `instructorstatistics`
- Contains date/time fields - use appropriate date pickers and formatting


<a id='serializers'></a>
## Serializers

### App: courses

#### CategorySerializer

**Model:** Category

**Fields:**
- `course_count`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'name', 'description', 'icon', 'slug', 'is_active', 'sort_order', 'course_count', 'created_date', 'updated_date']
- `read_only_fields`: ['slug', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Category data representation
- Fields listed above are directly accessible in API responses

#### ResourceSerializer

**Model:** Resource

**Fields:**
- `file_size_display`
- `duration_display`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'type', 'description', 'file', 'url', 'premium', 'order', 'file_size', 'file_size_display', 'mime_type', 'uploaded', 'storage_key', 'duration_minutes', 'duration_display', 'created_date', 'updated_date']
- `read_only_fields`: ['file_size', 'mime_type', 'uploaded', 'storage_key', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Resource data representation
- Fields listed above are directly accessible in API responses

#### AnswerSerializer

**Model:** Answer

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'answer_text', 'is_correct', 'explanation', 'order', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Answer data representation
- Fields listed above are directly accessible in API responses

#### QuestionSerializer

**Model:** Question

**Fields:**
- `answers`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'question_text', 'question_type', 'order', 'points', 'explanation', 'answers', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Question data representation
- Fields listed above are directly accessible in API responses

#### QuestionDetailSerializer

**Model:** None

**Fields:**
- `answers`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### AssessmentSerializer

**Model:** Assessment

**Fields:**
- `questions`
- `question_count`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'description', 'time_limit', 'passing_score', 'max_attempts', 'randomize_questions', 'show_results', 'questions', 'question_count', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Assessment data representation
- Fields listed above are directly accessible in API responses

#### LessonSerializer

**Model:** Lesson

**Fields:**
- `resources`
- `premium_resources`
- `is_completed`
- `assessment`
- `progress_percentage`
- `duration_display`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'content', 'guest_content', 'registered_content', 'access_level', 'duration_minutes', 'duration_display', 'type', 'order', 'has_assessment', 'has_lab', 'is_free_preview', 'video_url', 'transcript', 'resources', 'premium_resources', 'is_completed', 'assessment', 'progress_percentage', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Lesson data representation
- Fields listed above are directly accessible in API responses

#### ModuleSerializer

**Model:** Module

**Fields:**
- `lessons`
- `lesson_count`
- `duration_display`
- `course`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'description', 'order', 'duration_minutes', 'duration_display', 'is_published', 'lessons', 'lesson_count', 'course', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Module data representation
- Fields listed above are directly accessible in API responses

#### ModuleDetailSerializer

**Model:** None

**Fields:**
- `lessons`
- `completion_stats`

**Meta Options:**
- `fields`: BinOp

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### CourseInstructorSerializer

**Model:** CourseInstructor

**Fields:**
- `instructor`
- `instructor_stats`

**Meta Options:**
- `model`: Name
- `fields`: ['instructor', 'title', 'bio', 'is_lead', 'is_active', 'instructor_stats', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for CourseInstructor data representation
- Fields listed above are directly accessible in API responses

#### CourseVersionSerializer

**Model:** Course

**Fields:**
- `parent_version`
- `children`
- `version_family`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'version', 'is_draft', 'parent_version', 'children', 'title', 'slug', 'version_family', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Course data representation
- Fields listed above are directly accessible in API responses

#### CourseSerializer

**Model:** Course

**Fields:**
- `category`
- `category_id`
- `instructors`
- `slug`
- `rating`
- `enrolled_students`
- `is_enrolled`
- `module_count`
- `lesson_count`
- `duration_display`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'subtitle', 'slug', 'description', 'category', 'category_id', 'thumbnail', 'price', 'discount_price', 'discount_ends', 'level', 'duration_minutes', 'duration_display', 'has_certificate', 'is_featured', 'is_published', 'is_draft', 'published_date', 'updated_date', 'instructors', 'rating', 'enrolled_students', 'is_enrolled', 'creation_method', 'completion_status', 'completion_percentage', 'version', 'module_count', 'lesson_count', 'requirements', 'skills', 'learning_objectives', 'target_audience', 'avg_rating', 'total_reviews', 'enrolled_students_count']
- `read_only_fields`: ['version', 'published_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Course data representation
- Fields listed above are directly accessible in API responses

#### CourseDetailSerializer

**Model:** None

**Fields:**
- `modules`
- `user_progress`
- `version_info`
- `enrollment_info`
- `recent_reviews`

**Meta Options:**
- `fields`: BinOp

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### CourseCloneSerializer

**Model:** None

**Fields:**
- `title`
- `description`
- `copy_modules`
- `copy_resources`
- `copy_assessments`
- `create_as_draft`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### EnrollmentSerializer

**Model:** Enrollment

**Fields:**
- `course`
- `course_id`
- `progress_summary`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'course', 'course_id', 'status', 'completion_date', 'last_accessed', 'total_time_spent', 'progress_percentage', 'progress_summary', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date', 'last_accessed']

**Frontend Usage Notes:**

- This serializer is used for Enrollment data representation
- Fields listed above are directly accessible in API responses

#### ProgressSerializer

**Model:** Progress

**Fields:**
- `lesson`
- `lesson_id`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'lesson', 'lesson_id', 'is_completed', 'completed_date', 'time_spent', 'progress_percentage', 'notes', 'last_accessed', 'created_date', 'updated_date']
- `read_only_fields`: ['completed_date', 'last_accessed', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Progress data representation
- Fields listed above are directly accessible in API responses

#### AssessmentAttemptSerializer

**Model:** AssessmentAttempt

**Fields:**
- `assessment`
- `detailed_results`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'assessment', 'start_time', 'end_time', 'score', 'passed', 'score_percentage', 'attempt_number', 'detailed_results', 'ip_address', 'user_agent', 'created_date', 'updated_date']
- `read_only_fields`: ['start_time', 'end_time', 'score', 'passed', 'score_percentage', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for AssessmentAttempt data representation
- Fields listed above are directly accessible in API responses

#### AttemptAnswerSerializer

**Model:** AttemptAnswer

**Fields:**
- `question`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'question', 'selected_answer', 'text_answer', 'is_correct', 'points_earned', 'feedback', 'answered_at']
- `read_only_fields`: ['is_correct', 'points_earned', 'answered_at']

**Frontend Usage Notes:**

- This serializer is used for AttemptAnswer data representation
- Fields listed above are directly accessible in API responses

#### ReviewSerializer

**Model:** Review

**Fields:**
- `user`
- `helpful_votes`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'user', 'rating', 'title', 'content', 'helpful_count', 'helpful_votes', 'is_verified_purchase', 'is_approved', 'created_date', 'updated_date']
- `read_only_fields`: ['helpful_count', 'is_verified_purchase', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Review data representation
- Fields listed above are directly accessible in API responses

#### NoteSerializer

**Model:** Note

**Fields:**
- `lesson`
- `lesson_id`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'lesson', 'lesson_id', 'content', 'is_private', 'tags', 'created_date', 'updated_date']
- `read_only_fields`: ['created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Note data representation
- Fields listed above are directly accessible in API responses

#### CertificateSerializer

**Model:** Certificate

**Fields:**
- `enrollment`
- `course`
- `user`
- `verification_url`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'enrollment', 'certificate_number', 'course', 'user', 'verification_url', 'is_valid', 'verification_hash', 'template_version', 'revocation_date', 'revocation_reason', 'created_date', 'updated_date']
- `read_only_fields`: ['certificate_number', 'verification_hash', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for Certificate data representation
- Fields listed above are directly accessible in API responses

### App: instructor_portal

#### InstructorProfileSerializer

**Model:** InstructorProfile

**Fields:**
- `expertise_areas`
- `expertise_areas_display`
- `status_display`
- `tier_display`
- `performance_metrics`
- `tier_benefits`
- `next_tier_requirements`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'display_name', 'bio', 'title', 'organization', 'years_experience', 'website', 'linkedin_profile', 'twitter_handle', 'profile_image', 'cover_image', 'status', 'status_display', 'is_verified', 'tier', 'tier_display', 'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue', 'email_notifications', 'marketing_emails', 'public_profile', 'expertise_areas', 'expertise_areas_display', 'performance_metrics', 'tier_benefits', 'next_tier_requirements', 'created_date', 'updated_date', 'last_login']
- `read_only_fields`: ['id', 'status', 'is_verified', 'tier', 'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for InstructorProfile data representation
- Fields listed above are directly accessible in API responses

#### CourseInstructorSerializer

**Model:** CourseInstructor

**Fields:**
- `instructor_name`
- `instructor_email`
- `instructor_profile`
- `course_title`
- `course_slug`
- `role_display`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'course', 'instructor', 'role', 'role_display', 'is_active', 'is_lead', 'can_edit_content', 'can_manage_students', 'can_view_analytics', 'revenue_share_percentage', 'instructor_name', 'instructor_email', 'instructor_profile', 'course_title', 'course_slug', 'joined_date', 'updated_date']
- `read_only_fields`: ['id', 'joined_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for CourseInstructor data representation
- Fields listed above are directly accessible in API responses

#### InstructorDashboardSerializer

**Model:** InstructorDashboard

**Fields:**
- `dashboard_data`
- `available_widgets`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'show_analytics', 'show_recent_students', 'show_performance_metrics', 'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments', 'notify_new_reviews', 'notify_course_completions', 'widget_order', 'custom_colors', 'dashboard_data', 'available_widgets', 'created_date', 'updated_date']
- `read_only_fields`: ['id', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for InstructorDashboard data representation
- Fields listed above are directly accessible in API responses

#### CourseCreationSessionSerializer

**Model:** CourseCreationSession

**Fields:**
- `instructor_name`
- `instructor_tier`
- `creation_method_display`
- `status_display`
- `validation_status`
- `step_configuration`
- `resume_data`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'session_id', 'instructor', 'instructor_name', 'instructor_tier', 'creation_method', 'creation_method_display', 'status', 'status_display', 'course_data', 'current_step', 'total_steps', 'completed_steps', 'progress_percentage', 'last_auto_save', 'auto_save_data', 'validation_errors', 'quality_score', 'ai_prompt', 'ai_suggestions', 'template_used', 'draft_course', 'published_course', 'validation_status', 'step_configuration', 'resume_data', 'created_date', 'updated_date', 'expires_at']
- `read_only_fields`: ['id', 'session_id', 'progress_percentage', 'last_auto_save', 'validation_errors', 'published_course', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for CourseCreationSession data representation
- Fields listed above are directly accessible in API responses

#### CourseTemplateSerializer

**Model:** CourseTemplate

**Fields:**
- `category_name`
- `template_type_display`
- `created_by_name`
- `usage_analytics`
- `preview_data`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'name', 'description', 'template_type', 'template_type_display', 'category', 'category_name', 'template_data', 'estimated_duration', 'difficulty_level', 'usage_count', 'success_rate', 'is_active', 'created_by', 'created_by_name', 'usage_analytics', 'preview_data', 'created_date', 'updated_date']
- `read_only_fields`: ['id', 'usage_count', 'success_rate', 'created_by', 'created_date', 'updated_date']

**Frontend Usage Notes:**

- This serializer is used for CourseTemplate data representation
- Fields listed above are directly accessible in API responses

#### DraftCourseContentSerializer

**Model:** DraftCourseContent

**Fields:**
- `session_info`
- `content_type_display`
- `content_hash`
- `version_history`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'session', 'session_info', 'content_type', 'content_type_display', 'content_id', 'version', 'content_data', 'title', 'order', 'is_complete', 'validation_errors', 'auto_save_version', 'content_hash', 'version_history', 'last_saved']
- `read_only_fields`: ['id', 'auto_save_version', 'last_saved']

**Frontend Usage Notes:**

- This serializer is used for DraftCourseContent data representation
- Fields listed above are directly accessible in API responses

#### CourseContentDraftSerializer

**Model:** CourseContentDraft

**Fields:**
- `session_info`
- `content_type_display`
- `processing_status_display`
- `file_info`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'session', 'session_info', 'content_type', 'content_type_display', 'file_path', 'content_hash', 'version', 'is_processed', 'processing_status', 'processing_status_display', 'file_size', 'mime_type', 'file_info', 'created_date', 'processed_date']
- `read_only_fields`: ['id', 'content_hash', 'is_processed', 'processing_status', 'file_size', 'created_date', 'processed_date']

**Frontend Usage Notes:**

- This serializer is used for CourseContentDraft data representation
- Fields listed above are directly accessible in API responses

#### InstructorResourceSerializer

**Model:** Resource

**Fields:**
- `lesson_title`
- `course_title`
- `upload_info`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'type', 'file', 'url', 'description', 'premium', 'storage_key', 'uploaded', 'file_size', 'mime_type', 'order', 'duration_minutes', 'lesson_title', 'course_title', 'upload_info']
- `read_only_fields`: ['id', 'uploaded']

**Frontend Usage Notes:**

- This serializer is used for Resource data representation
- Fields listed above are directly accessible in API responses

#### InstructorLessonSerializer

**Model:** Lesson

**Fields:**
- `resources`
- `module_title`
- `course_title`
- `progress_analytics`
- `content_analytics`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'content', 'guest_content', 'registered_content', 'access_level', 'duration_minutes', 'type', 'order', 'has_assessment', 'has_lab', 'is_free_preview', 'video_url', 'transcript', 'resources', 'module_title', 'course_title', 'progress_analytics', 'content_analytics']
- `read_only_fields`: ['id']

**Frontend Usage Notes:**

- This serializer is used for Lesson data representation
- Fields listed above are directly accessible in API responses

#### InstructorModuleSerializer

**Model:** Module

**Fields:**
- `lessons_count`
- `lessons`
- `course_title`
- `completion_analytics`
- `content_summary`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'description', 'order', 'duration_minutes', 'is_published', 'lessons_count', 'lessons', 'course_title', 'completion_analytics', 'content_summary']
- `read_only_fields`: ['id']

**Frontend Usage Notes:**

- This serializer is used for Module data representation
- Fields listed above are directly accessible in API responses

#### InstructorCourseSerializer

**Model:** Course

**Fields:**
- `modules_count`
- `modules`
- `modules_json`
- `modules_json_gz`
- `category_id`
- `category_name`
- `instructors`
- `instructor_role`
- `can_edit`
- `course_analytics`
- `enrolled_students_count`
- `avg_rating`
- `total_reviews`
- `revenue_analytics`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'title', 'subtitle', 'slug', 'description', 'short_description', 'category', 'category_id', 'category_name', 'thumbnail', 'price', 'discount_price', 'discount_ends', 'level', 'duration_minutes', 'has_certificate', 'is_published', 'is_draft', 'creation_method', 'completion_status', 'completion_percentage', 'version', 'parent_version', 'modules_count', 'modules', 'requirements', 'skills', 'learning_objectives', 'target_audience', 'modules_json', 'modules_json_gz', 'instructors', 'instructor_role', 'can_edit', 'enrolled_students_count', 'avg_rating', 'total_reviews', 'course_analytics', 'revenue_analytics', 'created_date', 'updated_date', 'published_date']
- `read_only_fields`: ['id', 'slug', 'version', 'parent_version', 'enrolled_students_count', 'avg_rating', 'total_reviews', 'created_date', 'updated_date', 'published_date']

**Frontend Usage Notes:**

- This serializer is used for Course data representation
- Fields listed above are directly accessible in API responses

### App: ai_course_builder

#### AICourseBuilderDraftSerializer

**Model:** AICourseBuilderDraft

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'instructor', 'created_at', 'updated_at', 'status', 'title', 'description', 'course_objectives', 'target_audience', 'difficulty_level', 'duration_minutes', 'price', 'outline', 'content', 'assessments', 'has_outline', 'has_modules', 'has_lessons', 'has_assessments', 'generation_metadata']
- `read_only_fields`: ['id', 'instructor', 'created_at', 'updated_at']

**Frontend Usage Notes:**

- This serializer is used for AICourseBuilderDraft data representation
- Fields listed above are directly accessible in API responses

### App: users

#### ProfileSerializer

**Model:** Profile

**Meta Options:**
- `model`: Name
- `exclude`: ['user', 'created_at', 'updated_at']

**Frontend Usage Notes:**

- This serializer is used for Profile data representation
- Fields listed above are directly accessible in API responses

#### SubscriptionSerializer

**Model:** Subscription

**Fields:**
- `is_active`
- `days_remaining`

**Meta Options:**
- `model`: Name
- `fields`: ['tier', 'status', 'start_date', 'end_date', 'is_auto_renew', 'last_payment_date', 'is_active', 'days_remaining']

**Frontend Usage Notes:**

- This serializer is used for Subscription data representation
- Fields listed above are directly accessible in API responses

#### UserSerializer

**Model:** User

**Fields:**
- `profile`
- `subscription`

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified', 'date_joined', 'last_login', 'profile', 'subscription']
- `read_only_fields`: ['id', 'date_joined', 'last_login', 'is_email_verified']

**Frontend Usage Notes:**

- This serializer is used for User data representation
- Fields listed above are directly accessible in API responses

#### UserDetailSerializer

**Model:** None

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### UserCreateSerializer

**Model:** User

**Fields:**
- `password`
- `password_confirm`

**Meta Options:**
- `model`: Name
- `fields`: ['email', 'username', 'password', 'password_confirm', 'first_name', 'last_name', 'role']
- `extra_kwargs`: {'first_name': {'required': True}, 'last_name': {'required': True}, 'role': {'required': True}}

**Frontend Usage Notes:**

- This serializer is used for User data representation
- Fields listed above are directly accessible in API responses

#### UpdateProfileSerializer

**Model:** User

**Fields:**
- `first_name`
- `last_name`
- `profile`

**Meta Options:**
- `model`: Name
- `fields`: ['first_name', 'last_name', 'profile']

**Frontend Usage Notes:**

- This serializer is used for User data representation
- Fields listed above are directly accessible in API responses

#### EmailVerificationSerializer

**Model:** None

**Fields:**
- `token`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### PasswordChangeSerializer

**Model:** None

**Fields:**
- `old_password`
- `new_password`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### PasswordResetRequestSerializer

**Model:** None

**Fields:**
- `email`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### PasswordResetConfirmSerializer

**Model:** None

**Fields:**
- `token`
- `password`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### LoginSerializer

**Model:** None

**Fields:**
- `email`
- `password`
- `remember_me`

**Frontend Usage Notes:**

- This serializer is used for None data representation
- Fields listed above are directly accessible in API responses

#### UserSessionSerializer

**Model:** UserSession

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'session_key', 'ip_address', 'user_agent', 'created_at', 'expires_at', 'last_activity', 'is_active', 'device_type', 'location']
- `read_only_fields`: ['id', 'created_at', 'last_activity']

**Frontend Usage Notes:**

- This serializer is used for UserSession data representation
- Fields listed above are directly accessible in API responses

### App: content

#### TestimonialSerializer

**Model:** Testimonial

**Meta Options:**
- `model`: Name
- `fields`: ['id', 'name', 'role', 'content', 'rating', 'avatar', 'created_at']
- `read_only_fields`: ['id', 'created_at']

**Frontend Usage Notes:**

- This serializer is used for Testimonial data representation
- Fields listed above are directly accessible in API responses

#### PlatformStatisticsSerializer

**Model:** PlatformStatistics

**Meta Options:**
- `model`: Name
- `fields`: ['total_courses', 'total_students', 'total_instructors', 'total_lessons_completed', 'total_certificates_issued', 'last_updated']
- `read_only_fields`: ['last_updated']

**Frontend Usage Notes:**

- This serializer is used for PlatformStatistics data representation
- Fields listed above are directly accessible in API responses

#### UserLearningStatisticsSerializer

**Model:** UserLearningStatistics

**Meta Options:**
- `model`: Name
- `fields`: ['courses_completed', 'hours_spent', 'average_score', 'last_updated']
- `read_only_fields`: ['last_updated']

**Frontend Usage Notes:**

- This serializer is used for UserLearningStatistics data representation
- Fields listed above are directly accessible in API responses

#### InstructorStatisticsSerializer

**Model:** InstructorStatistics

**Meta Options:**
- `model`: Name
- `fields`: ['courses_created', 'total_students', 'average_rating', 'last_updated']
- `read_only_fields`: ['last_updated']

**Frontend Usage Notes:**

- This serializer is used for InstructorStatistics data representation
- Fields listed above are directly accessible in API responses


<a id='entity-relationship-diagram'></a>
## Entity-Relationship Diagram

# Entity-Relationship Diagram

## App: instructor_portal
```
[InstructorProfile]
  user: OneToOneField (on_delete=Attribute, related_name=instructor_profile, verbose_name=Call, db_index=True, to=Name)
  display_name: CharField (max_length=100, verbose_name=Call, help_text=Call)
  bio: TextField (max_length=2000, blank=True, verbose_name=Call, help_text=Call)
  expertise_areas: ManyToManyField (blank=True, related_name=expert_instructors, verbose_name=Call, to=courses.Category)
  title: CharField (max_length=150, blank=True, verbose_name=Call, help_text=Call)
  organization: CharField (max_length=200, blank=True, verbose_name=Call)
  years_experience: PositiveIntegerField (default=0, validators=['Call'], verbose_name=Call)
  website: URLField (blank=True, validators=['Call'], verbose_name=Call)
  linkedin_profile: URLField (blank=True, validators=['Call'], verbose_name=Call)
  twitter_handle: CharField (max_length=50, blank=True, verbose_name=Call)
  profile_image: ImageField (upload_to=Name, blank=True, null=True, verbose_name=Call)
  cover_image: ImageField (upload_to=Name, blank=True, null=True, verbose_name=Call)
  status: CharField (max_length=30, choices=Attribute, default=Attribute, verbose_name=Call)
  is_verified: BooleanField (default=False, verbose_name=Call, help_text=Call)
  tier: CharField (max_length=30, choices=Attribute, default=Attribute, verbose_name=Call)
  email_notifications: BooleanField (default=True, verbose_name=Call)
  marketing_emails: BooleanField (default=False, verbose_name=Call)
  public_profile: BooleanField (default=True, verbose_name=Call, help_text=Call)
  approved_by: ForeignKey (on_delete=Attribute, null=True, blank=True, related_name=approved_instructors, verbose_name=Call, to=Name)
  approval_date: DateTimeField (null=True, blank=True, verbose_name=Call)
  suspension_reason: TextField (blank=True, verbose_name=Call)
  created_date: DateTimeField (auto_now_add=True, verbose_name=Call)
  updated_date: DateTimeField (auto_now=True, verbose_name=Call)
  last_login: DateTimeField (null=True, blank=True, verbose_name=Call)

[InstructorAnalytics]
  instructor: OneToOneField (on_delete=Attribute, related_name=analytics, verbose_name=Call, to=Name)
  total_students: PositiveIntegerField (default=0, verbose_name=Call)
  total_courses: PositiveIntegerField (default=0, verbose_name=Call)
  average_rating: DecimalField (max_digits=3, decimal_places=2, default=Call, validators=['Call', 'Call'], verbose_name=Call)
  total_reviews: PositiveIntegerField (default=0, verbose_name=Call)
  total_revenue: DecimalField (max_digits=12, decimal_places=2, default=Call, validators=['Call'], verbose_name=Call)
  completion_rate: DecimalField (max_digits=5, decimal_places=2, default=Call, verbose_name=Call)
  student_satisfaction_rate: DecimalField (max_digits=5, decimal_places=2, default=Call, verbose_name=Call)
  monthly_revenue: DecimalField (max_digits=12, decimal_places=2, default=Call, verbose_name=Call)
  last_updated: DateTimeField (auto_now=True, verbose_name=Call)
  last_calculated: DateTimeField (null=True, blank=True, verbose_name=Call)

[InstructorAnalyticsHistory]
  instructor: ForeignKey (on_delete=Attribute, related_name=analytics_history, verbose_name=Call, to=Name)
  date: DateTimeField (default=Attribute, verbose_name=Call)
  total_students: PositiveIntegerField (default=0)
  total_courses: PositiveIntegerField (default=0)
  average_rating: DecimalField (max_digits=3, decimal_places=2, default=Call)
  total_revenue: DecimalField (max_digits=12, decimal_places=2, default=Call)
  completion_rate: DecimalField (max_digits=5, decimal_places=2, default=Call)
  data_type: CharField (max_length=50, default=daily, verbose_name=Call, help_text=Call)
  additional_data: JSONField (default=Name, blank=True, verbose_name=Call)

[CourseInstructor]
  course: ForeignKey (on_delete=Attribute, verbose_name=Call, to=courses.Course)
  instructor: ForeignKey (on_delete=Attribute, verbose_name=Call, to=Name)
  role: CharField (max_length=30, choices=Attribute, default=Attribute, verbose_name=Call)
  is_active: BooleanField (default=True, verbose_name=Call)
  is_lead: BooleanField (default=False, verbose_name=Call)
  can_edit_content: BooleanField (default=True)
  can_manage_students: BooleanField (default=True)
  can_view_analytics: BooleanField (default=True)
  revenue_share_percentage: DecimalField (max_digits=5, decimal_places=2, default=Call, validators=['Call', 'Call'])
  joined_date: DateTimeField (auto_now_add=True)
  updated_date: DateTimeField (auto_now=True)

[InstructorDashboard]
  instructor: OneToOneField (on_delete=Attribute, related_name=dashboard, verbose_name=Call, to=Name)
  show_analytics: BooleanField (default=True)
  show_recent_students: BooleanField (default=True)
  show_performance_metrics: BooleanField (default=True)
  show_revenue_charts: BooleanField (default=True)
  show_course_progress: BooleanField (default=True)
  notify_new_enrollments: BooleanField (default=True)
  notify_new_reviews: BooleanField (default=True)
  notify_course_completions: BooleanField (default=True)
  widget_order: JSONField (default=Name, blank=True)
  custom_colors: JSONField (default=Name, blank=True)
  created_date: DateTimeField (auto_now_add=True)
  updated_date: DateTimeField (auto_now=True)

[CourseCreationSession]
  session_id: UUIDField (default=Attribute, unique=True)
  instructor: ForeignKey (on_delete=Attribute, related_name=creation_sessions, to=Name)
  creation_method: CharField (max_length=30, choices=Attribute)
  status: CharField (max_length=30, choices=Attribute, default=Attribute)
  course_data: JSONField (default=Name)
  current_step: PositiveIntegerField (default=1)
  total_steps: PositiveIntegerField (default=0)
  completed_steps: JSONField (default=Name)
  progress_percentage: DecimalField (max_digits=5, decimal_places=2, default=Call)
  last_auto_save: DateTimeField (null=True, blank=True)
  auto_save_data: JSONField (default=Name)
  validation_errors: JSONField (default=Name)
  quality_score: DecimalField (max_digits=5, decimal_places=2, null=True, blank=True)
  ai_prompt: TextField (blank=True)
  ai_suggestions: JSONField (default=Name)
  template_used: CharField (max_length=100, blank=True)
  reference_courses: ManyToManyField (blank=True, related_name=referenced_in_creation, to=courses.Course)
  draft_course: ForeignKey (on_delete=Attribute, null=True, blank=True, related_name=active_sessions, to=courses.Course)
  published_course: OneToOneField (on_delete=Attribute, null=True, blank=True, related_name=creation_session, to=courses.Course)
  created_date: DateTimeField (auto_now_add=True)
  updated_date: DateTimeField (auto_now=True)
  completed_date: DateTimeField (null=True, blank=True)
  expires_at: DateTimeField

[CourseTemplate]
  name: CharField (max_length=100)
  description: TextField
  template_type: CharField (max_length=30, choices=Attribute)
  category: ForeignKey (on_delete=Attribute, related_name=templates, to=courses.Category)
  template_data: JSONField
  estimated_duration: PositiveIntegerField
  difficulty_level: CharField (max_length=30, default=beginner)
  usage_count: PositiveIntegerField (default=0)
  success_rate: DecimalField (max_digits=5, decimal_places=2, default=Call)
  is_active: BooleanField (default=True)
  created_by: ForeignKey (on_delete=Attribute, null=True, related_name=created_templates, to=Name)
  created_date: DateTimeField (auto_now_add=True)
  updated_date: DateTimeField (auto_now=True)

[DraftCourseContent]
  session: ForeignKey (on_delete=Attribute, related_name=draft_content, verbose_name=Call, to=Name)
  content_type: CharField (max_length=30, choices=Attribute, verbose_name=Call)
  content_id: CharField (max_length=50, verbose_name=Call, help_text=Call)
  version: PositiveIntegerField (default=1, verbose_name=Call, help_text=Call)
  content_data: JSONField (verbose_name=Call, help_text=Call)
  title: CharField (max_length=200, blank=True, verbose_name=Call)
  order: PositiveIntegerField (default=1, verbose_name=Call)
  is_complete: BooleanField (default=False, verbose_name=Call, help_text=Call)
  validation_errors: JSONField (default=Name, verbose_name=Call, help_text=Call)
  auto_save_version: PositiveIntegerField (default=1, verbose_name=Call, help_text=Call)
  last_saved: DateTimeField (auto_now=True, verbose_name=Call)
  ai_generated: BooleanField (default=False, verbose_name=Call, help_text=Call)
  ai_prompt: TextField (blank=True, verbose_name=Call, help_text=Call)

[CourseContentDraft]
  session: ForeignKey (on_delete=Attribute, related_name=content_drafts, verbose_name=Call, to=Name)
  content_type: CharField (max_length=30, choices=Attribute, verbose_name=Call)
  file_path: FileField (upload_to=course_drafts/%Y/%m/%d/, null=True, blank=True, verbose_name=Call)
  content_hash: CharField (max_length=64, verbose_name=Call, help_text=Call)
  version: PositiveIntegerField (default=1, verbose_name=Call)
  is_processed: BooleanField (default=False, verbose_name=Call, help_text=Call)
  processing_status: CharField (max_length=30, choices=[('pending', 'Call'), ('processing', 'Call'), ('completed', 'Call'), ('failed', 'Call'), ('virus_scan', 'Call'), ('format_conversion', 'Call')], default=pending, verbose_name=Call)
  processing_error: TextField (blank=True, verbose_name=Call, help_text=Call)
  file_size: PositiveIntegerField (null=True, blank=True, verbose_name=Call)
  mime_type: CharField (max_length=100, blank=True, verbose_name=Call)
  original_filename: CharField (max_length=255, blank=True, verbose_name=Call)
  processing_metadata: JSONField (default=Name, blank=True, verbose_name=Call, help_text=Call)
  created_date: DateTimeField (auto_now_add=True, verbose_name=Call)
  processed_date: DateTimeField (null=True, blank=True, verbose_name=Call)

[InstructorNotification]
  instructor: ForeignKey (on_delete=Attribute, related_name=notifications, verbose_name=Call, to=Name)
  notification_type: CharField (max_length=30, choices=Attribute, verbose_name=Call)
  priority: CharField (max_length=20, choices=Attribute, default=Attribute, verbose_name=Call)
  title: CharField (max_length=200, verbose_name=Call)
  message: TextField (verbose_name=Call)
  action_url: URLField (blank=True, verbose_name=Call, help_text=Call)
  action_text: CharField (max_length=50, blank=True, verbose_name=Call, help_text=Call)
  metadata: JSONField (default=Name, blank=True, verbose_name=Call, help_text=Call)
  is_read: BooleanField (default=False, verbose_name=Call)
  read_at: DateTimeField (null=True, blank=True, verbose_name=Call)
  is_dismissed: BooleanField (default=False, verbose_name=Call)
  dismissed_at: DateTimeField (null=True, blank=True, verbose_name=Call)
  email_sent: BooleanField (default=False, verbose_name=Call)
  email_sent_at: DateTimeField (null=True, blank=True, verbose_name=Call)
  created_date: DateTimeField (auto_now_add=True, verbose_name=Call)
  expires_at: DateTimeField (null=True, blank=True, verbose_name=Call, help_text=Call)

[InstructorSession]
  instructor: ForeignKey (on_delete=Attribute, related_name=sessions, verbose_name=Call, to=Name)
  session_key: CharField (max_length=40, unique=True, verbose_name=Call)
  ip_address: GenericIPAddressField (verbose_name=Call)
  user_agent: TextField (blank=True, verbose_name=Call)
  device_type: CharField (max_length=20, choices=[('desktop', 'Call'), ('mobile', 'Call'), ('tablet', 'Call'), ('unknown', 'Call')], default=unknown, verbose_name=Call)
  location: CharField (max_length=100, blank=True, verbose_name=Call, help_text=Call)
  login_time: DateTimeField (auto_now_add=True, verbose_name=Call)
  last_activity: DateTimeField (auto_now=True, verbose_name=Call)
  logout_time: DateTimeField (null=True, blank=True, verbose_name=Call)
  is_active: BooleanField (default=True, verbose_name=Call)
  is_suspicious: BooleanField (default=False, verbose_name=Call, help_text=Call)
  security_notes: TextField (blank=True, verbose_name=Call)

# Relationships
[InstructorProfile] -- [Name] : user (as instructor_profile)
[InstructorProfile] <-> [courses.Category] : expertise_areas (as expert_instructors)
[InstructorProfile] -> [Name] : approved_by (as approved_instructors)
[InstructorAnalytics] -- [Name] : instructor (as analytics)
[InstructorAnalyticsHistory] -> [Name] : instructor (as analytics_history)
[CourseInstructor] -> [courses.Course] : course
[CourseInstructor] -> [Name] : instructor
[InstructorDashboard] -- [Name] : instructor (as dashboard)
[CourseCreationSession] -> [Name] : instructor (as creation_sessions)
[CourseCreationSession] <-> [courses.Course] : reference_courses (as referenced_in_creation)
[CourseCreationSession] -> [courses.Course] : draft_course (as active_sessions)
[CourseCreationSession] -- [courses.Course] : published_course (as creation_session)
[CourseTemplate] -> [courses.Category] : category (as templates)
[CourseTemplate] -> [Name] : created_by (as created_templates)
[DraftCourseContent] -> [Name] : session (as draft_content)
[CourseContentDraft] -> [Name] : session (as content_drafts)
[InstructorNotification] -> [Name] : instructor (as notifications)
[InstructorSession] -> [Name] : instructor (as sessions)
```

## App: ai_course_builder
```
[AICourseBuilderDraft]
  STATUS_CHOICES: Unknown
  LEVEL_CHOICES: Unknown
  instructor: ForeignKey (on_delete=Attribute, related_name=ai_course_drafts, to=Name)
  created_at: DateTimeField (auto_now_add=True)
  updated_at: DateTimeField (auto_now=True)
  status: CharField (max_length=20, choices=Name, default=DRAFT)
  title: CharField (max_length=255, null=True, blank=True)
  description: TextField (null=True, blank=True)
  course_objectives: JSONField (default=Name, blank=True, null=True)
  target_audience: JSONField (default=Name, blank=True, null=True)
  difficulty_level: CharField (max_length=20, choices=Name, default=all_levels, null=True, blank=True)
  duration_minutes: PositiveIntegerField (null=True, blank=True)
  price: DecimalField (max_digits=10, decimal_places=2, null=True, blank=True)
  outline: JSONField (default=Name, blank=True, null=True)
  content: JSONField (default=Name, blank=True, null=True)
  assessments: JSONField (default=Name, blank=True, null=True)
  has_outline: BooleanField (default=False)
  has_modules: BooleanField (default=False)
  has_lessons: BooleanField (default=False)
  has_assessments: BooleanField (default=False)
  generation_metadata: JSONField (default=Name, blank=True, null=True)

# Relationships
[AICourseBuilderDraft] -> [Name] : instructor (as ai_course_drafts)
```

## App: users
```
[Profile]
  user: OneToOneField (on_delete=Attribute, related_name=profile, to=Attribute)
  profile_picture: ImageField (upload_to=profile_pictures/, null=True, blank=True)
  bio: TextField (blank=True)
  date_of_birth: DateField (null=True, blank=True)
  phone_number: CharField (max_length=20, blank=True)
  address: TextField (blank=True)
  city: CharField (max_length=100, blank=True)
  state: CharField (max_length=100, blank=True)
  country: CharField (max_length=100, blank=True)
  postal_code: CharField (max_length=20, blank=True)
  website: URLField (blank=True)
  linkedin: URLField (blank=True)
  twitter: CharField (max_length=100, blank=True)
  github: CharField (max_length=100, blank=True)
  expertise: CharField (max_length=200, blank=True)
  teaching_experience: PositiveIntegerField (default=0)
  educational_background: TextField (blank=True)
  interests: TextField (blank=True)
  receive_email_notifications: BooleanField (default=True)
  receive_marketing_emails: BooleanField (default=False)
  created_at: DateTimeField (auto_now_add=True)
  updated_at: DateTimeField (auto_now=True)

[EmailVerification]
  user: ForeignKey (on_delete=Attribute, related_name=email_verifications, to=Attribute)
  token: UUIDField (default=Attribute, editable=False, unique=True)
  created_at: DateTimeField (auto_now_add=True)
  expires_at: DateTimeField
  verified_at: DateTimeField (null=True, blank=True)
  is_used: BooleanField (default=False)

[PasswordReset]
  user: ForeignKey (on_delete=Attribute, related_name=password_resets, to=Attribute)
  token: UUIDField (default=Attribute, editable=False, unique=True)
  created_at: DateTimeField (auto_now_add=True)
  expires_at: DateTimeField
  used_at: DateTimeField (null=True, blank=True)
  is_used: BooleanField (default=False)
  ip_address: GenericIPAddressField (null=True, blank=True)

[LoginLog]
  user: ForeignKey (on_delete=Attribute, related_name=login_logs, to=Attribute)
  timestamp: DateTimeField (auto_now_add=True)
  ip_address: GenericIPAddressField
  user_agent: TextField
  successful: BooleanField (default=False)

[UserSession]
  user: ForeignKey (on_delete=Attribute, related_name=sessions, to=Attribute)
  session_key: CharField (max_length=255)
  ip_address: GenericIPAddressField
  user_agent: TextField
  created_at: DateTimeField (auto_now_add=True)
  expires_at: DateTimeField
  last_activity: DateTimeField (auto_now=True)
  is_active: BooleanField (default=True)
  device_type: CharField (max_length=50, blank=True)
  location: CharField (max_length=100, blank=True)
  login_method: CharField (max_length=50, blank=True, null=True)

[Subscription]
  SUBSCRIPTION_TIERS: Unknown
  STATUS_CHOICES: Unknown
  user: OneToOneField (on_delete=Attribute, related_name=subscription, to=users.CustomUser)
  tier: CharField (max_length=20, choices=Name, default=registered)
  status: CharField (max_length=20, choices=Name, default=active)
  start_date: DateTimeField (auto_now_add=True)
  end_date: DateTimeField (null=True, blank=True)
  is_auto_renew: BooleanField (default=False)
  last_payment_date: DateTimeField (null=True, blank=True)
  payment_method: CharField (max_length=50, blank=True, null=True)
  payment_id: CharField (max_length=100, blank=True, null=True)

# Relationships
[Profile] -- [Attribute] : user (as profile)
[EmailVerification] -> [Attribute] : user (as email_verifications)
[PasswordReset] -> [Attribute] : user (as password_resets)
[LoginLog] -> [Attribute] : user (as login_logs)
[UserSession] -> [Attribute] : user (as sessions)
[Subscription] -- [users.CustomUser] : user (as subscription)
```

## App: content
```
[Testimonial]
  name: CharField (max_length=100)
  role: CharField (max_length=100)
  content: TextField
  rating: IntegerField (validators=['Call', 'Call'], default=5)
  avatar: ImageField (upload_to=testimonials/, null=True, blank=True)
  featured: BooleanField (default=False)
  created_at: DateTimeField (auto_now_add=True)
  updated_at: DateTimeField (auto_now=True)

[PlatformStatistics]
  total_courses: PositiveIntegerField (default=0)
  total_students: PositiveIntegerField (default=0)
  total_instructors: PositiveIntegerField (default=0)
  total_lessons_completed: PositiveIntegerField (default=0)
  total_certificates_issued: PositiveIntegerField (default=0)
  last_updated: DateTimeField (auto_now=True)

[UserLearningStatistics]
  user: OneToOneField (on_delete=Attribute, related_name=learning_stats, to=Name)
  courses_completed: PositiveIntegerField (default=0)
  hours_spent: PositiveIntegerField (default=0)
  average_score: FloatField (default=0.0)
  last_updated: DateTimeField (auto_now=True)

[InstructorStatistics]
  user: OneToOneField (on_delete=Attribute, related_name=instructor_stats, to=Name)
  courses_created: PositiveIntegerField (default=0)
  total_students: PositiveIntegerField (default=0)
  average_rating: FloatField (default=0.0)
  last_updated: DateTimeField (auto_now=True)

# Relationships
[UserLearningStatistics] -- [Name] : user (as learning_stats)
[InstructorStatistics] -- [Name] : user (as instructor_stats)
```


<a id='authentication'></a>
## Authentication

### Authentication Mechanisms

- **Django Authentication**: Standard Django authentication system
- **Social Authentication**: Authentication via social providers
  - Frontend will need to implement social login buttons and flows
- **Django Allauth**: Extended authentication supporting social accounts
- **JWT Authentication**: JSON Web Token based authentication
  - Frontend should send the token in the `Authorization` header: `Bearer <token_value>`
  - Tokens are typically stored in localStorage or cookies

### User Model

- **Custom User Model**: `users.CustomUser`
  - Frontend should check for custom user fields when handling user data

### Frontend Integration Notes

1. **Authentication Flow**:
   - User submits login credentials
   - Backend returns a token
   - Frontend stores the token (localStorage, httpOnly cookie, etc.)
   - Frontend sends the token with each request in the Authorization header

2. **Authorization**:
   - Check permissions for each endpoint in the API Endpoints section above
   - Handle unauthorized access gracefully with appropriate UI feedback

3. **Common Auth Endpoints**:
| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/login/` | Login with username/email and password |
| POST | `/api/auth/logout/` | Logout and invalidate token/session |
| POST | `/api/auth/register/` | Create a new user account |
| POST | `/api/auth/password/reset/` | Request a password reset email |
| POST | `/api/auth/password/reset/confirm/` | Confirm password reset with token |


<a id='security-matrix'></a>
## Security Matrix

## API Security Matrix

- Total endpoints: 56
- Protected endpoints: 4
- Public endpoints: 52
- Unique permission classes: 3

### Permission Classes

| Permission Class | Endpoints Using | Authentication Required |
| --- | --- | --- |
| IsOwnerOrAdmin | 1 | No |
| AllowAny | 7 | No |
| IsAuthenticated | 4 | Yes |

### Protected Endpoints

| Method | Path | Permissions |
| --- | --- | --- |
| GET | api/instructor/ai-course-builder/health/ | IsAuthenticated |
| POST | logout/ | IsAuthenticated |
| GET | me/ | IsAuthenticated, IsOwnerOrAdmin |
| POST | password/change/ | IsAuthenticated |

### Public Endpoints

| Method | Path | Permissions |
| --- | --- | --- |
| GET | admin/ | None |
| GET | test-static/ | None |
| GET | test-admin-static/ | None |
| GET | instructor/debug/courses/ | None |
| GET | instructor/debug/courses/simple/ | None |
| GET | api/ | None |
| GET | api/token/ | None |
| GET | api/token/refresh/ | None |
| GET | api/system/db-status/ | None |
| GET | api/system/db-stats/ | None |
| GET | api/user/ | None |
| GET | api/instructor/ | None |
| GET | api/debug/courses/ | None |
| GET | api-auth/ | None |
| GET | JoinedStr | None |
| GET | auth/register/ | None |
| GET | auth/verify/<uuid:verification_token>/ | None |
| GET | auth/status/ | None |
| GET | auth/approval/ | None |
| GET | analytics/reports/ | None |
| GET | analytics/revenue/ | None |
| GET | students/ | None |
| GET | create/wizard/ | None |
| GET | create/ai/ | None |
| GET | create/dnd/ | None |
| GET | create/template/ | None |
| GET | create/import/ | None |
| GET | courses/ | None |
| GET | drafts/ | None |
| GET | uploads/ | None |
| GET | profile/ | None |
| GET | settings/ | None |
| GET | templates/ | None |
| GET | bulk/ | None |
| GET | utils/ | None |
| GET | ai/ | None |
| GET | reports/ | None |
| GET | integrations/ | None |
| GET | debug/ | None |
| GET | health/ | None |
| GET | register/ | AllowAny |
| POST | login/ | AllowAny |
| GET | token/ | None |
| GET | token/refresh/ | None |
| POST | password/reset/ | AllowAny |
| POST | password/reset/confirm/ | AllowAny |
| POST | email/verify/ | AllowAny |
| POST | email/verify/resend/ | AllowAny |
| GET | testimonials/featured/ | AllowAny |
| GET | statistics/platform/ | None |
| GET | statistics/user/learning/ | None |
| GET | statistics/instructor/ | None |


---

<a id='backend-compatibility'></a>
# BACKEND COMPATIBILITY

<a id='issues'></a>
## Issues

### ERROR Issues (68)

#### Serializer Model Mismatch (23)

- Serializer courses.CategorySerializer references model Category which was not found
- Serializer courses.ResourceSerializer references model Resource which was not found
- Serializer courses.AnswerSerializer references model Answer which was not found
- Serializer courses.QuestionSerializer references model Question which was not found
- Serializer courses.AssessmentSerializer references model Assessment which was not found
- Serializer courses.LessonSerializer references model Lesson which was not found
- Serializer courses.ModuleSerializer references model Module which was not found
- Serializer courses.CourseVersionSerializer references model Course which was not found
- Serializer courses.CourseSerializer references model Course which was not found
- Serializer courses.EnrollmentSerializer references model Enrollment which was not found
- Serializer courses.ProgressSerializer references model Progress which was not found
- Serializer courses.AssessmentAttemptSerializer references model AssessmentAttempt which was not found
- Serializer courses.AttemptAnswerSerializer references model AttemptAnswer which was not found
- Serializer courses.ReviewSerializer references model Review which was not found
- Serializer courses.NoteSerializer references model Note which was not found
- Serializer courses.CertificateSerializer references model Certificate which was not found
- Serializer instructor_portal.InstructorResourceSerializer references model Resource which was not found
- Serializer instructor_portal.InstructorLessonSerializer references model Lesson which was not found
- Serializer instructor_portal.InstructorModuleSerializer references model Module which was not found
- Serializer instructor_portal.InstructorCourseSerializer references model Course which was not found
- Serializer users.UserSerializer references model User which was not found
- Serializer users.UserCreateSerializer references model User which was not found
- Serializer users.UpdateProfileSerializer references model User which was not found

**Suggestions:**
- Ensure the model is properly imported in the serializer file
- Check for typos in the model name
- Make sure the model exists in the project

#### Field Mismatch (45)

- Serializer CourseInstructorSerializer references field 'title' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'bio' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'instructor_stats' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'created_date' which does not exist in model CourseInstructor
- Serializer InstructorProfileSerializer references field 'status_display' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'tier_display' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'total_students' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'total_courses' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'average_rating' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'total_reviews' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'total_revenue' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'expertise_areas_display' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'performance_metrics' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'tier_benefits' which does not exist in model InstructorProfile
- Serializer InstructorProfileSerializer references field 'next_tier_requirements' which does not exist in model InstructorProfile
- Serializer CourseInstructorSerializer references field 'role_display' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'instructor_name' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'instructor_email' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'instructor_profile' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'course_title' which does not exist in model CourseInstructor
- Serializer CourseInstructorSerializer references field 'course_slug' which does not exist in model CourseInstructor
- Serializer InstructorDashboardSerializer references field 'dashboard_data' which does not exist in model InstructorDashboard
- Serializer InstructorDashboardSerializer references field 'available_widgets' which does not exist in model InstructorDashboard
- Serializer CourseCreationSessionSerializer references field 'instructor_name' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'instructor_tier' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'creation_method_display' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'status_display' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'validation_status' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'step_configuration' which does not exist in model CourseCreationSession
- Serializer CourseCreationSessionSerializer references field 'resume_data' which does not exist in model CourseCreationSession
- Serializer CourseTemplateSerializer references field 'template_type_display' which does not exist in model CourseTemplate
- Serializer CourseTemplateSerializer references field 'category_name' which does not exist in model CourseTemplate
- Serializer CourseTemplateSerializer references field 'created_by_name' which does not exist in model CourseTemplate
- Serializer CourseTemplateSerializer references field 'usage_analytics' which does not exist in model CourseTemplate
- Serializer CourseTemplateSerializer references field 'preview_data' which does not exist in model CourseTemplate
- Serializer DraftCourseContentSerializer references field 'session_info' which does not exist in model DraftCourseContent
- Serializer DraftCourseContentSerializer references field 'content_type_display' which does not exist in model DraftCourseContent
- Serializer DraftCourseContentSerializer references field 'content_hash' which does not exist in model DraftCourseContent
- Serializer DraftCourseContentSerializer references field 'version_history' which does not exist in model DraftCourseContent
- Serializer CourseContentDraftSerializer references field 'session_info' which does not exist in model CourseContentDraft
- Serializer CourseContentDraftSerializer references field 'content_type_display' which does not exist in model CourseContentDraft
- Serializer CourseContentDraftSerializer references field 'processing_status_display' which does not exist in model CourseContentDraft
- Serializer CourseContentDraftSerializer references field 'file_info' which does not exist in model CourseContentDraft
- Serializer SubscriptionSerializer references field 'is_active' which does not exist in model Subscription
- Serializer SubscriptionSerializer references field 'days_remaining' which does not exist in model Subscription

**Suggestions:**
- Update the serializer to only include fields that exist in the model
- Add missing fields to the model if they're needed
- Check for typos in field names


<a id='component-mappings'></a>
## Component Mappings

### Model to Serializers

- **Category** → courses.CategorySerializer
- **Resource** → courses.ResourceSerializer, instructor_portal.InstructorResourceSerializer
- **Answer** → courses.AnswerSerializer
- **Question** → courses.QuestionSerializer
- **Assessment** → courses.AssessmentSerializer
- **Lesson** → courses.LessonSerializer, instructor_portal.InstructorLessonSerializer
- **Module** → courses.ModuleSerializer, instructor_portal.InstructorModuleSerializer
- **CourseInstructor** → courses.CourseInstructorSerializer, instructor_portal.CourseInstructorSerializer
- **Course** → courses.CourseVersionSerializer, courses.CourseSerializer, instructor_portal.InstructorCourseSerializer
- **Enrollment** → courses.EnrollmentSerializer
- **Progress** → courses.ProgressSerializer
- **AssessmentAttempt** → courses.AssessmentAttemptSerializer
- **AttemptAnswer** → courses.AttemptAnswerSerializer
- **Review** → courses.ReviewSerializer
- **Note** → courses.NoteSerializer
- **Certificate** → courses.CertificateSerializer
- **InstructorProfile** → instructor_portal.InstructorProfileSerializer
- **InstructorDashboard** → instructor_portal.InstructorDashboardSerializer
- **CourseCreationSession** → instructor_portal.CourseCreationSessionSerializer
- **CourseTemplate** → instructor_portal.CourseTemplateSerializer
- **DraftCourseContent** → instructor_portal.DraftCourseContentSerializer
- **CourseContentDraft** → instructor_portal.CourseContentDraftSerializer
- **AICourseBuilderDraft** → ai_course_builder.AICourseBuilderDraftSerializer
- **Profile** → users.ProfileSerializer
- **Subscription** → users.SubscriptionSerializer
- **User** → users.UserSerializer, users.UserCreateSerializer, users.UpdateProfileSerializer
- **UserSession** → users.UserSessionSerializer
- **Testimonial** → content.TestimonialSerializer
- **PlatformStatistics** → content.PlatformStatisticsSerializer
- **UserLearningStatistics** → content.UserLearningStatisticsSerializer
- **InstructorStatistics** → content.InstructorStatisticsSerializer

### Serializer to Views

- **CategorySerializer** → courses.CategoryViewSet
- **CourseSerializer** → courses.CourseViewSet
- **ModuleSerializer** → courses.ModuleViewSet
- **LessonSerializer** → courses.LessonViewSet
- **EnrollmentSerializer** → courses.EnrollmentViewSet
- **CertificateSerializer** → courses.CertificateViewSet
- **ProgressSerializer** → courses.ProgressViewSet
- **ReviewSerializer** → courses.ReviewViewSet
- **NoteSerializer** → courses.NoteViewSet
- **InstructorCourseSerializer** → instructor_portal.InstructorCourseViewSet
- **InstructorProfileSerializer** → instructor_portal.InstructorProfileViewSet
- **CourseInstructorSerializer** → instructor_portal.CourseInstructorViewSet
- **CourseCreationSessionSerializer** → instructor_portal.CourseCreationSessionViewSet
- **CourseTemplateSerializer** → instructor_portal.CourseTemplateViewSet
- **InstructorModuleSerializer** → instructor_portal.InstructorModuleViewSet
- **InstructorLessonSerializer** → instructor_portal.InstructorLessonViewSet
- **InstructorResourceSerializer** → instructor_portal.InstructorResourceViewSet
- **AICourseBuilderDraftSerializer** → ai_course_builder.AICourseBuilderDraftViewSet
- **UserCreateSerializer** → users.RegisterView
- **LoginSerializer** → users.LoginView
- **UserDetailSerializer** → users.UserView, users.UserSessionViewSet
- **ProfileSerializer** → users.ProfileView
- **UpdateProfileSerializer** → users.UpdateProfileView
- **PasswordChangeSerializer** → users.PasswordChangeView
- **PasswordResetRequestSerializer** → users.PasswordResetRequestView
- **PasswordResetConfirmSerializer** → users.PasswordResetConfirmView
- **EmailVerificationSerializer** → users.EmailVerificationView
- **SubscriptionSerializer** → users.SubscriptionViewSet
- **TestimonialSerializer** → content.TestimonialViewSet, content.FeaturedTestimonialsView

### View to URLs

- **urls** → admin/ → admin.site.urls
- **test_static** → test-static/ → test_static (test-static)
- **test_admin_static** → test-admin-static/ → test_admin_static (test-admin-static)
- **debug_courses** → instructor/debug/courses/ → debug_courses (debug-courses-direct), instructor/debug/courses/simple/ → debug_courses (debug-courses-simple), api/debug/courses/ → debug_courses (api-debug-courses)
- **include** → api/ → include, api/user/ → include, api/instructor/ → include, api/ → include, api-auth/ → include, JoinedStr → include, create/wizard/ → include, create/ai/ → include, create/dnd/ → include, create/template/ → include, create/import/ → include, courses/ → include, drafts/ → include, uploads/ → include, profile/ → include, settings/ → include, templates/ → include, bulk/ → include, utils/ → include, ai/ → include, reports/ → include, integrations/ → include, debug/ → include, health/ → include, api/ → include
- **TokenObtainPairView** → api/token/ → TokenObtainPairView (token_obtain_pair), token/ → TokenObtainPairView (token_obtain_pair)
- **TokenRefreshView** → api/token/refresh/ → TokenRefreshView (token_refresh), token/refresh/ → TokenRefreshView (token_refresh)
- **db_status** → api/system/db-status/ → db_status (db-status)
- **db_stats** → api/system/db-stats/ → db_stats (db-stats)
- **InstructorRegistrationView** → auth/register/ → InstructorRegistrationView (instructor-register)
- **InstructorVerificationView** → auth/verify/<uuid:verification_token>/ → InstructorVerificationView (instructor-verify)
- **InstructorStatusView** → auth/status/ → InstructorStatusView (instructor-status)
- **InstructorApprovalView** → auth/approval/ → InstructorApprovalView (instructor-approval)
- **InstructorReportsView** → analytics/reports/ → InstructorReportsView (instructor-reports)
- **RevenueAnalyticsView** → analytics/revenue/ → RevenueAnalyticsView (revenue-analytics)
- **StudentManagementView** → students/ → StudentManagementView (student-management)
- **AICourseBuilderHealthView** → api/instructor/ai-course-builder/health/ → AICourseBuilderHealthView (ai-course-builder-health)
- **RegisterView** → register/ → RegisterView (register)
- **LoginView** → login/ → LoginView (login)
- **LogoutView** → logout/ → LogoutView (logout)
- **UserView** → me/ → UserView (user-detail)
- **ProfileView** → profile/ → ProfileView (user-profile)
- **PasswordChangeView** → password/change/ → PasswordChangeView (password-change)
- **PasswordResetRequestView** → password/reset/ → PasswordResetRequestView (password-reset-request)
- **PasswordResetConfirmView** → password/reset/confirm/ → PasswordResetConfirmView (password-reset-confirm)
- **EmailVerificationView** → email/verify/ → EmailVerificationView (email-verify)
- **ResendVerificationView** → email/verify/resend/ → ResendVerificationView (email-verify-resend)
- **FeaturedTestimonialsView** → testimonials/featured/ → views.FeaturedTestimonialsView (featured-testimonials)
- **platform_statistics** → statistics/platform/ → views.platform_statistics (platform-statistics)
- **user_learning_statistics** → statistics/user/learning/ → views.user_learning_statistics (user-learning-statistics)
- **instructor_statistics** → statistics/instructor/ → views.instructor_statistics (instructor-statistics)


---

## Metadata

- **Script Version**: 2.0
- **Analyzer Run Time**: 2025-06-20 19:53:49
- **Used Django Reflection**: False
- **Excluded Apps**: None