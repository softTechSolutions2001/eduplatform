"""
AST parser module for analyzing Django Python files.

This module uses the AST NodeVisitor pattern to efficiently parse Python files
and extract relevant information about Django components.
"""

import ast
import os
import re
from typing import Dict, List, Optional, Any, Tuple, Set, Union

from ..models import (
    ModelField, ModelInfo, SerializerInfo, ViewInfo, Relationship
)

def get_constant_value(node):
    """Extract value from ast.Constant (Python 3.8+) or legacy nodes"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.List):
        return [get_constant_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(get_constant_value(elt) for elt in node.elts)
    elif isinstance(node, ast.Dict):
        keys = [get_constant_value(k) for k in node.keys]
        values = [get_constant_value(v) for v in node.values]
        return dict(zip(keys, values))
    else:
        return str(type(node).__name__)


def get_import_module_name(node, default=None):
    """Extract module name from an import node"""
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


class ModelVisitor(ast.NodeVisitor):
    """Node visitor for extracting information about Django models."""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.models: List[ModelInfo] = []
        self.current_model: Optional[ModelInfo] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition to check if it's a Django model."""
        if self._is_model_subclass(node):
            self.current_model = ModelInfo(
                name=node.name,
                app_name=self.app_name
            )
            
            # Visit all nodes in the class
            for item in node.body:
                self.visit(item)
            
            # Add the completed model to the list
            self.models.append(self.current_model)
        
        # Continue visiting other nodes
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit an assignment node to check for model field definitions."""
        if not self.current_model:
            return
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                field_name = target.id
                
                # Skip if it's not a field assignment
                if not isinstance(node.value, ast.Call):
                    continue
                
                field_type, options = self._extract_field_info(node.value)
                
                # Add the field to the model
                model_field = ModelField(
                    name=field_name,
                    field_type=field_type,
                    options=options
                )
                self.current_model.fields.append(model_field)
                
                # Check if it's a relationship field
                if field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                    related_model = options.get('to', '')
                    if not related_model:
                        # Try to extract from first arg
                        if isinstance(node.value, ast.Call) and node.value.args:
                            if hasattr(node.value.args[0], 's'):  # For Python < 3.8
                                related_model = node.value.args[0].s
                            elif hasattr(node.value.args[0], 'id'):
                                related_model = node.value.args[0].id
                            else:
                                related_model = get_constant_value(node.value.args[0])
                    
                    relationship = Relationship(
                        field_name=field_name,
                        relation_type=field_type,
                        related_model=related_model,
                        related_name=options.get('related_name', None)
                    )
                    self.current_model.relationships.append(relationship)
    
    def visit_ClassDef_Meta(self, node: ast.ClassDef) -> None:
        """Visit a Meta class definition in a model."""
        if not self.current_model or node.name != 'Meta':
            return
        
        for item in node.body:
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                meta_name = item.targets[0].id
                meta_value = get_constant_value(item.value)
                self.current_model.meta[meta_name] = meta_value
    
    def _is_model_subclass(self, node: ast.ClassDef) -> bool:
        """Check if a class is a subclass of models.Model or similar base classes"""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Model':
                return True
            elif isinstance(base, ast.Attribute):
                # Get full attribute chain
                attr_chain = []
                current = base
                while isinstance(current, ast.Attribute):
                    attr_chain.insert(0, current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    attr_chain.insert(0, current.id)
                
                # Check if last part is 'Model'
                if attr_chain and attr_chain[-1] == 'Model':
                    return True
                # Handle common model parent classes
                if base.attr in ['AbstractUser', 'AbstractBaseUser', 'Model']:
                    return True
        return False
    
    def _extract_field_info(self, node: ast.Call) -> Tuple[str, Dict[str, Any]]:
        """Extract field type and options from a field definition"""
        field_type = None
        options = {}
        
        # Get field type
        if isinstance(node.func, ast.Name):
            field_type = node.func.id
        elif isinstance(node.func, ast.Attribute):
            field_type = node.func.attr
        
        # Get field options
        for keyword in node.keywords:
            option_value = get_constant_value(keyword.value)
            options[keyword.arg] = option_value
        
        # For positional arguments (like ForeignKey('Model'))
        for i, arg in enumerate(node.args):
            if i == 0 and field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                # First arg for relationship fields is often the related model
                try:
                    model_name = get_constant_value(arg)
                    if isinstance(model_name, str):
                        options['to'] = model_name
                    elif hasattr(arg, 'id'):  # For model references like User
                        options['to'] = arg.id
                except:
                    pass
        
        return field_type or "Unknown", options


class SerializerVisitor(ast.NodeVisitor):
    """Node visitor for extracting information about DRF serializers."""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.serializers: List[SerializerInfo] = []
        self.current_serializer: Optional[SerializerInfo] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition to check if it's a DRF serializer."""
        if self._is_serializer_subclass(node):
            self.current_serializer = SerializerInfo(
                name=node.name,
            )
            
            # Extract Meta information
            for item in node.body:
                if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                    self.visit_ClassDef_Meta(item)
                else:
                    self.visit(item)
            
            # Add the completed serializer to the list
            self.serializers.append(self.current_serializer)
        
        # Continue visiting other nodes
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit an assignment node to check for serializer field definitions."""
        if not self.current_serializer:
            return
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                field_name = target.id
                
                # Skip if it's not a field assignment
                if not isinstance(node.value, ast.Call):
                    continue
                
                # Extract field type for special handling
                field_type = None
                if isinstance(node.value.func, ast.Name):
                    field_type = node.value.func.id
                elif isinstance(node.value.func, ast.Attribute):
                    field_type = node.value.func.attr
                
                # Handle SerializerMethodField
                if field_type == 'SerializerMethodField':
                    # Add to fields list if not already there
                    if field_name not in self.current_serializer.fields:
                        self.current_serializer.fields.append(field_name)
                    
                    # Try to find the method that provides the value
                    method_name = None
                    for keyword in node.value.keywords:
                        if keyword.arg == 'method_name':
                            method_name = get_constant_value(keyword.value)
                    
                    # If method_name not specified, use default pattern
                    if not method_name:
                        method_name = f"get_{field_name}"
                    
                    # Store in extra_kwargs for documentation
                    self.current_serializer.extra_kwargs[field_name] = {
                        'method_field': True,
                        'method_name': method_name
                    }
                
                # Handle nested serializers (e.g., field = NestedSerializer())
                elif field_type and field_type.endswith('Serializer'):
                    # Add to fields list if not already there
                    if field_name not in self.current_serializer.fields:
                        self.current_serializer.fields.append(field_name)
                    
                    # Store information about nested serializer
                    self.current_serializer.extra_kwargs[field_name] = {
                        'nested_serializer': field_type,
                        'many': self._is_many_specified(node.value)
                    }
    
    def visit_ClassDef_Meta(self, node: ast.ClassDef) -> None:
        """Visit a Meta class definition in a serializer."""
        for item in node.body:
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                meta_name = item.targets[0].id
                meta_value = get_constant_value(item.value)
                
                if meta_name == 'model':
                    # Model can be a string or a class reference
                    if isinstance(item.value, ast.Name):
                        self.current_serializer.model = item.value.id
                    elif meta_value:
                        self.current_serializer.model = meta_value
                
                elif meta_name == 'fields':
                    if meta_value == '__all__':
                        self.current_serializer.fields = ['__all__']
                    elif isinstance(meta_value, (list, tuple)):
                        self.current_serializer.fields = list(meta_value)
                
                elif meta_name == 'exclude':
                    self.current_serializer.meta['exclude'] = meta_value
                
                elif meta_name == 'read_only_fields':
                    self.current_serializer.read_only_fields = list(meta_value)
                
                elif meta_name == 'write_only_fields':
                    self.current_serializer.write_only_fields = list(meta_value)
                
                elif meta_name == 'extra_kwargs':
                    self.current_serializer.extra_kwargs.update(meta_value)
                
                else:
                    self.current_serializer.meta[meta_name] = meta_value
    
    def _is_serializer_subclass(self, node: ast.ClassDef) -> bool:
        """Check if a class is a subclass of a serializer"""
        for base in node.bases:
            # Direct serializer base class
            if isinstance(base, ast.Name) and base.id.endswith('Serializer'):
                return True
            
            # Attribute reference (like serializers.ModelSerializer)
            elif isinstance(base, ast.Attribute) and base.attr.endswith('Serializer'):
                return True
        
        return False
    
    def _is_many_specified(self, node: ast.Call) -> bool:
        """Check if many=True is specified in a nested serializer"""
        for keyword in node.keywords:
            if keyword.arg == 'many':
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    return True
                elif isinstance(keyword.value, ast.NameConstant) and keyword.value.value is True:
                    return True
        return False


class ViewVisitor(ast.NodeVisitor):
    """Node visitor for extracting information about Django views."""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.views: List[ViewInfo] = []
        self.current_view: Optional[ViewInfo] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition to check if it's a Django view."""
        # Determine view type from bases
        view_type, model, serializer = self._extract_view_type_and_model(node)
        
        if view_type:
            methods, permissions = self._extract_view_methods_and_permissions(node)
            self.current_view = ViewInfo(
                name=node.name,
                view_type=view_type,
                model=model,
                serializer=serializer,
                methods=methods,
                permissions=permissions
            )
            
            # Add the completed view to the list
            self.views.append(self.current_view)
        
        # Continue visiting other nodes
        self.generic_visit(node)
    
    def _extract_view_type_and_model(self, node: ast.ClassDef) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract view type, model, and serializer from a view class"""
        view_type = None
        model = None
        serializer = None
        
        # Check base classes to determine view type
        for base in node.bases:
            if isinstance(base, ast.Name):
                view_type = base.id
            elif isinstance(base, ast.Attribute):
                view_type = base.attr
        
        # Extract model and serializer from class variables
        for item in node.body:
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                var_name = item.targets[0].id
                
                if var_name == 'queryset' and isinstance(item.value, ast.Call):
                    # Extract model from queryset = Model.objects.all() or Model.objects.filter(...)
                    if isinstance(item.value.func, ast.Attribute) and item.value.func.attr in ['all', 'filter', 'exclude', 'get_queryset']:
                        if isinstance(item.value.func.value, ast.Attribute) and item.value.func.value.attr in ['objects', 'published', 'active']:
                            if isinstance(item.value.func.value.value, ast.Name):
                                model = item.value.func.value.value.id
                
                elif var_name == 'model' and isinstance(item.value, ast.Name):
                    # Extract model from model = ModelName
                    model = item.value.id
                
                elif var_name == 'serializer_class' and isinstance(item.value, ast.Name):
                    # Extract serializer from serializer_class = SerializerName
                    serializer = item.value.id
            
            # Check for get_serializer_class method
            elif isinstance(item, ast.FunctionDef) and item.name == 'get_serializer_class':
                # Try to extract serializer from return statement
                for sub_node in ast.walk(item):
                    if isinstance(sub_node, ast.Return) and isinstance(sub_node.value, ast.Name):
                        serializer = sub_node.value.id
                        break
        
        return view_type, model, serializer

    def _extract_view_methods_and_permissions(self, node: ast.ClassDef) -> Tuple[List[str], List[str]]:
        """Extract HTTP methods and permissions from a view class node"""
        methods = []
        permissions = []
        
        for item in node.body:
            # Extract methods defined in the class
            if isinstance(item, ast.FunctionDef):
                method_name = item.name.lower()
                if method_name in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    methods.append(method_name.upper())
            
            # Extract permissions from permission_classes
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                var_name = item.targets[0].id
                
                if var_name == 'permission_classes':
                    if isinstance(item.value, ast.List):
                        for element in item.value.elts:
                            if isinstance(element, ast.Name):
                                permissions.append(element.id)
                            elif isinstance(element, ast.Attribute):
                                permissions.append(element.attr)
            
            # Extract permissions from get_permissions method
            elif isinstance(item, ast.FunctionDef) and item.name == 'get_permissions':
                for sub_node in ast.walk(item):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name) and sub_node.func.id.endswith('Permission'):
                            permissions.append(sub_node.func.id)
                        elif isinstance(sub_node.func, ast.Attribute) and sub_node.func.attr.endswith('Permission'):
                            permissions.append(sub_node.func.attr)
        
        # Check for @action decorators
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check for decorators
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'action':
                        # Extract HTTP methods from the decorator
                        methods_arg = None
                        for keyword in decorator.keywords:
                            if keyword.arg == 'methods':
                                methods_arg = keyword.value
                        
                        if methods_arg and isinstance(methods_arg, ast.List):
                            for method_node in methods_arg.elts:
                                method_str = get_constant_value(method_node)
                                if isinstance(method_str, str):
                                    methods.append(method_str.upper())
        
        return methods, permissions


class FileAnalyzer:
    """Analyzes Python files for Django components."""
    
    def __init__(self, file_path: str, app_name: str, file_cache=None):
        """
        Initialize the file analyzer.
        
        Args:
            file_path: Path to the file to analyze
            app_name: Name of the Django app
            file_cache: Optional FileCacheManager for caching
        """
        self.file_path = file_path
        self.app_name = app_name
        self.file_cache = file_cache
        self._ast = None
    
    def read_file(self) -> str:
        """Read the file content."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_ast(self) -> ast.AST:
        """Parse the file into an AST."""
        if self._ast is not None:
            return self._ast
            
        # Check if we can use the cache
        if self.file_cache:
            # Create a cache key based on file path, mtime, and size
            import os
            file_stat = os.stat(self.file_path)
            cache_key = f"{self.file_path}:{file_stat.st_mtime}:{file_stat.st_size}"
            
            # Try to get from cache
            cached_ast = self.file_cache.get(cache_key)
            if cached_ast:
                self._ast = cached_ast
                return self._ast
        
        # Parse the file
        source_code = self.read_file()
        self._ast = ast.parse(source_code)
        
        # Store in cache if available
        if self.file_cache:
            self.file_cache.put(cache_key, self._ast)
            
        return self._ast
    
    def analyze_models(self) -> List[ModelInfo]:
        """Extract Django model information from the file."""
        tree = self.parse_ast()
        visitor = ModelVisitor(self.app_name)
        visitor.visit(tree)
        return visitor.models
    
    def analyze_serializers(self) -> List[SerializerInfo]:
        """Extract DRF serializer information from the file."""
        tree = self.parse_ast()
        visitor = SerializerVisitor(self.app_name)
        visitor.visit(tree)
        return visitor.serializers
    
    def analyze_views(self) -> List[ViewInfo]:
        """Extract Django view information from the file."""
        tree = self.parse_ast()
        visitor = ViewVisitor(self.app_name)
        visitor.visit(tree)
        return visitor.views 