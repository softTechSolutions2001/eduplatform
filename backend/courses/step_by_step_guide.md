# File Path: /docs/BACKEND_COURSE_SYSTEM_COMPREHENSIVE_SCHEMA.md
# Folder Path: /docs/
# Date Created: 2025-06-17 12:08:42
# Date Revised: 2025-06-17 12:30:28
# Current Date and Time (UTC): 2025-06-17 12:30:28
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-17 12:30:28 UTC
# User: sujibeautysalon
# Version: 3.0.1 - COMPREHENSIVE UNIFIED VERSION WITH CORRECTED METADATA
#
# Comprehensive Backend Course Management System Schema Documentation
#
# This unified document combines the original comprehensive documentation with
# critical corrections verified against the actual codebase to provide accurate
# and complete technical specifications for the Django REST Framework course
# management system backend.
#
# Repository: Course Management System Backend
# Language: Markdown
# Framework: Django REST Framework
# Database: PostgreSQL
# Authentication: Django Token + Session Authentication
#
# This documentation serves as the complete reference for frontend developers
# building applications that integrate with the course management system backend.

# Backend Course Management System - Complete Schema Documentation


## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Database Schema & Models](#database-schema--models)
4. [API Endpoints Specification](#api-endpoints-specification)
5. [Business Logic & Rules](#business-logic--rules)
6. [Validation System](#validation-system)
7. [File Upload & Media Management](#file-upload--media-management)
8. [Real-Time Features & Signals](#real-time-features--signals)
9. [Advanced Features & Integration](#advanced-features--integration)
10. [Performance & Optimization](#performance--optimization)
11. [Error Handling & Status Codes](#error-handling--status-codes)
12. [Frontend Integration Guidelines](#frontend-integration-guidelines)

---

## System Architecture Overview

### Framework & Technology Stack
- **Backend Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL with optimized indexing
- **Authentication**: Django Token Authentication + Session Authentication (VERIFIED)
- **File Storage**: Configurable (local/cloud storage with S3 compatibility)
- **API Architecture**: RESTful API with ViewSets and custom actions
- **Code Architecture**: DRY principles with abstract mixins and utilities

### Core Design Patterns
- **Model-View-Serializer (MVS)** pattern for API endpoints
- **Abstract Mixins** for code reuse across models (TimeStampedMixin, SlugMixin, etc.)
- **Signal-driven automation** for real-time updates
- **Permission-based access control** with role hierarchy
- **Multi-tier content access** system (Guest/Registered/Premium)
- **Course versioning & cloning** system

### Key System Features
- Dual course creation methods (Traditional Builder + AI Integration)
- Multi-tier content access control with fallback content
- Comprehensive assessment system with multiple question types
- Real-time progress tracking and analytics
- Course versioning, cloning, and draft management
- Certificate generation with verification system
- Role-based permissions (Student/Instructor/Administrator)

---

## Authentication & Authorization

### Authentication System (VERIFIED IMPLEMENTATION)
- **Method**: Django Token Authentication + Session Authentication
- **Token Type**: Django's built-in Token model (NOT JWT)
- **Header Format**: `Authorization: Token <token_value>`
- **Session Support**: Cookie-based session authentication for web interface
- **Token Management**: One token per user, regenerated on demand

### Authentication Configuration (ACTUAL)
**DRF Settings**:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
```

### Token Management (VERIFIED)
- **Token Creation**: Auto-created on user registration via signals
- **Token Retrieval**: Login endpoint returns existing token
- **Token Invalidation**: Delete and recreate for logout/security
- **No Expiration**: Tokens don't expire (unlike JWT)

### User Roles & Permissions (FROM ACTUAL CODE)
**Role Hierarchy**: Administrator > Instructor > Student

**Verified Permission Classes**:
- `IsEnrolledOrReadOnly`: Enrollment required for modifications
- `IsEnrolled`: Strict enrollment requirement
- `IsInstructorOrAdmin`: Instructor/admin role verification
- `IsPremiumUser`: Premium subscription verification
- `CanManageCourse`: Course management permissions

**Student Role**:
- Course enrollment and learning
- Progress tracking and note-taking
- Review submission
- Certificate access (premium users)

**Instructor Role**:
- All student permissions
- Course creation and management
- Student progress monitoring
- Assessment grading
- Course analytics access

**Administrator Role**:
- All instructor permissions
- User management
- System-wide analytics
- Category management
- Content moderation

### Access Control Logic (VERIFIED)
**Multi-Tier Content Access**:
- **Guest**: Unauthenticated users (limited preview content)
- **Registered**: Authenticated users (basic content access)
- **Premium**: Paid subscribers (full content access)

**Content Serving Logic**:
1. Check user authentication status
2. Determine user access level (guest/registered/premium)
3. Verify enrollment status for course content
4. Apply access level restrictions
5. Serve appropriate content tier or access denial message

---

## Database Schema & Models

### Model Hierarchy Structure
```
Category (1) → Course (M) → Module (M) → Lesson (M) → Resource/Assessment (M)
                ↓
User (1) → Enrollment (M) → Progress (M) → Certificate (1)
     ↓
     Review (M), Note (M), AssessmentAttempt (M)
```

### Abstract Mixins (FROM ACTUAL MIXINS.PY)

**TimeStampedMixin**:
- `created_date`: DateTimeField(auto_now_add=True)
- `updated_date`: DateTimeField(auto_now=True)

**SlugMixin**:
- `slug`: SlugField(max_length=100, unique=True, blank=True)
- Auto-generation from title/name field

**OrderedMixin**:
- `order`: PositiveIntegerField(default=1)
- Ordering within parent relationships

**PublishableMixin**:
- `is_published`: BooleanField(default=False)
- `published_date`: DateTimeField(blank=True, null=True)

**DurationMixin**:
- `duration_minutes`: PositiveIntegerField(blank=True, null=True, validators=[validate_duration_minutes])

**AnalyticsMixin**:
- `enrolled_students_count`: PositiveIntegerField(default=0)
- `avg_rating`: FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
- `total_reviews`: PositiveIntegerField(default=0)
- `last_enrollment_date`: DateTimeField(null=True, blank=True)

### 1. Category Model
**Purpose**: Organize courses into logical categories

**Field Specifications**:
- `name`: CharField(100) - Unique category name, minimum 2 characters
- `description`: TextField - Optional category description
- `icon`: CharField(50) - CSS icon class for UI display
- `sort_order`: PositiveIntegerField - Display ordering (default: 0)
- `slug`: SlugField - Auto-generated URL-friendly identifier
- `is_active`: BooleanField - Visibility control (default: True)
- `created_date`: DateTimeField - Auto-populated on creation
- `updated_date`: DateTimeField - Auto-updated on modification

**Business Rules**:
- Names must be unique across all categories
- Slug auto-generated from name with uniqueness validation
- Sort order determines display sequence in frontend
- Inactive categories hidden from public API responses
- Computed field: `course_count` available via method

**API Access**: Public read access, admin-only write access

### 2. Course Model (Primary Entity - VERIFIED FROM CODE)
**Purpose**: Central course entity with comprehensive metadata and versioning

**Complete Field List (ACTUAL IMPLEMENTATION)**:
```python
# Basic Information
title = CharField(max_length=160, validators=[MinLengthValidator(3)])
subtitle = CharField(max_length=255, blank=True)
description = TextField(validators=[MinLengthValidator(50)])
category = ForeignKey(Category, on_delete=PROTECT, default=get_default_category)

# Media & Pricing
thumbnail = ImageField(upload_to=upload_course_thumbnail, blank=True)
price = DecimalField(max_digits=10, decimal_places=2, default=Decimal('490.00'), validators=[validate_price_range])
discount_price = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[validate_price_range])
discount_ends = DateTimeField(blank=True, null=True)

# Course Structure (JSON Fields with Validators)
requirements = JSONField(default=list, validators=[validate_course_requirements])
skills = JSONField(default=list, blank=True)
learning_objectives = JSONField(default=list, validators=[validate_learning_objectives])
target_audience = TextField(blank=True)

# Creation Tracking
creation_method = CharField(max_length=20, choices=CREATION_METHODS, default='builder')
completion_status = CharField(max_length=20, choices=COMPLETION_STATUSES, default='not_started')
completion_percentage = PositiveIntegerField(default=0, validators=[validate_percentage])

# Versioning
version = FloatField(default=1.0, validators=[MinValueValidator(1.0)])
is_draft = BooleanField(default=True)
parent_version = ForeignKey('self', null=True, blank=True, on_delete=SET_NULL, related_name='children')

# Features
has_certificate = BooleanField(default=False)
is_featured = BooleanField(default=False)
level = CharField(max_length=20, choices=LEVEL_CHOICES, default='all_levels')
```

**Choice Fields (FROM CONSTANTS.PY)**:
```python
LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('all_levels', 'All Levels')
]

CREATION_METHODS = [
    ('builder', 'Drag & Drop Builder'),
    ('wizard', 'Step-by-Step Wizard'),
    ('ai', 'AI-Powered Builder'),
    ('import', 'Imported Course'),
    ('manual', 'Manual Creation')
]

COMPLETION_STATUSES = [
    ('not_started', 'Not Started'),
    ('partially_complete', 'Partially Complete'),
    ('complete', 'Complete'),
    ('published', 'Published'),
    ('archived', 'Archived')
]
```

**Business Rules**:
- Title uniqueness validated within version family
- Discount price must be less than regular price
- Auto-slug generation with uniqueness handling
- Version increment on cloning (0.1 increments)
- Analytics fields updated via signals on related model changes
- Draft courses invisible to students unless enrolled

### 3. CourseInstructor Model
**Purpose**: Many-to-many relationship between courses and instructors

**Field Specifications**:
- `course`: ForeignKey(Course) - Associated course
- `instructor`: ForeignKey(User) - Instructor user account
- `title`: CharField(100) - Instructor role title (optional)
- `bio`: TextField - Course-specific instructor biography
- `is_lead`: BooleanField - Lead instructor designation
- `is_active`: BooleanField - Active instructor status

**Business Rules**:
- Unique constraint on (course, instructor) combination
- Instructor must have appropriate role permissions
- Lead instructor automatically assigned on course creation
- Multiple instructors allowed per course

### 4. Module Model
**Purpose**: Organize course content into logical sections

**Field Specifications**:
- `course`: ForeignKey(Course) - Parent course
- `title`: CharField(255) - Module title, minimum 2 characters
- `description`: TextField - Module description (optional)
- `order`: PositiveIntegerField - Display order within course
- `duration_minutes`: PositiveIntegerField - Auto-calculated from lessons
- `is_published`: BooleanField - Publication status

**Business Rules**:
- Unique ordering within each course
- Auto-ordering on creation (next available order)
- Duration calculated from all lesson durations
- Unpublished modules hidden from students

### 5. Lesson Model (Multi-Tier Content - VERIFIED)
**Purpose**: Individual learning units with tiered content access

**Core Fields**:
- `module`: ForeignKey(Module) - Parent module
- `title`: CharField(255) - Lesson title, minimum 2 characters
- `order`: PositiveIntegerField - Display order within module
- `type`: CharField(20) - Choices: video/reading/interactive/quiz/lab_exercise/assignment/discussion

**Multi-Tier Content System (VERIFIED)**:
```python
# Tiered Content System
content = TextField(validators=[MinLengthValidator(10)])  # Full content
guest_content = TextField(blank=True, null=True)  # Preview content
registered_content = TextField(blank=True, null=True)  # Limited content

# Access Control
access_level = CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='registered')
is_free_preview = BooleanField(default=False)

# Lesson Type and Features
type = CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
has_assessment = BooleanField(default=False)
has_lab = BooleanField(default=False)

# Media
video_url = URLField(blank=True, validators=[validate_video_url])
transcript = TextField(blank=True, null=True)
```

**Access Level Choices (VERIFIED)**:
```python
ACCESS_LEVEL_CHOICES = [
    ('guest', 'Guest - Unregistered Users'),
    ('registered', 'Registered - Logged In Users'),
    ('premium', 'Premium - Paid Subscribers')
]

LESSON_TYPE_CHOICES = [
    ('video', 'Video'),
    ('reading', 'Reading'),
    ('interactive', 'Interactive'),
    ('quiz', 'Quiz'),
    ('lab_exercise', 'Lab Exercise'),
    ('assignment', 'Assignment'),
    ('discussion', 'Discussion')
]
```

**Business Rules**:
- Content served based on user access level and enrollment status
- Free preview lessons bypass access restrictions
- Guest content required for guest-level access
- Video URL validation for supported platforms
- Unique ordering within each module

### 6. Resource Model
**Purpose**: Supplementary materials attached to lessons

**Field Specifications**:
- `lesson`: ForeignKey(Lesson) - Parent lesson
- `title`: CharField(255) - Resource title, minimum 2 characters
- `type`: CharField(20) - Choices: document/video/audio/image/link/code_sample/tool_software/dataset/template
- `description`: TextField - Resource description (optional)
- `order`: PositiveIntegerField - Display order within lesson

**Content Storage**:
- `file`: FileField - Uploaded file (upload_to: "lesson_resources/")
- `url`: URLField - External resource URL
- `premium`: BooleanField - Premium access requirement

**File Metadata (Auto-populated)**:
- `uploaded`: BooleanField - File upload status
- `file_size`: PositiveBigIntegerField - File size in bytes
- `mime_type`: CharField(120) - File MIME type
- `storage_key`: CharField(512) - Cloud storage path
- `duration_minutes`: PositiveIntegerField - Media duration

**Resource Type Choices**:
```python
RESOURCE_TYPE_CHOICES = [
    ('document', 'Document'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('image', 'Image'),
    ('link', 'Link'),
    ('code_sample', 'Code Sample'),
    ('tool_software', 'Tool/Software'),
    ('dataset', 'Dataset'),
    ('template', 'Template')
]
```

**Business Rules**:
- Either file or URL required based on resource type
- Link-type resources require URL
- File-type resources require file upload
- Premium resources require premium subscription access
- File metadata auto-extracted on upload

### 7. Assessment System Models

#### Assessment Model
**Purpose**: Configure assessments for lessons

**Field Specifications**:
- `lesson`: OneToOneField(Lesson) - Associated lesson
- `title`: CharField(255) - Assessment title, minimum 2 characters
- `description`: TextField - Assessment instructions (optional)
- `time_limit`: PositiveIntegerField - Time limit in minutes (0 = unlimited)
- `passing_score`: PositiveIntegerField - Passing percentage (0-100, default: 70)
- `max_attempts`: PositiveIntegerField - Maximum attempts allowed (default: 3)
- `randomize_questions`: BooleanField - Question randomization flag
- `show_results`: BooleanField - Immediate results display flag

#### Question Model
**Purpose**: Individual assessment questions

**Field Specifications**:
- `assessment`: ForeignKey(Assessment) - Parent assessment
- `question_text`: TextField - Question content, minimum 5 characters
- `question_type`: CharField(20) - Choices: multiple_choice/true_false/short_answer/essay/matching/fill_blank
- `order`: PositiveIntegerField - Question order (randomizable)
- `points`: PositiveIntegerField - Points awarded (minimum: 1)
- `explanation`: TextField - Answer explanation (optional)

**Question Type Choices**:
```python
QUESTION_TYPE_CHOICES = [
    ('multiple_choice', 'Multiple Choice'),
    ('true_false', 'True/False'),
    ('short_answer', 'Short Answer'),
    ('essay', 'Essay'),
    ('matching', 'Matching'),
    ('fill_blank', 'Fill in the Blank')
]
```

#### Answer Model
**Purpose**: Answer choices for questions

**Field Specifications**:
- `question`: ForeignKey(Question) - Parent question
- `answer_text`: CharField(500) - Answer choice text
- `is_correct`: BooleanField - Correct answer flag
- `explanation`: TextField - Answer-specific explanation
- `order`: PositiveIntegerField - Answer display order

**Business Rules**:
- Multiple choice questions require 2+ answers with exactly one correct
- True/false questions auto-generate two answers
- Text questions (short_answer/essay) don't use Answer model
- Answer correctness hidden from students during attempts

### 8. User Interaction Models

#### Enrollment Model
**Purpose**: Track student course registrations

**Field Specifications**:
- `user`: ForeignKey(User) - Enrolled student
- `course`: ForeignKey(Course) - Enrolled course
- `status`: CharField(20) - Choices: active/completed/dropped/suspended/unenrolled
- `completion_date`: DateTimeField - Course completion timestamp
- `last_accessed`: DateTimeField - Last access timestamp (auto-updated)

**Analytics Fields**:
- `total_time_spent`: PositiveIntegerField - Total time in seconds
- `progress_percentage`: PositiveIntegerField - Overall progress (0-100)
- `last_lesson_accessed`: ForeignKey(Lesson) - Last accessed lesson

**Status Choices**:
```python
STATUS_CHOICES = [
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('dropped', 'Dropped'),
    ('suspended', 'Suspended'),
    ('unenrolled', 'Unenrolled')
]
```

**Business Rules**:
- Unique constraint per (user, course)
- Auto-status change to 'completed' at 100% progress
- Progress calculated from lesson completion
- Time tracking via lesson access signals

#### Progress Model
**Purpose**: Track individual lesson progress

**Field Specifications**:
- `enrollment`: ForeignKey(Enrollment) - Parent enrollment
- `lesson`: ForeignKey(Lesson) - Associated lesson
- `is_completed`: BooleanField - Completion status
- `completed_date`: DateTimeField - Completion timestamp
- `time_spent`: PositiveIntegerField - Time spent in seconds
- `progress_percentage`: PositiveIntegerField - Lesson progress (0-100)
- `notes`: TextField - Student notes (optional)
- `last_accessed`: DateTimeField - Last access timestamp

**Business Rules**:
- Unique constraint per (enrollment, lesson)
- Auto-creates progress records on enrollment
- Completion triggers enrollment progress update
- Time tracking via frontend integration

#### Review Model
**Purpose**: Course ratings and feedback

**Field Specifications**:
- `user`: ForeignKey(User) - Review author
- `course`: ForeignKey(Course) - Reviewed course
- `rating`: PositiveSmallIntegerField - 1-5 star rating
- `title`: CharField(255) - Review title (optional)
- `content`: TextField - Review content, minimum 10 characters
- `helpful_count`: PositiveIntegerField - Helpful votes count

**Moderation Fields**:
- `is_verified_purchase`: BooleanField - Enrollment verification flag
- `is_approved`: BooleanField - Moderation approval status
- `moderation_notes`: TextField - Internal moderation notes

**Business Rules**:
- Unique constraint per (user, course)
- Auto-verification based on enrollment status
- Rating updates trigger course analytics recalculation
- Unapproved reviews hidden from public display

#### Certificate Model
**Purpose**: Course completion certificates

**Field Specifications**:
- `enrollment`: OneToOneField(Enrollment) - Associated enrollment
- `certificate_number`: CharField(50) - Unique certificate identifier
- `is_valid`: BooleanField - Certificate validity status
- `revocation_date`: DateTimeField - Revocation timestamp (if revoked)
- `revocation_reason`: TextField - Revocation reason
- `verification_hash`: CharField(64) - SHA-256 verification hash
- `template_version`: CharField(10) - Certificate template version

**Business Rules**:
- Auto-generated on course completion (if course.has_certificate)
- Unique certificate number format: CERT-{course_id}-{user_id}-{timestamp}
- Verification hash for authenticity validation
- Revocation capability for misused certificates

#### Note Model
**Purpose**: Student lesson notes

**Field Specifications**:
- `user`: ForeignKey(User) - Note author
- `lesson`: ForeignKey(Lesson) - Associated lesson
- `content`: TextField - Note content, minimum 1 character
- `is_private`: BooleanField - Privacy setting (default: True)
- `tags`: JSONField - Organization tags (max 10 items, min 2 chars each)

### 9. Assessment Tracking Models

#### AssessmentAttempt Model
**Purpose**: Track assessment attempts

**Field Specifications**:
- `user`: ForeignKey(User) - Student taking assessment
- `assessment`: ForeignKey(Assessment) - Assessment being attempted
- `start_time`: DateTimeField - Attempt start timestamp
- `end_time`: DateTimeField - Attempt completion timestamp
- `score`: PositiveIntegerField - Raw score achieved
- `passed`: BooleanField - Pass/fail status
- `attempt_number`: PositiveIntegerField - Attempt sequence number
- `ip_address`: GenericIPAddressField - User IP address
- `user_agent`: TextField - Browser user agent

**Computed Properties**:
- `score_percentage`: Calculated as (score/max_score) * 100
- `time_taken`: Difference between end_time and start_time

**Business Rules**:
- Auto-increment attempt_number per user/assessment
- Max attempts validation against assessment.max_attempts
- Auto-submission on time limit expiration
- Pass/fail determination based on assessment.passing_score

#### AttemptAnswer Model
**Purpose**: Individual answers within attempts

**Field Specifications**:
- `attempt`: ForeignKey(AssessmentAttempt) - Parent attempt
- `question`: ForeignKey(Question) - Question being answered
- `selected_answer`: ForeignKey(Answer) - Selected answer (for multiple choice)
- `text_answer`: TextField - Text response (for text questions)
- `is_correct`: BooleanField - Correctness flag
- `points_earned`: PositiveIntegerField - Points awarded
- `feedback`: TextField - Instructor feedback (optional)
- `answered_at`: DateTimeField - Answer submission timestamp

**Business Rules**:
- Unique constraint per (attempt, question)
- Auto-validation for multiple choice questions
- Manual grading support for text questions
- Points calculation based on question configuration

---

## API Endpoints Specification

### Base Configuration (VERIFIED)
- **API Base URL**: `/api/`
- **Authentication**: Django Token in Authorization header OR Session cookies
- **Content Type**: `application/json` for requests/responses
- **File Uploads**: `multipart/form-data` for file-containing requests

### Pagination Parameters (CORRECTED)
- **Page Size**: `?page_size=20` (NOT `?limit=20`)
- **Page Number**: `?page=2`
- **Default Page Size**: 20 items per page
- **Max Page Size**: 100 items per page

### 1. Category Endpoints (VERIFIED)
**Base Path**: `/api/categories/`

**GET /api/categories/**
- **Purpose**: List all active categories
- **Authentication**: None required
- **Query Parameters**:
  - `search`: Text search in name/description
  - `page_size`: Items per page (default: 20)
  - `page`: Page number
- **Response**: Paginated array of category objects with course_count

**GET /api/categories/{slug}/**
- **Purpose**: Retrieve specific category details
- **Authentication**: None required
- **Response**: Single category object with full details

### 2. Course Endpoints (VERIFIED FROM CODE)
**Base Path**: `/api/courses/`

**GET /api/courses/**
- **Purpose**: List courses with filtering and pagination
- **Authentication**: Optional (affects content access)
- **Query Parameters** (VERIFIED):
  - `category`: Filter by category slug
  - `level`: Filter by difficulty level
  - `search`: Text search in title/description/subtitle
  - `max_price`: Maximum price filter
  - `is_featured`: Featured courses only (true/false)
  - `is_draft`: Draft status (instructor-only filter)
  - `creation_method`: Filter by creation method
  - `page_size`: Items per page (NOT `limit`)
  - `page`: Page number

**POST /api/courses/**
- **Purpose**: Create new course
- **Authentication**: Required (Instructor role)
- **Content Type**: `multipart/form-data`
- **Request Fields**: All course model fields except computed fields
- **Auto-assignments**: Creator as lead instructor, draft status

**GET /api/courses/{slug}/**
- **Purpose**: Retrieve detailed course information
- **Authentication**: Optional (affects content detail)
- **Response Includes**:
  - Complete course metadata
  - Module and lesson structure
  - User-specific progress (if authenticated)
  - Instructor information
  - Recent reviews
  - Version information

**PUT /api/courses/{slug}/**
- **Purpose**: Update course information
- **Authentication**: Required (Course instructor or admin)
- **Content Type**: `multipart/form-data`
- **Validation**: Edit permission verification

**DELETE /api/courses/{slug}/**
- **Purpose**: Delete course (soft delete recommended)
- **Authentication**: Required (Course instructor or admin)

**Custom Actions (FROM VIEWSET CODE)**:
- `POST /api/courses/{id}/clone/`: Clone course
- `POST /api/courses/{id}/enroll/`: Enroll current user
- `PUT /api/courses/{id}/publish/`: Publish course
- `PUT /api/courses/{id}/unpublish/`: Unpublish course
- `GET /api/courses/featured/`: Get featured courses

**POST /api/courses/{slug}/clone/**
- **Purpose**: Clone course with options
- **Authentication**: Required (Instructor role)
- **Request Body**:
  - `title`: New course title (optional)
  - `copy_modules`: Boolean (default: true)
  - `copy_resources`: Boolean (default: true)
  - `copy_assessments`: Boolean (default: true)
  - `create_as_draft`: Boolean (default: true)

**POST /api/courses/{slug}/enroll/**
- **Purpose**: Enroll current user in course
- **Authentication**: Required
- **Validation**: Enrollment eligibility, subscription requirements

**PUT /api/courses/{slug}/publish/**
- **Purpose**: Publish course (make public)
- **Authentication**: Required (Course instructor or admin)
- **Validation**: Course completion requirements

**PUT /api/courses/{slug}/unpublish/**
- **Purpose**: Unpublish course
- **Authentication**: Required (Course instructor or admin)

**GET /api/courses/featured/**
- **Purpose**: Retrieve featured courses
- **Authentication**: None required
- **Query Parameters**: `page_size`: Maximum results

### 3. Module Endpoints (VERIFIED)
**Base Path**: `/api/modules/`

**GET /api/modules/**
- **Purpose**: List modules with filtering
- **Authentication**: Optional
- **Query Parameters**:
  - `course`: Filter by course slug
  - `course_id`: Filter by course ID
  - `page_size`: Items per page
  - `page`: Page number
- **Response**: Modules with lesson previews

**POST /api/modules/**
- **Purpose**: Create new module
- **Authentication**: Required (Course instructor)
- **Request Fields**: course, title, description, order

**GET /api/modules/{id}/**
- **Purpose**: Retrieve detailed module with lessons
- **Authentication**: Optional (affects lesson content)

**PUT /api/modules/{id}/**
- **Purpose**: Update module
- **Authentication**: Required (Course instructor)

**DELETE /api/modules/{id}/**
- **Purpose**: Delete module
- **Authentication**: Required (Course instructor)

### 4. Lesson Endpoints (VERIFIED)
**Base Path**: `/api/lessons/`

**GET /api/lessons/**
- **Purpose**: List lessons with filtering
- **Authentication**: Optional (affects content access)
- **Query Parameters**:
  - `module`: Filter by module ID
  - `course`: Filter by course slug
  - `access_level`: Filter by access level
  - `type`: Filter by lesson type
  - `free_preview`: Filter free preview lessons
  - `page_size`: Items per page
  - `page`: Page number

**GET /api/lessons/{id}/**
- **Purpose**: Retrieve lesson with access-controlled content
- **Authentication**: Optional
- **Content Logic**:
  - Serves appropriate content based on user access level
  - Free preview overrides access restrictions
  - Enrollment requirement for non-guest content

### 5. Enrollment & Progress Endpoints (VERIFIED)

**GET /api/enrollments/**
- **Purpose**: List user's enrollments
- **Authentication**: Required
- **Query Parameters**:
  - `page_size`: Items per page
  - `page`: Page number
  - `status`: Filter by enrollment status
- **Response**: Enrollments with progress summaries

**POST /api/enrollments/**
- **Purpose**: Create enrollment (alternative to course enrollment endpoint)
- **Authentication**: Required

**POST /api/enrollments/{id}/unenroll/**
- **Purpose**: Unenroll from course
- **Authentication**: Required

**GET /api/progress/**
- **Purpose**: List user's lesson progress
- **Authentication**: Required
- **Query Parameters**:
  - `lesson`: Filter by lesson ID
  - `course`: Filter by course slug
  - `enrollment`: Filter by enrollment ID
  - `page_size`: Items per page
  - `page`: Page number

**PUT /api/progress/{id}/**
- **Purpose**: Update lesson progress
- **Authentication**: Required
- **Request Fields**: is_completed, progress_percentage, time_spent, notes

**GET /api/user/progress-stats/**
- **Purpose**: Comprehensive user progress statistics
- **Authentication**: Required
- **Response**: total_courses, courses_completed, courses_in_progress, total_time_spent, certificates_earned, average_progress

### 6. Assessment Endpoints

**POST /api/assessments/{id}/start/**
- **Purpose**: Start new assessment attempt
- **Authentication**: Required (Enrolled user)
- **Response**: Attempt ID and questions (without correct answers)

**POST /api/attempt-answers/**
- **Purpose**: Submit answer for question
- **Authentication**: Required
- **Request Fields**: attempt_id, question_id, selected_answer_id OR text_answer

**POST /api/assessment-attempts/{id}/complete/**
- **Purpose**: Complete assessment attempt
- **Authentication**: Required
- **Response**: Score, pass/fail status, detailed results

### 7. Review & Certificate Endpoints

**GET /api/reviews/**
- **Purpose**: List user's reviews
- **Authentication**: Required

**POST /api/reviews/**
- **Purpose**: Create course review
- **Authentication**: Required
- **Validation**: Enrollment verification

**GET /api/certificates/**
- **Purpose**: List user's certificates
- **Authentication**: Required (Premium users only)

**GET /api/certificates/verify/**
- **Purpose**: Verify certificate by number
- **Authentication**: None required
- **Query Parameter**: `certificate_number`

### 8. Utility Endpoints

**GET /api/health/**
- **Purpose**: API health check
- **Authentication**: None required
- **Response**: Status, timestamp, version

---

## Business Logic & Rules

### Course Creation Rules
- Title uniqueness within version family
- Minimum content requirements for publication
- Auto-instructor assignment to course creator
- Draft status by default for new courses
- Slug auto-generation with conflict resolution

### Enrollment Rules
- Single enrollment per user per course
- Subscription requirement validation
- Course availability verification
- Auto-progress record creation

### Progress Tracking Rules
- Automatic progress record creation on enrollment
- Real-time progress percentage calculation
- Course completion at 100% lesson completion
- Certificate generation trigger on completion

### Assessment Rules
- Attempt limit enforcement
- Time limit validation and auto-submission
- Score calculation and pass/fail determination
- Answer validation based on question type

### Pricing & Discount Rules
- Discount price must be less than regular price
- Discount expiration handling
- Free course enrollment without restrictions
- Premium content access validation

### Versioning Rules
- Version increment on course cloning (0.1 steps)
- Parent-child relationship maintenance
- Independent editing of cloned versions
- Version family identification

---

## Validation System (FROM ACTUAL VALIDATORS.PY)

### Core Validators (IMPLEMENTED)

**validate_price_range(value)**:
- Validates price between 0 and 10,000
- Supports both integer and decimal values
- Raises ValidationError for out-of-range values

**validate_percentage(value)**:
- Validates percentage between 0 and 100
- Integer values only
- Used for completion_percentage fields

**validate_duration_minutes(value)**:
- Validates duration between 0 and 10,080 minutes (1 week)
- Non-negative values only
- Used for lesson and course durations

**validate_video_url(value)**:
- Validates YouTube, Vimeo, and direct video URLs
- Supports various URL formats
- Pattern matching for supported platforms

**validate_course_requirements(value)**:
- Validates list of up to 20 requirements
- Each requirement minimum 3 characters
- Array structure validation

**validate_learning_objectives(value)**:
- Validates list of up to 15 objectives
- Each objective minimum 5 characters
- Array structure validation

### Custom Validator Classes (IMPLEMENTED)

**MinStrLenValidator**:
- Minimum string length after stripping whitespace
- Deconstructible for migrations
- Custom error messages

**FileSizeValidator**:
- Configurable maximum file size
- Supports different size limits per file type
- Human-readable error messages

**JSONListValidator**:
- Generic JSON list validation
- Configurable item limits and types
- Item-level validation support

### Field-Level Validation
**String Fields**:
- Minimum/maximum length requirements
- Character set restrictions for slugs
- HTML content sanitization

**Numeric Fields**:
- Range validation (0-100 for percentages)
- Positive number enforcement
- Currency format validation

**JSON Fields**:
- Array structure validation
- Item count limits
- Individual item validation

**File Fields**:
- File type restrictions
- Size limitations
- Image dimension validation

### Model-Level Validation
**Course Validation**:
- Title uniqueness within version family
- Discount price vs regular price comparison
- Content requirement verification

**Lesson Validation**:
- Access level consistency
- Content requirement based on access level
- Video URL format validation

**Assessment Validation**:
- Question count requirements
- Answer consistency for question types
- Time limit reasonableness

### Business Logic Validation
**Enrollment Validation**:
- Duplicate enrollment prevention
- Subscription requirement checking
- Course availability verification

**Access Control Validation**:
- User permission verification
- Content access level checking
- Subscription status validation

**Progress Validation**:
- Completion percentage bounds
- Time spent reasonableness
- Sequential lesson access (if configured)

---

## File Upload & Media Management

### Upload Configurations
**Course Thumbnails**:
- Path: `course_thumbnails/{course_id}/`
- Formats: JPG, PNG, WebP
- Max Size: 10MB
- Dimensions: Recommended 1280x720

**Lesson Resources**:
- Path: `lesson_resources/{lesson_id}/`
- Formats: PDF, DOC, DOCX, MP4, MP3, ZIP, etc.
- Max Size: 500MB (videos), 50MB (documents)

**File Metadata Tracking**:
- Auto-extraction of file size, MIME type
- Cloud storage path recording
- Upload status tracking
- Duration extraction for media files

### Storage Architecture
- Local storage for development
- Cloud storage (S3-compatible) for production
- CDN integration for media delivery
- Automatic backup and versioning

---

## Real-Time Features & Signals

### Django Signals Implementation (FROM SIGNALS.PY)

**Post-Save Signals (ACTUAL IMPLEMENTATION)**:
- **Course Post-Save**: Updates duration from modules/lessons, recalculates analytics fields
- **Enrollment Post-Save**: Creates Progress records for all lessons, updates course enrollment count
- **Progress Post-Save**: Updates enrollment progress percentage, triggers completion events
- **Review Post-Save**: Recalculates course average rating, updates review count

**Post-Delete Signals**:
- Review deletion triggers rating recalculation
- Resource deletion triggers storage cleanup

**Pre-Save Signals**:
- Course completion status updates
- Slug generation and uniqueness handling

### Model Method Implementations (VERIFIED)

**Course Methods**:
- `get_absolute_url()`: Returns course detail URL
- `calculate_duration()`: Aggregates lesson durations
- `update_analytics()`: Refreshes cached analytics
- `can_user_enroll(user)`: Enrollment eligibility check

**Enrollment Methods**:
- `calculate_progress()`: Computes completion percentage
- `get_current_lesson()`: Next incomplete lesson
- `mark_completed()`: Course completion handling

### Real-Time Updates
**Progress Tracking**:
- Lesson completion status
- Time spent calculation
- Course progress percentage

**Analytics Updates**:
- Enrollment counts
- Average ratings
- Review statistics

**Content Updates**:
- Course duration calculation
- Module duration aggregation

---

## Advanced Features & Integration

### 1. Course Versioning & Cloning System

**Version Management Architecture**:
- **Version Numbering**: Semantic versioning with 0.1 increments (1.0, 1.1, 1.2, etc.)
- **Parent-Child Relationships**: Cloned courses maintain reference to original
- **Independent Evolution**: Cloned versions can be modified independently
- **Version Family**: Grouped by original course for management

**Clone Operation Specifications**:
- **Selective Cloning**: Options to clone modules, resources, assessments independently
- **Content Inheritance**: Cloned content inherits original structure and content
- **Instructor Assignment**: Clone creator automatically assigned as lead instructor
- **Draft Status**: Cloned courses default to draft status for editing

**API Integration Points**:
- Clone endpoint with granular options
- Version history retrieval
- Family relationship navigation
- Bulk operations on version families

### 2. Multi-Tier Content Access System

**Access Level Hierarchy**:
```
Guest (Level 0) → Registered (Level 1) → Premium (Level 2)
```

**Content Serving Logic Flow**:
1. **User Authentication Check**: Determine if user is authenticated
2. **Subscription Validation**: Check subscription tier and active status
3. **Access Level Mapping**: Map subscription to access level
4. **Content Selection**: Choose appropriate content tier
5. **Fallback Logic**: Provide lower-tier content if available
6. **Enrollment Override**: Enrolled users may access course-specific content

**Content Field Mapping**:
- **Full Content** (`content`): Premium users and enrolled students
- **Registered Content** (`registered_content`): Authenticated users
- **Guest Content** (`guest_content`): All users (preview)
- **Access Denied Message**: Custom messages for insufficient access

**Business Rules**:
- Free preview lessons bypass all restrictions
- Enrollment grants access regardless of subscription tier
- Premium content requires active premium subscription
- Fallback content must be manually created by instructors

### 3. Assessment System Architecture

**Question Type Specifications**:

**Multiple Choice**:
- Minimum 2 answers, maximum 10 answers per question
- Exactly one correct answer required
- Answer randomization support
- Partial credit not supported

**True/False**:
- Auto-generated two answers (True/False)
- Single correct answer selection
- Optional explanation for both answers

**Short Answer**:
- Text input validation (minimum/maximum length)
- Manual grading required
- Keyword-based auto-grading support
- Case sensitivity options

**Essay**:
- Rich text input support
- Manual grading only
- Rubric-based scoring
- File attachment support

**Fill in the Blank**:
- Multiple blank support per question
- Exact match or pattern matching
- Case sensitivity configuration
- Alternative answer support

**Matching**:
- Left and right column definitions
- One-to-one or one-to-many matching
- Drag-and-drop interface support
- Partial credit calculation

**Assessment Configuration Options**:
- **Time Limits**: Per-assessment time restrictions with auto-submission
- **Attempt Limits**: Maximum attempts per user with cooldown periods
- **Question Randomization**: Random question order for each attempt
- **Answer Randomization**: Random answer order for multiple choice
- **Immediate Feedback**: Show correct answers immediately or after completion
- **Partial Credit**: Award partial points for partially correct answers

**Scoring Algorithms**:
- **Point-based Scoring**: Total points earned / total points possible
- **Percentage Scoring**: Normalized to 0-100% scale
- **Weighted Scoring**: Different point values per question
- **Penalty Scoring**: Deduct points for incorrect answers

### 4. Progress Tracking & Analytics

**Progress Calculation Methods**:

**Lesson-Based Progress**:
- Completed lessons / Total lessons * 100
- Binary completion tracking (completed/not completed)
- Sequential progression requirements (optional)

**Time-Based Progress**:
- Time spent / Expected duration * 100
- Automatic time tracking via frontend integration
- Pause/resume capability
- Idle time detection and exclusion

**Assessment-Based Progress**:
- Passed assessments / Total assessments * 100
- Minimum score requirements
- Retake policies and progress impact

**Weighted Progress**:
- Different weights for lessons, assessments, and activities
- Configurable weighting per course
- Activity type consideration (reading vs. video vs. lab)

**Analytics Data Points**:
- **Engagement Metrics**: Login frequency, session duration, content interaction
- **Learning Patterns**: Peak activity times, content preferences, completion rates
- **Performance Metrics**: Assessment scores, improvement trends, struggle areas
- **Behavioral Data**: Navigation patterns, resource usage, help-seeking behavior

### 5. Certificate System

**Certificate Generation Workflow**:
1. **Completion Verification**: Verify 100% course completion
2. **Assessment Requirements**: Ensure all required assessments passed
3. **Template Selection**: Choose appropriate certificate template
4. **Data Population**: Fill certificate with student and course data
5. **Digital Signature**: Apply cryptographic signature for authenticity
6. **Storage**: Store certificate file and metadata
7. **Notification**: Send completion notification to student

**Certificate Components**:
- **Student Information**: Name, ID, completion date
- **Course Information**: Title, instructor, duration, level
- **Verification Elements**: Certificate number, QR code, verification URL
- **Design Elements**: Institution logo, instructor signature, template styling

**Verification System**:
- **Unique Certificate Numbers**: Format: CERT-{course_id}-{user_id}-{timestamp}
- **Cryptographic Hash**: SHA-256 hash for tamper detection
- **Public Verification**: Web-based verification portal
- **QR Code Integration**: Quick verification via mobile scanning
- **Blockchain Integration**: Optional blockchain recording for permanent verification

**Certificate Management**:
- **Revocation Capability**: Administrative certificate invalidation
- **Reissuance Process**: Lost certificate replacement
- **Bulk Operations**: Mass certificate generation and management
- **Template Versioning**: Multiple certificate designs and layouts

### 6. Real-Time Features & WebSocket Integration

**Real-Time Event Types**:

**Progress Updates**:
- Lesson completion events
- Assessment submission events
- Course progress milestones
- Time tracking updates

**Collaborative Features**:
- Instructor announcements
- Discussion forum updates
- Peer interaction notifications
- Group project updates

**System Notifications**:
- Course updates and changes
- Assignment deadlines
- Maintenance notifications
- Feature announcements

**WebSocket Channel Structure**:
```
/ws/course/{course_id}/user/{user_id}/
/ws/assessment/{assessment_id}/
/ws/notifications/{user_id}/
/ws/instructor/{instructor_id}/
```

**Message Format**:
```json
{
  "type": "progress_update",
  "timestamp": "2025-06-17T12:30:28Z",
  "data": {
    "lesson_id": 123,
    "progress_percentage": 75,
    "is_completed": false
  }
}
```

### 7. Search & Discovery System

**Search Capabilities**:

**Course Search**:
- Full-text search across title, description, and content
- Faceted search by category, level, price, rating
- Auto-suggest and type-ahead functionality
- Search result ranking by relevance and popularity

**Content Search**:
- Lesson content search within enrolled courses
- Resource search by type and content
- Assessment question search for instructors
- Tag-based content discovery

**Advanced Filtering**:
- Multiple filter combinations
- Price range filtering
- Duration-based filtering
- Instructor-based filtering
- Language and subtitle availability

**Search Analytics**:
- Popular search terms tracking
- Search result click-through rates
- No-results queries identification
- Search performance metrics

---

## Performance & Optimization

### Database Optimization
**Indexing Strategy (IMPLEMENTATION)**:

**Primary Indexes**:
- `Course.slug` - Unique index for fast course lookup
- `User.email` - Unique index for authentication
- `Enrollment.user_id, Enrollment.course_id` - Composite unique index
- `Progress.enrollment_id, Progress.lesson_id` - Composite unique index
- `AssessmentAttempt.user_id, AssessmentAttempt.assessment_id` - Composite index

**Search Indexes**:
- `Course.title` - Full-text search index with trigram support
- `Course.description` - Full-text search index
- `Lesson.content` - Full-text search index for content search
- `Category.name` - B-tree index for fast category filtering

**Temporal Indexes**:
- `Course.created_date` - For chronological sorting
- `Enrollment.last_accessed` - For recent activity queries
- `Progress.last_accessed` - For learning pattern analysis

**Query Optimization Patterns**:

**Select Related Usage**:
```python
# Course with category information
Course.objects.select_related('category')

# Enrollment with user and course details
Enrollment.objects.select_related('user', 'course__category')

# Progress with lesson and module information
Progress.objects.select_related('lesson__module__course')
```

**Prefetch Related Usage**:
```python
# Course with modules and lessons
Course.objects.prefetch_related('modules__lessons')

# Course with instructors
Course.objects.prefetch_related('courseinstructor_set__instructor')

# Assessment with questions and answers
Assessment.objects.prefetch_related('questions__answers')
```

**Database Connection Management**:
- Connection pooling configuration
- Read/write database splitting
- Query timeout settings
- Connection retry logic

### Caching Strategy
**Cache Layer Hierarchy**:

**Level 1: Application Cache (Redis)**:
- Session data storage
- User authentication tokens
- Temporary calculation results
- API rate limiting counters

**Level 2: Database Query Cache**:
- Frequently accessed course data
- Category listings
- User permission cache
- Analytics aggregations

**Level 3: CDN Cache**:
- Static media files
- Course thumbnails
- Video content
- Resource downloads

**Cache Key Patterns**:
```
course:{slug}:detail
course:{slug}:modules
user:{id}:enrollments
user:{id}:progress
category:list:active
analytics:{course_id}:summary
```

**Cache Invalidation Strategy**:
- Time-based expiration (TTL)
- Event-driven invalidation via signals
- Version-based cache keys
- Hierarchical cache clearing

**Cache Warming Procedures**:
- Popular course preloading
- User session preparation
- Analytics pre-calculation
- Search index preparation

### API Performance
**Pagination (CORRECTED)**:
- Default pagination for list endpoints
- Configurable page sizes using `?page_size` parameter
- Cursor pagination for large datasets

**Field Selection**:
- Minimal field sets for list views
- Full detail sets for detail views
- Custom serializers for specific use cases

**Request Optimization**:
- Bulk operations where applicable
- Batched updates for progress tracking
- Efficient file upload handling

### Frontend Integration Optimization
**Data Structure**:
- Nested data inclusion in single requests
- Computed fields for common calculations
- Efficient relationship handling

**Real-Time Features**:
- WebSocket integration points
- Polling optimization
- Event-driven updates

---

## Error Handling & Status Codes

### HTTP Status Code Usage
**200 OK**: Successful GET requests
**201 Created**: Successful POST requests (creation)
**204 No Content**: Successful DELETE requests
**400 Bad Request**: Validation errors, malformed requests
**401 Unauthorized**: Authentication required
**403 Forbidden**: Permission denied
**404 Not Found**: Resource not found
**429 Too Many Requests**: Rate limiting
**500 Internal Server Error**: Server-side errors

### Error Response Format
**Validation Errors**:
```json
{
  "field_name": ["Error message 1", "Error message 2"],
  "non_field_errors": ["General error message"]
}
```

**General Errors**:
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Common Error Scenarios
**Authentication Errors**:
- Token expired or invalid
- Missing authentication headers
- Account deactivated

**Permission Errors**:
- Insufficient role permissions
- Course access restrictions
- Subscription requirements

**Validation Errors**:
- Required field missing
- Format validation failures
- Business rule violations

**Resource Errors**:
- Course not found
- Lesson access restricted
- Assessment attempt limits exceeded

---

## Frontend Integration Guidelines

### 1. API Client Implementation

**Authentication Flow (CORRECTED)**:
1. User login with credentials
2. Receive Django Token (NOT JWT)
3. Include token in all authenticated requests using `Authorization: Token <token_value>`
4. Handle token invalidation/regeneration
5. Implement logout and token cleanup

**Error Handling Strategy**:
1. Implement comprehensive error type detection
2. Provide user-friendly error messages
3. Implement retry logic for network errors
4. Handle authentication errors with redirect
5. Log errors for debugging and monitoring

**Caching Strategy**:
1. Cache course listings and categories
2. Implement cache invalidation on updates
3. Use local storage for user preferences
4. Cache media files for offline access
5. Implement cache expiration policies

### 2. Real-Time Integration

**WebSocket Connection Management**:
1. Establish connections on page load
2. Handle connection drops and reconnection
3. Implement heartbeat mechanism
4. Route messages to appropriate handlers
5. Clean up connections on page unload

**State Management**:
1. Implement centralized state management
2. Handle real-time updates to local state
3. Resolve conflicts between local and server state
4. Implement optimistic updates
5. Provide offline capability

### 3. Progressive Web App (PWA) Considerations

**Offline Functionality**:
- Course content caching for offline viewing
- Progress synchronization when online
- Offline-first architecture implementation
- Service worker configuration

**Performance Optimization**:
- Lazy loading for course content
- Image optimization and lazy loading
- Code splitting for faster initial loads
- Bundle size optimization

### 4. State Management Patterns

**Global State Management**:
- User authentication state
- Course enrollment status
- Progress tracking data
- Notification management

**Local State Management**:
- Form input handling
- UI component state
- Temporary data storage
- Cache management

**State Synchronization**:
- Server state reconciliation
- Optimistic update handling
- Conflict resolution
- Offline state management

### 5. Performance Optimization Strategies

**Bundle Optimization**:
- Code splitting by route
- Lazy loading components
- Tree shaking implementation
- Asset optimization

**Network Optimization**:
- Request batching
- Response compression
- HTTP/2 utilization
- Service worker implementation

**Rendering Optimization**:
- Virtual scrolling for large lists
- Image lazy loading
- Component memoization
- Critical rendering path optimization

### 6. Error Boundary Implementation

**Error Classification**:
- Network errors
- Authentication errors
- Validation errors
- Application errors

**Recovery Strategies**:
- Automatic retry mechanisms
- Graceful degradation
- Fallback content display
- User notification systems

**Error Reporting**:
- Client-side error logging
- Error aggregation services
- Performance impact tracking
- User feedback collection

---

## Complete Feature Coverage Verification

### ✅ VERIFIED FEATURES FROM CODEBASE:

1. **Authentication System**: Django Token + Session Authentication (CORRECTED)
2. **Multi-Tier Content Access**: Guest/Registered/Premium levels with fallback content
3. **Course Versioning**: Parent-child relationships with version increments
4. **Assessment System**: Complete question/answer framework with multiple types
5. **Progress Tracking**: Real-time progress calculation with signal-driven updates
6. **Certificate Generation**: Automated certificate creation with verification
7. **File Upload System**: Configurable storage with metadata tracking
8. **Signal-Driven Updates**: Automatic analytics refresh via Django signals
9. **Permission System**: Role-based access control with custom permission classes
10. **Validation Framework**: Comprehensive field validation from validators.py
11. **API Pagination**: Page-based pagination with `page_size` parameter (CORRECTED)
12. **Search & Filtering**: Full-text search with multiple filter parameters
13. **Course Cloning**: Complete course duplication with selective cloning options
14. **Review System**: Rating and feedback management with moderation
15. **Analytics**: Real-time course and user statistics with cached aggregations
16. **Abstract Mixins**: DRY architecture with reusable model mixins
17. **Multi-tier Lesson Content**: Guest/registered/premium content serving
18. **Assessment Tracking**: Complete attempt and answer tracking system
19. **Resource Management**: File upload with metadata and premium access control
20. **Course Management**: Draft/publish workflow with completion tracking


This comprehensive documentation now accurately reflects the actual implementation in the codebase and provides complete technical specifications for frontend developers to build robust, production-ready applications that integrate seamlessly with the course management system backend.
