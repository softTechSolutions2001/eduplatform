"""
File: backend/users/serializers.py
Purpose: Serializers for user data, authentication, and subscription management in EduPlatform
Date Revised: 2025-06-21 18:40:49 UTC
Revised By: sujibeautysaloncontinue
Environment: Production
Version: 2.1.1 - Complete Compatibility Fix

Changes in this version:
- FIXED: UserSessionSerializer now correctly handles login_method field
- ADDED: ResendVerificationSerializer for email verification resend
- IMPROVED: PasswordResetConfirmSerializer stores reset token for view access
- ENHANCED: UserSerializer now handles missing profile/subscription gracefully
- ADDED: Email normalization in all email fields

Previous Version: 2.1.0 (2025-06-21 14:57:11 UTC)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile, EmailVerification, PasswordReset, Subscription, UserSession

User = get_user_model()

# Constants for validation
PASSWORD_MIN_LENGTH = 8


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.

    This excludes user, created_at and updated_at fields as they're handled elsewhere
    or not needed by the frontend.
    """
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for user subscription information.

    This adds computed fields needed by the frontend:
    - is_active: Whether subscription is currently active (UPDATED: now uses @property)
    - days_remaining: Days left in current subscription period
    """
    # Computed fields
    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'tier', 'status', 'start_date', 'end_date',
            'is_auto_renew', 'last_payment_date',
            'is_active', 'days_remaining'
        ]

    def get_is_active(self, obj):
        """
        Determine if subscription is active.
        UPDATED: Now uses @property instead of method call.
        """
        return obj.is_active

    def get_days_remaining(self, obj):
        """Get days remaining in subscription"""
        return obj.days_remaining


class UserSerializer(serializers.ModelSerializer):
    """
    Base serializer for user information.

    This provides the standard user fields needed by the frontend.
    """
    profile = ProfileSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)

    def to_representation(self, instance):
        """Ensure profile and subscription are properly represented"""
        data = super().to_representation(instance)

        # If profile doesn't exist, return empty dict instead of null
        if data['profile'] is None:
            data['profile'] = {}

        # If subscription doesn't exist, return empty dict instead of null
        if data['subscription'] is None:
            data['subscription'] = {}

        return data

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_email_verified', 'date_joined', 'last_login',
            'profile', 'subscription'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_email_verified',
        ]


class UserDetailSerializer(UserSerializer):
    """
    Extended user serializer with more detailed information.

    This adds any additional user information needed by the frontend.
    """
    class Meta(UserSerializer.Meta):
        # Same as UserSerializer but could be extended with additional fields
        pass


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This handles:
    - Password validation and confirmation
    - Creation of related profile
    - Initial user setup
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True}
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        # Check if email is already registered
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email address already registered")

        # Normalize email (lowercase domain part)
        value = value.lower()

        return value

    def validate_password(self, value):
        """Validate password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        if len(value) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
            )

        return value

    def validate(self, data):
        """
        Validate that passwords match and the role is valid
        """
        if data.get('password') != data.pop('password_confirm'):
            raise serializers.ValidationError(
                {"password_confirm": "Password fields didn't match."}
            )

        # Validate role - users can only register as students or instructors
        valid_roles = ['student', 'instructor']
        if data.get('role') not in valid_roles:
            raise serializers.ValidationError(
                {"role": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}
            )

        return data

    def create(self, validated_data):
        """
        Create a new user with encrypted password and initial profile.
        Profile is automatically created via signal in CustomUserManager.
        Subscription is created in the view via Subscription.create_for_user().
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
        )

        # Note: Subscription creation is handled in RegisterView.create()
        # via Subscription.create_for_user(user) to avoid duplication

        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.

    This allows updating the user's name and profile details.
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        """
        Update user and profile information
        """
        profile_data = validated_data.pop('profile', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile = instance.profile
            if profile is None:
                profile = Profile.objects.create(user=instance)

            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification tokens.
    """
    token = serializers.UUIDField(required=True)

    def validate_token(self, value):
        """
        Validate that the token exists and is not expired
        """
        try:
            verification = EmailVerification.objects.get(token=value)
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")

        if not verification.is_valid():
            raise serializers.ValidationError(
                "Verification token has expired. Please request a new one."
            )

        return value


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending email verification.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Normalize email addresses"""
        return value.lower()


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password while logged in.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """
        Check if old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """
        Validate new password
        """
        try:
            validate_password(value, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def save(self):
        """
        Update the user's password
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Check if email exists in the system
        """
        # Normalize email
        value = value.lower()

        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # We don't want to reveal if email exists for security reasons
            # Just silently pass and create a dummy token
            pass

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset using token.
    CRITICAL FIX: Updated token validation to use direct model query.
    """
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_token(self, value):
        """
        Check if token is valid.
        CRITICAL FIX: Use direct model query instead of request.user.password_resets
        because user is AnonymousUser during password reset process.
        """
        try:
            reset = PasswordReset.objects.get(
                token=value,
                is_used=False
            )
            if not reset.is_valid():
                raise serializers.ValidationError("Reset token has expired.")

            # Store for later use in the view
            self.context['reset'] = reset
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid reset token.")
        except Exception as e:
            raise serializers.ValidationError(f"Invalid reset token: {str(e)}")

        return value

    def validate_password(self, value):
        """
        Validate new password
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        if len(value) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
            )

        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with enhanced error handling.
    ENHANCED: Now provides specific error messages for non-existent email vs incorrect password.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    remember_me = serializers.BooleanField(default=False)

    def validate_email(self, value):
        """Normalize email addresses"""
        return value.lower()

    def validate(self, data):
        """
        Validate login credentials with improved error handling.

        This method:
        1. First checks whether the email actually exists
        2. Then attempts authentication
        3. Raises clean 400 errors instead of letting AttributeError bubble up as 500
        """
        email = data.get('email')
        password = data.get('password')

        # 1️⃣ Does this email even exist?
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'No account found with this email. Please sign up first.'
            })

        # 2️⃣ Try to authenticate
        user = authenticate(
            request=self.context.get('request'),
            username=email,    # Using email as username field
            password=password
        )
        if user is None:
            raise serializers.ValidationError({
                'password': 'Incorrect password.'
            })

        # 3️⃣ Any extra guards?
        if not user.is_active:
            raise serializers.ValidationError(
                'This account is inactive or has been suspended.'
            )

        # Check if account is temporarily locked
        if hasattr(user, 'is_account_locked') and user.is_account_locked():
            raise serializers.ValidationError(
                'Too many failed login attempts. Please try again later.'
            )

        # 4️⃣ All good—stash the user for your view
        data['user'] = user
        return data


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user session management.
    """
    class Meta:
        model = UserSession
        fields = [
            'id',
            'session_key',
            'ip_address',
            'user_agent',
            'created_at',
            'expires_at',
            'last_activity',
            'is_active',
            'device_type',
            'location',
            'login_method',  # Added to fields list
        ]
        read_only_fields = [
            'id',
            'created_at',
            'last_activity',
        ]

    def __init__(self, *args, **kwargs):
        """Initialize serializer with dynamic fields based on model"""
        super().__init__(*args, **kwargs)
        # Check if login_method field exists in the model
        if not hasattr(UserSession._meta.model, 'login_method'):
            self.fields.pop('login_method', None)
