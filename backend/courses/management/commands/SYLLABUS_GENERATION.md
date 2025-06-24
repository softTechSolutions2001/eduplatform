"Please review this comprehensive reference document and confirm you understand the educational platform structure, database schema, and course generation requirements before we continue with course expansion with much detailed explanations.

---

## **🏗️ PROJECT OVERVIEW**

### **Platform Type:**
Enterprise-grade educational platform for software testing courses with Django/PostgreSQL backend

### **Current Project Status:**
- **Course 1**: "Software Testing with AI-Driven Test Automation" (16 weeks, Foundation to Intermediate)
- **Course 2**: "Advanced Software Testing with AI-Driven Test Automation" (Future development)
- **Access Model**: 75% Free (Guest), 25% Premium (Registered)
- **Target**: Job placement guarantee for $45K-$75K QA positions

### **Technology Stack:**
- **Backend**: Django 5.2 + PostgreSQL
- **Authentication**: JWT + OAuth integration
- **File Storage**: Advanced media handling with file tracking
- **Security**: Production-grade security settings
- **Deployment**: Production-ready configuration

---

## **📊 COMPLETE DATABASE SCHEMA v2.7.1**

### **File Reference**: `backend/courses/models.py` (Version 2.7.1)

### **Key Architecture Features:**
- **DRY Mixins**: Abstract base classes for common functionality
- **Enhanced Analytics**: Built-in course and user analytics
- **Tiered Content Access**: Guest, Registered, Premium access levels
- **Advanced Ordering**: Automatic ordering system for hierarchical content
- **File Tracking**: Comprehensive file management and metadata
- **Validation Framework**: Extensive validation and error handling

---

## **🎯 CORE MODEL STRUCTURE**

### **1. Category Model**
```python
Category (TimeStampedMixin, SlugMixin, StateMixin):
├── name: CharField(100) - unique, min 2 chars
├── description: TextField - optional category description
├── icon: CharField(50) - CSS icon class
├── sort_order: PositiveIntegerField - display order
├── slug: Auto-generated from name
├── is_active: BooleanField - state management
├── created_date/updated_date: Auto timestamps
└── Methods: get_course_count()
```

### **2. Course Model (Primary)**
```python
Course (TimeStampedMixin, SlugMixin, DurationMixin, PublishableMixin, AnalyticsMixin):
├── Basic Information:
│   ├── title: CharField(160) - min 3 chars
│   ├── subtitle: CharField(255) - optional
│   ├── description: TextField - min 50 chars
│   └── category: ForeignKey(Category)
│
├── Pricing & Media:
│   ├── price: DecimalField - default 0.00
│   ├── discount_price: DecimalField - optional
│   ├── discount_ends: DateTimeField - optional
│   └── thumbnail: ImageField - course image
│
├── Course Metadata:
│   ├── level: CharField(20) - LEVEL_CHOICES
│   ├── has_certificate: BooleanField
│   ├── is_featured: BooleanField
│   ├── requirements: JSONField - list of prerequisites
│   ├── skills: JSONField - list of skills learned
│   ├── learning_objectives: JSONField - learning goals
│   └── target_audience: TextField
│
├── Management & Versioning:
│   ├── creation_method: CharField(20) - CREATION_METHODS
│   ├── completion_status: CharField(20) - COMPLETION_STATUSES
│   ├── completion_percentage: IntegerField(0-100)
│   ├── version: FloatField - version number
│   ├── is_draft: BooleanField
│   ├── parent_version: ForeignKey(self) - for cloning
│   └── is_published: BooleanField
│
├── Analytics (Computed Fields):
│   ├── enrolled_students_count: PositiveIntegerField
│   ├── avg_rating: FloatField
│   ├── total_reviews: PositiveIntegerField
│   └── last_enrollment_date: DateTimeField
│
└── Methods:
    ├── clone_version() - comprehensive course cloning
    ├── update_analytics() - refresh analytics data
    └── clean() - enhanced validation
```

