# Database Check Report

**Generated:** 2025-07-11 21:24:37
**Database:** postgresql

---

=== GENERIC DATABASE CHECKER ===

## All Apps Check


==================================================

## App: admin

Checking tables for app: admin

### Model: LogEntry


Checking model: LogEntry (table: django_admin_log)
✅ Table django_admin_log exists
  ✅ id
  ✅ action_time
  ✅ user_id
  ✅ content_type_id
  ✅ object_id
  ✅ object_repr
  ✅ action_flag
  ✅ change_message

==================================================

## App: auth

Checking tables for app: auth

### Model: Permission


Checking model: Permission (table: auth_permission)
✅ Table auth_permission exists
  ✅ id
  ✅ name
  ✅ content_type_id
  ✅ codename

### Model: Group


Checking model: Group (table: auth_group)
✅ Table auth_group exists
  ✅ id
  ✅ name

==================================================

## App: contenttypes

Checking tables for app: contenttypes

### Model: ContentType


Checking model: ContentType (table: django_content_type)
✅ Table django_content_type exists
  ✅ id
  ✅ app_label
  ✅ model

==================================================

## App: sessions

Checking tables for app: sessions

### Model: Session


Checking model: Session (table: django_session)
✅ Table django_session exists
  ✅ session_key
  ✅ session_data
  ✅ expire_date

==================================================

## App: sites

Checking tables for app: sites

### Model: Site


Checking model: Site (table: django_site)
✅ Table django_site exists
  ✅ id
  ✅ domain
  ✅ name

==================================================

## App: token_blacklist

Checking tables for app: token_blacklist

### Model: OutstandingToken


Checking model: OutstandingToken (table: token_blacklist_outstandingtoken)
✅ Table token_blacklist_outstandingtoken exists
  ✅ id
  ✅ user_id
  ✅ jti
  ✅ token
  ✅ created_at
  ✅ expires_at

### Model: BlacklistedToken


Checking model: BlacklistedToken (table: token_blacklist_blacklistedtoken)
✅ Table token_blacklist_blacklistedtoken exists
  ✅ id
  ✅ token_id
  ✅ blacklisted_at

==================================================

## App: django_celery_beat

Checking tables for app: django_celery_beat

### Model: SolarSchedule


Checking model: SolarSchedule (table: django_celery_beat_solarschedule)
✅ Table django_celery_beat_solarschedule exists
  ✅ id
  ✅ event
  ✅ latitude
  ✅ longitude

### Model: IntervalSchedule


Checking model: IntervalSchedule (table: django_celery_beat_intervalschedule)
✅ Table django_celery_beat_intervalschedule exists
  ✅ id
  ✅ every
  ✅ period

### Model: ClockedSchedule


Checking model: ClockedSchedule (table: django_celery_beat_clockedschedule)
✅ Table django_celery_beat_clockedschedule exists
  ✅ id
  ✅ clocked_time

### Model: CrontabSchedule


Checking model: CrontabSchedule (table: django_celery_beat_crontabschedule)
✅ Table django_celery_beat_crontabschedule exists
  ✅ id
  ✅ minute
  ✅ hour
  ✅ day_of_month
  ✅ month_of_year
  ✅ day_of_week
  ✅ timezone

### Model: PeriodicTasks


Checking model: PeriodicTasks (table: django_celery_beat_periodictasks)
✅ Table django_celery_beat_periodictasks exists
  ✅ ident
  ✅ last_update

### Model: PeriodicTask


Checking model: PeriodicTask (table: django_celery_beat_periodictask)
✅ Table django_celery_beat_periodictask exists
  ✅ id
  ✅ name
  ✅ task
  ✅ interval_id
  ✅ crontab_id
  ✅ solar_id
  ✅ clocked_id
  ✅ args
  ✅ kwargs
  ✅ queue
  ✅ exchange
  ✅ routing_key
  ✅ headers
  ✅ priority
  ✅ expires
  ✅ expire_seconds
  ✅ one_off
  ✅ start_time
  ✅ enabled
  ✅ last_run_at
  ✅ total_run_count
  ✅ date_changed
  ✅ description

==================================================

## App: social_django

Checking tables for app: social_django

### Model: UserSocialAuth


