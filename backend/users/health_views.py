"""
File: backend/users/health_views.py
Purpose: Health check and monitoring endpoints
Date Created: 2025-07-15 00:00:00 UTC
Version: 1.1.0 - Enhanced Monitoring and Health Checks

PROVIDES:
- Health check endpoint for load balancers
- Metrics endpoint for monitoring systems
- Database connectivity checks
- Cache health validation
- Performance metrics
"""

import logging
import time
from datetime import timedelta
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .apps import UsersConfig
from .models import LoginLog, Subscription, UserSession
from .permissions import IsPlatformAdmin

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()


class UserHealthCheckView(APIView):
    """
    Health check endpoint for users app.
    Used by load balancers and monitoring systems.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return health status of users app."""
        try:
            start_time = time.time()

            health_data = UsersConfig.get_health_status()

            # Add timing information
            health_data["response_time_ms"] = round(
                (time.time() - start_time) * 1000, 2
            )
            health_data["timestamp"] = timezone.now().isoformat()
            health_data["service"] = "users"

            # Determine HTTP status based on health
            http_status = (
                status.HTTP_200_OK
                if health_data["status"] == "healthy"
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )

            logger.info(f"Health check completed: {health_data['status']}")
            return Response(health_data, status=http_status)

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": timezone.now().isoformat(),
                    "service": "users",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class UserMetricsView(APIView):
    """
    Metrics endpoint for monitoring systems.
    Provides operational metrics for the users app.
    """

    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        """Return operational metrics."""
        try:
            start_time = time.time()

            # Gather metrics
            metrics = self._gather_metrics()

            # Add meta information
            metrics["collection_time_ms"] = round((time.time() - start_time) * 1000, 2)
            metrics["timestamp"] = timezone.now().isoformat()

            logger.info("Metrics collected successfully")
            return Response(metrics, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Metrics collection failed: {str(e)}")
            return Response(
                {
                    "error": str(e),
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _gather_metrics(self) -> Dict[str, Any]:
        """Gather various operational metrics."""
        now = timezone.now()

        # User metrics
        user_metrics = self._get_user_metrics(now)

        # Session metrics
        session_metrics = self._get_session_metrics(now)

        # Authentication metrics
        auth_metrics = self._get_auth_metrics(now)

        # Subscription metrics
        subscription_metrics = self._get_subscription_metrics()

        # System metrics
        system_metrics = self._get_system_metrics()

        return {
            "users": user_metrics,
            "sessions": session_metrics,
            "authentication": auth_metrics,
            "subscriptions": subscription_metrics,
            "system": system_metrics,
        }

    def _get_user_metrics(self, now) -> Dict[str, Any]:
        """Get user-related metrics."""
        try:
            return {
                "total_users": User.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "verified_users": User.objects.filter(is_email_verified=True).count(),
                "new_users_today": User.objects.filter(
                    date_joined__date=now.date()
                ).count(),
                "new_users_this_week": User.objects.filter(
                    date_joined__gte=now - timedelta(days=7)
                ).count(),
                "users_by_role": {
                    role[0]: User.objects.filter(role=role[0]).count()
                    for role in User.USER_ROLES
                },
            }
        except Exception as e:
            logger.error(f"Error gathering user metrics: {str(e)}")
            return {"error": str(e)}

    def _get_session_metrics(self, now) -> Dict[str, Any]:
        """Get session-related metrics."""
        try:
            active_sessions = UserSession.objects.filter(is_active=True)

            return {
                "total_active_sessions": active_sessions.count(),
                "sessions_by_device": {
                    device: active_sessions.filter(device_type=device).count()
                    for device in ["Desktop", "Mobile", "Tablet", "Unknown"]
                },
                "sessions_created_today": UserSession.objects.filter(
                    created_at__date=now.date()
                ).count(),
                "average_session_duration_hours": self._calculate_avg_session_duration(),
            }
        except Exception as e:
            logger.error(f"Error gathering session metrics: {str(e)}")
            return {"error": str(e)}

    def _get_auth_metrics(self, now) -> Dict[str, Any]:
        """Get authentication-related metrics."""
        try:
            today_logins = LoginLog.objects.filter(timestamp__date=now.date())

            return {
                "logins_today": today_logins.count(),
                "successful_logins_today": today_logins.filter(successful=True).count(),
                "failed_logins_today": today_logins.filter(successful=False).count(),
                "success_rate_today": self._calculate_success_rate(today_logins),
                "locked_accounts": User.objects.filter(ban_expires_at__gt=now).count(),
            }
        except Exception as e:
            logger.error(f"Error gathering auth metrics: {str(e)}")
            return {"error": str(e)}

    def _get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription-related metrics."""
        try:
            subscriptions = Subscription.objects.all()

            return {
                "total_subscriptions": subscriptions.count(),
                "active_subscriptions": subscriptions.filter(status="active").count(),
                "subscriptions_by_tier": {
                    tier[0]: subscriptions.filter(tier=tier[0]).count()
                    for tier in Subscription.SUBSCRIPTION_TIERS
                },
                "subscriptions_by_status": {
                    status_choice[0]: subscriptions.filter(
                        status=status_choice[0]
                    ).count()
                    for status_choice in Subscription.STATUS_CHOICES
                },
                "auto_renew_enabled": subscriptions.filter(is_auto_renew=True).count(),
            }
        except Exception as e:
            logger.error(f"Error gathering subscription metrics: {str(e)}")
            return {"error": str(e)}

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-related metrics."""
        try:
            # Database query performance
            db_start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_session")
                db_query_time = round((time.time() - db_start) * 1000, 2)

            # Cache performance
            cache_start = time.time()
            cache.set("metrics_test", "test", 1)
            cache.get("metrics_test")
            cache_query_time = round((time.time() - cache_start) * 1000, 2)

            return {
                "app_version": UsersConfig.get_version(),
                "database_query_time_ms": db_query_time,
                "cache_query_time_ms": cache_query_time,
                "cache_status": "healthy" if cache_query_time < 100 else "slow",
            }
        except Exception as e:
            logger.error(f"Error gathering system metrics: {str(e)}")
            return {"error": str(e)}

    def _calculate_avg_session_duration(self) -> float:
        """Calculate average session duration in hours."""
        try:
            active_sessions = UserSession.objects.filter(is_active=True)
            if not active_sessions.exists():
                return 0.0

            total_duration = sum(
                [
                    (timezone.now() - session.created_at).total_seconds()
                    for session in active_sessions
                ]
            )

            avg_seconds = total_duration / active_sessions.count()
            return round(avg_seconds / 3600, 2)  # Convert to hours

        except Exception:
            return 0.0

    def _calculate_success_rate(self, login_logs) -> float:
        """Calculate login success rate as percentage."""
        try:
            total = login_logs.count()
            if total == 0:
                return 0.0

            successful = login_logs.filter(successful=True).count()
            return round((successful / total) * 100, 2)

        except Exception:
            return 0.0


class DatabaseHealthView(APIView):
    """
    Specific database health check endpoint.
    Tests database connectivity and performance.
    """

    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        """Check database health."""
        try:
            start_time = time.time()

            # Test basic connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            # Test query performance
            query_start = time.time()
            User.objects.count()
            query_time = round((time.time() - query_start) * 1000, 2)

            total_time = round((time.time() - start_time) * 1000, 2)

            logger.info(f"Database health check passed in {total_time}ms")
            return Response(
                {
                    "status": "healthy",
                    "database": "healthy",
                    "connection": "ok",
                    "query_test": result[0] == 1,
                    "query_time_ms": query_time,
                    "total_time_ms": total_time,
                    "timestamp": timezone.now().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return Response(
                {
                    "status": "unhealthy",
                    "database": "unhealthy",
                    "error": str(e),
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class CacheHealthView(APIView):
    """
    Specific cache health check endpoint.
    Tests cache connectivity and performance.
    """

    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        """Check cache health."""
        try:
            start_time = time.time()

            # Test cache set/get
            test_key = f"health_check_{int(time.time())}"
            test_value = "cache_test"

            cache.set(test_key, test_value, timeout=60)
            retrieved_value = cache.get(test_key)

            # Clean up
            cache.delete(test_key)

            total_time = round((time.time() - start_time) * 1000, 2)
            is_healthy = retrieved_value == test_value

            if is_healthy:
                logger.info(f"Cache health check passed in {total_time}ms")
            else:
                logger.warning(f"Cache health check failed: value mismatch")

            return Response(
                {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "cache": "healthy" if is_healthy else "unhealthy",
                    "set_get_test": is_healthy,
                    "response_time_ms": total_time,
                    "timestamp": timezone.now().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return Response(
                {
                    "status": "unhealthy",
                    "cache": "unhealthy",
                    "error": str(e),
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