### **3. CourseInstructor Model**
```python
CourseInstructor (TimeStampedMixin, StateMixin):
├── course: ForeignKey(Course)
├── instructor: ForeignKey(User)
├── title: CharField(100) - instructor role
├── bio: TextField - instructor bio for course
├── is_lead: BooleanField - lead instructor flag
└── Validation: Instructor privileges required
```

### **4. Module Model**
```python
Module (TimeStampedMixin, OrderedMixin, DurationMixin, PublishableMixin):
├── course: ForeignKey(Course)
├── title: CharField(255) - min 2 chars
├── description: TextField - optional
├── order: Automatic ordering within course
├── duration_minutes: PositiveIntegerField
└── is_published: BooleanField
```

### **5. Lesson Model (Enhanced)**
```python
Lesson (TimeStampedMixin, OrderedMixin, DurationMixin):
├── module: ForeignKey(Module)
├── title: CharField(255) - min 2 chars
├── Content (Tiered Access):
│   ├── content: TextField - full content (authorized users)
│   ├── guest_content: TextField - preview for guests
│   └── registered_content: TextField - limited for registered
│
├── Access Control:
│   ├── access_level: CharField(20) - ACCESS_LEVEL_CHOICES
│   ├── type: CharField(20) - LESSON_TYPE_CHOICES
│   ├── is_free_preview: BooleanField
│   ├── has_assessment: BooleanField
│   └── has_lab: BooleanField
│
├── Media:
│   ├── video_url: URLField - with validation
│   ├── transcript: TextField - video transcript
│   └── order: Automatic ordering within module
```

**ACCESS_LEVEL_CHOICES:**
- `guest`: Free access for unregistered users
- `registered`: Requires user registration
- `premium`: Premium subscription required

**LESSON_TYPE_CHOICES:**
- `video`, `text`, `quiz`, `lab`, `project`, `interactive`, `document`, `live`

### **6. Resource Model (Enhanced)**
```python
Resource (TimeStampedMixin, OrderedMixin, DurationMixin, FileTrackingMixin):
├── lesson: ForeignKey(Lesson)
├── title: CharField(255) - min 2 chars
├── type: CharField(20) - RESOURCE_TYPE_CHOICES
├── description: TextField - optional
├── File Management:
│   ├── file: FileField - uploaded resource
│   ├── url: URLField - external resource
│   ├── file_size: Auto-populated from FileTrackingMixin
│   └── download_count: Tracking from FileTrackingMixin
├── premium: BooleanField - premium resource flag
└── order: Automatic ordering within lesson
```

**RESOURCE_TYPE_CHOICES:**
- `pdf`, `video`, `audio`, `image`, `zip`, `link`, `tool`, `dataset`, `template`, `interactive`

### **7. Assessment System**
```python
Assessment (TimeStampedMixin):
├── lesson: OneToOneField(Lesson)
├── title: CharField(255) - min 2 chars
├── description: TextField - optional instructions
├── Configuration:
│   ├── time_limit: PositiveIntegerField - minutes (0 = no limit)
│   ├── passing_score: PositiveIntegerField(0-100)
│   ├── max_attempts: PositiveIntegerField - default 3
│   ├── randomize_questions: BooleanField
│   └── show_results: BooleanField

Question (TimeStampedMixin, OrderedMixin):
├── assessment: ForeignKey(Assessment)
├── question_text: TextField - min 5 chars
├── question_type: CharField(20) - QUESTION_TYPE_CHOICES
├── points: PositiveIntegerField - default 1
├── explanation: TextField - optional explanation
└── order: Automatic ordering within assessment

Answer (TimeStampedMixin, OrderedMixin):
├── question: ForeignKey(Question)
├── answer_text: CharField(500) - min 1 char
├── is_correct: BooleanField
├── explanation: TextField - optional explanation
└── order: Automatic ordering within question
```

