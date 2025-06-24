# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django environment setup utility

This module provides functions to set up the Django environment
for static analysis of models, views, and other components.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:13:56
"""

import os
import sys
import logging
import importlib
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_django_environment(project_path: str) -> None:
    """Set up Django environment for static analysis

    Args:
        project_path: Path to the Django project root directory

    Raises:
        ImportError: If Django settings cannot be imported
    """
    # Convert to Path object
    project_path = Path(project_path).resolve()

    # Add project directory to Python path
    sys.path.insert(0, str(project_path))

    # Find Django settings module
    settings_module = find_settings_module(project_path)

    if not settings_module:
        logger.warning("Could not find Django settings module automatically")

        # Try with default naming convention
        project_name = project_path.name
        settings_module = f"{project_name}.settings"
        logger.info(f"Using default settings module name: {settings_module}")

    # Set Django settings module environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    # Disable DEBUG to avoid side effects
    os.environ.setdefault('DEBUG', 'False')

    # Use a test database to avoid modifying production data
    os.environ.setdefault('DATABASE_URL', 'sqlite://:memory:')

    # Configure Django
    try:
        import django
        django.setup()
        logger.info(
            f"Django {django.get_version()} environment setup complete")
        logger.info(f"Using settings module: {settings_module}")

    except ImportError as e:
        logger.error(f"Could not import Django: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error setting up Django environment: {str(e)}")
        raise


def find_settings_module(project_path: Path) -> str:
    """Find Django settings module in a project directory

    Args:
        project_path: Path to the Django project root directory

    Returns:
        str: Django settings module name, or empty string if not found
    """
    # Common patterns for settings modules
    settings_patterns = [
        '{project_name}/settings.py',
        '{project_name}/settings/__init__.py',
        'settings.py',
        'config/settings.py',
        'conf/settings.py',
    ]

    # Try to determine the project name from the directory name
    project_name = project_path.name

    # Check each pattern
    for pattern in settings_patterns:
        # Replace project_name placeholder
        pattern_filled = pattern.format(project_name=project_name)

        # Check if file exists
        settings_path = project_path / pattern_filled
        if settings_path.exists():
            # Convert file path to module name
            relative_path = settings_path.relative_to(project_path)
            module_path = str(relative_path).replace(
                '/', '.').replace('\\', '.')

            # Remove .py extension
            if module_path.endswith('.py'):
                module_path = module_path[:-3]

            return module_path

    # Fall back to scanning the directory
    for item in project_path.glob('**/settings.py'):
        # Skip virtual environments
        if any(venv_dir in str(item) for venv_dir in ['venv', 'env', '.env', 'virtualenv', '.virtualenv']):
            continue

        # Convert file path to module name
        try:
            relative_path = item.relative_to(project_path)
            module_path = str(relative_path).replace(
                '/', '.').replace('\\', '.')

            # Remove .py extension
            if module_path.endswith('.py'):
                module_path = module_path[:-3]

            return module_path
        except ValueError:
            pass

    return ""
