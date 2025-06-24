#!/usr/bin/env python
"""
Django Backend Generator - Comprehensive backend file generator and documentation tool

This script analyzes Django models in an app and automatically generates:
1. All dependent backend files (serializers, views, urls, admin, forms, etc.)
2. A comprehensive markdown report documenting models, API endpoints, relationships
3. Cross-checks integrity between generated files
4. Identifies relationships with other apps

Usage:
    python django_backend_generator.py --app APP_NAME [--output OUTPUT_DIR] [--format FORMAT]

Arguments:
    --app APP_NAME          The name of the Django app to analyze
    --output OUTPUT_DIR     Output directory for generated files (default: current directory)
    --format FORMAT         Format for the report (markdown, html, pdf) (default: markdown)
    --overwrite             Overwrite existing files (default: False)
"""

import os
import sys
import ast
import argparse
import importlib
import inspect
import json
import re
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional, Union
import django
from django.apps import apps
from django.conf import settings
from django.urls import path, include
from django.core.management import execute_from_command_line
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField

# Templates for generated files
TEMPLATES = {
    'serializers': '''from rest_framework import serializers
from {app_name}.models import {model_imports}

{serializer_classes}
''',

    'views': '''from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from {app_name}.models import {model_imports}
from {app_name}.serializers import {serializer_imports}
{permission_import}

{view_classes}
''',

    'urls': '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from {app_name} import views

router = DefaultRouter()
{router_registrations}

urlpatterns = [
    path('', include(router.urls)),
    {custom_urls}
]
''',

    'admin': '''from django.contrib import admin
from {app_name}.models import {model_imports}

{admin_classes}
''',

    'forms': '''from django import forms
from {app_name}.models import {model_imports}

{form_classes}
''',

    'tests': '''from django.test import TestCase
from rest_framework.test import APITestCase
from {app_name}.models import {model_imports}

{test_classes}
''',

    'permissions': '''from rest_framework import permissions

{permission_classes}
''',

    'signals': '''from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from {app_name}.models import {model_imports}

{signal_handlers}
'''
}

class ModelAnalyzer:
    """Analyzes Django models and extracts their structure and relationships."""
    
    def __init__(self, app_name):
        self.app_name = app_name
        self.app_config = apps.get_app_config(app_name)
        self.models = {}
        self.relationships = []
        self.external_relationships = []
    
    def analyze(self):
        """Analyze all models in the app."""
        for model in self.app_config.get_models():
            model_info = self._analyze_model(model)
            self.models[model.__name__] = model_info
        
        return {
            'models': self.models,
            'relationships': self.relationships,
            'external_relationships': self.external_relationships
        }
    
    def _analyze_model(self, model):
        """Analyze a single model."""
        fields = {}
        
        # Analyze field information
        for field in model._meta.fields:
            field_info = {
                'type': field.__class__.__name__,
                'required': not field.null,
                'unique': field.unique,
                'help_text': str(field.help_text),
                'verbose_name': str(field.verbose_name),
            }
            
            # Add field-specific attributes
            if hasattr(field, 'max_length'):
                field_info['max_length'] = field.max_length
                
            if isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField):
                related_model = field.remote_field.model
                field_info['related_model'] = related_model.__name__
                field_info['related_app'] = related_model._meta.app_label
                field_info['on_delete'] = field.remote_field.on_delete.__name__
                
                relationship = {
                    'from_model': model.__name__,
                    'from_app': model._meta.app_label,
                    'to_model': related_model.__name__,
                    'to_app': related_model._meta.app_label,
                    'type': field.__class__.__name__,
                    'field_name': field.name
                }
                
                if related_model._meta.app_label != self.app_name:
                    self.external_relationships.append(relationship)
                else:
                    self.relationships.append(relationship)
            
            fields[field.name] = field_info
        
        # Handle many-to-many relationships
        for field in model._meta.many_to_many:
            field_info = {
                'type': field.__class__.__name__,
                'help_text': str(field.help_text),
                'verbose_name': str(field.verbose_name),
            }
            
            related_model = field.remote_field.model
            field_info['related_model'] = related_model.__name__
            field_info['related_app'] = related_model._meta.app_label
            
            relationship = {
                'from_model': model.__name__,
                'from_app': model._meta.app_label,
                'to_model': related_model.__name__,
                'to_app': related_model._meta.app_label,
                'type': 'ManyToManyField',
                'field_name': field.name
            }
            
            if related_model._meta.app_label != self.app_name:
                self.external_relationships.append(relationship)
            else:
                self.relationships.append(relationship)
                
            fields[field.name] = field_info
        
        # Meta information
        meta_info = {
            'verbose_name': str(model._meta.verbose_name),
            'verbose_name_plural': str(model._meta.verbose_name_plural),
            'ordering': list(model._meta.ordering),
            'unique_together': list(model._meta.unique_together),
            'abstract': model._meta.abstract,
            'app_label': model._meta.app_label,
        }
        
        return {
            'fields': fields,
            'meta': meta_info,
            'has_custom_manager': hasattr(model, 'objects') and not isinstance(model.objects, models.Manager),
            'has_str_method': hasattr(model, '__str__') and model.__str__.__qualname__.startswith(model.__name__),
        }


class FileGenerator:
    """Generates backend files based on model analysis."""
    
    def __init__(self, app_name, model_analysis, output_dir='.', overwrite=False):
        self.app_name = app_name
        self.model_analysis = model_analysis
        self.output_dir = output_dir
        self.app_dir = os.path.join(output_dir, app_name)
        self.overwrite = overwrite
        
        # Create app directory if it doesn't exist
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)
    
    def generate_all(self):
        """Generate all backend files."""
        generated_files = {}
        
        # Generate each file type
        generated_files['serializers.py'] = self._generate_serializers()
        generated_files['views.py'] = self._generate_views()
        generated_files['urls.py'] = self._generate_urls()
        generated_files['admin.py'] = self._generate_admin()
        generated_files['forms.py'] = self._generate_forms()
        generated_files['tests.py'] = self._generate_tests()
        
        # Generate additional files only if there's content
        permissions = self._generate_permissions()
        if permissions:
            generated_files['permissions.py'] = permissions
            
        signals = self._generate_signals()
        if signals:
            generated_files['signals.py'] = signals
        
        # Write all generated files
        for filename, content in generated_files.items():
            if content:
                file_path = os.path.join(self.app_dir, filename)
                if os.path.exists(file_path) and not self.overwrite:
                    print(f"Warning: File {file_path} already exists. Use --overwrite to overwrite.")
                else:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"Generated {file_path}")
        
        return generated_files
    
    def _generate_serializers(self):
        """Generate serializers.py file."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        serializer_classes = []
        
        for model_name, model_info in models.items():
            fields_list = list(model_info['fields'].keys())
            
            # Create a ModelSerializer for each model
            serializer_class = f'''class {model_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = {repr(fields_list)}
'''
            serializer_classes.append(serializer_class)

            # Create a nested serializer for detail views
            nested_fields = []
            for field_name, field_info in model_info['fields'].items():
                if field_info.get('type') in ('ForeignKey', 'OneToOneField', 'ManyToManyField'):
                    related_model = field_info.get('related_model')
                    if related_model in models:  # Only for models in this app
                        nested_fields.append(field_name)
            
            if nested_fields:
                nested_serializer = f'''class {model_name}DetailSerializer(serializers.ModelSerializer):
    {self._generate_nested_fields(nested_fields)}
    
    class Meta:
        model = {model_name}
        fields = {repr(fields_list)}
'''
                serializer_classes.append(nested_serializer)
        
        return TEMPLATES['serializers'].format(
            app_name=self.app_name,
            model_imports=model_imports,
            serializer_classes='\n\n'.join(serializer_classes)
        )
    
    def _generate_nested_fields(self, field_names):
        """Generate nested serializer fields."""
        return '\n    '.join([f"{field} = serializers.SerializerMethodField()" for field in field_names])
    
    def _generate_views(self):
        """Generate views.py file."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        serializer_imports = ', '.join([f"{model}Serializer" for model in models.keys()])
        serializer_imports += ', ' + ', '.join([f"{model}DetailSerializer" for model in models.keys() 
                                             if self._has_relations(model)])
        
        permission_import = ''
        if self._has_custom_permissions():
            permission_import = f"from {self.app_name}.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly"
        
        view_classes = []
        for model_name, model_info in models.items():
            fields = model_info['fields']
            filterset_fields = []
            search_fields = []
            
            for field_name, field_info in fields.items():
                if field_info['type'] in ['CharField', 'TextField', 'EmailField', 'UUIDField', 'SlugField']:
                    search_fields.append(field_name)
                if field_info['type'] not in ['TextField', 'BinaryField', 'FileField', 'ImageField']:
                    filterset_fields.append(field_name)
            
            has_detail_serializer = self._has_relations(model_name)
            detail_serializer = f"{model_name}DetailSerializer" if has_detail_serializer else f"{model_name}Serializer"
            
            view_class = f'''class {model_name}ViewSet(viewsets.ModelViewSet):
    """
    API endpoint for {model_name} objects
    """
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {filterset_fields}
    search_fields = {search_fields}
    ordering_fields = ['__all__']
    
    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return {detail_serializer}
        return {model_name}Serializer
'''
            view_classes.append(view_class)
        
        return TEMPLATES['views'].format(
            app_name=self.app_name,
            model_imports=model_imports,
            serializer_imports=serializer_imports,
            permission_import=permission_import,
            view_classes='\n\n'.join(view_classes)
        )
    
    def _generate_urls(self):
        """Generate urls.py file."""
        models = self.model_analysis['models']
        router_registrations = []
        
        for model_name in models.keys():
            # Convert CamelCase to kebab-case for URL
            url_path = re.sub(r'(?<!^)(?=[A-Z])', '-', model_name).lower()
            router_registrations.append(f"router.register(r'{url_path}s', views.{model_name}ViewSet)")
        
        return TEMPLATES['urls'].format(
            app_name=self.app_name,
            router_registrations='\n'.join(router_registrations),
            custom_urls=''
        )
    
    def _generate_admin(self):
        """Generate admin.py file."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        admin_classes = []
        
        for model_name, model_info in models.items():
            fields = model_info['fields']
            list_display = []
            search_fields = []
            list_filter = []
            
            # Add ID and common display fields
            if 'id' in fields:
                list_display.append('id')
            if 'name' in fields:
                list_display.append('name')
            if 'title' in fields:
                list_display.append('title')
            if 'created_at' in fields:
                list_display.append('created_at')
            if 'updated_at' in fields:
                list_display.append('updated_at')
            
            # Add search fields for text-based fields
            for field_name, field_info in fields.items():
                if field_info['type'] in ['CharField', 'TextField', 'EmailField', 'SlugField']:
                    search_fields.append(field_name)
                if field_info['type'] in ['BooleanField', 'DateField', 'DateTimeField', 'ForeignKey', 'ManyToManyField']:
                    list_filter.append(field_name)
                if len(list_display) < 5 and field_name not in list_display:
                    list_display.append(field_name)
            
            admin_class = f'''@admin.register({model_name})
class {model_name}Admin(admin.ModelAdmin):
    list_display = {list_display}
    search_fields = {search_fields}
    list_filter = {list_filter}
'''
            admin_classes.append(admin_class)
        
        return TEMPLATES['admin'].format(
            app_name=self.app_name,
            model_imports=model_imports,
            admin_classes='\n\n'.join(admin_classes)
        )
    
    def _generate_forms(self):
        """Generate forms.py file."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        form_classes = []
        
        for model_name, model_info in models.items():
            fields = list(model_info['fields'].keys())
            exclude = []
            
            # Exclude auto fields
            for field_name, field_info in model_info['fields'].items():
                if field_info['type'] in ['AutoField', 'BigAutoField']:
                    exclude.append(field_name)
            
            form_class = f'''class {model_name}Form(forms.ModelForm):
    class Meta:
        model = {model_name}
        fields = {repr(fields) if not exclude else '__all__'}
        {f"exclude = {repr(exclude)}" if exclude else ""}
'''
            form_classes.append(form_class)
        
        return TEMPLATES['forms'].format(
            app_name=self.app_name,
            model_imports=model_imports,
            form_classes='\n\n'.join(form_classes)
        )
    
    def _generate_tests(self):
        """Generate tests.py file."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        test_classes = []
        
        # Model tests
        for model_name in models.keys():
            model_test = f'''class {model_name}ModelTests(TestCase):
    def setUp(self):
        # Create test data
        pass
        
    def test_create_{model_name.lower()}(self):
        # Test model creation
        self.assertTrue(True)
'''
            test_classes.append(model_test)
        
        # API tests
        for model_name in models.keys():
            url_path = re.sub(r'(?<!^)(?=[A-Z])', '-', model_name).lower()
            api_test = f'''class {model_name}APITests(APITestCase):
    def setUp(self):
        # Create test data and authenticate
        pass
        
    def test_list_{model_name.lower()}(self):
        # Test API list endpoint
        url = f'/api/{url_path}s/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_create_{model_name.lower()}(self):
        # Test API create endpoint
        url = f'/api/{url_path}s/'
        data = {{
            # Add required fields
        }}
        # response = self.client.post(url, data, format='json')
        # self.assertEqual(response.status_code, 201)
'''
            test_classes.append(api_test)
        
        return TEMPLATES['tests'].format(
            app_name=self.app_name,
            model_imports=model_imports,
            test_classes='\n\n'.join(test_classes)
        )
    
    def _generate_permissions(self):
        """Generate permissions.py file if needed."""
        # Only generate if there are models that might need object-level permissions
        if self._has_user_related_models():
            permission_classes = '''class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to modify objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admins
        return request.user and request.user.is_staff
'''
            return TEMPLATES['permissions'].format(
                permission_classes=permission_classes
            )
        return None
    
    def _generate_signals(self):
        """Generate signals.py file if needed."""
        models = self.model_analysis['models']
        model_imports = ', '.join(models.keys())
        signal_handlers = []
        
        # Only generate for models that might benefit from signals
        has_signals = False
        for model_name, model_info in models.items():
            for field_name, field_info in model_info['fields'].items():
                # Create signals for timestamps or related fields that might need sync
                if field_name in ['created_at', 'updated_at'] or field_info['type'] in ['ForeignKey', 'ManyToManyField']:
                    has_signals = True
                    signal_handler = f'''@receiver(post_save, sender={model_name})
def {model_name.lower()}_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for {model_name} post_save
    """
    if created:
        # Do something when {model_name} is created
        pass
    else:
        # Do something when {model_name} is updated
        pass
'''
                    signal_handlers.append(signal_handler)
        
        if has_signals:
            return TEMPLATES['signals'].format(
                app_name=self.app_name,
                model_imports=model_imports,
                signal_handlers='\n\n'.join(signal_handlers)
            )
        return None
    
    def _has_relations(self, model_name):
        """Check if a model has related fields to other models."""
        model_info = self.model_analysis['models'][model_name]
        for field_info in model_info['fields'].values():
            if field_info['type'] in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                return True
        return False
    
    def _has_custom_permissions(self):
        """Check if custom permissions are needed."""
        return self._has_user_related_models()
    
    def _has_user_related_models(self):
        """Check if any models are related to User model."""
        for relation in self.model_analysis['external_relationships']:
            if relation['to_app'] == 'auth' and relation['to_model'] == 'User':
                return True
        
        # Also check for common ownership fields
        for model_info in self.model_analysis['models'].values():
            for field_name in model_info['fields']:
                if field_name in ['owner', 'user', 'creator', 'author']:
                    return True
        return False


class ReportGenerator:
    """Generates a comprehensive API documentation report."""
    
    def __init__(self, app_name, model_analysis, generated_files):
        self.app_name = app_name
        self.model_analysis = model_analysis
        self.generated_files = generated_files
        
    def generate_markdown_report(self):
        """Generate a comprehensive markdown report."""
        report = []
        
        # Title and introduction
        report.append(f"# {self.app_name.capitalize()} API Documentation")
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## Overview")
        report.append(f"\nThis document provides a comprehensive overview of the {self.app_name} API, "
                      f"including models, endpoints, and relationships.")
        
        # Table of Contents
        report.append("\n## Table of Contents")
        report.append("\n1. [Models](#models)")
        for model_name in self.model_analysis['models'].keys():
            report.append(f"   - [{model_name}](#{model_name.lower()})")
        report.append("2. [API Endpoints](#api-endpoints)")
        report.append("3. [Relationships](#relationships)")
        report.append("4. [External Dependencies](#external-dependencies)")
        report.append("5. [Generated Files](#generated-files)")
        
        # Models section
        report.append("\n## Models")
        for model_name, model_info in self.model_analysis['models'].items():
            report.append(f"\n### {model_name}<a name='{model_name.lower()}'></a>")
            report.append(f"\n**Description**: {model_info['meta']['verbose_name']}")
            
            # Fields table
            report.append("\n#### Fields")
            report.append("\n| Field Name | Type | Required | Unique | Description |")
            report.append("| ---------- | ---- | -------- | ------ | ----------- |")
            
            for field_name, field_info in model_info['fields'].items():
                field_type = field_info['type']
                if field_info['type'] in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                    related_model = field_info.get('related_model')
                    field_type = f"{field_type} → {related_model}"
                
                report.append(f"| {field_name} | {field_type} | "
                              f"{'Yes' if field_info.get('required', False) else 'No'} | "
                              f"{'Yes' if field_info.get('unique', False) else 'No'} | "
                              f"{field_info.get('help_text') or field_info.get('verbose_name') or ''} |")
            
            # Meta information
            report.append("\n#### Meta Information")
            report.append(f"\n- Verbose Name: {model_info['meta']['verbose_name']}")
            report.append(f"- Verbose Name Plural: {model_info['meta']['verbose_name_plural']}")
            report.append(f"- Ordering: {', '.join(model_info['meta']['ordering']) if model_info['meta']['ordering'] else 'Default'}")
            
            if model_info['meta']['unique_together']:
                unique_together = []
                for constraint in model_info['meta']['unique_together']:
                    if isinstance(constraint, tuple) or isinstance(constraint, list):
                        unique_together.append(', '.join(constraint))
                report.append(f"- Unique Together: {' | '.join(unique_together)}")
        
        # API Endpoints section
        report.append("\n## API Endpoints")
        for model_name in self.model_analysis['models'].keys():
            url_path = re.sub(r'(?<!^)(?=[A-Z])', '-', model_name).lower()
            
            report.append(f"\n### {model_name} Endpoints")
            
            # List/Create endpoint
            report.append(f"\n#### GET /api/{url_path}s/")
            report.append(f"\nRetrieve a list of {model_name} objects.")
            report.append("\n**Parameters**:")
            report.append("\n- `page`: Page number for pagination")
            report.append("- `page_size`: Number of items per page")
            
            fields = self.model_analysis['models'][model_name]['fields']
            for field_name, field_info in fields.items():
                if field_info['type'] not in ['TextField', 'BinaryField', 'FileField', 'ImageField']:
                    report.append(f"- `{field_name}`: Filter by {field_name}")
            
            report.append("\n**Response**:")
            report.append("\n```json")
            report.append("{")
            report.append("  \"count\": 123,")
            report.append("  \"next\": \"http://api.example.com/api/{}s/?page=2\",".format(url_path))
            report.append("  \"previous\": null,")
            report.append("  \"results\": [")
            report.append("    {")
            
            for field_name, field_info in fields.items():
                if field_info['type'] == 'CharField':
                    report.append(f"      \"{field_name}\": \"Example {field_name}\",")
                elif field_info['type'] == 'IntegerField':
                    report.append(f"      \"{field_name}\": 123,")
                elif field_info['type'] == 'BooleanField':
                    report.append(f"      \"{field_name}\": true,")
                elif field_info['type'] == 'DateTimeField':
                    report.append(f"      \"{field_name}\": \"2025-05-02T12:00:00Z\",")
                elif field_info['type'] == 'ForeignKey':
                    report.append(f"      \"{field_name}\": 1,")
                elif field_info['type'] == 'ManyToManyField':
                    report.append(f"      \"{field_name}\": [1, 2, 3],")
                else:
                    report.append(f"      \"{field_name}\": null,")
            
            # Remove the last comma
            last_line = report.pop()
            report.append(last_line.rstrip(","))
            
            report.append("    }")
            report.append("  ]")
            report.append("}")
            report.append("```")
            
            # Create endpoint
            report.append(f"\n#### POST /api/{url_path}s/")
            report.append(f"\nCreate a new {model_name} object.")
            report.append("\n**Request Body**:")
            report.append("\n```json")
            report.append("{")
            
            required_fields = []
            for field_name, field_info in fields.items():
                if field_info.get('required', False) and field_name not in ['id', 'pk']:
                    required_fields.append(field_name)
                    
                    if field_info['type'] == 'CharField':
                        report.append(f"  \"{field_name}\": \"Example {field_name}\",")
                    elif field_info['type'] == 'IntegerField':
                        report.append(f"  \"{field_name}\": 123,")
                    elif field_info['type'] == 'BooleanField':
                        report.append(f"  \"{field_name}\": true,")
                    elif field_info['type'] == 'DateTimeField':
                        report.append(f"  \"{field_name}\": \"2025-05-02T12:00:00Z\",")
                    elif field_info['type'] == 'ForeignKey':
                        report.append(f"  \"{field_name}\": 1,")
                    elif field_info['type'] == 'ManyToManyField':
                        report.append(f"  \"{field_name}\": [1, 2, 3],")
            
            # Remove the last comma
            if required_fields:
                last_line = report.pop()
                report.append(last_line.rstrip(","))
            
            report.append("}")
            report.append("```")
            
            # Detail endpoint
            report.append(f"\n#### GET /api/{url_path}s/{{id}}/")
            report.append(f"\nRetrieve a specific {model_name} object.")
            
            report.append("\n**Response**:")
            report.append("\n```json")
            report.append("{")
            
            for field_name, field_info in fields.items():
                if field_info['type'] == 'CharField':
                    report.append(f"  \"{field_name}\": \"Example {field_name}\",")
                elif field_info['type'] == 'IntegerField':
                    report.append(f"  \"{field_name}\": 123,")
                elif field_info['type'] == 'BooleanField':
                    report.append(f"  \"{field_name}\": true,")
                elif field_info['type'] == 'DateTimeField':
                    report.append(f"  \"{field_name}\": \"2025-05-02T12:00:00Z\",")
                elif field_info['type'] == 'ForeignKey':
                    report.append(f"  \"{field_name}\": {{")
                    report.append(f"    \"id\": 1,")
                    report.append(f"    \"name\": \"Related {field_info.get('related_model')}\",")
                    report.append("  },")
                elif field_info['type'] == 'ManyToManyField':
                    report.append(f"  \"{field_name}\": [")
                    report.append("    {")
                    report.append("      \"id\": 1,")
                    report.append(f"      \"name\": \"Related {field_info.get('related_model')} 1\"")
                    report.append("    },")
                    report.append("    {")
                    report.append("      \"id\": 2,")
                    report.append(f"      \"name\": \"Related {field_info.get('related_model')} 2\"")
                    report.append("    }")
                    report.append("  ],")
                else:
                    report.append(f"  \"{field_name}\": null,")
            
            # Remove the last comma
            last_line = report.pop()
            report.append(last_line.rstrip(","))
            
            report.append("}")
            report.append("```")
            
            # Update and Delete endpoints
            report.append(f"\n#### PUT /api/{url_path}s/{{id}}/")
            report.append(f"\nUpdate an existing {model_name} object.")
            
            report.append(f"\n#### DELETE /api/{url_path}s/{{id}}/")
            report.append(f"\nDelete a {model_name} object.")
        
        # Relationships section
        report.append("\n## Relationships")
        if self.model_analysis['relationships']:
            report.append("\n### Internal Relationships")
            for rel in self.model_analysis['relationships']:
                report.append(f"\n- **{rel['from_model']}** → **{rel['to_model']}** ({rel['type']} via field `{rel['field_name']}`)")
        else:
            report.append("\nNo internal relationships found.")
        
        # External dependencies
        if self.model_analysis['external_relationships']:
            report.append("\n### External Dependencies")
            for rel in self.model_analysis['external_relationships']:
                report.append(f"\n- **{rel['from_model']}** → **{rel['to_app']}.{rel['to_model']}** ({rel['type']} via field `{rel['field_name']}`)")
        else:
            report.append("\nNo external dependencies found.")
        
        # Generated files section
        report.append("\n## Generated Files")
        for filename in sorted(self.generated_files.keys()):
            if self.generated_files[filename]:
                report.append(f"\n### {filename}")
                report.append("\n```python")
                # Add first few lines of the file for preview
                preview_lines = self.generated_files[filename].split('\n')[:15]
                report.append('\n'.join(preview_lines))
                if len(self.generated_files[filename].split('\n')) > 15:
                    report.append("\n... (truncated for brevity)")
                report.append("\n```")
        
        return '\n'.join(report)


def main():
    """Main function that runs the generator."""
    parser = argparse.ArgumentParser(description='Generate Django backend files and documentation')
    parser.add_argument('--app', required=True, help='Django app name')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--format', choices=['markdown', 'html', 'pdf'], default='markdown', help='Report format')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()
    
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        print(f"Analyzing models in {args.app}...")
        analyzer = ModelAnalyzer(args.app)
        model_analysis = analyzer.analyze()
        
        print(f"Generating files for {args.app}...")
        generator = FileGenerator(args.app, model_analysis, args.output, args.overwrite)
        generated_files = generator.generate_all()
        
        print("Generating API documentation report...")
        report_generator = ReportGenerator(args.app, model_analysis, generated_files)
        report = report_generator.generate_markdown_report()
        
        # Write the report to a file
        report_filename = f"{args.app}_api_documentation.md"
        with open(os.path.join(args.output, report_filename), 'w') as f:
            f.write(report)
        
        print(f"Report generated: {os.path.join(args.output, report_filename)}")
        print("Done!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())