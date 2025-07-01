#
# File Path: instructor_portal/serializers/profile.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 13:35:44
# Date Revised: 2025-06-27 06:16:38
# Current Date and Time (UTC): 2025-06-27 06:16:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:16:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Profile-related serializers for instructor_portal
# Split from original serializers.py maintaining exact code compatibility

import logging
from django.conf import settings
from rest_framework import serializers
from courses.models import Category
from ..models import InstructorProfile

logger = logging.getLogger(__name__)

# Get MAX_EXPERIENCE_YEARS from settings if available, otherwise use default
MAX_EXPERIENCE_YEARS = getattr(settings, 'MAX_INSTRUCTOR_EXPERIENCE_YEARS', 50)

class InstructorProfileSerializer(serializers.ModelSerializer):
    """Serializer for instructor profile management"""
    expertise_areas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    expertise_areas_display = serializers.StringRelatedField(
        source='expertise_areas',
        many=True,
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    performance_metrics = serializers.SerializerMethodField()
    tier_benefits = serializers.SerializerMethodField()
    next_tier_requirements = serializers.SerializerMethodField()

    # Re-added analytics counters for backward compatibility
    total_students = serializers.SerializerMethodField()
    total_courses = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = [
            'id', 'display_name', 'bio', 'title', 'organization', 'years_experience',
            'website', 'linkedin_profile', 'twitter_handle', 'profile_image', 'cover_image',
            'status', 'status_display', 'is_verified', 'tier', 'tier_display',
            'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue',
            'email_notifications', 'marketing_emails', 'public_profile',
            'expertise_areas', 'expertise_areas_display', 'performance_metrics',
            'tier_benefits', 'next_tier_requirements',
            'created_date', 'updated_date', 'last_login'
        ]
        read_only_fields = [
            'id', 'status', 'is_verified', 'tier', 'total_students', 'total_courses',
            'average_rating', 'total_reviews', 'total_revenue', 'created_date', 'updated_date'
        ]

    def get_performance_metrics(self, obj):
        """Get comprehensive performance metrics"""
        try:
            if hasattr(obj, 'analytics'):
                return obj.analytics.get_performance_metrics()
            return {}
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

    # Added methods to get analytics counters
    def get_total_students(self, obj):
        """Get total students count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_students
        return 0

    def get_total_courses(self, obj):
        """Get total courses count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_courses
        return 0

    def get_average_rating(self, obj):
        """Get average rating from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.average_rating
        return 0.0

    def get_total_reviews(self, obj):
        """Get total reviews count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_reviews
        return 0

    def get_total_revenue(self, obj):
        """Get total revenue from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_revenue
        return 0.0

    def get_tier_benefits(self, obj):
        """Get benefits for current tier"""
        tier_benefits = {
            InstructorProfile.Tier.BRONZE: {
                'max_courses': 3,
                'max_file_size_mb': 10,
                'analytics_history_days': 30,
                'features': ['Basic analytics', 'Course creation', 'Student management']
            },
            InstructorProfile.Tier.SILVER: {
                'max_courses': 10,
                'max_file_size_mb': 50,
                'analytics_history_days': 90,
                'features': ['Advanced analytics', 'Course cloning', 'Revenue reports', 'Bulk operations']
            },
            InstructorProfile.Tier.GOLD: {
                'max_courses': 25,
                'max_file_size_mb': 100,
                'analytics_history_days': 180,
                'features': ['Premium analytics', 'AI course builder', 'Advanced imports', 'Co-instructor support']
            },
            InstructorProfile.Tier.PLATINUM: {
                'max_courses': 100,
                'max_file_size_mb': 500,
                'analytics_history_days': 365,
                'features': ['Enterprise analytics', 'Custom templates', 'API access', 'Priority support']
            },
            InstructorProfile.Tier.DIAMOND: {
                'max_courses': 1000,
                'max_file_size_mb': 1024,
                'analytics_history_days': 730,
                'features': ['Complete feature access', 'White-label options', 'Dedicated support', 'Beta features']
            }
        }
        return tier_benefits.get(obj.tier, tier_benefits[InstructorProfile.Tier.BRONZE])

    def get_next_tier_requirements(self, obj):
        """Get requirements for next tier"""
        tier_order = [
            InstructorProfile.Tier.BRONZE,
            InstructorProfile.Tier.SILVER,
            InstructorProfile.Tier.GOLD,
            InstructorProfile.Tier.PLATINUM,
            InstructorProfile.Tier.DIAMOND
        ]

        current_index = tier_order.index(obj.tier)
        if current_index >= len(tier_order) - 1:
            return None

        next_tier = tier_order[current_index + 1]
        requirements = {
            InstructorProfile.Tier.SILVER: {
                'min_students': 50,
                'min_courses': 2,
                'min_rating': 3.5,
                'min_reviews': 10
            },
            InstructorProfile.Tier.GOLD: {
                'min_students': 100,
                'min_courses': 5,
                'min_rating': 4.0,
                'min_reviews': 25
            },
            InstructorProfile.Tier.PLATINUM: {
                'min_students': 500,
                'min_courses': 10,
                'min_rating': 4.5,
                'min_reviews': 100
            },
            InstructorProfile.Tier.DIAMOND: {
                'min_students': 1000,
                'min_courses': 20,
                'min_rating': 4.5,
                'min_reviews': 200
            }
        }

        req = requirements.get(next_tier, {})
        analytics = getattr(obj, 'analytics', None)

        progress = {
            'next_tier': next_tier,
            'requirements': req,
            'current_progress': {
                'students': analytics.total_students if analytics else 0,
                'courses': analytics.total_courses if analytics else 0,
                'rating': float(analytics.average_rating) if analytics else 0.0,
                'reviews': analytics.total_reviews if analytics else 0
            }
        }
        return progress

    def validate_bio(self, value):
        """Validate instructor bio with tier requirements"""
        if value and len(value) < 50:
            if self.instance and self.instance.status == InstructorProfile.Status.ACTIVE:
                raise serializers.ValidationError("Active instructors must have a bio of at least 50 characters")
        return value

    def validate_years_experience(self, value):
        """Validate years of experience using configurable maximum"""
        if value is not None and (value < 0 or value > MAX_EXPERIENCE_YEARS):
            raise serializers.ValidationError(f"Years of experience must be between 0 and {MAX_EXPERIENCE_YEARS}")
        return value

    def validate(self, data):
        """Enhanced validation for instructor profile"""
        # Active instructors need proper bio
        if data.get('status') == InstructorProfile.Status.ACTIVE:
            bio = data.get('bio', getattr(self.instance, 'bio', ''))
            if len(bio) < 100:
                raise serializers.ValidationError(
                    {'bio': 'Active instructors need detailed bio (100+ characters)'}
                )

            # Check for profile image
            profile_image = data.get('profile_image', getattr(self.instance, 'profile_image', None))
            if not profile_image:
                raise serializers.ValidationError(
                    {'profile_image': 'Active instructors must upload profile image'}
                )

        return data

    def save(self, **kwargs):
        """Override save to update analytics with optimization"""
        instance = super().save(**kwargs)

        # Check if any fields that should trigger analytics update changed
        analytics_trigger_fields = ['display_name', 'profile_image', 'status', 'tier']
        should_update = False

        if hasattr(self, '_validated_data'):  # Check if we have data changes
            for field in analytics_trigger_fields:
                if field in self._validated_data:
                    should_update = True
                    break

        # Update analytics only when needed
        if should_update and hasattr(instance, 'analytics'):
            instance.analytics.update_analytics()

        return instance
