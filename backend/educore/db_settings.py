"""
Database settings for the Educational Platform project.
This file contains settings specific to PostgreSQL database configuration.
"""

import os
from pathlib import Path

# Get environment variables or use default values
DB_NAME = os.environ.get('DB_NAME', 'eduplatform')
DB_USER = os.environ.get('DB_USER', 'eduplatform_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Vajjiram@79')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

# PostgreSQL database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            # Enable server-side connection pooling
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
        },
        'CONN_MAX_AGE': 600,  # Connection pooling - keep connections for 10 minutes
    }
}

# Database connection error handling
DATABASE_CONNECTION_RETRY_ATTEMPTS = 3
DATABASE_CONNECTION_RETRY_DELAY = 1  # seconds

# Performance settings
DATABASE_ATOMIC_REQUESTS = True  # Wrap all requests in a transaction

# Database testing settings (for pytest/unittest)
if os.environ.get('TESTING', False):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db.sqlite3',
    }
