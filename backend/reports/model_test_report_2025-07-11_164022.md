# Django Model Test Report

## Document Information
- **Date Generated**: 2025-07-11_164022
- **Test Timestamp**: 2025-07-11 16:40:22 UTC
- **Django Version**: 5.2

## Purpose
This document provides a comprehensive analysis of all Django models in the project, testing their ability to be instantiated without errors. This serves as a health check for the entire data model, ensuring that:

- All models can be created with valid data
- Field constraints are properly defined
- Foreign key relationships work correctly
- No circular dependencies exist
- Database schema is consistent with model definitions

## Executive Summary
- **Total Models Tested**: 69
- **Passed**: 64 (92.8%)
- **Failed**: 0
- **Skipped**: 5
- **Overall Status**: ✅ HEALTHY

## Results by Application

### ✅ admin
- **Total Models**: 1
- **Passed**: 0 (0.0%)
- **Failed**: 0
- **Skipped**: 1

### ✅ auth
- **Total Models**: 2
- **Passed**: 0 (0.0%)
- **Failed**: 0
- **Skipped**: 2

### ✅ contenttypes
- **Total Models**: 1
- **Passed**: 0 (0.0%)
- **Failed**: 0
- **Skipped**: 1

### ✅ sessions
- **Total Models**: 1
- **Passed**: 0 (0.0%)
- **Failed**: 0
- **Skipped**: 1

### ✅ sites
- **Total Models**: 1
- **Passed**: 1 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ token_blacklist
- **Total Models**: 2
- **Passed**: 2 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ django_celery_beat
- **Total Models**: 6
- **Passed**: 6 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ social_django
- **Total Models**: 5
- **Passed**: 5 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ account
- **Total Models**: 2
- **Passed**: 2 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ socialaccount
- **Total Models**: 3
- **Passed**: 3 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ users
- **Total Models**: 7
- **Passed**: 7 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ courses
- **Total Models**: 22
- **Passed**: 22 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ instructor_portal
- **Total Models**: 11
- **Passed**: 11 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ content
- **Total Models**: 4
- **Passed**: 4 (100.0%)
- **Failed**: 0
- **Skipped**: 0

### ✅ ai_course_builder
- **Total Models**: 1
- **Passed**: 1 (100.0%)
- **Failed**: 0
- **Skipped**: 0

## ✅ Successful Models (64)
- **sites.Site** - 3 fields
- **token_blacklist.OutstandingToken** - 6 fields
- **token_blacklist.BlacklistedToken** - 3 fields
- **django_celery_beat.SolarSchedule** - 4 fields
- **django_celery_beat.IntervalSchedule** - 3 fields
- **django_celery_beat.ClockedSchedule** - 2 fields
- **django_celery_beat.CrontabSchedule** - 7 fields
- **django_celery_beat.PeriodicTasks** - 2 fields
- **django_celery_beat.PeriodicTask** - 23 fields
- **social_django.UserSocialAuth** - 7 fields
- **social_django.Nonce** - 4 fields
- **social_django.Association** - 7 fields
- **social_django.Code** - 5 fields
- **social_django.Partial** - 6 fields
- **account.EmailAddress** - 5 fields
- **account.EmailConfirmation** - 5 fields
- **socialaccount.SocialApp** - 8 fields
- **socialaccount.SocialAccount** - 7 fields
- **socialaccount.SocialToken** - 6 fields
- **users.CustomUser** - 15 fields
- **users.Profile** - 23 fields
- **users.EmailVerification** - 7 fields
- **users.PasswordReset** - 8 fields
- **users.LoginLog** - 6 fields
- **users.UserSession** - 12 fields
- **users.Subscription** - 10 fields
- **courses.Category** - 11 fields
- **courses.Course** - 37 fields
- **courses.Module** - 10 fields
- **courses.Lesson** - 18 fields
- **courses.Resource** - 17 fields
- **courses.Enrollment** - 12 fields
- **courses.Progress** - 11 fields
- **courses.Certificate** - 10 fields
- **courses.CourseProgress** - 15 fields
- **courses.Assessment** - 13 fields
- **courses.Question** - 11 fields
- **courses.Answer** - 9 fields
- **courses.AssessmentAttempt** - 16 fields
- **courses.AttemptAnswer** - 11 fields
- **courses.Review** - 13 fields
- **courses.Note** - 9 fields
- **courses.UserActivity** - 10 fields
- **courses.CourseStats** - 11 fields
- **courses.UserStats** - 11 fields
- **courses.Notification** - 11 fields
- **courses.Bookmark** - 11 fields
- **courses.UserPreference** - 17 fields
- **instructor_portal.InstructorProfile** - 24 fields
- **instructor_portal.InstructorAnalytics** - 12 fields
- **instructor_portal.InstructorAnalyticsHistory** - 10 fields
- **instructor_portal.CourseInstructor** - 12 fields
- **instructor_portal.InstructorDashboard** - 14 fields
- **instructor_portal.CourseCreationSession** - 20 fields
- **instructor_portal.CourseTemplate** - 14 fields
- **instructor_portal.DraftCourseContent** - 14 fields
- **instructor_portal.CourseContentDraft** - 15 fields
- **instructor_portal.InstructorNotification** - 17 fields
- **instructor_portal.InstructorSession** - 13 fields
- **content.Testimonial** - 9 fields
- **content.PlatformStatistics** - 7 fields
- **content.UserLearningStatistics** - 6 fields
- **content.InstructorStatistics** - 6 fields
- **ai_course_builder.AICourseBuilderDraft** - 20 fields

## ⏭️ Skipped Models (5)
- **admin.LogEntry** - Internal Django model
- **auth.Permission** - Internal Django model
- **auth.Group** - Internal Django model
- **contenttypes.ContentType** - Internal Django model
- **sessions.Session** - Internal Django model

## Error Classification
- **🔧 Code/Definition Errors**: Issues with model definitions, field configurations, or code logic
- **📊 Data/Constraint Errors**: Database constraints, validation rules, or data integrity issues

## Recommendations

### For Failed Models
1. **Code/Definition Errors** 🔧
   - Review field definitions and model configurations
   - Check for missing required fields or invalid field types
   - Verify custom model methods and properties

2. **Data/Constraint Errors** 📊
   - Review database constraints and validation rules
   - Check for conflicting unique constraints
   - Verify foreign key relationships and cascading rules

### For Healthy Models
1. **Maintain Standards** - Continue following current model patterns
2. **Regular Testing** - Run this report periodically to catch regressions
3. **Documentation** - Keep model relationships well documented

## Next Steps
- ✅ All models are healthy! Continue with regular monitoring.
- Schedule regular model health checks (recommended: before each deployment)
- Consider integrating this report into your CI/CD pipeline
- Review and update model documentation based on findings

---
*Report generated automatically by Django Model Test Management Command v2.0*
*For questions or improvements, contact your development team*
