"""
OpenAPI Schema Generator for Django backend analysis.

This module provides functionality to generate OpenAPI schema from 
Django REST Framework API endpoints.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Set, Tuple

logger = logging.getLogger('backend_analyzer')


class OpenAPIGenerator:
    """Generator for OpenAPI schema from Django REST Framework endpoints."""
    
    def __init__(self, 
                 api_endpoints: List[Dict[str, Any]], 
                 data_models: Dict[str, Any],
                 serializers: Dict[str, Any],
                 info: Dict[str, Any] = None):
        """
        Initialize the OpenAPI generator.
        
        Args:
            api_endpoints: List of API endpoints
            data_models: Dictionary of data models
            serializers: Dictionary of serializers
            info: OpenAPI info object
        """
        self.api_endpoints = api_endpoints
        self.data_models = data_models
        self.serializers = serializers
        self.info = info or {
            'title': 'Django Backend API',
            'version': '1.0.0',
            'description': 'API generated from Django backend analysis'
        }
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate OpenAPI schema.
        
        Returns:
            OpenAPI schema as dictionary
        """
        try:
            # Start with basic OpenAPI structure
            schema = {
                'openapi': '3.0.0',
                'info': self.info,
                'paths': {},
                'components': {
                    'schemas': {},
                    'securitySchemes': {
                        'bearerAuth': {
                            'type': 'http',
                            'scheme': 'bearer',
                            'bearerFormat': 'JWT'
                        }
                    }
                }
            }
            
            # Add paths
            self._add_paths(schema)
            
            # Add schemas
            self._add_schemas(schema)
            
            return schema
        
        except Exception as e:
            logger.error(f"Error generating OpenAPI schema: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'openapi': '3.0.0',
                'info': self.info,
                'paths': {},
                'components': {'schemas': {}}
            }
    
    def _add_paths(self, schema: Dict[str, Any]) -> None:
        """
        Add paths to OpenAPI schema.
        
        Args:
            schema: OpenAPI schema dictionary
        """
        # Track processed paths to avoid duplicates
        processed_paths = set()
        
        for endpoint in self.api_endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '').lower()
            
            if not path or not method:
                continue
            
            # Normalize path to OpenAPI format
            openapi_path = self._normalize_path(path)
            path_key = f"{openapi_path}:{method}"
            
            # Skip duplicates
            if path_key in processed_paths:
                continue
            
            processed_paths.add(path_key)
            
            # Add path if it doesn't exist
            if openapi_path not in schema['paths']:
                schema['paths'][openapi_path] = {}
            
            # Build operation object
            operation = {
                'summary': self._generate_summary(endpoint),
                'description': self._generate_description(endpoint),
                'tags': [self._extract_tag(endpoint)],
                'responses': self._generate_responses(endpoint),
            }
            
            # Add parameters for path parameters
            path_params = self._extract_path_parameters(openapi_path)
            if path_params:
                operation['parameters'] = path_params
            
            # Add request body for non-GET operations
            if method in ['post', 'put', 'patch']:
                operation['requestBody'] = self._generate_request_body(endpoint)
            
            # Add security if the endpoint has permissions
            if endpoint.get('permissions'):
                operation['security'] = [{'bearerAuth': []}]
            
            # Add operation to path
            schema['paths'][openapi_path][method] = operation
    
    def _add_schemas(self, schema: Dict[str, Any]) -> None:
        """
        Add schemas to OpenAPI schema.
        
        Args:
            schema: OpenAPI schema dictionary
        """
        # Process serializers first - they provide the actual API schemas
        for serializer_name, serializer_info in self.serializers.items():
            if not serializer_info.get('model'):
                continue
                
            # Create schema name (use just last part of serializer name)
            schema_name = serializer_name.split('.')[-1]
            
            # Find related model
            model_info = None
            model_name = serializer_info.get('model')
            
            for key, value in self.data_models.items():
                if key.endswith('.' + model_name) or value.get('name') == model_name:
                    model_info = value
                    break
            
            if not model_info:
                continue
            
            # Create schema properties from model fields
            properties = {}
            required = []
            
            # Process model fields
            for field in model_info.get('fields', []):
                field_name = field.get('name')
                field_type = field.get('field_type')
                options = field.get('options', {})
                
                # Skip if this field is not in serializer fields and not auto-included
                serializer_fields = serializer_info.get('fields', [])
                if serializer_fields and field_name not in serializer_fields:
                    # Some fields like 'id' might be automatically included
                    if field_name != 'id' and not field_name.endswith('_id'):
                        continue
                
                # Add to required if not nullable and no default
                if not options.get('null', False) and 'default' not in options:
                    # But don't include auto_fields (id, created_at, etc.) as required
                    if not (field_name == 'id' or 
                            field_name.endswith('_id') or 
                            field_name in ['created_at', 'updated_at']):
                        required.append(field_name)
                
                # Convert Django field type to OpenAPI type
                openapi_type = self._django_type_to_openapi(field_type, options)
                
                # Skip if can't map the type
                if not openapi_type:
                    continue
                
                # Add property
                properties[field_name] = openapi_type
            
            # Create schema object
            schema_obj = {
                'type': 'object',
                'properties': properties
            }
            
            if required:
                schema_obj['required'] = required
            
            # Add schema to components
            schema['components']['schemas'][schema_name] = schema_obj
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize Django URL path to OpenAPI path.
        
        Args:
            path: Django URL path
            
        Returns:
            OpenAPI compatible path
        """
        # Replace Django path parameters with OpenAPI parameters
        # Example: /users/<id>/ becomes /users/{id}/
        # Or: /users/<int:id>/ becomes /users/{id}/
        normalized = re.sub(r'<(?:int:|str:|uuid:|slug:)?([^>]+)>', r'{\1}', path)
        
        # Ensure path starts with /
        if not normalized.startswith('/'):
            normalized = '/' + normalized
            
        # Remove trailing slash
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
            
        return normalized
    
    def _generate_summary(self, endpoint: Dict[str, Any]) -> str:
        """
        Generate operation summary from endpoint.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Operation summary
        """
        method = endpoint.get('method', '').upper()
        path = endpoint.get('path', '')
        view = endpoint.get('view', '')
        name = endpoint.get('name', '')
        
        if name:
            return name.replace('_', ' ').title()
        elif view:
            # Generate from view name
            action_words = {
                'GET': 'Get',
                'POST': 'Create',
                'PUT': 'Update',
                'PATCH': 'Partial Update',
                'DELETE': 'Delete'
            }
            
            # Extract resource name from view
            resource = view.replace('View', '').replace('ViewSet', '')
            action = action_words.get(method, method)
            
            # Detect if it's a list or detail view
            if '<' in path:  # Path parameter indicates detail view
                return f"{action} {resource} Details"
            else:
                return f"{action} {resource} List"
        else:
            # Fallback
            return f"{method} {path}"
    
    def _generate_description(self, endpoint: Dict[str, Any]) -> str:
        """
        Generate operation description from endpoint.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Operation description
        """
        method = endpoint.get('method', '').upper()
        view = endpoint.get('view', '')
        model = endpoint.get('model', '')
        
        # Basic description template
        descriptions = {
            'GET': f"Retrieve {model or 'data'} information",
            'POST': f"Create a new {model or 'resource'}",
            'PUT': f"Replace {model or 'resource'} with new data",
            'PATCH': f"Update {model or 'resource'} fields",
            'DELETE': f"Delete {model or 'resource'}"
        }
        
        description = descriptions.get(method, f"{method} operation")
        
        # Add view name
        if view:
            description += f" using {view}"
            
        # Add permissions if available
        if endpoint.get('permissions'):
            description += "\n\nRequires authentication with permissions: "
            description += ", ".join(endpoint.get('permissions'))
            
        return description
    
    def _extract_tag(self, endpoint: Dict[str, Any]) -> str:
        """
        Extract tag for grouping operations.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Tag name
        """
        # Try to get tag from model or view
        model = endpoint.get('model', '')
        view = endpoint.get('view', '')
        
        if model:
            return model
        elif view:
            # Remove View/ViewSet suffix
            return re.sub(r'(View|ViewSet)$', '', view)
        else:
            # Fallback to the first path segment
            path = endpoint.get('path', '')
            segments = path.strip('/').split('/')
            if segments:
                return segments[0].title()
            return 'Default'
    
    def _generate_responses(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response objects for the operation.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Responses object
        """
        method = endpoint.get('method', '').upper()
        serializer = endpoint.get('serializer', '')
        
        # Basic responses
        responses = {
            '401': {
                'description': 'Unauthorized - Authentication credentials were not provided or are invalid'
            },
            '403': {
                'description': 'Forbidden - You do not have permission to perform this action'
            },
            '500': {
                'description': 'Internal Server Error'
            }
        }
        
        # Add method-specific responses
        if method == 'GET':
            responses['200'] = {
                'description': 'Successful response'
            }
            
            # Add schema if serializer is available
            if serializer:
                schema_ref = self._get_schema_ref(serializer)
                if schema_ref:
                    # Check if this is likely a list endpoint (no parameters in URL)
                    if '<' not in endpoint.get('path', ''):
                        responses['200']['content'] = {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': schema_ref
                                    }
                                }
                            }
                        }
                    else:
                        responses['200']['content'] = {
                            'application/json': {
                                'schema': {
                                    '$ref': schema_ref
                                }
                            }
                        }
            
            responses['404'] = {
                'description': 'Not Found - The specified resource was not found'
            }
            
        elif method == 'POST':
            responses['201'] = {
                'description': 'Created - Resource was created successfully'
            }
            
            # Add schema if serializer is available
            if serializer:
                schema_ref = self._get_schema_ref(serializer)
                if schema_ref:
                    responses['201']['content'] = {
                        'application/json': {
                            'schema': {
                                '$ref': schema_ref
                            }
                        }
                    }
            
            responses['400'] = {
                'description': 'Bad Request - The request data was invalid'
            }
            
        elif method in ['PUT', 'PATCH']:
            responses['200'] = {
                'description': 'OK - Resource was updated successfully'
            }
            
            # Add schema if serializer is available
            if serializer:
                schema_ref = self._get_schema_ref(serializer)
                if schema_ref:
                    responses['200']['content'] = {
                        'application/json': {
                            'schema': {
                                '$ref': schema_ref
                            }
                        }
                    }
            
            responses['400'] = {
                'description': 'Bad Request - The request data was invalid'
            }
            responses['404'] = {
                'description': 'Not Found - The specified resource was not found'
            }
            
        elif method == 'DELETE':
            responses['204'] = {
                'description': 'No Content - Resource was deleted successfully'
            }
            responses['404'] = {
                'description': 'Not Found - The specified resource was not found'
            }
        
        return responses
    
    def _generate_request_body(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate request body for POST, PUT, PATCH operations.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Request body object
        """
        serializer = endpoint.get('serializer', '')
        method = endpoint.get('method', '').upper()
        
        request_body = {
            'description': f'Data for {method} operation',
            'required': True,
            'content': {
                'application/json': {
                    'schema': {}
                }
            }
        }
        
        # Add schema if serializer is available
        if serializer:
            schema_ref = self._get_schema_ref(serializer)
            if schema_ref:
                request_body['content']['application/json']['schema'] = {
                    '$ref': schema_ref
                }
            else:
                # Fallback to generic object
                request_body['content']['application/json']['schema'] = {
                    'type': 'object'
                }
        else:
            # Fallback to generic object
            request_body['content']['application/json']['schema'] = {
                'type': 'object'
            }
        
        return request_body
    
    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """
        Extract path parameters from OpenAPI path.
        
        Args:
            path: OpenAPI path
            
        Returns:
            List of parameter objects
        """
        parameters = []
        
        # Find all {parameter} occurrences
        param_matches = re.findall(r'\{([^}]+)\}', path)
        
        for param in param_matches:
            # Determine parameter type
            param_type = 'string'
            if param in ['id', 'pk'] or param.endswith('_id'):
                param_type = 'integer'
            elif param in ['uuid']:
                param_type = 'string'
                
            # Create parameter object
            parameter = {
                'name': param,
                'in': 'path',
                'required': True,
                'description': f'The {param} of the resource',
                'schema': {
                    'type': param_type
                }
            }
            
            parameters.append(parameter)
        
        return parameters
    
    def _get_schema_ref(self, serializer: str) -> Optional[str]:
        """
        Get schema reference for a serializer.
        
        Args:
            serializer: Serializer name
            
        Returns:
            Schema reference or None if not found
        """
        # Extract serializer name without module
        serializer_name = serializer.split('.')[-1]
        
        # Check if the serializer exists in components
        if serializer_name:
            return f'#/components/schemas/{serializer_name}'
        
        return None
    
    def _django_type_to_openapi(self, 
                               field_type: str, 
                               options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert Django field type to OpenAPI type.
        
        Args:
            field_type: Django field type
            options: Field options
            
        Returns:
            OpenAPI type object or None if no mapping
        """
        # Common type mappings
        type_map = {
            'CharField': {'type': 'string'},
            'TextField': {'type': 'string'},
            'EmailField': {'type': 'string', 'format': 'email'},
            'URLField': {'type': 'string', 'format': 'uri'},
            'SlugField': {'type': 'string'},
            'FileField': {'type': 'string', 'format': 'binary'},
            'ImageField': {'type': 'string', 'format': 'binary'},
            'BooleanField': {'type': 'boolean'},
            'IntegerField': {'type': 'integer'},
            'PositiveIntegerField': {'type': 'integer', 'minimum': 0},
            'BigIntegerField': {'type': 'integer', 'format': 'int64'},
            'FloatField': {'type': 'number', 'format': 'float'},
            'DecimalField': {'type': 'number', 'format': 'double'},
            'DateField': {'type': 'string', 'format': 'date'},
            'DateTimeField': {'type': 'string', 'format': 'date-time'},
            'TimeField': {'type': 'string', 'format': 'time'},
            'DurationField': {'type': 'string'},
            'UUIDField': {'type': 'string', 'format': 'uuid'},
            'JSONField': {'type': 'object'},
            'AutoField': {'type': 'integer', 'readOnly': True},
            'BigAutoField': {'type': 'integer', 'format': 'int64', 'readOnly': True},
            'ForeignKey': {'type': 'integer'},
            'OneToOneField': {'type': 'integer'},
            'ManyToManyField': {'type': 'array', 'items': {'type': 'integer'}}
        }
        
        # Get base type
        openapi_type = type_map.get(field_type)
        
        if not openapi_type:
            return None
            
        # Make a copy to avoid modifying the template
        result = openapi_type.copy()
        
        # Add common field options
        if options.get('null', False):
            result['nullable'] = True
            
        if 'default' in options:
            result['default'] = options['default']
            
        if 'choices' in options:
            choices = options['choices']
            if isinstance(choices, (list, tuple)):
                # Extract choice values
                enum_values = []
                for choice in choices:
                    if isinstance(choice, (list, tuple)) and len(choice) >= 1:
                        enum_values.append(choice[0])
                    else:
                        enum_values.append(choice)
                        
                if enum_values:
                    result['enum'] = enum_values
            
        # Add field-specific options
        if field_type == 'CharField' and 'max_length' in options:
            result['maxLength'] = options['max_length']
            
        if field_type in ['IntegerField', 'PositiveIntegerField', 'BigIntegerField']:
            if 'min_value' in options:
                result['minimum'] = options['min_value']
            if 'max_value' in options:
                result['maximum'] = options['max_value']
                
        if field_type == 'DecimalField':
            if 'max_digits' in options:
                result['maximum'] = 10 ** options['max_digits'] - 1
            if 'decimal_places' in options:
                result['multipleOf'] = 10 ** -options['decimal_places']
        
        return result


def generate_openapi_schema(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate OpenAPI schema from analysis data.
    
    Args:
        analysis_data: Analysis data from backend analyzer
        
    Returns:
        OpenAPI schema
    """
    try:
        # Extract necessary data
        frontend_data = analysis_data.get('frontend_data', {})
        api_endpoints = frontend_data.get('api_endpoints', [])
        data_models = frontend_data.get('data_models', {})
        serializers = frontend_data.get('serializers', {})
        
        # Extract metadata
        metadata = analysis_data.get('metadata', {})
        info = {
            'title': 'Django Backend API',
            'version': metadata.get('django_version', '1.0.0'),
            'description': 'API documentation generated by Django Backend Analyzer'
        }
        
        # Create generator
        generator = OpenAPIGenerator(api_endpoints, data_models, serializers, info)
        
        # Generate schema
        return generator.generate()
    
    except Exception as e:
        logger.error(f"Error generating OpenAPI schema: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        
        # Return minimal schema
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'Django Backend API',
                'version': '1.0.0',
                'description': 'Error generating schema'
            },
            'paths': {},
            'components': {'schemas': {}}
        } 