**QUESTION_TYPE_CHOICES:**
- `multiple_choice`, `true_false`, `short_answer`, `essay`, `code`, `matching`

### **8. Enrollment & Progress System**
```python
Enrollment (TimeStampedMixin):
├── user: ForeignKey(User)
├── course: ForeignKey(Course)
├── status: CharField(20) - STATUS_CHOICES
├── Progress Tracking:
│   ├── progress_percentage: PositiveIntegerField(0-100)
│   ├── completion_date: DateTimeField - optional
│   ├── last_accessed: Auto-updated timestamp
│   ├── total_time_spent: PositiveIntegerField - seconds
│   └── last_lesson_accessed: ForeignKey(Lesson) - optional
└── Methods: update_progress() - auto-calculate progress

Progress (TimeStampedMixin):
├── enrollment: ForeignKey(Enrollment)
├── lesson: ForeignKey(Lesson)
├── is_completed: BooleanField
├── completed_date: DateTimeField - auto-set on completion
├── time_spent: PositiveIntegerField - seconds
├── progress_percentage: PositiveIntegerField(0-100)
├── notes: TextField - student notes
└── last_accessed: Auto-updated timestamp
```

### **9. Assessment Attempts**
```python
AssessmentAttempt (TimeStampedMixin):
├── user: ForeignKey(User)
├── assessment: ForeignKey(Assessment)
├── Timing:
│   ├── start_time: Auto-generated
│   ├── end_time: DateTimeField - optional
│   └── attempt_number: Auto-incremented
├── Results:
│   ├── score: PositiveIntegerField - raw score
│   ├── passed: BooleanField - auto-calculated
│   └── Properties: score_percentage, time_taken
├── Tracking:
│   ├── ip_address: GenericIPAddressField
│   └── user_agent: TextField

AttemptAnswer (No mixins):
├── attempt: ForeignKey(AssessmentAttempt)
├── question: ForeignKey(Question)
├── selected_answer: ForeignKey(Answer) - for multiple choice
├── text_answer: TextField - for open-ended
├── is_correct: BooleanField - auto-calculated
├── points_earned: PositiveIntegerField - auto-calculated
├── feedback: TextField - instructor feedback
└── answered_at: Auto-generated timestamp
```

### **10. Reviews & Analytics**
```python
Review (TimeStampedMixin):
├── user: ForeignKey(User)
├── course: ForeignKey(Course)
├── rating: PositiveSmallIntegerField(1-5)
├── title: CharField(255) - optional
├── content: TextField - min 10 chars
├── helpful_count: PositiveIntegerField - user votes
├── Moderation:
│   ├── is_verified_purchase: BooleanField - auto-set
│   ├── is_approved: BooleanField - default True
│   └── moderation_notes: TextField - internal notes

Note (TimeStampedMixin):
├── user: ForeignKey(User)
├── lesson: ForeignKey(Lesson)
├── content: TextField - min 1 char
├── is_private: BooleanField - default True
└── tags: JSONField - organization tags

Certificate (TimeStampedMixin):
├── enrollment: OneToOneField(Enrollment)
├── certificate_number: CharField(50) - unique, auto-generated
├── Verification:
│   ├── is_valid: BooleanField - default True
│   ├── verification_hash: CharField(64) - SHA-256, auto-generated
│   ├── revocation_date: DateTimeField - optional
│   └── revocation_reason: TextField - optional
├── template_version: CharField(10) - default "1.0"
└── Methods: revoke() - revoke certificate
```

---

## **🎯 COURSE GENERATION REQUIREMENTS**

### **Course 1 Specifications:**
```python
Course Details:
├── Title: "Software Testing with AI-Driven Test Automation"
├── Subtitle: "From Zero to Industry-Ready QA Professional in 16 Weeks"
├── Level: "beginner_to_intermediate"
├── Price: 0.00 (FREE)
├── Duration: 7,200 minutes (120 hours)
├── Modules: 16 modules (1 per week)
├── Lessons: 128+ lessons (8+ per module)
├── Access Model: 75% guest, 25% registered
├── Target Jobs: $45K-$75K QA positions
└── Certificate: Professional certification included
```