Checking model: UserSocialAuth (table: social_auth_usersocialauth)
✅ Table social_auth_usersocialauth exists
  ✅ id
  ✅ user_id
  ✅ provider
  ✅ uid
  ✅ extra_data
  ✅ created
  ✅ modified

### Model: Nonce


Checking model: Nonce (table: social_auth_nonce)
✅ Table social_auth_nonce exists
  ✅ id
  ✅ server_url
  ✅ timestamp
  ✅ salt

### Model: Association


Checking model: Association (table: social_auth_association)
✅ Table social_auth_association exists
  ✅ id
  ✅ server_url
  ✅ handle
  ✅ secret
  ✅ issued
  ✅ lifetime
  ✅ assoc_type

### Model: Code


Checking model: Code (table: social_auth_code)
✅ Table social_auth_code exists
  ✅ id
  ✅ email
  ✅ code
  ✅ verified
  ✅ timestamp

### Model: Partial


Checking model: Partial (table: social_auth_partial)
✅ Table social_auth_partial exists
  ✅ id
  ✅ token
  ✅ next_step
  ✅ backend
  ✅ data
  ✅ timestamp

==================================================

## App: account

Checking tables for app: account

### Model: EmailAddress


Checking model: EmailAddress (table: account_emailaddress)
✅ Table account_emailaddress exists
  ✅ id
  ✅ user_id
  ✅ email
  ✅ verified
  ✅ primary

### Model: EmailConfirmation


Checking model: EmailConfirmation (table: account_emailconfirmation)
✅ Table account_emailconfirmation exists
  ✅ id
  ✅ email_address_id
  ✅ created
  ✅ sent
  ✅ key

==================================================

## App: socialaccount

Checking tables for app: socialaccount

### Model: SocialApp


Checking model: SocialApp (table: socialaccount_socialapp)
✅ Table socialaccount_socialapp exists
  ✅ id
  ✅ provider
  ✅ provider_id
  ✅ name
  ✅ client_id
  ✅ secret
  ✅ key
  ✅ settings

### Model: SocialAccount


Checking model: SocialAccount (table: socialaccount_socialaccount)
✅ Table socialaccount_socialaccount exists
  ✅ id
  ✅ user_id
  ✅ provider
  ✅ uid
  ✅ last_login
  ✅ date_joined
  ✅ extra_data

### Model: SocialToken


Checking model: SocialToken (table: socialaccount_socialtoken)
✅ Table socialaccount_socialtoken exists
  ✅ id
  ✅ app_id
  ✅ account_id
  ✅ token
  ✅ token_secret
  ✅ expires_at

==================================================

## App: users

Checking tables for app: users

### Model: CustomUser


Checking model: CustomUser (table: users_customuser)
✅ Table users_customuser exists
  ✅ id
  ✅ password
  ✅ is_superuser
  ✅ first_name
  ✅ last_name
  ✅ is_staff
  ✅ email
  ✅ username
  ✅ role
  ✅ is_email_verified
  ✅ date_joined
  ✅ last_login
  ✅ failed_login_attempts
  ✅ temporary_ban_until
  ✅ is_active

### Model: Profile


Checking model: Profile (table: users_profile)
✅ Table users_profile exists
  ✅ id
  ✅ user_id
  ✅ profile_picture
  ✅ bio
  ✅ date_of_birth
  ✅ phone_number
  ✅ address
  ✅ city
  ✅ state
  ✅ country
  ✅ postal_code
  ✅ website
  ✅ linkedin
  ✅ twitter
  ✅ github
  ✅ expertise
  ✅ teaching_experience
  ✅ educational_background
  ✅ interests
  ✅ receive_email_notifications
  ✅ receive_marketing_emails
  ✅ created_at
  ✅ updated_at

### Model: EmailVerification


Checking model: EmailVerification (table: users_emailverification)
✅ Table users_emailverification exists
  ✅ id
  ✅ user_id
  ✅ token
  ✅ created_at
  ✅ expires_at
  ✅ verified_at
  ✅ is_used

### Model: PasswordReset


Checking model: PasswordReset (table: users_passwordreset)
✅ Table users_passwordreset exists
  ✅ id
  ✅ user_id
  ✅ token
  ✅ created_at
  ✅ expires_at
  ✅ used_at
  ✅ is_used
  ✅ ip_address

