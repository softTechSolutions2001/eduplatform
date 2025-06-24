#
# File Path: instructor_portal/tasks.py
# Integrated Instructor Portal Tasks
# Version: 3.0.0 - Unified & Optimized
# Date: 2025-06-19
#
# Combines course operations, maintenance, and analytics in a lean, secure framework

import logging
import json
import uuid
import time
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from decimal import Decimal

from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

# Flexible task backend imports
try:
    from celery import shared_task, Task
    from celery.exceptions import Retry, WorkerLostError
    CELERY_AVAILABLE = True
except ImportError:
    try:
        from django_background_tasks import background as shared_task
        CELERY_AVAILABLE = False
        Task = object
    except ImportError:
        CELERY_AVAILABLE = False
        shared_task = None
        Task = object

logger = logging.getLogger(__name__)
User = get_user_model()

# Unified configuration
CONFIG = {
    'MAX_IMPORT_SIZE': 50 * 1024 * 1024,  # 50MB
    'MAX_PROCESSING_TIME': 3600,  # 1 hour
    'MAX_RETRIES': 3,
    'RETRY_BACKOFF': 60,
    'BATCH_SIZE': 100,
    'TASK_LOCK_TIMEOUT': 3600,
    'ALLOWED_FORMATS': {'json', 'csv', 'xml'},
    'MAX_STORAGE_KEY_LENGTH': 500,
    'AUDIT_LOG_MAX_SIZE': 1000
}

# ====================================
# CORE UTILITIES
# ====================================

def audit_log(task_name: str, action: str, user_id: Optional[int] = None,
              metadata: Optional[Dict] = None):
    """Lean audit logging with size limits"""
    try:
        log_data = {
            'task': task_name,
            'action': action,
            'user_id': user_id,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }

        # Truncate large metadata
        log_str = json.dumps(log_data)
        if len(log_str) > CONFIG['AUDIT_LOG_MAX_SIZE']:
            log_data['metadata'] = {'truncated': True, 'size': len(log_str)}

        logger.info(f"TASK_AUDIT: {json.dumps(log_data)}")
    except Exception as e:
        logger.error(f"Audit log failed: {e}")

def validate_params(**kwargs) -> Dict[str, Any]:
    """Streamlined parameter validation"""
    validated = {}

    for key, value in kwargs.items():
        if key.endswith('_id') and value is not None:
            validated[key] = int(value)
            if validated[key] <= 0:
                raise ValueError(f"Invalid {key}: must be positive")

        elif key == 'storage_key' and value:
            key_str = str(value).strip()
            if len(key_str) > CONFIG['MAX_STORAGE_KEY_LENGTH'] or '..' in key_str:
                raise ValueError(f"Invalid storage_key")
            validated[key] = key_str

        elif key == 'format' and value:
            fmt = str(value).lower()
            if fmt not in CONFIG['ALLOWED_FORMATS']:
                raise ValueError(f"Unsupported format: {fmt}")
            validated[key] = fmt
        else:
            validated[key] = value

    return validated

def check_permissions(user_id: int, permission: str = 'instructor') -> bool:
    """Fast permission check"""
    try:
        user = User.objects.select_related().get(id=user_id)
        if user.is_staff or user.is_superuser:
            return True

        # Check role or instructor status
        if hasattr(user, 'role') and user.role in ['administrator', 'instructor']:
            return True

        if permission == 'instructor':
            return user.courseinstructor_set.filter(is_active=True).exists()

        return False
    except User.DoesNotExist:
        return False