### **Content Access Distribution Strategy:**
```python
Access Level Distribution:
├── 75% GUEST ACCESS (guest):
│   ├── Core learning content and concepts
│   ├── Basic resources (PDFs, guides, videos)
│   ├── Fundamental practical exercises
│   ├── Assessment questions and explanations
│   └── Career guidance and job preparation
│
└── 25% REGISTERED ACCESS (registered):
    ├── Advanced hands-on lab environments
    ├── Premium tools and software access
    ├── Interactive coding environments
    ├── Advanced project templates
    ├── Mentorship and community access
    └── Career placement assistance
```

### **Learning Progression (16 Modules):**
```python
Phase 1 - Foundation (Weeks 1-4):
├── Module 1: Introduction to Testing Universe (guest: 80%, registered: 20%)
├── Module 2: Manual Testing Deep Dive (guest: 75%, registered: 25%)
├── Module 3: Test Management and Tools (guest: 70%, registered: 30%)
└── Module 4: Programming Fundamentals for Testers (guest: 75%, registered: 25%)

Phase 2 - Practical Skills (Weeks 5-8):
├── Module 5: API Testing Mastery (guest: 75%, registered: 25%)
├── Module 6: Database Testing Essentials (guest: 70%, registered: 30%)
├── Module 7: Web UI Testing Foundations (guest: 75%, registered: 25%)
└── Module 8: Introduction to Test Automation (guest: 70%, registered: 30%)

Phase 3 - Automation & AI (Weeks 9-12):
├── Module 9: AI-Enhanced Testing Introduction (guest: 75%, registered: 25%)
├── Module 10: Advanced Selenium and Framework Development (guest: 70%, registered: 30%)
├── Module 11: Performance Testing Fundamentals (guest: 75%, registered: 25%)
└── Module 12: CI/CD and DevOps Testing (guest: 70%, registered: 30%)

Phase 4 - Industry Readiness (Weeks 13-16):
├── Module 13: Security Testing Basics (guest: 75%, registered: 25%)
├── Module 14: Mobile Testing Automation (guest: 70%, registered: 30%)
├── Module 15: Industry Best Practices and Standards (guest: 80%, registered: 20%)
└── Module 16: Capstone Project and Career Preparation (guest: 75%, registered: 25%)
```

---

## **📝 CONTENT CREATION STANDARDS v2.0**

### **Module Structure Requirements:**
```python
Each Module Must Include:
├── Module Header:
│   ├── Philosophy with memorable analogy
│   ├── Duration in minutes (total module time)
│   ├── Learning objectives (4-5 specific, measurable goals)
│   └── Prerequisites from previous modules
│
├── 8-10 Detailed Lessons:
│   ├── Progressive difficulty (45-90 minutes each)
│   ├── Proper access level distribution (75% guest, 25% registered)
│   ├── Mix of content types (video, lab, interactive, project)
│   ├── Real-world industry examples and case studies
│   └── Job-relevant skill development focus
│
├── Hands-on Components (60% practical):
│   ├── Step-by-step lab exercises
│   ├── Real-world project assignments
│   ├── Interactive coding environments (registered)
│   └── Professional tool usage
│
├── Assessment System:
│   ├── Knowledge check quizzes (guest access)
│   ├── Practical assessments (registered access)
│   ├── Project-based evaluations
│   └── Industry scenario questions
│
└── Supporting Resources:
    ├── 4-6 resources per lesson
    ├── Professional documentation and guides
    ├── Industry-standard templates and tools
    └── Career development materials
```

