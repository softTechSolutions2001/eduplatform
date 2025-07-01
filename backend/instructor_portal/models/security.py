# File Path: instructor_portal/models/security.py
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
# Security models - Session tracking and security monitoring
# Restored from original models.py to maintain backward compatibility

import logging
from typing import List
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
User = get_user_model()


class InstructorSession(models.Model):
    """
    Track instructor login sessions for security and analytics
    ADDED: Enhanced session tracking for security monitoring
    """

    instructor = models.ForeignKey(
        'InstructorProfile',
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('Instructor')
    )

    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_('Session Key')
    )

    # Device and location information
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address')
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )

    device_type = models.CharField(
        max_length=20,
        choices=[
            ('desktop', _('Desktop')),
            ('mobile', _('Mobile')),
            ('tablet', _('Tablet')),
            ('unknown', _('Unknown'))
        ],
        default='unknown',
        verbose_name=_('Device Type')
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Location'),
        help_text=_('Approximate location based on IP')
    )

    # Session tracking
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Login Time')
    )

    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Activity')
    )

    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Logout Time')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    # Security flags
    is_suspicious = models.BooleanField(
        default=False,
        verbose_name=_('Is Suspicious'),
        help_text=_('Flagged for suspicious activity')
    )

    security_notes = models.TextField(
        blank=True,
        verbose_name=_('Security Notes')
    )

    class Meta:
        verbose_name = _('Instructor Session')
        verbose_name_plural = _('Instructor Sessions')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['instructor', '-login_time']),
            models.Index(fields=['session_key']),
            models.Index(fields=['ip_address', 'login_time']),
            models.Index(fields=['is_active', 'last_activity']),
        ]

    def __str__(self):
        return f"Session for {self.instructor.display_name} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def create_session(cls, instructor, request) -> 'InstructorSession':
        """Create a new instructor session"""
        try:
            # Extract device and location information
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = cls._get_client_ip(request)
            device_type = cls._get_device_type(user_agent)
            location = cls._get_location_from_ip(ip_address)

            session = cls.objects.create(
                instructor=instructor,
                session_key=request.session.session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                location=location
            )

            # Update instructor last login
            instructor.last_login = timezone.now()
            instructor.save(update_fields=['last_login'])

            logger.info(f"Created session for {instructor.display_name} from {ip_address}")
            return session

        except Exception as e:
            logger.error(f"Error creating instructor session: {e}")
            raise

    @staticmethod
    def _get_client_ip(request) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

    @staticmethod
    def _get_device_type(user_agent: str) -> str:
        """Determine device type from user agent"""
        ua_lower = user_agent.lower()

        mobile_indicators = ['mobile', 'android', 'iphone']
        tablet_indicators = ['tablet', 'ipad']

        if any(indicator in ua_lower for indicator in mobile_indicators):
            return 'mobile'
        elif any(indicator in ua_lower for indicator in tablet_indicators):
            return 'tablet'
        elif user_agent:
            return 'desktop'
        else:
            return 'unknown'

    @staticmethod
    def _get_location_from_ip(ip_address: str) -> str:
        """Get approximate location from IP address"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except Exception:
            return 'Unknown'

    def end_session(self) -> bool:
        """End the instructor session"""
        try:
            if self.is_active:
                self.is_active = False
                self.logout_time = timezone.now()
                self.save(update_fields=['is_active', 'logout_time'])
                logger.debug(f"Ended session {self.session_key}")
            return True
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False

    @classmethod
    def cleanup_expired_sessions(cls, days_old: int = 30) -> int:
        """Clean up old inactive sessions"""
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
            old_sessions = cls.objects.filter(
                last_activity__lt=cutoff_date,
                is_active=False
            )

            count = old_sessions.count()
            if count > 0:
                old_sessions.delete()
                logger.info(f"Cleaned up {count} old instructor sessions")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    @classmethod
    def detect_suspicious_activity(cls) -> List['InstructorSession']:
        """Detect potentially suspicious session activity"""
        suspicious_sessions = []

        try:
            # Check for multiple concurrent sessions from different IPs
            recent_time = timezone.now() - timezone.timedelta(hours=1)

            instructors_with_multiple_ips = cls.objects.filter(
                login_time__gte=recent_time,
                is_active=True
            ).values('instructor').annotate(
                ip_count=models.Count('ip_address', distinct=True)
            ).filter(ip_count__gt=1)

            for item in instructors_with_multiple_ips:
                sessions = cls.objects.filter(
                    instructor_id=item['instructor'],
                    login_time__gte=recent_time,
                    is_active=True
                )

                for session in sessions:
                    if not session.is_suspicious:
                        session.is_suspicious = True
                        session.security_notes = 'Multiple concurrent sessions from different IPs detected'
                        session.save(update_fields=['is_suspicious', 'security_notes'])
                        suspicious_sessions.append(session)

            logger.info(f"Detected {len(suspicious_sessions)} suspicious sessions")
            return suspicious_sessions

        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return []
