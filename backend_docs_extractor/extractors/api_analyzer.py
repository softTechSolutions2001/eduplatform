# fmt: off
# isort: skip_file
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Analyzer for Django projects

This module analyzes Django URL patterns and views to extract API endpoint information.
It supports various Django REST framework view types and includes authentication requirements.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:04:05
"""

import inspect
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RoutePattern, RegexPattern
from django.utils.functional import cached_property

# For Django REST Framework support
try:
    from rest_framework.viewsets import ViewSet, ModelViewSet, ReadOnlyModelViewSet
    from rest_framework.decorators import action
    from rest_framework.views import APIView
    from rest_framework.serializers import Serializer
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

logger = logging.getLogger(__name__)


class ApiAnalyzer:
    """Analyze Django URL patterns and views to extract API information"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL
        self.analyzed_views = set()

    def extract(self) -> Dict[str, Any]:
        """Extract API information from the Django project"""
        logger.info("Extracting API information")

        # Get the URL resolver for the project
        resolver = get_resolver()

        # Extract endpoints from the resolver
        api_endpoints = self._extract_url_patterns(resolver, prefix='/')

        # Group endpoints by app and module
        grouped_endpoints = self._group_endpoints(api_endpoints)

        logger.info(f"Extracted {len(api_endpoints)} API endpoints")
        return {
            'endpoints': api_endpoints,
            'grouped': grouped_endpoints,
        }

    def _extract_url_patterns(
        self, resolver, prefix='', namespace=None, app_name=None
    ) -> List[Dict[str, Any]]:
        """Extract URL patterns recursively"""
        endpoints = []

        url_patterns = resolver.url_patterns

        for pattern in url_patterns:
            # Handle both URLPattern and URLResolver
            if isinstance(pattern, URLPattern):
                endpoint = self._extract_endpoint(pattern, prefix, namespace, app_name)
                if endpoint:
                    endpoints.append(endpoint)

            elif isinstance(pattern, URLResolver):
                # Get namespace and app_name
                if pattern.namespace:
                    namespace = pattern.namespace
                if pattern.app_name:
                    app_name = pattern.app_name

                # Get the pattern prefix
                pattern_prefix = self._get_pattern_prefix(pattern)
                new_prefix = prefix + pattern_prefix

                # Extract nested patterns recursively
                nested_endpoints = self._extract_url_patterns(
                    pattern, new_prefix, namespace, app_name
                )
                endpoints.extend(nested_endpoints)

        return endpoints

    def _extract_endpoint(
        self, pattern: URLPattern, prefix: str, namespace: Optional[str], app_name: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Extract information about a URL pattern"""
        # Get the view function or class
        view = pattern.callback

        # Skip admin views or other non-API views based on naming conventions
        if self._should_skip_view(view, pattern):
            return None

        # Get pattern prefix
        pattern_prefix = self._get_pattern_prefix(pattern)
        full_path = prefix + pattern_prefix

        # Clean up the path for display
        full_path = self._clean_path(full_path)

        # Check if this is already analyzed (for viewsets with multiple endpoints)
        view_id = id(view)
        if view_id in self.analyzed_views and self._is_viewset(view):
            # For viewsets, we analyze once but make multiple endpoints
            pass
        else:
            self.analyzed_views.add(view_id)

        # Get information about the view
        view_info = self._extract_view_info(view)

        # Extract serializer information if this is a DRF view
        serializer_info = self._extract_serializer_info(view) if DRF_AVAILABLE else None

        # Get HTTP methods
        http_methods = self._get_http_methods(view)

        # Get authentication and permission requirements
        auth_info = self._extract_auth_info(view)

        # Get query parameters
        query_params = self._extract_query_params(view)

        # Create the endpoint object
        endpoint = {
            'path': full_path,
            'pattern_regex': self._get_pattern_regex(pattern),
            'name': pattern.name or '',
            'view': view_info,
            'http_methods': http_methods,
            'namespace': namespace or '',
            'app_name': app_name or '',
            'authentication': auth_info,
            'query_params': query_params,
        }

        if serializer_info:
            endpoint['serializer'] = serializer_info

        # If DRF is available, check if this is a viewset and extract actions
        if DRF_AVAILABLE and self._is_viewset(view):
            viewset_endpoints = self._extract_viewset_endpoints(
                view, full_path, endpoint
            )
            return viewset_endpoints

        return endpoint

    def _extract_viewset_endpoints(
        self, viewset, base_path: str, base_endpoint: Dict
    ) -> Dict[str, Any]:
        """Extract endpoints for DRF ViewSets which have multiple actions per URL"""
        # For ViewSets, we extend the base endpoint with action information

        # ViewSets have multiple actions mapped to HTTP methods
        # We want to document each action separately
        actions = self._get_viewset_actions(viewset)

        # Add viewset-specific information
        base_endpoint['viewset'] = {
            'class': viewset.__name__ if hasattr(viewset, '__name__') else viewset.__class__.__name__,
            'actions': actions,
            'is_model_viewset': isinstance(viewset, ModelViewSet) if DRF_AVAILABLE else False,
            'is_readonly_viewset': isinstance(viewset, ReadOnlyModelViewSet) if DRF_AVAILABLE else False,
            'model': self._get_viewset_model(viewset) if DRF_AVAILABLE else None,
        }

        # If this is a model viewset, add the model serializer
        if base_endpoint['viewset']['is_model_viewset']:
            base_endpoint['model_serializer'] = self._extract_model_serializer_info(viewset)

        return base_endpoint

    def _get_viewset_actions(self, viewset) -> Dict[str, Any]:
        """Get the actions defined on a DRF ViewSet"""
        actions = {}

        # Get standard viewset actions
        if hasattr(viewset, 'get_extra_actions'):
            # This is a ViewSet instance
            methods = viewset.get_extra_actions()
            for method in methods:
                action_info = self._get_action_info(method)
                actions[method.__name__] = action_info
        elif hasattr(viewset, 'get_extra_actions') and inspect.isclass(viewset):
            # This is a ViewSet class
            try:
                method_list = viewset.get_extra_actions.im_func(viewset)
                for method in method_list:
                    action_info = self._get_action_info(method)
                    actions[method.__name__] = action_info
            except AttributeError:
                # Python 3 compatibility
                try:
                    method_list = viewset.get_extra_actions.__func__(viewset)
                    for method in method_list:
                        action_info = self._get_action_info(method)
                        actions[method.__name__] = action_info
                except Exception as e:
                    logger.debug(f"Could not get extra actions: {str(e)}")

        # Add standard CRUD actions based on ViewSet type
        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'list'):
            actions['list'] = {'http_methods': ['GET'], 'detail': False, 'description': 'List objects'}

        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'create'):
            actions['create'] = {'http_methods': ['POST'], 'detail': False, 'description': 'Create object'}

        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'retrieve'):
            actions['retrieve'] = {'http_methods': ['GET'], 'detail': True, 'description': 'Retrieve object'}

        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'update'):
            actions['update'] = {'http_methods': ['PUT'], 'detail': True, 'description': 'Update object'}

        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'partial_update'):
            actions['partial_update'] = {'http_methods': ['PATCH'], 'detail': True, 'description': 'Partially update object'}

        if isinstance(viewset, ModelViewSet) or hasattr(viewset, 'destroy'):
            actions['destroy'] = {'http_methods': ['DELETE'], 'detail': True, 'description': 'Delete object'}

        return actions

    def _get_action_info(self, method) -> Dict[str, Any]:
        """Get information about a viewset action"""
        # Check if this is a DRF @action
        if hasattr(method, 'mapping'):
            # This is a DRF @action
            return {
                'http_methods': list(method.mapping.keys()),
                'detail': getattr(method, 'detail', False),
                'url_path': getattr(method, 'url_path', method.__name__.replace('_', '-')),
                'url_name': getattr(method, 'url_name', method.__name__.replace('_', '-')),
                'description': (method.__doc__ or '').strip(),
                'permissions': self._extract_action_permissions(method),
            }

        # Regular method
        return {
            'http_methods': [],  # Can't determine HTTP methods for non-@action methods
            'detail': False,  # Assume not detail by default
            'description': (method.__doc__ or '').strip(),
        }

    def _extract_action_permissions(self, action) -> List[str]:
        """Extract permission classes for a DRF viewset action"""
        permission_classes = []

        if hasattr(action, 'kwargs') and 'permission_classes' in action.kwargs:
            for permission_class in action.kwargs['permission_classes']:
                permission_classes.append(permission_class.__name__)

        return permission_classes

    def _get_viewset_model(self, viewset) -> Optional[str]:
        """Get the model name used by a ModelViewSet"""
        # Check if this is a ModelViewSet
        if not hasattr(viewset, 'queryset'):
            return None

        queryset = viewset.queryset

        if hasattr(queryset, 'model'):
            return queryset.model.__name__

        return None

    def _extract_model_serializer_info(self, viewset) -> Dict[str, Any]:
        """Extract information about the serializer used by a ModelViewSet"""
        serializer_class = getattr(viewset, 'serializer_class', None)

        if not serializer_class:
            return {}

        serializer_info = {
            'class': serializer_class.__name__,
            'module': serializer_class.__module__,
        }

        # Get the fields defined in the serializer
        serializer_instance = None
        try:
            serializer_instance = serializer_class()
        except Exception:
            pass

        if serializer_instance:
            fields = {}
            for field_name, field in serializer_instance.fields.items():
                fields[field_name] = {
                    'type': field.__class__.__name__,
                    'required': field.required,
                    'read_only': field.read_only,
                    'write_only': field.write_only,
                    'help_text': str(field.help_text) if field.help_text else '',
                    'label': str(field.label) if field.label else '',
                }

            serializer_info['fields'] = fields

        return serializer_info

    def _extract_view_info(self, view) -> Dict[str, Any]:
        """Extract information about a view function or class"""
        view_info = {
            'module': self._get_view_module(view),
        }

        # Add class and method name for class-based views
        if hasattr(view, '__name__'):
            # Function-based view
            view_info['name'] = view.__name__
            view_info['docstring'] = inspect.getdoc(view) or ''
            view_info['is_class_based'] = False

            # Extract parameters
            view_info['parameters'] = self._extract_view_parameters(view)
        else:
            # Class-based view
            view_class = view.__class__
            view_info['name'] = view_class.__name__
            view_info['class'] = view_class.__name__
            view_info['is_class_based'] = True

            # Get the view method docstrings
            view_info['method_docstrings'] = {}
            for http_method in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options'):
                if hasattr(view, http_method):
                    method = getattr(view, http_method)
                    view_info['method_docstrings'][http_method] = inspect.getdoc(method) or ''

        return view_info

    def _extract_view_parameters(self, view) -> List[str]:
        """Extract parameters from a function-based view"""
        try:
            signature = inspect.signature(view)
            # Skip 'self' or 'request' parameters
            params = [p.name for p in signature.parameters.values()
                     if p.name not in ('self', 'request')]
            return params
        except (ValueError, TypeError):
            return []

    def _get_view_module(self, view) -> str:
        """Get the module name of a view function or class"""
        if hasattr(view, '__module__'):
            return view.__module__

        if hasattr(view, '__class__') and hasattr(view.__class__, '__module__'):
            return view.__class__.__module__

        return ''

    def _extract_serializer_info(self, view) -> Optional[Dict[str, Any]]:
        """Extract information about the serializer used by a DRF view"""
        if not DRF_AVAILABLE:
            return None

        serializer_class = None

        # Try different ways to get the serializer class
        if hasattr(view, 'get_serializer_class'):
            try:
                serializer_class = view.get_serializer_class()
            except Exception:
                pass

        if serializer_class is None and hasattr(view, 'serializer_class'):
            serializer_class = view.serializer_class

        if serializer_class is None:
            return None

        # Extract information about the serializer
        serializer_info = {
            'class': serializer_class.__name__,
            'module': serializer_class.__module__,
            'fields': {},
        }

        # Try to get fields from the serializer
        try:
            serializer = serializer_class()
            for field_name, field in serializer.fields.items():
                field_info = {
                    'type': field.__class__.__name__,
                    'required': field.required,
                    'read_only': field.read_only,
                    'write_only': field.write_only,
                }

                if hasattr(field, 'help_text') and field.help_text:
                    field_info['help_text'] = str(field.help_text)

                if hasattr(field, 'style') and field.style:
                    field_info['style'] = field.style

                serializer_info['fields'][field_name] = field_info
        except Exception as e:
            logger.debug(f"Could not instantiate serializer {serializer_class.__name__}: {str(e)}")

        return serializer_info

    def _extract_auth_info(self, view) -> Dict[str, Any]:
        """Extract authentication and permission information from a DRF view"""
        auth_info = {
            'authentication_classes': [],
            'permission_classes': [],
            'requires_authentication': False,
        }

        # Check for authentication classes
        if hasattr(view, 'authentication_classes'):
            for auth_class in view.authentication_classes:
                auth_info['authentication_classes'].append({
                    'class': auth_class.__name__,
                    'module': auth_class.__module__,
                })

            auth_info['requires_authentication'] = len(auth_info['authentication_classes']) > 0

        # Check for permission classes
        if hasattr(view, 'permission_classes'):
            for permission_class in view.permission_classes:
                auth_info['permission_classes'].append({
                    'class': permission_class.__name__,
                    'module': permission_class.__module__,
                })

                # Check if this permission requires authentication
                if permission_class.__name__ != 'AllowAny':
                    auth_info['requires_authentication'] = True

        return auth_info

    def _extract_query_params(self, view) -> List[Dict[str, Any]]:
        """Extract query parameters from a view"""
        params = []

        # Check for query parameter filtering in DRF
        if hasattr(view, 'filter_backends'):
            params.extend(self._extract_filter_params(view))

        # Look for pagination parameters
        if hasattr(view, 'pagination_class'):
            params.extend(self._extract_pagination_params(view))

        return params

    def _extract_filter_params(self, view) -> List[Dict[str, Any]]:
        """Extract filter parameters from a view"""
        params = []

        # Common DRF filter backends and their parameters
        if not hasattr(view, 'filter_backends'):
            return params

        for filter_backend in view.filter_backends:
            if filter_backend.__name__ == 'SearchFilter':
                params.append({
                    'name': 'search',
                    'type': 'string',
                    'required': False,
                    'description': 'A search term for filtering results',
                })

            if filter_backend.__name__ == 'OrderingFilter':
                params.append({
                    'name': 'ordering',
                    'type': 'string',
                    'required': False,
                    'description': 'Which field to use when ordering the results',
                    'example': 'id,-created_at',
                })

            if filter_backend.__name__ == 'DjangoFilterBackend':
                # Try to get filterset_class or filterset_fields
                filterset_fields = []
                if hasattr(view, 'filterset_fields'):
                    filterset_fields = view.filterset_fields
                elif hasattr(view, 'filter_fields'):
                    filterset_fields = view.filter_fields

                for field in filterset_fields:
                    params.append({
                        'name': field,
                        'type': 'string',
                        'required': False,
                        'description': f'Filter by {field}',
                    })

        return params

    def _extract_pagination_params(self, view) -> List[Dict[str, Any]]:
        """Extract pagination parameters from a view"""
        params = []

        if not hasattr(view, 'pagination_class'):
            return params

        # Add common pagination parameters
        params.append({
            'name': 'page',
            'type': 'integer',
            'required': False,
            'description': 'A page number within the paginated result set',
        })

        params.append({
            'name': 'page_size',
            'type': 'integer',
            'required': False,
            'description': 'Number of results to return per page',
        })

        return params

    def _get_http_methods(self, view) -> List[str]:
        """Get HTTP methods allowed by a view"""
        methods = []

        # Django REST Framework views
        if hasattr(view, 'allowed_methods'):
            try:
                return [method.lower() for method in view.allowed_methods]
            except Exception:
                pass

        # Class-based views
        if hasattr(view, 'http_method_names'):
            methods = [method for method in view.http_method_names 
                      if method != 'options' and hasattr(view, method)]
            return methods

        # Function-based views
        if hasattr(view, '__name__'):
            # Can't determine methods from function name, assume GET
            methods = ['get']

        return methods

    def _get_pattern_regex(self, pattern) -> str:
        """Get the regex pattern of a URL pattern"""
        if hasattr(pattern, 'pattern'):
            if isinstance(pattern.pattern, RegexPattern):
                return pattern.pattern._regex
            elif isinstance(pattern.pattern, RoutePattern):
                return pattern.pattern._route

        return ''

    def _get_pattern_prefix(self, pattern) -> str:
        """Get the prefix of a URL pattern or resolver"""
        if hasattr(pattern, 'pattern'):
            if isinstance(pattern.pattern, RegexPattern):
                # Convert regex to a simpler form for display
                regex = pattern.pattern._regex
                # Replace named capture groups with URL params
                regex = re.sub(r'\(\?P<([^>]+)>[^)]+\)', r'{\1}', regex)
                # Replace non-named capture groups
                regex = re.sub(r'\([^)]+\)', r'{}', regex)
                # Remove regex syntax
                regex = regex.replace('^', '').replace('$', '')
                return regex
            elif isinstance(pattern.pattern, RoutePattern):
                return pattern.pattern._route

        return ''

    def _clean_path(self, path: str) -> str:
        """Clean up a URL path for display"""
        # Replace multiple slashes with a single slash
        path = re.sub(r'/{2,}', '/', path)

        # Ensure path starts with a slash
        if not path.startswith('/'):
            path = '/' + path

        # Replace regex patterns with URL params
        path = re.sub(r'\(\?P<([^>]+)>[^)]+\)', r'{\1}', path)

        # Replace non-named capture groups
        path = re.sub(r'\([^)]+\)', r'{}', path)

        # Remove regex syntax
        path = path.replace('^', '').replace('$', '')

        return path

    def _should_skip_view(self, view, pattern) -> bool:
        """Check if a view should be skipped from API documentation"""
        view_module = self._get_view_module(view)

        # Skip Django admin views
        if 'django.contrib.admin' in view_module:
            return True

        # Skip Django auth views
        if 'django.contrib.auth.views' in view_module:
            return True

        # Check URL pattern
        if pattern.name and pattern.name.startswith(('admin:', 'django_admin')):
            return True

        return False

    def _is_viewset(self, view) -> bool:
        """Check if a view is a DRF ViewSet"""
        if not DRF_AVAILABLE:
            return False

        # Check if this is a ViewSet
        if hasattr(view, '__class__') and issubclass(view.__class__, ViewSet):
            return True

        return False

    def _group_endpoints(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group endpoints by app and module"""
        grouped = {}

        for endpoint in endpoints:
            # Get app and module from view information
            module = endpoint['view'].get('module', '')

            # Skip endpoints without a module
            if not module:
                continue

            # Split module into parts
            parts = module.split('.')

            # Get app name (usually the first part of the module)
            app = parts[0] if parts else ''

            # Skip if no app name
            if not app:
                continue

            # Create app entry if it doesn't exist
            if app not in grouped:
                grouped[app] = {
                    'modules': {},
                    'endpoints': [],
                }

            # Add endpoint to app
            grouped[app]['endpoints'].append(endpoint)

            # Skip if only one part in module
            if len(parts) <= 1:
                continue

            # Get module name (all parts after the first)
            module_name = '.'.join(parts[1:])

            # Create module entry if it doesn't exist
            if module_name not in grouped[app]['modules']:
                grouped[app]['modules'][module_name] = []

            # Add endpoint to module
            grouped[app]['modules'][module_name].append(endpoint)

        return grouped