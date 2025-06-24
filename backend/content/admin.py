from django.contrib import admin
from .models import (
    Testimonial, PlatformStatistics,
    UserLearningStatistics, InstructorStatistics
)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rating', 'featured', 'created_at')
    list_filter = ('rating', 'featured', 'created_at')
    search_fields = ('name', 'role', 'content')
    list_editable = ('featured',)
    date_hierarchy = 'created_at'


@admin.register(PlatformStatistics)
class PlatformStatisticsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'total_courses', 'total_students',
                    'total_instructors', 'last_updated')
    readonly_fields = ('last_updated',)

    def has_add_permission(self, request):
        # Prevent creating multiple statistics instances
        return PlatformStatistics.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the statistics instance
        return False

    actions = ['update_statistics']

    def update_statistics(self, request, queryset):
        for stats in queryset:
            stats.update_stats()
        self.message_user(request, "Statistics updated successfully.")
    update_statistics.short_description = "Update selected statistics"


@admin.register(UserLearningStatistics)
class UserLearningStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'courses_completed', 'hours_spent',
                    'average_score', 'last_updated')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)


@admin.register(InstructorStatistics)
class InstructorStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'courses_created', 'total_students',
                    'average_rating', 'last_updated')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)
