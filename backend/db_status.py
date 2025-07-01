#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduplatform.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db.utils import IntegrityError

def check_database_connection():
    """Check if database is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            print(f"✓ Table {table_name} exists")
            return True
    except Exception as e:
        print(f"✗ Table {table_name} does not exist: {e}")
        return False

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
            print(f"✓ Column {table_name}.{column_name} exists")
            return True
    except Exception as e:
        print(f"✗ Column {table_name}.{column_name} does not exist: {e}")
        return False

if __name__ == '__main__':
    print("=== DATABASE STATUS CHECK ===")

    if not check_database_connection():
        exit(1)

    # Check critical tables and columns
    check_table_exists('courses_course')
    check_column_exists('courses_course', 'meta_keywords')
    check_column_exists('courses_course', 'meta_description')

    print("\n=== CHECKING MIGRATIONS ===")
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

    if plan:
        print(f"⚠ Unapplied migrations found: {len(plan)}")
        for migration, backwards in plan:
            print(f"  - {migration}")
    else:
        print("✓ All migrations are applied")

    print("\n=== MIGRATION STATUS COMPLETE ===")
