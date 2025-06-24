"""
File: C:\Users\Santhanam\OneDrive\Personal\Full stack web development\eduplatform\backend\courses\management\commands\setup_test_data.py
Purpose: Creates test data for simulating your three-tiered educational platform

This command sets up:
1. Test users for each access level (unregistered, registered, premium)
2. Course content with different access levels
3. Categories and other required data

Usage: python manage.py setup_test_data

Variables you might need to modify:
- TEST_USERS: Change usernames, emails, or passwords for test accounts
- Test content: You can modify the course content to better match your educational needs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Module, Lesson, Resource
from users.models import Subscription
import datetime
import os

User = get_user_model()

# Test user credentials - Change these if you want different test accounts
TEST_USERS = [
    {
        'email': 'admin@example.com',
        'username': 'admin',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'subscription': 'premium'
    },
    {
        'email': 'premium@example.com',
        'username': 'premium',
        'password': 'premium123',
        'first_name': 'Premium',
        'last_name': 'User',
        'role': 'student',
        'subscription': 'premium'
    },
    {
        'email': 'basic@example.com',
        'username': 'basic',
        'password': 'basic123',
        'first_name': 'Basic',
        'last_name': 'User',
        'role': 'student',
        'subscription': 'basic'
    },
    {
        'email': 'free@example.com',
        'username': 'free',
        'password': 'free123',
        'first_name': 'Free',
        'last_name': 'User',
        'role': 'student',
        'subscription': 'free'
    },
    {
        'email': 'instructor@example.com',
        'username': 'instructor',
        'password': 'instructor123',
        'first_name': 'Instructor',
        'last_name': 'User',
        'role': 'instructor',
        'subscription': 'premium'
    }
]


class Command(BaseCommand):
    help = 'Sets up test data for simulating all three access tiers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test data...'))

        # Create test users
        self.create_test_users()

        # Create categories
        self.create_categories()

        # Create test courses with tiered content
        self.create_test_courses()

        self.stdout.write(self.style.SUCCESS(
            'Test data created successfully! You can now log in with the following accounts:\n'
            '- Admin: admin@example.com / admin123\n'
            '- Premium User: premium@example.com / premium123\n'
            '- Basic User: basic@example.com / basic123\n'
            '- Free User: free@example.com / free123\n'
            '- Instructor: instructor@example.com / instructor123'
        ))

    def create_test_users(self):
        """Create test users for all access tiers"""
        self.stdout.write('Creating test users...')

        for user_data in TEST_USERS:
            # Check if user already exists
            if not User.objects.filter(email=user_data['email']).exists():
                # Create user
                user = User.objects.create_user(
                    email=user_data['email'],
                    username=user_data['username'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_email_verified=True  # For testing, auto-verify email
                )

                # Create subscription
                subscription_tier = user_data['subscription']
                end_date = None

                if subscription_tier != 'free':
                    # Set subscription to expire in 30 days
                    end_date = timezone.now() + datetime.timedelta(days=30)

                Subscription.objects.create(
                    user=user,
                    tier=subscription_tier,
                    status='active',
                    end_date=end_date
                )

                self.stdout.write(
                    f'  Created {subscription_tier} user: {user.email}')
            else:
                self.stdout.write(
                    f'  User {user_data["email"]} already exists')

    def create_categories(self):
        """Create course categories"""
        self.stdout.write('Creating course categories...')

        categories = [
            {'name': 'Programming', 'description': 'Learn coding and software development'},
            {'name': 'Data Science', 'description': 'Analyze and interpret complex data'},
            {'name': 'Business', 'description': 'Develop business skills and knowledge'},
            {'name': 'Design', 'description': 'Learn graphic design and UX/UI principles'},
            {'name': 'Language',
                'description': 'Learn new languages and communication skills'}
        ]

        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )

            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Category {category.name} already exists')

    def create_test_courses(self):
        """Create test courses with tiered content"""
        self.stdout.write('Creating test courses with tiered content...')

        # Get instructor user
        try:
            instructor = User.objects.get(username='instructor')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Instructor user not found!'))
            return

        # Get categories
        programming = Category.objects.get(name='Programming')

        # Create a test course
        course, created = Course.objects.get_or_create(
            title='Python for Beginners',
            defaults={
                'subtitle': 'Learn Python programming from scratch',
                'description': 'A comprehensive course to learn Python programming language with tiered content access for testing.',
                'category': programming,
                'price': 490,
                'level': 'beginner',
                'duration': '8 hours',
                'has_certificate': True,
                'is_featured': True,
                'is_published': True,
            }
        )

        if created:
            self.stdout.write(f'  Created course: {course.title}')

            # Create modules
            self.create_modules_and_lessons(course, instructor)
        else:
            self.stdout.write(f'  Course {course.title} already exists')

    def create_modules_and_lessons(self, course, instructor):
        """Create modules and lessons with different access levels"""

        # Create course instructor relationship
        from courses.models import CourseInstructor
        CourseInstructor.objects.create(
            course=course,
            instructor=instructor,
            title='Lead Instructor',
            is_lead=True
        )

        # Module 1: Introduction (mostly basic access)
        module1 = Module.objects.create(
            course=course,
            title='Introduction to Python',
            description='Learn the basics of Python programming language',
            order=1,
            duration='2 hours'
        )

        # Lesson with basic access (for unregistered users)
        Lesson.objects.create(
            module=module1,
            title='What is Python?',
            content='<h1>Introduction to Python</h1><p>Python is a high-level, interpreted programming language known for its readability and simplicity.</p>',
            access_level='basic',
            duration='15min',
            type='video',
            order=1,
            is_free_preview=True
        )        # Lesson with registered access (for registered users)
        lesson2 = Lesson.objects.create(
            module=module1,
            title='Setting Up Your Environment',
            content='<h1>Setting Up Python</h1><p>Learn how to install Python and set up your development environment with detailed instructions.</p>',
            guest_content='<h1>Setting Up Python</h1><p>This content requires a free account. Please register to view the full installation guide.</p>',
            access_level='registered',
            duration='25min',
            type='video',
            order=2
        )

        # Resource for intermediate lesson
        Resource.objects.create(
            lesson=lesson2,
            title='Python Installation Guide',
            type='document',
            description='Step-by-step guide for installing Python'
        )

        # Module 2: Advanced Topics (premium access)
        module2 = Module.objects.create(
            course=course,
            title='Advanced Python Concepts',
            description='Explore advanced topics in Python programming',
            order=2,
            duration='3 hours'
        )        # Lesson with premium access (for premium users)
        lesson3 = Lesson.objects.create(
            module=module2,
            title='Object-Oriented Programming',
            content='<h1>Object-Oriented Programming in Python</h1><p>This premium lesson covers classes, inheritance, polymorphism, and best practices for OOP in Python.</p>',
            guest_content='<h1>Object-Oriented Programming</h1><p>This is premium content. Please upgrade your account to access this lesson.</p>',
            registered_content='<h1>Object-Oriented Programming</h1><p>This is premium content requiring a paid subscription. You can view basic information about OOP here, but detailed examples require an upgrade.</p>',
            access_level='premium',
            duration='45min',
            type='video',
            order=1
        )

        # Premium resource
        Resource.objects.create(
            lesson=lesson3,
            title='OOP Exercises',
            type='document',
            description='Practice exercises for OOP concepts',
            premium=True
        )
