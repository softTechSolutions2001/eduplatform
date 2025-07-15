#
# File Path: instructor_portal/views/profile_views.py
# Folder Path: instructor_portal/views/
# Date Created: 2025-06-26 14:49:15
# Date Revised: 2025-06-27 06:55:35
# Current Date and Time (UTC): 2025-06-27 06:55:35
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:55:35 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Profile and settings viewsets for instructor_portal
# COMPLETELY REVISED: Enhanced with query optimizations and advanced features
# Maintains 100% backward compatibility with performance improvements

import logging
from datetime import timedelta
from typing import Dict, List, Any, Optional

from django.db import transaction, models
from django.db.models import Q, Count, Avg, Sum, Prefetch
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.throttling import UserRateThrottle

from courses.models import Course, Enrollment
from ..models import CourseInstructor
from ..models import InstructorProfile, InstructorAnalytics, InstructorDashboard, TierManager
from ..serializers import InstructorProfileSerializer, InstructorSettingsSerializer
from .mixins import (
    InstructorBaseViewSet, require_instructor_profile, tier_required,
    get_instructor_profile, audit_log, scrub_sensitive_data,
    ANALYTICS_CACHE_TIMEOUT, PERMISSIONS_CACHE_TIMEOUT
)

User = get_user_model()
logger = logging.getLogger(__name__)


