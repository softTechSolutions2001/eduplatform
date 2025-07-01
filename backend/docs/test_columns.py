#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educore.settings')
django.setup()

from django.db import connection

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
            print(f"OK: Column {table_name}.{column_name} exists")
            return True
    except Exception as e:
        print(f"ERROR: Column {table_name}.{column_name} does not exist: {e}")
        return False

def test_featured_endpoint_query():
    """Test the query that's failing in the featured endpoint"""
    try:
        from courses.models import Course
        # This should work if meta_keywords column exists
        courses = Course.objects.filter(is_featured=True).values(
            'id', 'title', 'meta_keywords', 'meta_description'
        )[:5]
        print(f"OK: Featured courses query works, found {len(list(courses))} courses")
        return True
    except Exception as e:
        print(f"ERROR: Featured courses query failed: {e}")
        return False

if __name__ == '__main__':
    print("=== DATABASE COLUMN CHECK ===")

    # Check critical columns
    meta_keywords_exists = check_column_exists('courses_course', 'meta_keywords')
    meta_description_exists = check_column_exists('courses_course', 'meta_description')

    print("\n=== TESTING FEATURED ENDPOINT QUERY ===")
    query_works = test_featured_endpoint_query()

    print(f"\n=== SUMMARY ===")
    print(f"meta_keywords column: {'EXISTS' if meta_keywords_exists else 'MISSING'}")
    print(f"meta_description column: {'EXISTS' if meta_description_exists else 'MISSING'}")
    print(f"Featured endpoint query: {'WORKS' if query_works else 'FAILS'}")

    if meta_keywords_exists and meta_description_exists and query_works:
        print("STATUS: ALL GOOD - Database should be working")
    else:
        print("STATUS: ISSUES FOUND - 500 errors likely to persist")
