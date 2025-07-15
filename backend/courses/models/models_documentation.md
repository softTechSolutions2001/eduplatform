# Course Analytics Models Documentation

## Overview

The `analytics.py` module provides Django models for a comprehensive course management system with assessment capabilities, user tracking, and analytics. This module handles course assessments, user interactions, performance tracking, and statistical analysis.

**Module Path:** `backend/courses/models/analytics.py`

---

## Core Dependencies

```python
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, DatabaseError, OperationalError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.apps import apps
```

**Custom Dependencies:**
- `TimeStampedMixin`, `OrderedMixin` from `mixins.py`
- Constants from `constants.py`
- Validators from `validators.py`
- Utility functions from `utils.model_helpers`

---

## Assessment Models

### Assessment

Core assessment configuration model with comprehensive settings for course evaluations.

```python
class Assessment(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `lesson` | OneToOneField | Associated lesson (CASCADE delete) |
| `title` | CharField(255) | Assessment title with minimum 2 characters |
| `description` | TextField | Optional assessment instructions |
| `passing_score` | PositiveIntegerField | Required percentage to pass (0-100) |
| `max_attempts` | PositiveIntegerField | Maximum allowed attempts (min: 1) |
| `time_limit` | PositiveIntegerField | Time limit in minutes (0 = unlimited) |
| `time_limit_minutes` | PositiveIntegerField | Backward compatibility alias |
| `randomize_questions` | BooleanField | Randomize question order per attempt |
| `show_correct_answers` | BooleanField | Display correct answers after completion |
| `show_results` | BooleanField | Show immediate results after completion |

**Key Methods:**

- `save()`: Synchronizes time_limit fields, uses atomic transactions
- `get_questions()`: Returns optimized queryset with select_related/prefetch_related
- `get_max_score()`: Calculates total points using database aggregation
- `clean()`: Validates time_limit and passing_score ranges

**Database Indexes:**
- `lesson` (implicit OneToOne)
- `passing_score`
- `show_results, show_correct_answers` (composite)

### Question

Individual assessment questions with automatic ordering and type validation.

```python
class Question(TimeStampedMixin, OrderedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `assessment` | ForeignKey | Parent assessment (CASCADE delete) |
| `question_text` | TextField | Primary question content |
| `text` | TextField | Backward compatibility alias |
| `question_type` | CharField(20) | Question type (see choices below) |
| `points` | PositiveIntegerField | Points for correct answer (min: 1) |
| `order` | PositiveIntegerField | Display order within assessment |
| `explanation` | TextField | Answer explanation |
| `feedback` | TextField | Backward compatibility alias |

**Question Types:**
- `multiple_choice`: Multiple Choice
- `true_false`: True/False
- `short_answer`: Short Answer
- `essay`: Essay
- `matching`: Matching
- `fill_blank`: Fill in the Blank

**Key Methods:**

- `save()`: Synchronizes text fields, handles automatic ordering with atomic transactions
- `get_next_order()`: Thread-safe order calculation with select_for_update
- `get_answers()`: Returns optimized answer queryset
- `text_property`: Property returning question_text or text
- `feedback_property`: Property returning explanation or feedback

**Database Indexes:**
- `assessment, order` (composite)
- `question_type`

**Constraints:**
- `unique_question_order`: Unique order per assessment

### Answer

Answer choices for questions with ordering and correctness tracking.

```python
class Answer(TimeStampedMixin, OrderedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `question` | ForeignKey | Parent question (CASCADE delete) |
| `answer_text` | CharField(500) | Primary answer content |
| `text` | TextField | Backward compatibility alias |
| `is_correct` | BooleanField | Correct answer flag |
| `explanation` | TextField | Explanation for answer choice |
| `order` | PositiveIntegerField | Display order within question |

**Key Methods:**

- `save()`: Synchronizes text fields, handles atomic ordering
- `get_next_order()`: Thread-safe order calculation for question scope
- `text_property`: Property always returning answer text

**Database Indexes:**
- `question, order` (composite)
- `is_correct`

**Constraints:**
- `unique_answer_order`: Unique order per question

---

## Attempt and Response Models

### AssessmentAttempt

Comprehensive tracking of user assessment attempts with timing and scoring.

```python
class AssessmentAttempt(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | User taking assessment (CASCADE delete) |
| `assessment` | ForeignKey | Assessment being attempted (CASCADE delete) |
| `start_time` | DateTimeField | Attempt start timestamp (auto_now_add) |
| `end_time` | DateTimeField | Attempt completion timestamp |
| `time_taken_seconds` | PositiveIntegerField | Duration in seconds |
| `score` | PositiveIntegerField | Raw score achieved |
| `max_score` | PositiveIntegerField | Maximum possible score |
| `is_completed` | BooleanField | Completion status |
| `is_passed` | BooleanField | Pass/fail status |
| `passed` | BooleanField | Backward compatibility alias |
| `attempt_number` | PositiveIntegerField | Sequential attempt number |
| `ip_address` | GenericIPAddressField | User's IP address |
| `user_agent` | TextField | Browser user agent |

**Key Methods:**

- `save()`: Atomic transaction handling, attempt numbering, max_attempts validation, pass/fail calculation
- `score_percentage`: Cached property calculating percentage with fallbacks
- `time_taken`: Property calculating duration from timestamps or stored value

**Database Indexes:**
- `user, assessment` (composite)
- `assessment, -created_date` (composite)
- `is_completed, is_passed` (composite)

### AttemptAnswer

Individual question responses within assessment attempts.

```python
class AttemptAnswer(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `attempt` | ForeignKey | Parent assessment attempt (CASCADE delete) |
| `question` | ForeignKey | Question being answered (CASCADE delete) |
| `selected_answer` | ForeignKey | Selected answer choice (for MC questions) |
| `text_answer` | TextField | Text response (for open-ended questions) |
| `is_correct` | BooleanField | Correctness status |
| `points_earned` | PositiveIntegerField | Points awarded |
| `feedback` | TextField | Instructor feedback |
| `answered_at` | DateTimeField | Response timestamp (auto_now_add) |

**Properties:**
- `answer`: Alias for selected_answer
- `text_response`: Alias for text_answer

**Key Methods:**

- `save()`: Automatic correctness checking, points calculation with optimized queries
- `clean()`: Validates required fields based on question type

**Database Indexes:**
- `attempt, question` (composite)
- `is_correct`

**Constraints:**
- `unique_attempt_answer`: Unique answer per attempt/question

---

## User Interaction Models

### Review

Course reviews with rating system and moderation capabilities.

```python
class Review(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Review author (CASCADE delete) |
| `course` | ForeignKey | Course being reviewed (CASCADE delete) |
| `rating` | PositiveSmallIntegerField | Star rating (1-5) |
| `title` | CharField(255) | Review title |
| `content` | TextField | Review content (min: 10 characters) |
| `helpful_count` | PositiveIntegerField | Helpful votes count |
| `is_verified_purchase` | BooleanField | Enrollment verification status |
| `is_approved` | BooleanField | Moderation approval status |
| `is_featured` | BooleanField | Featured review flag |
| `moderation_notes` | TextField | Internal moderation notes |

**Key Methods:**

- `save()`: Enrollment verification, selective analytics updates, atomic transactions

**Database Indexes:**
- `course, -created_date` (composite)
- `user, -created_date` (composite)
- `is_approved, is_featured` (composite)
- `rating`

**Constraints:**
- `unique_user_course_review`: One review per user per course

### Note

User notes on lessons with organization and privacy features.

```python
class Note(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Note author (CASCADE delete) |
| `lesson` | ForeignKey | Associated lesson (CASCADE delete) |
| `content` | TextField | Note content (min: 1 character) |
| `timestamp_seconds` | PositiveIntegerField | Video timestamp for media notes |
| `is_private` | BooleanField | Privacy setting |
| `tags` | JSONField | Organizational tags (max: 10 items) |

**Database Indexes:**
- `user, lesson` (composite)
- `lesson, is_private` (composite)

---

## Analytics Models

### UserActivity

Comprehensive user activity tracking across the platform.

```python
class UserActivity(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | User performing activity (CASCADE delete) |
| `activity_type` | CharField(255) | Type of activity performed |
| `course` | ForeignKey | Related course (optional) |
| `lesson` | ForeignKey | Related lesson (optional) |
| `resource` | ForeignKey | Related resource (optional) |
| `assessment` | ForeignKey | Related assessment (optional) |
| `data` | JSONField | Additional activity data |

**Activity Types:**
- `view_course`: Course page view
- `start_lesson`: Lesson initiation
- `complete_lesson`: Lesson completion
- `download_resource`: Resource download
- `take_quiz`: Assessment interaction
- `post_comment`: Comment creation
- `give_review`: Review submission

**Database Indexes:**
- `user, -created_date` (composite)
- `course, -created_date` (composite)
- `activity_type`

### CourseStats

Aggregate statistics and analytics for courses.

```python
class CourseStats(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `course` | OneToOneField | Associated course |
| `total_students` | PositiveIntegerField | Total enrolled students |
| `active_students` | PositiveIntegerField | Currently active students |
| `completion_count` | PositiveIntegerField | Course completions |
| `average_completion_days` | PositiveIntegerField | Average completion time |
| `engagement_score` | DecimalField(5,2) | Calculated engagement metric |
| `assessment_stats` | JSONField | Assessment performance data |
| `revenue_data` | JSONField | Financial metrics |

**Database Indexes:**
- `course` (implicit OneToOne)

### UserStats

Individual user learning analytics and progress tracking.

```python
class UserStats(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Associated user |
| `courses_enrolled` | PositiveIntegerField | Total course enrollments |
| `courses_completed` | PositiveIntegerField | Completed courses |
| `total_time_spent_seconds` | PositiveBigIntegerField | Total learning time |
| `assessment_avg_score` | DecimalField(5,2) | Average assessment score |
| `last_activity` | DateTimeField | Last platform activity |
| `activity_streak` | PositiveIntegerField | Consecutive active days |
| `learning_habits` | JSONField | Behavioral analysis data |

**Database Indexes:**
- `user` (implicit OneToOne)
- `activity_streak, last_activity` (composite)

### Notification

Course-related notifications and messaging system.

```python
class Notification(TimeStampedMixin)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Notification recipient (CASCADE delete) |
| `title` | CharField(255) | Notification title |
| `message` | TextField | Notification content |
| `notification_type` | CharField(255) | Notification category |
| `course` | ForeignKey | Related course (optional) |
| `is_read` | BooleanField | Read status |
| `read_date` | DateTimeField | Read timestamp |
| `action_url` | URLField | Action link |

**Notification Types:**
- `course_update`: Course content updates
- `reminder`: Learning reminders
- `achievement`: Milestone achievements
- `announcement`: General announcements
- `feedback`: Feedback requests
- `custom`: Custom notifications

**Database Indexes:**
- `user, -created_date` (composite)
- `is_read`
- `notification_type`

---

## Technical Implementation

### Transaction Management

All models implement atomic transaction handling:

```python
def save(self, *args, **kwargs):
    try:
        with transaction.atomic():
            # Model-specific logic
            super().save(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {self.__class__.__name__}.save(): {e}")
        raise
```

### Query Optimization

**N+1 Query Prevention:**
- `select_related()` for forward foreign keys
- `prefetch_related()` for reverse foreign keys and many-to-many
- Database-level aggregation for calculations

**Example:**
```python
def get_questions(self):
    return self.questions.select_related('assessment').prefetch_related('answers').order_by('order')
```

### Caching Strategy

**Score Percentage Caching:**
```python
@property
def score_percentage(self):
    if hasattr(self, '_score_percentage_cache'):
        return self._score_percentage_cache

    # Calculate and cache result
    result = self._calculate_percentage()
    self._score_percentage_cache = result
    return result
```

### Concurrency Control

**Race Condition Prevention:**
```python
def get_next_order(self):
    with transaction.atomic():
        last_order = Model.objects.select_for_update().filter(
            parent=self.parent
        ).aggregate(max_order=models.Max('order'))['max_order'] or 0
        return last_order + 1
```

### Error Handling

**Comprehensive Exception Handling:**
- `DatabaseError`: Database connectivity issues
- `OperationalError`: Database operation failures
- `ValidationError`: Data validation failures
- `AttributeError`: Missing attribute access

**Logging Strategy:**
- Error level: Critical failures
- Warning level: Recoverable issues
- Info level: Important state changes

### Field Synchronization

**Backward Compatibility:**
Many models maintain dual fields for API compatibility:

```python
def save(self, *args, **kwargs):
    # Synchronize fields
    if self.primary_field and not self.legacy_field:
        self.legacy_field = self.primary_field
    elif self.legacy_field and not self.primary_field:
        self.primary_field = self.legacy_field
```

### Validation Framework

**Built-in Validators:**
- `MinValueValidator`: Minimum value constraints
- `MaxValueValidator`: Maximum value constraints
- `validate_percentage`: Custom percentage validation (0-100)

**Model-level Validation:**
```python
def clean(self):
    super().clean()
    if self.field < 0:
        raise ValidationError("Field must be non-negative")
```

---

## Database Schema

### Index Strategy

**Composite Indexes:** Optimized for common query patterns
- Foreign key + ordering: `(assessment, order)`
- Foreign key + datetime: `(user, -created_date)`
- Status combinations: `(is_completed, is_passed)`

**Single Column Indexes:** For frequently filtered fields
- Status fields: `is_correct`, `is_read`
- Categorical fields: `question_type`, `activity_type`

### Constraints

**Unique Constraints:**
- Prevent duplicate data: `(user, course)` for reviews
- Maintain ordering: `(assessment, order)` for questions
- Ensure data integrity: `(attempt, question)` for answers

### JSON Field Usage

**Flexible Data Storage:**
- `tags`: Array of strings with validation
- `data`: Activity-specific information
- `assessment_stats`: Performance metrics
- `learning_habits`: User behavior analysis

---

## Usage Patterns

### Assessment Creation

```python
# Create assessment
assessment = Assessment.objects.create(
    lesson=lesson,
    title="Final Exam",
    passing_score=80,
    max_attempts=2,
    time_limit=60
)

# Add questions with automatic ordering
question = Question.objects.create(
    assessment=assessment,
    question_text="What is the capital of France?",
    question_type="multiple_choice",
    points=5
)

# Add answers with automatic ordering
Answer.objects.bulk_create([
    Answer(question=question, answer_text="Paris", is_correct=True),
    Answer(question=question, answer_text="London", is_correct=False),
    Answer(question=question, answer_text="Berlin", is_correct=False),
])
```

### Attempt Processing

```python
# Start attempt
attempt = AssessmentAttempt.objects.create(
    user=user,
    assessment=assessment
)

# Process answers
for question_id, answer_data in submitted_answers.items():
    AttemptAnswer.objects.create(
        attempt=attempt,
        question_id=question_id,
        selected_answer_id=answer_data.get('selected_answer'),
        text_answer=answer_data.get('text_answer', '')
    )

# Complete attempt
attempt.is_completed = True
attempt.end_time = timezone.now()
attempt.save()  # Automatic score calculation and pass/fail determination
```

### Analytics Queries

```python
# Course performance
stats = CourseStats.objects.select_related('course').get(course=course)
completion_rate = (stats.completion_count / stats.total_students) * 100

# User progress
user_stats = UserStats.objects.get(user=user)
learning_streak = user_stats.activity_streak

# Activity tracking
UserActivity.objects.create(
    user=user,
    activity_type='complete_lesson',
    course=course,
    lesson=lesson,
    data={'time_spent': 1800, 'score': 85}
)
```

---

## Performance Considerations

### Database Queries
- Use `select_related()` for foreign key access
- Use `prefetch_related()` for reverse relationships
- Implement database-level aggregations
- Cache computed values

### Memory Management
- Lazy loading of large text fields
- Selective field updates with `update_fields`
- JSON field optimization for variable data

### Scalability
- Proper indexing for query optimization
- Transaction boundaries for data consistency
- Concurrent access handling with locking
- Archive strategies for historical data

---

## Security Features

### Data Validation
- Input length validation
- Numeric range validation
- Custom business logic validation

### Access Control
- User-based data isolation
- Privacy controls for sensitive data
- Moderation capabilities for public content

### Audit Trail
- Comprehensive activity logging
- Timestamp tracking on all models
- IP address and user agent tracking

### Concurrent Safety
- Atomic transactions for critical operations
- Row-level locking for race condition prevention
- Unique constraints for data integrity