### Model: LoginLog


Checking model: LoginLog (table: users_loginlog)
✅ Table users_loginlog exists
  ✅ id
  ✅ user_id
  ✅ timestamp
  ✅ ip_address
  ✅ user_agent
  ✅ successful

### Model: UserSession


Checking model: UserSession (table: users_usersession)
✅ Table users_usersession exists
  ✅ id
  ✅ user_id
  ✅ session_key
  ✅ ip_address
  ✅ user_agent
  ✅ created_at
  ✅ expires_at
  ✅ last_activity
  ✅ is_active
  ✅ device_type
  ✅ location
  ✅ login_method

### Model: Subscription


Checking model: Subscription (table: users_subscription)
✅ Table users_subscription exists
  ✅ id
  ✅ user_id
  ✅ tier
  ✅ status
  ✅ start_date
  ✅ end_date
  ✅ is_auto_renew
  ✅ last_payment_date
  ✅ payment_method
  ✅ payment_id

==================================================

## App: courses

Checking tables for app: courses

### Model: Category


Checking model: Category (table: courses_category)
✅ Table courses_category exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ slug
  ✅ is_active
  ✅ name
  ✅ description
  ✅ icon
  ✅ sort_order
  ✅ parent_id
  ✅ featured

### Model: Course


Checking model: Course (table: courses_course)
✅ Table courses_course exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ slug
  ✅ duration_minutes
  ✅ is_published
  ✅ published_date
  ✅ view_count
  ✅ last_accessed
  ✅ title
  ✅ subtitle
  ✅ description
  ✅ category_id
  ✅ thumbnail
  ✅ price
  ✅ discount_price
  ✅ discount_ends
  ✅ level
  ✅ has_certificate
  ✅ is_featured
  ✅ requirements
  ✅ skills
  ✅ learning_objectives
  ✅ target_audience
  ✅ creation_method
  ✅ completion_status
  ✅ completion_percentage
  ✅ version
  ✅ is_draft
  ✅ parent_version_id
  ✅ meta_keywords
  ✅ meta_description
  ✅ sort_order
  ✅ enrolled_students_count
  ✅ avg_rating
  ✅ total_reviews
  ✅ last_enrollment_date

### Model: Module


Checking model: Module (table: courses_module)
✅ Table courses_module exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ order
  ✅ duration_minutes
  ✅ is_published
  ✅ published_date
  ✅ course_id
  ✅ title
  ✅ description

### Model: Lesson


Checking model: Lesson (table: courses_lesson)
✅ Table courses_lesson exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ order
  ✅ duration_minutes
  ✅ module_id
  ✅ title
  ✅ content
  ✅ guest_content
  ✅ registered_content
  ✅ access_level
  ✅ type
  ✅ activity_type
  ✅ has_assessment
  ✅ has_lab
  ✅ is_free_preview
  ✅ video_url
  ✅ transcript

### Model: Resource


Checking model: Resource (table: courses_resource)
✅ Table courses_resource exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ order
  ✅ duration_minutes
  ✅ storage_key
  ✅ uploaded
  ✅ file_size
  ✅ mime_type
  ✅ lesson_id
  ✅ title
  ✅ type
  ✅ description
  ✅ file
  ✅ url
  ✅ premium
  ✅ download_count

### Model: Enrollment


Checking model: Enrollment (table: courses_enrollment)
✅ Table courses_enrollment exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ course_id
  ✅ status
  ✅ completion_date
  ✅ last_accessed
  ✅ enrolled_date
  ✅ total_time_spent
  ✅ progress_percentage
  ✅ last_lesson_accessed_id

### Model: Progress


Checking model: Progress (table: courses_progress)
✅ Table courses_progress exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ enrollment_id
  ✅ lesson_id
  ✅ is_completed
  ✅ completed_date
  ✅ time_spent
  ✅ progress_percentage
  ✅ notes
  ✅ last_accessed

### Model: Certificate


Checking model: Certificate (table: courses_certificate)
✅ Table courses_certificate exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ enrollment_id
  ✅ certificate_number
  ✅ is_valid
  ✅ revocation_date
  ✅ revocation_reason
  ✅ verification_hash
  ✅ template_version

