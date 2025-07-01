# File Path: instructor_portal/models/maintenance.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-27 04:03:52
# Date Revised: 2025-06-27 04:03:52
# Current Date and Time (UTC): 2025-06-27 04:03:52
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 04:03:52 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Maintenance utilities - Cleanup and system health checks
# Restored from original models.py to maintain backward compatibility

import logging
from typing import Dict, Any, List
from django.db import models, connection
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.cache import cache

from .creation import CourseCreationSession
from .analytics import InstructorAnalyticsHistory
from .profile import InstructorProfile
from .security import InstructorSession

logger = logging.getLogger(__name__)


class InstructorPortalCleanup:
    """Utility class for cleanup operations"""

    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """Clean up expired course creation sessions"""
        try:
            cutoff_date = timezone.now()
            expired_sessions = CourseCreationSession.objects.filter(
                expires_at__lt=cutoff_date,
                status__in=[
                    CourseCreationSession.Status.DRAFT,
                    CourseCreationSession.Status.IN_PROGRESS,
                    CourseCreationSession.Status.PAUSED,
                    CourseCreationSession.Status.ABANDONED
                ]
            )

            count = expired_sessions.count()
            if count > 0:
                expired_sessions.delete()
                logger.info(f"Cleaned up {count} expired course creation sessions")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    @classmethod
    def cleanup_old_analytics_history(cls) -> int:
        """Clean up old analytics history based on tier limits"""
        try:
            total_cleaned = 0

            for tier_name, tier_data in InstructorProfile.objects.values('tier').annotate(
                count=models.Count('id')).filter(count__gt=0).values_list('tier', flat=True).distinct():

                from .utils import TierManager
                days_to_keep = TierManager.get_tier_limits(tier_name)['analytics_history_days']
                cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)

                # Get instructors with this tier
                instructors = InstructorProfile.objects.filter(tier=tier_name)

                for instructor in instructors:
                    deleted_count = InstructorAnalyticsHistory.objects.filter(
                        instructor=instructor,
                        date__lt=cutoff_date
                    ).delete()[0]
                    total_cleaned += deleted_count

            logger.info(f"Cleaned up {total_cleaned} old analytics history records")
            return total_cleaned

        except Exception as e:
            logger.error(f"Error cleaning up analytics history: {e}")
            return 0

    @classmethod
    def refresh_all_instructor_analytics(cls) -> int:
        """Refresh analytics for all active instructors"""
        try:
            active_instructors = InstructorProfile.objects.filter(
                status=InstructorProfile.Status.ACTIVE
            ).select_related('analytics')

            updated_count = 0
            for instructor in active_instructors:
                try:
                    if instructor.analytics.update_analytics(force=True):
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating analytics for instructor {instructor.id}: {e}")
                    continue

            logger.info(f"Updated analytics for {updated_count} instructors")
            return updated_count

        except Exception as e:
            logger.error(f"Error refreshing instructor analytics: {e}")
            return 0

    @classmethod
    def cleanup_orphaned_files(cls) -> int:
        """Clean up orphaned files not linked to any database records"""
        try:
            deleted_count = 0

            # Get all instructor profile image paths from database
            profile_image_paths = set(
                InstructorProfile.objects.exclude(profile_image='')
                .values_list('profile_image', flat=True)
            )

            cover_image_paths = set(
                InstructorProfile.objects.exclude(cover_image='')
                .values_list('cover_image', flat=True)
            )

            # Combine all valid paths
            valid_paths = profile_image_paths.union(cover_image_paths)

            # Check for orphaned files in storage
            storage_dirs = ['instructor_profiles', 'instructor_covers']

            for storage_dir in storage_dirs:
                try:
                    if default_storage.exists(storage_dir):
                        # List all files in the directory
                        dirs, files = default_storage.listdir(storage_dir)

                        # Check subdirectories (sharded paths)
                        for subdir in dirs:
                            subdir_path = f"{storage_dir}/{subdir}"
                            if default_storage.exists(subdir_path):
                                _, subfiles = default_storage.listdir(subdir_path)

                                for file in subfiles:
                                    file_path = f"{storage_dir}/{subdir}/{file}"

                                    # If file not in valid paths, it's orphaned
                                    if file_path not in valid_paths:
                                        try:
                                            default_storage.delete(file_path)
                                            deleted_count += 1
                                            logger.debug(f"Deleted orphaned file: {file_path}")
                                        except Exception as e:
                                            logger.error(f"Error deleting orphaned file {file_path}: {e}")

                        # Check files in root directory
                        for file in files:
                            file_path = f"{storage_dir}/{file}"
                            if file_path not in valid_paths:
                                try:
                                    default_storage.delete(file_path)
                                    deleted_count += 1
                                    logger.debug(f"Deleted orphaned file: {file_path}")
                                except Exception as e:
                                    logger.error(f"Error deleting orphaned file {file_path}: {e}")

                except Exception as e:
                    logger.error(f"Error processing storage directory {storage_dir}: {e}")
                    continue

            logger.info(f"Cleaned up {deleted_count} orphaned files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}")
            return 0


