# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown Documentation Generator

This module generates Markdown documentation from extracted backend information.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:20:08
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Generate Markdown documentation from extracted information"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

    def generate(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate Markdown documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where Markdown files will be generated
        """
        logger.info("Generating Markdown documentation")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create README.md (main index)
        self._generate_readme(data, output_dir)

        # Generate sections based on configuration
        for section in self.config.DOCUMENTATION_SECTIONS:
            if section == 'project_overview':
                self._generate_project_overview(data, output_dir)
            elif section == 'models_and_database':
                self._generate_models_documentation(data, output_dir)
            elif section == 'api_endpoints':
                self._generate_api_documentation(data, output_dir)
            elif section == 'authentication':
                self._generate_authentication_documentation(data, output_dir)
            elif section == 'frontend_integration':
                self._generate_frontend_integration(data, output_dir)
            elif section == 'typescript_interfaces':
                # Skip TypeScript interfaces in Markdown output
                pass

        logger.info(f"Markdown documentation generated in {output_dir}")

    def _generate_readme(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate main README.md with project overview and navigation"""
        readme_path = output_dir / "README.md"

        # Get project info
        project_info = data.get('project_info', {})
        project_name = project_info.get('name', 'Django Project')

        # Get extraction date
        extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'extraction_date' in project_info:
            try:
                extraction_date = datetime.fromisoformat(project_info['extraction_date']).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                pass

        # Get counts for key statistics
        model_count = sum(len(app_info.get('models', {})) 
                          for app_info in data.get('models', {}).values())
        api_count = len(data.get('apis', {}).get('endpoints', []))
        serializer_count = data.get('serializers', {}).get('count', 0)

        # Create README content
        readme = [
            f"# {project_name} Backend Documentation",
            "",
            "This documentation provides comprehensive information about the backend system for frontend development.",
            "",
            f"**Generated on:** {extraction_date}",
            "",
            "## Table of Contents",
            "",
            "1. [Project Overview](project_overview.md)",
            "2. [Models and Database Schema](models_and_database.md)",
            "3. [API Endpoints](api_endpoints.md)",
            "4. [Authentication and Authorization](authentication.md)",
            "5. [Frontend Integration Guide](frontend_integration.md)",
            "",
            "## Quick Statistics",
            "",
            f"- **Django Apps:** {len(project_info.get('apps', []))}",
            f"- **Models:** {model_count}",
            f"- **API Endpoints:** {api_count}",
            f"- **Serializers:** {serializer_count}",
            "",
            "## How to Use This Documentation",
            "",
            "This documentation is designed for frontend developers working with this backend system. ",
            "It provides detailed information about the data models, API endpoints, authentication ",
            "requirements, and more. For effective integration, we recommend the following approach:",
            "",
            "1. Start with the **Project Overview** to understand the system architecture",
            "2. Review the **Models and Database Schema** to understand the data structures",
            "3. Explore the **API Endpoints** to see available operations and request/response formats",
            "4. Check the **Authentication** section to implement proper auth flows",
            "5. Use the **Frontend Integration Guide** for best practices and examples",
            "",
            "## Notes for Frontend Developers",
            "",
            "When implementing frontend components that interact with this backend:",
            "",
            "- Always check authentication requirements for endpoints",
            "- Use the TypeScript interfaces to ensure type safety",
            "- Follow the pagination patterns described in the API documentation",
            "- Reference the example React hooks for common data fetching patterns",
            "",
            f"---",
            f"Generated with Backend Documentation Generator | Detail Level: {self.detail_level.capitalize()}",
        ]

        # Write README
        with open(readme_path, 'w') as f:
            f.write('\n'.join(readme))

        logger.info(f"Generated README.md")

    def _generate_project_overview(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate project overview documentation"""
        overview_path = output_dir / "project_overview.md"

        # Get project info
        project_info = data.get('project_info', {})
        project_name = project_info.get('name', 'Django Project')

        # Create overview content
        overview = [
            f"# {project_name} Project Overview",
            "",
            "## System Architecture",
            "",
            "This Django application follows a standard architectural pattern with the following components:",
            "",
            "- **Models**: Define the database schema and data relationships",
            "- **Views/ViewSets**: Handle API requests and responses",
            "- **Serializers**: Transform data between Python objects and API formats",
            "- **URLs**: Define the API endpoints",
            "- **Settings**: Configure the application behavior",
            "",
            "## Django Apps",
            "",
        ]

        # Add apps information
        apps = project_info.get('apps', [])
        if apps:
            overview.append("The project consists of the following Django apps:")
            overview.append("")

            for app in apps:
                overview.append(f"- **{app}**")
        else:
            overview.append("No Django apps information available.")

        overview.extend([
            "",
            "## Environment Configuration",
            "",
            "The application requires the following environment configuration:",
            "",
            "- **Database**: PostgreSQL database connection details",
            "- **Secret Key**: Django secret key for cryptographic signing",
            "- **Debug Mode**: Set to False in production",
            "- **Allowed Hosts**: Domains that can serve the application",
            "",
            "## Backend Technologies",
            "",
            "The backend is built with the following core technologies:",
            "",
            "- **Django**: Web framework for building the application",
            "- **Django REST Framework**: Library for building RESTful APIs",
            "- **PostgreSQL**: Relational database management system",
            "",
            "## External Services",
            "",
            "The system may integrate with the following external services (check settings for details):",
            "",
            "- **Email Provider**: For sending notifications and password resets",
            "- **File Storage**: For storing media files",
            "- **Authentication Providers**: For social authentication (if configured)",
            "",
            f"---",
            "[Back to Index](README.md)",
        ])

        # Write overview file
        with open(overview_path, 'w') as f:
            f.write('\n'.join(overview))

        logger.info(f"Generated project_overview.md")

    def _generate_models_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate documentation for models and database schema"""
        models_path = output_dir / "models_and_database.md"

        # Get models data
        models_data = data.get('models', {})

        # Create models documentation content
        models_doc = [
            "# Models and Database Schema",
            "",
            "This document describes all models in the system and their relationships.",
            "",
            "## Table of Contents",
            "",
        ]

        # Generate table of contents
        app_count = 0
        for app_label, app_info in sorted(models_data.items()):
            app_count += 1
            models_doc.append(f"{app_count}. [{app_label}](#app-{app_label.lower().replace('.', '-')})")

        # Generate detailed documentation for each app
        if app_count > 0:
            for app_label, app_info in sorted(models_data.items()):
                models_doc.extend([
                    "",
                    f"<a id='app-{app_label.lower().replace('.', '-')}'></a>",
                    f"## {app_label}",
                    "",
                ])

                # Add models for this app
                for model_name, model_info in sorted(app_info.get('models', {}).items()):
                    models_doc.extend([
                        f"### {model_name}",
                        "",
                        f"**Table Name:** `{model_info.get('table_name')}`",
                        "",
                        f"{model_info.get('verbose_name_plural', model_name)}",
                        "",
                        "#### Fields",
                        "",
                        "| Field | Type | Required | Description |",
                        "| ----- | ---- | -------- | ----------- |",
                    ])

                    # Add fields
                    for field_name, field_info in sorted(model_info.get('fields', {}).items()):
                        required = "Yes" if not field_info.get('null', True) and not field_info.get('blank', True) else "No"
                        description = field_info.get('help_text', '') or field_info.get('verbose_name', '')
                        field_type = field_info.get('type', '')

                        # Add extra type info
                        if field_type == 'CharField' and 'max_length' in field_info:
                            field_type += f" (max_length={field_info['max_length']})"
                        elif field_type == 'DecimalField' and 'max_digits' in field_info:
                            field_type += f" (max_digits={field_info['max_digits']}, decimal_places={field_info.get('decimal_places', 0)})"

                        models_doc.append(f"| {field_name} | {field_type} | {required} | {description} |")

                    # Add relationships
                    relationships = model_info.get('relationships', {})

                    # Foreign keys
                    foreign_keys = relationships.get('foreign_keys', [])
                    if foreign_keys:
                        models_doc.extend([
                            "",
                            "#### Foreign Keys",
                            "",
                            "| Field | References | On Delete | Description |",
                            "| ----- | ---------- | --------- | ----------- |",
                        ])

                        for fk in foreign_keys:
                            target = f"{fk.get('target_app')}.{fk.get('target_model')}"
                            on_delete = fk.get('on_delete', '')
                            description = fk.get('help_text', '') or fk.get('verbose_name', '')

                            models_doc.append(f"| {fk.get('name')} | {target} | {on_delete} | {description} |")

                    # Many to many
                    many_to_many = relationships.get('many_to_many', [])
                    if many_to_many:
                        models_doc.extend([
                            "",
                            "#### Many-to-Many Relationships",
                            "",
                            "| Field | Related Model | Through | Description |",
                            "| ----- | ------------- | ------- | ----------- |",
                        ])

                        for m2m in many_to_many:
                            target = f"{m2m.get('target_app')}.{m2m.get('target_model')}"
                            through = m2m.get('through', '')
                            description = m2m.get('help_text', '') or m2m.get('verbose_name', '')

                            models_doc.append(f"| {m2m.get('name')} | {target} | {through} | {description} |")

                    # One to one
                    one_to_one = relationships.get('one_to_one', [])
                    if one_to_one:
                        models_doc.extend([
                            "",
                            "#### One-to-One Relationships",
                            "",
                            "| Field | Related Model | On Delete | Description |",
                            "| ----- | ------------- | --------- | ----------- |",
                        ])

                        for o2o in one_to_one:
                            target = f"{o2o.get('target_app')}.{o2o.get('target_model')}"
                            on_delete = o2o.get('on_delete', '')
                            description = o2o.get('help_text', '') or o2o.get('verbose_name', '')

                            models_doc.append(f"| {o2o.get('name')} | {target} | {on_delete} | {description} |")

                    # Meta options
                    meta = model_info.get('meta_options', {})
                    if meta and (meta.get('ordering') or meta.get('unique_together') or meta.get('index_together')):
                        models_doc.extend([
                            "",
                            "#### Meta Options",
                            "",
                        ])

                        if meta.get('ordering'):
                            models_doc.extend([
                                "**Ordering:** " + ", ".join(str(field) for field in meta.get('ordering', [])),
                                "",
                            ])

                        if meta.get('unique_together'):
                            models_doc.extend([
                                "**Unique Together:**",
                                "",
                            ])
                            for ut in meta.get('unique_together', []):
                                models_doc.append(f"- " + ", ".join(str(field) for field in ut))
                            models_doc.append("")

                        if meta.get('index_together'):
                            models_doc.extend([
                                "**Index Together:**",
                                "",
                            ])
                            for it in meta.get('index_together', []):
                                models_doc.append(f"- " + ", ".join(str(field) for field in it))
                            models_doc.append("")

                    # Add separator between models
                    models_doc.append("")
        else:
            models_doc.extend([
                "",
                "No model information available.",
                "",
            ])

        # Add footer
        models_doc.extend([
            f"---",
            "[Back to Index](README.md)",
        ])

        # Write models file
        with open(models_path, 'w') as f:
            f.write('\n'.join(models_doc))

        logger.info(f"Generated models_and_database.md")

    def _generate_api_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate API endpoints documentation"""
        api_path = output_dir / "api_endpoints.md"

        # Get API data
        apis = data.get('apis', {})
        endpoints = apis.get('endpoints', [])
        grouped_endpoints = apis.get('grouped', {})

        # Create API documentation content
        api_doc = [
            "# API Endpoints",
            "",
            "This document describes all available API endpoints in the system.",
            "",
            "## Table of Contents",
            "",
        ]

        # Generate table of contents by app
        if grouped_endpoints:
            app_index = 1
            for app_name, app_info in sorted(grouped_endpoints.items()):
                api_doc.append(f"{app_index}. [{app_name}](#app-{app_name.lower().replace('.', '-')})")
                app_index += 1
        else:
            # Simple list of endpoints if not grouped
            api_doc.append("- [All Endpoints](#all-endpoints)")

        # Generate detailed documentation
        if grouped_endpoints:
            for app_name, app_info in sorted(grouped_endpoints.items()):
                api_doc.extend([
                    "",
                    f"<a id='app-{app_name.lower().replace('.', '-')}'></a>",
                    f"## {app_name}",
                    "",
                ])

                # Add endpoints for this app
                for endpoint in app_info.get('endpoints', []):
                    api_doc.extend(self._format_endpoint(endpoint, data))
        elif endpoints:
            # Simple list if not grouped
            api_doc.extend([
                "",
                "<a id='all-endpoints'></a>",
                "## All Endpoints",
                "",
            ])

            for endpoint in endpoints:
                api_doc.extend(self._format_endpoint(endpoint, data))
        else:
            api_doc.extend([
                "",
                "No API endpoint information available.",
                "",
            ])

        # Add footer
        api_doc.extend([
            f"---",
            "[Back to Index](README.md)",
        ])

        # Write API file
        with open(api_path, 'w') as f:
            f.write('\n'.join(api_doc))

        logger.info(f"Generated api_endpoints.md")

    def _format_endpoint(self, endpoint: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
        """Format an API endpoint for Markdown documentation"""
        result = []

        # Get basic endpoint info
        path = endpoint.get('path', '')
        http_methods = endpoint.get('http_methods', [])
        http_methods_str = ', '.join(method.upper() for method in http_methods)

        # Endpoint header
        result.extend([
            f"### `{path}`",
            "",
            f"**Methods:** {http_methods_str}",
            "",
        ])

        # Add endpoint description from docstring
        view_info = endpoint.get('view', {})
        docstring = view_info.get('docstring', '')
        if not docstring and 'method_docstrings' in view_info:
            # Try to get method docstring for the first HTTP method
            for method in http_methods:
                if method in view_info.get('method_docstrings', {}):
                    docstring = view_info['method_docstrings'][method]
                    break

        if docstring:
            result.extend([
                "**Description:**",
                "",
                docstring,
                "",
            ])

        # Add authentication requirements
        auth_info = endpoint.get('authentication', {})
        requires_auth = auth_info.get('requires_authentication', False)

        result.append("**Requires Authentication:** " + ("Yes" if requires_auth else "No"))
        result.append("")

        if requires_auth and auth_info.get('permission_classes'):
            result.append("**Permission Classes:**")
            result.append("")
            for permission in auth_info.get('permission_classes', []):
                result.append(f"- {permission.get('class', '')}")
            result.append("")

        # Add query parameters
        query_params = endpoint.get('query_params', [])
        if query_params:
            result.extend([
                "**Query Parameters:**",
                "",
                "| Parameter | Type | Required | Description |",
                "| --------- | ---- | -------- | ----------- |",
            ])

            for param in query_params:
                name = param.get('name', '')
                param_type = param.get('type', '')
                required = "Yes" if param.get('required', False) else "No"
                description = param.get('description', '')

                result.append(f"| {name} | {param_type} | {required} | {description} |")

            result.append("")

        # Add response format from serializer
        serializer_info = endpoint.get('serializer', {})
        if serializer_info and 'fields' in serializer_info:
            result.extend([
                "**Response Format:**",
                "",
                "| Field | Type | Read Only | Description |",
                "| ----- | ---- | --------- | ----------- |",
            ])

            for field_name, field_info in sorted(serializer_info.get('fields', {}).items()):
                field_type = field_info.get('type', '')
                read_only = "Yes" if field_info.get('read_only', False) else "No"
                description = field_info.get('help_text', '')

                result.append(f"| {field_name} | {field_type} | {read_only} | {description} |")

            result.append("")

        # Add example response if available from runtime tests
        runtime_tests = data.get('runtime_tests', {}).get('endpoints', {})
        if path in runtime_tests and runtime_tests[path].get('success', False):
            response_example = runtime_tests[path].get('response')
            if response_example:
                result.extend([
                    "**Example Response:**",
                    "",
                    "```json",
                ])

                # Format response as JSON
                if isinstance(response_example, (dict, list)):
                    try:
                        result.append(json.dumps(response_example, indent=2))
                    except:
                        result.append(str(response_example))
                else:
                    result.append(str(response_example))

                result.extend([
                    "```",
                    "",
                ])

        # Add separator
        result.append("")

        return result

    def _generate_authentication_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate authentication and authorization documentation"""
        auth_path = output_dir / "authentication.md"

        # Get authentication data
        auth_data = data.get('authentication', {})

        # Create authentication documentation content
        auth_doc = [
            "# Authentication and Authorization",
            "",
            "This document describes the authentication and authorization mechanisms used in the system.",
            "",
        ]

        # Add primary authentication method
        primary_method = auth_data.get('auth_flows', {}).get('primary_method', '')
        if primary_method:
            auth_doc.extend([
                "## Primary Authentication Method",
                "",
                f"The primary authentication method used in this system is **{primary_method.upper()}**.",
                "",
            ])

        # Add authentication flows
        auth_flows = auth_data.get('auth_flows', {})
        if auth_flows:
            auth_doc.extend([
                "## Supported Authentication Methods",
                "",
            ])

            if auth_flows.get('token_based_auth'):
                auth_doc.extend([
                    "### Token Authentication",
                    "",
                    "The system supports token-based authentication. To authenticate:",
                    "",
                    "1. Obtain a token by sending credentials to the token endpoint",
                    "2. Include the token in the `Authorization` header with all subsequent requests",
                    "",
                    "```http",
                    "Authorization: Token your_token_here",
                    "```",
                    "",
                ])

            if auth_flows.get('jwt_auth'):
                auth_doc.extend([
                    "### JWT Authentication",
                    "",
                    "The system uses JSON Web Tokens (JWT) for authentication. The process is:",
                    "",
                    "1. Obtain access and refresh tokens by sending credentials to the JWT endpoint",
                    "2. Include the access token in the `Authorization` header with all requests",
                    "3. When the access token expires, use the refresh token to get a new one",
                    "",
                    "```http",
                    "Authorization: Bearer your_jwt_access_token",
                    "```",
                    "",
                ])

                # Add JWT settings if available
                jwt_settings = auth_data.get('jwt_auth', {})
                if jwt_settings:
                    token_lifetime = jwt_settings.get('access_token_lifetime', '')
                    refresh_lifetime = jwt_settings.get('refresh_token_lifetime', '')

                    auth_doc.extend([
                        "**Token Lifetimes:**",
                        "",
                        f"- Access Token: {token_lifetime}",
                        f"- Refresh Token: {refresh_lifetime}",
                        "",
                    ])

            if auth_flows.get('session_auth'):
                auth_doc.extend([
                    "### Session Authentication",
                    "",
                    "The system supports session-based authentication for browser clients.",
                    "This method uses cookies to maintain the session state.",
                    "",
                ])

            if auth_flows.get('oauth2'):
                auth_doc.extend([
                    "### OAuth2",
                    "",
                    "The system supports OAuth2 for authentication with external providers.",
                    "",
                ])

            if auth_flows.get('basic_auth'):
                auth_doc.extend([
                    "### Basic Authentication",
                    "",
                    "The system supports HTTP Basic Authentication. To authenticate:",
                    "",
                    "```http",
                    "Authorization: Basic base64(username:password)",
                    "```",
                    "",
                    "*Note: Basic authentication should only be used over HTTPS.*",
                    "",
                ])

        # Add token lifetimes
        token_lifetimes = auth_data.get('token_lifetimes', {})
        if token_lifetimes:
            auth_doc.extend([
                "## Token Lifetimes",
                "",
            ])

            for token_type, lifetime in token_lifetimes.items():
                auth_doc.append(f"- **{token_type}**: {lifetime}")

            auth_doc.append("")

        # Add permission classes
        permission_classes = auth_data.get('permission_classes', [])
        if permission_classes:
            auth_doc.extend([
                "## Permission Classes",
                "",
                "The system uses the following permission classes to control access:",
                "",
            ])

            for permission in permission_classes:
                name = permission.get('name', '')
                docstring = permission.get('docstring', '')

                auth_doc.extend([
                    f"### {name}",
                    "",
                ])

                if docstring:
                    auth_doc.extend([
                        docstring,
                        "",
                    ])

            auth_doc.append("")

        # Add authentication endpoints
        auth_doc.extend([
            "## Authentication Endpoints",
            "",
            "### Login and Token Acquisition",
            "",
        ])

        # Add JWT endpoints if used
        if auth_flows.get('jwt_auth'):
            auth_doc.extend([
                "#### JWT Authentication Endpoints",
                "",
                "| Endpoint | Method | Description |",
                "| -------- | ------ | ----------- |",
                "| `/api/token/` | POST | Obtain JWT access and refresh tokens |",
                "| `/api/token/refresh/` | POST | Refresh JWT access token |",
                "| `/api/token/verify/` | POST | Verify JWT token validity |",
                "",
            ])

        # Add token endpoints if used
        if auth_flows.get('token_based_auth'):
            auth_doc.extend([
                "#### Token Authentication Endpoints",
                "",
                "| Endpoint | Method | Description |",
                "| -------- | ------ | ----------- |",
                "| `/api/auth-token/` | POST | Obtain authentication token |",
                "",
            ])

        # Add session endpoints if used
        if auth_flows.get('session_auth'):
            auth_doc.extend([
                "#### Session Authentication Endpoints",
                "",
                "| Endpoint | Method | Description |",
                "| -------- | ------ | ----------- |",
                "| `/accounts/login/` | POST | Log in and create session |",
                "| `/accounts/logout/` | POST | Log out and destroy session |",
                "",
            ])

        # Add footer
        auth_doc.extend([
            f"---",
            "[Back to Index](README.md)",
        ])

        # Write authentication file
        with open(auth_path, 'w') as f:
            f.write('\n'.join(auth_doc))

        logger.info(f"Generated authentication.md")

    def _generate_frontend_integration(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate frontend integration documentation"""
        integration_path = output_dir / "frontend_integration.md"

        # Get authentication data
        auth_data = data.get('authentication', {})
        primary_auth_method = auth_data.get('auth_flows', {}).get('primary_method', '')

        # Create frontend integration documentation content
        integration_doc = [
            "# Frontend Integration Guide",
            "",
            "This document provides guidelines and examples for integrating the backend with frontend applications.",
            "",
            "## API Base URL",
            "",
            f"All API endpoints are relative to the base URL of the backend server. ",
            f"For example, if the backend is hosted at `https://api.example.com`, ",
            f"then the full URL for an endpoint would be `https://api.example.com/api/endpoint/`.",
            "",
            "## Authentication Integration",
            "",
        ]

        # Add authentication integration details based on primary method
        if primary_auth_method == 'jwt':
            integration_doc.extend([
                "### JWT Authentication",
                "",
                "This backend uses JSON Web Tokens (JWT) for authentication. Here's how to implement it in your frontend:",
                "",
                "#### 1. Login and Token Storage",
                "",
                "```javascript",
                "// Example using fetch API",
                "async function login(username, password) {",
                "  try {",
                "    const response = await fetch('/api/token/', {",
                "      method: 'POST',",
                "      headers: {",
                "        'Content-Type': 'application/json',",
                "      },",
                "      body: JSON.stringify({ username, password }),",
                "    });",
                "",
                "    const data = await response.json();",
                "",
                "    if (response.ok) {",
                "      // Store tokens securely",
                "      localStorage.setItem('accessToken', data.access);",
                "      localStorage.setItem('refreshToken', data.refresh);",
                "      return true;",
                "    } else {",
                "      // Handle error",
                "      console.error('Login failed:', data);",
                "      return false;",
                "    }",
                "  } catch (error) {",
                "    console.error('Login error:', error);",
                "    return false;",
                "  }",
                "}",
                "```",
                "",
                "#### 2. Authenticated Requests",
                "",
                "```javascript",
                "// Example of making authenticated API calls",
                "async function fetchData(url) {",
                "  const accessToken = localStorage.getItem('accessToken');",
                "",
                "  try {",
                "    const response = await fetch(url, {",
                "      headers: {",
                "        'Authorization': `Bearer ${accessToken}`,",
                "        'Content-Type': 'application/json',",
                "      },",
                "    });",
                "",
                "    if (response.status === 401) {",
                "      // Token expired, try to refresh",
                "      const refreshed = await refreshToken();",
                "      if (refreshed) {",
                "        // Retry the request with the new token",
                "        return fetchData(url);",
                "      } else {",
                "        // Refresh failed, redirect to login",
                "        redirectToLogin();",
                "        return null;",
                "      }",
                "    }",
                "",
                "    return response.json();",
                "  } catch (error) {",
                "    console.error('API request failed:', error);",
                "    return null;",
                "  }",
                "}",
                "```",
                "",
                "#### 3. Token Refresh",
                "",
                "```javascript",
                "// Example of refreshing the JWT token",
                "async function refreshToken() {",
                "  const refreshToken = localStorage.getItem('refreshToken');",
                "",
                "  if (!refreshToken) {",
                "    return false;",
                "  }",
                "",
                "  try {",
                "    const response = await fetch('/api/token/refresh/', {",
                "      method: 'POST',",
                "      headers: {",
                "        'Content-Type': 'application/json',",
                "      },",
                "      body: JSON.stringify({ refresh: refreshToken }),",
                "    });",
                "",
                "    if (response.ok) {",
                "      const data = await response.json();",
                "      localStorage.setItem('accessToken', data.access);",
                "      return true;",
                "    } else {",
                "      // Refresh failed, clear tokens",
                "      localStorage.removeItem('accessToken');",
                "      localStorage.removeItem('refreshToken');",
                "      return false;",
                "    }",
                "  } catch (error) {",
                "    console.error('Token refresh error:', error);",
                "    return false;",
                "  }",
                "}",
                "```",
                "",
            ])
        elif primary_auth_method == 'token':
            integration_doc.extend([
                "### Token Authentication",
                "",
                "This backend uses token-based authentication. Here's how to implement it in your frontend:",
                "",
                "#### 1. Login and Token Storage",
                "",
                "```javascript",
                "// Example using fetch API",
                "async function login(username, password) {",
                "  try {",
                "    const response = await fetch('/api/auth-token/', {",
                "      method: 'POST',",
                "      headers: {",
                "        'Content-Type': 'application/json',",
                "      },",
                "      body: JSON.stringify({ username, password }),",
                "    });",
                "",
                "    const data = await response.json();",
                "",
                "    if (response.ok) {",
                "      // Store token securely",
                "      localStorage.setItem('authToken', data.token);",
                "      return true;",
                "    } else {",
                "      // Handle error",
                "      console.error('Login failed:', data);",
                "      return false;",
                "    }",
                "  } catch (error) {",
                "    console.error('Login error:', error);",
                "    return false;",
                "  }",
                "}",
                "```",
                "",
                "#### 2. Authenticated Requests",
                "",
                "```javascript",
                "// Example of making authenticated API calls",
                "async function fetchData(url) {",
                "  const authToken = localStorage.getItem('authToken');",
                "",
                "  try {",
                "    const response = await fetch(url, {",
                "      headers: {",
                "        'Authorization': `Token ${authToken}`,",
                "        'Content-Type': 'application/json',",
                "      },",
                "    });",
                "",
                "    if (response.status === 401) {",
                "      // Token expired, redirect to login",
                "      redirectToLogin();",
                "      return null;",
                "    }",
                "",
                "    return response.json();",
                "  } catch (error) {",
                "    console.error('API request failed:', error);",
                "    return null;",
                "  }",
                "}",
                "```",
                "",
            ])
        elif primary_auth_method == 'session':
            integration_doc.extend([
                "### Session Authentication",
                "",
                "This backend uses session-based authentication. Here's how to implement it in your frontend:",
                "",
                "#### 1. Login",
                "",
                "```javascript",
                "// Example using fetch API with credentials",
                "async function login(username, password) {",
                "  try {",
                "    const response = await fetch('/accounts/login/', {",
                "      method: 'POST',",
                "      headers: {",
                "        'Content-Type': 'application/json',",
                "      },",
                "      body: JSON.stringify({ username, password }),",
                "      // Important for session cookies",
                "      credentials: 'include',",
                "    });",
                "",
                "    if (response.ok) {",
                "      return true;",
                "    } else {",
                "      // Handle error",
                "      console.error('Login failed');",
                "      return false;",
                "    }",
                "  } catch (error) {",
                "    console.error('Login error:', error);",
                "    return false;",
                "  }",
                "}",
                "```",
                "",
                "#### 2. Authenticated Requests",
                "",
                "```javascript",
                "// Example of making authenticated API calls with session",
                "async function fetchData(url) {",
                "  try {",
                "    const response = await fetch(url, {",
                "      // Important for session cookies",
                "      credentials: 'include',",
                "      headers: {",
                "        'Content-Type': 'application/json',",
                "      },",
                "    });",
                "",
                "    if (response.status === 403 || response.status === 401) {",
                "      // Session expired, redirect to login",
                "      redirectToLogin();",
                "      return null;",
                "    }",
                "",
                "    return response.json();",
                "  } catch (error) {",
                "    console.error('API request failed:', error);",
                "    return null;",
                "  }",
                "}",
                "```",
                "",
            ])
        else:
            integration_doc.extend([
                "### Authentication",
                "",
                "Check the [Authentication](authentication.md) section for details on the authentication system.",
                "",
            ])

        # Add data fetching patterns section
        integration_doc.extend([
            "## Data Fetching Patterns",
            "",
            "### Handling Paginated Responses",
            "",
            "Many API endpoints return paginated results. Here's how to handle them:",
            "",
            "```javascript",
            "// Example of fetching paginated data",
            "async function fetchPaginatedData(baseUrl) {",
            "  let url = baseUrl;",
            "  let allResults = [];",
            "",
            "  while (url) {",
            "    const response = await fetchData(url);",
            "    ",
            "    if (!response) break;",
            "    ",
            "    // Add results to the array",
            "    allResults = [...allResults, ...response.results];",
            "    ",
            "    // Update URL to next page or null",
            "    url = response.next;",
            "  }",
            "  ",
            "  return allResults;",
            "}",
            "```",
            "",
            "### Error Handling",
            "",
            "It's important to handle errors consistently in your frontend application:",
            "",
            "```javascript",
            "// Example of API call with comprehensive error handling",
            "async function apiRequest(url, options = {}) {",
            "  try {",
            "    // Set default headers and credentials",
            "    const requestOptions = {",
            "      headers: {",
            "        'Content-Type': 'application/json',",
            "        ...(getAuthHeader()), // Get auth header based on your auth method",
            "        ...options.headers,",
            "      },",
            "      ...options,",
            "    };",
            "",
            "    const response = await fetch(url, requestOptions);",
            "",
            "    // Parse the response based on content type",
            "    const contentType = response.headers.get('content-type');",
            "    let data;",
            "",
            "    if (contentType && contentType.includes('application/json')) {",
            "      data = await response.json();",
            "    } else {",
            "      data = await response.text();",
            "    }",
            "",
            "    // Handle different response statuses",
            "    if (response.ok) {",
            "      return { success: true, data, status: response.status };",
            "    } else {",
            "      // Handle specific error codes",
            "      if (response.status === 401) {",
            "        // Handle authentication errors",
            "        handleAuthError();",
            "      }",
            "",
            "      return {",
            "        success: false,",
            "        error: data,",
            "        status: response.status,",
            "        message: data.detail || data.message || 'An error occurred',",
            "      };",
            "    }",
            "  } catch (error) {",
            "    // Handle network errors",
            "    return {",
            "      success: false,",
            "      error,",
            "      message: 'Network error',",
            "    };",
            "  }",
            "}",
            "```",
            "",
        ])

        # Add React hooks section
        integration_doc.extend([
            "## React Integration",
            "",
            "### React Hooks for API Calls",
            "",
            "Here are some example React hooks for interacting with the API:",
            "",
            "#### useFetch Hook",
            "",
            "```jsx",
            "import { useState, useEffect } from 'react';",
            "",
            "export function useFetch(url, options = {}) {",
            "  const [data, setData] = useState(null);",
            "  const [loading, setLoading] = useState(true);",
            "  const [error, setError] = useState(null);",
            "  const [refetchIndex, setRefetchIndex] = useState(0);",
            "",
            "  const refetch = () => setRefetchIndex(prev => prev + 1);",
            "",
            "  useEffect(() => {",
            "    let isMounted = true;",
            "    const controller = new AbortController();",
            "    const signal = controller.signal;",
            "",
            "    const fetchData = async () => {",
            "      setLoading(true);",
            "",
            "      try {",
            "        // Add auth header to options",
            "        const authHeader = getAuthHeader();",
            "        const fetchOptions = {",
            "          ...options,",
            "          headers: {",
            "            ...options.headers,",
            "            ...authHeader,",
            "          },",
            "          signal,",
            "        };",
            "",
            "        const response = await fetch(url, fetchOptions);",
            "        const result = await response.json();",
            "",
            "        if (!response.ok) {",
            "          throw new Error(result.detail || 'An error occurred');",
            "        }",
            "",
            "        if (isMounted) {",
            "          setData(result);",
            "          setError(null);",
            "        }",
            "      } catch (err) {",
            "        if (isMounted && err.name !== 'AbortError') {",
            "          setError(err.message);",
            "          setData(null);",
            "        }",
            "      } finally {",
            "        if (isMounted) {",
            "          setLoading(false);",
            "        }",
            "      }",
            "    };",
            "",
            "    fetchData();",
            "",
            "    return () => {",
            "      isMounted = false;",
            "      controller.abort();",
            "    };",
            "  }, [url, refetchIndex, JSON.stringify(options)]);",
            "",
            "  return { data, loading, error, refetch };",
            "}",
            "```",
            "",
            "#### Usage Example",
            "",
            "```jsx",
            "function UserList() {",
            "  const { data, loading, error } = useFetch('/api/users/');",
            "",
            "  if (loading) return <p>Loading...</p>;",
            "  if (error) return <p>Error: {error}</p>;",
            "",
            "  return (",
            "    <ul>",
            "      {data?.results.map(user => (",
            "        <li key={user.id}>{user.username}</li>",
            "      ))}",
            "    </ul>",
            "  );",
            "}",
            "```",
            "",
        ])

        # Add file upload section
        integration_doc.extend([
            "## File Upload",
            "",
            "For file uploads, use the following pattern:",
            "",
            "```javascript",
            "async function uploadFile(file, url) {",
            "  const formData = new FormData();",
            "  formData.append('file', file);",
            "",
            "  const authHeader = getAuthHeader();",
            "",
            "  try {",
            "    const response = await fetch(url, {",
            "      method: 'POST',",
            "      headers: {",
            "        ...authHeader,",
            "        // Do NOT set Content-Type when using FormData",
            "        // Browser will set it automatically with boundary",
            "      },",
            "      body: formData,",
            "    });",
            "",
            "    if (!response.ok) {",
            "      throw new Error('File upload failed');",
            "    }",
            "",
            "    return await response.json();",
            "  } catch (error) {",
            "    console.error('Upload error:', error);",
            "    throw error;",
            "  }",
            "}",
            "```",
            "",
        ])

        # Add best practices section
        integration_doc.extend([
            "## Best Practices",
            "",
            "### State Management",
            "",
            "For complex applications, consider using a state management library:",
            "",
            "- **Redux Toolkit**: For large applications with complex state",
            "- **Zustand**: For simpler applications with less boilerplate",
            "- **React Context**: For small to medium applications",
            "",
            "### TypeScript Integration",
            "",
            "Use the TypeScript interfaces generated in the `typescript` directory to ensure type safety:",
            "",
            "```typescript",
            "// Example usage of generated types",
            "import { User, UserResponse } from '../types/api';",
            "",
            "async function fetchUserById(userId: number): Promise<User | null> {",
            "  try {",
            "    const response = await fetch(`/api/users/${userId}/`);",
            "    const data: UserResponse = await response.json();",
            "    return data;",
            "  } catch (error) {",
            "    console.error('Error fetching user:', error);",
            "    return null;",
            "  }",
            "}",
            "```",
            "",
            "### Performance Optimization",
            "",
            "- Use `React.memo` for components that render frequently with the same props",
            "- Implement request caching for frequently used data",
            "- Use pagination and infinite scrolling for large data sets",
            "- Implement debouncing for search inputs and other frequent user interactions",
            "",
            f"---",
            "[Back to Index](README.md)",
        ])

        # Write integration file
        with open(integration_path, 'w') as f:
            f.write('\n'.join(integration_doc))

        logger.info(f"Generated frontend_integration.md")