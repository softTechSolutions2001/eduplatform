from django.db.models import Count, Q, Avg
from courses.models import Course, Enrollment, Progress

from rest_framework import generics, status, views, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta
import uuid
import logging
import json
import requests

from .serializers import (
    UserSerializer, UserCreateSerializer, UserDetailSerializer,
    ProfileSerializer, LoginSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer,
    PasswordChangeSerializer, UpdateProfileSerializer, SubscriptionSerializer,
    UserSessionSerializer, ResendVerificationSerializer
)
from .models import Profile, EmailVerification, PasswordReset, UserSession, Subscription
from .permissions import IsOwnerOrAdmin, IsUserOrAdmin
from .utils import (
    get_client_ip, get_user_agent, get_device_type, get_location_from_ip,
    sanitize_email_for_logging, get_masked_ip
)

User = get_user_model()
logger = logging.getLogger(__name__)

# Constants for system configuration
DEFAULT_SUBSCRIPTION_DAYS = 30
SUBSCRIPTION_PRICES = {
    'registered': 9.99,
    'premium': 19.99,
}
EMAIL_VERIFICATION_EXPIRY_HOURS = 48
PASSWORD_RESET_EXPIRY_HOURS = 24

# Ensure required settings are available
REQUIRED_SETTINGS = [
    'FRONTEND_URL',
    'DEFAULT_FROM_EMAIL'
]

# Throttle classes
class LoginRateThrottle(AnonRateThrottle):
    """Rate throttle for login attempts"""
    scope = 'login'


class PasswordResetRateThrottle(AnonRateThrottle):
    """Rate throttle for password reset requests"""
    scope = 'password_reset'


class EmailVerifyRateThrottle(AnonRateThrottle):
    """Rate throttle for email verification"""
    scope = 'email_verify'


