# File Path: backend/courses/management/commands/populate_module_01_lesson_01_final.py
# Folder Path: /backend/courses/management/commands/
# Date Created: 2025-06-16 16:39:00
# Date Revised: 2025-06-16 16:39:00
# Current User: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-16 16:39:00 UTC
# Version: 1.0.0
# Purpose: ERROR-FREE course population using exact field names and constraints
# Course: Software Testing with AI-Driven Test Automation
# Module: 1 - Introduction to Software Testing Universe
# Lesson: 1.1 - What is Software Testing? - The Health Check Analogy

from django.core.management.base import BaseCommand
from courses.models import *
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Populate Module 1, Lesson 1 with ERROR-FREE field mapping'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('🚀 Starting ERROR-FREE population...'))

                # Phase 1: Create Category
                category = self.create_category()

                # Phase 2: Create Course
                course = self.create_course(category)

                # Phase 3: Create Module
                module = self.create_module(course)

                # Phase 4: Create Lesson
                lesson = self.create_lesson(module)

                # Phase 5: Create Resources
                resources = self.create_resources(lesson)

                # Phase 6: Create Assessment
                assessment = self.create_assessment(lesson)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ SUCCESS: Created course with {len(resources)} resources and {assessment.questions.count()} questions'
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ FAILED: {str(e)}'))
            raise

    def create_category(self):
        """Create Software Testing category"""
        category, created = Category.objects.get_or_create(
            name='Software Testing',
            defaults={
                'description': 'Comprehensive software testing courses covering manual testing, automation, and AI-driven testing.',
                'icon': 'fas fa-bug',
                'sort_order': 1,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('✅ Created category: Software Testing')
        return category

    def create_course(self, category):
        """Create course with EXACT field names"""
        course_data = {
            # Basic Information (CONFIRMED FIELD NAMES)
            'title': 'Software Testing with AI-Driven Test Automation',
            'subtitle': 'From Zero to Industry-Ready QA Professional in 16 Weeks',
            'description': 'Master software testing fundamentals and advanced AI-driven automation techniques in this comprehensive 16-week program designed for career changers and professionals.',
            'category': category,

            # Pricing (CONFIRMED FIELD NAMES)
            'price': 0.00,
            'discount_price': None,
            'discount_ends': None,

            # Course Metadata (CONFIRMED FIELD NAMES AND CHOICE VALUES)
            'level': 'intermediate',  # ✅ CONFIRMED: Valid choice, 12 chars < 20 limit
            'has_certificate': True,
            'is_featured': True,
            'requirements': [
                'Basic computer literacy and internet navigation skills',
                'Familiarity with using websites and mobile applications',
                'High school education or equivalent'
            ],
            'skills': [
                'Manual Software Testing Techniques',
                'Test Case Design and Execution',
                'Bug Reporting and Defect Management',
                'API Testing with Postman',
                'Web UI Automation with Selenium'
            ],
            'learning_objectives': [
                'Execute comprehensive manual testing strategies for web and mobile applications',
                'Design and implement automated testing frameworks using industry-standard tools',
                'Perform API testing and validation using modern testing tools'
            ],
            'target_audience': 'Career changers seeking entry into software testing, recent graduates, and professionals wanting to transition into quality assurance.',

            # Creation & Management (CONFIRMED FIELD NAMES AND CHOICE VALUES)
            'creation_method': 'manual',     # ✅ CONFIRMED: Valid choice, 6 chars < 20 limit
            'completion_status': 'complete', # ✅ CONFIRMED: Valid choice, 8 chars < 20 limit
            'completion_percentage': 8,
            'version': 1.0,
            'is_draft': False,
            'parent_version': None,

            # Publishing (CONFIRMED FIELD NAMES)
            'is_published': True,

            # Duration (CONFIRMED FIELD NAMES)
            'duration_minutes': 7200,  # 120 hours total

            # Analytics (CONFIRMED FIELD NAMES)
            'enrolled_students_count': 0,
            'avg_rating': 0.0,
            'total_reviews': 0,
            'last_enrollment_date': None
        }

        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults=course_data
        )

        if created:
            self.stdout.write(f'✅ Created course: {course.title}')
        return course

    def create_module(self, course):
        """Create Module 1 with EXACT field names"""
        module_data = {
            # Basic Information (CONFIRMED FIELD NAMES)
            'course': course,
            'title': 'Introduction to Software Testing Universe',
            'description': 'Welcome to the fascinating world of software testing! This foundational module introduces you to testing mindset, core concepts, and professional practices.',

            # Ordering (CONFIRMED FIELD NAMES)
            'order': 1,

            # Duration (CONFIRMED FIELD NAMES)
            'duration_minutes': 450,  # 7.5 hours

            # Publishing (CONFIRMED FIELD NAMES)
            'is_published': True
        }

        module, created = Module.objects.get_or_create(
            course=course,
            order=1,
            defaults=module_data
        )

        if created:
            self.stdout.write(f'✅ Created module: {module.title}')
        return module

    def create_lesson(self, module):
        """Create Lesson 1.1 with EXACT field names"""
        lesson_data = {
            # Basic Information (CONFIRMED FIELD NAMES)
            'module': module,
            'title': 'What is Software Testing? - The Health Check Analogy',

            # Content (CONFIRMED FIELD NAMES)
            'content': '''
# What is Software Testing? - The Health Check Analogy

## Learning Objectives
By the end of this lesson, you will be able to:
1. Define software testing using the health check analogy
2. Identify key components of effective software testing
3. Recognize the business value of testing through real-world examples
4. Understand the basic testing mindset and principles

## The Health Check Analogy

Just like doctors perform regular health checkups to identify potential health issues before they become serious problems, software testers perform systematic "health checkups" on software applications to identify bugs, defects, and usability issues before they reach end users.

## What is Software Testing?

Software testing is a systematic process of evaluating and verifying that a software application:
- Functions correctly according to requirements
- Meets quality standards for performance and usability
- Provides positive user experience
- Operates reliably under various conditions

## Core Testing Concepts

### Understanding Bugs and Quality
**Software Bug:** An error or flaw that causes incorrect behavior

### Quality Attributes
- **Functionality** - Does it work correctly?
- **Reliability** - Does it work consistently?
- **Performance** - Does it work efficiently?
- **Security** - Does it protect data?
- **Usability** - Is it user-friendly?

## Real-World Impact Examples
- Ariane 5 Rocket failure: $500 million loss
- Y2K Bug prevention: $300+ billion investment

## Business Benefits
- Early testing saves 10x costs
- Quality creates customer loyalty
- Career opportunities: $45K-$75K entry salaries

## Key Takeaways
1. Testing is healthcare for applications
2. Early testing saves money and reputation
3. Testers advocate for users and protect businesses
            ''',

            'guest_content': '''
# What is Software Testing? - The Health Check Analogy

## Learning Objectives
By the end of this lesson, you will be able to:
1. Define software testing using the health check analogy
2. Identify the key components of effective software testing
3. Recognize the business value of testing

## The Health Check Analogy
Just like doctors perform health checkups, software testers perform systematic "health checkups" on software applications.

## What is Software Testing?
Software testing is a systematic process of evaluating and verifying that software works correctly and meets quality standards.

## Key Takeaways
1. Testing is like healthcare for applications
2. Early testing saves money and reputation
3. Testers protect businesses and users
            ''',

            'registered_content': '''
# Advanced Software Testing Concepts

## Extended Learning Objectives
- Apply testing concepts to real-world business scenarios
- Analyze ROI of testing activities
- Understand career pathways in software testing

## Career Development Insights
### Salary Progression (2024 Data)
- Entry Level QA: $45,000-$55,000
- QA Analyst: $55,000-$70,000
- Senior QA Engineer: $70,000-$90,000

## Professional Certifications
- ISTQB Foundation Level
- CSTE Certification
- Agile Testing Certification
            ''',

            # Access & Type (CONFIRMED FIELD NAMES AND CHOICE VALUES)
            'access_level': 'guest',      # ✅ CONFIRMED: Valid choice, 5 chars < 20 limit
            'type': 'video',              # ✅ CONFIRMED: Field name is 'type', valid choice, 5 chars < 20 limit
            'has_assessment': True,
            'has_lab': False,
            'is_free_preview': True,

            # Media (CONFIRMED FIELD NAMES)
            'video_url': 'https://academy.testingpro.com/course1/module1/lesson1',
            'transcript': 'Welcome to your first lesson in software testing! Today we explore what software testing really means...',

            # Ordering (CONFIRMED FIELD NAMES)
            'order': 1,

            # Duration (CONFIRMED FIELD NAMES)
            'duration_minutes': 45
        }

        lesson, created = Lesson.objects.get_or_create(
            module=module,
            order=1,
            defaults=lesson_data
        )

        if created:
            self.stdout.write(f'✅ Created lesson: {lesson.title}')
        return lesson

    def create_resources(self, lesson):
        """Create resources with EXACT field names"""
        resources_data = [
            {
                # Basic Information (CONFIRMED FIELD NAMES)
                'lesson': lesson,
                'title': 'Testing Fundamentals Handbook',
                'type': 'document',  # ✅ CONFIRMED: Field name is 'type', valid choice, 8 chars < 20 limit
                'description': 'Comprehensive 25-page handbook covering software testing basics, terminology, and industry best practices.',

                # Content (CONFIRMED FIELD NAMES)
                'file': 'lesson_resources/module_01/lesson_01/testing_fundamentals_handbook.pdf',
                'url': None,
                'premium': False,

                # File Tracking (CONFIRMED FIELD NAMES)
                'uploaded': True,
                'file_size': 2048000,  # 2MB
                'mime_type': 'application/pdf',

                # Ordering (CONFIRMED FIELD NAMES)
                'order': 1
            },
            {
                'lesson': lesson,
                'title': 'Testing vs Development Visual Guide',
                'type': 'image',     # ✅ CONFIRMED: Valid choice, 5 chars < 20 limit
                'description': 'Professional infographic explaining differences between development and testing roles.',
                'file': 'lesson_resources/module_01/lesson_01/testing_vs_development_infographic.png',
                'url': None,
                'premium': False,
                'uploaded': True,
                'file_size': 512000,  # 512KB
                'mime_type': 'image/png',
                'order': 2
            },
            {
                'lesson': lesson,
                'title': 'Software Failures Video Compilation',
                'type': 'video',     # ✅ CONFIRMED: Valid choice, 5 chars < 20 limit
                'description': '15-minute video compilation analyzing famous software failures.',
                'file': 'lesson_resources/module_01/lesson_01/software_failures_compilation.mp4',
                'url': 'https://academy.testingpro.com/resources/software-failures-compilation',
                'premium': False,
                'uploaded': True,
                'file_size': 52428800,  # 50MB
                'mime_type': 'video/mp4',
                'order': 3
            }
        ]

        created_resources = []
        for resource_data in resources_data:
            resource, created = Resource.objects.get_or_create(
                lesson=lesson,
                title=resource_data['title'],
                defaults=resource_data
            )
            if created:
                created_resources.append(resource)
                self.stdout.write(f'  ✅ Created resource: {resource.title}')

        return created_resources

    def create_assessment(self, lesson):
        """Create assessment with EXACT field names"""
        # Create Assessment
        assessment_data = {
            # Basic Information (CONFIRMED FIELD NAMES)
            'lesson': lesson,
            'title': 'Software Testing Fundamentals Assessment',
            'description': 'Assessment covering health check analogy, core testing concepts, and professional testing mindset.',

            # Assessment Settings (CONFIRMED FIELD NAMES)
            'time_limit': 30,         # 30 minutes
            'passing_score': 70,      # 70% to pass
            'max_attempts': 3,
            'randomize_questions': True,
            'show_results': True
        }

        assessment, created = Assessment.objects.get_or_create(
            lesson=lesson,
            defaults=assessment_data
        )

        if created:
            self.stdout.write(f'✅ Created assessment: {assessment.title}')

            # Create Question
            question_data = {
                # Basic Information (CONFIRMED FIELD NAMES)
                'assessment': assessment,
                'question_text': 'What is the primary purpose of software testing according to the health check analogy?',
                'question_type': 'multiple_choice',  # ✅ CONFIRMED: Valid choice, 15 chars < 20 limit
                'order': 1,
                'points': 10,
                'explanation': 'Software testing serves as systematic health check for applications, identifying issues before they reach end users.'
            }

            question, q_created = Question.objects.get_or_create(
                assessment=assessment,
                question_text=question_data['question_text'],
                defaults=question_data
            )

            if q_created:
                # Create Answers
                answers_data = [
                    {
                        'question': question,
                        'answer_text': 'To systematically evaluate software quality and identify issues before users encounter them',
                        'is_correct': True,
                        'explanation': 'Correct! Testing is about proactive quality evaluation and early problem detection.',
                        'order': 1
                    },
                    {
                        'question': question,
                        'answer_text': 'To delay software releases until they are completely perfect',
                        'is_correct': False,
                        'explanation': 'Incorrect. Testing is about risk management within practical constraints.',
                        'order': 2
                    },
                    {
                        'question': question,
                        'answer_text': 'To find as many bugs as possible in the shortest time',
                        'is_correct': False,
                        'explanation': 'Incorrect. Testing is about systematic quality evaluation, not just bug hunting.',
                        'order': 3
                    }
                ]

                for answer_data in answers_data:
                    Answer.objects.get_or_create(
                        question=question,
                        answer_text=answer_data['answer_text'],
                        defaults=answer_data
                    )

                self.stdout.write(f'  ✅ Created question with {len(answers_data)} answers')

        return assessment
