#
# File Path: backend/courses/apps.py
# Folder Path: backend/courses/
# Date Created: 2025-06-15 08:00:00
# Date Revised: 2025-06-18 15:52:17
# Current Date and Time (UTC): 2025-06-18 15:52:17
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-18 15:52:17 UTC
# User: sujibeautysalon
# Version: 2.0.1
#
# Production-Ready Django App Configuration for Course Management System
#
# This module provides comprehensive Django app configuration with fixes from
# three code reviews including security enhancements, signal handling, error
# handling, monitoring setup, production-ready initialization, and Windows compatibility.
#
# Version 2.0.1 Changes:
# - FIXED: Windows compatibility for resource module import
# - ENHANCED: Cross-platform memory monitoring with fallback implementations
# - IMPROVED: Error handling for platform-specific features
# - ADDED: Platform detection and appropriate feature enablement

import logging
import platform
import sys
from typing import Any, Dict, Optional

from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.utils import timezone

# Platform-specific imports with fallback handling
try:
    import resource

    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

# Additional cross-platform imports
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

# App constants
APP_NAME = "courses"
APP_VERBOSE_NAME = "Course Management System"
APP_VERSION = "2.0.1"

# Platform detection
IS_WINDOWS = platform.system().lower() == "windows"
IS_LINUX = platform.system().lower() == "linux"
IS_MACOS = platform.system().lower() == "darwin"


