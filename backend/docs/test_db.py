#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educore.settings')

# Setup Django
django.setup()

try:
    from courses.models import Course, Category
    print(f"✅ Course model loaded successfully")
    print(f"✅ Course count: {Course.objects.count()}")
    print(f"✅ Category count: {Category.objects.count()}")

    # Test featured courses query
    featured_courses = Course.objects.filter(is_featured=True, is_published=True)
    print(f"✅ Featured courses query works: {featured_courses.count()} featured courses")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"❌ Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
