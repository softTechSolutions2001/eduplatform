# Minimal URLs for instructor_portal to allow Django to start
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import only the views that exist
from .views import (
    InstructorProfileViewSet, InstructorDashboardViewSet,
    CourseCreationSessionViewSet, CourseTemplateViewSet,
    InstructorCourseViewSet, InstructorModuleViewSet,
    InstructorLessonViewSet, InstructorResourceViewSet
)

app_name = 'instructor_portal'

# Create router for ViewSets
router = DefaultRouter()

# Register the ViewSets that exist
try:
    router.register(r'profile', InstructorProfileViewSet, basename='instructor-profile')
except:
    pass

try:
    router.register(r'dashboard', InstructorDashboardViewSet, basename='instructor-dashboard')
except:
    pass

try:
    router.register(r'sessions', CourseCreationSessionViewSet, basename='creation-session')
except:
    pass

try:
    router.register(r'templates', CourseTemplateViewSet, basename='course-template')
except:
    pass

try:
    router.register(r'courses', InstructorCourseViewSet, basename='instructor-course')
except:
    pass

try:
    router.register(r'modules', InstructorModuleViewSet, basename='instructor-module')
except:
    pass

try:
    router.register(r'lessons', InstructorLessonViewSet, basename='instructor-lesson')
except:
    pass

try:
    router.register(r'resources', InstructorResourceViewSet, basename='instructor-resource')
except:
    pass

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