def task_lock(name: str, timeout: int = None):
    """Distributed task locking decorator"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"task_lock:{name}"
            lock_timeout = timeout or CONFIG['TASK_LOCK_TIMEOUT']

            if cache.add(lock_key, True, lock_timeout):
                try:
                    return func(*args, **kwargs)
                finally:
                    cache.delete(lock_key)
            else:
                logger.info(f"Task {name} already running - skipped")
                return {'status': 'skipped', 'reason': 'already_running'}
        return wrapper
    return decorator

# ====================================
# UNIFIED BASE TASK
# ====================================

class UnifiedTask(Task if CELERY_AVAILABLE else object):
    """Unified base task with essential features"""

    autoretry_for = (Exception,) if CELERY_AVAILABLE else ()
    retry_kwargs = {'max_retries': CONFIG['MAX_RETRIES'], 'countdown': CONFIG['RETRY_BACKOFF']}
    soft_time_limit = CONFIG['MAX_PROCESSING_TIME']

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        audit_log(self.name, 'failed', kwargs.get('user_id'), {
            'task_id': task_id, 'error': str(exc)[:200]
        })

    def on_success(self, retval, task_id, args, kwargs):
        audit_log(self.name, 'completed', kwargs.get('user_id'), {
            'task_id': task_id, 'status': retval.get('status') if isinstance(retval, dict) else 'done'
        })

# ====================================
# MOCK IMPLEMENTATION
# ====================================

class MockTask:
    """Lean mock task for testing"""
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__

    def delay(self, *args, **kwargs):
        task_id = f"mock_{uuid.uuid4().hex[:12]}"
        audit_log(self.name, 'mock_started', kwargs.get('user_id'), {'task_id': task_id})

        # Simple mock result
        return type('MockResult', (), {
            'id': task_id,
            'ready': lambda: True,
            'successful': lambda: True,
            'get': lambda: {'status': 'completed', 'message': f'Mock {self.name} completed'}
        })()

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

# ====================================
# TASK IMPLEMENTATIONS
# ====================================

def _import_course_impl(course_id: int, storage_key: str, user_id: int, format: str = 'json') -> Dict[str, Any]:
    """Streamlined course import implementation"""
    start_time = time.time()

    try:
        # Validate inputs
        params = validate_params(course_id=course_id, storage_key=storage_key,
                               user_id=user_id, format=format)

        if not check_permissions(params['user_id'], 'instructor'):
            raise PermissionError("Insufficient permissions")

        # Validate course access
        from courses.models import Course
        course = Course.objects.get(id=params['course_id'])
        user = User.objects.get(id=params['user_id'])

        if not (user.is_staff or course.courseinstructor_set.filter(
            instructor=user, is_active=True).exists()):
            raise PermissionError("No access to this course")

        # Mock data processing (replace with actual implementation)
        mock_data = {
            'modules': [{'title': 'Sample Module', 'lessons': [{'title': 'Sample Lesson'}]}]
        }

        # Process import
        with transaction.atomic():
            processed_count = len(mock_data.get('modules', []))
            # Add actual import logic here

        duration = time.time() - start_time

        return {
            'status': 'completed',
            'course_id': params['course_id'],
            'items_processed': processed_count,
            'duration': round(duration, 2)
        }

    except Exception as e:
        logger.error(f"Course import failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'duration': round(time.time() - start_time, 2)
        }

def _cleanup_sessions_impl() -> Dict[str, Any]:
    """Streamlined session cleanup"""
    try:
        # Mock cleanup logic - replace with actual implementation
        cleaned_count = 0

        # Example: Delete expired sessions
        # expired_sessions = Session.objects.filter(
        #     expire_date__lt=timezone.now() - timedelta(days=7)
        # )
        # cleaned_count = expired_sessions.count()
        # expired_sessions.delete()

        return {
            'status': 'completed',
            'cleaned_count': cleaned_count
        }

    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return {'status': 'failed', 'error': str(e)}

def _generate_analytics_impl(user_id: int) -> Dict[str, Any]:
    """Streamlined analytics generation"""
    try:
        if not check_permissions(user_id, 'instructor'):
            raise PermissionError("Insufficient permissions")

        # Mock analytics generation
        analytics = {
            'total_courses': 0,
            'total_students': 0,
            'completion_rate': 0.0,
            'generated_at': timezone.now().isoformat()
        }

        return {
            'status': 'completed',
            'analytics': analytics
        }

    except Exception as e:
        logger.error(f"Analytics generation failed: {e}")
        return {'status': 'failed', 'error': str(e)}

# ====================================
# TASK DEFINITIONS
# ====================================

if CELERY_AVAILABLE and shared_task:
    @shared_task(bind=True, base=UnifiedTask)
    def import_course_from_key(self, course_id: int, storage_key: str, user_id: int, **kwargs):
        """Import course from storage key"""
        return _import_course_impl(course_id, storage_key, user_id, **kwargs)

    @shared_task(bind=True, base=UnifiedTask)
    @task_lock('cleanup_sessions')
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        return _cleanup_sessions_impl()

    @shared_task(bind=True, base=UnifiedTask)
    @task_lock('generate_analytics')
    def generate_analytics(self, user_id: int):
        """Generate user analytics"""
        return _generate_analytics_impl(user_id)

    @shared_task(bind=True, base=UnifiedTask)
    @task_lock('cleanup_files')
    def cleanup_orphaned_files(self):
        """Clean up orphaned files"""
        try:
            # Mock file cleanup
            cleaned_count = 0
            return {'status': 'completed', 'cleaned_count': cleaned_count}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

else:
    # Fallback implementations
    import_course_from_key = MockTask(_import_course_impl, 'import_course_from_key')
    cleanup_expired_sessions = MockTask(_cleanup_sessions_impl, 'cleanup_expired_sessions')
    generate_analytics = MockTask(_generate_analytics_impl, 'generate_analytics')
    cleanup_orphaned_files = MockTask(lambda: {'status': 'completed'}, 'cleanup_orphaned_files')

# ====================================
# MANAGEMENT UTILITIES
# ====================================

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status with unified interface"""
    try:
        if CELERY_AVAILABLE:
            from celery.result import AsyncResult
            result = AsyncResult(task_id)
            return {
                'task_id': task_id,
                'status': result.status,
                'result': result.result if result.ready() else None,
                'timestamp': timezone.now().isoformat()
            }
        else:
            return {
                'task_id': task_id,
                'status': 'UNKNOWN',
                'message': 'Task backend not available',
                'timestamp': timezone.now().isoformat()
            }
    except Exception as e:
        return {'task_id': task_id, 'status': 'ERROR', 'error': str(e)}

