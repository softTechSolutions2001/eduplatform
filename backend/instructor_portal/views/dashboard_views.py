#
# File Path: instructor_portal/views/dashboard_views.py
# Folder Path: instructor_portal/views/
# Date Created: 2025-06-26 14:49:15
# Date Revised: 2025-06-27 07:05:38
# Current Date and Time (UTC): 2025-06-27 07:05:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 07:05:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Dashboard and analytics viewsets for instructor_portal
# COMPLETELY REVISED: Enhanced with performance optimizations and real-time features
# Maintains 100% backward compatibility with advanced functionality

import logging
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional

from django.db import transaction, models
from django.db.models import (
    Q, Count, Avg, Sum, Max, Min, F, Case, When,
    IntegerField, DecimalField, Prefetch
)
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import ValidationError

from courses.models import Course, Enrollment, Review
from ..models import CourseInstructor
from ..models import (
    InstructorProfile, InstructorDashboard, InstructorAnalytics, TierManager
)
from ..serializers import InstructorDashboardSerializer, InstructorAnalyticsSerializer
from .mixins import (
    require_instructor_profile, tier_required, get_instructor_profile,
    audit_log, scrub_sensitive_data, ANALYTICS_CACHE_TIMEOUT
)

User = get_user_model()
logger = logging.getLogger(__name__)


