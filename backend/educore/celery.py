"""
Celery configuration for the eduplatform project.

This module sets up Celery for handling asynchronous tasks,
particularly for the AI course builder's long-running operations.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educore.settings')

# Create the Celery app
app = Celery('educore')

# Use the CELERY namespace for configuration keys
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Simple task that can be used for debugging Celery setup.
    """
    print(f'Request: {self.request!r}')