class RegisterView(generics.CreateAPIView):
    """
    Register a new user
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            email = request.data.get('email', 'unknown')
            sanitized_email = sanitize_email_for_logging(email)
            ip_address = get_masked_ip(get_client_ip(request))
            logger.warning(
                f"Registration validation failed for {sanitized_email} from {ip_address}: {serializer.errors}"
            )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = serializer.save()

            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS)
            verification = EmailVerification.objects.create(
                user=user,
                token=token,
                expires_at=expiry
            )

            Subscription.create_for_user(user)

            try:
                self._send_verification_email(user, verification.token)
            except Exception as e:
                sanitized_email = sanitize_email_for_logging(user.email)
                logger.error(
                    f"Failed to send verification email to {sanitized_email}: {str(e)}"
                )

            sanitized_email = sanitize_email_for_logging(user.email)
            ip_address = get_masked_ip(get_client_ip(request))
            logger.info(
                f"User registration successful: {sanitized_email} from {ip_address}"
            )

            return Response(
                {"detail": "User registered successfully. Please check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return Response(
                {"detail": "An error occurred during registration. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_verification_email(self, user, token):
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            subject = "Verify your EduPlatform account"

            try:
                message = render_to_string('users/email_verification.html', {
                    'user': user,
                    'verification_url': verification_url,
                    'valid_hours': EMAIL_VERIFICATION_EXPIRY_HOURS,
                })
            except Exception as e:
                logger.error(f"Error rendering email template: {str(e)}")
                message = f"""
                Hello {user.first_name},

                Thank you for registering with EduPlatform. Please verify your email by clicking the link below:

                {verification_url}

                This link is valid for {EMAIL_VERIFICATION_EXPIRY_HOURS} hours.

                If you didn't register for an account, please ignore this email.

                Best regards,
                The EduPlatform Team
                """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message if '<html' in message else None
            )

            sanitized_email = sanitize_email_for_logging(user.email)
            logger.info(f"Verification email sent to {sanitized_email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise


class LoginView(APIView):
    """
    User login with throttling
    """
    permission_classes = []
    throttle_classes = [LoginRateThrottle]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        if not serializer.is_valid():
            email = request.data.get('email', 'unknown')
            sanitized_email = sanitize_email_for_logging(email)
            masked_ip = get_masked_ip(ip_address)
            logger.warning(
                f"Login validation failed for {sanitized_email} from {masked_ip}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        remember_me = serializer.validated_data.get('remember_me', False)

        # Record login if method exists
        if hasattr(user, 'record_login_attempt'):
            user.record_login_attempt(successful=True, request=request)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)

        if not remember_me:
            refresh.set_exp(lifetime=timedelta(hours=24))

        if remember_me:
            expires_at = timezone.now() + timedelta(days=30)
        else:
            expires_at = timezone.now() + timedelta(hours=24)

        # Create session data object with all required fields
        session_data = {
            'user': user,
            'session_key': refresh.access_token['jti'],
            'ip_address': ip_address,
            'user_agent': user_agent,
            'expires_at': expires_at,
            'device_type': get_device_type(user_agent),
            'location': get_location_from_ip(ip_address)
        }

        # Optional field handling
        try:
            UserSession._meta.get_field('login_method')
            session_data['login_method'] = 'credentials'
        except Exception:
            pass

        UserSession.objects.create(**session_data)

        # Get subscription information if available
        try:
            subscription = user.subscription
        except Subscription.DoesNotExist:
            subscription = Subscription.create_for_user(user)

        sanitized_email = sanitize_email_for_logging(user.email)
        masked_ip = get_masked_ip(ip_address)
        device_type = get_device_type(user_agent)
        logger.info(
            f"Successful login: {sanitized_email} from {masked_ip} using {device_type}"
        )

        serializer_context = {
            'request': request,
        }

        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user, context=serializer_context).data,
        }

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    """
    User logout with session invalidation and token blacklisting
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            jti = None
            if hasattr(request, 'auth') and hasattr(request.auth, 'payload'):
                jti = request.auth.payload.get('jti')

            if jti:
                sessions = UserSession.objects.filter(
                    user=request.user,
                    session_key=jti,
                    is_active=True
                )
                for session in sessions:
                    session.invalidate()
                    logger.info(f"Invalidated session by JTI: {jti}")
            else:
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if 'Bearer ' in auth_header:
                    token = auth_header.split(' ')[1]
                    sessions = UserSession.objects.filter(
                        user=request.user,
                        session_key=token,
                        is_active=True
                    )
                    for session in sessions:
                        session.invalidate()
                        logger.info(f"Invalidated session by encoded token")

            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    logger.info("Blacklisted refresh token")
                except Exception as e:
                    logger.warning(f"Error blacklisting token: {str(e)}")

            sanitized_email = sanitize_email_for_logging(request.user.email)
            ip_address = get_masked_ip(get_client_ip(request))
            logger.info(f"Successful logout: {sanitized_email} from {ip_address}")

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.RetrieveUpdateAPIView):
    """
    View and update the authenticated user's information
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    View and update user profile
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrAdmin]

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Profile updated for {sanitized_email}")

        return Response(serializer.data)


class UpdateProfileView(generics.GenericAPIView):
    """
    Comprehensive profile update including both user and profile data
    """
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Comprehensive profile update for {sanitized_email}")

        return Response(UserDetailSerializer(request.user).data)


class PasswordChangeView(generics.GenericAPIView):
    """
    Change password for authenticated user
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        current_session_key = None

        if hasattr(request, 'auth') and hasattr(request.auth, 'payload'):
            jti = request.auth.payload.get('jti')
            if jti:
                current_session_key = jti
                logger.info(f"Using JTI as session key: {jti}")

        if not current_session_key and hasattr(request.auth, 'token'):
            current_session_key = request.auth.token
            logger.info("Using encoded token as session key")

        if current_session_key:
            UserSession.objects.filter(user=request.user).exclude(
                session_key=current_session_key
            ).update(is_active=False)
            logger.info(f"Invalidated other sessions during password change")
        else:
            logger.warning(
                "Could not identify current session during password change")

        sanitized_email = sanitize_email_for_logging(request.user.email)
        ip_address = get_masked_ip(get_client_ip(request))
        logger.info(f"Password changed successfully for {sanitized_email} from {ip_address}")

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request a password reset email
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        ip_address = get_client_ip(request)

        try:
            user = User.objects.get(email=email)

            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)

            PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=expiry,
                ip_address=ip_address
            )

            self._send_reset_email(user, token)

            sanitized_email = sanitize_email_for_logging(email)
            masked_ip = get_masked_ip(ip_address)
            logger.info(f"Password reset requested for {sanitized_email} from {masked_ip}")

        except User.DoesNotExist:
            sanitized_email = sanitize_email_for_logging(email)
            masked_ip = get_masked_ip(ip_address)
            logger.info(f"Password reset requested for non-existent {sanitized_email} from {masked_ip}")

        return Response(
            {"detail": "If an account exists with this email, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )

    def _send_reset_email(self, user, token):
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            subject = "Reset your EduPlatform password"
            message = render_to_string('users/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'valid_hours': PASSWORD_RESET_EXPIRY_HOURS,
            })

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message
            )

            sanitized_email = sanitize_email_for_logging(user.email)
            logger.info(f"Password reset email sent to {sanitized_email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm a password reset using a token
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']

            # Use reset object from serializer context if available
            reset = serializer.context.get('reset')
            if not reset:
                reset = get_object_or_404(PasswordReset, token=token)
                # Double-check validity if not verified by serializer
                if not reset.is_valid():
                    logger.warning(f"Expired password reset token used: {token}")
                    return Response(
                        {"detail": "This password reset link has expired or already been used."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            user = reset.user
            user.set_password(password)
            user.save()

            reset.use_token()

            UserSession.objects.filter(user=user).update(is_active=False)

            sanitized_email = sanitize_email_for_logging(user.email)
            ip_address = get_masked_ip(get_client_ip(request))
            logger.info(f"Password reset completed for {sanitized_email} from {ip_address}")

            return Response(
                {"detail": "Password has been reset successfully. You can now log in with your new password."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {"detail": "Password reset failed."},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailVerificationView(generics.GenericAPIView):
    """
    Verify email address using token
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = serializer.validated_data['token']

            verification = get_object_or_404(EmailVerification, token=token)

            if not verification.is_valid():
                logger.warning(f"Expired email verification token used: {token}")
                return Response(
                    {"detail": "This verification link has expired or already been used."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if verification.use_token():
                sanitized_email = sanitize_email_for_logging(verification.user.email)
                ip_address = get_masked_ip(get_client_ip(request))
                logger.info(f"Email verified successfully: {sanitized_email} from {ip_address}")

                return Response(
                    {"detail": "Email verified successfully. You can now log in."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Email verification failed."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response(
                {"detail": "Email verification failed."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(generics.GenericAPIView):
    """
    Resend email verification link
    """
    serializer_class = ResendVerificationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            if not email:
                return Response(
                    {"detail": "Email address is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_object_or_404(User, email=email)

            if user.is_email_verified:
                return Response(
                    {"detail": "Email address is already verified."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = uuid.uuid4()
            expiry = timezone.now() + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS)

            EmailVerification.objects.create(
                user=user,
                token=token,
                expires_at=expiry
            )

            self._send_verification_email(user, token)

            sanitized_email = sanitize_email_for_logging(email)
            ip_address = get_masked_ip(get_client_ip(request))
            logger.info(f"Verification email resent to {sanitized_email} from {ip_address}")

            return Response(
                {"detail": "Verification email has been sent."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            return Response(
                {"detail": "Failed to resend verification email."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _send_verification_email(self, user, token):
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            subject = "Verify your EduPlatform account"

            try:
                message = render_to_string('users/email_verification.html', {
                    'user': user,
                    'verification_url': verification_url,
                    'valid_hours': EMAIL_VERIFICATION_EXPIRY_HOURS,
                })
            except Exception as e:
                logger.error(f"Error rendering email template: {str(e)}")
                message = f"""
                Hello {user.first_name},

                Thank you for registering with EduPlatform. Please verify your email by clicking the link below:

                {verification_url}

                This link is valid for {EMAIL_VERIFICATION_EXPIRY_HOURS} hours.

                If you didn't register for an account, please ignore this email.

                Best regards,
                The EduPlatform Team
                """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message if '<html' in message else None
            )

            sanitized_email = sanitize_email_for_logging(user.email)
            logger.info(f"Verification email sent to {sanitized_email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise


class UserSessionViewSet(viewsets.ModelViewSet):
    """
    Manage user sessions (listing and invalidation)
    """
    serializer_class = UserSessionSerializer  # FIXED! Now using correct serializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.invalidate()

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Session manually invalidated for {sanitized_email}")

        return Response(
            {"detail": "Session invalidated successfully."},
            status=status.HTTP_200_OK
        )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Manage user subscriptions
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def get_object(self):
        try:
            return Subscription.objects.get(user=self.request.user)
        except Subscription.DoesNotExist:
            return Subscription.create_for_user(self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        subscription = self.get_object()
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        subscription = self.get_object()
        tier = request.data.get('tier')

        if tier not in ['registered', 'premium']:
            return Response({
                'detail': 'Invalid subscription tier. Choose from: registered, premium'
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.tier = tier
        subscription.status = 'active'
        subscription.end_date = timezone.now() + timedelta(days=DEFAULT_SUBSCRIPTION_DAYS)
        subscription.last_payment_date = timezone.now()
        subscription.is_auto_renew = request.data.get('auto_renew', True)
        subscription.payment_method = request.data.get('payment_method', 'demo')
        subscription.save()

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Subscription upgraded to {tier} tier for {sanitized_email}")

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        subscription = self.get_object()

        if subscription.tier == 'guest':
            return Response({
                'detail': 'Cannot cancel a guest tier subscription'
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'cancelled'
        subscription.is_auto_renew = False
        subscription.save()

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Subscription cancelled for {sanitized_email} ({subscription.tier} tier)")

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def downgrade(self, request):
        subscription = self.get_object()

        if subscription.tier == 'guest':
            return Response({
                'detail': 'Already on guest tier'
            }, status=status.HTTP_400_BAD_REQUEST)

        if subscription.tier == 'premium':
            new_tier = request.data.get('tier', 'registered')
            if new_tier not in ['registered', 'guest']:
                return Response({
                    'detail': 'Invalid downgrade tier. Choose from: registered, guest'
                }, status=status.HTTP_400_BAD_REQUEST)

            subscription.tier = new_tier
            subscription.save()
        else:
            subscription.tier = 'guest'
            subscription.end_date = None
            subscription.save()

        sanitized_email = sanitize_email_for_logging(request.user.email)
        logger.info(f"Subscription downgraded to {subscription.tier} tier for {sanitized_email}")

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)


class SocialAuthGoogleView(views.APIView):
    """
    Initiate Google OAuth flow
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Check required settings
        for setting in ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', 'FRONTEND_URL']:
            if not hasattr(settings, setting):
                logger.error(f"Missing required setting: {setting}")
                return Response(
                    {"detail": "OAuth configuration error. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        code_challenge = request.GET.get('code_challenge')
        code_challenge_method = request.GET.get('code_challenge_method', 'S256')
        state = request.GET.get('state')

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/google/callback"

        auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}&redirect_uri={redirect_uri}&response_type=code&scope=email%20profile&access_type=offline&prompt=consent"

        if code_challenge:
            auth_url += f"&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"
            logger.info(f"Adding PKCE to Google OAuth flow with method: {code_challenge_method}")

        if state:
            auth_url += f"&state={state}"
            logger.info("Adding state parameter to Google OAuth flow for CSRF protection")

        ip_address = get_masked_ip(get_client_ip(request))
        logger.info(f"Google OAuth flow initiated from {ip_address}")

        return Response({'authorizationUrl': auth_url})


class SocialAuthGithubView(views.APIView):
    """
    Initiate GitHub OAuth flow
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Check required settings
        for setting in ['SOCIAL_AUTH_GITHUB_KEY', 'SOCIAL_AUTH_GITHUB_SECRET', 'FRONTEND_URL']:
            if not hasattr(settings, setting):
                logger.error(f"Missing required setting: {setting}")
                return Response(
                    {"detail": "OAuth configuration error. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        code_challenge = request.GET.get('code_challenge')
        code_challenge_method = request.GET.get('code_challenge_method', 'S256')
        state = request.GET.get('state')

        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/github/callback"

        auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.SOCIAL_AUTH_GITHUB_KEY}&redirect_uri={redirect_uri}&scope=user:email"

        if code_challenge:
            auth_url += f"&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"
            logger.info(f"Adding PKCE to GitHub OAuth flow with method: {code_challenge_method}")

        if state:
            auth_url += f"&state={state}"
            logger.info("Adding state parameter to GitHub OAuth flow for CSRF protection")

        ip_address = get_masked_ip(get_client_ip(request))
        logger.info(f"GitHub OAuth flow initiated from {ip_address}")

        return Response({'authorizationUrl': auth_url})


class SocialAuthCompleteView(views.APIView):
    """
    Complete OAuth flow for social authentication
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            code = request.data.get('code')
            provider = request.data.get('provider')
            code_verifier = request.data.get('code_verifier')
            state = request.data.get('state')

            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            masked_ip = get_masked_ip(ip_address)

            logger.info(f"Social auth request: provider={provider}, from {masked_ip}")

            if not code:
                logger.warning(f"Social auth missing code from {masked_ip}")
                return Response(
                    {"detail": "Authorization code is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not provider or provider not in ['google', 'github']:
                logger.warning(f"Social auth invalid provider '{provider}' from {masked_ip}")
                return Response(
                    {"detail": "Valid provider (google or github) is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_dev = settings.DEBUG
            if is_dev and code_verifier == 'dev-verifier':
                logger.info("Using development code verifier bypass")
                code_verifier = None

            # Store code in request session to prevent reuse
            session_key = f"oauth_{provider}_code"
            if hasattr(request, 'session'):
                if request.session.get(session_key) == code:
                    logger.warning(f"Attempt to reuse {provider} OAuth code from {masked_ip}")
                    return Response(
                        {"detail": "This authorization code has already been used."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                request.session[session_key] = code

            # Exchange code for user info with provider
            if provider == 'google':
                try:
                    user_info = self._exchange_google_code(code, code_verifier)
                except Exception as e:
                    logger.error(f"Google token exchange error from {masked_ip}: {str(e)}")
                    return Response(
                        {"detail": f"Google authentication failed: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validate email verification status
                if not user_info.get('email_verified', True):
                    sanitized_email = sanitize_email_for_logging(user_info.get('email', 'unknown'))
                    logger.warning(f"Google account email not verified: {sanitized_email}")
                    return Response(
                        {"detail": "Your Google account email is not verified. Please verify your email with Google."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                email = user_info.get('email')
                if not email:
                    logger.error(f"Could not get email from Google for user from {masked_ip}")
                    return Response(
                        {"detail": "Could not get email from Google."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Find or create user
                try:
                    user = User.objects.get(email=email)
                    sanitized_email = sanitize_email_for_logging(email)
                    logger.info(f"Found existing user for Google login: {sanitized_email}")
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        email=email,
                        username=email,
                        first_name=user_info.get('given_name', ''),
                        last_name=user_info.get('family_name', ''),
                        is_active=True,
                        is_email_verified=True
                    )
                    # Create profile and subscription for new users
                    try:
                        Profile.objects.get_or_create(user=user)
                    except Exception as e:
                        logger.error(f"Error creating profile: {str(e)}")
                    try:
                        Subscription.create_for_user(user)
                    except Exception as e:
                        logger.error(f"Error creating subscription: {str(e)}")
                    sanitized_email = sanitize_email_for_logging(email)
                    logger.info(f"Created new user from Google OAuth: {sanitized_email}")

            elif provider == 'github':
                try:
                    user_info = self._exchange_github_code(code, code_verifier)
                except Exception as e:
                    logger.error(f"GitHub token exchange error from {masked_ip}: {str(e)}")
                    return Response(
                        {"detail": f"GitHub authentication failed: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                email = user_info.get('email')
                if not email:
                    logger.error(f"Could not get email from GitHub for user from {masked_ip}")
                    return Response(
                        {"detail": "Could not get email from GitHub."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Parse name into first and last name
                full_name = user_info.get('name', '')
                name_parts = full_name.split(' ', 1) if full_name else ['', '']
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                # Find or create user
                try:
                    user = User.objects.get(email=email)
                    sanitized_email = sanitize_email_for_logging(email)
                    logger.info(f"Found existing user for GitHub login: {sanitized_email}")
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        email=email,
                        username=email,
                        first_name=first_name,
                        last_name=last_name,
                        is_active=True,
                        is_email_verified=True
                    )
                    # Create profile and subscription for new users
                    try:
                        Profile.objects.get_or_create(user=user)
                    except Exception as e:
                        logger.error(f"Error creating profile: {str(e)}")
                    try:
                        Subscription.create_for_user(user)
                    except Exception as e:
                        logger.error(f"Error creating subscription: {str(e)}")
                    sanitized_email = sanitize_email_for_logging(email)
                    logger.info(f"Created new user from GitHub OAuth: {sanitized_email}")

            # Update last login timestamp
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)

            # Create user session with real IP/User-Agent
            expires_at = timezone.now() + timedelta(days=14)

            session_data = {
                'user': user,
                'session_key': refresh.access_token['jti'],
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at,
                'device_type': get_device_type(user_agent),
                'location': get_location_from_ip(ip_address)
            }

            # Check if login_method field exists in the model before adding it
            try:
                UserSession._meta.get_field('login_method')
                session_data['login_method'] = f"social_{provider}"
            except Exception:
                # Field doesn't exist, don't include it
                pass

            # Create the session
            UserSession.objects.create(**session_data)

            # Create serializer context
            serializer_context = {
                'request': request,
            }

            # Return tokens as JSON response
            data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserDetailSerializer(user, context=serializer_context).data,
            }

            # Log successful social authentication with sanitized data
            sanitized_email = sanitize_email_for_logging(user.email)
            device_type = get_device_type(user_agent)
            logger.info(f"Social authentication successful: {sanitized_email} via {provider} from {masked_ip} using {device_type}")

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            masked_ip = get_masked_ip(get_client_ip(request))
            logger.error(f"Social auth error from {masked_ip}: {str(e)}")
            return Response(
                {"detail": f"Authentication failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _exchange_google_code(self, code, code_verifier=None):
        """Exchange Google authorization code for tokens and user info."""
        # Verify required settings
        if not hasattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'):
            raise Exception("Google OAuth client ID is not configured")

        if not hasattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'):
            raise Exception("Google OAuth client secret is not configured")

        if not hasattr(settings, 'FRONTEND_URL'):
            raise Exception("Frontend URL is not configured")

        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/google/callback"

        token_payload = {
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        # Add code_verifier for PKCE if provided
        if code_verifier:
            token_payload['code_verifier'] = code_verifier
            logger.info("Using PKCE code_verifier for Google token exchange")

        # Request access token
        token_response = requests.post(token_url, data=token_payload)

        if token_response.status_code != 200:
            logger.error(f"Google token exchange failed: {token_response.text}")
            raise Exception("Failed to exchange Google code for token")

        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            raise Exception("No access token received from Google")

        # Use access token to get user information
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}

        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            logger.error(f"Google user info request failed: {userinfo_response.text}")
            raise Exception("Failed to get user information from Google")

        user_data = userinfo_response.json()

        # Return user info
        return {
            'email': user_data.get('email'),
            'email_verified': user_data.get('email_verified', False),
            'given_name': user_data.get('given_name', ''),
            'family_name': user_data.get('family_name', ''),
            'picture': user_data.get('picture', ''),
            'sub': user_data.get('sub')  # Unique Google ID
        }

    def _exchange_github_code(self, code, code_verifier=None):
        """Exchange GitHub authorization code for tokens and user info."""
        # Verify required settings
        if not hasattr(settings, 'SOCIAL_AUTH_GITHUB_KEY'):
            raise Exception("GitHub OAuth client ID is not configured")

        if not hasattr(settings, 'SOCIAL_AUTH_GITHUB_SECRET'):
            raise Exception("GitHub OAuth client secret is not configured")

        if not hasattr(settings, 'FRONTEND_URL'):
            raise Exception("Frontend URL is not configured")

        # Exchange code for access token
        token_url = "https://github.com/login/oauth/access_token"
        redirect_uri = f"{settings.FRONTEND_URL}/auth/social/github/callback"

        token_payload = {
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
            'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
            'redirect_uri': redirect_uri
        }

        # Add code_verifier for PKCE if provided
        if code_verifier:
            token_payload['code_verifier'] = code_verifier
            logger.info("Using PKCE code_verifier for GitHub token exchange")

        headers = {'Accept': 'application/json'}

        # Request access token
        token_response = requests.post(token_url, data=token_payload, headers=headers)

        if token_response.status_code != 200:
            logger.error(f"GitHub token exchange failed: {token_response.text}")
            raise Exception("Failed to exchange GitHub code for token")

        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            raise Exception("No access token received from GitHub")

        # Use access token to get user information
        api_headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        # Get basic user info
        user_url = "https://api.github.com/user"
        user_response = requests.get(user_url, headers=api_headers)

        if user_response.status_code != 200:
            logger.error(f"GitHub user info request failed: {user_response.text}")
            raise Exception("Failed to get user information from GitHub")

        user_data = user_response.json()

        # Get email from emails endpoint if not in profile
        email = user_data.get('email')
        if not email:
            emails_url = "https://api.github.com/user/emails"
            emails_response = requests.get(emails_url, headers=api_headers)

            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Find primary and verified email
                primary_email = next((e for e in emails if e.get('primary') and e.get('verified')), None)
                if primary_email:
                    email = primary_email.get('email')
                else:
                    # If no primary email, get first verified email
                    verified_email = next((e for e in emails if e.get('verified')), None)
                    if verified_email:
                        email = verified_email.get('email')

        if not email:
            raise Exception("Could not retrieve verified email from GitHub")

        # Return user info
        return {
            'email': email,
            'name': user_data.get('name', ''),
            'login': user_data.get('login'),
            'avatar_url': user_data.get('avatar_url', ''),
            'id': user_data.get('id')  # Unique GitHub ID
        }


class SocialAuthErrorView(views.APIView):
    """
    API view to handle social auth errors.
    Enhanced with secure logging.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        error = request.GET.get('error', 'Unknown error')
        error_description = request.GET.get('error_description', '')
        state = request.GET.get('state', '')

        # Log the error with masked IP
        masked_ip = get_masked_ip(get_client_ip(request))
        logger.error(f"Social auth error from {masked_ip}: {error} - {error_description}")

        # Build error message
        error_message = f"{error}: {error_description}" if error_description else error

        # Verify required settings
        if not hasattr(settings, 'FRONTEND_URL'):
            logger.error("FRONTEND_URL setting is missing")
            return Response(
                {"detail": "Frontend URL is not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Redirect to frontend with error and state (if available)
        redirect_url = f"{settings.FRONTEND_URL}/login?error={error_message}"
        if state:
            redirect_url += f"&state={state}"

        return redirect(redirect_url)