### Model: CourseProgress


Checking model: CourseProgress (table: courses_courseprogress)
✅ Table courses_courseprogress exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ course_id
  ✅ completion_percentage
  ✅ last_accessed
  ✅ started_at
  ✅ completed_at
  ✅ current_lesson_id
  ✅ total_time_spent
  ✅ lessons_completed
  ✅ assessments_passed
  ✅ study_streak_days
  ✅ last_study_date

### Model: Assessment


Checking model: Assessment (table: courses_assessment)
✅ Table courses_assessment exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ lesson_id
  ✅ title
  ✅ description
  ✅ passing_score
  ✅ max_attempts
  ✅ time_limit
  ✅ time_limit_minutes
  ✅ randomize_questions
  ✅ show_correct_answers
  ✅ show_results

### Model: Question


Checking model: Question (table: courses_question)
✅ Table courses_question exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ assessment_id
  ✅ question_text
  ✅ text
  ✅ question_type
  ✅ points
  ✅ order
  ✅ explanation
  ✅ feedback

### Model: Answer


Checking model: Answer (table: courses_answer)
✅ Table courses_answer exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ question_id
  ✅ answer_text
  ✅ text
  ✅ is_correct
  ✅ explanation
  ✅ order

### Model: AssessmentAttempt


Checking model: AssessmentAttempt (table: courses_assessmentattempt)
✅ Table courses_assessmentattempt exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ assessment_id
  ✅ start_time
  ✅ end_time
  ✅ time_taken_seconds
  ✅ score
  ✅ max_score
  ✅ is_completed
  ✅ is_passed
  ✅ passed
  ✅ attempt_number
  ✅ ip_address
  ✅ user_agent

### Model: AttemptAnswer


Checking model: AttemptAnswer (table: courses_attemptanswer)
✅ Table courses_attemptanswer exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ attempt_id
  ✅ question_id
  ✅ selected_answer_id
  ✅ text_answer
  ✅ is_correct
  ✅ points_earned
  ✅ feedback
  ✅ answered_at

### Model: Review


Checking model: Review (table: courses_review)
✅ Table courses_review exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ course_id
  ✅ rating
  ✅ title
  ✅ content
  ✅ helpful_count
  ✅ is_verified_purchase
  ✅ is_approved
  ✅ is_featured
  ✅ moderation_notes

### Model: Note


Checking model: Note (table: courses_note)
✅ Table courses_note exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ lesson_id
  ✅ content
  ✅ timestamp_seconds
  ✅ is_private
  ✅ tags

### Model: UserActivity


Checking model: UserActivity (table: courses_useractivity)
✅ Table courses_useractivity exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ activity_type
  ✅ course_id
  ✅ lesson_id
  ✅ resource_id
  ✅ assessment_id
  ✅ data

### Model: CourseStats


Checking model: CourseStats (table: courses_coursestats)
✅ Table courses_coursestats exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ course_id
  ✅ total_students
  ✅ active_students
  ✅ completion_count
  ✅ average_completion_days
  ✅ engagement_score
  ✅ assessment_stats
  ✅ revenue_data

### Model: UserStats


Checking model: UserStats (table: courses_userstats)
✅ Table courses_userstats exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ courses_enrolled
  ✅ courses_completed
  ✅ total_time_spent_seconds
  ✅ assessment_avg_score
  ✅ last_activity
  ✅ activity_streak
  ✅ learning_habits

### Model: Notification


Checking model: Notification (table: courses_notification)
✅ Table courses_notification exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ title
  ✅ message
  ✅ notification_type
  ✅ course_id
  ✅ is_read
  ✅ read_date
  ✅ action_url

### Model: Bookmark


Checking model: Bookmark (table: courses_bookmark)
✅ Table courses_bookmark exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ content_type_id
  ✅ object_id
  ✅ title
  ✅ notes
  ✅ position
  ✅ is_favorite
  ✅ tags

### Model: UserPreference