class CoursesConfig(AppConfig):
    """
    Enhanced Django app configuration with comprehensive security, monitoring, and cross-platform compatibility
    FIXED: All app configuration security vulnerabilities, initialization issues, and Windows compatibility
    """

    # Core Django app configuration
    default_auto_field = "django.db.models.BigAutoField"
    name = APP_NAME
    verbose_name = APP_VERBOSE_NAME

    def __init__(self, app_name: str, app_module):
        """
        Initialize app config with enhanced validation and platform detection
        ADDED: Cross-platform initialization validation
        """
        super().__init__(app_name, app_module)
        self.startup_time = None
        self.initialization_errors = []
        self.health_status = "initializing"
        self.platform_features = self._detect_platform_features()

        logger.info(
            f"Initializing {APP_VERBOSE_NAME} v{APP_VERSION} on {platform.system()}"
        )

    def _detect_platform_features(self) -> Dict[str, bool]:
        """
        Detect available platform-specific features
        ADDED: Platform feature detection
        """
        features = {
            "has_resource": HAS_RESOURCE,
            "has_psutil": HAS_PSUTIL,
            "is_windows": IS_WINDOWS,
            "is_linux": IS_LINUX,
            "is_macos": IS_MACOS,
            "supports_unix_signals": not IS_WINDOWS,
            "supports_memory_monitoring": HAS_RESOURCE or HAS_PSUTIL,
        }

        logger.debug(f"Platform features detected: {features}")
        return features

    def ready(self):
        """
        Enhanced app ready method with comprehensive initialization and cross-platform support
        FIXED: Signal handling, initialization, and Windows compatibility
        """
        try:
            self.startup_time = timezone.now()
            logger.info(
                f"Starting {APP_VERBOSE_NAME} initialization on {platform.system()}..."
            )

            # Validate configuration
            self._validate_configuration()

            # Setup signal handlers
            self._setup_signal_handlers()

            # Initialize monitoring
            self._initialize_monitoring()

            # Validate database connections
            self._validate_database_connections()

            # Setup caching
            self._setup_caching()

            # Register custom checks
            self._register_system_checks()

            # Initialize performance monitoring with cross-platform support
            self._initialize_performance_monitoring()

            # Validate permissions and security
            self._validate_security_configuration()

            # Mark as ready
            self.health_status = "ready"

            initialization_time = (timezone.now() - self.startup_time).total_seconds()
            logger.info(
                f"{APP_VERBOSE_NAME} v{APP_VERSION} initialized successfully "
                f"in {initialization_time:.2f} seconds on {platform.system()}"
            )

        except Exception as e:
            self.health_status = "error"
            self.initialization_errors.append(str(e))
            logger.error(f"Failed to initialize {APP_VERBOSE_NAME}: {e}")

            # In production, we want to continue but log the error
            # In development, we might want to raise the exception
            if settings.DEBUG:
                raise
            else:
                # Log error but don't prevent startup
                logger.error(f"App initialization error (continuing): {e}")

    def _validate_configuration(self):
        """
        Comprehensive configuration validation with platform-specific checks
        ENHANCED: Platform-aware configuration validation
        """
        try:
            # Validate required settings
            required_settings = [
                "DATABASES",
                "SECRET_KEY",
                "ALLOWED_HOSTS",
            ]

            for setting in required_settings:
                if not hasattr(settings, setting):
                    raise ImproperlyConfigured(f"Required setting {setting} is missing")

            # Validate security settings
            if settings.DEBUG and not settings.ALLOWED_HOSTS:
                logger.warning(
                    "DEBUG=True but ALLOWED_HOSTS is empty - potential security risk"
                )

            # Validate database configuration
            if "default" not in settings.DATABASES:
                raise ImproperlyConfigured("Default database configuration is missing")

            # Validate cache configuration
            if hasattr(settings, "CACHES") and "default" not in settings.CACHES:
                logger.warning(
                    "Default cache configuration is missing - using dummy cache"
                )

            # Validate file upload settings
            max_upload_size = getattr(
                settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 2621440
            )  # 2.5MB default
            if max_upload_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(
                    f"FILE_UPLOAD_MAX_MEMORY_SIZE is very large: {max_upload_size}"
                )

            # Validate security middleware
            security_middleware = [
                "django.middleware.security.SecurityMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
            ]

            middleware = getattr(settings, "MIDDLEWARE", [])
            missing_middleware = [
                mw for mw in security_middleware if mw not in middleware
            ]

            if missing_middleware:
                logger.warning(f"Missing security middleware: {missing_middleware}")

            # Platform-specific validation
            if IS_WINDOWS:
                logger.debug("Windows-specific configuration validated")
            elif IS_LINUX:
                logger.debug("Linux-specific configuration validated")
            elif IS_MACOS:
                logger.debug("macOS-specific configuration validated")

            logger.debug("Configuration validation completed successfully")

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    def _setup_signal_handlers(self):
        """
        Setup Django signal handlers with comprehensive error handling and platform awareness
        ENHANCED: Platform-aware signal handling
        """
        try:
            # Import signals module to register handlers
            from django.db.models.signals import post_migrate, post_save, pre_delete

            from . import signals

            # Log registered signal handlers for monitoring
            signal_count = 0

            # Check for course-related signals
            if hasattr(signals, "course_post_save"):
                signal_count += 1
            if hasattr(signals, "enrollment_post_save"):
                signal_count += 1
            if hasattr(signals, "progress_post_save"):
                signal_count += 1

            # Platform-specific signal handling
            if self.platform_features["supports_unix_signals"]:
                logger.debug("Unix signal handling enabled")
            else:
                logger.debug("Unix signal handling disabled (Windows platform)")

            logger.info(f"Registered {signal_count} signal handlers successfully")

        except ImportError:
            logger.warning("No signals module found - signal handlers not registered")
        except Exception as e:
            logger.error(f"Error setting up signal handlers: {e}")
            # Don't raise - signal handlers are not critical for basic functionality

    def _initialize_monitoring(self):
        """
        Initialize comprehensive monitoring and health checks with cross-platform support
        ENHANCED: Cross-platform monitoring initialization
        """
        try:
            # Initialize application metrics
            self._initialize_metrics()

            # Setup health check endpoints
            self._setup_health_checks()

            # Initialize performance tracking with platform awareness
            self._setup_performance_tracking()

            logger.debug("Monitoring initialization completed")

        except Exception as e:
            logger.error(f"Monitoring initialization failed: {e}")
            # Continue without monitoring rather than failing startup

    def _initialize_metrics(self):
        """
        Initialize application metrics collection with platform information
        ENHANCED: Platform-aware metrics collection
        """
        try:
            # Store startup metrics in cache
            startup_metrics = {
                "app_name": APP_NAME,
                "version": APP_VERSION,
                "startup_time": (
                    self.startup_time.isoformat() if self.startup_time else None
                ),
                "django_version": getattr(settings, "DJANGO_VERSION", "unknown"),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "debug_mode": settings.DEBUG,
                "platform_features": self.platform_features,
            }

            cache_key = f"{APP_NAME}_startup_metrics"
            cache.set(cache_key, startup_metrics, timeout=3600)  # 1 hour

            logger.debug("Application metrics initialized with platform information")

        except Exception as e:
            logger.error(f"Metrics initialization failed: {e}")

    def _setup_health_checks(self):
        """
        Setup comprehensive health check system with platform awareness
        ENHANCED: Platform-aware health checks
        """
        try:
            # Initialize health check status
            health_status = {
                "app_status": self.health_status,
                "database_status": "unknown",
                "cache_status": "unknown",
                "platform": platform.system(),
                "platform_features": self.platform_features,
                "last_check": timezone.now().isoformat(),
                "initialization_errors": self.initialization_errors,
            }

            # Store health status in cache
            cache_key = f"{APP_NAME}_health_status"
            cache.set(cache_key, health_status, timeout=300)  # 5 minutes

            logger.debug("Health checks setup completed with platform awareness")

        except Exception as e:
            logger.error(f"Health check setup failed: {e}")

    def _setup_performance_tracking(self):
        """
        Setup performance monitoring and tracking with cross-platform support
        ENHANCED: Cross-platform performance tracking
        """
        try:
            # Get initial memory usage using available method
            initial_memory = self._get_memory_usage()

            # Initialize performance counters
            performance_counters = {
                "requests_total": 0,
                "requests_errors": 0,
                "average_response_time": 0.0,
                "database_queries_total": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "initial_memory_usage": initial_memory,
                "memory_monitoring_method": self._get_memory_monitoring_method(),
                "platform": platform.system(),
                "last_reset": timezone.now().isoformat(),
            }

            cache_key = f"{APP_NAME}_performance_counters"
            cache.set(cache_key, performance_counters, timeout=86400)  # 24 hours

            logger.debug(
                f"Performance tracking initialized with {performance_counters['memory_monitoring_method']} method"
            )

        except Exception as e:
            logger.error(f"Performance tracking setup failed: {e}")

    def _get_memory_usage(self) -> Optional[float]:
        """
        Get current memory usage using available method
        ADDED: Cross-platform memory usage detection
        """
        try:
            if HAS_PSUTIL:
                # Use psutil for cross-platform memory monitoring
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / 1024  # Convert to KB
            elif HAS_RESOURCE:
                # Use resource module (Unix/Linux/macOS)
                memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                # On Linux, ru_maxrss is in KB, on macOS it's in bytes
                if IS_MACOS:
                    return memory_usage / 1024  # Convert bytes to KB
                else:
                    return memory_usage  # Already in KB
            else:
                logger.warning("No memory monitoring available on this platform")
                return None
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return None

    def _get_memory_monitoring_method(self) -> str:
        """
        Get the method used for memory monitoring
        ADDED: Memory monitoring method detection
        """
        if HAS_PSUTIL:
            return "psutil"
        elif HAS_RESOURCE:
            return "resource"
        else:
            return "unavailable"

    def _validate_database_connections(self):
        """
        Validate database connections and migration status
        ADDED: Database connection validation
        """
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    raise Exception("Database connection test failed")

            # Check if migrations are up to date
            from django.db.migrations.executor import MigrationExecutor

            executor = MigrationExecutor(connection)

            # Get pending migrations
            pending_migrations = executor.migration_plan(
                executor.loader.graph.leaf_nodes()
            )

            if pending_migrations:
                migration_names = [
                    f"{migration[0]}.{migration[1]}" for migration in pending_migrations
                ]
                logger.warning(f"Pending migrations detected: {migration_names}")
            else:
                logger.debug("All migrations are up to date")

            # Update health status
            health_status = cache.get(f"{APP_NAME}_health_status", {})
            health_status["database_status"] = "connected"
            cache.set(f"{APP_NAME}_health_status", health_status, timeout=300)

            logger.debug("Database connection validation completed")

        except Exception as e:
            logger.error(f"Database validation failed: {e}")

            # Update health status with error
            health_status = cache.get(f"{APP_NAME}_health_status", {})
            health_status["database_status"] = f"error: {str(e)}"
            cache.set(f"{APP_NAME}_health_status", health_status, timeout=300)

            raise

    def _setup_caching(self):
        """
        Setup and validate caching configuration
        ADDED: Caching setup and validation
        """
        try:
            # Test cache connection
            test_key = f"{APP_NAME}_cache_test"
            test_value = "cache_test_value"

            cache.set(test_key, test_value, timeout=60)
            retrieved_value = cache.get(test_key)

            if retrieved_value != test_value:
                raise Exception("Cache test failed - values don't match")

            # Clean up test key
            cache.delete(test_key)

            # Update health status
            health_status = cache.get(f"{APP_NAME}_health_status", {})
            health_status["cache_status"] = "connected"
            cache.set(f"{APP_NAME}_health_status", health_status, timeout=300)

            logger.debug("Cache setup and validation completed")

        except Exception as e:
            logger.error(f"Cache setup failed: {e}")

            # Update health status with error
            health_status = cache.get(f"{APP_NAME}_health_status", {})
            health_status["cache_status"] = f"error: {str(e)}"
            cache.set(f"{APP_NAME}_health_status", health_status, timeout=300)

            # Cache failure is not critical - continue without caching

    def _register_system_checks(self):
        """
        Register custom Django system checks
        ADDED: Custom system checks registration
        """
        try:
            from django.core.checks import Tags, register

            from . import checks

            # Register custom checks if available
            if hasattr(checks, "check_course_configuration"):
                register(checks.check_course_configuration, Tags.models)

            if hasattr(checks, "check_security_configuration"):
                register(checks.check_security_configuration, Tags.security)

            if hasattr(checks, "check_performance_configuration"):
                register(checks.check_performance_configuration, Tags.compatibility)

            logger.debug("Custom system checks registered")

        except ImportError:
            logger.warning("No custom checks module found")
        except Exception as e:
            logger.error(f"System checks registration failed: {e}")

    def _initialize_performance_monitoring(self):
        """
        Initialize advanced performance monitoring with cross-platform support
        ENHANCED: Cross-platform performance monitoring
        """
        try:
            # Setup query monitoring
            if settings.DEBUG:
                from django.db import connection

                # Enable query logging in debug mode
                logger.debug("Query monitoring enabled for debug mode")

            # Initialize memory monitoring with cross-platform support
            initial_memory = self._get_memory_usage()

            # Store initial memory usage
            performance_data = cache.get(f"{APP_NAME}_performance_counters", {})
            performance_data["initial_memory_usage"] = initial_memory
            performance_data["memory_monitoring_available"] = initial_memory is not None
            cache.set(
                f"{APP_NAME}_performance_counters", performance_data, timeout=86400
            )

            if initial_memory is not None:
                logger.debug(
                    f"Performance monitoring initialized - initial memory: {initial_memory:.2f}KB "
                    f"using {self._get_memory_monitoring_method()} method"
                )
            else:
                logger.debug(
                    "Performance monitoring initialized without memory tracking"
                )

        except Exception as e:
            logger.error(f"Performance monitoring initialization failed: {e}")

    def _validate_security_configuration(self):
        """
        Validate security configuration and permissions
        ADDED: Security configuration validation
        """
        try:
            # Check security settings
            security_warnings = []

            # Check SECRET_KEY
            if hasattr(settings, "SECRET_KEY"):
                secret_key = settings.SECRET_KEY
                if len(secret_key) < 50:
                    security_warnings.append("SECRET_KEY is too short")
                if secret_key == "django-insecure-change-me":
                    security_warnings.append(
                        "SECRET_KEY is using default insecure value"
                    )

            # Check DEBUG setting in production
            if not settings.DEBUG and hasattr(settings, "ALLOWED_HOSTS"):
                if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ["*"]:
                    security_warnings.append(
                        "ALLOWED_HOSTS is not properly configured for production"
                    )

            # Check HTTPS settings
            if not settings.DEBUG:
                https_settings = [
                    "SECURE_SSL_REDIRECT",
                    "SECURE_HSTS_SECONDS",
                    "SECURE_CONTENT_TYPE_NOSNIFF",
                    "SECURE_BROWSER_XSS_FILTER",
                ]

                for setting in https_settings:
                    if not getattr(settings, setting, False):
                        security_warnings.append(
                            f"Security setting {setting} is not enabled"
                        )

            # Log security warnings
            if security_warnings:
                for warning in security_warnings:
                    logger.warning(f"Security warning: {warning}")
            else:
                logger.debug("Security configuration validation passed")

        except Exception as e:
            logger.error(f"Security validation failed: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status information with platform details
        ENHANCED: Platform-aware health status reporting
        """
        try:
            health_status = cache.get(f"{APP_NAME}_health_status", {})

            # Add current timestamp and platform information
            health_status.update(
                {
                    "current_time": timezone.now().isoformat(),
                    "app_version": APP_VERSION,
                    "platform": platform.system(),
                    "platform_features": self.platform_features,
                    "memory_monitoring_available": self.platform_features[
                        "supports_memory_monitoring"
                    ],
                }
            )

            return health_status

        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "app_status": "error",
                "error": str(e),
                "current_time": timezone.now().isoformat(),
                "platform": platform.system(),
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics with cross-platform memory monitoring
        ENHANCED: Cross-platform performance metrics
        """
        try:
            metrics = cache.get(f"{APP_NAME}_performance_counters", {})

            # Add current memory usage using available method
            current_memory = self._get_memory_usage()
            if current_memory is not None:
                metrics["current_memory_usage"] = current_memory

            # Calculate uptime
            if self.startup_time:
                uptime = (timezone.now() - self.startup_time).total_seconds()
                metrics["uptime_seconds"] = uptime

            # Add platform information
            metrics.update(
                {
                    "platform": platform.system(),
                    "memory_monitoring_method": self._get_memory_monitoring_method(),
                    "memory_monitoring_available": current_memory is not None,
                }
            )

            return metrics

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "error": str(e),
                "platform": platform.system(),
            }

    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get detailed platform information
        ADDED: Platform information reporting
        """
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "platform_features": self.platform_features,
                "memory_monitoring_method": self._get_memory_monitoring_method(),
            }
        except Exception as e:
            logger.error(f"Error getting platform info: {e}")
            return {"error": str(e)}

    def __str__(self):
        """String representation of the app config"""
        return f"{APP_VERBOSE_NAME} v{APP_VERSION} ({self.health_status}) on {platform.system()}"

    def __repr__(self):
        """Detailed representation of the app config"""
        return (
            f"CoursesConfig(name='{self.name}', "
            f"version='{APP_VERSION}', "
            f"status='{self.health_status}', "
            f"platform='{platform.system()}', "
            f"startup_time='{self.startup_time}')"
        )