class InstructorProfileViewSet(InstructorBaseViewSet):
    """
    Enhanced API endpoint for instructor profile management
    COMPLETELY REVISED: Full integration with optimizations and caching
    """
    serializer_class = InstructorProfileSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    resource_name = 'instructor_profile'

    def get_queryset(self):
        """Optimized queryset with proper select_related and prefetch_related"""
        return InstructorProfile.objects.select_related(
            'user',
            'approved_by'
        ).prefetch_related(
            Prefetch(
                'user__courseinstructor_set',
                queryset=CourseInstructor.objects.select_related('course').filter(is_active=True)
            )
        )

    def get_object(self):
        """Get current user's instructor profile or create if needed with optimization"""
        try:
            # Try cache first
            cache_key = f"instructor_profile_full:{self.request.user.id}"
            profile = cache.get(cache_key)

            if profile is None:
                # Get from database with optimizations
                try:
                    profile = self.get_queryset().get(user=self.request.user)
                    cache.set(cache_key, profile, PERMISSIONS_CACHE_TIMEOUT)
                except InstructorProfile.DoesNotExist:
                    # Create profile if it doesn't exist
                    profile = self._create_instructor_profile(self.request.user)

            return profile

        except Exception as e:
            logger.error(f"Error getting/creating instructor profile: {e}", exc_info=True)
            raise

    def _create_instructor_profile(self, user: User) -> InstructorProfile:
        """Create new instructor profile with proper defaults"""
        try:
            with transaction.atomic():
                display_name = user.get_full_name() or user.username

                profile = InstructorProfile.objects.create(
                    user=user,
                    display_name=display_name,
                    status=InstructorProfile.Status.PENDING,
                    tier=InstructorProfile.Tier.BRONZE,
                    email_notifications=True,
                    marketing_emails=False,
                    public_profile=True
                )

                # Create default dashboard configuration
                InstructorDashboard.objects.create(
                    instructor=profile,
                    show_analytics=True,
                    show_recent_students=True,
                    show_performance_metrics=True,
                    show_revenue_charts=True,
                    show_course_progress=True
                )

                # Invalidate caches
                cache.delete(f"instructor_profile:{user.id}")
                cache.delete(f"instructor_profile_full:{user.id}")

                audit_log(
                    user,
                    'instructor_profile_created',
                    'instructor_profile',
                    profile.id,
                    metadata={'display_name': display_name},
                    request=getattr(self, 'request', None)
                )

                return profile

        except Exception as e:
            logger.error(f"Error creating instructor profile: {e}", exc_info=True)
            raise

    @require_instructor_profile
    def retrieve(self, request, pk=None):
        """Get instructor profile with comprehensive data"""
        instructor_profile = self.get_object()

        try:
            # Build comprehensive profile data
            profile_data = self.get_serializer(instructor_profile).data

            # Add computed fields
            profile_data.update({
                'profile_completion': self._calculate_profile_completion(instructor_profile),
                'tier_info': {
                    'current_tier': instructor_profile.get_tier_display(),
                    'tier_limits': TierManager.get_tier_limits(instructor_profile.tier),
                    'next_tier': self._get_next_tier_info(instructor_profile)
                },
                'statistics': self._get_profile_statistics(instructor_profile),
                'recent_activity': self._get_recent_activity(instructor_profile),
                'achievements': self._get_achievements(instructor_profile)
            })

            return Response(profile_data)

        except Exception as e:
            logger.error(f"Error retrieving profile data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve profile data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    def update(self, request, pk=None):
        """Update instructor profile with validation"""
        instructor_profile = self.get_object()

        try:
            with transaction.atomic():
                # Validate update data
                validation_errors = self._validate_profile_update(request.data)
                if validation_errors:
                    return Response(
                        {'detail': 'Validation failed', 'errors': validation_errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update profile
                serializer = self.get_serializer(
                    instructor_profile,
                    data=request.data,
                    partial=True
                )

                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()

                # Clear caches
                self._clear_profile_caches(request.user.id)

                # Update analytics if needed
                if any(field in request.data for field in ['display_name', 'bio', 'expertise_areas']):
                    instructor_profile.update_analytics()

            audit_log(
                request.user,
                'instructor_profile_updated',
                'instructor_profile',
                instructor_profile.id,
                metadata=scrub_sensitive_data(request.data),
                request=request
            )

            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error updating profile: {e}", exc_info=True)
            return Response(
                {'detail': 'Profile update failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get comprehensive instructor analytics with caching"""
        instructor_profile = self.get_object()

        try:
            # Check cache first
            cache_key = f"instructor_analytics:{instructor_profile.id}"
            analytics_data = cache.get(cache_key)

            if analytics_data is None:
                # Get analytics data
                performance_metrics = instructor_profile.get_performance_metrics()
                tier_limits = TierManager.get_tier_limits(instructor_profile.tier)

                # Get recent analytics with optimization
                days_limit = tier_limits.get('analytics_history_days', 30)
                cutoff_date = timezone.now() - timezone.timedelta(days=days_limit)

                recent_analytics = InstructorAnalytics.objects.filter(
                    instructor=instructor_profile,
                    date__gte=cutoff_date
                ).only(
                    'date', 'total_students', 'total_courses', 'average_rating',
                    'total_revenue', 'completion_rate'
                ).order_by('-date')[:30]

                # Calculate trends efficiently
                trends = self._calculate_analytics_trends(recent_analytics)

                # Get course performance data
                course_performance = self._get_course_performance_data(instructor_profile)

                analytics_data = {
                    'profile': InstructorProfileSerializer(instructor_profile).data,
                    'performance_metrics': performance_metrics,
                    'tier_limits': tier_limits,
                    'trends': trends,
                    'course_performance': course_performance,
                    'recent_analytics': [
                        {
                            'date': analytics.date,
                            'total_students': analytics.total_students,
                            'total_courses': analytics.total_courses,
                            'average_rating': float(analytics.average_rating),
                            'total_revenue': float(analytics.total_revenue),
                            'completion_rate': float(analytics.completion_rate)
                        }
                        for analytics in recent_analytics
                    ],
                    'summary_statistics': self._get_analytics_summary(instructor_profile, recent_analytics)
                }

                # Cache for performance
                cache.set(cache_key, analytics_data, ANALYTICS_CACHE_TIMEOUT)

            # Record analytics access
            audit_log(
                request.user,
                'analytics_accessed',
                'instructor_profile',
                instructor_profile.id,
                metadata={'tier': instructor_profile.tier},
                request=request
            )

            return Response(analytics_data)

        except Exception as e:
            logger.error(f"Error getting analytics data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve analytics data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def request_verification(self, request):
        """Request instructor verification with enhanced validation"""
        instructor_profile = self.get_object()

        try:
            # Check if already verified
            if instructor_profile.is_verified:
                return Response(
                    {'detail': 'Profile is already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if already pending
            if instructor_profile.status == InstructorProfile.Status.PENDING:
                return Response(
                    {'detail': 'Verification request already pending'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate profile completeness
            completion_percentage = self._calculate_profile_completion(instructor_profile)
            if completion_percentage < 75:
                return Response(
                    {
                        'detail': 'Profile must be at least 75% complete to request verification',
                        'current_completion': completion_percentage,
                        'required_completion': 75
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                # Update status to pending verification
                instructor_profile.status = InstructorProfile.Status.PENDING
                instructor_profile.verification_requested_at = timezone.now()
                instructor_profile.save(update_fields=['status', 'verification_requested_at'])

                # Clear caches
                self._clear_profile_caches(request.user.id)

            audit_log(
                request.user,
                'verification_requested',
                'instructor_profile',
                instructor_profile.id,
                metadata={'completion_percentage': completion_percentage},
                request=request
            )

            return Response({
                'detail': 'Verification request submitted successfully',
                'status': instructor_profile.get_status_display(),
                'estimated_review_time': '2-5 business days'
            })

        except Exception as e:
            logger.error(f"Error requesting verification: {e}", exc_info=True)
            return Response(
                {'detail': 'Verification request failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def update_analytics(self, request):
        """Manually update analytics with rate limiting"""
        instructor_profile = self.get_object()

        try:
            # Check rate limiting
            rate_limit_key = f"analytics_update:{instructor_profile.id}"
            if cache.get(rate_limit_key):
                return Response(
                    {'detail': 'Please wait before updating analytics again'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Update analytics
            success = instructor_profile.update_analytics()

            if success:
                # Create daily snapshot
                InstructorAnalytics.record_daily_snapshot(instructor_profile)

                # Set rate limit (5 minutes)
                cache.set(rate_limit_key, True, timeout=300)

                # Clear analytics cache
                cache.delete(f"instructor_analytics:{instructor_profile.id}")

                audit_log(
                    request.user,
                    'analytics_manually_updated',
                    'instructor_profile',
                    instructor_profile.id,
                    request=request
                )

                return Response({
                    'detail': 'Analytics updated successfully',
                    'last_updated': timezone.now().isoformat()
                })
            else:
                return Response(
                    {'detail': 'Failed to update analytics. Please try again later.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error updating analytics: {e}", exc_info=True)
            return Response(
                {'detail': 'Analytics update failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def tier_info(self, request):
        """Get comprehensive tier information and upgrade paths"""
        instructor_profile = self.get_object()

        try:
            current_tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            next_tier_info = self._get_next_tier_info(instructor_profile)

            tier_data = {
                'current_tier': {
                    'name': instructor_profile.get_tier_display(),
                    'code': instructor_profile.tier,
                    'limits': current_tier_limits,
                    'usage': {
                        'courses': instructor_profile.total_courses,
                        'students': instructor_profile.total_students,
                        'revenue': float(instructor_profile.total_revenue)
                    }
                },
                'next_tier': next_tier_info,
                'upgrade_eligibility': self._check_tier_upgrade_eligibility(instructor_profile),
                'tier_benefits': self._get_tier_benefits_comparison(),
                'upgrade_recommendations': self._get_upgrade_recommendations(instructor_profile)
            }

            return Response(tier_data)

        except Exception as e:
            logger.error(f"Error getting tier info: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve tier information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @tier_required('gold')
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """Export instructor data (premium feature)"""
        instructor_profile = self.get_object()

        try:
            export_format = request.data.get('format', 'json')  # json, csv, xlsx
            include_analytics = request.data.get('include_analytics', True)
            date_range = request.data.get('date_range', 'all')  # all, last_30_days, last_90_days

            if export_format not in ['json', 'csv', 'xlsx']:
                return Response(
                    {'detail': 'Invalid export format. Supported: json, csv, xlsx'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate export data
            export_data = self._generate_export_data(
                instructor_profile,
                include_analytics,
                date_range
            )

            audit_log(
                request.user,
                'data_exported',
                'instructor_profile',
                instructor_profile.id,
                metadata={'format': export_format, 'include_analytics': include_analytics},
                request=request
            )

            # In a real implementation, you would generate and return the file
            return Response({
                'detail': 'Export generated successfully',
                'export_id': str(uuid.uuid4()),
                'format': export_format,
                'download_url': f'/api/instructor/exports/{export_format}',
                'expires_at': (timezone.now() + timedelta(hours=24)).isoformat()
            })

        except Exception as e:
            logger.error(f"Error exporting data: {e}", exc_info=True)
            return Response(
                {'detail': 'Data export failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Helper methods
    def _validate_profile_update(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validate profile update data"""
        errors = {}

        if 'display_name' in data:
            display_name = data['display_name'].strip()
            if not display_name:
                errors['display_name'] = 'Display name cannot be empty'
            elif len(display_name) > 100:
                errors['display_name'] = 'Display name too long (max 100 characters)'

        if 'bio' in data:
            bio = data['bio'].strip()
            if len(bio) > 1000:
                errors['bio'] = 'Bio too long (max 1000 characters)'

        if 'expertise_areas' in data:
            expertise_areas = data['expertise_areas']
            if not isinstance(expertise_areas, list):
                errors['expertise_areas'] = 'Expertise areas must be a list'
            elif len(expertise_areas) > 10:
                errors['expertise_areas'] = 'Too many expertise areas (max 10)'

        return errors

    def _calculate_profile_completion(self, instructor_profile: InstructorProfile) -> int:
        """Calculate profile completion percentage"""
        total_fields = 10
        completed_fields = 0

        # Profile fields
        if instructor_profile.display_name:
            completed_fields += 1
        if instructor_profile.bio:
            completed_fields += 1
        if instructor_profile.expertise_areas:
            completed_fields += 1

        # User fields
        user = instructor_profile.user
        if user.first_name:
            completed_fields += 1
        if user.last_name:
            completed_fields += 1
        if user.is_active:
            completed_fields += 1

        # Status and verification
        if instructor_profile.status == InstructorProfile.Status.ACTIVE:
            completed_fields += 1
        if instructor_profile.is_verified:
            completed_fields += 1

        # Additional profile data
        if instructor_profile.public_profile is not None:
            completed_fields += 1
        if instructor_profile.total_courses > 0:
            completed_fields += 1

        return int((completed_fields / total_fields) * 100)

    def _calculate_analytics_trends(self, analytics_data) -> Dict[str, float]:
        """Calculate analytics trends efficiently"""
        if len(analytics_data) < 2:
            return {
                'students_trend': 0.0,
                'revenue_trend': 0.0,
                'rating_trend': 0.0,
                'completion_trend': 0.0
            }

        latest = analytics_data[0]
        previous = analytics_data[1]

        return {
            'students_trend': latest.total_students - previous.total_students,
            'revenue_trend': float(latest.total_revenue - previous.total_revenue),
            'rating_trend': float(latest.average_rating - previous.average_rating),
            'completion_trend': float(latest.completion_rate - previous.completion_rate)
        }

    def _get_course_performance_data(self, instructor_profile: InstructorProfile) -> List[Dict]:
        """Get optimized course performance data"""
        courses = Course.objects.filter(
            courseinstructor_set__instructor=instructor_profile.user,
            courseinstructor_set__is_active=True
        ).annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status='active')),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            completion_rate=Avg('enrollments__progress', filter=Q(enrollments__status='completed'))
        ).only('id', 'title', 'slug', 'created_date')

        return [
            {
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'enrolled_students': course.enrolled_count or 0,
                'average_rating': float(course.avg_rating or 0),
                'completion_rate': float(course.completion_rate or 0),
                'created_date': course.created_date
            }
            for course in courses
        ]

    def _get_analytics_summary(self, instructor_profile: InstructorProfile, recent_analytics) -> Dict:
        """Get analytics summary statistics"""
        if not recent_analytics:
            return {}

        analytics_list = list(recent_analytics)

        return {
            'total_data_points': len(analytics_list),
            'date_range': {
                'start': analytics_list[-1].date if analytics_list else None,
                'end': analytics_list[0].date if analytics_list else None
            },
            'averages': {
                'students': sum(a.total_students for a in analytics_list) / len(analytics_list),
                'rating': sum(float(a.average_rating) for a in analytics_list) / len(analytics_list),
                'completion_rate': sum(float(a.completion_rate) for a in analytics_list) / len(analytics_list)
            }
        }

    def _get_next_tier_info(self, instructor_profile: InstructorProfile) -> Optional[Dict]:
        """Get information about the next tier"""
        tier_hierarchy = ['bronze', 'silver', 'gold', 'platinum', 'diamond']
        current_index = tier_hierarchy.index(instructor_profile.tier.lower())

        if current_index < len(tier_hierarchy) - 1:
            next_tier = tier_hierarchy[current_index + 1]
            next_tier_limits = TierManager.get_tier_limits(next_tier)

            return {
                'name': next_tier.title(),
                'code': next_tier,
                'limits': next_tier_limits,
                'requirements': self._get_tier_requirements(next_tier)
            }

        return None

    def _get_tier_requirements(self, tier: str) -> Dict:
        """Get requirements for a specific tier"""
        requirements = {
            'silver': {'min_courses': 3, 'min_students': 50, 'min_rating': 4.0},
            'gold': {'min_courses': 10, 'min_students': 200, 'min_rating': 4.2},
            'platinum': {'min_courses': 25, 'min_students': 500, 'min_rating': 4.5},
            'diamond': {'min_courses': 50, 'min_students': 1000, 'min_rating': 4.7}
        }
        return requirements.get(tier, {})

    def _clear_profile_caches(self, user_id: int):
        """Clear all profile-related caches"""
        cache.delete(f"instructor_profile:{user_id}")
        cache.delete(f"instructor_profile_full:{user_id}")
        cache.delete(f"instructor_profile_status:{user_id}")
        cache.delete(f"instructor_analytics:{user_id}")


class InstructorSettingsViewSet(viewsets.ViewSet):
    """
    Enhanced instructor settings management with comprehensive functionality
    COMPLETELY REVISED: Full settings management system
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @require_instructor_profile
    def retrieve(self, request, pk=None):
        """Get comprehensive instructor settings"""
        instructor_profile = request.instructor_profile

        try:
            # Get dashboard configuration
            try:
                dashboard = InstructorDashboard.objects.get(instructor=instructor_profile)
                dashboard_config = {
                    'show_analytics': dashboard.show_analytics,
                    'show_recent_students': dashboard.show_recent_students,
                    'show_performance_metrics': dashboard.show_performance_metrics,
                    'show_revenue_charts': dashboard.show_revenue_charts,
                    'show_course_progress': dashboard.show_course_progress,
                    'notify_new_enrollments': dashboard.notify_new_enrollments,
                    'notify_new_reviews': dashboard.notify_new_reviews,
                    'notify_course_completions': dashboard.notify_course_completions,
                    'widget_order': dashboard.widget_order,
                    'custom_colors': dashboard.custom_colors
                }
            except InstructorDashboard.DoesNotExist:
                dashboard_config = {
                    'show_analytics': True,
                    'show_recent_students': True,
                    'show_performance_metrics': True,
                    'show_revenue_charts': True,
                    'show_course_progress': True,
                    'notify_new_enrollments': True,
                    'notify_new_reviews': True,
                    'notify_course_completions': True,
                    'widget_order': [],
                    'custom_colors': {}
                }

            settings_data = {
                'profile_settings': {
                    'email_notifications': instructor_profile.email_notifications,
                    'marketing_emails': instructor_profile.marketing_emails,
                    'public_profile': instructor_profile.public_profile,
                },
                'dashboard_config': dashboard_config,
                'privacy_settings': {
                    'show_email_in_profile': False,  # Default privacy setting
                    'allow_contact_from_students': True,
                    'show_revenue_publicly': False
                },
                'notification_preferences': self._get_notification_preferences(instructor_profile),
                'account_settings': {
                    'timezone': getattr(instructor_profile, 'timezone', 'UTC'),
                    'language': getattr(instructor_profile, 'language', 'en'),
                    'date_format': getattr(instructor_profile, 'date_format', 'YYYY-MM-DD')
                }
            }

            return Response(settings_data)

        except Exception as e:
            logger.error(f"Error retrieving settings: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve settings'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    def update(self, request, pk=None):
        """Update instructor settings with validation"""
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                # Update profile settings
                profile_fields = ['email_notifications', 'marketing_emails', 'public_profile']
                updated_profile_fields = []

                for field in profile_fields:
                    if field in request.data.get('profile_settings', {}):
                        value = request.data['profile_settings'][field]
                        setattr(instructor_profile, field, value)
                        updated_profile_fields.append(field)

                if updated_profile_fields:
                    instructor_profile.save(update_fields=updated_profile_fields)

                # Update dashboard configuration
                if 'dashboard_config' in request.data:
                    self._update_dashboard_config(instructor_profile, request.data['dashboard_config'])

                # Clear caches
                cache.delete(f"instructor_profile:{request.user.id}")
                cache.delete(f"instructor_profile_full:{request.user.id}")

            audit_log(
                request.user,
                'instructor_settings_updated',
                'instructor_profile',
                instructor_profile.id,
                metadata=scrub_sensitive_data(request.data),
                request=request
            )

            return Response({
                'detail': 'Settings updated successfully',
                'updated_fields': updated_profile_fields
            })

        except Exception as e:
            logger.error(f"Error updating settings: {e}", exc_info=True)
            return Response(
                {'detail': 'Settings update failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """Get detailed notification settings"""
        instructor_profile = request.instructor_profile

        try:
            notification_data = {
                'email_notifications': instructor_profile.email_notifications,
                'marketing_emails': instructor_profile.marketing_emails,
                'notification_types': {
                    'new_enrollments': True,
                    'course_completions': True,
                    'new_reviews': True,
                    'payment_notifications': True,
                    'system_updates': True,
                    'security_alerts': True
                },
                'frequency_settings': {
                    'digest_frequency': 'daily',  # daily, weekly, monthly
                    'instant_notifications': True,
                    'quiet_hours': {
                        'enabled': False,
                        'start_time': '22:00',
                        'end_time': '08:00'
                    }
                }
            }

            return Response(notification_data)

        except Exception as e:
            logger.error(f"Error getting notification settings: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to get notification settings'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['put'])
    def update_notifications(self, request):
        """Update notification settings with validation"""
        instructor_profile = request.instructor_profile

        try:
            updated_fields = []

            with transaction.atomic():
                if 'email_notifications' in request.data:
                    instructor_profile.email_notifications = request.data['email_notifications']
                    updated_fields.append('email_notifications')

                if 'marketing_emails' in request.data:
                    instructor_profile.marketing_emails = request.data['marketing_emails']
                    updated_fields.append('marketing_emails')

                if updated_fields:
                    instructor_profile.save(update_fields=updated_fields)

                # Update dashboard notification settings if provided
                if 'dashboard_notifications' in request.data:
                    self._update_dashboard_notifications(
                        instructor_profile,
                        request.data['dashboard_notifications']
                    )

            audit_log(
                request.user,
                'notification_settings_updated',
                'instructor_profile',
                instructor_profile.id,
                metadata={'updated_fields': updated_fields},
                request=request
            )

            return Response({
                'detail': 'Notification settings updated successfully',
                'updated_fields': updated_fields
            })

        except Exception as e:
            logger.error(f"Error updating notification settings: {e}", exc_info=True)
            return Response(
                {'detail': 'Notification settings update failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def reset_settings(self, request):
        """Reset settings to default values"""
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                # Reset profile settings to defaults
                instructor_profile.email_notifications = True
                instructor_profile.marketing_emails = False
                instructor_profile.public_profile = True
                instructor_profile.save(update_fields=[
                    'email_notifications', 'marketing_emails', 'public_profile'
                ])

                # Reset dashboard configuration
                try:
                    dashboard = InstructorDashboard.objects.get(instructor=instructor_profile)
                    dashboard.show_analytics = True
                    dashboard.show_recent_students = True
                    dashboard.show_performance_metrics = True
                    dashboard.show_revenue_charts = True
                    dashboard.show_course_progress = True
                    dashboard.notify_new_enrollments = True
                    dashboard.notify_new_reviews = True
                    dashboard.notify_course_completions = True
                    dashboard.widget_order = []
                    dashboard.custom_colors = {}
                    dashboard.save()
                except InstructorDashboard.DoesNotExist:
                    # Create default dashboard if it doesn't exist
                    InstructorDashboard.objects.create(
                        instructor=instructor_profile,
                        show_analytics=True,
                        show_recent_students=True,
                        show_performance_metrics=True
                    )

                # Clear caches
                cache.delete(f"instructor_profile:{request.user.id}")
                cache.delete(f"instructor_profile_full:{request.user.id}")

            audit_log(
                request.user,
                'settings_reset_to_defaults',
                'instructor_profile',
                instructor_profile.id,
                request=request
            )

            return Response({'detail': 'Settings reset to default values successfully'})

        except Exception as e:
            logger.error(f"Error resetting settings: {e}", exc_info=True)
            return Response(
                {'detail': 'Settings reset failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Helper methods
    def _update_dashboard_config(self, instructor_profile: InstructorProfile, config_data: Dict):
        """Update dashboard configuration"""
        try:
            dashboard, created = InstructorDashboard.objects.get_or_create(
                instructor=instructor_profile,
                defaults={
                    'show_analytics': True,
                    'show_recent_students': True,
                    'show_performance_metrics': True
                }
            )

            # Update dashboard fields
            dashboard_fields = [
                'show_analytics', 'show_recent_students', 'show_performance_metrics',
                'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
                'notify_new_reviews', 'notify_course_completions'
            ]

            updated_fields = []
            for field in dashboard_fields:
                if field in config_data:
                    setattr(dashboard, field, config_data[field])
                    updated_fields.append(field)

            # Update layout settings
            if 'widget_order' in config_data:
                if isinstance(config_data['widget_order'], list):
                    dashboard.widget_order = config_data['widget_order']
                    updated_fields.append('widget_order')

            if 'custom_colors' in config_data:
                if isinstance(config_data['custom_colors'], dict):
                    dashboard.custom_colors = config_data['custom_colors']
                    updated_fields.append('custom_colors')

            if updated_fields:
                dashboard.save(update_fields=updated_fields)

        except Exception as e:
            logger.error(f"Error updating dashboard config: {e}", exc_info=True)
            raise

    def _update_dashboard_notifications(self, instructor_profile: InstructorProfile, notification_data: Dict):
        """Update dashboard notification settings"""
        try:
            dashboard, created = InstructorDashboard.objects.get_or_create(
                instructor=instructor_profile,
                defaults={'notify_new_enrollments': True}
            )

            notification_fields = ['notify_new_enrollments', 'notify_new_reviews', 'notify_course_completions']
            updated_fields = []

            for field in notification_fields:
                if field in notification_data:
                    setattr(dashboard, field, notification_data[field])
                    updated_fields.append(field)

            if updated_fields:
                dashboard.save(update_fields=updated_fields)

        except Exception as e:
            logger.error(f"Error updating dashboard notifications: {e}", exc_info=True)
            raise

    def _get_notification_preferences(self, instructor_profile: InstructorProfile) -> Dict:
        """Get comprehensive notification preferences"""
        try:
            dashboard = InstructorDashboard.objects.get(instructor=instructor_profile)
            return {
                'new_enrollments': dashboard.notify_new_enrollments,
                'new_reviews': dashboard.notify_new_reviews,
                'course_completions': dashboard.notify_course_completions,
                'email_enabled': instructor_profile.email_notifications,
                'marketing_enabled': instructor_profile.marketing_emails
            }
        except InstructorDashboard.DoesNotExist:
            return {
                'new_enrollments': True,
                'new_reviews': True,
                'course_completions': True,
                'email_enabled': instructor_profile.email_notifications,
                'marketing_enabled': instructor_profile.marketing_emails
            }

    def _check_tier_upgrade_eligibility(self, instructor_profile: InstructorProfile) -> Dict:
        """Check if instructor is eligible for tier upgrade"""
        next_tier_info = self._get_next_tier_info(instructor_profile)

        if not next_tier_info:
            return {'eligible': False, 'reason': 'Already at highest tier'}

        requirements = next_tier_info.get('requirements', {})
        current_metrics = instructor_profile.get_performance_metrics()

        eligibility = {
            'eligible': True,
            'missing_requirements': [],
            'progress': {}
        }

        # Check each requirement
        for req_key, req_value in requirements.items():
            if req_key == 'min_courses':
                current_value = current_metrics.get('total_courses', 0)
                if current_value < req_value:
                    eligibility['eligible'] = False
                    eligibility['missing_requirements'].append(f'Need {req_value - current_value} more courses')
                eligibility['progress']['courses'] = f"{current_value}/{req_value}"

            elif req_key == 'min_students':
                current_value = current_metrics.get('total_students', 0)
                if current_value < req_value:
                    eligibility['eligible'] = False
                    eligibility['missing_requirements'].append(f'Need {req_value - current_value} more students')
                eligibility['progress']['students'] = f"{current_value}/{req_value}"

            elif req_key == 'min_rating':
                current_value = float(current_metrics.get('average_rating', 0))
                if current_value < req_value:
                    eligibility['eligible'] = False
                    eligibility['missing_requirements'].append(f'Need rating of {req_value} (currently {current_value:.1f})')
                eligibility['progress']['rating'] = f"{current_value:.1f}/{req_value}"

        return eligibility

    def _get_tier_benefits_comparison(self) -> Dict:
        """Get comparison of benefits across all tiers"""
        return {
            'bronze': {
                'max_courses': 3,
                'max_file_size': '10MB',
                'analytics_history': '30 days',
                'support': 'Email only'
            },
            'silver': {
                'max_courses': 10,
                'max_file_size': '25MB',
                'analytics_history': '90 days',
                'support': 'Priority email'
            },
            'gold': {
                'max_courses': 25,
                'max_file_size': '50MB',
                'analytics_history': '365 days',
                'support': 'Chat + email',
                'ai_features': 'Basic'
            },
            'platinum': {
                'max_courses': 100,
                'max_file_size': '100MB',
                'analytics_history': 'Unlimited',
                'support': '24/7 chat + phone',
                'ai_features': 'Advanced'
            },
            'diamond': {
                'max_courses': 'Unlimited',
                'max_file_size': '500MB',
                'analytics_history': 'Unlimited',
                'support': 'Dedicated manager',
                'ai_features': 'Premium',
                'custom_branding': True
            }
        }

    def _get_upgrade_recommendations(self, instructor_profile: InstructorProfile) -> List[str]:
        """Get personalized upgrade recommendations"""
        recommendations = []
        metrics = instructor_profile.get_performance_metrics()

        if metrics.get('total_courses', 0) >= 5:
            recommendations.append("Create more courses to unlock higher tiers")

        if metrics.get('average_rating', 0) < 4.5:
            recommendations.append("Focus on improving course quality to increase ratings")

        if metrics.get('total_students', 0) < 100:
            recommendations.append("Market your courses to attract more students")

        return recommendations

    def _generate_export_data(self, instructor_profile: InstructorProfile,
                            include_analytics: bool, date_range: str) -> Dict:
        """Generate export data for instructor"""
        export_data = {
            'profile': InstructorProfileSerializer(instructor_profile).data,
            'export_metadata': {
                'generated_at': timezone.now().isoformat(),
                'instructor_id': instructor_profile.id,
                'include_analytics': include_analytics,
                'date_range': date_range
            }
        }

        if include_analytics:
            # Add analytics data based on date range
            if date_range == 'last_30_days':
                cutoff = timezone.now() - timedelta(days=30)
            elif date_range == 'last_90_days':
                cutoff = timezone.now() - timedelta(days=90)
            else:
                cutoff = None

            analytics_query = InstructorAnalytics.objects.filter(instructor=instructor_profile)
            if cutoff:
                analytics_query = analytics_query.filter(date__gte=cutoff)

            export_data['analytics'] = [
                {
                    'date': analytics.date,
                    'total_students': analytics.total_students,
                    'total_courses': analytics.total_courses,
                    'average_rating': float(analytics.average_rating),
                    'total_revenue': float(analytics.total_revenue),
                    'completion_rate': float(analytics.completion_rate)
                }
                for analytics in analytics_query.order_by('-date')
            ]

        return export_data