Checking model: UserPreference (table: courses_userpreference)
✅ Table courses_userpreference exists
  ✅ id
  ✅ created_date
  ✅ updated_date
  ✅ user_id
  ✅ email_notifications
  ✅ push_notifications
  ✅ reminder_frequency
  ✅ theme
  ✅ language
  ✅ timezone
  ✅ autoplay_videos
  ✅ video_playback_speed
  ✅ auto_advance_lessons
  ✅ content_filters
  ✅ accessibility
  ✅ profile_visibility
  ✅ show_progress_to_instructors

==================================================

## App: instructor_portal

Checking tables for app: instructor_portal

### Model: InstructorProfile


Checking model: InstructorProfile (table: instructor_portal_instructorprofile)
✅ Table instructor_portal_instructorprofile exists
  ✅ id
  ✅ user_id
  ✅ display_name
  ✅ bio
  ✅ title
  ✅ organization
  ✅ years_experience
  ✅ website
  ✅ linkedin_profile
  ✅ twitter_handle
  ✅ profile_image
  ✅ cover_image
  ✅ status
  ✅ is_verified
  ✅ tier
  ✅ email_notifications
  ✅ marketing_emails
  ✅ public_profile
  ✅ approved_by_id
  ✅ approval_date
  ✅ suspension_reason
  ✅ created_date
  ✅ updated_date
  ✅ last_login

### Model: InstructorAnalytics


Checking model: InstructorAnalytics (table: instructor_portal_instructoranalytics)
✅ Table instructor_portal_instructoranalytics exists
  ✅ id
  ✅ instructor_id
  ✅ total_students
  ✅ total_courses
  ✅ average_rating
  ✅ total_reviews
  ✅ total_revenue
  ✅ completion_rate
  ✅ student_satisfaction_rate
  ✅ monthly_revenue
  ✅ last_updated
  ✅ last_calculated

### Model: InstructorAnalyticsHistory


Checking model: InstructorAnalyticsHistory (table: instructor_portal_instructoranalyticshistory)
✅ Table instructor_portal_instructoranalyticshistory exists
  ✅ id
  ✅ instructor_id
  ✅ date
  ✅ total_students
  ✅ total_courses
  ✅ average_rating
  ✅ total_revenue
  ✅ completion_rate
  ✅ data_type
  ✅ additional_data

### Model: CourseInstructor


Checking model: CourseInstructor (table: instructor_portal_courseinstructor)
✅ Table instructor_portal_courseinstructor exists
  ✅ id
  ✅ course_id
  ✅ instructor_id
  ✅ role
  ✅ is_active
  ✅ is_lead
  ✅ can_edit_content
  ✅ can_manage_students
  ✅ can_view_analytics
  ✅ revenue_share_percentage
  ✅ joined_date
  ✅ updated_date

### Model: InstructorDashboard


Checking model: InstructorDashboard (table: instructor_portal_instructordashboard)
✅ Table instructor_portal_instructordashboard exists
  ✅ id
  ✅ instructor_id
  ✅ show_analytics
  ✅ show_recent_students
  ✅ show_performance_metrics
  ✅ show_revenue_charts
  ✅ show_course_progress
  ✅ notify_new_enrollments
  ✅ notify_new_reviews
  ✅ notify_course_completions
  ✅ widget_order
  ✅ custom_colors
  ✅ created_date
  ✅ updated_date

### Model: CourseCreationSession


Checking model: CourseCreationSession (table: instructor_portal_coursecreationsession)
✅ Table instructor_portal_coursecreationsession exists
  ✅ id
  ✅ session_id
  ✅ instructor_id
  ✅ creation_method
  ✅ template_id
  ✅ status
  ✅ current_step
  ✅ total_steps
  ✅ completion_percentage
  ✅ course_data
  ✅ metadata
  ✅ steps_completed
  ✅ validation_errors
  ✅ template_used
  ✅ ai_prompts_used
  ✅ expires_at
  ✅ last_activity
  ✅ published_course_id
  ✅ created_date
  ✅ updated_date

### Model: CourseTemplate


Checking model: CourseTemplate (table: instructor_portal_coursetemplate)
✅ Table instructor_portal_coursetemplate exists
  ✅ id
  ✅ name
  ✅ description
  ✅ template_type
  ✅ template_data
  ✅ is_active
  ✅ is_premium
  ✅ required_tier
  ✅ usage_count
  ✅ success_rate
  ✅ created_by_id
  ✅ tags
  ✅ created_date
  ✅ updated_date