### **Lesson Content Standards:**
```python
Each Lesson Must Include:
├── Lesson Header:
│   ├── Clear learning objectives (3-4 specific goals)
│   ├── Prerequisites (what students should know)
│   ├── Duration and lesson type
│   └── Access level assignment (guest/registered)
│
├── Content Structure:
│   ├── Simple analogy for complex concepts
│   ├── Step-by-step explanations with examples
│   ├── Industry-relevant scenarios and case studies
│   ├── Common mistakes and troubleshooting tips
│   └── Best practices and professional standards
│
├── Practical Components:
│   ├── Hands-on exercises with clear instructions
│   ├── Real-world problem-solving scenarios
│   ├── Tool usage and configuration steps
│   └── Validation criteria for success
│
├── Assessment Questions:
│   ├── 5-10 questions testing comprehension
│   ├── Multiple choice, true/false, and scenario-based
│   ├── Detailed explanations for each answer
│   └── Reference to lesson content for review
│
└── Supporting Materials:
    ├── Professional resource files
    ├── Templates and code examples
    ├── Additional reading materials
    └── Career skill development notes
```

### **Resource Requirements:**
```python
Resource Distribution Per Lesson:
├── FREE Resources (guest access - 75%):
│   ├── PDF guides and documentation
│   ├── Video tutorials and explanations
│   ├── Basic templates and examples
│   ├── Industry articles and case studies
│   └── Career guidance materials
│
└── REGISTERED Resources (registered access - 25%):
    ├── Interactive tools and environments
    ├── Advanced software and platform access
    ├── Premium templates and frameworks
    ├── Hands-on lab environments
    └── Professional development tools

Resource Specifications:
├── Realistic file sizes and descriptions
├── Professional naming conventions
├── Proper resource type categorization
├── Download tracking and analytics
├── Access level enforcement
└── Version control and updates
```

---

## **🔧 TECHNICAL IMPLEMENTATION REQUIREMENTS v2.0**

### **Django Management Command Structure:**
```python
# File Path: backend/courses/management/commands/populate_module_[X].py
# Command Name: populate_module_[X]

from django.core.management.base import BaseCommand
from courses.models import *
from django.contrib.auth import get_user_model
import json

class Command(BaseCommand):
    help = 'Populate Module [X]: [Title]'

    def handle(self, *args, **options):
        try:
            # 1. Create/Get Course and Category
            category = self.get_or_create_category()
            course = self.get_or_create_course(category)

            # 2. Create Module with proper validation
            module = self.create_module(course, module_data)

            # 3. Create Lessons with tiered content
            for lesson_data in lessons:
                lesson = self.create_lesson(module, lesson_data)

                # 4. Create Resources with proper access levels
                self.create_resources(lesson, lesson_data['resources'])

                # 5. Create Assessments if applicable
                if lesson_data.get('has_assessment'):
                    self.create_assessment(lesson, lesson_data['assessment'])

            # 6. Validate and report
            self.validate_module(module)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Module {X}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
```

### **Database Population Best Practices:**
```python
Implementation Requirements:
├── Django ORM Only: No raw SQL queries
├── Proper Relationships: Use foreign key references correctly
├── Error Handling: Comprehensive try-catch blocks with rollback
├── Data Validation: Use model clean() methods and validators
├── Incremental Updates: Support for updating existing content
├── Performance: Use bulk operations where appropriate
├── Logging: Detailed execution logs for debugging
├── Atomic Transactions: Ensure data consistency
├── File Management: Proper handling of resource files
└── Access Control: Enforce 75%/25% distribution
```

### **File Management System:**
```python
Resource File Organization:
└── media/
    ├── course_thumbnails/
    ├── lesson_resources/
    │   ├── module_01/
    │   │   ├── lesson_01/
    │   │   │   ├── fundamentals_guide.pdf
    │   │   │   ├── testing_infographic.png
    │   │   │   └── practice_quiz.html
    │   │   ├── lesson_02/
    │   │   └── ...
    │   ├── module_02/
    │   └── ...
    └── certificates/

File Handling Requirements:
├── Organized directory structure by module/lesson
├── Realistic file sizes and metadata
├── Proper MIME type detection
├── Access level enforcement at file level
├── Download tracking and analytics
└── Version control for updated resources
```

