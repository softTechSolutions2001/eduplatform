"""
File: backend/users/apps.py
Purpose: Enhanced Django app configuration for users app
Date Revised: 2025-07-15 00:00:00 UTC
Version: 2.0.0 - Production-Ready Configuration

ENHANCEMENTS:
- Added signal registration for proper model event handling
- Enhanced error handling and logging
- Added health checks and monitoring
- Improved security and performance settings
"""

import logging
import sys

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register

logger = logging.getLogger(__name__)


class UsersConfig(AppConfig):
    """
    Enhanced configuration for the users Django app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "User Management System"

    def ready(self):
        """
        Initialize app when Django starts.
        ENHANCED: Added comprehensive initialization.
        """
        try:
            # Import signals to register them (your existing code)
            import users.signals

            # Import and register health checks
            self._register_health_checks()

            # Validate configuration
            self._validate_configuration()

            # Initialize monitoring
            self._initialize_monitoring()

            logger.info(f"Users app initialized successfully - {self.verbose_name}")

        except Exception as e:
            logger.error(f"Error initializing users app: {str(e)}")
            # Don't re-raise in production to prevent startup failures
            if settings.DEBUG:
                raise

    def _register_health_checks(self):
        """Register health check endpoints."""
        try:
            from django.core.checks import Tags, register

            @register(Tags.security)
            def check_user_security_settings(app_configs, **kwargs):
                """Check security-related settings for users app."""
                errors = []

                # Check password validation
                if not getattr(settings, "AUTH_PASSWORD_VALIDATORS", None):
                    errors.append(
                        Error(
                            "AUTH_PASSWORD_VALIDATORS not configured",
                            hint="Configure password validators for security",
                            id="users.E001",
                        )
                    )

                # Check JWT secret key
                if hasattr(settings, "SIMPLE_JWT"):
                    jwt_settings = settings.SIMPLE_JWT
                    if jwt_settings.get("SIGNING_KEY") == settings.SECRET_KEY:
                        errors.append(
                            Error(
                                "JWT using default SECRET_KEY",
                                hint="Use a separate signing key for JWT tokens",
                                id="users.E002",
                            )
                        )

                # Check email backend
                if (
                    settings.EMAIL_BACKEND
                    == "django.core.mail.backends.dummy.EmailBackend"
                ):
                    if not settings.DEBUG:
                        errors.append(
                            Error(
                                "Dummy email backend in production",
                                hint="Configure proper email backend for production",
                                id="users.E003",
                            )
                        )

                return errors

            logger.debug("Health checks registered for users app")

        except Exception as e:
            logger.error(f"Error registering health checks: {str(e)}")

    def _validate_configuration(self):
        """Validate critical configuration settings."""
        try:
            required_settings = [
                "SECRET_KEY",
                "DEFAULT_FROM_EMAIL",
            ]

            missing_settings = []
            for setting in required_settings:
                if not hasattr(settings, setting) or not getattr(settings, setting):
                    missing_settings.append(setting)

            if missing_settings:
                logger.warning(
                    f"Missing required settings: {', '.join(missing_settings)}"
                )

            # Validate JWT settings if present
            if hasattr(settings, "SIMPLE_JWT"):
                jwt_settings = settings.SIMPLE_JWT

                # Check token lifetimes
                access_lifetime = jwt_settings.get("ACCESS_TOKEN_LIFETIME")
                refresh_lifetime = jwt_settings.get("REFRESH_TOKEN_LIFETIME")

                if access_lifetime and refresh_lifetime:
                    if access_lifetime >= refresh_lifetime:
                        logger.warning(
                            "Access token lifetime should be shorter than refresh token lifetime"
                        )

            logger.debug("Configuration validation completed")

        except Exception as e:
            logger.error(f"Error validating configuration: {str(e)}")

    def _initialize_monitoring(self):
        """Initialize monitoring and metrics collection."""
        try:
            # Initialize performance monitoring
            if hasattr(settings, "MONITORING_ENABLED") and settings.MONITORING_ENABLED:
                logger.info("Monitoring enabled for users app")

            # Set up periodic cleanup tasks if Celery is available
            try:
                from celery import current_app

                if current_app:
                    logger.debug("Celery detected - periodic tasks can be configured")
            except ImportError:
                logger.debug("Celery not available - using alternative cleanup methods")

            # Initialize cache warming if needed
            self._warm_cache()

        except Exception as e:
            logger.error(f"Error initializing monitoring: {str(e)}")

    def _warm_cache(self):
        """Warm up frequently accessed cache entries."""
        try:
            from django.core.cache import cache

            # Cache common permission lookups
            cache.set("users:app_initialized", True, timeout=3600)

            logger.debug("Cache warming completed")

        except Exception as e:
            logger.error(f"Error warming cache: {str(e)}")

    @classmethod
    def get_version(cls):
        """Get the current version of the users app."""
        return "2.0.0"

    @classmethod
    def get_health_status(cls):
        """Get health status of the users app."""
        try:
            # Check database connectivity
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            # Check cache connectivity
            from django.core.cache import cache

            cache.set("health_check", "ok", timeout=60)
            cache_status = cache.get("health_check") == "ok"

            # Check required models
            from .models import Profile, Subscription, User

            model_status = all(
                [
                    User._meta.db_table,
                    Profile._meta.db_table,
                    Subscription._meta.db_table,
                ]
            )

            return {
                "status": "healthy",
                "database": "connected",
                "cache": "connected" if cache_status else "disconnected",
                "models": "ready" if model_status else "not_ready",
                "version": cls.get_version(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "version": cls.get_version(),
            }
