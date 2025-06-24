#
# File Path: instructor_portal/apps.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-01 00:00:00
# Date Revised: 2025-06-21 18:51:00
# Current Date and Time (UTC): 2025-06-21 18:51:00
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-21 18:51:00 UTC
# User: sujibeautysalon
# Version: 2.0.1
#
# Application Configuration for the Instructor Portal
#
# Version 2.0.1 Changes:
# - FIXED: Changed register_cleanup_tasks to setup_periodic_tasks
# - RESOLVED: Import error that was causing startup warnings

from django.apps import AppConfig
from django.conf import settings
import logging
import os


class InstructorPortalConfig(AppConfig):
    """
    App configuration for the instructor portal module
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'instructor_portal'
    verbose_name = 'Instructor Portal & Course Management'

    def ready(self):
        """
        Initialize app with proper signal handling and task registration
        """
        logger = logging.getLogger(__name__)
        logger.info("Initializing Instructor Portal module")

        try:
            # Import signals
            from . import signals
            logger.debug("Instructor Portal signals registered")

            # Register periodic tasks if enabled
            if getattr(settings, 'ENABLE_INSTRUCTOR_PORTAL_TASKS', True):
                try:
                    # FIXED: Use existing setup_periodic_tasks instead of non-existent register_cleanup_tasks
                    from .tasks import setup_periodic_tasks
                    success = setup_periodic_tasks()
                    if success:
                        logger.info("Instructor Portal maintenance tasks registered successfully")
                    else:
                        logger.warning("Maintenance tasks setup completed with warnings")
                except Exception as e:
                    logger.warning(f"Failed to register maintenance tasks: {e}")

            # Initialize course statistics cache
            if getattr(settings, 'PRELOAD_INSTRUCTOR_STATS', False):
                try:
                    from .models import InstructorProfile
                    user_model = settings.AUTH_USER_MODEL

                    # Defer actual work to avoid app registry not ready issues
                    from django.core.cache import cache
                    cache.set('instructor_portal_initialized', True, 3600)

                    logger.info("Instructor statistics preloading scheduled")
                except Exception as e:
                    logger.warning(f"Failed to initialize statistics cache: {e}")

            # Check for environment-specific configurations
            if os.environ.get('INSTRUCTOR_PORTAL_TIER_OVERRIDE'):
                logger.warning(
                    "INSTRUCTOR_PORTAL_TIER_OVERRIDE environment variable detected. "
                    "This will override normal tier restrictions and should only be used in development."
                )

        except Exception as e:
            logger.error(f"Error initializing Instructor Portal: {e}", exc_info=True)