def cancel_task(task_id: str, user_id: int) -> Dict[str, Any]:
    """Cancel task with permission check"""
    try:
        if not check_permissions(user_id, 'instructor'):
            raise PermissionError("Insufficient permissions")

        if CELERY_AVAILABLE:
            from celery.result import AsyncResult
            AsyncResult(task_id).revoke(terminate=True)
            audit_log('task_cancelled', 'completed', user_id, {'task_id': task_id})
            return {'status': 'cancelled', 'task_id': task_id}
        else:
            return {'status': 'cancelled', 'task_id': task_id, 'message': 'Mock cancellation'}

    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def setup_periodic_tasks():
    """Setup periodic tasks if Celery Beat is available"""
    if not CELERY_AVAILABLE:
        return False

    try:
        from django_celery_beat.models import PeriodicTask, CrontabSchedule

        # Daily cleanup at 2 AM
        schedule, _ = CrontabSchedule.objects.get_or_create(
            hour=2, minute=0, day_of_week='*', day_of_month='*', month_of_year='*'
        )

        PeriodicTask.objects.update_or_create(
            name="daily_cleanup",
            defaults={
                'crontab': schedule,
                'task': 'instructor_portal.tasks.cleanup_expired_sessions',
                'enabled': True
            }
        )

        # Weekly file cleanup on Sundays at 3 AM
        schedule, _ = CrontabSchedule.objects.get_or_create(
            hour=3, minute=0, day_of_week='0', day_of_month='*', month_of_year='*'
        )

        PeriodicTask.objects.update_or_create(
            name="weekly_file_cleanup",
            defaults={
                'crontab': schedule,
                'task': 'instructor_portal.tasks.cleanup_orphaned_files',
                'enabled': True
            }
        )

        logger.info("Periodic tasks configured successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to setup periodic tasks: {e}")
        return False

# ====================================
# EXPORTS
# ====================================

__all__ = [
    'import_course_from_key',
    'cleanup_expired_sessions',
    'generate_analytics',
    'cleanup_orphaned_files',
    'get_task_status',
    'cancel_task',
    'setup_periodic_tasks',
    'audit_log',
    'validate_params',
    'check_permissions'
]

# Auto-setup periodic tasks on import
# if __name__ != '__main__':
#     setup_periodic_tasks()