### Model: DraftCourseContent


Checking model: DraftCourseContent (table: instructor_portal_draftcoursecontent)
✅ Table instructor_portal_draftcoursecontent exists
  ✅ id
  ✅ session_id
  ✅ content_type
  ✅ content_id
  ✅ version
  ✅ content_data
  ✅ title
  ✅ order
  ✅ is_complete
  ✅ validation_errors
  ✅ auto_save_version
  ✅ last_saved
  ✅ ai_generated
  ✅ ai_prompt

### Model: CourseContentDraft


Checking model: CourseContentDraft (table: instructor_portal_coursecontentdraft)
✅ Table instructor_portal_coursecontentdraft exists
  ✅ id
  ✅ session_id
  ✅ content_type
  ✅ file_path
  ✅ content_hash
  ✅ version
  ✅ is_processed
  ✅ processing_status
  ✅ processing_error
  ✅ file_size
  ✅ mime_type
  ✅ original_filename
  ✅ processing_metadata
  ✅ created_date
  ✅ processed_date

### Model: InstructorNotification


Checking model: InstructorNotification (table: instructor_portal_instructornotification)
✅ Table instructor_portal_instructornotification exists
  ✅ id
  ✅ instructor_id
  ✅ notification_type
  ✅ priority
  ✅ title
  ✅ message
  ✅ action_url
  ✅ action_text
  ✅ metadata
  ✅ is_read
  ✅ read_at
  ✅ is_dismissed
  ✅ dismissed_at
  ✅ email_sent
  ✅ email_sent_at
  ✅ created_date
  ✅ expires_at

### Model: InstructorSession


Checking model: InstructorSession (table: instructor_portal_instructorsession)
✅ Table instructor_portal_instructorsession exists
  ✅ id
  ✅ instructor_id
  ✅ session_key
  ✅ ip_address
  ✅ user_agent
  ✅ device_type
  ✅ location
  ✅ login_time
  ✅ last_activity
  ✅ logout_time
  ✅ is_active
  ✅ is_suspicious
  ✅ security_notes

==================================================

## App: content

Checking tables for app: content

### Model: Testimonial


Checking model: Testimonial (table: content_testimonial)
✅ Table content_testimonial exists
  ✅ id
  ✅ name
  ✅ role
  ✅ content
  ✅ rating
  ✅ avatar
  ✅ featured
  ✅ created_at
  ✅ updated_at

### Model: PlatformStatistics


Checking model: PlatformStatistics (table: content_platformstatistics)
✅ Table content_platformstatistics exists
  ✅ id
  ✅ total_courses
  ✅ total_students
  ✅ total_instructors
  ✅ total_lessons_completed
  ✅ total_certificates_issued
  ✅ last_updated

### Model: UserLearningStatistics


Checking model: UserLearningStatistics (table: content_userlearningstatistics)
✅ Table content_userlearningstatistics exists
  ✅ id
  ✅ user_id
  ✅ courses_completed
  ✅ hours_spent
  ✅ average_score
  ✅ last_updated

### Model: InstructorStatistics


Checking model: InstructorStatistics (table: content_instructorstatistics)
✅ Table content_instructorstatistics exists
  ✅ id
  ✅ user_id
  ✅ courses_created
  ✅ total_students
  ✅ average_rating
  ✅ last_updated

==================================================

## App: ai_course_builder

Checking tables for app: ai_course_builder

### Model: AICourseBuilderDraft


Checking model: AICourseBuilderDraft (table: ai_course_builder_aicoursebuilderdraft)
✅ Table ai_course_builder_aicoursebuilderdraft exists
  ✅ id
  ✅ instructor_id
  ✅ created_at
  ✅ updated_at
  ✅ status
  ✅ title
  ✅ description
  ✅ course_objectives
  ✅ target_audience
  ✅ difficulty_level
  ✅ duration_minutes
  ✅ price
  ✅ outline
  ✅ content
  ✅ assessments
  ✅ has_outline
  ✅ has_modules
  ✅ has_lessons
  ✅ has_assessments
  ✅ generation_metadata

=== CHECK COMPLETE ===