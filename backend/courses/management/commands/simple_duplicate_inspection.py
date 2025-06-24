# File Path: backend/courses/management/commands/simple_duplicate_inspection.py
# Version: 1.0.0
# Date Created: 2025-06-15 05:54:32
# Date Revised: 2025-06-15 05:54:32
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 05:54:32 UTC
# User: sujibeautysalon
#
# Django Management Command: Simple Duplicate Category Inspection
#
# This command provides a complete forensic analysis of duplicate categories
# using only raw SQL queries to avoid Django ORM model/database mismatches.
#
# Key Features:
# - Works with current database schema (no migrations required)
# - Bypasses Django ORM to avoid column mismatch errors
# - Provides complete duplicate analysis and recommendations
# - Shows which duplicates to keep/remove with reasoning

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Simple duplicate category inspection using raw SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-courses',
            action='store_true',
            help='Show which courses are associated with each duplicate category',
        )

    def handle(self, *args, **options):
        show_courses = options['show_courses']

        self.stdout.write(
            self.style.SUCCESS('🔍 SIMPLE DUPLICATE CATEGORY ANALYSIS\n')
        )

        # Step 1: Find duplicates
        duplicates = self.find_duplicates()

        if not duplicates:
            self.stdout.write(
                self.style.SUCCESS('✅ No duplicates found!')
            )
            return

        # Step 2: Analyze each duplicate group
        self.analyze_duplicates(duplicates, show_courses)

        # Step 3: Show the fix plan
        self.show_fix_plan(duplicates)

    def find_duplicates(self):
        """Find duplicate categories using raw SQL."""
        self.stdout.write('1️⃣ FINDING DUPLICATE CATEGORIES...\n')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    LOWER(TRIM(name)) as normalized_name,
                    COUNT(*) as count,
                    ARRAY_AGG(id ORDER BY id) as ids,
                    ARRAY_AGG(name ORDER BY id) as names
                FROM courses_category
                GROUP BY LOWER(TRIM(name))
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC, LOWER(TRIM(name))
            """)

            results = cursor.fetchall()

        duplicates = []
        total_extra_records = 0

        for normalized_name, count, ids, names in results:
            duplicate_info = {
                'normalized_name': normalized_name,
                'count': count,
                'ids': ids,
                'names': names
            }
            duplicates.append(duplicate_info)
            total_extra_records += count - 1

            self.stdout.write(f'   🔴 "{names[0]}": {count} duplicates (IDs: {ids})')
            if len(set(names)) > 1:
                self.stdout.write(f'      Name variations: {list(set(names))}')

        self.stdout.write(f'\n   📊 Summary: {len(duplicates)} duplicate groups, {total_extra_records} records to remove\n')
        return duplicates

    def analyze_duplicates(self, duplicates, show_courses):
        """Analyze each duplicate group in detail."""
        self.stdout.write('2️⃣ DETAILED DUPLICATE ANALYSIS...\n')

        for dup in duplicates:
            ids = dup['ids']
            names = dup['names']

            self.stdout.write(f'🔍 Analyzing "{names[0]}" group:')

            # Get course counts for each category
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        cat.id,
                        cat.name,
                        COUNT(course.id) as course_count
                    FROM courses_category cat
                    LEFT JOIN courses_course course ON course.category_id = cat.id
                    WHERE cat.id = ANY(%s)
                    GROUP BY cat.id, cat.name
                    ORDER BY COUNT(course.id) DESC, cat.id
                """, [ids])

                results = cursor.fetchall()

            # Determine which one to keep (most courses, then lowest ID)
            keeper = results[0]  # First result has most courses due to ORDER BY
            victims = results[1:]

            self.stdout.write(f'   ✅ KEEPER: ID {keeper[0]} - "{keeper[1]}" ({keeper[2]} courses)')

            total_courses_to_reassign = 0
            for victim_id, victim_name, victim_courses in victims:
                total_courses_to_reassign += victim_courses
                self.stdout.write(f'   ❌ REMOVE: ID {victim_id} - "{victim_name}" ({victim_courses} courses)')

            self.stdout.write(f'   📊 Total courses to reassign: {total_courses_to_reassign}')

            # Show sample courses if requested
            if show_courses and total_courses_to_reassign > 0:
                self.show_affected_courses(ids)

            # Analyze creation patterns
            self.analyze_creation_pattern(ids)
            self.stdout.write('')

    def show_affected_courses(self, category_ids):
        """Show which courses will be affected by duplicate removal."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    course.id,
                    course.title,
                    course.category_id,
                    cat.name as category_name
                FROM courses_course course
                JOIN courses_category cat ON cat.id = course.category_id
                WHERE course.category_id = ANY(%s)
                ORDER BY course.category_id, course.title
                LIMIT 10
            """, [category_ids])

            results = cursor.fetchall()

            if results:
                self.stdout.write('      📚 Sample affected courses:')
                for course_id, course_title, cat_id, cat_name in results:
                    self.stdout.write(f'         - "{course_title}" (Course ID: {course_id}, Category ID: {cat_id})')

    def analyze_creation_pattern(self, ids):
        """Analyze the creation pattern based on ID gaps."""
        if len(ids) < 2:
            return

        id_gaps = []
        for i in range(1, len(ids)):
            gap = ids[i] - ids[i-1]
            id_gaps.append(gap)

        min_gap = min(id_gaps)

        if min_gap == 1:
            pattern = "🚨 CONSECUTIVE IDs - likely race condition or rapid double-click"
        elif min_gap <= 5:
            pattern = "⚠️  CLOSE IDs - likely created in same session"
        elif min_gap <= 50:
            pattern = "ℹ️  NEARBY IDs - created relatively close in time"
        else:
            pattern = "✅ SPREAD IDs - created over extended time"

        self.stdout.write(f'   🔍 Creation pattern: {pattern}')
        self.stdout.write(f'      ID sequence: {ids} (gaps: {id_gaps})')

    def show_fix_plan(self, duplicates):
        """Show the complete fix plan."""
        self.stdout.write('3️⃣ COMPLETE FIX PLAN...\n')

        self.stdout.write('📋 DATA MIGRATION OPERATIONS:')

        total_categories_to_delete = 0
        total_courses_to_reassign = 0

        for dup in duplicates:
            ids = dup['ids']

            # Get course counts
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        cat.id,
                        cat.name,
                        COUNT(course.id) as course_count
                    FROM courses_category cat
                    LEFT JOIN courses_course course ON course.category_id = cat.id
                    WHERE cat.id = ANY(%s)
                    GROUP BY cat.id, cat.name
                    ORDER BY COUNT(course.id) DESC, cat.id
                """, [ids])

                results = cursor.fetchall()

            keeper = results[0]
            victims = results[1:]

            self.stdout.write(f'\n   Group: "{keeper[1]}"')
            self.stdout.write(f'   ✅ Keep: ID {keeper[0]} ({keeper[2]} courses)')

            for victim_id, victim_name, victim_courses in victims:
                total_categories_to_delete += 1
                total_courses_to_reassign += victim_courses
                self.stdout.write(f'   ❌ Delete: ID {victim_id} (reassign {victim_courses} courses to ID {keeper[0]})')

        # Show the exact SQL operations
        self.stdout.write(f'\n📊 SUMMARY:')
        self.stdout.write(f'   • Categories to delete: {total_categories_to_delete}')
        self.stdout.write(f'   • Courses to reassign: {total_courses_to_reassign}')

        self.stdout.write(f'\n🛠️  NEXT STEPS:')
        steps = [
            "1. Create data migration to remove duplicates (preserves all course data)",
            "2. Apply schema migration to add unique constraint",
            "3. Update Category model with validation",
            "4. Test that no new duplicates can be created"
        ]

        for step in steps:
            self.stdout.write(f'   {step}')

        # Show the ROOT CAUSE
        self.stdout.write(f'\n🎯 ROOT CAUSE ANALYSIS:')
        causes = [
            "• No unique constraint on category.name in database",
            "• No model-level validation preventing duplicates",
            "• Frontend allows duplicate submissions",
            "• Race conditions from concurrent requests"
        ]

        for cause in causes:
            self.stdout.write(f'   {cause}')

        self.stdout.write(f'\n✨ This analysis shows we have a simple, solvable duplicate issue!')
