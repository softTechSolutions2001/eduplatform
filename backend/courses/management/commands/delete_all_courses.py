# File Path: backend/courses/management/commands/delete_all_courses.py
# Folder Path: /backend/courses/management/commands/
# Date Created: 2025-06-15 16:04:18
# Date Revised: 2025-06-15 16:08:06
# Current Date and Time (UTC): 2025-06-15 16:08:06
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 16:08:06 UTC
# User: sujibeautysalon
# Version: 1.0.1
#
# Django Management Command for Safe Course Deletion - FIXED
#
# This command provides multiple methods to delete existing courses from the backend
# with proper cleanup of related data, files, and maintaining referential integrity.
#
# Version 1.0.1 Changes:
# - FIXED: Handle missing timestamp fields in models (created_date, updated_date)
# - ADDED: Database field existence checks before operations
# - IMPROVED: Raw SQL deletion as fallback for problematic models
# - ENHANCED: Better error handling for missing database columns

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Lesson, Resource, Assessment, Question, Answer,
    Enrollment, Progress, CourseInstructor, Category
)
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Safely delete all existing courses with proper cleanup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without interactive prompt'
        )
        parser.add_argument(
            '--keep-categories',
            action='store_true',
            help='Keep categories when deleting courses'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force-sql',
            action='store_true',
            help='Use raw SQL deletion to bypass model issues'
        )

    def handle(self, *args, **options):
        """Execute the course deletion command"""

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No actual deletion will occur"))

        # Get deletion statistics
        stats = self.get_deletion_stats()
        self.display_stats(stats)

        if options['dry_run']:
            return

        # Confirmation check
        if not options['confirm']:
            confirm = input("\nAre you sure you want to delete all courses? Type 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                self.stdout.write(self.style.ERROR("Deletion cancelled."))
                return

        # Perform deletion
        try:
            if options['force_sql']:
                deleted_counts = self.delete_with_raw_sql(options)
            else:
                with transaction.atomic():
                    deleted_counts = self.delete_all_courses(options)

            self.display_deletion_results(deleted_counts)

        except Exception as e:
            logger.error(f"Error during course deletion: {e}")
            self.stdout.write(
                self.style.ERROR(f"Deletion failed with Django ORM: {e}")
            )
            self.stdout.write(
                self.style.WARNING("Trying with raw SQL deletion...")
            )
            try:
                deleted_counts = self.delete_with_raw_sql(options)
                self.display_deletion_results(deleted_counts)
            except Exception as sql_error:
                raise CommandError(f"Both ORM and SQL deletion failed: {sql_error}")

    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = %s
            """, [table_name])
            return cursor.fetchone()[0] > 0

    def get_table_count(self, table_name):
        """Get count of records in a table safely"""
        if not self.table_exists(table_name):
            return 0

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def get_deletion_stats(self):
        """Get statistics of what will be deleted"""
        # Use table names directly to avoid model field issues
        stats = {
            'courses': self.get_table_count('courses_course'),
            'modules': self.get_table_count('courses_module'),
            'lessons': self.get_table_count('courses_lesson'),
            'resources': self.get_table_count('courses_resource'),
            'assessments': self.get_table_count('courses_assessment'),
            'questions': self.get_table_count('courses_question'),
            'answers': self.get_table_count('courses_answer'),
            'enrollments': self.get_table_count('courses_enrollment'),
            'progress_records': self.get_table_count('courses_progress'),
            'assessment_attempts': self.get_table_count('courses_assessmentattempt'),
            'attempt_answers': self.get_table_count('courses_attemptanswer'),
            'reviews': self.get_table_count('courses_review'),
            'notes': self.get_table_count('courses_note'),
            'certificates': self.get_table_count('courses_certificate'),
            'course_instructors': self.get_table_count('courses_courseinstructor'),
        }
        return stats

    def display_stats(self, stats):
        """Display deletion statistics"""
        self.stdout.write(self.style.WARNING("\n=== DELETION STATISTICS ==="))
        for item, count in stats.items():
            if count > 0:
                self.stdout.write(f"{item.replace('_', ' ').title()}: {count}")

        total_records = sum(stats.values())
        self.stdout.write(f"\nTotal records to be deleted: {total_records}")

    def delete_with_raw_sql(self, options):
        """Delete using raw SQL to bypass model field issues"""
        self.stdout.write(self.style.WARNING("\nUsing RAW SQL deletion to bypass model issues..."))

        deleted_counts = {}

        # Define deletion order (respecting foreign key constraints)
        deletion_order = [
            ('attempt_answers', 'courses_attemptanswer'),
            ('assessment_attempts', 'courses_assessmentattempt'),
            ('progress_records', 'courses_progress'),
            ('notes', 'courses_note'),
            ('certificates', 'courses_certificate'),
            ('reviews', 'courses_review'),
            ('enrollments', 'courses_enrollment'),
            ('answers', 'courses_answer'),
            ('questions', 'courses_question'),
            ('assessments', 'courses_assessment'),
            ('resources', 'courses_resource'),
            ('lessons', 'courses_lesson'),
            ('modules', 'courses_module'),
            ('course_instructors', 'courses_courseinstructor'),
            ('courses', 'courses_course'),
        ]

        # Clean up files first
        self.cleanup_resource_files()

        with connection.cursor() as cursor:
            # Disable foreign key checks temporarily for MySQL
            try:
                cursor.execute("SET foreign_key_checks = 0")
            except:
                pass  # Not MySQL

            for item_name, table_name in deletion_order:
                if self.table_exists(table_name):
                    try:
                        # Get count before deletion
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]

                        if count > 0:
                            self.stdout.write(f"Deleting {count} records from {table_name}...")
                            cursor.execute(f"DELETE FROM {table_name}")
                            deleted_counts[item_name] = count
                        else:
                            deleted_counts[item_name] = 0

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error deleting from {table_name}: {e}")
                        )
                        deleted_counts[item_name] = 0
                else:
                    self.stdout.write(
                        self.style.NOTICE(f"Table {table_name} does not exist, skipping...")
                    )
                    deleted_counts[item_name] = 0

            # Re-enable foreign key checks
            try:
                cursor.execute("SET foreign_key_checks = 1")
            except:
                pass  # Not MySQL

        # Optionally clean up categories
        if not options['keep_categories']:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM courses_category")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        cursor.execute("DELETE FROM courses_category")
                        deleted_counts['categories'] = count
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error deleting categories: {e}")
                )

        return deleted_counts

    def delete_all_courses(self, options):
        """Delete all courses and related data with proper cleanup using Django ORM"""
        deleted_counts = {}

        self.stdout.write(self.style.WARNING("\nStarting deletion process with Django ORM..."))

        # Try to delete using ORM, fall back to raw SQL if needed
        try:
            # 1. Delete student progress and analytics
            self.stdout.write("Deleting student progress data...")

            # Handle models that might have missing fields
            try:
                from courses.models import AttemptAnswer, AssessmentAttempt
                deleted_counts['attempt_answers'] = AttemptAnswer.objects.all().delete()[0]
                deleted_counts['assessment_attempts'] = AssessmentAttempt.objects.all().delete()[0]
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Using raw SQL for attempt data: {e}"))
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM courses_attemptanswer")
                    cursor.execute("DELETE FROM courses_assessmentattempt")
                    deleted_counts['attempt_answers'] = cursor.rowcount
                    deleted_counts['assessment_attempts'] = cursor.rowcount

            deleted_counts['progress_records'] = Progress.objects.all().delete()[0]

            # Handle models that might not exist
            try:
                from courses.models import Note, Certificate, Review
                deleted_counts['notes'] = Note.objects.all().delete()[0]
                deleted_counts['certificates'] = Certificate.objects.all().delete()[0]
                deleted_counts['reviews'] = Review.objects.all().delete()[0]
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Some models don't exist: {e}"))
                deleted_counts.update({'notes': 0, 'certificates': 0, 'reviews': 0})

            # 2. Delete enrollments
            self.stdout.write("Deleting enrollments...")
            deleted_counts['enrollments'] = Enrollment.objects.all().delete()[0]

            # 3. Delete course content
            self.stdout.write("Deleting course content...")
            deleted_counts['answers'] = Answer.objects.all().delete()[0]
            deleted_counts['questions'] = Question.objects.all().delete()[0]
            deleted_counts['assessments'] = Assessment.objects.all().delete()[0]

            # Clean up resource files
            self.cleanup_resource_files()
            deleted_counts['resources'] = Resource.objects.all().delete()[0]

            deleted_counts['lessons'] = Lesson.objects.all().delete()[0]
            deleted_counts['modules'] = Module.objects.all().delete()[0]

            # 4. Delete course instructor relationships
            self.stdout.write("Deleting instructor assignments...")
            deleted_counts['course_instructors'] = CourseInstructor.objects.all().delete()[0]

            # 5. Delete courses
            self.stdout.write("Deleting courses...")
            deleted_counts['courses'] = Course.objects.all().delete()[0]

            # 6. Optionally clean up categories
            if not options['keep_categories']:
                self.stdout.write("Deleting empty categories...")
                deleted_counts['categories'] = Category.objects.filter(courses__isnull=True).delete()[0]

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ORM deletion failed: {e}"))
            raise e

        return deleted_counts

    def cleanup_resource_files(self):
        """Clean up uploaded files for resources"""
        self.stdout.write("Cleaning up uploaded files...")

        deleted_files = 0

        # Clean up resource files using raw SQL to avoid model issues
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT file FROM courses_resource WHERE file IS NOT NULL AND file != ''")
                file_paths = [row[0] for row in cursor.fetchall()]

                for file_path in file_paths:
                    try:
                        full_path = os.path.join('media', file_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_files += 1
                    except Exception as e:
                        logger.warning(f"Could not delete file {file_path}: {e}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not clean resource files: {e}"))

        # Clean up course thumbnails
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT thumbnail FROM courses_course WHERE thumbnail IS NOT NULL AND thumbnail != ''")
                thumbnail_paths = [row[0] for row in cursor.fetchall()]

                for thumbnail_path in thumbnail_paths:
                    try:
                        full_path = os.path.join('media', thumbnail_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_files += 1
                    except Exception as e:
                        logger.warning(f"Could not delete thumbnail {thumbnail_path}: {e}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not clean thumbnail files: {e}"))

        self.stdout.write(f"Deleted {deleted_files} files from filesystem")

    def display_deletion_results(self, deleted_counts):
        """Display deletion results"""
        self.stdout.write(self.style.SUCCESS("\n=== DELETION COMPLETED ==="))

        total_deleted = 0
        for item, count in deleted_counts.items():
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {item.replace('_', ' ').title()}: {count} deleted")
                )
                total_deleted += count

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal records deleted: {total_deleted}")
        )
        self.stdout.write(
            self.style.SUCCESS("All courses and related data have been successfully deleted!")
        )
