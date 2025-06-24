"""
File: backend/users/authentication.py
Purpose: Configures JWT authentication for EduPlatform.

This file contains:
- Custom JWT authentication class
- JWT response handler
- JWT settings
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from .models import UserSession


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class to validate tokens and track active sessions.
    """

    def authenticate(self, request):
        """
        Authenticate the request and update session activity.
        """
        # Use parent class to authenticate
        authenticated = super().authenticate(request)

        if authenticated:
            user, token = authenticated

            # Update session activity if exists
            try:
                session = UserSession.objects.get(
                    user=user,
                    session_key=token.payload['jti'],
                    is_active=True
                )

                # Update last activity
                session.last_activity = timezone.now()
                session.save(update_fields=['last_activity'])

                # Check if session is still valid
                if not session.is_valid():
                    return None

            except UserSession.DoesNotExist:
                # Session doesn't exist or is no longer active
                pass

            return authenticated

        return None


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Custom response payload handler for JWT authentication.
    Updated to use 'access' key for consistency with SimpleJWT.
    """
    return {
        'access': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_email_verified': user.is_email_verified
        }
    }


# JWT settings to be included in settings.py
JWT_AUTH_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=14),
}