---

## **🎯 SUCCESS CRITERIA & VALIDATION**

### **Course Quality Standards:**
```python
Quality Checklist:
├── Job Placement Ready:
│   ├── Skills directly applicable to $45K-$75K positions
│   ├── Industry-standard tools and practices
│   ├── Professional project portfolio
│   └── Interview preparation materials
│
├── Content Quality:
│   ├── Progressive learning structure (beginner to intermediate)
│   ├── 75% valuable content accessible for free
│   ├── 60% hands-on practical exercises
│   ├── Current industry practices (2024-2025)
│   └── Clear, jargon-free explanations with analogies
│
├── Technical Excellence:
│   ├── Perfect integration with Django models v2.7.1
│   ├── Proper access level enforcement
│   ├── Comprehensive assessment system
│   ├── Resource management and tracking
│   └── Analytics and progress monitoring
│
└── Student Success:
    ├── Clear learning objectives for each lesson
    ├── Immediate feedback through assessments
    ├── Real-world project experience
    ├── Professional certificate upon completion
    └── Career guidance and job placement support
```

### **Technical Validation Checklist:**
```python
Validation Requirements:
├── Database Schema Compatibility:
│   ├── All models follow v2.7.1 structure
│   ├── Proper use of mixins and inheritance
│   ├── Foreign key relationships validated
│   ├── JSON field validation working
│   └── Model clean() methods implemented
│
├── Content Distribution:
│   ├── 75% content marked as guest access
│   ├── 25% content marked as registered access
│   ├── Progressive complexity maintained
│   ├── Access levels properly enforced
│   └── Resource files properly categorized
│
├── Assessment System:
│   ├── Question and answer relationships correct
│   ├── Assessment attempt tracking functional
│   ├── Scoring and passing logic implemented
│   ├── Time limits and attempts enforced
│   └── Results and feedback system working
│
├── Analytics and Tracking:
│   ├── Enrollment progress calculation
│   ├── Course analytics updating
│   ├── Resource download tracking
│   ├── Time spent monitoring
│   └── Completion certificate generation
│
└── Performance and Security:
    ├── Efficient database queries
    ├── Proper indexing utilized
    ├── File access security enforced
    ├── User permission validation
    └── Error handling and logging
```

---

## **📋 CONTINUATION PROMPT FOR CONTEXT RESTORATION**

**When context is lost, use this exact prompt:**

*"I'm continuing course content generation for our educational platform. Please review the comprehensive reference document I'm providing that contains:*

1. *Complete Django database schema v2.7.1 with enhanced mixins and validation*
2. *Course 1 specifications: 16 modules, 75% guest/25% registered access model*
3. *Content creation standards with tiered access requirements*
4. *Technical implementation using Django ORM with proper model relationships*
5. *Success criteria and validation checklist for job-placement focused content*

*Key Technical Details:*
- *Models use TimeStampedMixin, OrderedMixin, DurationMixin, etc.*
- *Lesson model has tiered content: content, guest_content, registered_content*
- *Resource model includes FileTrackingMixin with download tracking*
- *Assessment system with Question/Answer relationships*
- *Course cloning and versioning capabilities*
- *Comprehensive analytics and progress tracking*

*Content Requirements:*
- *Course 1: "Software Testing with AI-Driven Test Automation" (16 weeks)*
- *Access: 75% guest (free), 25% registered (premium)*
- *Target: $45K-$75K QA job placement*
- *Structure: 8+ lessons per module, progressive difficulty*
- *Focus: Practical skills, industry tools, real-world projects*

*Please confirm you understand the platform structure and database schema, then continue with [specific task - e.g., "Module 5 content generation" or "Database population for Modules 1-3"].*

*Remember: Use the exact model structure from v2.7.1, maintain 75%/25% access distribution, focus on job-placement skills, and ensure Django ORM compatibility."*

---
