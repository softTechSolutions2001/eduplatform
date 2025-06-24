# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Authentication Analyzer for Django projects

This module analyzes authentication and permission configurations in a Django project,
focusing on Django REST Framework authentication classes, permission classes,
and custom authentication flows.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:04:05
"""

import inspect
import logging
import re
import importlib
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from django.conf import settings

# For Django REST Framework support
try:
    from rest_framework.authentication import BaseAuthentication
    from rest_framework.permissions import BasePermission
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

# For JWT support
try:
    import rest_framework_simplejwt
    SIMPLEJWT_AVAILABLE = True
except ImportError:
    SIMPLEJWT_AVAILABLE = False

logger = logging.getLogger(__name__)


class AuthenticationAnalyzer:
    """Extract authentication and authorization information from a Django project"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

        # Auth components discovered in the project
        self.authentication_classes = []
        self.permission_classes = []

    def extract(self) -> Dict[str, Any]:
        """Extract authentication configuration information"""
        logger.info("Extracting authentication information")

        # Extract Django authentication settings
        django_auth = self._extract_django_auth_settings()

        # Extract DRF authentication settings
        drf_auth = self._extract_drf_auth_settings() if DRF_AVAILABLE else {}

        # Extract JWT settings if available
        jwt_auth = self._extract_jwt_settings() if SIMPLEJWT_AVAILABLE else {}

        # Discover custom authentication classes
        self._discover_authentication_classes()

        # Extract Authentication flows
        auth_flows = self._extract_auth_flows()

        # Create complete authentication information
        auth_info = {
            'django_auth': django_auth,
            'drf_auth': drf_auth,
            'jwt_auth': jwt_auth,
            'authentication_classes': self._format_authentication_classes(),
            'permission_classes': self._format_permission_classes(),
            'auth_flows': auth_flows,
            'token_lifetimes': self._extract_token_lifetimes(),
            'has_oauth': self._has_oauth(),
            'has_social_auth': self._has_social_auth(),
        }

        logger.info("Authentication information extraction complete")
        return auth_info

    def _extract_django_auth_settings(self) -> Dict[str, Any]:
        """Extract authentication settings from Django settings"""
        django_auth = {
            'auth_user_model': getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
            'login_url': getattr(settings, 'LOGIN_URL', '/accounts/login/'),
            'logout_url': getattr(settings, 'LOGOUT_URL', '/accounts/logout/'),
            'login_redirect_url': getattr(settings, 'LOGIN_REDIRECT_URL', '/'),
            'authentication_backends': getattr(settings, 'AUTHENTICATION_BACKENDS', 
                                             ['django.contrib.auth.backends.ModelBackend']),
            'password_hashers': getattr(settings, 'PASSWORD_HASHERS', None),
            'auth_password_validators': self._extract_password_validators(),
            'session_cookie_age': getattr(settings, 'SESSION_COOKIE_AGE', 1209600),  # 2 weeks
        }

        return django_auth

    def _extract_password_validators(self) -> List[Dict[str, Any]]:
        """Extract password validator settings"""
        validators = []

        # Get password validators from settings
        password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])

        for validator_config in password_validators:
            validator_info = {
                'name': validator_config.get('NAME', ''),
                'options': validator_config.get('OPTIONS', {})
            }

            # Try to get the validator class
            try:
                module_path, class_name = validator_config['NAME'].rsplit('.', 1)
                module = importlib.import_module(module_path)
                validator_class = getattr(module, class_name)

                validator_info['help_text'] = getattr(validator_class, 'get_help_text', lambda: '')()

            except (ImportError, AttributeError, ValueError) as e:
                logger.debug(f"Could not import validator {validator_config['NAME']}: {str(e)}")

            validators.append(validator_info)

        return validators

    def _extract_drf_auth_settings(self) -> Dict[str, Any]:
        """Extract DRF-specific authentication settings"""
        # Get DRF settings from Django settings
        drf_settings = getattr(settings, 'REST_FRAMEWORK', {})

        # Extract authentication and permission settings
        drf_auth = {
            'default_authentication_classes': drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', []),
            'default_permission_classes': drf_settings.get('DEFAULT_PERMISSION_CLASSES', []),
            'unauthenticated_user': drf_settings.get('UNAUTHENTICATED_USER', 'django.contrib.auth.models.AnonymousUser'),
            'throttle_classes': drf_settings.get('DEFAULT_THROTTLE_CLASSES', []),
            'throttle_rates': drf_settings.get('DEFAULT_THROTTLE_RATES', {}),
        }

        # Format class names for better display
        drf_auth['default_authentication_classes'] = [
            self._get_class_name(cls) for cls in drf_auth['default_authentication_classes']
        ]

        drf_auth['default_permission_classes'] = [
            self._get_class_name(cls) for cls in drf_auth['default_permission_classes']
        ]

        return drf_auth

    def _extract_jwt_settings(self) -> Dict[str, Any]:
        """Extract JWT authentication settings"""
        # Get JWT settings from Django settings
        simplejwt_settings = getattr(settings, 'SIMPLE_JWT', {})

        # Extract important JWT settings
        jwt_settings = {
            'access_token_lifetime': str(simplejwt_settings.get('ACCESS_TOKEN_LIFETIME', '')),
            'refresh_token_lifetime': str(simplejwt_settings.get('REFRESH_TOKEN_LIFETIME', '')),
            'algorithm': simplejwt_settings.get('ALGORITHM', 'HS256'),
            'auth_header_types': simplejwt_settings.get('AUTH_HEADER_TYPES', ('Bearer',)),
            'auth_header_name': simplejwt_settings.get('AUTH_HEADER_NAME', 'HTTP_AUTHORIZATION'),
            'user_id_field': simplejwt_settings.get('USER_ID_FIELD', 'id'),
            'user_id_claim': simplejwt_settings.get('USER_ID_CLAIM', 'user_id'),
            'sliding_token_refresh_enabled': simplejwt_settings.get('SLIDING_TOKEN_REFRESH', False),
            'blacklist_enabled': simplejwt_settings.get('BLACKLIST_AFTER_ROTATION', False),
        }

        return jwt_settings

    def _discover_authentication_classes(self):
        """Discover authentication and permission classes in the project"""
        # Only available with DRF
        if not DRF_AVAILABLE:
            return

        from django.apps import apps

        # Get all Django apps
        app_configs = apps.get_app_configs()

        # Filter apps based on configuration
        if self.config.INCLUDED_APPS:
            app_configs = [app for app in app_configs 
                          if app.name in self.config.INCLUDED_APPS]

        # Apply exclusions
        app_configs = [app for app in app_configs 
                      if app.name not in self.config.EXCLUDED_APPS]

        # Look for authentication and permission classes in each app
        for app_config in app_configs:
            app_path = Path(app_config.path)

            # Common module names where auth classes might be found
            auth_module_patterns = [
                'authentication.py', 'auth.py', 'permissions.py',
                'api/authentication.py', 'api/permissions.py'
            ]

            for pattern in auth_module_patterns:
                module_path = app_path / pattern
                if module_path.exists():
                    module_name = f"{app_config.name}.{pattern.replace('/', '.').replace('.py', '')}"
                    self._find_auth_classes_in_module(module_name)

    def _find_auth_classes_in_module(self, module_name: str):
        """Find authentication and permission classes in a Python module"""
        try:
            module = importlib.import_module(module_name)

            # Find authentication classes
            for name, obj in inspect.getmembers(module):
                # Skip non-classes
                if not inspect.isclass(obj):
                    continue

                # Skip imported classes
                if obj.__module__ != module_name:
                    continue

                # Check if this is an authentication class
                if DRF_AVAILABLE and issubclass(obj, BaseAuthentication) and obj is not BaseAuthentication:
                    self.authentication_classes.append(obj)
                    logger.debug(f"Found authentication class: {obj.__name__}")

                # Check if this is a permission class
                if DRF_AVAILABLE and issubclass(obj, BasePermission) and obj is not BasePermission:
                    self.permission_classes.append(obj)
                    logger.debug(f"Found permission class: {obj.__name__}")

        except ImportError as e:
            logger.debug(f"Could not import module {module_name}: {str(e)}")
        except Exception as e:
            logger.debug(f"Error inspecting module {module_name}: {str(e)}")

    def _format_authentication_classes(self) -> List[Dict[str, Any]]:
        """Format discovered authentication classes"""
        result = []

        for auth_class in self.authentication_classes:
            class_info = {
                'name': auth_class.__name__,
                'module': auth_class.__module__,
                'docstring': inspect.getdoc(auth_class) or '',
            }

            # Extract authenticate method details
            if hasattr(auth_class, 'authenticate'):
                method = auth_class.authenticate

                if inspect.isfunction(method) or inspect.ismethod(method):
                    # Get parameters of the authenticate method
                    try:
                        signature = inspect.signature(method)
                        class_info['parameters'] = [p.name for p in signature.parameters.values()
                                                   if p.name != 'self']
                    except ValueError:
                        pass

            result.append(class_info)

        return result

    def _format_permission_classes(self) -> List[Dict[str, Any]]:
        """Format discovered permission classes"""
        result = []

        for permission_class in self.permission_classes:
            class_info = {
                'name': permission_class.__name__,
                'module': permission_class.__module__,
                'docstring': inspect.getdoc(permission_class) or '',
            }

            # Extract has_permission method details
            if hasattr(permission_class, 'has_permission'):
                method = permission_class.has_permission

                if inspect.isfunction(method) or inspect.ismethod(method):
                    # Get parameters of the has_permission method
                    try:
                        signature = inspect.signature(method)
                        class_info['parameters'] = [p.name for p in signature.parameters.values()
                                                   if p.name != 'self']
                    except ValueError:
                        pass

            result.append(class_info)

        return result

    def _extract_auth_flows(self) -> Dict[str, Any]:
        """Extract authentication flows based on settings and discovered classes"""
        auth_flows = {
            'token_based_auth': self._has_token_auth(),
            'session_auth': self._has_session_auth(),
            'jwt_auth': SIMPLEJWT_AVAILABLE,
            'oauth2': self._has_oauth(),
            'basic_auth': self._has_basic_auth(),
            'custom_auth': len(self.authentication_classes) > 0,
        }

        # Determine the primary authentication method
        primary_auth = self._determine_primary_auth_method(auth_flows)
        auth_flows['primary_method'] = primary_auth

        return auth_flows

    def _has_token_auth(self) -> bool:
        """Check if the project uses token-based authentication"""
        # Check DRF settings
        if DRF_AVAILABLE:
            drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
            default_auth = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])

            for auth_class in default_auth:
                class_name = self._get_class_name(auth_class)
                if 'TokenAuthentication' in class_name:
                    return True

        # Check installed apps
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        return 'rest_framework.authtoken' in installed_apps

    def _has_session_auth(self) -> bool:
        """Check if the project uses session-based authentication"""
        # Check DRF settings
        if DRF_AVAILABLE:
            drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
            default_auth = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])

            for auth_class in default_auth:
                class_name = self._get_class_name(auth_class)
                if 'SessionAuthentication' in class_name:
                    return True

        # If Django sessions middleware is enabled, assume session auth is used
        middleware = getattr(settings, 'MIDDLEWARE', [])
        return 'django.contrib.sessions.middleware.SessionMiddleware' in middleware

    def _has_basic_auth(self) -> bool:
        """Check if the project uses basic authentication"""
        # Check DRF settings
        if DRF_AVAILABLE:
            drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
            default_auth = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])

            for auth_class in default_auth:
                class_name = self._get_class_name(auth_class)
                if 'BasicAuthentication' in class_name:
                    return True

        return False

    def _has_oauth(self) -> bool:
        """Check if the project uses OAuth2"""
        # Check installed apps
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])

        oauth_apps = [
            'oauth2_provider',
            'rest_framework_social_oauth2',
            'drf_social_oauth2',
            'django_oauth_toolkit',
        ]

        for app in oauth_apps:
            if any(installed_app.startswith(app) for installed_app in installed_apps):
                return True

        return False

    def _has_social_auth(self) -> bool:
        """Check if the project uses social authentication"""
        # Check installed apps
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])

        social_auth_apps = [
            'social_django',
            'allauth.socialaccount',
            'django_allauth',
        ]

        for app in social_auth_apps:
            if any(installed_app.startswith(app) for installed_app in installed_apps):
                return True

        return False

    def _determine_primary_auth_method(self, auth_flows: Dict[str, bool]) -> str:
        """Determine the primary authentication method used in the project"""
        # Check DRF settings first
        if DRF_AVAILABLE:
            drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
            default_auth = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])

            if default_auth:
                first_auth = default_auth[0]
                class_name = self._get_class_name(first_auth)

                if 'TokenAuthentication' in class_name:
                    return 'token'
                elif 'SessionAuthentication' in class_name:
                    return 'session'
                elif 'JWTAuthentication' in class_name or 'JSONWebTokenAuthentication' in class_name:
                    return 'jwt'
                elif 'OAuth2Authentication' in class_name:
                    return 'oauth2'
                elif 'BasicAuthentication' in class_name:
                    return 'basic'

        # If no DRF default, check what's enabled
        if auth_flows.get('jwt_auth'):
            return 'jwt'
        elif auth_flows.get('token_based_auth'):
            return 'token'
        elif auth_flows.get('oauth2'):
            return 'oauth2'
        elif auth_flows.get('session_auth'):
            return 'session'
        elif auth_flows.get('basic_auth'):
            return 'basic'
        elif auth_flows.get('custom_auth'):
            return 'custom'

        # Default to session authentication
        return 'session'

    def _extract_token_lifetimes(self) -> Dict[str, str]:
        """Extract token lifetime settings"""
        token_settings = {}

        # JWT token lifetimes
        if SIMPLEJWT_AVAILABLE:
            simplejwt_settings = getattr(settings, 'SIMPLE_JWT', {})

            access_lifetime = simplejwt_settings.get('ACCESS_TOKEN_LIFETIME')
            if access_lifetime:
                token_settings['jwt_access_token'] = str(access_lifetime)

            refresh_lifetime = simplejwt_settings.get('REFRESH_TOKEN_LIFETIME')
            if refresh_lifetime:
                token_settings['jwt_refresh_token'] = str(refresh_lifetime)

        # DRF token expiration
        if DRF_AVAILABLE:
            token_expire = getattr(settings, 'TOKEN_EXPIRED_AFTER_SECONDS', None)
            if token_expire is not None:
                token_settings['drf_token'] = f"{token_expire} seconds"

        # OAuth2 token expiration
        if self._has_oauth():
            oauth2_settings = getattr(settings, 'OAUTH2_PROVIDER', {})

            access_lifetime = oauth2_settings.get('ACCESS_TOKEN_EXPIRE_SECONDS')
            if access_lifetime:
                token_settings['oauth2_access_token'] = f"{access_lifetime} seconds"

            refresh_lifetime = oauth2_settings.get('REFRESH_TOKEN_EXPIRE_SECONDS')
            if refresh_lifetime:
                token_settings['oauth2_refresh_token'] = f"{refresh_lifetime} seconds"

        # Session timeout
        session_cookie_age = getattr(settings, 'SESSION_COOKIE_AGE', None)
        if session_cookie_age is not None:
            token_settings['session'] = f"{session_cookie_age} seconds"

        return token_settings

    def _get_class_name(self, class_path_or_obj) -> str:
        """Get class name from a string path or object"""
        if isinstance(class_path_or_obj, str):
            # This is a string path like 'rest_framework.authentication.TokenAuthentication'
            return class_path_or_obj.split('.')[-1]
        else:
            # This is an actual class or instance
            return class_path_or_obj.__name__