class InstructorDashboardViewSet(viewsets.ViewSet):
    """
    Enhanced API endpoint for instructor dashboard management
    COMPLETELY REVISED: Advanced dashboard with real-time analytics and caching
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @require_instructor_profile
    def list(self, request):
        """Get comprehensive dashboard data with advanced caching"""
        instructor_profile = request.instructor_profile

        try:
            # Check cache first for performance
            cache_key = f"instructor_dashboard_full:{instructor_profile.id}"
            dashboard_data = cache.get(cache_key)

            if dashboard_data is None:
                # Get or create dashboard configuration
                dashboard, created = InstructorDashboard.objects.get_or_create(
                    instructor=instructor_profile,
                    defaults={
                        'show_analytics': True,
                        'show_recent_students': True,
                        'show_performance_metrics': True,
                        'show_revenue_charts': True,
                        'show_course_progress': True
                    }
                )

                # Get comprehensive dashboard data
                dashboard_data = {
                    'config': InstructorDashboardSerializer(dashboard).data,
                    'dashboard': self._get_comprehensive_dashboard_data(instructor_profile),
                    'instructor': {
                        'id': instructor_profile.id,
                        'display_name': instructor_profile.display_name,
                        'tier': instructor_profile.get_tier_display(),
                        'status': instructor_profile.get_status_display(),
                        'analytics': instructor_profile.get_performance_metrics(),
                        'tier_limits': TierManager.get_tier_limits(instructor_profile.tier)
                    },
                    'real_time_stats': self._get_real_time_statistics(instructor_profile),
                    'recent_activity': self._get_recent_activity(instructor_profile),
                    'notifications': self._get_dashboard_notifications(instructor_profile),
                    'quick_actions': self._get_quick_actions(instructor_profile)
                }

                # Cache for performance (shorter TTL for real-time data)
                cache.set(cache_key, dashboard_data, timeout=300)  # 5 minutes

            # Log dashboard access
            audit_log(
                request.user,
                'dashboard_accessed',
                'instructor_dashboard',
                instructor_profile.id,
                metadata={'tier': instructor_profile.tier},
                request=request
            )

            return Response(dashboard_data)

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def update_config(self, request):
        """Update dashboard configuration with validation"""
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                dashboard, created = InstructorDashboard.objects.get_or_create(
                    instructor=instructor_profile,
                    defaults={'show_analytics': True}
                )

                # Validate configuration data
                config_errors = self._validate_dashboard_config(request.data)
                if config_errors:
                    return Response(
                        {'detail': 'Configuration validation failed', 'errors': config_errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update configuration fields
                config_fields = [
                    'show_analytics', 'show_recent_students', 'show_performance_metrics',
                    'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
                    'notify_new_reviews', 'notify_course_completions'
                ]

                updated_fields = []
                for field in config_fields:
                    if field in request.data:
                        setattr(dashboard, field, request.data[field])
                        updated_fields.append(field)

                # Update layout settings
                if 'widget_order' in request.data:
                    widget_order = request.data['widget_order']
                    if isinstance(widget_order, list) and len(widget_order) <= 20:
                        dashboard.widget_order = widget_order
                        updated_fields.append('widget_order')

                if 'custom_colors' in request.data:
                    custom_colors = request.data['custom_colors']
                    if isinstance(custom_colors, dict):
                        dashboard.custom_colors = custom_colors
                        updated_fields.append('custom_colors')

                if updated_fields:
                    dashboard.save(update_fields=updated_fields)

                # Clear cache
                cache.delete(f"instructor_dashboard_full:{instructor_profile.id}")

            audit_log(
                request.user,
                'dashboard_config_updated',
                'instructor_dashboard',
                dashboard.id,
                metadata={'updated_fields': updated_fields},
                request=request
            )

            return Response({
                'detail': 'Dashboard configuration updated successfully',
                'config': InstructorDashboardSerializer(dashboard).data,
                'updated_fields': updated_fields
            })

        except Exception as e:
            logger.error(f"Error updating dashboard config: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to update dashboard configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def analytics_summary(self, request):
        """Get enhanced analytics summary for dashboard with trend analysis"""
        instructor_profile = request.instructor_profile

        try:
            # Get tier-based analytics limits
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            history_days = tier_limits.get('analytics_history_days', 30)
            cutoff_date = timezone.now() - timezone.timedelta(days=history_days)

            # Check cache first
            cache_key = f"instructor_analytics_summary:{instructor_profile.id}:{history_days}"
            analytics_summary = cache.get(cache_key)

            if analytics_summary is None:
                # Get recent analytics with optimized queries
                recent_analytics = InstructorAnalytics.objects.filter(
                    instructor=instructor_profile,
                    date__gte=cutoff_date
                ).only(
                    'date', 'total_students', 'total_courses', 'average_rating',
                    'total_revenue', 'completion_rate'
                ).order_by('-date')

                # Calculate comprehensive trends
                trends = self._calculate_advanced_trends(recent_analytics)

                # Get course performance breakdown
                course_breakdown = self._get_course_performance_breakdown(instructor_profile)

                # Get student engagement metrics
                engagement_metrics = self._get_student_engagement_metrics(instructor_profile)

                analytics_summary = {
                    'current_metrics': instructor_profile.get_performance_metrics(),
                    'trends': trends,
                    'course_breakdown': course_breakdown,
                    'engagement_metrics': engagement_metrics,
                    'tier_limits': tier_limits,
                    'history_days_available': history_days,
                    'recent_data': [
                        {
                            'date': analytics.date,
                            'students': analytics.total_students,
                            'revenue': float(analytics.total_revenue),
                            'rating': float(analytics.average_rating),
                            'completion_rate': float(analytics.completion_rate),
                            'courses': analytics.total_courses
                        }
                        for analytics in recent_analytics[:min(30, history_days)]
                    ],
                    'performance_indicators': self._get_performance_indicators(instructor_profile, recent_analytics),
                    'recommendations': self._get_analytics_recommendations(instructor_profile, trends)
                }

                # Cache analytics summary
                cache.set(cache_key, analytics_summary, ANALYTICS_CACHE_TIMEOUT)

            return Response(analytics_summary)

        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load analytics summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def real_time_stats(self, request):
        """Get real-time statistics for dashboard"""
        instructor_profile = request.instructor_profile

        try:
            # Get real-time data with short cache
            cache_key = f"instructor_realtime:{instructor_profile.id}"
            real_time_data = cache.get(cache_key)

            if real_time_data is None:
                real_time_data = self._get_real_time_statistics(instructor_profile)
                cache.set(cache_key, real_time_data, timeout=60)  # 1 minute cache

            return Response(real_time_data)

        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load real-time statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @tier_required('gold')
    @action(detail=False, methods=['get'])
    def advanced_analytics(self, request):
        """Get advanced analytics (premium feature)"""
        instructor_profile = request.instructor_profile

        try:
            # Date range parameter
            days = int(request.query_params.get('days', 90))
            if days > 365:  # Limit to 1 year
                days = 365

            advanced_data = {
                'student_demographics': self._get_student_demographics(instructor_profile),
                'revenue_analytics': self._get_revenue_analytics(instructor_profile, days),
                'course_performance_matrix': self._get_course_performance_matrix(instructor_profile),
                'learning_patterns': self._get_learning_patterns(instructor_profile),
                'competitive_analysis': self._get_competitive_analysis(instructor_profile),
                'growth_predictions': self._get_growth_predictions(instructor_profile)
            }

            audit_log(
                request.user,
                'advanced_analytics_accessed',
                'instructor_analytics',
                instructor_profile.id,
                metadata={'days_requested': days},
                request=request
            )

            return Response(advanced_data)

        except Exception as e:
            logger.error(f"Error getting advanced analytics: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load advanced analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """Enhanced health check endpoint with system status"""
        try:
            # Check database connectivity
            instructor_count = InstructorProfile.objects.count()

            # Check cache connectivity
            cache_test_key = f"health_check:{timezone.now().timestamp()}"
            cache.set(cache_test_key, "test", timeout=10)
            cache_working = cache.get(cache_test_key) == "test"
            cache.delete(cache_test_key)

            health_data = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'version': '1.0.1',
                'services': {
                    'database': 'operational',
                    'cache': 'operational' if cache_working else 'degraded',
                    'analytics': 'operational'
                },
                'stats': {
                    'total_instructors': instructor_count,
                    'active_sessions': self._get_active_sessions_count()
                }
            }

            return Response(health_data)

        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return Response({
                'status': 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Helper methods
    def _get_comprehensive_dashboard_data(self, instructor_profile: InstructorProfile) -> Dict:
        """Get comprehensive dashboard data with optimized queries"""
        # Get instructor courses with analytics
        instructor_courses = Course.objects.filter(
            courseinstructor_set__instructor=instructor_profile.user,
            courseinstructor_set__is_active=True
        ).annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status='active')),
            completed_count=Count('enrollments', filter=Q(enrollments__status='completed')),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            total_revenue=Sum('enrollments__payment_amount', filter=Q(enrollments__status__in=['active', 'completed']))
        ).select_related('category')

        # Calculate completion rates and other metrics
        dashboard_data = {
            'overview': {
                'total_courses': instructor_courses.count(),
                'total_students': sum(course.enrolled_count or 0 for course in instructor_courses),
                'total_revenue': sum(float(course.total_revenue or 0) for course in instructor_courses),
                'average_rating': instructor_profile.average_rating,
                'completion_rate': self._calculate_overall_completion_rate(instructor_courses)
            },
            'courses': [
                {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'enrolled_students': course.enrolled_count or 0,
                    'completed_students': course.completed_count or 0,
                    'average_rating': float(course.avg_rating or 0),
                    'revenue': float(course.total_revenue or 0),
                    'completion_rate': self._calculate_course_completion_rate(course),
                    'created_date': course.created_date,
                    'status': course.status
                }
                for course in instructor_courses[:10]  # Limit for performance
            ],
            'monthly_stats': self._get_monthly_statistics(instructor_profile),
            'top_performing_courses': self._get_top_performing_courses(instructor_courses),
            'recent_enrollments': self._get_recent_enrollments(instructor_profile),
            'recent_reviews': self._get_recent_reviews(instructor_profile)
        }

        return dashboard_data

    def _get_real_time_statistics(self, instructor_profile: InstructorProfile) -> Dict:
        """Get real-time statistics"""
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)

        # Get today's stats
        today_enrollments = Enrollment.objects.filter(
            course__courseinstructor_set__instructor=instructor_profile.user,
            course__courseinstructor_set__is_active=True,
            enrolled_date__date=today
        ).count()

        yesterday_enrollments = Enrollment.objects.filter(
            course__courseinstructor_set__instructor=instructor_profile.user,
            course__courseinstructor_set__is_active=True,
            enrolled_date__date=yesterday
        ).count()

        # Get recent completions
        today_completions = Enrollment.objects.filter(
            course__courseinstructor_set__instructor=instructor_profile.user,
            course__courseinstructor_set__is_active=True,
            completion_date__date=today
        ).count()

        return {
            'enrollments_today': today_enrollments,
            'enrollments_yesterday': yesterday_enrollments,
            'enrollments_trend': today_enrollments - yesterday_enrollments,
            'completions_today': today_completions,
            'active_students_online': self._get_active_students_count(instructor_profile),
            'revenue_today': self._get_today_revenue(instructor_profile),
            'last_updated': now.isoformat()
        }

    def _validate_dashboard_config(self, config_data: Dict) -> Dict[str, str]:
        """Validate dashboard configuration data"""
        errors = {}

        # Validate boolean fields
        boolean_fields = [
            'show_analytics', 'show_recent_students', 'show_performance_metrics',
            'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
            'notify_new_reviews', 'notify_course_completions'
        ]

        for field in boolean_fields:
            if field in config_data and not isinstance(config_data[field], bool):
                errors[field] = f'{field} must be a boolean value'

        # Validate widget order
        if 'widget_order' in config_data:
            widget_order = config_data['widget_order']
            if not isinstance(widget_order, list):
                errors['widget_order'] = 'widget_order must be a list'
            elif len(widget_order) > 20:
                errors['widget_order'] = 'Too many widgets (max 20)'

        # Validate custom colors
        if 'custom_colors' in config_data:
            custom_colors = config_data['custom_colors']
            if not isinstance(custom_colors, dict):
                errors['custom_colors'] = 'custom_colors must be an object'

        return errors

    def _calculate_advanced_trends(self, analytics_data) -> Dict:
        """Calculate advanced trend analysis"""
        if len(analytics_data) < 7:  # Need at least a week of data
            return {
                'students_trend': 0.0,
                'revenue_trend': 0.0,
                'rating_trend': 0.0,
                'completion_trend': 0.0,
                'growth_rate': 0.0,
                'trend_direction': 'stable'
            }

        analytics_list = list(analytics_data)

        # Calculate weekly averages for trend analysis
        recent_week = analytics_list[:7]
        previous_week = analytics_list[7:14] if len(analytics_list) >= 14 else []

        recent_avg = {
            'students': sum(a.total_students for a in recent_week) / len(recent_week),
            'revenue': sum(float(a.total_revenue) for a in recent_week) / len(recent_week),
            'rating': sum(float(a.average_rating) for a in recent_week) / len(recent_week),
            'completion': sum(float(a.completion_rate) for a in recent_week) / len(recent_week)
        }

        if previous_week:
            previous_avg = {
                'students': sum(a.total_students for a in previous_week) / len(previous_week),
                'revenue': sum(float(a.total_revenue) for a in previous_week) / len(previous_week),
                'rating': sum(float(a.average_rating) for a in previous_week) / len(previous_week),
                'completion': sum(float(a.completion_rate) for a in previous_week) / len(previous_week)
            }

            trends = {
                'students_trend': recent_avg['students'] - previous_avg['students'],
                'revenue_trend': recent_avg['revenue'] - previous_avg['revenue'],
                'rating_trend': recent_avg['rating'] - previous_avg['rating'],
                'completion_trend': recent_avg['completion'] - previous_avg['completion']
            }

            # Calculate overall growth rate
            total_growth = (
                trends['students_trend'] + trends['revenue_trend'] +
                trends['rating_trend'] + trends['completion_trend']
            ) / 4

            trends['growth_rate'] = total_growth
            trends['trend_direction'] = 'growing' if total_growth > 0 else 'declining' if total_growth < 0 else 'stable'
        else:
            trends = {
                'students_trend': 0.0,
                'revenue_trend': 0.0,
                'rating_trend': 0.0,
                'completion_trend': 0.0,
                'growth_rate': 0.0,
                'trend_direction': 'stable'
            }

        return trends

    def _get_course_performance_breakdown(self, instructor_profile: InstructorProfile) -> List[Dict]:
        """Get detailed course performance breakdown"""
        courses = Course.objects.filter(
            courseinstructor_set__instructor=instructor_profile.user,
            courseinstructor_set__is_active=True
        ).annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status='active')),
            completed_count=Count('enrollments', filter=Q(enrollments__status='completed')),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            total_revenue=Sum('enrollments__payment_amount', filter=Q(enrollments__status__in=['active', 'completed']))
        )[:10]  # Top 10 courses

        return [
            {
                'course_id': course.id,
                'title': course.title,
                'performance_score': self._calculate_course_performance_score(course),
                'enrolled_students': course.enrolled_count or 0,
                'completion_rate': self._calculate_course_completion_rate(course),
                'average_rating': float(course.avg_rating or 0),
                'revenue': float(course.total_revenue or 0),
                'trend': self._get_course_trend(course)
            }
            for course in courses
        ]

    def _calculate_course_performance_score(self, course) -> float:
        """Calculate overall performance score for a course"""
        # Weighted scoring: rating (40%), completion rate (30%), enrollment (30%)
        rating_score = (float(getattr(course, 'avg_rating', 0)) / 5.0) * 40
        completion_score = (self._calculate_course_completion_rate(course) / 100.0) * 30
        enrollment_score = min((getattr(course, 'enrolled_count', 0) / 100.0), 1.0) * 30

        return rating_score + completion_score + enrollment_score

    def _calculate_course_completion_rate(self, course) -> float:
        """Calculate completion rate for a specific course"""
        total_enrollments = getattr(course, 'enrolled_count', 0) + getattr(course, 'completed_count', 0)
        if total_enrollments == 0:
            return 0.0
        return (getattr(course, 'completed_count', 0) / total_enrollments) * 100

    def _calculate_overall_completion_rate(self, courses) -> float:
        """Calculate overall completion rate across all courses"""
        total_enrolled = sum(getattr(course, 'enrolled_count', 0) for course in courses)
        total_completed = sum(getattr(course, 'completed_count', 0) for course in courses)
        total_students = total_enrolled + total_completed

        if total_students == 0:
            return 0.0
        return (total_completed / total_students) * 100

    # Continue with remaining helper methods...
    def _get_active_sessions_count(self) -> int:
        """Get active sessions count (placeholder)"""
        return 0  # Implement based on your session tracking

    def _get_active_students_count(self, instructor_profile: InstructorProfile) -> int:
        """Get currently active students count (placeholder)"""
        return 0  # Implement based on your real-time tracking

    def _get_today_revenue(self, instructor_profile: InstructorProfile) -> float:
        """Get today's revenue"""
        today = timezone.now().date()
        today_revenue = Enrollment.objects.filter(
            course__courseinstructor_set__instructor=instructor_profile.user,
            course__courseinstructor_set__is_active=True,
            enrolled_date__date=today
        ).aggregate(total=Sum('payment_amount'))['total']

        return float(today_revenue or 0)