class InstructorPortalSystemHealth:
    """
    System health monitoring and maintenance utilities
    ADDED: Comprehensive system health monitoring for instructor portal
    """

    @classmethod
    def run_health_check(cls) -> Dict[str, Any]:
        """Run comprehensive health check on instructor portal"""
        health_report = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        try:
            # Database connectivity check
            health_report['checks']['database'] = cls._check_database_health()

            # Cache connectivity check
            health_report['checks']['cache'] = cls._check_cache_health()

            # File storage check
            health_report['checks']['storage'] = cls._check_storage_health()

            # Data integrity checks
            health_report['checks']['data_integrity'] = cls._check_data_integrity()

            # Performance metrics
            health_report['checks']['performance'] = cls._check_performance_metrics()

            # Determine overall status
            failed_checks = [check for check in health_report['checks'].values() if not check['status']]
            if failed_checks:
                health_report['overall_status'] = 'degraded' if len(failed_checks) == 1 else 'unhealthy'

            logger.info(f"Health check completed - Status: {health_report['overall_status']}")
            return health_report

        except Exception as e:
            logger.error(f"Error running health check: {e}")
            health_report['overall_status'] = 'error'
            health_report['error'] = str(e)
            return health_report

    @staticmethod
    def _check_database_health() -> Dict[str, Any]:
        """Check database connectivity and basic operations"""
        try:
            # Test basic database operations
            count = InstructorProfile.objects.count()
            analytics_count = InstructorProfile.objects.filter(analytics__isnull=False).count()

            return {
                'status': True,
                'message': 'Database is accessible',
                'details': {
                    'instructor_profiles': count,
                    'analytics_records': analytics_count
                }
            }
        except Exception as e:
            return {
                'status': False,
                'message': f'Database check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_cache_health() -> Dict[str, Any]:
        """Check cache connectivity and operations"""
        try:
            # Test cache operations
            test_key = 'health_check_test'
            test_value = 'test_data'

            cache.set(test_key, test_value, timeout=60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)

            if retrieved_value == test_value:
                return {
                    'status': True,
                    'message': 'Cache is working properly',
                    'details': {}
                }
            else:
                return {
                    'status': False,
                    'message': 'Cache test failed - value mismatch',
                    'details': {}
                }

        except Exception as e:
            return {
                'status': False,
                'message': f'Cache check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_storage_health() -> Dict[str, Any]:
        """Check file storage accessibility"""
        try:
            # Test storage operations
            test_filename = 'health_check_test.txt'
            test_content = b'Health check test file'

            # Save test file
            from django.core.files.base import ContentFile
            test_file = ContentFile(test_content)
            saved_path = default_storage.save(test_filename, test_file)

            # Verify file exists
            if default_storage.exists(saved_path):
                # Clean up test file
                default_storage.delete(saved_path)

                return {
                    'status': True,
                    'message': 'Storage is accessible',
                    'details': {}
                }
            else:
                return {
                    'status': False,
                    'message': 'Storage test failed - file not found after save',
                    'details': {}
                }

        except Exception as e:
            return {
                'status': False,
                'message': f'Storage check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_data_integrity() -> Dict[str, Any]:
        """Check data integrity across related models"""
        try:
            issues = []

            # Check for instructors without analytics
            instructors_without_analytics = InstructorProfile.objects.filter(
                analytics__isnull=True
            ).count()

            if instructors_without_analytics > 0:
                issues.append(f'{instructors_without_analytics} instructors without analytics records')

            # Check for orphaned sessions
            expired_sessions = CourseCreationSession.objects.filter(
                expires_at__lt=timezone.now(),
                status__in=['draft', 'paused']
            ).count()

            if expired_sessions > 10:  # Threshold for concern
                issues.append(f'{expired_sessions} expired sessions need cleanup')

            # Check for inconsistent analytics
            from .analytics import InstructorAnalytics
            inconsistent_analytics = InstructorAnalytics.objects.filter(
                total_courses__gt=0,
                total_students=0
            ).count()

            if inconsistent_analytics > 0:
                issues.append(f'{inconsistent_analytics} analytics records with inconsistent data')

            return {
                'status': len(issues) == 0,
                'message': 'Data integrity check completed' if len(issues) == 0 else f'Found {len(issues)} issues',
                'details': {'issues': issues}
            }

        except Exception as e:
            return {
                'status': False,
                'message': f'Data integrity check failed: {str(e)}',
                'details': {}
            }

    @staticmethod
    def _check_performance_metrics() -> Dict[str, Any]:
        """Check system performance metrics"""
        try:
            # Get query count
            query_count = len(connection.queries) if hasattr(connection, 'queries') else 0

            # Check for slow operations (simplified)
            from .analytics import InstructorAnalytics
            slow_analytics_updates = InstructorAnalytics.objects.filter(
                last_calculated__lt=timezone.now() - timezone.timedelta(hours=24)
            ).count()

            return {
                'status': slow_analytics_updates < 10,  # Threshold
                'message': 'Performance check completed',
                'details': {
                    'query_count': query_count,
                    'stale_analytics': slow_analytics_updates
                }
            }

        except Exception as e:
            return {
                'status': False,
                'message': f'Performance check failed: {str(e)}',
                'details': {}
            }

    @classmethod
    def run_maintenance_tasks(cls) -> Dict[str, Any]:
        """Run routine maintenance tasks"""
        maintenance_report = {
            'timestamp': timezone.now().isoformat(),
            'tasks_completed': {}
        }

        try:
            # Clean up expired sessions
            expired_sessions = InstructorPortalCleanup.cleanup_expired_sessions()
            maintenance_report['tasks_completed']['expired_sessions_cleanup'] = expired_sessions

            # Clean up old analytics history
            old_analytics = InstructorPortalCleanup.cleanup_old_analytics_history()
            maintenance_report['tasks_completed']['analytics_history_cleanup'] = old_analytics

            # Clean up expired notifications
            from .notifications import InstructorNotification
            expired_notifications = InstructorNotification.cleanup_expired_notifications()
            maintenance_report['tasks_completed']['notifications_cleanup'] = expired_notifications

            # Clean up old instructor sessions
            old_sessions = InstructorSession.cleanup_expired_sessions()
            maintenance_report['tasks_completed']['instructor_sessions_cleanup'] = old_sessions

            # Clean up orphaned files
            orphaned_files = InstructorPortalCleanup.cleanup_orphaned_files()
            maintenance_report['tasks_completed']['orphaned_files_cleanup'] = orphaned_files

            # Detect suspicious activity
            suspicious_sessions = InstructorSession.detect_suspicious_activity()
            maintenance_report['tasks_completed']['suspicious_activity_detection'] = len(suspicious_sessions)

            logger.info(f"Maintenance tasks completed: {maintenance_report}")
            return maintenance_report

        except Exception as e:
            logger.error(f"Error running maintenance tasks: {e}")
            maintenance_report['error'] = str(e)
            return maintenance_report
