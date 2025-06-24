"""
File: C:\Users\Santhanam\OneDrive\Personal\Full stack web development\eduplatform\backend\courses\management\commands\run_local_prod.py
Purpose: Django management command to run a production-like server locally

This command allows you to start a production-like server on your local machine
for testing your educational platform with all three user tiers.

Usage: python manage.py run_local_prod

Variables you might need to modify:
- DEFAULT_PORT: Change this if port 8000 is already in use on your system
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import sys


class Command(BaseCommand):
    help = 'Runs the server with production-like settings for local testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            default=8000,
            type=int,
            help='Port to run the server on'
        )

    def handle(self, *args, **options):
        # Set the settings module to use our local prod settings
        os.environ['DJANGO_SETTINGS_MODULE'] = 'educore.settings_local_prod'

        # Collect static files like in production
        self.stdout.write(self.style.SUCCESS('Collecting static files...'))
        call_command('collectstatic', '--no-input')

        # Run migrations to ensure database is up to date
        self.stdout.write(self.style.SUCCESS('Running migrations...'))
        call_command('migrate')

        # Start the server
        port = options['port']
        self.stdout.write(self.style.SUCCESS(
            f'Starting production-like server at http://127.0.0.1:{port}/'
        ))

        # Use Django's runserver but with the production settings
        call_command('runserver', f'0.0.0.0:{port}')
