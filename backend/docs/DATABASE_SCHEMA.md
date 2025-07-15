# Database Schema Documentation

**Generated on:** 2025-07-11 20:53:50
**Django Version:** 5.2
**Total Tables:** 69
**Total Apps:** 15

## Table of Contents

- [Account App](#account-app)
  - [email address](#account-emailaddress)
  - [email confirmation](#account-emailconfirmation)
- [Admin App](#admin-app)
  - [log entry](#django-admin-log)
- [Ai_Course_Builder App](#ai-course-builder-app)
  - [AI Course Builder Draft](#ai-course-builder-aicoursebuilderdraft)
- [Auth App](#auth-app)
  - [group](#auth-group)
  - [permission](#auth-permission)
- [Content App](#content-app)
  - [Instructor Statistics](#content-instructorstatistics)
  - [Platform Statistics](#content-platformstatistics)
  - [testimonial](#content-testimonial)
  - [User Learning Statistics](#content-userlearningstatistics)
- [Contenttypes App](#contenttypes-app)
  - [content type](#django-content-type)
- [Courses App](#courses-app)
  - [Answer](#courses-answer)
  - [Assessment](#courses-assessment)
  - [Assessment Attempt](#courses-assessmentattempt)
  - [Attempt Answer](#courses-attemptanswer)
  - [Bookmark](#courses-bookmark)
  - [Category](#courses-category)
  - [Certificate](#courses-certificate)
  - [Course](#courses-course)
  - [Course Progress](#courses-courseprogress)
  - [course stats](#courses-coursestats)
  - [Enrollment](#courses-enrollment)
  - [Lesson](#courses-lesson)
  - [Module](#courses-module)
  - [Note](#courses-note)
  - [notification](#courses-notification)
  - [Progress](#courses-progress)
  - [Question](#courses-question)
  - [Resource](#courses-resource)
  - [Review](#courses-review)
  - [user activity](#courses-useractivity)
  - [User Preference](#courses-userpreference)
  - [user stats](#courses-userstats)
- [Django_Celery_Beat App](#django-celery-beat-app)
  - [clocked](#django-celery-beat-clockedschedule)
  - [crontab](#django-celery-beat-crontabschedule)
  - [interval](#django-celery-beat-intervalschedule)
  - [periodic task](#django-celery-beat-periodictask)
  - [periodic task track](#django-celery-beat-periodictasks)
  - [solar event](#django-celery-beat-solarschedule)
- [Instructor_Portal App](#instructor-portal-app)
  - [Course Content Draft](#instructor-portal-coursecontentdraft)
  - [Course Creation Session](#instructor-portal-coursecreationsession)
  - [Course Instructor](#instructor-portal-courseinstructor)
  - [Course Template](#instructor-portal-coursetemplate)
  - [Draft Course Content](#instructor-portal-draftcoursecontent)
  - [Instructor Analytics](#instructor-portal-instructoranalytics)
  - [Analytics History](#instructor-portal-instructoranalyticshistory)
  - [Instructor Dashboard](#instructor-portal-instructordashboard)
  - [Instructor Notification](#instructor-portal-instructornotification)
  - [Instructor Profile](#instructor-portal-instructorprofile)
  - [Instructor Session](#instructor-portal-instructorsession)
- [Sessions App](#sessions-app)
  - [session](#django-session)
- [Sites App](#sites-app)
  - [site](#django-site)
- [Social_Django App](#social-django-app)
  - [association](#social-auth-association)
  - [code](#social-auth-code)
  - [nonce](#social-auth-nonce)
  - [partial](#social-auth-partial)
  - [user social auth](#social-auth-usersocialauth)
- [Socialaccount App](#socialaccount-app)
  - [social account](#socialaccount-socialaccount)
  - [social application](#socialaccount-socialapp)
  - [social application token](#socialaccount-socialtoken)
- [Token_Blacklist App](#token-blacklist-app)
  - [blacklisted token](#token-blacklist-blacklistedtoken)
  - [outstanding token](#token-blacklist-outstandingtoken)
- [Users App](#users-app)
  - [user](#users-customuser)
  - [email verification](#users-emailverification)
  - [login log](#users-loginlog)
  - [password reset](#users-passwordreset)
  - [profile](#users-profile)
  - [Subscription](#users-subscription)
  - [user session](#users-usersession)

---

## Account App

### email address (`account_emailaddress`)

**Model:** `emailaddress`  
**App:** `account`  
**Verbose Name:** email address  
**Plural Name:** email addresses  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `email` | CharField | varchar(254) | ✗ | - | ✗ | ✗ | 254 | - |
| `verified` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `primary` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Constraints

- unique_primary_email
- unique_verified_email

#### Unique Together

- user, email
- user, primary
- email

---

### email confirmation (`account_emailconfirmation`)

**Model:** `emailconfirmation`  
**App:** `account`  
**Verbose Name:** email confirmation  
**Plural Name:** email confirmations  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `email_address_id` | ForeignKey | integer | ✗ | - | ✗ | ✗ | - | - |
| `created` | DateTimeField | timestamp with time zone | ✗ | 2025-07-11 15:23:50.845375+00:00 | ✗ | ✗ | - | - |
| `sent` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `key` | CharField | varchar(64) | ✗ | - | ✗ | ✓ | 64 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `email_address_id` | ForeignKey | `account_emailaddress` |

---

## Admin App

### log entry (`django_admin_log`)

**Model:** `logentry`  
**App:** `admin`  
**Verbose Name:** log entry  
**Plural Name:** log entries  
**Default Ordering:** -, a, c, t, i, o, n, _, t, i, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `action_time` | DateTimeField | timestamp with time zone | ✗ | 2025-07-11 15:23:50.842912+00:00 | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `content_type_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | - |
| `object_id` | TextField | text | ✓ | - | ✗ | ✗ | - | - |
| `object_repr` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `action_flag` | PositiveSmallIntegerField | smallint | ✗ | - | ✗ | ✗ | - | - |
| `change_message` | TextField | text | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `content_type_id` | ForeignKey | `django_content_type` |

---

## Ai_Course_Builder App

### AI Course Builder Draft (`ai_course_builder_aicoursebuilderdraft`)

**Model:** `aicoursebuilderdraft`  
**App:** `ai_course_builder`  
**Verbose Name:** AI Course Builder Draft  
**Plural Name:** AI Course Builder Drafts  
**Default Ordering:** -, u, p, d, a, t, e, d, _, a, t  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `status` | CharField | varchar(20) | ✗ | DRAFT | ✗ | ✗ | 20 | - |
| `title` | CharField | varchar(255) | ✓ | - | ✗ | ✗ | 255 | - |
| `description` | TextField | text | ✓ | - | ✗ | ✗ | - | - |
| `course_objectives` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |
| `target_audience` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |
| `difficulty_level` | CharField | varchar(20) | ✓ | all_levels | ✗ | ✗ | 20 | - |
| `duration_minutes` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | - |
| `price` | DecimalField | numeric(10, 2) | ✓ | - | ✗ | ✗ | - | - |
| `outline` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |
| `content` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |
| `assessments` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |
| `has_outline` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `has_modules` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `has_lessons` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `has_assessments` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `generation_metadata` | JSONField | jsonb | ✓ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | ForeignKey | `users_customuser` |

---

## Auth App

### group (`auth_group`)

**Model:** `group`  
**App:** `auth`  
**Verbose Name:** group  
**Plural Name:** groups  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `name` | CharField | varchar(150) | ✗ | - | ✗ | ✓ | 150 | - |

---

### permission (`auth_permission`)

**Model:** `permission`  
**App:** `auth`  
**Verbose Name:** permission  
**Plural Name:** permissions  
**Default Ordering:** c, o, n, t, e, n, t, _, t, y, p, e, _, _, a, p, p, _, l, a, b, e, l, ,,  , c, o, n, t, e, n, t, _, t, y, p, e, _, _, m, o, d, e, l, ,,  , c, o, d, e, n, a, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `name` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `content_type_id` | ForeignKey | integer | ✗ | - | ✗ | ✗ | - | - |
| `codename` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `content_type_id` | ForeignKey | `django_content_type` |

#### Unique Together

- content_type, codename

---

## Content App

### Instructor Statistics (`content_instructorstatistics`)

**Model:** `instructorstatistics`  
**App:** `content`  
**Verbose Name:** Instructor Statistics  
**Plural Name:** Instructor Statistics  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `courses_created` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `average_rating` | FloatField | double precision | ✗ | - | ✗ | ✗ | - | - |
| `last_updated` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

---

### Platform Statistics (`content_platformstatistics`)

**Model:** `platformstatistics`  
**App:** `content`  
**Verbose Name:** Platform Statistics  
**Plural Name:** Platform Statistics  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `total_courses` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_instructors` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_lessons_completed` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_certificates_issued` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `last_updated` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

---

### testimonial (`content_testimonial`)

**Model:** `testimonial`  
**App:** `content`  
**Verbose Name:** testimonial  
**Plural Name:** testimonials  
**Default Ordering:** -, f, e, a, t, u, r, e, d, ,,  , -, c, r, e, a, t, e, d, _, a, t  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `name` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `role` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `content` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `rating` | IntegerField | integer | ✗ | 5 | ✗ | ✗ | - | - |
| `avatar` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |
| `featured` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

---

### User Learning Statistics (`content_userlearningstatistics`)

**Model:** `userlearningstatistics`  
**App:** `content`  
**Verbose Name:** User Learning Statistics  
**Plural Name:** User Learning Statistics  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `courses_completed` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `hours_spent` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `average_score` | FloatField | double precision | ✗ | - | ✗ | ✗ | - | - |
| `last_updated` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

---

## Contenttypes App

### content type (`django_content_type`)

**Model:** `contenttype`  
**App:** `contenttypes`  
**Verbose Name:** content type  
**Plural Name:** content types  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `app_label` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `model` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |

#### Unique Together

- app_label, model

---

## Courses App

### Answer (`courses_answer`)

**Model:** `answer`  
**App:** `courses`  
**Verbose Name:** Answer  
**Plural Name:** Answers  
**Default Ordering:** q, u, e, s, t, i, o, n, ,,  , o, r, d, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `question_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Parent question |
| `answer_text` | CharField | varchar(500) | ✗ | - | ✗ | ✗ | 500 | Answer text (minimum 1 character) |
| `text` | TextField | text | ✗ | - | ✗ | ✗ | - | Alias for answer_text for backward compatibility |
| `is_correct` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether this is the correct answer |
| `explanation` | TextField | text | ✗ | - | ✗ | ✗ | - | Explanation for this answer choice |
| `order` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | Display order of this answer |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `question_id` | ForeignKey | `courses_question` |

#### Constraints

- unique_answer_order

#### Unique Together

- question, order

#### Indexes

- courses_ans_questio_aedf7d_idx
- courses_ans_is_corr_9dd4bc_idx

---

### Assessment (`courses_assessment`)

**Model:** `assessment`  
**App:** `courses`  
**Verbose Name:** Assessment  
**Plural Name:** Assessments  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `lesson_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | Associated lesson |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Assessment title (minimum 2 characters) |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | Assessment description or instructions |
| `passing_score` | PositiveIntegerField | integer | ✗ | 70 | ✗ | ✗ | - | Passing score percentage (0-100) |
| `max_attempts` | PositiveIntegerField | integer | ✗ | 3 | ✗ | ✗ | - | Maximum number of attempts allowed |
| `time_limit` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Time limit in minutes, 0 means no limit |
| `time_limit_minutes` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Alias for time_limit for backward compatibility |
| `randomize_questions` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Randomize question order for each attempt |
| `show_correct_answers` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Show correct answers after completion |
| `show_results` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Show results immediately after completion |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `lesson_id` | OneToOneField | `courses_lesson` |

#### Indexes

- courses_ass_passing_b8a83e_idx
- courses_ass_show_re_52db30_idx

---

### Assessment Attempt (`courses_assessmentattempt`)

**Model:** `assessmentattempt`  
**App:** `courses`  
**Verbose Name:** Assessment Attempt  
**Plural Name:** Assessment Attempts  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | User taking the assessment |
| `assessment_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Assessment being attempted |
| `start_time` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | When attempt was started |
| `end_time` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | When attempt was completed |
| `time_taken_seconds` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `score` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Raw score achieved |
| `max_score` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `is_completed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `is_passed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether attempt passed the assessment |
| `passed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Alias for is_passed for backward compatibility |
| `attempt_number` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | Attempt number for this user/assessment combination |
| `ip_address` | GenericIPAddressField | inet | ✓ | - | ✗ | ✗ | 39 | IP address of the user during attempt |
| `user_agent` | TextField | text | ✗ | - | ✗ | ✗ | - | User agent string during attempt |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `assessment_id` | ForeignKey | `courses_assessment` |

#### Indexes

- courses_ass_user_id_fedd97_idx
- courses_ass_assessm_1f3420_idx
- courses_ass_is_comp_899cc6_idx

---

### Attempt Answer (`courses_attemptanswer`)

**Model:** `attemptanswer`  
**App:** `courses`  
**Verbose Name:** Attempt Answer  
**Plural Name:** Attempt Answers  
**Default Ordering:** a, t, t, e, m, p, t, ,,  , q, u, e, s, t, i, o, n  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `attempt_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Associated assessment attempt |
| `question_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Question being answered |
| `selected_answer_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | Selected answer for multiple choice questions |
| `text_answer` | TextField | text | ✗ | - | ✗ | ✗ | - | Text answer for open-ended questions |
| `is_correct` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether the answer is correct |
| `points_earned` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Points earned for this answer |
| `feedback` | TextField | text | ✗ | - | ✗ | ✗ | - | Instructor feedback for this answer |
| `answered_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | When answer was submitted |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `attempt_id` | ForeignKey | `courses_assessmentattempt` |
| `question_id` | ForeignKey | `courses_question` |
| `selected_answer_id` | ForeignKey | `courses_answer` |

#### Constraints

- unique_attempt_answer

#### Unique Together

- attempt, question

#### Indexes

- courses_att_attempt_aab6c9_idx
- courses_att_is_corr_be0997_idx

---

### Bookmark (`courses_bookmark`)

**Model:** `bookmark`  
**App:** `courses`  
**Verbose Name:** Bookmark  
**Plural Name:** Bookmarks  
**Default Ordering:** p, o, s, i, t, i, o, n, ,,  , -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | User who created this bookmark |
| `content_type_id` | ForeignKey | integer | ✗ | - | ✗ | ✗ | - | Type of content being bookmarked |
| `object_id` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | ID of the bookmarked object (supports both integer and UUID) |
| `title` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | Custom title for the bookmark |
| `notes` | TextField | text | ✓ | - | ✗ | ✗ | - | Personal notes about the bookmarked content |
| `position` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Order position for bookmark organization |
| `is_favorite` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether this bookmark is marked as favorite |
| `tags` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Tags for organizing bookmarks |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `content_type_id` | ForeignKey | `django_content_type` |

#### Constraints

- unique_bookmark_per_user

#### Unique Together

- user, content_type, object_id

#### Indexes

- courses_boo_user_id_9a294c_idx
- courses_boo_user_id_8141b3_idx
- courses_boo_content_885b7e_idx
- courses_boo_user_id_c5e744_idx

---

### Category (`courses_category`)

**Model:** `category`  
**App:** `courses`  
**Verbose Name:** Category  
**Plural Name:** Categories  
**Default Ordering:** s, o, r, t, _, o, r, d, e, r, ,,  , n, a, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `slug` | SlugField | varchar(180) | ✗ | - | ✗ | ✓ | 180 | - |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `name` | CharField | varchar(100) | ✗ | - | ✗ | ✓ | 100 | Category name (minimum 2 characters) |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | Optional category description |
| `icon` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | CSS icon class |
| `sort_order` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Sort order for display |
| `parent_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | Parent category for hierarchy |
| `featured` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether category is featured on homepage |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `parent_id` | ForeignKey | `courses_category` |

#### Constraints

- unique_category_slug
- category_sort_order_positive

#### Unique Together

- slug

#### Indexes

- courses_cat_created_8cf2cb_idx
- courses_cat_updated_67ffb8_idx
- courses_cat_slug_33564e_idx
- courses_cat_is_acti_61a38c_idx
- courses_cat_sort_or_896e38_idx
- courses_cat_name_ab7c10_idx
- courses_cat_parent__abacdd_idx
- category_slug_idx
- courses_cat_is_acti_07f5fd_idx

---

### Certificate (`courses_certificate`)

**Model:** `certificate`  
**App:** `courses`  
**Verbose Name:** Certificate  
**Plural Name:** Certificates  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `enrollment_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | Associated enrollment |
| `certificate_number` | CharField | varchar(50) | ✗ | - | ✗ | ✓ | 50 | Unique certificate number |
| `is_valid` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Whether certificate is valid |
| `revocation_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Date when certificate was revoked |
| `revocation_reason` | TextField | text | ✗ | - | ✗ | ✗ | - | Reason for certificate revocation |
| `verification_hash` | CharField | varchar(64) | ✗ | - | ✗ | ✓ | 64 | SHA-256 hash for verification |
| `template_version` | CharField | varchar(10) | ✗ | 1.0 | ✗ | ✗ | 10 | Certificate template version |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `enrollment_id` | OneToOneField | `courses_enrollment` |

#### Constraints

- unique_certificate_number
- unique_verification_hash

#### Unique Together

- certificate_number
- verification_hash

#### Indexes

- courses_cer_created_6482f3_idx
- courses_cer_updated_e6b0b5_idx
- courses_cer_certifi_b5881b_idx
- courses_cer_verific_19df54_idx
- courses_cer_is_vali_2f2340_idx

---

### Course (`courses_course`)

**Model:** `course`  
**App:** `courses`  
**Verbose Name:** Course  
**Plural Name:** Courses  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `slug` | SlugField | varchar(180) | ✗ | - | ✗ | ✓ | 180 | - |
| `duration_minutes` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Duration in minutes |
| `is_published` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `published_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `view_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `last_accessed` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `title` | CharField | varchar(160) | ✗ | - | ✗ | ✗ | 160 | Course title (minimum 3 characters) |
| `subtitle` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Optional course subtitle |
| `description` | TextField | text | ✓ | - | ✗ | ✗ | - | Course description (minimum 50 characters) |
| `category_id` | ForeignKey | bigint | ✓ | 1 | ✗ | ✗ | - | Course category |
| `thumbnail` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | Course thumbnail |
| `price` | DecimalField | numeric(8, 2) | ✗ | 49.99 | ✗ | ✗ | - | Course price (decimal precision) |
| `discount_price` | DecimalField | numeric(8, 2) | ✓ | - | ✗ | ✗ | - | Discounted price (optional, decimal precision) |
| `discount_ends` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Discount expiration date |
| `level` | CharField | varchar(20) | ✗ | all_levels | ✗ | ✗ | 20 | Course difficulty level |
| `has_certificate` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether course offers completion certificate |
| `is_featured` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether course is featured on homepage |
| `requirements` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | List of course requirements |
| `skills` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | List of skills students will learn |
| `learning_objectives` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | List of learning objectives |
| `target_audience` | TextField | text | ✗ | - | ✗ | ✗ | - | Description of target audience |
| `creation_method` | CharField | varchar(20) | ✗ | builder | ✗ | ✗ | 20 | Method used to create course |
| `completion_status` | CharField | varchar(20) | ✗ | not_started | ✗ | ✗ | 20 | Course completion status |
| `completion_percentage` | IntegerField | integer | ✗ | - | ✗ | ✗ | - | Completion percentage (0-100) |
| `version` | DecimalField | numeric(4, 1) | ✗ | 1.0 | ✗ | ✗ | - | Course version number (decimal precision) |
| `is_draft` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Whether course is in draft state |
| `parent_version_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | Parent course version for cloned courses |
| `meta_keywords` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | SEO meta keywords |
| `meta_description` | TextField | text | ✓ | - | ✗ | ✗ | - | SEO meta description |
| `sort_order` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Sort order for catalog display |
| `enrolled_students_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Cached count of enrolled students |
| `avg_rating` | DecimalField | numeric(3, 2) | ✗ | - | ✗ | ✗ | - | Average rating from reviews (decimal precision) |
| `total_reviews` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Total number of reviews |
| `last_enrollment_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Date of last student enrollment |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `category_id` | ForeignKey | `courses_category` |
| `parent_version_id` | ForeignKey | `courses_course` |

#### Constraints

- unique_course_slug
- course_price_positive
- course_discount_price_positive
- course_version_positive
- course_discount_less_than_price

#### Unique Together

- slug

#### Indexes

- courses_cou_created_7da7d5_idx
- courses_cou_updated_517180_idx
- courses_cou_slug_2e551f_idx
- courses_cou_is_publ_4b99b9_idx
- courses_cou_publish_80f4bd_idx
- courses_cou_view_co_55d4de_idx
- courses_cou_last_ac_9655a6_idx
- courses_cou_categor_e9e0ba_idx
- courses_cou_is_feat_6821f1_idx
- courses_cou_level_a2b259_idx
- courses_cou_parent__886ac7_idx
- courses_cou_creatio_6175b0_idx
- courses_cou_complet_a28d16_idx
- courses_cou_is_draf_460a8b_idx
- courses_cou_price_1fbd18_idx
- courses_cou_avg_rat_82cd8e_idx
- course_slug_idx
- idx_course_pub_status
- idx_course_feat_sort

---

### Course Progress (`courses_courseprogress`)

**Model:** `courseprogress`  
**App:** `courses`  
**Verbose Name:** Course Progress  
**Plural Name:** Course Progress Records  
**Default Ordering:** -, l, a, s, t, _, a, c, c, e, s, s, e, d  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Student user |
| `course_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Associated course |
| `completion_percentage` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | Course completion percentage (0.00 to 100.00) |
| `last_accessed` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Last time the user accessed this course |
| `started_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | When the user first started this course |
| `completed_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | When the user completed this course |
| `current_lesson_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | The lesson the user is currently on |
| `total_time_spent` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Total time spent on this course in seconds |
| `lessons_completed` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Number of lessons completed |
| `assessments_passed` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Number of assessments passed |
| `study_streak_days` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Consecutive days of course activity |
| `last_study_date` | DateField | date | ✓ | - | ✗ | ✗ | - | Last date the user studied this course |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `course_id` | ForeignKey | `courses_course` |
| `current_lesson_id` | ForeignKey | `courses_lesson` |

#### Constraints

- unique_course_progress
- course_progress_percentage_range
- course_progress_lessons_completed_positive
- course_progress_assessments_passed_positive
- course_progress_study_streak_positive

#### Unique Together

- user, course

#### Indexes

- courses_cou_created_6c9322_idx
- courses_cou_updated_2dc6a5_idx
- courses_cou_user_id_06f975_idx
- courses_cou_course__4ab7f3_idx
- courses_cou_user_id_d1c82f_idx

---

### course stats (`courses_coursestats`)

**Model:** `coursestats`  
**App:** `courses`  
**Verbose Name:** course stats  
**Plural Name:** Course stats  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `course_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `total_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `active_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `completion_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `average_completion_days` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `engagement_score` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `assessment_stats` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `revenue_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `course_id` | OneToOneField | `courses_course` |

#### Indexes

- courses_cou_course__3bcaa8_idx

---

### Enrollment (`courses_enrollment`)

**Model:** `enrollment`  
**App:** `courses`  
**Verbose Name:** Enrollment  
**Plural Name:** Enrollments  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Enrolled student |
| `course_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Enrolled course |
| `status` | CharField | varchar(20) | ✗ | active | ✗ | ✗ | 20 | Enrollment status |
| `completion_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Date when course was completed |
| `last_accessed` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Last time student accessed the course |
| `enrolled_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | Date when student enrolled |
| `total_time_spent` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Total time spent in seconds |
| `progress_percentage` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Enrollment progress percentage (0-100) |
| `last_lesson_accessed_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | Last lesson accessed by student |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `course_id` | ForeignKey | `courses_course` |
| `last_lesson_accessed_id` | ForeignKey | `courses_lesson` |

#### Constraints

- unique_active_enrollment

#### Unique Together

- user, course

#### Indexes

- courses_enr_created_2cb035_idx
- courses_enr_updated_05225a_idx
- courses_enr_user_id_ce8b5b_idx
- courses_enr_course__78d524_idx
- idx_enrl_user_course_act

---

### Lesson (`courses_lesson`)

**Model:** `lesson`  
**App:** `courses`  
**Verbose Name:** Lesson  
**Plural Name:** Lessons  
**Default Ordering:** m, o, d, u, l, e, ,,  , o, r, d, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `order` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `duration_minutes` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Duration in minutes |
| `module_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Parent module |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Lesson title (minimum 2 characters) |
| `content` | TextField | text | ✓ | - | ✗ | ✗ | - | Full content visible to authorized users (minimum 10 characters) |
| `guest_content` | TextField | text | ✗ | - | ✗ | ✗ | - | Preview content for unregistered users |
| `registered_content` | TextField | text | ✗ | - | ✗ | ✗ | - | Limited content for registered users |
| `access_level` | CharField | varchar(20) | ✗ | registered | ✗ | ✗ | 20 | Minimum access level required to view this lesson |
| `type` | CharField | varchar(20) | ✗ | video | ✗ | ✗ | 20 | Type of lesson content |
| `activity_type` | CharField | varchar(20) | ✗ | video | ✗ | ✗ | 20 | Type of learning activity in this lesson |
| `has_assessment` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether lesson includes an assessment |
| `has_lab` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether lesson includes a lab exercise |
| `is_free_preview` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether lesson is available as free preview |
| `video_url` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | URL for video content |
| `transcript` | TextField | text | ✗ | - | ✗ | ✗ | - | Video transcript or lesson transcript |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `module_id` | ForeignKey | `courses_module` |

#### Constraints

- unique_lesson_order

#### Unique Together

- module, order

#### Indexes

- courses_les_created_7fbce2_idx
- courses_les_updated_ac21ad_idx
- courses_les_order_ffd43c_idx
- courses_les_module__4accd4_idx
- courses_les_access__657329_idx
- courses_les_type_805272_idx
- courses_les_activit_845908_idx
- courses_les_is_free_a8e681_idx
- courses_les_has_ass_d9b62a_idx
- courses_les_has_lab_01b267_idx

---

### Module (`courses_module`)

**Model:** `module`  
**App:** `courses`  
**Verbose Name:** Module  
**Plural Name:** Modules  
**Default Ordering:** c, o, u, r, s, e, ,,  , o, r, d, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `order` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `duration_minutes` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Duration in minutes |
| `is_published` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `published_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `course_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Parent course |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Module title (minimum 2 characters) |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | Module description |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `course_id` | ForeignKey | `courses_course` |

#### Constraints

- unique_module_order

#### Unique Together

- course, order

#### Indexes

- courses_mod_created_9a6a7d_idx
- courses_mod_updated_141b50_idx
- courses_mod_order_e9c068_idx
- courses_mod_is_publ_875329_idx
- courses_mod_publish_823717_idx
- courses_mod_course__20183c_idx
- courses_mod_course__92d7f3_idx

---

### Note (`courses_note`)

**Model:** `note`  
**App:** `courses`  
**Verbose Name:** Note  
**Plural Name:** Notes  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | User who created the note |
| `lesson_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Lesson the note is associated with |
| `content` | TextField | text | ✗ | - | ✗ | ✗ | - | Note content |
| `timestamp_seconds` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Timestamp in seconds for video notes |
| `is_private` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Whether this note is private to the user |
| `tags` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Tags for organizing notes |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `lesson_id` | ForeignKey | `courses_lesson` |

#### Indexes

- courses_not_user_id_eece44_idx
- courses_not_lesson__5f16a2_idx

---

### notification (`courses_notification`)

**Model:** `notification`  
**App:** `courses`  
**Verbose Name:** notification  
**Plural Name:** notifications  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `message` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `notification_type` | CharField | varchar(255) | ✗ | announcement | ✗ | ✗ | 255 | - |
| `course_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `is_read` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `read_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `action_url` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `course_id` | ForeignKey | `courses_course` |

#### Indexes

- courses_not_user_id_149621_idx
- courses_not_is_read_7c54d4_idx
- courses_not_notific_2eee2c_idx

---

### Progress (`courses_progress`)

**Model:** `progress`  
**App:** `courses`  
**Verbose Name:** Progress  
**Plural Name:** Progress Records  
**Default Ordering:** -, l, a, s, t, _, a, c, c, e, s, s, e, d  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `enrollment_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Associated enrollment |
| `lesson_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Lesson being tracked |
| `is_completed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether lesson is completed |
| `completed_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Date when lesson was completed |
| `time_spent` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Time spent on this lesson in seconds |
| `progress_percentage` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Progress within this specific lesson (0-100) |
| `notes` | TextField | text | ✗ | - | ✗ | ✗ | - | Student notes for this lesson |
| `last_accessed` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Last time lesson was accessed |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `enrollment_id` | ForeignKey | `courses_enrollment` |
| `lesson_id` | ForeignKey | `courses_lesson` |

#### Constraints

- unique_progress_record

#### Unique Together

- enrollment, lesson

#### Indexes

- courses_pro_created_6822b9_idx
- courses_pro_updated_f54b15_idx
- courses_pro_enrollm_e8bb03_idx
- courses_pro_lesson__76321e_idx
- courses_pro_enrollm_96426f_idx

---

### Question (`courses_question`)

**Model:** `question`  
**App:** `courses`  
**Verbose Name:** Question  
**Plural Name:** Questions  
**Default Ordering:** a, s, s, e, s, s, m, e, n, t, ,,  , o, r, d, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `assessment_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Parent assessment |
| `question_text` | TextField | text | ✗ | - | ✗ | ✗ | - | Question text |
| `text` | TextField | text | ✗ | - | ✗ | ✗ | - | Alias for question_text for backward compatibility |
| `question_type` | CharField | varchar(20) | ✗ | multiple_choice | ✗ | ✗ | 20 | Type of question |
| `points` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | Points awarded for correct answer |
| `order` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | - |
| `explanation` | TextField | text | ✗ | - | ✗ | ✗ | - | Explanation shown after answering |
| `feedback` | TextField | text | ✗ | - | ✗ | ✗ | - | Alias for explanation for backward compatibility |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `assessment_id` | ForeignKey | `courses_assessment` |

#### Constraints

- unique_question_order

#### Unique Together

- assessment, order

#### Indexes

- courses_que_assessm_2927ae_idx
- courses_que_questio_beffac_idx

---

### Resource (`courses_resource`)

**Model:** `resource`  
**App:** `courses`  
**Verbose Name:** Resource  
**Plural Name:** Resources  
**Default Ordering:** l, e, s, s, o, n, ,,  , o, r, d, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `order` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `duration_minutes` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Duration in minutes |
| `storage_key` | CharField | varchar(512) | ✓ | - | ✗ | ✗ | 512 | Cloud storage path/object name |
| `uploaded` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether file uploaded successfully |
| `file_size` | PositiveBigIntegerField | bigint | ✓ | - | ✗ | ✗ | - | File size in bytes |
| `mime_type` | CharField | varchar(120) | ✓ | - | ✗ | ✗ | 120 | MIME type of uploaded file |
| `lesson_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Parent lesson |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Resource title (minimum 2 characters) |
| `type` | CharField | varchar(20) | ✗ | - | ✗ | ✗ | 20 | Type of resource |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | Resource description |
| `file` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | Uploaded file resource |
| `url` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | External URL resource |
| `premium` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether this resource requires premium subscription |
| `download_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Number of times this resource was downloaded |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `lesson_id` | ForeignKey | `courses_lesson` |

#### Constraints

- unique_resource_order

#### Unique Together

- lesson, order

#### Indexes

- courses_res_created_2d1e4f_idx
- courses_res_updated_5e9c80_idx
- courses_res_order_e289a6_idx
- courses_res_uploade_42c1ed_idx
- courses_res_mime_ty_616554_idx
- courses_res_lesson__12dbf2_idx
- courses_res_type_380823_idx
- courses_res_premium_945503_idx

---

### Review (`courses_review`)

**Model:** `review`  
**App:** `courses`  
**Verbose Name:** Review  
**Plural Name:** Reviews  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | User who wrote the review |
| `course_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | Course being reviewed |
| `rating` | PositiveSmallIntegerField | smallint | ✗ | - | ✗ | ✗ | - | Rating from 1 to 5 stars |
| `title` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | Review title |
| `content` | TextField | text | ✗ | - | ✗ | ✗ | - | Review content (minimum 10 characters) |
| `helpful_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Number of users who found this review helpful |
| `is_verified_purchase` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether reviewer is enrolled in the course |
| `is_approved` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Whether review is approved for display |
| `is_featured` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether review is featured |
| `moderation_notes` | TextField | text | ✗ | - | ✗ | ✗ | - | Internal moderation notes |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `course_id` | ForeignKey | `courses_course` |

#### Constraints

- unique_user_course_review

#### Unique Together

- user, course

#### Indexes

- courses_rev_course__c5c65a_idx
- courses_rev_user_id_6a1f95_idx
- courses_rev_is_appr_03a92f_idx
- courses_rev_rating_004eae_idx

---

### user activity (`courses_useractivity`)

**Model:** `useractivity`  
**App:** `courses`  
**Verbose Name:** user activity  
**Plural Name:** User activities  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `activity_type` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `course_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `lesson_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `resource_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `assessment_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |
| `course_id` | ForeignKey | `courses_course` |
| `lesson_id` | ForeignKey | `courses_lesson` |
| `resource_id` | ForeignKey | `courses_resource` |
| `assessment_id` | ForeignKey | `courses_assessment` |

#### Indexes

- courses_use_user_id_b38400_idx
- courses_use_course__fa711b_idx
- courses_use_activit_804475_idx

---

### User Preference (`courses_userpreference`)

**Model:** `userpreference`  
**App:** `courses`  
**Verbose Name:** User Preference  
**Plural Name:** User Preferences  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | User these preferences belong to |
| `email_notifications` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Receive email notifications for course updates |
| `push_notifications` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Receive push notifications on supported devices |
| `reminder_frequency` | CharField | varchar(20) | ✗ | weekly | ✗ | ✗ | 20 | How often to receive study reminders |
| `theme` | CharField | varchar(20) | ✗ | system | ✗ | ✗ | 20 | Visual theme preference |
| `language` | CharField | varchar(10) | ✗ | en | ✗ | ✗ | 10 | Preferred language code (ISO 639-1) |
| `timezone` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | User's preferred timezone |
| `autoplay_videos` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Automatically play videos when starting lessons |
| `video_playback_speed` | DecimalField | numeric(3, 2) | ✗ | 1.0 | ✗ | ✗ | - | Default video playback speed (0.25 to 3.00) |
| `auto_advance_lessons` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Automatically advance to next lesson after completion |
| `content_filters` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Content filtering preferences as JSON |
| `accessibility` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Accessibility settings as JSON |
| `profile_visibility` | CharField | varchar(20) | ✗ | students_only | ✗ | ✗ | 20 | Who can view your profile and progress |
| `show_progress_to_instructors` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Allow instructors to see your detailed progress |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

#### Indexes

- courses_use_theme_92da9e_idx
- courses_use_languag_9ff8cf_idx
- courses_use_profile_c01d2b_idx

---

### user stats (`courses_userstats`)

**Model:** `userstats`  
**App:** `courses`  
**Verbose Name:** user stats  
**Plural Name:** User stats  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `courses_enrolled` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `courses_completed` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_time_spent_seconds` | PositiveBigIntegerField | bigint | ✗ | - | ✗ | ✗ | - | - |
| `assessment_avg_score` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `last_activity` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `activity_streak` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `learning_habits` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

#### Indexes

- courses_use_user_id_689f8b_idx
- courses_use_activit_2aa706_idx

---

## Django_Celery_Beat App

### clocked (`django_celery_beat_clockedschedule`)

**Model:** `clockedschedule`  
**App:** `django_celery_beat`  
**Verbose Name:** clocked  
**Plural Name:** clocked  
**Default Ordering:** c, l, o, c, k, e, d, _, t, i, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `clocked_time` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | Run the task at clocked time |

---

### crontab (`django_celery_beat_crontabschedule`)

**Model:** `crontabschedule`  
**App:** `django_celery_beat`  
**Verbose Name:** crontab  
**Plural Name:** crontabs  
**Default Ordering:** m, o, n, t, h, _, o, f, _, y, e, a, r, ,,  , d, a, y, _, o, f, _, m, o, n, t, h, ,,  , d, a, y, _, o, f, _, w, e, e, k, ,,  , h, o, u, r, ,,  , m, i, n, u, t, e, ,,  , t, i, m, e, z, o, n, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `minute` | CharField | varchar(240) | ✗ | * | ✗ | ✗ | 240 | Cron Minutes to Run. Use "*" for "all". (Example: "0,30") |
| `hour` | CharField | varchar(96) | ✗ | * | ✗ | ✗ | 96 | Cron Hours to Run. Use "*" for "all". (Example: "8,20") |
| `day_of_month` | CharField | varchar(124) | ✗ | * | ✗ | ✗ | 124 | Cron Days Of The Month to Run. Use "*" for "all". (Example: "1,15") |
| `month_of_year` | CharField | varchar(64) | ✗ | * | ✗ | ✗ | 64 | Cron Months (1-12) Of The Year to Run. Use "*" for "all". (Example: "1,12") |
| `day_of_week` | CharField | varchar(64) | ✗ | * | ✗ | ✗ | 64 | Cron Days Of The Week to Run. Use "*" for "all", Sunday is 0 or 7, Monday is 1. (Example: "0,5") |
| `timezone` | CharField | varchar(63) | ✗ | Asia/Kolkata | ✗ | ✗ | 63 | Timezone to Run the Cron Schedule on. Default is UTC. |

---

### interval (`django_celery_beat_intervalschedule`)

**Model:** `intervalschedule`  
**App:** `django_celery_beat`  
**Verbose Name:** interval  
**Plural Name:** intervals  
**Default Ordering:** p, e, r, i, o, d, ,,  , e, v, e, r, y  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `every` | IntegerField | integer | ✗ | - | ✗ | ✗ | - | Number of interval periods to wait before running the task again |
| `period` | CharField | varchar(24) | ✗ | - | ✗ | ✗ | 24 | The type of period between task runs (Example: days) |

---

### periodic task (`django_celery_beat_periodictask`)

**Model:** `periodictask`  
**App:** `django_celery_beat`  
**Verbose Name:** periodic task  
**Plural Name:** periodic tasks  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `name` | CharField | varchar(200) | ✗ | - | ✗ | ✓ | 200 | Short Description For This Task |
| `task` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | The Name of the Celery Task that Should be Run.  (Example: "proj.tasks.import_contacts") |
| `interval_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | Interval Schedule to run the task on.  Set only one schedule type, leave the others null. |
| `crontab_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | Crontab Schedule to run the task on.  Set only one schedule type, leave the others null. |
| `solar_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | Solar Schedule to run the task on.  Set only one schedule type, leave the others null. |
| `clocked_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | Clocked Schedule to run the task on.  Set only one schedule type, leave the others null. |
| `args` | TextField | text | ✗ | [] | ✗ | ✗ | - | JSON encoded positional arguments (Example: ["arg1", "arg2"]) |
| `kwargs` | TextField | text | ✗ | {} | ✗ | ✗ | - | JSON encoded keyword arguments (Example: {"argument": "value"}) |
| `queue` | CharField | varchar(200) | ✓ | - | ✗ | ✗ | 200 | Queue defined in CELERY_TASK_QUEUES. Leave None for default queuing. |
| `exchange` | CharField | varchar(200) | ✓ | - | ✗ | ✗ | 200 | Override Exchange for low-level AMQP routing |
| `routing_key` | CharField | varchar(200) | ✓ | - | ✗ | ✗ | 200 | Override Routing Key for low-level AMQP routing |
| `headers` | TextField | text | ✗ | {} | ✗ | ✗ | - | JSON encoded message headers for the AMQP message. |
| `priority` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Priority Number between 0 and 255. Supported by: RabbitMQ, Redis (priority reversed, 0 is highest). |
| `expires` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Datetime after which the schedule will no longer trigger the task to run |
| `expire_seconds` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | Timedelta with seconds which the schedule will no longer trigger the task to run |
| `one_off` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | If True, the schedule will only run the task a single time |
| `start_time` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Datetime when the schedule should begin triggering the task to run |
| `enabled` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Set to False to disable the schedule |
| `last_run_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | Datetime that the schedule last triggered the task to run. Reset to None if enabled is set to False. |
| `total_run_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | Running count of how many times the schedule has triggered the task |
| `date_changed` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | Datetime that this PeriodicTask was last modified |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | Detailed description about the details of this Periodic Task |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `interval_id` | ForeignKey | `django_celery_beat_intervalschedule` |
| `crontab_id` | ForeignKey | `django_celery_beat_crontabschedule` |
| `solar_id` | ForeignKey | `django_celery_beat_solarschedule` |
| `clocked_id` | ForeignKey | `django_celery_beat_clockedschedule` |

---

### periodic task track (`django_celery_beat_periodictasks`)

**Model:** `periodictasks`  
**App:** `django_celery_beat`  
**Verbose Name:** periodic task track  
**Plural Name:** periodic task tracks  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `ident` | SmallIntegerField | smallint | ✗ | 1 | ✓ | ✓ | - | - |
| `last_update` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

---

### solar event (`django_celery_beat_solarschedule`)

**Model:** `solarschedule`  
**App:** `django_celery_beat`  
**Verbose Name:** solar event  
**Plural Name:** solar events  
**Default Ordering:** e, v, e, n, t, ,,  , l, a, t, i, t, u, d, e, ,,  , l, o, n, g, i, t, u, d, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `event` | CharField | varchar(24) | ✗ | - | ✗ | ✗ | 24 | The type of solar event when the job should run |
| `latitude` | DecimalField | numeric(9, 6) | ✗ | - | ✗ | ✗ | - | Run the task when the event happens at this latitude |
| `longitude` | DecimalField | numeric(9, 6) | ✗ | - | ✗ | ✗ | - | Run the task when the event happens at this longitude |

#### Unique Together

- event, latitude, longitude

---

## Instructor_Portal App

### Course Content Draft (`instructor_portal_coursecontentdraft`)

**Model:** `coursecontentdraft`  
**App:** `instructor_portal`  
**Verbose Name:** Course Content Draft  
**Plural Name:** Course Content Drafts  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `session_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `content_type` | CharField | varchar(30) | ✗ | - | ✗ | ✗ | 30 | - |
| `file_path` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |
| `content_hash` | CharField | varchar(64) | ✗ | - | ✗ | ✗ | 64 | SHA-256 hash for content deduplication and integrity |
| `version` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | - |
| `is_processed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether file has been processed and validated |
| `processing_status` | CharField | varchar(30) | ✗ | pending | ✗ | ✗ | 30 | - |
| `processing_error` | TextField | text | ✗ | - | ✗ | ✗ | - | Error message if processing failed |
| `file_size` | PositiveIntegerField | integer | ✓ | - | ✗ | ✗ | - | - |
| `mime_type` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `original_filename` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `processing_metadata` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Additional metadata from processing (dimensions, duration, etc.) |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `processed_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `session_id` | ForeignKey | `instructor_portal_coursecreationsession` |

#### Unique Together

- session, content_type, version

#### Indexes

- instructor__session_f8b88d_idx
- instructor__content_c32597_idx
- instructor__is_proc_36af61_idx
- instructor__process_5df0ce_idx

---

### Course Creation Session (`instructor_portal_coursecreationsession`)

**Model:** `coursecreationsession`  
**App:** `instructor_portal`  
**Verbose Name:** Course Creation Session  
**Plural Name:** Course Creation Sessions  
**Default Ordering:** -, u, p, d, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `session_id` | UUIDField | uuid | ✗ | 4bfd6fd7-9e25-4366-b89f-abadf8903345 | ✗ | ✓ | 32 | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `creation_method` | CharField | varchar(30) | ✗ | wizard | ✗ | ✗ | 30 | - |
| `template_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `status` | CharField | varchar(30) | ✗ | draft | ✗ | ✗ | 30 | - |
| `current_step` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | - |
| `total_steps` | PositiveIntegerField | integer | ✗ | 6 | ✗ | ✗ | - | - |
| `completion_percentage` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `course_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Course information and content being created |
| `metadata` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Additional session information and tracking data |
| `steps_completed` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `validation_errors` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `template_used` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `ai_prompts_used` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | When this session expires if not completed |
| `last_activity` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `published_course_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | ForeignKey | `instructor_portal_instructorprofile` |
| `template_id` | ForeignKey | `instructor_portal_coursetemplate` |
| `published_course_id` | ForeignKey | `courses_course` |

#### Indexes

- instructor__instruc_fffdb5_idx
- instructor__status_ff6efa_idx
- instructor__session_1a1386_idx
- instructor__creatio_af8e34_idx

---

### Course Instructor (`instructor_portal_courseinstructor`)

**Model:** `courseinstructor`  
**App:** `instructor_portal`  
**Verbose Name:** Course Instructor  
**Plural Name:** Course Instructors  
**Default Ordering:** c, o, u, r, s, e, ,,  , -, i, s, _, l, e, a, d, ,,  , j, o, i, n, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `course_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `role` | CharField | varchar(30) | ✗ | primary | ✗ | ✗ | 30 | - |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `is_lead` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `can_edit_content` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `can_manage_students` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `can_view_analytics` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `revenue_share_percentage` | DecimalField | numeric(5, 2) | ✗ | 100.00 | ✗ | ✗ | - | - |
| `joined_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `course_id` | ForeignKey | `courses_course` |
| `instructor_id` | ForeignKey | `users_customuser` |

#### Constraints

- valid_revenue_share_percentage

#### Unique Together

- course, instructor

#### Indexes

- instructor__course__80570e_idx
- instructor__instruc_6c0904_idx
- instructor__role_dc193b_idx

---

### Course Template (`instructor_portal_coursetemplate`)

**Model:** `coursetemplate`  
**App:** `instructor_portal`  
**Verbose Name:** Course Template  
**Plural Name:** Course Templates  
**Default Ordering:** n, a, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `name` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `description` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `template_type` | CharField | varchar(30) | ✗ | - | ✗ | ✗ | 30 | - |
| `template_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | JSON structure for the course template |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `is_premium` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Only available to higher tier instructors |
| `required_tier` | CharField | varchar(30) | ✗ | bronze | ✗ | ✗ | 30 | - |
| `usage_count` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `success_rate` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `created_by_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `tags` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `created_by_id` | ForeignKey | `users_customuser` |

#### Indexes

- instructor__templat_e5f5ef_idx
- instructor__is_acti_bb05a8_idx
- instructor__usage_c_377784_idx

---

### Draft Course Content (`instructor_portal_draftcoursecontent`)

**Model:** `draftcoursecontent`  
**App:** `instructor_portal`  
**Verbose Name:** Draft Course Content  
**Plural Name:** Draft Course Contents  
**Default Ordering:** o, r, d, e, r, ,,  , v, e, r, s, i, o, n  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `session_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `content_type` | CharField | varchar(30) | ✗ | - | ✗ | ✗ | 30 | - |
| `content_id` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | Unique identifier for this content piece |
| `version` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | Version number for AI iteration support |
| `content_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | JSON structure containing the actual content |
| `title` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `order` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | - |
| `is_complete` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether this content piece is ready for publication |
| `validation_errors` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | List of validation errors for this content |
| `auto_save_version` | PositiveIntegerField | integer | ✗ | 1 | ✗ | ✗ | - | Internal version for auto-save functionality |
| `last_saved` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `ai_generated` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Whether this content was generated using AI |
| `ai_prompt` | TextField | text | ✗ | - | ✗ | ✗ | - | Original AI prompt used to generate this content |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `session_id` | ForeignKey | `instructor_portal_coursecreationsession` |

#### Unique Together

- session, content_type, content_id, version

#### Indexes

- instructor__session_60ca31_idx
- instructor__session_126edb_idx
- instructor__session_ab2b78_idx
- instructor__is_comp_5366a4_idx

---

### Instructor Analytics (`instructor_portal_instructoranalytics`)

**Model:** `instructoranalytics`  
**App:** `instructor_portal`  
**Verbose Name:** Instructor Analytics  
**Plural Name:** Instructor Analytics  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `total_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_courses` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `average_rating` | DecimalField | numeric(3, 2) | ✗ | - | ✗ | ✗ | - | - |
| `total_reviews` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_revenue` | DecimalField | numeric(12, 2) | ✗ | - | ✗ | ✗ | - | - |
| `completion_rate` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `student_satisfaction_rate` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `monthly_revenue` | DecimalField | numeric(12, 2) | ✗ | - | ✗ | ✗ | - | - |
| `last_updated` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `last_calculated` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | OneToOneField | `instructor_portal_instructorprofile` |

#### Constraints

- analytics_valid_rating
- analytics_positive_revenue

#### Indexes

- instructor__instruc_b18673_idx
- instructor__total_s_6586c2_idx

---

### Analytics History (`instructor_portal_instructoranalyticshistory`)

**Model:** `instructoranalyticshistory`  
**App:** `instructor_portal`  
**Verbose Name:** Analytics History  
**Plural Name:** Analytics History  
**Default Ordering:** -, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `date` | DateTimeField | timestamp with time zone | ✗ | 2025-07-11 15:23:50.867245+00:00 | ✗ | ✗ | - | - |
| `total_students` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `total_courses` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `average_rating` | DecimalField | numeric(3, 2) | ✗ | - | ✗ | ✗ | - | - |
| `total_revenue` | DecimalField | numeric(12, 2) | ✗ | - | ✗ | ✗ | - | - |
| `completion_rate` | DecimalField | numeric(5, 2) | ✗ | - | ✗ | ✗ | - | - |
| `data_type` | CharField | varchar(50) | ✗ | daily | ✗ | ✗ | 50 | Type of analytics snapshot (daily, weekly, monthly) |
| `additional_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | ForeignKey | `instructor_portal_instructorprofile` |

#### Indexes

- instructor__instruc_a853b6_idx
- instructor__instruc_105e89_idx

---

### Instructor Dashboard (`instructor_portal_instructordashboard`)

**Model:** `instructordashboard`  
**App:** `instructor_portal`  
**Verbose Name:** Instructor Dashboard  
**Plural Name:** Instructor Dashboards  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `show_analytics` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `show_recent_students` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `show_performance_metrics` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `show_revenue_charts` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `show_course_progress` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `notify_new_enrollments` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `notify_new_reviews` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `notify_course_completions` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `widget_order` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `custom_colors` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | OneToOneField | `instructor_portal_instructorprofile` |

---

### Instructor Notification (`instructor_portal_instructornotification`)

**Model:** `instructornotification`  
**App:** `instructor_portal`  
**Verbose Name:** Instructor Notification  
**Plural Name:** Instructor Notifications  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `notification_type` | CharField | varchar(30) | ✗ | - | ✗ | ✗ | 30 | - |
| `priority` | CharField | varchar(20) | ✗ | medium | ✗ | ✗ | 20 | - |
| `title` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `message` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `action_url` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | URL for the primary action button |
| `action_text` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | Text for the primary action button |
| `metadata` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | Additional data related to the notification |
| `is_read` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `read_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_dismissed` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `dismissed_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `email_sent` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `email_sent_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | When this notification should be automatically dismissed |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | ForeignKey | `instructor_portal_instructorprofile` |

#### Indexes

- instructor__instruc_7d1457_idx
- instructor__instruc_bf496b_idx
- instructor__priorit_1cb57a_idx
- instructor__expires_657510_idx

---

### Instructor Profile (`instructor_portal_instructorprofile`)

**Model:** `instructorprofile`  
**App:** `instructor_portal`  
**Verbose Name:** Instructor Profile  
**Plural Name:** Instructor Profiles  
**Default Ordering:** -, c, r, e, a, t, e, d, _, d, a, t, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `display_name` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | Name shown to students |
| `bio` | TextField | text | ✗ | - | ✗ | ✗ | 2000 | Professional biography and background |
| `title` | CharField | varchar(150) | ✗ | - | ✗ | ✗ | 150 | e.g., Senior Software Engineer, PhD in Computer Science |
| `organization` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `years_experience` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `website` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `linkedin_profile` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `twitter_handle` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | - |
| `profile_image` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |
| `cover_image` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |
| `status` | CharField | varchar(30) | ✗ | pending | ✗ | ✗ | 30 | - |
| `is_verified` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Identity and credentials verified |
| `tier` | CharField | varchar(30) | ✗ | bronze | ✗ | ✗ | 30 | - |
| `email_notifications` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `marketing_emails` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `public_profile` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | Allow students to view your profile |
| `approved_by_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `approval_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `suspension_reason` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `created_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `last_login` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |
| `approved_by_id` | ForeignKey | `users_customuser` |

#### Constraints

- valid_experience_years

#### Indexes

- instructor_status_verified_idx
- instructor_tier_created_idx
- instructor_status_tier_idx

---

### Instructor Session (`instructor_portal_instructorsession`)

**Model:** `instructorsession`  
**App:** `instructor_portal`  
**Verbose Name:** Instructor Session  
**Plural Name:** Instructor Sessions  
**Default Ordering:** -, l, o, g, i, n, _, t, i, m, e  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `instructor_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `session_key` | CharField | varchar(40) | ✗ | - | ✗ | ✓ | 40 | - |
| `ip_address` | GenericIPAddressField | inet | ✗ | - | ✗ | ✗ | 39 | - |
| `user_agent` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `device_type` | CharField | varchar(20) | ✗ | unknown | ✗ | ✗ | 20 | - |
| `location` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | Approximate location based on IP |
| `login_time` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `last_activity` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `logout_time` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `is_suspicious` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Flagged for suspicious activity |
| `security_notes` | TextField | text | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `instructor_id` | ForeignKey | `instructor_portal_instructorprofile` |

#### Indexes

- instructor__instruc_a56576_idx
- instructor__session_8512ff_idx
- instructor__ip_addr_6fb7f3_idx
- instructor__is_acti_dbf638_idx

---

## Sessions App

### session (`django_session`)

**Model:** `session`  
**App:** `sessions`  
**Verbose Name:** session  
**Plural Name:** sessions  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `session_key` | CharField | varchar(40) | ✗ | - | ✓ | ✓ | 40 | - |
| `session_data` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `expire_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

---

## Sites App

### site (`django_site`)

**Model:** `site`  
**App:** `sites`  
**Verbose Name:** site  
**Plural Name:** sites  
**Default Ordering:** d, o, m, a, i, n  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `domain` | CharField | varchar(100) | ✗ | - | ✗ | ✓ | 100 | - |
| `name` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | - |

---

## Social_Django App

### association (`social_auth_association`)

**Model:** `association`  
**App:** `social_django`  
**Verbose Name:** association  
**Plural Name:** associations  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `server_url` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `handle` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `secret` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `issued` | IntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `lifetime` | IntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `assoc_type` | CharField | varchar(64) | ✗ | - | ✗ | ✗ | 64 | - |

#### Unique Together

- server_url, handle

---

### code (`social_auth_code`)

**Model:** `code`  
**App:** `social_django`  
**Verbose Name:** code  
**Plural Name:** codes  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `email` | CharField | varchar(254) | ✗ | - | ✗ | ✗ | 254 | - |
| `code` | CharField | varchar(32) | ✗ | - | ✗ | ✗ | 32 | - |
| `verified` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `timestamp` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Unique Together

- email, code

---

### nonce (`social_auth_nonce`)

**Model:** `nonce`  
**App:** `social_django`  
**Verbose Name:** nonce  
**Plural Name:** nonces  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `server_url` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `timestamp` | IntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `salt` | CharField | varchar(65) | ✗ | - | ✗ | ✗ | 65 | - |

#### Unique Together

- server_url, timestamp, salt

---

### partial (`social_auth_partial`)

**Model:** `partial`  
**App:** `social_django`  
**Verbose Name:** partial  
**Plural Name:** partials  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `token` | CharField | varchar(32) | ✗ | - | ✗ | ✗ | 32 | - |
| `next_step` | PositiveSmallIntegerField | smallint | ✗ | - | ✗ | ✗ | - | - |
| `backend` | CharField | varchar(32) | ✗ | - | ✗ | ✗ | 32 | - |
| `data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `timestamp` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

---

### user social auth (`social_auth_usersocialauth`)

**Model:** `usersocialauth`  
**App:** `social_django`  
**Verbose Name:** user social auth  
**Plural Name:** user social auths  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `provider` | CharField | varchar(32) | ✗ | - | ✗ | ✗ | 32 | - |
| `uid` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `extra_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |
| `created` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `modified` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Unique Together

- provider, uid

---

## Socialaccount App

### social account (`socialaccount_socialaccount`)

**Model:** `socialaccount`  
**App:** `socialaccount`  
**Verbose Name:** social account  
**Plural Name:** social accounts  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `provider` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `uid` | CharField | varchar(191) | ✗ | - | ✗ | ✗ | 191 | - |
| `last_login` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `date_joined` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `extra_data` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Unique Together

- provider, uid

---

### social application (`socialaccount_socialapp`)

**Model:** `socialapp`  
**App:** `socialaccount`  
**Verbose Name:** social application  
**Plural Name:** social applications  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `provider` | CharField | varchar(30) | ✗ | - | ✗ | ✗ | 30 | - |
| `provider_id` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `name` | CharField | varchar(40) | ✗ | - | ✗ | ✗ | 40 | - |
| `client_id` | CharField | varchar(191) | ✗ | - | ✗ | ✗ | 191 | App ID, or consumer key |
| `secret` | CharField | varchar(191) | ✗ | - | ✗ | ✗ | 191 | API secret, client secret, or consumer secret |
| `key` | CharField | varchar(191) | ✗ | - | ✗ | ✗ | 191 | Key |
| `settings` | JSONField | jsonb | ✗ | - | ✗ | ✗ | - | - |

---

### social application token (`socialaccount_socialtoken`)

**Model:** `socialtoken`  
**App:** `socialaccount`  
**Verbose Name:** social application token  
**Plural Name:** social application tokens  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | AutoField | integer | ✗ | - | ✓ | ✓ | - | - |
| `app_id` | ForeignKey | integer | ✓ | - | ✗ | ✗ | - | - |
| `account_id` | ForeignKey | integer | ✗ | - | ✗ | ✗ | - | - |
| `token` | TextField | text | ✗ | - | ✗ | ✗ | - | "oauth_token" (OAuth1) or access token (OAuth2) |
| `token_secret` | TextField | text | ✗ | - | ✗ | ✗ | - | "oauth_token_secret" (OAuth1) or refresh token (OAuth2) |
| `expires_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `app_id` | ForeignKey | `socialaccount_socialapp` |
| `account_id` | ForeignKey | `socialaccount_socialaccount` |

#### Unique Together

- app, account

---

## Token_Blacklist App

### blacklisted token (`token_blacklist_blacklistedtoken`)

**Model:** `blacklistedtoken`  
**App:** `token_blacklist`  
**Verbose Name:** blacklisted token  
**Plural Name:** blacklisted tokens  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `token_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `blacklisted_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `token_id` | OneToOneField | `token_blacklist_outstandingtoken` |

---

### outstanding token (`token_blacklist_outstandingtoken`)

**Model:** `outstandingtoken`  
**App:** `token_blacklist`  
**Verbose Name:** outstanding token  
**Plural Name:** outstanding tokens  
**Default Ordering:** u, s, e, r  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✓ | - | ✗ | ✗ | - | - |
| `jti` | CharField | varchar(255) | ✗ | - | ✗ | ✓ | 255 | - |
| `token` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `created_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

---

## Users App

### user (`users_customuser`)

**Model:** `customuser`  
**App:** `users`  
**Verbose Name:** user  
**Plural Name:** users  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `password` | CharField | varchar(128) | ✗ | - | ✗ | ✗ | 128 | - |
| `is_superuser` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Designates that this user has all permissions without explicitly assigning them. |
| `first_name` | CharField | varchar(150) | ✗ | - | ✗ | ✗ | 150 | - |
| `last_name` | CharField | varchar(150) | ✗ | - | ✗ | ✗ | 150 | - |
| `is_staff` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | Designates whether the user can log into this admin site. |
| `email` | CharField | varchar(254) | ✗ | - | ✗ | ✓ | 254 | - |
| `username` | CharField | varchar(150) | ✗ | - | ✗ | ✓ | 150 | - |
| `role` | CharField | varchar(20) | ✗ | student | ✗ | ✗ | 20 | - |
| `is_email_verified` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `date_joined` | DateTimeField | timestamp with time zone | ✗ | 2025-07-11 15:23:50.845775+00:00 | ✗ | ✗ | - | - |
| `last_login` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `failed_login_attempts` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `temporary_ban_until` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |

---

### email verification (`users_emailverification`)

**Model:** `emailverification`  
**App:** `users`  
**Verbose Name:** email verification  
**Plural Name:** email verifications  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `token` | UUIDField | uuid | ✗ | faae7a72-06df-4213-ac50-42d4e7671024 | ✗ | ✓ | 32 | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `verified_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_used` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Indexes

- users_email_token_c80ef6_idx
- users_email_user_id_8f79bf_idx

---

### login log (`users_loginlog`)

**Model:** `loginlog`  
**App:** `users`  
**Verbose Name:** login log  
**Plural Name:** login logs  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `timestamp` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `ip_address` | GenericIPAddressField | inet | ✗ | - | ✗ | ✗ | 39 | - |
| `user_agent` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `successful` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Indexes

- users_login_user_id_312dc6_idx
- users_login_ip_addr_651077_idx

---

### password reset (`users_passwordreset`)

**Model:** `passwordreset`  
**App:** `users`  
**Verbose Name:** password reset  
**Plural Name:** password resets  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `token` | UUIDField | uuid | ✗ | 04dd5041-ed67-42a5-a00f-d7296b37d5fb | ✗ | ✓ | 32 | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `used_at` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_used` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `ip_address` | GenericIPAddressField | inet | ✓ | - | ✗ | ✗ | 39 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Indexes

- users_passw_token_2def9c_idx
- users_passw_user_id_61b761_idx

---

### profile (`users_profile`)

**Model:** `profile`  
**App:** `users`  
**Verbose Name:** profile  
**Plural Name:** profiles  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `profile_picture` | FileField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |
| `bio` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `date_of_birth` | DateField | date | ✓ | - | ✗ | ✗ | - | - |
| `phone_number` | CharField | varchar(20) | ✗ | - | ✗ | ✗ | 20 | - |
| `address` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `city` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `state` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `country` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `postal_code` | CharField | varchar(20) | ✗ | - | ✗ | ✗ | 20 | - |
| `website` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `linkedin` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `twitter` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `github` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `expertise` | CharField | varchar(200) | ✗ | - | ✗ | ✗ | 200 | - |
| `teaching_experience` | PositiveIntegerField | integer | ✗ | - | ✗ | ✗ | - | - |
| `educational_background` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `interests` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `receive_email_notifications` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `receive_marketing_emails` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `updated_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

---

### Subscription (`users_subscription`)

**Model:** `subscription`  
**App:** `users`  
**Verbose Name:** Subscription  
**Plural Name:** Subscriptions  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | OneToOneField | bigint | ✗ | - | ✗ | ✓ | - | - |
| `tier` | CharField | varchar(20) | ✗ | registered | ✗ | ✗ | 20 | - |
| `status` | CharField | varchar(20) | ✗ | active | ✗ | ✗ | 20 | - |
| `start_date` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `end_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `is_auto_renew` | BooleanField | boolean | ✗ | - | ✗ | ✗ | - | - |
| `last_payment_date` | DateTimeField | timestamp with time zone | ✓ | - | ✗ | ✗ | - | - |
| `payment_method` | CharField | varchar(50) | ✓ | - | ✗ | ✗ | 50 | - |
| `payment_id` | CharField | varchar(100) | ✓ | - | ✗ | ✗ | 100 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | OneToOneField | `users_customuser` |

---

### user session (`users_usersession`)

**Model:** `usersession`  
**App:** `users`  
**Verbose Name:** user session  
**Plural Name:** user sessions  

#### Fields

| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |
|--------|------|---------|------|---------|----|---------|-----------|--------------|
| `id` | BigAutoField | bigint | ✗ | - | ✓ | ✓ | - | - |
| `user_id` | ForeignKey | bigint | ✗ | - | ✗ | ✗ | - | - |
| `session_key` | CharField | varchar(255) | ✗ | - | ✗ | ✗ | 255 | - |
| `ip_address` | GenericIPAddressField | inet | ✗ | - | ✗ | ✗ | 39 | - |
| `user_agent` | TextField | text | ✗ | - | ✗ | ✗ | - | - |
| `created_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `expires_at` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `last_activity` | DateTimeField | timestamp with time zone | ✗ | - | ✗ | ✗ | - | - |
| `is_active` | BooleanField | boolean | ✗ | True | ✗ | ✗ | - | - |
| `device_type` | CharField | varchar(50) | ✗ | - | ✗ | ✗ | 50 | - |
| `location` | CharField | varchar(100) | ✗ | - | ✗ | ✗ | 100 | - |
| `login_method` | CharField | varchar(50) | ✓ | - | ✗ | ✗ | 50 | - |

#### Relationships

| Field | Type | Related Table |
|-------|------|---------------|
| `user_id` | ForeignKey | `users_customuser` |

#### Indexes

- users_users_user_id_3887fe_idx
- users_users_session_70af4d_idx

---

## Summary Statistics

| App | Tables | Total Fields |
|-----|--------|-------------|
| account | 2 | 10 |
| admin | 1 | 8 |
| ai_course_builder | 1 | 20 |
| auth | 2 | 6 |
| content | 4 | 28 |
| contenttypes | 1 | 3 |
| courses | 22 | 294 |
| django_celery_beat | 6 | 41 |
| instructor_portal | 11 | 165 |
| sessions | 1 | 3 |
| sites | 1 | 3 |
| social_django | 5 | 29 |
| socialaccount | 3 | 21 |
| token_blacklist | 2 | 9 |
| users | 7 | 81 |
| **Total** | **69** | **721** |
