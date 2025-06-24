"""
URL parser module for analyzing Django URL patterns.

This module provides tools to extract URL patterns from Django URLs modules
and map them to views.
"""

import ast
import os
import re
import posixpath
import logging
from typing import Dict, List, Optional, Any, Set, Tuple

from ..models import URLInfo, APIEndpoint

logger = logging.getLogger('backend_analyzer')


class URLPatternVisitor(ast.NodeVisitor):
    """Node visitor for extracting URL patterns from a urls.py file."""
    
    def __init__(self):
        self.url_patterns = []
        self.includes = []
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit an assignment node to check for urlpatterns variable."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'urlpatterns':
                if isinstance(node.value, ast.List):
                    for element in node.value.elts:
                        url_info = self._extract_url_from_node(element)
                        if url_info:
                            self.url_patterns.append(url_info)
                        
                        # Check for include statements
                        include_path = self._extract_include_from_node(element)
                        if include_path:
                            self.includes.append(include_path)
    
    def _extract_url_from_node(self, node: ast.Call) -> Optional[URLInfo]:
        """Extract URL info from a path(), re_path(), or url() node"""
        if not isinstance(node, ast.Call):
            return None
        
        # Check if it's a path/re_path/url function
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name not in ['path', 're_path', 'url']:
            return None
        
        # Extract pattern, view, and name
        pattern = None
        view = None
        name = None
        
        # Get positional arguments
        if len(node.args) >= 2:
            # First arg is the pattern
            pattern = self._get_constant_value(node.args[0])
            
            # Second arg is the view
            view_arg = node.args[1]
            if isinstance(view_arg, ast.Name):
                view = view_arg.id
            elif isinstance(view_arg, ast.Attribute):
                view = self._get_import_module_name(view_arg)
            elif isinstance(view_arg, ast.Call):
                if isinstance(view_arg.func, ast.Attribute) and view_arg.func.attr == 'as_view':
                    view = self._get_import_module_name(view_arg.func.value)
                else:
                    view = self._get_import_module_name(view_arg.func)
        
        # Get keyword arguments
        for keyword in node.keywords:
            if keyword.arg == 'name':
                name = self._get_constant_value(keyword.value)
        
        if pattern is not None and view:
            url_info = URLInfo(pattern=pattern, view=view, name=name)
            return url_info
        
        return None
    
    def _extract_include_from_node(self, node: ast.Call) -> Optional[str]:
        """Extract include path from an include() call"""
        if not isinstance(node, ast.Call):
            return None
        
        # Check if it's an include function
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name != 'include':
            return None
        
        # Extract include path
        if node.args:
            include_path = self._get_constant_value(node.args[0])
            return include_path
        
        return None
    
    def _get_constant_value(self, node: ast.expr) -> Any:
        """Extract value from a constant node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        return None
    
    def _get_import_module_name(self, node: ast.expr, default=None) -> str:
        """Extract module name from an import node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            module_parts = []
            current = node
            while isinstance(current, ast.Attribute):
                module_parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                module_parts.insert(0, current.id)
            return '.'.join(module_parts)
        return default


