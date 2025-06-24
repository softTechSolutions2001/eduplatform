from django.core.management.base import BaseCommand
from courses.models import Course, Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Adds sample data to the database'

    def handle(self, *args, **kwargs):
        # Create a category if it doesn't exist
        category, created = Category.objects.get_or_create(
            name='Software Development',
            defaults={
                'slug': 'software-development',
                'description': 'Courses related to software development.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created category: {category.name}'))

        # Create a course
        course, created = Course.objects.get_or_create(
            slug='software-testing',
            defaults={
                'title': 'Software Testing',
                'description': 'Learn software testing methodologies and best practices.',
                'category': category,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created course: {course.title}'))

        self.stdout.write(self.style.SUCCESS('Sample data added successfully'))
