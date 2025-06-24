"""
Main analyzer module for Django backend.

This module contains the main BackendAnalyzer class that orchestrates
the entire analysis process.
"""

import os
import sys
import re
import json
import logging
import importlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union

from .models import (
    ModelField, ModelInfo, SerializerInfo, ViewInfo, URLInfo, 
    APIEndpoint, CompatibilityIssue, Relationship
)
from .django_env import DjangoRefectionManager, import_safely
from .parsers.ast_parser import FileAnalyzer
from .parsers.url_parser import DjangoURLParser, APIEndpointIdentifier
from .utils import (
    setup_logging, FileCacheManager, ProgressTracker, 
    timed, parallel_process, truncate_text
)

logger = logging.getLogger('backend_analyzer')


class BackendAnalyzer:
    """Main analyzer class for Django backend"""

    def __init__(self, backend_path, verbose=False, exclude_apps=None, max_issues_to_show=100,
                 use_django_reflection=True, use_subprocess_isolation=True, subprocess_timeout=30, 
                 fail_on_error=False, output_openapi=False, output_typescript=False, 
                 config_file=None, log_file=None, plugins=None):
        """
        Initialize the backend analyzer.
        
        Args:
            backend_path: Path to the Django backend
            verbose: If True, enable verbose logging
            exclude_apps: List of app names to exclude from analysis
            max_issues_to_show: Maximum number of issues to include in report
            use_django_reflection: If True, use Django reflection for analysis
            use_subprocess_isolation: If True, use subprocess isolation for Django reflection
            subprocess_timeout: Timeout for subprocess in seconds
            fail_on_error: If True, exit with error code on critical issues
            output_openapi: If True, generate OpenAPI schema
            output_typescript: If True, generate TypeScript interfaces
            config_file: Path to config file
            log_file: Path to log file
            plugins: List of AnalyzerPlugin instances to extend functionality
        """
        self.backend_path = os.path.abspath(backend_path)
        self.verbose = verbose
        self.exclude_apps = set(exclude_apps or [])
        self.max_issues_to_show = max_issues_to_show
        self.use_django_reflection = use_django_reflection
        self.use_subprocess_isolation = use_subprocess_isolation
        self.subprocess_timeout = subprocess_timeout
        self.fail_on_error = fail_on_error
        self.output_openapi = output_openapi
        self.output_typescript = output_typescript
        self.config_file = config_file
        self.plugins = plugins or []
        
        # Setup logging
        setup_logging(verbose=verbose, log_file=log_file)
        
        # Initialize file cache
        self.file_cache = FileCacheManager(max_size=200)
        
        # Data structures to store analysis results
        self.apps = set()
        self.models = {}  # app_name.model_name -> ModelInfo
        self.serializers = {}  # app_name.serializer_name -> SerializerInfo
        self.views = {}  # app_name.view_name -> ViewInfo
        self.urls = {}  # app_name -> List[URLInfo]
        self.api_endpoints = []  # List of APIEndpoint objects
        self.issues = []  # List of CompatibilityIssue objects
        
        # Map to track relationships between different components
        self.model_to_serializers = defaultdict(list)
        self.serializer_to_views = defaultdict(list)
        self.view_to_urls = defaultdict(list)
        
        # Dictionary mapping viewset actions to HTTP methods
        self.viewset_action_map = {
            'list': 'GET',
            'retrieve': 'GET',
            'create': 'POST',
            'update': 'PUT',
            'partial_update': 'PATCH',
            'destroy': 'DELETE'
        }
        
        # Django integration state
        self.django_ready = False
        self.django_error = None
        
        # Django reflection manager
        if use_django_reflection:
            self.django_reflection = DjangoRefectionManager(
                backend_path=self.backend_path,
                use_isolation=use_subprocess_isolation,
                timeout=subprocess_timeout
            )
            self.django_ready = self.django_reflection.initialize()
            if self.django_ready:
                logger.success(f"Django environment successfully initialized")
            else:
                logger.warning(f"Django environment not initialized: {self.django_reflection.django_error}")
                logger.info("Falling back to static file analysis")
        else:
            self.django_reflection = None
        
        # Read config file if provided
        self.config = {}
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.json'):
                        self.config = json.load(f)
                    elif config_file.endswith(('.toml', '.tml')):
                        import toml
                        self.config = toml.load(f)
                    elif config_file.endswith(('.yaml', '.yml')):
                        import yaml
                        self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Error loading config file {config_file}: {str(e)}")
        
        # Initialize plugins
        self._initialize_plugins()
    
    def _initialize_plugins(self):
        """Initialize all plugins with the analyzer instance"""
        if not self.plugins:
            return
            
        logger.info(f"Initializing {len(self.plugins)} plugins")
        for plugin in self.plugins:
            try:
                plugin.initialize(self)
                logger.info(f"Initialized plugin: {plugin.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error initializing plugin {plugin.__class__.__name__}: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
    
    @timed()
    def analyze(self):
        """Run the full analysis"""
        logger.info("Starting full backend analysis...")
        
        try:
            # Basic project analysis
            self.find_django_apps()
            self.analyze_models()
            self.analyze_serializers()
            self.analyze_views()
            self.analyze_urls()
            self.identify_api_endpoints()
            self.analyze_permissions()
            self.analyze_settings()
            
            # Analyze authentication
            auth_data = self.analyze_authentication()
            
            # Detect issues and generate ER diagram
            self.detect_compatibility_issues()
            er_diagram = self.generate_er_diagram()
            
            # Prepare final report data
            analysis_data = {
                'frontend_data': {
                    'api_endpoints': [endpoint.to_dict() for endpoint in self.api_endpoints],
                    'data_models': {model_name: model.to_dict() for model_name, model in self.models.items()},
                    'serializers': {serializer_name: serializer.to_dict() for serializer_name, serializer in self.serializers.items()},
                    'er_diagram': er_diagram,
                    'authentication': auth_data
                },
                'backend_compatibility': {
                    'issues': [issue.to_dict() for issue in self.issues],
                    'model_serializer_mapping': dict(self.model_to_serializers),
                    'serializer_view_mapping': dict(self.serializer_to_views),
                    'view_url_mapping': dict(self.view_to_urls)
                },
                'metadata': {
                    'script_version': '2.0',
                    'timestamp': self._get_current_date(),
                    'django_version': getattr(self, 'django_version', 'Unknown'),
                    'drf_version': getattr(self, 'drf_version', 'Unknown'),
                    'django_reflection_used': self.django_ready,
                    'excluded_apps': list(self.exclude_apps)
                }
            }
            
            # Run plugin checks if any are available
            if self.plugins:
                logger.info(f"Running checks from {len(self.plugins)} plugins")
                for plugin in self.plugins:
                    try:
                        plugin_issues = plugin.check(analysis_data)
                        if plugin_issues:
                            plugin_name = plugin.__class__.__name__
                            logger.info(f"Plugin {plugin_name} found {len(plugin_issues)} issues")
                            
                            # Add issues from plugin
                            self.issues.extend(plugin_issues)
                            
                            # Update analysis data with new issues
                            analysis_data['backend_compatibility']['issues'] = [
                                issue.to_dict() for issue in self.issues
                            ]
                    except Exception as e:
                        logger.error(f"Error running plugin check: {str(e)}")
                        import traceback
                        logger.debug(traceback.format_exc())
            
            logger.success("Analysis completed successfully!")
            return analysis_data
        
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    @timed()
    def detect_compatibility_issues(self):
        """Detect compatibility issues between models, serializers, views, and URLs"""
        logger.info("Detecting compatibility issues...")
        
        # Create a progress tracker for issue detection
        tracker = ProgressTracker(total_steps=3, description="Detecting issues")
        tracker.start()
        
        # Check 1: Models referenced by serializers should exist
        tracker.update(1, "Checking serializer-model references")
        for serializer_name, serializer_info in self.serializers.items():
            if serializer_info.model:
                # Build possible model references
                found = False
                for model_key in self.models.keys():
                    if model_key.endswith('.' + serializer_info.model) or serializer_info.model == model_key.split('.')[-1]:
                        found = True
                        break
                
                if not found:
                    self.issues.append(CompatibilityIssue(
                        issue_type="serializer_model_mismatch",
                        description=f"Serializer {serializer_name} references model {serializer_info.model} which was not found",
                        severity="error"
                    ))
        
        # Check 2: Serializers referenced by views should exist
        tracker.update(1, "Checking view-serializer references")
        for view_name, view_info in self.views.items():
            if view_info.serializer:
                # Build possible serializer references
                found = False
                for serializer_key in self.serializers.keys():
                    if serializer_key.endswith('.' + view_info.serializer) or view_info.serializer == serializer_key.split('.')[-1]:
                        found = True
                        break
                
                if not found:
                    self.issues.append(CompatibilityIssue(
                        issue_type="view_serializer_mismatch",
                        description=f"View {view_name} references serializer {view_info.serializer} which was not found",
                        severity="error"
                    ))
        
        # Check 3: Views referenced by URLs should exist
        for app_name, url_list in self.urls.items():
            for url_info in url_list:
                view_name = self._extract_view_name_from_reference(url_info.view)
                
                # Skip function views, this analysis focuses on class-based views
                if self._is_class_based_view(url_info.view):
                    # Build possible view references
                    found = False
                    for view_key in self.views.keys():
                        if view_key.endswith('.' + view_name) or view_name == view_key.split('.')[-1]:
                            found = True
                            break
                    
                    if not found:
                        self.issues.append(CompatibilityIssue(
                            issue_type="url_view_mismatch",
                            description=f"URL {url_info.pattern} references view {view_name} which was not found",
                            severity="error"
                        ))
        
        # Other checks continue...
        tracker.finish(f"Found {len(self.issues)} compatibility issues")
        
        # Identify critical errors (any issue with severity="error")
        critical_errors = [issue for issue in self.issues if issue.severity == "error"]
        if critical_errors:
            logger.error(f"Found {len(critical_errors)} critical errors")
            
        return self.issues
    
    def _extract_view_name_from_reference(self, view_ref):
        """Extract the view name from a view reference in urls.py"""
        # Handle common patterns like 'views.ViewName.as_view()'
        if '.as_view' in view_ref:
            view_ref = view_ref.replace('.as_view()', '').replace('.as_view', '')
        
        # Handle 'app_name.views.ViewName' pattern
        parts = view_ref.split('.')
        if len(parts) > 1:
            return parts[-1]
        
        return view_ref
    
    def _is_class_based_view(self, view_ref):
        """Check if a view reference is likely to be a class-based view"""
        return '.as_view' in view_ref or any(view_ref.endswith(f".{v.name}") for v in self.views.values())
    
    @timed()
    def analyze_permissions(self):
        """Analyze permission classes"""
        logger.info("Analyzing permission classes...")
        
        permission_files = []
        for app_name in self.apps:
            permissions_path = os.path.join(self.backend_path, app_name, 'permissions.py')
            
            if os.path.exists(permissions_path):
                permission_files.append((app_name, permissions_path))
                logger.info(f"Found permissions.py in {app_name}")
        
        # If no specific permission files, look in views.py
        if not permission_files:
            logger.warning("No dedicated permission files found, using permissions from views")
            
            # Collect unique permissions
            unique_permissions = set()
            for view_info in self.views.values():
                unique_permissions.update(view_info.permissions)
            
            logger.info(f"Found {len(unique_permissions)} unique permission classes in views")
        
        return permission_files
    
    @timed()
    def analyze_settings(self):
        """Analyze Django settings.py for important configurations"""
        logger.info("Analyzing Django settings...")
        
        settings_data = {}
        
        # Find settings.py
        settings_path = None
        for root, dirs, files in os.walk(self.backend_path):
            if 'settings.py' in files:
                settings_path = os.path.join(root, 'settings.py')
                break
        
        if not settings_path:
            logger.error("settings.py not found")
            return settings_data
        
        try:
            # Read the file
            with open(settings_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Parse the AST tree
            import ast
            tree = ast.parse(file_content)
            
            # Function to extract values from AST nodes
            def get_constant_value(node):
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
            
            # Extract important settings
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    
                    # Check for important settings
                    if var_name in [
                        'INSTALLED_APPS', 'REST_FRAMEWORK', 'DATABASES', 
                        'MIDDLEWARE', 'CORS_ALLOWED_ORIGINS', 'CORS_ALLOW_ALL_ORIGINS',
                        'ALLOWED_HOSTS', 'DEBUG', 'STATIC_URL', 'MEDIA_URL',
                        'AUTHENTICATION_BACKENDS'
                    ]:
                        # Extract the value using our helper function
                        settings_data[var_name] = get_constant_value(node.value)
            
            logger.info(f"Found {len(settings_data)} important settings")
        
        except Exception as e:
            logger.error(f"Error analyzing settings: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        
        return settings_data
    
    @timed()
    def analyze_authentication(self):
        """Analyze authentication mechanism in the project"""
        logger.info("Analyzing authentication mechanisms...")
        
        auth_data = {
            'mechanisms': set(),
            'user_model': None,
            'custom_auth': False
        }
        
        try:
            # Check settings for authentication backends
            settings_data = self.analyze_settings()
            backends = settings_data.get('AUTHENTICATION_BACKENDS', [])
            
            if backends and isinstance(backends, list):
                for backend in backends:
                    if isinstance(backend, str):
                        if 'django.contrib.auth' in backend:
                            auth_data['mechanisms'].add('django_auth')
                        if 'allauth' in backend:
                            auth_data['mechanisms'].add('allauth')
                        if 'knox' in backend:
                            auth_data['mechanisms'].add('knox')
                        if 'rest_framework.authentication' in backend:
                            auth_data['mechanisms'].add('drf_auth')
                        if 'dj_rest_auth' in backend:
                            auth_data['mechanisms'].add('dj_rest_auth')
                        if 'oauth2' in backend or 'oauth' in backend:
                            auth_data['mechanisms'].add('oauth')
                        if 'jwt' in backend.lower():
                            auth_data['mechanisms'].add('jwt')
                        if 'social' in backend:
                            auth_data['mechanisms'].add('social_auth')
            
            # Check if settings has REST_FRAMEWORK with authentication classes
            rest_framework = settings_data.get('REST_FRAMEWORK', {})
            if isinstance(rest_framework, dict) and 'DEFAULT_AUTHENTICATION_CLASSES' in rest_framework:
                auth_classes = rest_framework['DEFAULT_AUTHENTICATION_CLASSES']
                if isinstance(auth_classes, list):
                    for auth_class in auth_classes:
                        if isinstance(auth_class, str):
                            if 'TokenAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_token')
                            if 'SessionAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_session')
                            if 'BasicAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_basic')
                            if 'JWTAuthentication' in auth_class or 'JWT' in auth_class:
                                auth_data['mechanisms'].add('jwt')
                            if 'KnoxAuthentication' in auth_class:
                                auth_data['mechanisms'].add('knox')
            
            # Check installed apps for authentication-related packages
            installed_apps = settings_data.get('INSTALLED_APPS', [])
            if isinstance(installed_apps, list):
                for app in installed_apps:
                    if isinstance(app, str):
                        if 'rest_framework.authtoken' in app:
                            auth_data['mechanisms'].add('drf_token')
                        if 'knox' in app:
                            auth_data['mechanisms'].add('knox')
                        if 'allauth' in app:
                            auth_data['mechanisms'].add('allauth')
                        if 'dj_rest_auth' in app:
                            auth_data['mechanisms'].add('dj_rest_auth')
                        if 'oauth2' in app or 'oauth' in app:
                            auth_data['mechanisms'].add('oauth')
                        if 'social' in app:
                            auth_data['mechanisms'].add('social_auth')
                        if 'jwt' in app.lower() or 'simplejwt' in app.lower() or 'rest_framework_simplejwt' in app:
                            auth_data['mechanisms'].add('jwt')
            
            # Find custom user models
            for app_name in self.apps:
                models_path = os.path.join(self.backend_path, app_name, 'models.py')
                
                if os.path.exists(models_path):
                    try:
                        with open(models_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        # Look for AbstractUser or AbstractBaseUser
                        if 'AbstractUser' in file_content or 'AbstractBaseUser' in file_content:
                            # Parse the AST tree
                            import ast
                            tree = ast.parse(file_content)
                            
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    for base in node.bases:
                                        base_name = None
                                        if isinstance(base, ast.Name):
                                            base_name = base.id
                                        elif isinstance(base, ast.Attribute):
                                            base_name = base.attr
                                        
                                        if base_name in ['AbstractUser', 'AbstractBaseUser']:
                                            auth_data['user_model'] = f"{app_name}.{node.name}"
                                            auth_data['custom_auth'] = True
                                            break
                    
                    except Exception as e:
                        logger.error(f"Error checking custom user model in {app_name}: {str(e)}")
            
            # If no custom user model found, assume default
            if not auth_data['user_model']:
                auth_data['user_model'] = "django.contrib.auth.models.User"
            
            # Convert set to list for better serialization
            auth_data['mechanisms'] = list(auth_data['mechanisms'])
            
            logger.info(f"Identified authentication mechanisms: {', '.join(auth_data['mechanisms'])}")
            if auth_data['custom_auth']:
                logger.info(f"Found custom user model: {auth_data['user_model']}")
        
        except Exception as e:
            logger.error(f"Error analyzing authentication: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        
        return auth_data
    
    @timed()
    def generate_er_diagram(self):
        """Generate entity-relationship diagram in text format"""
        logger.info("Generating entity-relationship diagram...")
        
        er_lines = ["# Entity-Relationship Diagram", ""]
        app_models = {}
        
        # Group models by app
        for model_key, model_info in self.models.items():
            if model_info.app_name not in app_models:
                app_models[model_info.app_name] = []
            
            app_models[model_info.app_name].append(model_info)
        
        # Generate diagram for each app
        for app_name, models in app_models.items():
            er_lines.append(f"## App: {app_name}")
            er_lines.append("```")
            
            # Add each model
            for model_info in models:
                er_lines.append(f"[{model_info.name}]")
                
                # Add fields
                for field in model_info.fields:
                    field_str = f"  {field.name}: {field.field_type}"
                    
                    # Add options if available
                    if field.options:
                        options_str = ", ".join(f"{k}={v}" for k, v in field.options.items())
                        if options_str:
                            field_str += f" ({options_str})"
                    
                    er_lines.append(field_str)
                
                er_lines.append("")
            
            # Add relationships
            er_lines.append("# Relationships")
            for model_info in models:
                for rel in model_info.relationships:
                    rel_type_symbol = {
                        'ForeignKey': '->',
                        'OneToOneField': '--',
                        'ManyToManyField': '<->'
                    }.get(rel.relation_type, '->')
                    
                    related_name = f" (as {rel.related_name})" if rel.related_name else ""
                    er_lines.append(f"[{model_info.name}] {rel_type_symbol} [{rel.related_model}] : {rel.field_name}{related_name}")
            
            er_lines.append("```")
            er_lines.append("")
        
        return "\n".join(er_lines)
    
    def _get_current_date(self):
        """Get current date in ISO format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @timed()
    def find_django_apps(self):
        """Find all Django apps in the backend directory"""
        logger.info("Searching for Django apps...")
        
        # Use progress tracker for visual feedback
        tracker = ProgressTracker(total_steps=100, description="Finding Django apps")
        tracker.start()
        
        # If Django is initialized, use apps registry
        if self.django_ready and self.django_reflection:
            try:
                apps_list = self.django_reflection.get_apps()
                tracker.update(50, "Processing apps from Django registry")
                
                for app in apps_list:
                    app_name = app["label"]
                    self.apps.add(app_name)
                    logger.success(f"Found Django app via registry: {app_name}")
                
                tracker.update(50, "Completed apps discovery")
            except Exception as e:
                logger.error(f"Error using Django app registry: {str(e)}")
                logger.warning("Falling back to file system search")
                # Continue with file system search
                self._find_apps_via_filesystem(tracker)
        else:
            # Use file system search if Django reflection isn't available
            self._find_apps_via_filesystem(tracker)
        
        # After finding all apps
        self.apps = {app for app in self.apps if app not in self.exclude_apps}
        tracker.finish(f"Found {len(self.apps)} Django apps")
        
        return self.apps
    
    def _find_apps_via_filesystem(self, tracker):
        """Find Django apps by searching the file system"""
        # Get a rough count of directories for progress tracking
        root_dirs = list(os.scandir(self.backend_path))
        total_dirs = len(root_dirs)
        step_size = max(1, total_dirs // 100)
        
        tracker.update(0, "Scanning filesystem")
        
        for i, entry in enumerate(root_dirs):
            if i % step_size == 0:
                progress = min(95, int((i / total_dirs) * 95))
                tracker.update(progress - tracker.completed_steps, f"Scanning {entry.name}")
            
            if entry.is_dir():
                # Check for apps.py which indicates a Django app
                apps_path = os.path.join(entry.path, 'apps.py')
                if os.path.exists(apps_path):
                    app_name = entry.name
                    self.apps.add(app_name)
                    logger.success(f"Found Django app: {app_name}")
                    continue
                
                # Check for models.py which also indicates a Django app
                models_path = os.path.join(entry.path, 'models.py')
                if os.path.exists(models_path):
                    app_name = entry.name
                    self.apps.add(app_name)
                    logger.success(f"Found Django app: {app_name}")
    
    @timed()
    def analyze_models(self):
        """Analyze models.py files in all Django apps"""
        logger.info("Analyzing Django models...")
        
        # Create a progress tracker
        tracker = ProgressTracker(
            total_steps=len(self.apps), 
            description="Analyzing models"
        )
        tracker.start()
        
        # If Django is initialized, use model registry
        if self.django_ready and self.django_reflection:
            try:
                models_dict = self.django_reflection.get_models()
                
                # Process models using file analysis for more detailed info
                for app_name in self.apps:
                    tracker.update(1, f"Processing {app_name}")
                    models_path = os.path.join(self.backend_path, app_name, 'models.py')
                    
                    if not os.path.exists(models_path):
                        models_dir = os.path.join(self.backend_path, app_name, 'models')
                        if os.path.isdir(models_dir) and os.path.exists(os.path.join(models_dir, '__init__.py')):
                            # Handle case where models are in a directory instead of a single file
                            logger.info(f"Found models directory for app: {app_name}")
                            for model_file in os.listdir(models_dir):
                                if model_file.endswith('.py') and model_file != '__init__.py':
                                    model_path = os.path.join(models_dir, model_file)
                                    self._analyze_model_file(model_path, app_name)
                        else:
                            logger.warning(f"No models.py found for app: {app_name}")
                        continue
                        
                    self._analyze_model_file(models_path, app_name)
                
                tracker.finish(f"Analyzed {len(self.models)} models")
                return self.models
            except Exception as e:
                logger.error(f"Error using Django model registry: {str(e)}")
                logger.warning("Falling back to static file analysis")
        
        # Traditional file analysis if Django reflection isn't available
        for app_name in self.apps:
            tracker.update(1, f"Processing {app_name}")
            models_path = os.path.join(self.backend_path, app_name, 'models.py')
            
            if not os.path.exists(models_path):
                models_dir = os.path.join(self.backend_path, app_name, 'models')
                if os.path.isdir(models_dir) and os.path.exists(os.path.join(models_dir, '__init__.py')):
                    # Handle case where models are in a directory instead of a single file
                    logger.info(f"Found models directory for app: {app_name}")
                    for model_file in os.listdir(models_dir):
                        if model_file.endswith('.py') and model_file != '__init__.py':
                            model_path = os.path.join(models_dir, model_file)
                            self._analyze_model_file(model_path, app_name)
                else:
                    logger.warning(f"No models.py found for app: {app_name}")
                continue
                
            self._analyze_model_file(models_path, app_name)
        
        tracker.finish(f"Analyzed {len(self.models)} models")
        return self.models
    
    def _analyze_model_file(self, models_path, app_name):
        """Analyze a models.py file to extract model information"""
        try:
            # Use the FileAnalyzer with AST NodeVisitor pattern
            analyzer = FileAnalyzer(models_path, app_name, file_cache=self.file_cache)
            models = analyzer.analyze_models()
            
            # Add the models to our collection
            for model in models:
                self.models[f"{app_name}.{model.name}"] = model
                logger.success(f"  Found model: {model.name} ({len(model.fields)} fields)")
        
        except Exception as e:
            logger.error(f"Error analyzing models in {app_name}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
    @timed()
    def analyze_serializers(self):
        """Analyze serializers.py files in all Django apps"""
        logger.info("Analyzing Django REST Framework serializers...")
        
        # Create a progress tracker
        tracker = ProgressTracker(
            total_steps=len(self.apps), 
            description="Analyzing serializers"
        )
        tracker.start()
        
        for app_name in self.apps:
            tracker.update(1, f"Processing {app_name}")
            serializers_path = os.path.join(self.backend_path, app_name, 'serializers.py')
            
            if not os.path.exists(serializers_path):
                logger.warning(f"No serializers.py found for app: {app_name}")
                continue
                
            logger.info(f"Processing serializers in: {app_name}")
            
            try:
                # Use the FileAnalyzer with AST NodeVisitor pattern
                analyzer = FileAnalyzer(serializers_path, app_name, file_cache=self.file_cache)
                serializers = analyzer.analyze_serializers()
                
                # Add the serializers to our collection
                for serializer in serializers:
                    self.serializers[f"{app_name}.{serializer.name}"] = serializer
                    logger.success(f"  Found serializer: {serializer.name} (model: {serializer.model or 'None'})")
                    
                    # Update model to serializer mapping if model is specified
                    if serializer.model:
                        # Look for matching model (could be in a different app)
                        model_key = None
                        for key in self.models.keys():
                            if key.endswith('.' + serializer.model):
                                model_key = key
                                break
                        
                        if model_key:
                            self.model_to_serializers[model_key].append(f"{app_name}.{serializer.name}")
            
            except Exception as e:
                logger.error(f"Error analyzing serializers in {app_name}: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
        
        tracker.finish(f"Analyzed {len(self.serializers)} serializers")
        return self.serializers
    
    @timed()
    def analyze_views(self):
        """Analyze views.py files in all Django apps"""
        logger.info("Analyzing Django views...")
        
        # Create a progress tracker
        tracker = ProgressTracker(
            total_steps=len(self.apps), 
            description="Analyzing views"
        )
        tracker.start()
        
        for app_name in self.apps:
            tracker.update(1, f"Processing {app_name}")
            views_path = os.path.join(self.backend_path, app_name, 'views.py')
            
            if not os.path.exists(views_path):
                views_dir = os.path.join(self.backend_path, app_name, 'views')
                if os.path.isdir(views_dir) and os.path.exists(os.path.join(views_dir, '__init__.py')):
                    # Handle case where views are in a directory instead of a single file
                    logger.info(f"Found views directory for app: {app_name}")
                    for view_file in os.listdir(views_dir):
                        if view_file.endswith('.py') and view_file != '__init__.py':
                            view_path = os.path.join(views_dir, view_file)
                            self._analyze_view_file(view_path, app_name)
                else:
                    logger.warning(f"No views.py found for app: {app_name}")
                continue
                
            self._analyze_view_file(views_path, app_name)
        
        tracker.finish(f"Analyzed {len(self.views)} views")
        return self.views
        
    def _analyze_view_file(self, views_path, app_name):
        """Analyze a views.py file to extract view information"""
        try:
            # Use the FileAnalyzer with AST NodeVisitor pattern
            analyzer = FileAnalyzer(views_path, app_name, file_cache=self.file_cache)
            views = analyzer.analyze_views()
            
            # Add the views to our collection
            for view in views:
                self.views[f"{app_name}.{view.name}"] = view
                logger.success(f"  Found view: {view.name} ({view.view_type})")
                
                # Update serializer to view mapping
                if view.serializer:
                    self.serializer_to_views[view.serializer].append(f"{app_name}.{view.name}")
        
        except Exception as e:
            logger.error(f"Error analyzing views in {app_name}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
    @timed()
    def analyze_urls(self):
        """Analyze urls.py files in all Django apps and root URLs"""
        logger.info("Analyzing Django URLs...")
        
        url_parser = DjangoURLParser(self.backend_path)
        
        # If Django is initialized, use URLResolver
        if self.django_ready and self.django_reflection:
            try:
                url_patterns = self.django_reflection.get_urls()
                
                # Process the URL patterns
                for pattern_info in url_patterns:
                    pattern = pattern_info.get("pattern", "")
                    view = pattern_info.get("callback", "")
                    if pattern_info.get("module"):
                        view = f"{pattern_info['module']}.{view}"
                    name = pattern_info.get("name")
                    
                    # Create URLInfo object
                    url_info = URLInfo(
                        pattern=pattern,
                        view=view,
                        name=name
                    )
                    
                    # Group by app
                    app_name = self._extract_app_name_from_view(view)
                    if app_name not in self.urls:
                        self.urls[app_name] = []
                    self.urls[app_name].append(url_info)
                    
                    # Update view to URL mapping
                    view_name = url_parser.extract_view_name_from_reference(view)
                    if view_name:
                        self.view_to_urls[view_name].append(url_info)
                
                # Process DRF routers if available
                self._process_drf_routers()
                
                total_urls = sum(len(urls) for urls in self.urls.values())
                logger.info(f"Total URL patterns found via resolver: {total_urls}")
                return self.urls
            except Exception as e:
                logger.error(f"Error using Django URL resolver: {str(e)}")
                logger.warning("Falling back to file analysis")
        
        # Create a progress tracker
        tracker = ProgressTracker(
            total_steps=len(self.apps) + 1,  # +1 for root URLs
            description="Analyzing URLs"
        )
        tracker.start()
        
        # Traditional file analysis if Django reflection isn't available
        # First check for root URLs
        root_urls_path = url_parser.find_root_urls_path()
        if root_urls_path:
            tracker.update(1, "Processing root URLs")
            logger.info(f"Processing root URLs: {root_urls_path}")
            self._process_urls_file(root_urls_path, "root", url_parser)
        else:
            tracker.update(1, "No root URLs found")
        
        # Then check app-specific URLs
        for app_name in self.apps:
            tracker.update(1, f"Processing URLs in {app_name}")
            urls_path = os.path.join(self.backend_path, app_name, 'urls.py')
            
            if not os.path.exists(urls_path):
                logger.warning(f"No urls.py found for app: {app_name}")
                continue
                
            logger.info(f"Processing URLs in: {app_name}")
            self._process_urls_file(urls_path, app_name, url_parser)
        
        # Count total URLs
        total_urls = sum(len(urls) for urls in self.urls.values())
        tracker.finish(f"Analyzed {total_urls} URL patterns")
        return self.urls
    
    def _extract_app_name_from_view(self, view_str):
        """Extract app name from a view string"""
        parts = view_str.split('.')
        if len(parts) > 1:
            # Try to find the app name in the module path
            for app in self.apps:
                if app in parts:
                    return app
            # Default to the first part of the module path
            return parts[0]
        return "unknown"
    
    def _process_urls_file(self, urls_path, app_name, url_parser):
        """Process a urls.py file to extract URL patterns using AST"""
        try:
            # Parse the URLs file
            url_patterns, includes = url_parser.parse_urls_file(urls_path, app_name)
            
            # Update the URL data structure
            if app_name not in self.urls:
                self.urls[app_name] = []
            
            self.urls[app_name].extend(url_patterns)
            
            # Update view to URL mapping
            for url_info in url_patterns:
                view_name = url_parser.extract_view_name_from_reference(url_info.view)
                if view_name:
                    self.view_to_urls[view_name].append(url_info)
            
            # Process include statements
            for include_path in includes:
                logger.info(f"  Found include: {include_path}")
                self._process_included_urls(include_path, app_name, url_parser)
        
        except Exception as e:
            logger.error(f"Error analyzing URLs in {app_name}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
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
            import traceback
            logger.debug(traceback.format_exc())
    
    def _is_safe_import_path(self, import_path):
        """
        Check if an import path is safe to dynamically import.
        
        This helps prevent arbitrary code execution via malicious imports.
        """
        # List of safe module prefixes
        safe_prefixes = [
            'django.',
            'rest_framework.',
        ]
        
        # Add apps from the project
        for app in self.apps:
            safe_prefixes.append(f"{app}.")
                
        # Check if the import path starts with any safe prefix or is an app name
        if any(import_path.startswith(prefix) for prefix in safe_prefixes):
            return True
            
        # Check if it's a direct reference to an app
        if import_path in self.apps:
            return True
            
        # Check if path contains suspicious patterns (like os, sys, subprocess)
        suspicious_modules = ['os', 'sys', 'subprocess', 'eval', 'exec', '__']
        if any(module in import_path.split('.') for module in suspicious_modules):
            return False
            
        # Default to being cautious
        logger.warning(f"Import path not in whitelist: {import_path}")
        return False
    
    def _process_drf_routers(self):
        """Process DRF routers to extract URL patterns"""
        logger.info("Processing DRF routers...")
        
        # Check if Django reflection is available
        if self.django_ready and self.django_reflection:
            try:
                # Try to import DRF and access router registries
                with temp_sys_path([self.backend_path]):
                    # Import safely to avoid side effects
                    from .django_env import import_safely
                    
                    # Try to import REST framework
                    drf_module = import_safely('rest_framework')
                    if not drf_module:
                        logger.warning("Could not import DRF in reflection mode")
                        return
                    
                    # Try different approaches to find routers
                    routers_found = self._find_routers_via_reflection()
                    if not routers_found:
                        # Fall back to static analysis if reflection didn't find routers
                        logger.info("No routers found via reflection, trying static analysis")
                        self._find_routers_via_static_analysis()
            
            except Exception as e:
                logger.error(f"Error processing DRF routers via reflection: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
                # Fall back to static analysis
                self._find_routers_via_static_analysis()
        else:
            # Use static analysis for routers when Django reflection is not available
            self._find_routers_via_static_analysis()
    
    def _find_routers_via_reflection(self):
        """Find DRF routers using Django reflection"""
        try:
            # Try to access the router registry directly
            # This is a more advanced approach that works if the router is already registered
            count = 0
            
            # Look for common router module patterns
            router_modules_to_try = [
                'urls',  # project root urls
                'api.urls',
                'api.routers',
                'api.routes',
                'core.urls',
                'core.routers',
            ]
            
            # Add app-specific router modules
            for app in self.apps:
                router_modules_to_try.append(f"{app}.urls")
                router_modules_to_try.append(f"{app}.routers")
                router_modules_to_try.append(f"{app}.api.urls")
            
            for module_name in router_modules_to_try:
                module = import_safely(module_name)
                if not module:
                    continue
                
                # Look for router attributes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Check if it's a DefaultRouter or SimpleRouter
                    if hasattr(attr, 'registry'):
                        logger.info(f"Found router: {module_name}.{attr_name}")
                        registry = getattr(attr, 'registry')
                        
                        # Process viewsets in the registry
                        for prefix, viewset, basename in registry:
                            viewset_name = viewset.__name__
                            logger.info(f"  Router registry: {prefix} -> {viewset_name}")
                            
                            # Try to find the viewset in our views collection
                            view_full_name = None
                            for key in self.views.keys():
                                if key.endswith('.' + viewset_name):
                                    view_full_name = key
                                    break
                            
                            if view_full_name:
                                view_info = self.views[view_full_name]
                                
                                # Generate URL patterns for this viewset 
                                for action, method in self.viewset_action_map.items():
                                    # Construct path for each action
                                    if action in ['list', 'create']:
                                        pattern = f"/{prefix}/"
                                    else:
                                        pattern = f"/{prefix}/<id>/"
                                    
                                    # Create URL info
                                    url_info = URLInfo(
                                        pattern=pattern,
                                        view=view_full_name,
                                        name=f"{basename}-{action}" if basename else None
                                    )
                                    
                                    # Group by app
                                    app_name = self._extract_app_name_from_view(view_full_name)
                                    if app_name not in self.urls:
                                        self.urls[app_name] = []
                                    self.urls[app_name].append(url_info)
                                    
                                    # Update view to URL mapping
                                    self.view_to_urls[view_full_name].append(url_info)
                                    
                                    count += 1
            
            logger.info(f"Processed {count} router entries via reflection")
            return count > 0
                                    
        except Exception as e:
            logger.error(f"Error accessing router registry: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def _find_routers_via_static_analysis(self):
        """Find DRF routers using static file analysis"""
        logger.info("Analyzing files for DRF router definitions...")
        
        # Create a router visitor for AST analysis
        class RouterVisitor(ast.NodeVisitor):
            def __init__(self):
                self.routers = []
                self.registrations = []
            
            def visit_Assign(self, node):
                # Look for router = DefaultRouter() or similar
                if isinstance(node.value, ast.Call) and len(node.targets) == 1:
                    if isinstance(node.targets[0], ast.Name):
                        router_name = node.targets[0].id
                        if isinstance(node.value.func, ast.Name) and node.value.func.id in ['DefaultRouter', 'SimpleRouter']:
                            self.routers.append(router_name)
                        elif isinstance(node.value.func, ast.Attribute) and node.value.func.attr in ['DefaultRouter', 'SimpleRouter']:
                            self.routers.append(router_name)
                self.generic_visit(node)
            
            def visit_Expr(self, node):
                # Look for router.register() calls
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'register':
                        if isinstance(node.value.func.value, ast.Name):
                            router_name = node.value.func.value.id
                            if router_name in self.routers and len(node.value.args) >= 2:
                                # Extract prefix and viewset from register call
                                prefix = None
                                viewset = None
                                
                                # First arg is prefix
                                if isinstance(node.value.args[0], ast.Constant):
                                    prefix = node.value.args[0].value
                                elif isinstance(node.value.args[0], ast.Str):  # Python < 3.8
                                    prefix = node.value.args[0].s
                                
                                # Second arg is viewset
                                if isinstance(node.value.args[1], ast.Name):
                                    viewset = node.value.args[1].id
                                elif isinstance(node.value.args[1], ast.Attribute):
                                    viewset = node.value.args[1].attr
                                
                                # Get basename if available
                                basename = None
                                if len(node.value.args) >= 3:
                                    if isinstance(node.value.args[2], ast.Constant):
                                        basename = node.value.args[2].value
                                    elif isinstance(node.value.args[2], ast.Str):  # Python < 3.8
                                        basename = node.value.args[2].s
                                
                                for keyword in node.value.keywords:
                                    if keyword.arg == 'basename' and isinstance(keyword.value, (ast.Constant, ast.Str)):
                                        basename = get_constant_value(keyword.value)
                                
                                if prefix and viewset:
                                    self.registrations.append((prefix, viewset, basename))
                self.generic_visit(node)
        
        # Function to get constant value from AST node (same as in other AST visitors)
        def get_constant_value(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.NameConstant):
                return node.value
            return None
        
        # Look for router registrations in urls.py files
        total_registrations = 0
        
        # Check root urls first
        url_parser = DjangoURLParser(self.backend_path)
        root_urls_path = url_parser.find_root_urls_path()
        if root_urls_path:
            self._process_router_file(root_urls_path, "root", RouterVisitor, get_constant_value)
        
        # Then check app URLs
        for app_name in self.apps:
            urls_path = os.path.join(self.backend_path, app_name, 'urls.py')
            if os.path.exists(urls_path):
                count = self._process_router_file(urls_path, app_name, RouterVisitor, get_constant_value)
                total_registrations += count
            
            # Also check for api.py or routers.py
            for extra_file in ['api.py', 'routers.py', os.path.join('api', 'urls.py')]:
                extra_path = os.path.join(self.backend_path, app_name, extra_file)
                if os.path.exists(extra_path):
                    count = self._process_router_file(extra_path, app_name, RouterVisitor, get_constant_value)
                    total_registrations += count
        
        logger.info(f"Found {total_registrations} router registrations via static analysis")
    
    def _process_router_file(self, file_path, app_name, RouterVisitor, get_constant_value):
        """Process a file to find router registrations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            visitor = RouterVisitor()
            visitor.visit(tree)
            
            registrations_count = 0
            
            # Process the registrations
            for prefix, viewset_name, basename in visitor.registrations:
                logger.info(f"  Router registration: {prefix} -> {viewset_name}")
                
                # Find the viewset in views
                view_full_name = None
                for key in self.views.keys():
                    if key.endswith('.' + viewset_name):
                        view_full_name = key
                        break
                
                if view_full_name:
                    view_info = self.views[view_full_name]
                    
                    # Generate URL patterns for this viewset
                    for action, method in self.viewset_action_map.items():
                        # Construct path for each action
                        if action in ['list', 'create']:
                            pattern = f"/{prefix}/"
                        else:
                            pattern = f"/{prefix}/<id>/"
                        
                        # Create URL info
                        url_info = URLInfo(
                            pattern=pattern,
                            view=view_full_name,
                            name=f"{basename}-{action}" if basename else None
                        )
                        
                        # Group by app
                        if app_name not in self.urls:
                            self.urls[app_name] = []
                        self.urls[app_name].append(url_info)
                        
                        # Update view to URL mapping
                        self.view_to_urls[view_full_name].append(url_info)
                        
                        registrations_count += 1
            
            return registrations_count
            
        except Exception as e:
            logger.error(f"Error analyzing router file {file_path}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return 0
    
    @timed()
    def identify_api_endpoints(self):
        """Identify API endpoints by combining URL, view, and serializer information"""
        logger.info("Identifying API endpoints...")
        
        # Dictionary to store unique endpoints for deduplication
        unique_endpoints = {}
        
        # Create endpoint identifier
        endpoint_identifier = APIEndpointIdentifier(self.views)
        
        # Create a progress tracker
        total_urls = sum(len(urls) for urls in self.urls.values())
        tracker = ProgressTracker(
            total_steps=total_urls,
            description="Identifying API endpoints"
        )
        tracker.start()
        
        for app_name, url_patterns in self.urls.items():
            for url_info in url_patterns:
                tracker.update(1)
                
                # Derive endpoints from URL and view
                endpoints = endpoint_identifier.derive_endpoints_from_url(url_info)
                
                # Add unique endpoints
                for endpoint in endpoints:
                    # Use endpoint key for deduplication
                    key = endpoint.get_endpoint_key()
                    if key not in unique_endpoints:
                        unique_endpoints[key] = endpoint
                        logger.success(f"  Identified API endpoint: {endpoint.method} {endpoint.path}")
        
        # Set the deduplicated endpoints list
        self.api_endpoints = list(unique_endpoints.values())
        tracker.finish(f"Identified {len(self.api_endpoints)} API endpoints")
        return self.api_endpoints 