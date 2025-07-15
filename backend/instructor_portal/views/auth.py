#
# File Path: instructor_portal/views/auth.py
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
# Authentication views for instructor_portal
# COMPLETELY REVISED: Full authentication workflows with security hardening
# Maintains 100% backward compatibility with enhanced functionality

import logging
import uuid
import re
from typing import Dict, Any, Optional
from datetime import timedelta

from django.contrib.auth import get_user_model, authenticate, login
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.core.cache import cache
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import ValidationError, PermissionDenied

from ..models import InstructorProfile, TierManager
from ..serializers import InstructorProfileSerializer  # InstructorRegistrationSerializer not found in refactored codebase
from .mixins import (
    audit_log, scrub_sensitive_data, validate_user_permission,
    get_instructor_profile, require_instructor_profile
)

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom throttle classes for authentication endpoints
class AuthRateThrottle(AnonRateThrottle):
    scope = 'auth'
    rate = '10/hour'

class VerificationRateThrottle(AnonRateThrottle):
    scope = 'verification'
    rate = '5/hour'


class InstructorRegistrationView(APIView):
    """
    Enhanced instructor registration with comprehensive validation
    COMPLETELY REVISED: Full workflow implementation
    """
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        """Register new instructor with validation and email verification"""
        try:
            # Extract and validate registration data
            email = request.data.get('email', '').strip().lower()
            password = request.data.get('password', '')
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            display_name = request.data.get('display_name', '').strip()
            bio = request.data.get('bio', '').strip()
            expertise_areas = request.data.get('expertise_areas', [])

            # Comprehensive input validation
            validation_errors = self._validate_registration_data({
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'display_name': display_name,
                'bio': bio,
                'expertise_areas': expertise_areas
            })

            if validation_errors:
                audit_log(
                    None,
                    'instructor_registration_failed',
                    'user',
                    metadata={'email': email, 'errors': validation_errors},
                    success=False,
                    request=request
                )
                return Response(
                    {'detail': 'Validation failed', 'errors': validation_errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                audit_log(
                    None,
                    'instructor_registration_duplicate',
                    'user',
                    metadata={'email': email},
                    success=False,
                    request=request
                )
                return Response(
                    {'detail': 'An account with this email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and instructor profile in transaction
            with transaction.atomic():
                # Create user account
                user = User.objects.create_user(
                    username=email,  # Use email as username
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=False  # Require email verification
                )

                # Generate display name if not provided
                if not display_name:
                    display_name = f"{first_name} {last_name}".strip()
                    if not display_name:
                        display_name = email.split('@')[0]

                # Create instructor profile
                instructor_profile = InstructorProfile.objects.create(
                    user=user,
                    display_name=display_name,
                    bio=bio,
                    expertise_areas=expertise_areas,
                    status=InstructorProfile.Status.PENDING,
                    tier=InstructorProfile.Tier.BRONZE,  # Default tier
                    email_notifications=True,
                    marketing_emails=False,
                    public_profile=True
                )

                # Generate verification token
                verification_token = self._generate_verification_token(user)

                # Cache verification token
                cache_key = f"instructor_verification:{verification_token}"
                cache.set(cache_key, {
                    'user_id': user.id,
                    'email': email,
                    'created_at': timezone.now().isoformat()
                }, timeout=86400)  # 24 hours

                # Send verification email
                self._send_verification_email(user, verification_token)

            # Log successful registration
            audit_log(
                user,
                'instructor_registration_success',
                'instructor_profile',
                instructor_profile.id,
                metadata={
                    'email': email,
                    'display_name': display_name,
                    'verification_token_sent': True
                },
                success=True,
                request=request
            )

            return Response({
                'detail': 'Registration successful',
                'message': 'Please check your email to verify your account',
                'user_id': user.id,
                'verification_required': True,
                'next_step': 'email_verification'
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Database integrity error during registration: {e}")
            return Response(
                {'detail': 'Registration failed due to a database error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}", exc_info=True)
            return Response(
                {'detail': 'Registration failed due to an unexpected error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Comprehensive validation of registration data"""
        errors = {}

        # Email validation
        email = data.get('email', '')
        if not email:
            errors['email'] = 'Email is required'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Invalid email format'
        elif len(email) > 254:
            errors['email'] = 'Email address too long'

        # Password validation
        password = data.get('password', '')
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        elif not re.search(r'[A-Z]', password):
            errors['password'] = 'Password must contain at least one uppercase letter'
        elif not re.search(r'[a-z]', password):
            errors['password'] = 'Password must contain at least one lowercase letter'
        elif not re.search(r'\d', password):
            errors['password'] = 'Password must contain at least one number'

        # Name validation
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        if not first_name:
            errors['first_name'] = 'First name is required'
        elif len(first_name) > 50:
            errors['first_name'] = 'First name too long (max 50 characters)'

        if not last_name:
            errors['last_name'] = 'Last name is required'
        elif len(last_name) > 50:
            errors['last_name'] = 'Last name too long (max 50 characters)'

        # Display name validation
        display_name = data.get('display_name', '').strip()
        if display_name and len(display_name) > 100:
            errors['display_name'] = 'Display name too long (max 100 characters)'

        # Bio validation
        bio = data.get('bio', '').strip()
        if bio and len(bio) > 1000:
            errors['bio'] = 'Bio too long (max 1000 characters)'

        # Expertise areas validation
        expertise_areas = data.get('expertise_areas', [])
        if expertise_areas:
            if not isinstance(expertise_areas, list):
                errors['expertise_areas'] = 'Expertise areas must be a list'
            elif len(expertise_areas) > 10:
                errors['expertise_areas'] = 'Too many expertise areas (max 10)'
            else:
                for i, area in enumerate(expertise_areas):
                    if not isinstance(area, str) or len(area.strip()) == 0:
                        errors['expertise_areas'] = f'Invalid expertise area at position {i}'
                        break
                    elif len(area.strip()) > 50:
                        errors['expertise_areas'] = f'Expertise area {i} too long (max 50 characters)'
                        break

        return errors

    def _generate_verification_token(self, user: User) -> str:
        """Generate secure verification token"""
        return str(uuid.uuid4()).replace('-', '')

    def _send_verification_email(self, user: User, verification_token: str):
        """Send verification email to user"""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token}"

            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': getattr(settings, 'SITE_NAME', 'Instructor Portal'),
                'expiry_hours': 24
            }

            subject = f"Verify your {context['site_name']} instructor account"
            html_message = render_to_string('emails/instructor_verification.html', context)
            plain_message = render_to_string('emails/instructor_verification.txt', context)

            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            logger.info(f"Verification email sent to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            # Don't raise exception as registration was successful


class InstructorVerificationView(APIView):
    """
    Enhanced email verification with comprehensive validation
    COMPLETELY REVISED: Full verification workflow
    """
    permission_classes = [AllowAny]
    throttle_classes = [VerificationRateThrottle]

    def get(self, request, verification_token=None):
        """Verify email with token"""
        if not verification_token:
            return Response(
                {'detail': 'Verification token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get cached verification data
            cache_key = f"instructor_verification:{verification_token}"
            verification_data = cache.get(cache_key)

            if not verification_data:
                audit_log(
                    None,
                    'instructor_verification_failed',
                    'user',
                    metadata={'token': verification_token[:8] + '...', 'reason': 'token_expired'},
                    success=False,
                    request=request
                )
                return Response(
                    {'detail': 'Verification token is invalid or has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get user
            user_id = verification_data.get('user_id')
            try:
                user = User.objects.select_related('instructor_profile').get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if already verified
            if user.is_active:
                return Response(
                    {'detail': 'Email already verified'},
                    status=status.HTTP_200_OK
                )

            # Activate user and update instructor profile
            with transaction.atomic():
                user.is_active = True
                user.save(update_fields=['is_active'])

                # Update instructor profile status
                instructor_profile = user.instructor_profile
                instructor_profile.status = InstructorProfile.Status.ACTIVE
                instructor_profile.verified_at = timezone.now()
                instructor_profile.save(update_fields=['status', 'verified_at'])

                # Clear verification token
                cache.delete(cache_key)

                # Clear any cached profile data
                cache.delete(f"instructor_profile:{user.id}")
                cache.delete(f"instructor_profile_status:{user.id}")

            # Log successful verification
            audit_log(
                user,
                'instructor_verification_success',
                'instructor_profile',
                instructor_profile.id,
                metadata={'email': user.email},
                success=True,
                request=request
            )

            return Response({
                'detail': 'Email verification successful',
                'message': 'Your instructor account is now active',
                'user_id': user.id,
                'status': 'verified',
                'next_step': 'complete_profile'
            })

        except Exception as e:
            logger.error(f"Error during email verification: {e}", exc_info=True)
            return Response(
                {'detail': 'Verification failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Resend verification email"""
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response(
                {'detail': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.select_related('instructor_profile').get(
                email=email,
                is_active=False
            )

            # Check rate limiting
            rate_limit_key = f"verification_resend:{email}"
            if cache.get(rate_limit_key):
                return Response(
                    {'detail': 'Please wait before requesting another verification email'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Generate new verification token
            verification_token = str(uuid.uuid4()).replace('-', '')

            # Cache new verification token
            cache_key = f"instructor_verification:{verification_token}"
            cache.set(cache_key, {
                'user_id': user.id,
                'email': email,
                'created_at': timezone.now().isoformat()
            }, timeout=86400)

            # Send verification email
            self._send_verification_email(user, verification_token)

            # Set rate limit
            cache.set(rate_limit_key, True, timeout=300)  # 5 minutes

            audit_log(
                user,
                'instructor_verification_resent',
                'user',
                user.id,
                metadata={'email': email},
                request=request
            )

            return Response({
                'detail': 'Verification email sent',
                'message': 'Please check your email for the verification link'
            })

        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                'detail': 'If an account with this email exists, a verification email will be sent'
            })
        except Exception as e:
            logger.error(f"Error resending verification email: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to resend verification email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_verification_email(self, user, verification_token):
        """Send verification email (same as registration)"""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token}"

            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': getattr(settings, 'SITE_NAME', 'Instructor Portal'),
                'expiry_hours': 24
            }

            subject = f"Verify your {context['site_name']} instructor account"
            html_message = render_to_string('emails/instructor_verification.html', context)
            plain_message = render_to_string('emails/instructor_verification.txt', context)

            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")


class InstructorApprovalView(APIView):
    """
    Enhanced instructor approval system
    COMPLETELY REVISED: Full approval workflow for admin use
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        """Approve or reject instructor application"""
        # Only staff can approve instructors
        if not request.user.is_staff:
            return Response(
                {'detail': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        instructor_id = request.data.get('instructor_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        reason = request.data.get('reason', '').strip()

        if not instructor_id:
            return Response(
                {'detail': 'instructor_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action not in ['approve', 'reject']:
            return Response(
                {'detail': 'action must be either "approve" or "reject"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instructor_profile = get_object_or_404(
                InstructorProfile.objects.select_related('user'),
                id=instructor_id
            )

            # Check current status
            if instructor_profile.status not in [
                InstructorProfile.Status.PENDING,
                InstructorProfile.Status.UNDER_REVIEW
            ]:
                return Response(
                    {'detail': f'Instructor is already {instructor_profile.get_status_display()}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                if action == 'approve':
                    instructor_profile.status = InstructorProfile.Status.ACTIVE
                    instructor_profile.approved_at = timezone.now()
                    instructor_profile.approved_by = request.user

                    # Send approval email
                    self._send_approval_email(instructor_profile.user, approved=True)

                    audit_action = 'instructor_approved'
                    response_detail = 'Instructor approved successfully'

                elif action == 'reject':
                    instructor_profile.status = InstructorProfile.Status.REJECTED
                    instructor_profile.rejection_reason = reason

                    # Send rejection email
                    self._send_approval_email(instructor_profile.user, approved=False, reason=reason)

                    audit_action = 'instructor_rejected'
                    response_detail = 'Instructor application rejected'

                instructor_profile.save(update_fields=[
                    'status', 'approved_at', 'approved_by', 'rejection_reason'
                ])

                # Clear caches
                cache.delete(f"instructor_profile:{instructor_profile.user.id}")
                cache.delete(f"instructor_profile_status:{instructor_profile.user.id}")

            # Log the action
            audit_log(
                request.user,
                audit_action,
                'instructor_profile',
                instructor_profile.id,
                metadata={
                    'instructor_email': instructor_profile.user.email,
                    'reason': reason,
                    'action': action
                },
                request=request
            )

            return Response({
                'detail': response_detail,
                'instructor_id': instructor_profile.id,
                'new_status': instructor_profile.get_status_display(),
                'action_performed': action
            })

        except Exception as e:
            logger.error(f"Error processing instructor approval: {e}", exc_info=True)
            return Response(
                {'detail': 'Approval processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """Get pending instructor applications"""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            pending_instructors = InstructorProfile.objects.filter(
                status__in=[
                    InstructorProfile.Status.PENDING,
                    InstructorProfile.Status.UNDER_REVIEW
                ]
            ).select_related('user').order_by('created_date')

            applications = []
            for profile in pending_instructors:
                applications.append({
                    'id': profile.id,
                    'user': {
                        'id': profile.user.id,
                        'email': profile.user.email,
                        'first_name': profile.user.first_name,
                        'last_name': profile.user.last_name,
                        'date_joined': profile.user.date_joined
                    },
                    'display_name': profile.display_name,
                    'bio': profile.bio,
                    'expertise_areas': profile.expertise_areas,
                    'status': profile.get_status_display(),
                    'created_date': profile.created_date,
                    'tier': profile.get_tier_display()
                })

            return Response({
                'pending_applications': applications,
                'total_count': len(applications)
            })

        except Exception as e:
            logger.error(f"Error fetching pending applications: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to fetch pending applications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_approval_email(self, user, approved: bool, reason: str = ''):
        """Send approval/rejection email"""
        try:
            context = {
                'user': user,
                'approved': approved,
                'reason': reason,
                'site_name': getattr(settings, 'SITE_NAME', 'Instructor Portal'),
                'login_url': f"{settings.FRONTEND_URL}/login"
            }

            if approved:
                subject = f"Your {context['site_name']} instructor application has been approved!"
                template_base = 'emails/instructor_approved'
            else:
                subject = f"Your {context['site_name']} instructor application"
                template_base = 'emails/instructor_rejected'

            html_message = render_to_string(f'{template_base}.html', context)
            plain_message = render_to_string(f'{template_base}.txt', context)

            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

        except Exception as e:
            logger.error(f"Failed to send approval email: {e}")


class InstructorStatusView(APIView):
    """
    Enhanced instructor status checking
    COMPLETELY REVISED: Comprehensive status information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current instructor status and profile information"""
        try:
            instructor_profile = get_instructor_profile(request.user)

            if not instructor_profile:
                return Response({
                    'has_instructor_profile': False,
                    'status': 'no_profile',
                    'message': 'No instructor profile found',
                    'next_steps': ['Create instructor profile']
                })

            # Get tier information
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)

            # Build comprehensive status response
            status_data = {
                'has_instructor_profile': True,
                'instructor_id': instructor_profile.id,
                'status': instructor_profile.status,
                'status_display': instructor_profile.get_status_display(),
                'tier': instructor_profile.tier,
                'tier_display': instructor_profile.get_tier_display(),
                'tier_limits': tier_limits,
                'is_active': instructor_profile.status == InstructorProfile.Status.ACTIVE,
                'is_verified': instructor_profile.is_verified,
                'profile_completion': self._calculate_profile_completion(instructor_profile),
                'user_info': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'is_email_verified': request.user.is_active,
                    'display_name': instructor_profile.display_name,
                    'joined_date': instructor_profile.created_date
                },
                'analytics': instructor_profile.get_performance_metrics(),
                'permissions': {
                    'can_create_courses': instructor_profile.status == InstructorProfile.Status.ACTIVE,
                    'can_view_analytics': instructor_profile.status == InstructorProfile.Status.ACTIVE,
                    'can_manage_students': instructor_profile.status == InstructorProfile.Status.ACTIVE
                }
            }

            # Add status-specific information
            if instructor_profile.status == InstructorProfile.Status.PENDING:
                status_data['message'] = 'Your instructor application is pending review'
                status_data['next_steps'] = ['Wait for admin approval']

            elif instructor_profile.status == InstructorProfile.Status.UNDER_REVIEW:
                status_data['message'] = 'Your instructor application is under review'
                status_data['next_steps'] = ['Wait for admin approval']

            elif instructor_profile.status == InstructorProfile.Status.ACTIVE:
                status_data['message'] = 'Your instructor account is active'
                next_steps = []
                if status_data['profile_completion'] < 100:
                    next_steps.append('Complete your profile')
                if instructor_profile.total_courses == 0:
                    next_steps.append('Create your first course')
                status_data['next_steps'] = next_steps

            elif instructor_profile.status == InstructorProfile.Status.REJECTED:
                status_data['message'] = 'Your instructor application was rejected'
                status_data['rejection_reason'] = instructor_profile.rejection_reason
                status_data['next_steps'] = ['Contact support for assistance']

            elif instructor_profile.status == InstructorProfile.Status.SUSPENDED:
                status_data['message'] = 'Your instructor account is suspended'
                status_data['next_steps'] = ['Contact support']

            # Log status check
            audit_log(
                request.user,
                'instructor_status_checked',
                'instructor_profile',
                instructor_profile.id,
                metadata={'status': instructor_profile.status},
                request=request
            )

            return Response(status_data)

        except Exception as e:
            logger.error(f"Error getting instructor status: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to retrieve instructor status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_profile_completion(self, instructor_profile: InstructorProfile) -> int:
        """Calculate profile completion percentage"""
        total_fields = 8
        completed_fields = 0

        # Required fields
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
        if user.is_active:  # Email verified
            completed_fields += 1

        # Status fields
        if instructor_profile.status == InstructorProfile.Status.ACTIVE:
            completed_fields += 1
        if instructor_profile.is_verified:
            completed_fields += 1

        return int((completed_fields / total_fields) * 100)
