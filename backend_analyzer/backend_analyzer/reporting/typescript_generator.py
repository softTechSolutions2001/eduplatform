"""
TypeScript interface generator for Django backend analysis.

This module provides functionality to generate TypeScript interfaces and
API service functions from Django models and API endpoints.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple

logger = logging.getLogger('backend_analyzer')


class TypeScriptGenerator:
    """Generator for TypeScript interfaces and API services."""
    
    def __init__(self, 
                 api_endpoints: List[Dict[str, Any]], 
                 data_models: Dict[str, Any],
                 serializers: Dict[str, Any],
                 model_serializer_mapping: Dict[str, List[str]],
                 base_url: str = '/api'):
        """
        Initialize the TypeScript generator.
        
        Args:
            api_endpoints: List of API endpoints
            data_models: Dictionary of data models
            serializers: Dictionary of serializers
            model_serializer_mapping: Mapping of models to serializers
            base_url: Base URL for API requests
        """
        self.api_endpoints = api_endpoints
        self.data_models = data_models
        self.serializers = serializers
        self.model_serializer_mapping = model_serializer_mapping
        self.base_url = base_url
        
        # Track processed models to avoid duplicates
        self.processed_models = set()
        
        # Map Django field types to TypeScript types
        self.type_map = {
            'AutoField': 'number',
            'BigAutoField': 'number',
            'BooleanField': 'boolean',
            'CharField': 'string',
            'DateField': 'string',
            'DateTimeField': 'string',
            'DecimalField': 'number',
            'EmailField': 'string',
            'FileField': 'string',
            'FloatField': 'number',
            'ImageField': 'string',
            'IntegerField': 'number',
            'JSONField': 'any',
            'PositiveIntegerField': 'number',
            'SlugField': 'string',
            'TextField': 'string',
            'TimeField': 'string',
            'URLField': 'string',
            'UUIDField': 'string',
            'ForeignKey': 'number',
            'OneToOneField': 'number',
            'ManyToManyField': 'number[]'
        }
    
    def generate_interfaces(self) -> str:
        """
        Generate TypeScript interfaces for all models and serializers.
        
        Returns:
            TypeScript interface code as string
        """
        ts_code = [
            "// Generated TypeScript interfaces for Django models",
            "// This file was automatically generated - do not edit manually",
            "",
            "// Interface for API error responses",
            "export interface ApiError {",
            "  detail?: string;",
            "  message?: string;",
            "  [key: string]: any;",
            "}",
            ""
        ]
        
        # Process serializers first as they represent the actual API shapes
        for serializer_name, serializer_info in self.serializers.items():
            if not serializer_info.get('model'):
                continue
                
            # Find matching model info
            model_name = serializer_info.get('model')
            model_info = self._find_model_by_name(model_name)
            
            if not model_info:
                continue
                
            # Generate interface for this model
            short_name = serializer_name.split('.')[-1].replace('Serializer', '')
            interface_code = self._generate_model_interface(short_name, model_info, serializer_info)
            ts_code.append(interface_code)
            
            # Track that we've processed this model
            self.processed_models.add(model_name)
        
        # Process remaining models that don't have serializers
        for model_key, model_info in self.data_models.items():
            model_name = model_info.get('name')
            if model_name in self.processed_models:
                continue
                
            # Generate interface for this model
            interface_code = self._generate_model_interface(model_name, model_info)
            ts_code.append(interface_code)
            
            # Track that we've processed this model
            self.processed_models.add(model_name)
        
        return "\n".join(ts_code)
    
    def generate_api_services(self, use_react_query: bool = True) -> str:
        """
        Generate TypeScript API service functions.
        
        Args:
            use_react_query: Whether to use React Query hooks
            
        Returns:
            TypeScript API service code as string
        """
        # Start with imports
        ts_code = [
            "// Generated TypeScript API services for Django endpoints",
            "// This file was automatically generated - do not edit manually",
            ""
        ]
        
        # Add appropriate imports
        if use_react_query:
            ts_code.extend([
                "import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';",
                "import axios, { AxiosError } from 'axios';",
                ""
            ])
        else:
            ts_code.extend([
                "import axios from 'axios';",
                ""
            ])
        
        # Add common API client setup
        ts_code.extend([
            "// API client configuration",
            "const apiClient = axios.create({",
            f"  baseURL: '{self.base_url}',",
            "  headers: {",
            "    'Content-Type': 'application/json',",
            "  },",
            "});",
            "",
            "// Configure authentication interceptor",
            "apiClient.interceptors.request.use(config => {",
            "  const token = localStorage.getItem('authToken');",
            "  if (token) {",
            "    config.headers['Authorization'] = `Bearer ${token}`;",
            "  }",
            "  return config;",
            "});",
            ""
        ])
        
        # Group endpoints by resource (model)
        endpoints_by_resource = {}
        
        for endpoint in self.api_endpoints:
            model = endpoint.get('model')
            if not model:
                # Try to extract from path
                path = endpoint.get('path', '')
                segments = path.strip('/').split('/')
                if segments:
                    model = segments[0].title()
            
            if model:
                if model not in endpoints_by_resource:
                    endpoints_by_resource[model] = []
                endpoints_by_resource[model].append(endpoint)
        
        # Generate service functions for each resource
        for resource, endpoints in endpoints_by_resource.items():
            resource_name = self._normalize_resource_name(resource)
            interface_name = resource_name
            plural_name = self._pluralize(resource_name.lower())
            
            # Generate service functions or React Query hooks
            if use_react_query:
                service_code = self._generate_react_query_hooks(
                    resource_name, interface_name, plural_name, endpoints
                )
            else:
                service_code = self._generate_service_functions(
                    resource_name, interface_name, plural_name, endpoints
                )
            
            ts_code.append(service_code)
        
        return "\n".join(ts_code)
    
    def _find_model_by_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a model by its name, regardless of app prefix.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model info dictionary or None if not found
        """
        for key, info in self.data_models.items():
            if key.endswith('.' + model_name) or info.get('name') == model_name:
                return info
        return None
    
    def _generate_model_interface(self, 
                                  interface_name: str, 
                                  model_info: Dict[str, Any],
                                  serializer_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate TypeScript interface for a Django model.
        
        Args:
            interface_name: Name for the TypeScript interface
            model_info: Model information
            serializer_info: Optional serializer information
            
        Returns:
            TypeScript interface code
        """
        lines = []
        
        # Add JSDoc comment
        app_name = model_info.get('app_name', '')
        model_name = model_info.get('name', '')
        
        lines.append(f"/**")
        lines.append(f" * {interface_name} interface")
        lines.append(f" * Represents the {model_name} model from the {app_name} app")
        
        if serializer_info:
            serializer_name = serializer_info.get('name', '')
            lines.append(f" * Serialized by {serializer_name}")
            
        lines.append(f" */")
        lines.append(f"export interface {interface_name} {{")
        
        # Add properties
        for field in model_info.get('fields', []):
            field_name = field.get('name')
            field_type = field.get('field_type')
            options = field.get('options', {})
            
            # Skip fields that are explicitly excluded in serializer
            if serializer_info:
                # Skip if field is not in serializer fields and not auto-included
                serializer_fields = serializer_info.get('fields', [])
                if serializer_fields and field_name not in serializer_fields:
                    # Still include id fields as they're often implicit in serializers
                    if field_name != 'id' and not field_name.endswith('_id'):
                        continue
                
                # Skip if field is in serializer write_only fields
                if field_name in serializer_info.get('write_only_fields', []):
                    continue
            
            # Generate comment
            comment = []
            
            # Add nullable or default info
            if options.get('null', False):
                comment.append("nullable")
            if 'default' in options:
                comment.append(f"default: {options['default']}")
            if 'choices' in options:
                choices_str = self._format_choices(options['choices'])
                if choices_str:
                    comment.append(f"choices: {choices_str}")
            
            # Add comment if we have one
            if comment:
                lines.append(f"  // {', '.join(comment)}")
            
            # Map field type to TypeScript type
            ts_type = self._map_field_type(field_type, options)
            
            # Add optional marker if field is nullable
            optional = "?" if options.get('null', False) else ""
            
            lines.append(f"  {field_name}{optional}: {ts_type};")
        
        # Add relationships
        relationships = model_info.get('relationships', [])
        if relationships:
            if model_info.get('fields'):  # Add separator if we have fields
                lines.append("")
                lines.append("  // Relationships")
            
            for rel in relationships:
                field_name = rel.get('field_name')
                relation_type = rel.get('relation_type')
                related_model = rel.get('related_model', '').split('.')[-1]
                related_name = rel.get('related_name')
                
                # Map relationship type
                if relation_type == 'ManyToManyField':
                    ts_type = f"{related_model}[]"
                elif relation_type in ['ForeignKey', 'OneToOneField']:
                    ts_type = related_model
                else:
                    ts_type = 'any'
                
                # Add comment for related_name
                if related_name:
                    lines.append(f"  // related_name: {related_name}")
                
                lines.append(f"  {field_name}?: {ts_type};")
        
        lines.append("}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _map_field_type(self, field_type: str, options: Dict[str, Any]) -> str:
        """
        Map Django field type to TypeScript type.
        
        Args:
            field_type: Django field type
            options: Field options
            
        Returns:
            TypeScript type
        """
        ts_type = self.type_map.get(field_type, 'any')
        
        # Handle special cases
        if field_type == 'CharField' and options.get('choices'):
            # Create a string union type for choices
            choices = options.get('choices', [])
            if isinstance(choices, (list, tuple)) and all(isinstance(c, (list, tuple)) for c in choices):
                # Extract first item of each tuple (value)
                choice_values = [c[0] for c in choices if len(c) > 0]
                if all(isinstance(c, str) for c in choice_values):
                    choice_strings = [f"'{c}'" for c in choice_values]
                    return " | ".join(choice_strings)
        
        return ts_type
    
    def _format_choices(self, choices) -> str:
        """Format choices for comments"""
        if isinstance(choices, (list, tuple)):
            if all(isinstance(c, (list, tuple)) for c in choices):
                # Extract value/label pairs
                return ", ".join([f"{c[0]}={c[1]}" for c in choices if len(c) >= 2])
            else:
                return ", ".join([str(c) for c in choices])
        return str(choices)
    
    def _normalize_resource_name(self, name: str) -> str:
        """
        Normalize a resource name to a proper TypeScript interface name.
        
        Args:
            name: Resource name, possibly with dots or underscores
            
        Returns:
            Normalized resource name
        """
        # Take last part after dot
        if '.' in name:
            name = name.split('.')[-1]
        
        # Convert snake_case to PascalCase
        if '_' in name:
            name = ''.join([part.capitalize() for part in name.split('_')])
        
        # Ensure first character is uppercase
        return name[0].upper() + name[1:] if name else 'Resource'
    
    def _pluralize(self, word: str) -> str:
        """
        Simple pluralization for English words.
        
        Args:
            word: Word to pluralize
            
        Returns:
            Pluralized word
        """
        if word.endswith('s') or word.endswith('sh') or word.endswith('ch') or word.endswith('x'):
            return word + 'es'
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        else:
            return word + 's'
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize API path to a format compatible with axios.
        
        Args:
            path: API path with Django-style parameters
            
        Returns:
            Path with parameters in format compatible with JS template literals
        """
        # Replace Django path parameters with JS template literals
        # Example: /users/<id>/ becomes /users/${id}/
        normalized = re.sub(r'<(?:int:|str:|uuid:|slug:)?([^>]+)>', r'${id}', path)
        
        # Ensure path starts with /
        if not normalized.startswith('/'):
            normalized = '/' + normalized
            
        # Remove trailing slash
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
            
        return normalized
    
    def _generate_service_functions(self, 
                                   resource_name: str, 
                                   interface_name: str,
                                   plural_name: str,
                                   endpoints: List[Dict[str, Any]]) -> str:
        """
        Generate TypeScript service functions for a resource.
        
        Args:
            resource_name: Name of the resource
            interface_name: Name of the TypeScript interface
            plural_name: Pluralized resource name
            endpoints: List of API endpoints for this resource
            
        Returns:
            TypeScript service code
        """
        lines = [
            f"// API service functions for {resource_name}",
            f"export const {resource_name}Service = {{"
        ]
        
        # Track function names to avoid duplicates
        function_names = set()
        
        # Identify common endpoint types
        list_endpoint = None
        detail_endpoint = None
        create_endpoint = None
        
        for endpoint in endpoints:
            method = endpoint.get('method', '').upper()
            path = endpoint.get('path', '')
            
            if method == 'GET' and '<' not in path:
                list_endpoint = endpoint
            elif method == 'GET' and '<' in path:
                detail_endpoint = endpoint
            elif method == 'POST' and '<' not in path:
                create_endpoint = endpoint
                
        # Add standard functions first
        if list_endpoint:
            path = list_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  /**",
                f"   * Get all {plural_name}",
                f"   */",
                f"  getAll: async () => {{",
                f"    const response = await apiClient.get<{interface_name}[]>(`{normalized_path}`);",
                f"    return response.data;",
                f"  }},",
                f""
            ])
            function_names.add('getAll')
            
        if detail_endpoint:
            path = detail_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  /**",
                f"   * Get {resource_name} by ID",
                f"   */",
                f"  getById: async (id: number | string) => {{",
                f"    const response = await apiClient.get<{interface_name}>(`{normalized_path}`);",
                f"    return response.data;",
                f"  }},",
                f""
            ])
            function_names.add('getById')
        
        if create_endpoint:
            path = create_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  /**",
                f"   * Create a new {resource_name}",
                f"   */",
                f"  create: async (data: Partial<{interface_name}>) => {{",
                f"    const response = await apiClient.post<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
                f""
            ])
            function_names.add('create')
            
        # Add update and delete if we have a detail endpoint
        if detail_endpoint:
            path = detail_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            # Add update (PUT)
            lines.extend([
                f"  /**",
                f"   * Update a {resource_name}",
                f"   */",
                f"  update: async (id: number | string, data: Partial<{interface_name}>) => {{",
                f"    const response = await apiClient.put<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
                f""
            ])
            function_names.add('update')
            
            # Add partial update (PATCH)
            lines.extend([
                f"  /**",
                f"   * Partially update a {resource_name}",
                f"   */",
                f"  patch: async (id: number | string, data: Partial<{interface_name}>) => {{",
                f"    const response = await apiClient.patch<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
                f""
            ])
            function_names.add('patch')
            
            # Add delete
            lines.extend([
                f"  /**",
                f"   * Delete a {resource_name}",
                f"   */",
                f"  delete: async (id: number | string) => {{",
                f"    await apiClient.delete(`{normalized_path}`);",
                f"  }},",
                f""
            ])
            function_names.add('delete')
            
        # Add custom endpoints
        for endpoint in endpoints:
            method = endpoint.get('method', '').upper()
            path = endpoint.get('path', '')
            name = endpoint.get('name', '')
            
            # Skip if already covered by standard methods
            if ((method == 'GET' and '<' not in path and 'getAll' in function_names) or
                (method == 'GET' and '<' in path and 'getById' in function_names) or
                (method == 'POST' and '<' not in path and 'create' in function_names) or
                (method == 'PUT' and '<' in path and 'update' in function_names) or
                (method == 'PATCH' and '<' in path and 'patch' in function_names) or
                (method == 'DELETE' and '<' in path and 'delete' in function_names)):
                continue
            
            # Generate a unique function name
            function_base_name = name if name else self._path_to_function_name(path, method)
            function_name = function_base_name
            
            # Ensure function name is unique
            counter = 1
            while function_name in function_names:
                function_name = f"{function_base_name}{counter}"
                counter += 1
                
            function_names.add(function_name)
            
            # Normalize path
            normalized_path = self._normalize_path(path)
            
            # Generate function based on HTTP method
            has_id = '<' in path
            return_type = f"{interface_name}" if method in ['GET', 'POST', 'PUT', 'PATCH'] else "void"
            return_array = method == 'GET' and not has_id
            if return_array:
                return_type = f"{interface_name}[]"
            
            if method == 'GET':
                if has_id:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async (id: number | string) => {{",
                        f"    const response = await apiClient.get<{return_type}>(`{normalized_path}`);",
                        f"    return response.data;",
                        f"  }},",
                        f""
                    ])
                else:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async () => {{",
                        f"    const response = await apiClient.get<{return_type}>(`{normalized_path}`);",
                        f"    return response.data;",
                        f"  }},",
                        f""
                    ])
            elif method in ['POST', 'PUT', 'PATCH']:
                if has_id:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async (id: number | string, data: Partial<{interface_name}>) => {{",
                        f"    const response = await apiClient.{method.lower()}<{return_type}>(`{normalized_path}`, data);",
                        f"    return response.data;",
                        f"  }},",
                        f""
                    ])
                else:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async (data: Partial<{interface_name}>) => {{",
                        f"    const response = await apiClient.{method.lower()}<{return_type}>(`{normalized_path}`, data);",
                        f"    return response.data;",
                        f"  }},",
                        f""
                    ])
            elif method == 'DELETE':
                if has_id:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async (id: number | string) => {{",
                        f"    await apiClient.delete(`{normalized_path}`);",
                        f"  }},",
                        f""
                    ])
                else:
                    lines.extend([
                        f"  /**",
                        f"   * Custom endpoint: {path} ({method})",
                        f"   */",
                        f"  {function_name}: async () => {{",
                        f"    await apiClient.delete(`{normalized_path}`);",
                        f"  }},",
                        f""
                    ])
        
        # Close service object
        lines.append("};")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_react_query_hooks(self, 
                                   resource_name: str, 
                                   interface_name: str,
                                   plural_name: str,
                                   endpoints: List[Dict[str, Any]]) -> str:
        """
        Generate React Query hooks for a resource.
        
        Args:
            resource_name: Name of the resource
            interface_name: Name of the TypeScript interface
            plural_name: Pluralized resource name
            endpoints: List of API endpoints for this resource
            
        Returns:
            TypeScript React Query hook code
        """
        lines = [
            f"// React Query hooks for {resource_name}",
            f"// Query keys",
            f"export const {resource_name}Keys = {{",
            f"  all: ['{resource_name}'] as const,",
            f"  lists: () => [...{resource_name}Keys.all, 'list'] as const,",
            f"  list: (filters: any) => [...{resource_name}Keys.lists(), {{ ...filters }}] as const,",
            f"  details: () => [...{resource_name}Keys.all, 'detail'] as const,",
            f"  detail: (id: number | string) => [...{resource_name}Keys.details(), id] as const,",
            f"}};",
            f""
        ]
        
        # Track function names to avoid duplicates
        function_names = set()
        
        # Identify common endpoint types
        list_endpoint = None
        detail_endpoint = None
        create_endpoint = None
        
        for endpoint in endpoints:
            method = endpoint.get('method', '').upper()
            path = endpoint.get('path', '')
            
            if method == 'GET' and '<' not in path:
                list_endpoint = endpoint
            elif method == 'GET' and '<' in path:
                detail_endpoint = endpoint
            elif method == 'POST' and '<' not in path:
                create_endpoint = endpoint
                
        # Add service object with base API functions
        lines.extend([
            f"// Base API functions",
            f"const {resource_name}Service = {{"
        ])
        
        if list_endpoint:
            path = list_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  getAll: async (): Promise<{interface_name}[]> => {{",
                f"    const response = await apiClient.get<{interface_name}[]>(`{normalized_path}`);",
                f"    return response.data;",
                f"  }},",
            ])
            
        if detail_endpoint:
            path = detail_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  getById: async (id: number | string): Promise<{interface_name}> => {{",
                f"    const response = await apiClient.get<{interface_name}>(`{normalized_path}`);",
                f"    return response.data;",
                f"  }},",
            ])
        
        if create_endpoint:
            path = create_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            lines.extend([
                f"  create: async (data: Partial<{interface_name}>): Promise<{interface_name}> => {{",
                f"    const response = await apiClient.post<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
            ])
            
        # Add update and delete if we have a detail endpoint
        if detail_endpoint:
            path = detail_endpoint.get('path', '')
            normalized_path = self._normalize_path(path)
            
            # Add update (PUT)
            lines.extend([
                f"  update: async (id: number | string, data: Partial<{interface_name}>): Promise<{interface_name}> => {{",
                f"    const response = await apiClient.put<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
            ])
            
            # Add partial update (PATCH)
            lines.extend([
                f"  patch: async (id: number | string, data: Partial<{interface_name}>): Promise<{interface_name}> => {{",
                f"    const response = await apiClient.patch<{interface_name}>(`{normalized_path}`, data);",
                f"    return response.data;",
                f"  }},",
            ])
            
            # Add delete
            lines.extend([
                f"  delete: async (id: number | string): Promise<void> => {{",
                f"    await apiClient.delete(`{normalized_path}`);",
                f"  }},",
            ])
        
        lines.extend([
            f"}};",
            f""
        ])
        
        # Add React Query hooks
        if list_endpoint:
            lines.extend([
                f"/**",
                f" * Hook to fetch all {plural_name}",
                f" */",
                f"export function useGet{resource_name}s(options?: UseQueryOptions<{interface_name}[], AxiosError<ApiError>>) {{",
                f"  return useQuery<{interface_name}[], AxiosError<ApiError>>(",
                f"    {resource_name}Keys.lists(),",
                f"    () => {resource_name}Service.getAll(),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('useGetAll')
            
        if detail_endpoint:
            lines.extend([
                f"/**",
                f" * Hook to fetch a {resource_name} by ID",
                f" */",
                f"export function use{resource_name}(id: number | string, options?: UseQueryOptions<{interface_name}, AxiosError<ApiError>>) {{",
                f"  return useQuery<{interface_name}, AxiosError<ApiError>>(",
                f"    {resource_name}Keys.detail(id),",
                f"    () => {resource_name}Service.getById(id),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('useGetById')
        
        if create_endpoint:
            lines.extend([
                f"/**",
                f" * Hook to create a {resource_name}",
                f" */",
                f"export function useCreate{resource_name}(options?: UseMutationOptions<{interface_name}, AxiosError<ApiError>, Partial<{interface_name}>>) {{",
                f"  return useMutation<{interface_name}, AxiosError<ApiError>, Partial<{interface_name}>>(",
                f"    (data) => {resource_name}Service.create(data),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('useCreate')
            
        # Add update and delete hooks if we have a detail endpoint
        if detail_endpoint:
            # Update hook
            lines.extend([
                f"/**",
                f" * Hook to update a {resource_name}",
                f" */",
                f"export function useUpdate{resource_name}(options?: UseMutationOptions<{interface_name}, AxiosError<ApiError>, {{ id: number | string; data: Partial<{interface_name}> }}>) {{",
                f"  return useMutation<{interface_name}, AxiosError<ApiError>, {{ id: number | string; data: Partial<{interface_name}> }}>(",
                f"    ({ id, data }) => {resource_name}Service.update(id, data),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('useUpdate')
            
            # Patch hook
            lines.extend([
                f"/**",
                f" * Hook to partially update a {resource_name}",
                f" */",
                f"export function usePatch{resource_name}(options?: UseMutationOptions<{interface_name}, AxiosError<ApiError>, {{ id: number | string; data: Partial<{interface_name}> }}>) {{",
                f"  return useMutation<{interface_name}, AxiosError<ApiError>, {{ id: number | string; data: Partial<{interface_name}> }}>(",
                f"    ({ id, data }) => {resource_name}Service.patch(id, data),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('usePatch')
            
            # Delete hook
            lines.extend([
                f"/**",
                f" * Hook to delete a {resource_name}",
                f" */",
                f"export function useDelete{resource_name}(options?: UseMutationOptions<void, AxiosError<ApiError>, number | string>) {{",
                f"  return useMutation<void, AxiosError<ApiError>, number | string>(",
                f"    (id) => {resource_name}Service.delete(id),",
                f"    options",
                f"  );",
                f"}}",
                f""
            ])
            function_names.add('useDelete')
        
        return "\n".join(lines)
    
    def _path_to_function_name(self, path: str, method: str) -> str:
        """Convert path and method to a function name"""
        # Extract relevant parts from path
        parts = [p for p in path.strip('/').split('/') if not p.startswith('<')]
        
        # Map method to prefix
        method_prefix = {
            'GET': 'get',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'patch',
            'DELETE': 'delete'
        }.get(method, method.lower())
        
        # Combine parts
        if parts:
            # Use first part as resource name
            resource = parts[0]
            # Capitalize remaining parts
            remaining = [p.capitalize() for p in parts[1:]]
            
            # Combine
            if remaining:
                return f"{method_prefix}{resource.capitalize()}{''.join(remaining)}"
            else:
                return f"{method_prefix}{resource.capitalize()}"
        else:
            return method_prefix


def generate_typescript(analysis_data: Dict[str, Any], 
                       include_react_query: bool = True, 
                       base_url: str = '/api') -> Dict[str, str]:
    """
    Generate TypeScript interfaces and API service functions.
    
    Args:
        analysis_data: Analysis data from backend analyzer
        include_react_query: Whether to include React Query hooks
        base_url: Base URL for API requests
        
    Returns:
        Dictionary with typescript_interfaces and typescript_services keys
    """
    try:
        # Extract necessary data
        frontend_data = analysis_data.get('frontend_data', {})
        api_endpoints = frontend_data.get('api_endpoints', [])
        data_models = frontend_data.get('data_models', {})
        serializers = frontend_data.get('serializers', {})
        
        # Get model_serializer_mapping
        model_serializer_mapping = analysis_data.get('backend_compatibility', {}).get('model_serializer_mapping', {})
        
        # Create generator
        generator = TypeScriptGenerator(
            api_endpoints, 
            data_models, 
            serializers, 
            model_serializer_mapping,
            base_url
        )
        
        # Generate interfaces
        interfaces_code = generator.generate_interfaces()
        
        # Generate services
        services_code = generator.generate_api_services(include_react_query)
        
        return {
            'typescript_interfaces': interfaces_code,
            'typescript_services': services_code
        }
    
    except Exception as e:
        logger.error(f"Error generating TypeScript code: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        
        # Return minimal code
        return {
            'typescript_interfaces': "// Error generating TypeScript interfaces\nexport interface ApiError { detail?: string; }\n",
            'typescript_services': "// Error generating TypeScript services\nimport axios from 'axios';\nconst apiClient = axios.create({ baseURL: '/api' });\n"
        } 