# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runtime API Tester for Django projects

This module tests actual API endpoints in a running Django application,
gathering response information, examples, and performance metrics.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:13:56
"""

import logging
import json
import time
import warnings
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

# Suppress insecure request warnings when testing
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# For making HTTP requests
try:
    import requests
    from requests.exceptions import RequestException
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RuntimeTester:
    """Test API endpoints at runtime and gather response information"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

        # Base URL for API testing
        self.base_url = config.BACKEND_URL

        # Authentication credentials
        self.auth_username = config.AUTH_USERNAME
        self.auth_password = config.AUTH_PASSWORD
        self.auth_token = config.AUTH_TOKEN

        # Request timeout
        self.timeout = config.REQUEST_TIMEOUT

        # Maximum items to fetch for list endpoints
        self.max_items = config.MAX_ITEMS_PER_ENDPOINT

        # Whether to test error scenarios
        self.test_errors = config.TEST_ERROR_SCENARIOS

        # Current authentication tokens
        self.current_tokens = {}

    def extract(self, apis: Dict[str, Any], auth_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test API endpoints and extract response information"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Python 'requests' package not available, skipping runtime API tests")
            return {
                'error': 'Python requests package not available',
                'endpoints_tested': 0,
                'endpoints_successful': 0,
            }

        if not self.base_url:
            logger.warning("No backend URL provided, skipping runtime API tests")
            return {
                'error': 'No backend URL provided',
                'endpoints_tested': 0,
                'endpoints_successful': 0,
            }

        logger.info(f"Testing API endpoints at {self.base_url}")

        # Extract authentication information to use in tests
        auth_headers = self._get_auth_headers(auth_info)

        # Results dictionary
        results = {
            'endpoints': {},
            'endpoints_tested': 0,
            'endpoints_successful': 0,
            'total_response_time': 0,
            'average_response_time': 0,
            'auth_methods': {},
            'status_codes': {},
            'content_types': {},
        }

        # Get the list of endpoints to test
        endpoints = apis.get('endpoints', [])

        # Test each endpoint
        for endpoint in endpoints:
            path = endpoint.get('path', '')
            if not path:
                continue

            # Only test GET endpoints by default
            if 'get' not in endpoint.get('http_methods', []):
                continue

            # Skip endpoints that require parameters in the URL
            if self._requires_url_params(path):
                logger.debug(f"Skipping endpoint {path} (requires URL parameters)")
                continue

            # Test the endpoint
            try:
                endpoint_result = self._test_endpoint(
                    path, 
                    endpoint, 
                    auth_headers
                )

                if endpoint_result:
                    results['endpoints'][path] = endpoint_result
                    results['endpoints_tested'] += 1

                    if endpoint_result.get('success', False):
                        results['endpoints_successful'] += 1

                        # Collect statistics
                        results['total_response_time'] += endpoint_result.get('response_time', 0)

                        # Count status codes
                        status_code = endpoint_result.get('status_code')
                        if status_code:
                            results['status_codes'][status_code] = results['status_codes'].get(status_code, 0) + 1

                        # Count content types
                        content_type = endpoint_result.get('content_type', '').split(';')[0]
                        if content_type:
                            results['content_types'][content_type] = results['content_types'].get(content_type, 0) + 1
            except Exception as e:
                logger.error(f"Error testing endpoint {path}: {str(e)}")

        # Calculate average response time
        if results['endpoints_successful'] > 0:
            results['average_response_time'] = results['total_response_time'] / results['endpoints_successful']

        logger.info(f"Tested {results['endpoints_tested']} endpoints, {results['endpoints_successful']} successful")
        return results

    def _test_endpoint(self, path: str, endpoint_info: Dict[str, Any], auth_headers: Dict[str, str]) -> Dict[str, Any]:
        """Test a single API endpoint"""
        url = urljoin(self.base_url, path)
        logger.debug(f"Testing endpoint: {url}")

        # Check if authentication is required
        requires_auth = endpoint_info.get('authentication', {}).get('requires_authentication', False)

        # Headers to use
        headers = {}
        if requires_auth:
            headers.update(auth_headers)

        # Results dictionary
        result = {
            'path': path,
            'url': url,
            'requires_auth': requires_auth,
            'method': 'GET',
            'success': False,
            'tested_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        try:
            # Make the request with timing
            start_time = time.time()
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                verify=False  # For testing against local/dev servers
            )
            end_time = time.time()
            response_time = end_time - start_time

            # Get response details
            result.update({
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_type': response.headers.get('Content-Type', ''),
                'response_size': len(response.content),
            })

            # Parse response content based on content type
            if 'application/json' in result['content_type']:
                try:
                    result['response'] = response.json()

                    # Limit large responses
                    if isinstance(result['response'], list) and len(result['response']) > self.max_items:
                        result['response'] = result['response'][:self.max_items]
                        result['response_truncated'] = True

                    # For objects with pagination
                    if isinstance(result['response'], dict) and 'results' in result['response']:
                        if isinstance(result['response']['results'], list) and len(result['response']['results']) > self.max_items:
                            result['response']['results'] = result['response']['results'][:self.max_items]
                            result['response_truncated'] = True

                except ValueError:
                    result['response'] = response.text[:1000]  # Limit text response
            else:
                # For non-JSON responses, just include the first part
                result['response'] = response.text[:1000]

            # Extract pagination information
            self._extract_pagination_info(result, response)

            # Test error scenarios if configured
            if self.test_errors and result['success']:
                result['error_tests'] = self._test_error_scenarios(url, headers)

        except RequestException as e:
            result.update({
                'success': False,
                'error': str(e),
            })
            logger.debug(f"Request error for {url}: {str(e)}")

        return result

    def _extract_pagination_info(self, result: Dict[str, Any], response) -> None:
        """Extract pagination information from a response"""
        pagination = {}

        # Check for common pagination patterns in the response
        if isinstance(result.get('response'), dict):
            resp = result['response']

            # Django REST Framework pattern
            if all(k in resp for k in ['count', 'next', 'previous', 'results']):
                pagination['type'] = 'drf_pagination'
                pagination['count'] = resp.get('count')
                pagination['next'] = resp.get('next')
                pagination['previous'] = resp.get('previous')

            # Page number pagination
            elif all(k in resp for k in ['page', 'pages', 'page_size']):
                pagination['type'] = 'page_number'
                pagination['page'] = resp.get('page')
                pagination['pages'] = resp.get('pages')
                pagination['page_size'] = resp.get('page_size')

            # Cursor pagination
            elif all(k in resp for k in ['next', 'previous', 'results']):
                pagination['type'] = 'cursor'
                pagination['next'] = resp.get('next')
                pagination['previous'] = resp.get('previous')

            # Offset/limit pagination
            elif all(k in resp for k in ['offset', 'limit', 'total']):
                pagination['type'] = 'offset_limit'
                pagination['offset'] = resp.get('offset')
                pagination['limit'] = resp.get('limit')
                pagination['total'] = resp.get('total')

        # Check headers for pagination info
        link_header = response.headers.get('Link')
        if link_header:
            pagination['type'] = 'header_link'
            pagination['link_header'] = link_header

        if pagination:
            result['pagination'] = pagination

    def _test_error_scenarios(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test common error scenarios for an endpoint"""
        error_results = {}

        # Test without authentication
        if headers:
            try:
                response = requests.get(url, timeout=self.timeout, verify=False)
                error_results['no_auth'] = {
                    'status_code': response.status_code,
                    'success': response.status_code < 400,
                }
            except RequestException:
                pass

        # Test with invalid parameters
        try:
            invalid_param_url = f"{url}?invalid_param=test"
            response = requests.get(
                invalid_param_url, 
                headers=headers, 
                timeout=self.timeout, 
                verify=False
            )
            error_results['invalid_param'] = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
            }
        except RequestException:
            pass

        return error_results

    def _get_auth_headers(self, auth_info: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers based on project's auth configuration"""
        headers = {}

        # Use token if provided in configuration
        if self.auth_token:
            if auth_info.get('primary_method') == 'jwt':
                headers['Authorization'] = f"Bearer {self.auth_token}"
            else:
                headers['Authorization'] = f"Token {self.auth_token}"
            return headers

        # Try to get token using credentials
        if self.auth_username and self.auth_password:
            # Check primary auth method
            primary_method = auth_info.get('auth_flows', {}).get('primary_method', '')

            if primary_method == 'jwt':
                jwt_token = self._get_jwt_token()
                if jwt_token:
                    headers['Authorization'] = f"Bearer {jwt_token}"
            elif primary_method == 'token':
                auth_token = self._get_auth_token()
                if auth_token:
                    headers['Authorization'] = f"Token {auth_token}"

        return headers

    def _get_jwt_token(self) -> Optional[str]:
        """Try to obtain a JWT token using configured credentials"""
        # Check if we already have a token
        if 'jwt' in self.current_tokens:
            return self.current_tokens['jwt']

        # Common JWT token endpoints
        token_endpoints = [
            '/api/token/',
            '/api/auth/token/',
            '/auth/token/',
            '/api/auth/login/',
            '/api/login/',
        ]

        for endpoint in token_endpoints:
            url = urljoin(self.base_url, endpoint)

            try:
                response = requests.post(
                    url,
                    json={
                        'username': self.auth_username,
                        'password': self.auth_password,
                    },
                    timeout=self.timeout,
                    verify=False
                )

                if response.status_code == 200:
                    data = response.json()

                    # Look for access token
                    token = data.get('access') or data.get('access_token') or data.get('token')

                    if token:
                        self.current_tokens['jwt'] = token
                        logger.info(f"Obtained JWT token from {endpoint}")
                        return token
            except RequestException:
                pass

        logger.warning("Could not obtain JWT token")
        return None

    def _get_auth_token(self) -> Optional[str]:
        """Try to obtain an authentication token using configured credentials"""
        # Check if we already have a token
        if 'token' in self.current_tokens:
            return self.current_tokens['token']

        # Common token endpoints
        token_endpoints = [
            '/api/auth-token/',
            '/api/token-auth/',
            '/api/auth/token/',
            '/api/get-token/',
            '/auth/token/',
        ]

        for endpoint in token_endpoints:
            url = urljoin(self.base_url, endpoint)

            try:
                response = requests.post(
                    url,
                    json={
                        'username': self.auth_username,
                        'password': self.auth_password,
                    },
                    timeout=self.timeout,
                    verify=False
                )

                if response.status_code == 200:
                    data = response.json()

                    # Look for token
                    token = data.get('token') or data.get('auth_token')

                    if token:
                        self.current_tokens['token'] = token
                        logger.info(f"Obtained auth token from {endpoint}")
                        return token
            except RequestException:
                pass

        logger.warning("Could not obtain auth token")
        return None

    def _requires_url_params(self, path: str) -> bool:
        """Check if a URL path requires parameters"""
        # Check for parameter patterns in the URL
        return '{' in path or '<' in path or ':' in path