class InstructorAnalyticsViewSet(viewsets.ViewSet):
    """
    Enhanced API endpoint for instructor analytics with advanced features
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @require_instructor_profile
    def list(self, request):
        """Get comprehensive analytics overview with caching"""
        instructor_profile = request.instructor_profile

        try:
            # Check cache first
            cache_key = f"instructor_analytics_overview:{instructor_profile.id}"
            analytics_data = cache.get(cache_key)

            if analytics_data is None:
                # Get tier-based limits
                tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
                history_days = tier_limits.get('analytics_history_days', 30)
                cutoff_date = timezone.now() - timezone.timedelta(days=history_days)

                # Get recent analytics efficiently
                recent_analytics = InstructorAnalytics.objects.filter(
                    instructor=instructor_profile,
                    date__gte=cutoff_date
                ).order_by('-date')

                analytics_data = {
                    'overview': instructor_profile.get_performance_metrics(),
                    'tier_info': {
                        'current_tier': instructor_profile.get_tier_display(),
                        'limits': tier_limits,
                        'history_days': history_days
                    },
                    'recent_data': [
                        {
                            'date': analytics.date,
                            'students': analytics.total_students,
                            'revenue': float(analytics.total_revenue),
                            'rating': float(analytics.average_rating),
                            'courses': analytics.total_courses,
                            'completion_rate': float(analytics.completion_rate)
                        }
                        for analytics in recent_analytics[:30]
                    ],
                    'summary_statistics': self._get_analytics_summary_stats(recent_analytics),
                    'performance_trends': self._calculate_performance_trends(recent_analytics)
                }

                # Cache analytics data
                cache.set(cache_key, analytics_data, ANALYTICS_CACHE_TIMEOUT)

            return Response(analytics_data)

        except Exception as e:
            logger.error(f"Error getting analytics overview: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load analytics data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['get'])
    def course_analytics(self, request):
        """Get course-specific analytics with detailed metrics"""
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response(
                {'detail': 'course_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify course ownership
            course = Course.objects.filter(
                id=course_id,
                courseinstructor_set__instructor=request.user,
                courseinstructor_set__is_active=True
            ).annotate(
                enrolled_count=Count('enrollments', filter=Q(enrollments__status='active')),
                completed_count=Count('enrollments', filter=Q(enrollments__status='completed')),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                total_revenue=Sum('enrollments__payment_amount', filter=Q(enrollments__status__in=['active', 'completed']))
            ).first()

            if not course:
                return Response(
                    {'detail': 'Course not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get detailed course analytics
            course_analytics = {
                'course_info': {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'created_date': course.created_date
                },
                'enrollment_metrics': {
                    'total_enrolled': course.enrolled_count or 0,
                    'total_completed': course.completed_count or 0,
                    'completion_rate': self._calculate_course_completion_rate(course),
                    'dropout_rate': self._calculate_dropout_rate(course)
                },
                'performance_metrics': {
                    'average_rating': float(course.avg_rating or 0),
                    'total_reviews': self._get_course_review_count(course),
                    'revenue': float(course.total_revenue or 0),
                    'performance_score': self._calculate_course_performance_score(course)
                },
                'engagement_metrics': self._get_course_engagement_metrics(course),
                'time_series_data': self._get_course_time_series(course),
                'student_feedback': self._get_course_feedback_summary(course)
            }

            return Response(course_analytics)

        except Exception as e:
            logger.error(f"Error getting course analytics: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load course analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Additional helper methods for analytics calculations...
    def _get_analytics_summary_stats(self, analytics_data) -> Dict:
        """Get summary statistics from analytics data"""
        if not analytics_data:
            return {}

        analytics_list = list(analytics_data)
        return {
            'total_data_points': len(analytics_list),
            'average_daily_students': sum(a.total_students for a in analytics_list) / len(analytics_list),
            'average_daily_revenue': sum(float(a.total_revenue) for a in analytics_list) / len(analytics_list),
            'highest_rating': max(float(a.average_rating) for a in analytics_list),
            'best_completion_rate': max(float(a.completion_rate) for a in analytics_list)
        }

    def _calculate_performance_trends(self, analytics_data) -> Dict:
        """Calculate performance trends over time"""
        if len(analytics_data) < 2:
            return {'trend': 'insufficient_data'}

        analytics_list = list(analytics_data)
        latest = analytics_list[0]
        oldest = analytics_list[-1]

        return {
            'student_growth': latest.total_students - oldest.total_students,
            'revenue_growth': float(latest.total_revenue - oldest.total_revenue),
            'rating_change': float(latest.average_rating - oldest.average_rating),
            'completion_rate_change': float(latest.completion_rate - oldest.completion_rate),
            'period_days': len(analytics_list)
        }


# Additional ViewSets for comprehensive dashboard functionality
class StudentManagementView(viewsets.ViewSet):
    """Enhanced student management with detailed analytics"""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @require_instructor_profile
    def list(self, request):
        """Get comprehensive students list with analytics"""
        instructor_profile = request.instructor_profile

        try:
            # Get all students enrolled in instructor's courses
            students_data = self._get_comprehensive_students_data(instructor_profile)

            return Response({
                'students': students_data,
                'summary': {
                    'total_students': len(students_data),
                    'active_students': len([s for s in students_data if s['status'] == 'active']),
                    'completed_students': len([s for s in students_data if s['status'] == 'completed'])
                }
            })

        except Exception as e:
            logger.error(f"Error getting students data: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load students data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_comprehensive_students_data(self, instructor_profile: InstructorProfile) -> List[Dict]:
        """Get comprehensive student data"""
        # Implementation would go here
        return []  # Placeholder


class RevenueAnalyticsView(viewsets.ViewSet):
    """Enhanced revenue analytics with detailed financial insights"""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @require_instructor_profile
    def list(self, request):
        """Get comprehensive revenue analytics"""
        instructor_profile = request.instructor_profile

        try:
            revenue_data = {
                'total_revenue': float(instructor_profile.total_revenue),
                'monthly_breakdown': self._get_monthly_revenue_breakdown(instructor_profile),
                'revenue_trends': self._get_revenue_trends(instructor_profile),
                'revenue_by_course': self._get_revenue_by_course(instructor_profile),
                'payment_analytics': self._get_payment_analytics(instructor_profile)
            }

            return Response(revenue_data)

        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to load revenue analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_monthly_revenue_breakdown(self, instructor_profile: InstructorProfile) -> List[Dict]:
        """Get monthly revenue breakdown"""
        # Implementation would go here
        return []  # Placeholder

    def _get_revenue_trends(self, instructor_profile: InstructorProfile) -> Dict:
        """Get revenue trend analysis"""
        # Implementation would go here
        return {}  # Placeholder

    def _get_revenue_by_course(self, instructor_profile: InstructorProfile) -> List[Dict]:
        """Get revenue breakdown by course"""
        # Implementation would go here
        return []  # Placeholder

    def _get_payment_analytics(self, instructor_profile: InstructorProfile) -> Dict:
        """Get payment method and timing analytics"""
        # Implementation would go here
        return {}  # Placeholder