class DjangoURLParser:
    """Parser for Django URL patterns using AST."""
    
    def __init__(self, backend_path: str):
        self.backend_path = os.path.abspath(backend_path)
        
    def find_root_urls_path(self) -> Optional[str]:
        """Find the root urls.py file."""
        # Try to find the Django project's root directory
        # This is typically a directory with settings.py
        for root, dirs, files in os.walk(self.backend_path):
            if 'settings.py' in files:
                project_dir = os.path.basename(root)
                urls_path = os.path.join(root, 'urls.py')
                
                if os.path.exists(urls_path):
                    return urls_path
        
        return None
    
    def parse_urls_file(self, urls_path: str, app_name: str) -> Tuple[List[URLInfo], List[str]]:
        """Parse a urls.py file to extract URL patterns and includes."""
        with open(urls_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        visitor = URLPatternVisitor()
        visitor.visit(tree)
        
        return visitor.url_patterns, visitor.includes
    
    def extract_view_name_from_reference(self, view_ref: str) -> str:
        """Extract the view name from a view reference in urls.py."""
        # Handle common patterns like 'views.ViewName.as_view()'
        if '.as_view' in view_ref:
            view_ref = view_ref.replace('.as_view()', '').replace('.as_view', '')
        
        # Handle 'app_name.views.ViewName' pattern
        parts = view_ref.split('.')
        if len(parts) > 1:
            return parts[-1]
        
        return view_ref
    
    def is_class_based_view(self, view_ref: str, views_dict: Dict[str, Any]) -> bool:
        """Check if a view reference is likely to be a class-based view."""
        return '.as_view' in view_ref or any(view_ref.endswith(f".{v.name}") for v in views_dict.values())
    
    def normalize_path(self, path: str) -> str:
        """Normalize URL path by ensuring it starts with / and has consistent formatting."""
        # Ensure pattern starts with /
        if not path.startswith('/'):
            path = '/' + path
            
        # Use posixpath to normalize the URL (avoid double slashes)
        return posixpath.normpath(path)

    def _process_included_urls(self, include_path, app_name, url_parser):
        """Process URLs from an included module"""
        try:
            # Security check: Only process Django-related Python modules
            if not self._is_safe_import_path(include_path):
                logger.warning(f"Skipping potentially unsafe import: {include_path}")
                return
                
            # Convert dotted path to filesystem path
            module_path = include_path.replace('.', '/') + '.py'
            if not module_path.startswith('/'):
                module_path = os.path.join(self.backend_path, module_path)
            
            if os.path.exists(module_path):
                self._process_urls_file(module_path, app_name, url_parser)
            else:
                logger.warning(f"Could not find included URLs module: {include_path}")
        except Exception as e:
            logger.error(f"Error processing included URLs {include_path}: {str(e)}")
    
    def _is_safe_import_path(self, import_path):
        """
        Check if an import path is safe to dynamically import.
        
        This helps prevent arbitrary code execution via malicious imports.
        """
        # List of safe module prefixes (customize as needed)
        safe_prefixes = [
            'django.',
            'rest_framework.',
            # Add project-specific app names
        ]
        
        # Add apps from the project
        for app in os.listdir(self.backend_path):
            if os.path.isdir(os.path.join(self.backend_path, app)):
                safe_prefixes.append(f"{app}.")
                
        # Check if the import path starts with any safe prefix or is an app name
        if any(import_path.startswith(prefix) for prefix in safe_prefixes):
            return True
            
        # Check if it's a direct reference to an app
        if import_path in os.listdir(self.backend_path):
            return True
            
        # Check if path contains suspicious patterns (like os, sys, subprocess)
        suspicious_modules = ['os', 'sys', 'subprocess', 'eval', 'exec', '__']
        if any(module in import_path.split('.') for module in suspicious_modules):
            return False
            
        # Default to being cautious
        logger.warning(f"Import path not in whitelist: {import_path}")
        return False


class APIEndpointIdentifier:
    """Helper class to identify API endpoints from URL patterns and views."""
    
    def __init__(self, views_dict: Dict[str, Any]):
        self.views_dict = views_dict
        self.viewset_action_map = {
            'list': 'GET',
            'retrieve': 'GET',
            'create': 'POST',
            'update': 'PUT',
            'partial_update': 'PATCH',
            'destroy': 'DELETE'
        }
    
    def derive_endpoints_from_url(self, url_info: URLInfo) -> List[APIEndpoint]:
        """Derive API endpoints from a URLInfo and corresponding view."""
        endpoints = []
        
        view_name = self._extract_view_name(url_info.view)
        
        # Try to find the matching view
        view_full_name = None
        for key in self.views_dict.keys():
            if key.endswith('.' + view_name):
                view_full_name = key
                break
        
        if view_full_name:
            view_info = self.views_dict[view_full_name]
            
            # For ViewSet or ModelViewSet, create multiple endpoints
            if 'ViewSet' in view_info.view_type:
                for action, method in self.viewset_action_map.items():
                    # Construct appropriate path based on action
                    path = url_info.pattern
                    if action == 'list':
                        path = path.rstrip('/')
                    elif action == 'retrieve':
                        if not path.endswith('/'):
                            path += '/'
                        path += '<id>/'
                    elif action in ['update', 'partial_update', 'destroy']:
                        if not path.endswith('/'):
                            path += '/'
                        path += '<id>/'
                    
                    # Normalize the path
                    path = posixpath.normpath(path)
                    
                    endpoint = APIEndpoint(
                        path=path,
                        method=method,
                        view=view_info.name,
                        name=f"{url_info.name}_{action}" if url_info.name else None,
                        model=view_info.model,
                        serializer=view_info.serializer,
                        permissions=view_info.permissions
                    )
                    
                    endpoints.append(endpoint)
            
            # For regular views, use the methods defined in the view
            else:
                for method in (view_info.methods or ['GET']):
                    endpoint = APIEndpoint(
                        path=url_info.pattern,
                        method=method,
                        view=view_info.name,
                        name=url_info.name,
                        model=view_info.model,
                        serializer=view_info.serializer,
                        permissions=view_info.permissions
                    )
                    
                    endpoints.append(endpoint)
        
        # If view not found but URL exists, add a placeholder
        elif not view_full_name and not self._is_class_based_view(url_info.view):
            endpoint = APIEndpoint(
                path=url_info.pattern,
                method="GET",  # Default method
                view=url_info.view,
                name=url_info.name
            )
            
            endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_view_name(self, view_ref: str) -> str:
        """Extract the view name from a view reference."""
        # Handle common patterns like 'views.ViewName.as_view()'
        if '.as_view' in view_ref:
            view_ref = view_ref.replace('.as_view()', '').replace('.as_view', '')
        
        # Handle 'app_name.views.ViewName' pattern
        parts = view_ref.split('.')
        if len(parts) > 1:
            return parts[-1]
        
        return view_ref
    
    def _is_class_based_view(self, view_ref: str) -> bool:
        """Check if a view reference is likely to be a class-based view."""
        return '.as_view' in view_ref or any(view_ref.endswith(f".{v.name}") for v in self.views_dict.values()) 