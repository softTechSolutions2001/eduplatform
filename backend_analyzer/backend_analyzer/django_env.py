"""
Django environment setup module.

This module handles Django environment initialization and reflection,
using subprocess isolation when necessary to prevent side effects.
"""

import os
import sys
import subprocess
import json
import tempfile
import importlib
import contextlib
from typing import Dict, List, Optional, Any, Tuple, Union
import logging

logger = logging.getLogger('backend_analyzer')


@contextlib.contextmanager
def temp_sys_path(paths):
    """Context manager to temporarily modify sys.path"""
    original_sys_path = sys.path.copy()
    try:
        for path in paths:
            if path not in sys.path:
                sys.path.insert(0, path)
        yield
    finally:
        sys.path = original_sys_path


def discover_settings_module(backend_path='.'):
    """Attempt to discover Django settings module path"""
    # Try common locations and patterns
    settings_candidates = [
        # Direct settings.py file
        os.path.join(backend_path, 'settings.py'),
        
        # Project/settings.py pattern
        *[os.path.join(backend_path, d, 'settings.py') 
          for d in os.listdir(backend_path) 
          if os.path.isdir(os.path.join(backend_path, d)) and 
          os.path.exists(os.path.join(backend_path, d, 'settings.py'))],
        
        # Project/config/settings.py pattern  
        *[os.path.join(backend_path, d, 'config', 'settings.py') 
          for d in os.listdir(backend_path) 
          if os.path.isdir(os.path.join(backend_path, d)) and 
          os.path.exists(os.path.join(backend_path, d, 'config', 'settings.py'))],
          
        # Project/project/settings.py pattern
        *[os.path.join(backend_path, d, d, 'settings.py') 
          for d in os.listdir(backend_path) 
          if os.path.isdir(os.path.join(backend_path, d)) and 
          os.path.exists(os.path.join(backend_path, d, d, 'settings.py'))]
    ]
    
    # Try to find manage.py and extract the settings module
    manage_py_path = os.path.join(backend_path, 'manage.py')
    if os.path.exists(manage_py_path):
        try:
            with open(manage_py_path, 'r') as f:
                manage_content = f.read()
                import re
                settings_matches = re.findall(r"os\.environ\.setdefault\(['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^'\"]+)['\"]", manage_content)
                if settings_matches:
                    return settings_matches[0]
        except Exception:
            pass
    
    # Filter to existing files
    settings_candidates = [p for p in settings_candidates if os.path.exists(p)]
    
    if not settings_candidates:
        return None
        
    # First candidate as default
    settings_path = settings_candidates[0]
    
    # Convert path to module notation
    module_path = os.path.relpath(settings_path, backend_path)
    module_path = module_path.replace(os.path.sep, '.').replace('.py', '')
    
    # If backend path is not in sys.path, prepare to add it in a context manager
    parent_dir = os.path.dirname(os.path.abspath(backend_path))
    backend_absolute = os.path.abspath(backend_path)
    
    return module_path, parent_dir, backend_absolute


def setup_django_environment(backend_path='.'):
    """Set up Django environment directly (no subprocess isolation)"""
    # Check if analyzer mode is enabled to prevent side effects
    analyzer_mode = os.environ.get('ANALYZER_MODE', '0') == '1'
    
    try:
        discovery_result = discover_settings_module(backend_path)
        if not discovery_result:
            return False, "Could not discover Django settings module"
            
        settings_module, parent_dir, backend_absolute = discovery_result
        
        # Set environment variable if not already set
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
        
        # Set analyzer mode to minimize side effects if requested
        if analyzer_mode:
            os.environ.setdefault('ANALYZER_MODE', '1')
        
        # Import Django and setup
        with temp_sys_path([parent_dir, backend_absolute]):
            import django
            
            # Try to import URL modules early to populate router registries
            try:
                # Find and import all urls.py files to populate router registries
                for root, dirs, files in os.walk(backend_absolute):
                    if 'urls.py' in files:
                        rel_path = os.path.relpath(root, backend_absolute)
                        if rel_path == '.':
                            module_path = 'urls'
                        else:
                            module_path = rel_path.replace(os.path.sep, '.') + '.urls'
                        
                        try:
                            importlib.import_module(module_path)
                        except ImportError:
                            # Silently continue if this module can't be imported directly
                            pass
            except Exception:
                # Failure to import URLs early is not critical
                pass
                
            # Now set up Django
            django.setup()
            
            # Get version information
            django_version = django.get_version()
            
            # Try to import DRF if available
            drf_version = None
            try:
                import rest_framework
                drf_version = rest_framework.__version__
            except ImportError:
                pass
                
            return True, {"django_version": django_version, "drf_version": drf_version}
    except Exception as e:
        return False, f"Error setting up Django environment: {str(e)}"


def setup_django_environment_isolated(backend_path='.', timeout=30):
    """
    Set up Django environment in a subprocess for isolation.
    
    This prevents any side effects from Django initialization affecting the main process.
    """
    # Generate a temporary Python script that will set up Django and report back
    script_content = """
import os
import sys
import json
import traceback

def run_isolated_setup():
    try:
        # Get backend path from arguments
        backend_path = sys.argv[1]
        
        # Set analyzer mode to minimize side effects
        os.environ['ANALYZER_MODE'] = '1'
        
        # Try to discover settings
        settings_module = None
        
        # Check for manage.py
        manage_py_path = os.path.join(backend_path, 'manage.py')
        if os.path.exists(manage_py_path):
            with open(manage_py_path, 'r') as f:
                manage_content = f.read()
                import re
                settings_matches = re.findall(r"os\\.environ\\.setdefault\\(['\\\"]DJANGO_SETTINGS_MODULE['\\\"],\\s*['\\\"]([^'\\\"]+)['\\\"]", manage_content)
                if settings_matches:
                    settings_module = settings_matches[0]
        
        if not settings_module:
            # Manual discovery of settings
            # [implementation similar to discover_settings_module]
            # This is simplified for the example
            for root, dirs, files in os.walk(backend_path):
                if 'settings.py' in files:
                    rel_path = os.path.relpath(root, backend_path)
                    if rel_path == '.':
                        settings_module = 'settings'
                    else:
                        settings_module = rel_path.replace(os.path.sep, '.') + '.settings'
                    break
        
        if not settings_module:
            print(json.dumps({
                "success": False,
                "error": "Could not discover Django settings module"
            }))
            return
        
        # Add backend path to sys.path
        sys.path.insert(0, os.path.abspath(backend_path))
        
        # Set Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
        
        # Import Django and set up
        import django
        django.setup()
        
        # Collect information about the Django project
        result = {
            "success": True,
            "django_version": django.get_version(),
            "settings_module": settings_module,
            "apps": [],
            "models": [],
            "urls": []
        }
        
        # Get installed apps
        from django.apps import apps
        for app_config in apps.get_app_configs():
            result["apps"].append({
                "name": app_config.name,
                "label": app_config.label,
                "models": [model.__name__ for model in app_config.get_models()]
            })
        
        # Get URL patterns (simplified)
        try:
            from django.urls import get_resolver
            resolver = get_resolver()
            
            def extract_patterns(resolver, prefix=''):
                patterns = []
                
                for pattern in resolver.url_patterns:
                    if hasattr(pattern, 'pattern'):
                        # This is a URLPattern
                        if hasattr(pattern, 'callback') and pattern.callback:
                            callback_name = pattern.callback.__name__ 
                            module_name = pattern.callback.__module__ if hasattr(pattern.callback, '__module__') else None
                            
                            patterns.append({
                                "pattern": prefix + str(pattern.pattern),
                                "name": pattern.name,
                                "callback": callback_name,
                                "module": module_name
                            })
                        elif hasattr(pattern, 'url_patterns'):
                            # This is a URLResolver
                            new_prefix = prefix + str(pattern.pattern)
                            patterns.extend(extract_patterns(pattern, new_prefix))
                
                return patterns
            
            result["urls"] = extract_patterns(resolver)
        except Exception as e:
            result["url_error"] = str(e)
        
        # Try to check for DRF
        try:
            import rest_framework
            result["drf_version"] = rest_framework.__version__
        except ImportError:
            result["drf_version"] = None
        
        # Return the result as JSON
        print(json.dumps(result))
    
    except Exception as e:
        error_info = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_info))

if __name__ == "__main__":
    run_isolated_setup()
"""

    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as script_file:
        script_file.write(script_content)
        script_path = script_file.name
    
    try:
        # Run the script in a subprocess
        result = subprocess.run(
            [sys.executable, script_path, os.path.abspath(backend_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Clean up the temporary script
        os.unlink(script_path)
        
        # Parse the output
        if result.returncode != 0:
            logger.error(f"Subprocess error: {result.stderr}")
            return False, f"Error in Django subprocess: {result.stderr}"
            
        try:
            data = json.loads(result.stdout)
            if not data.get("success", False):
                return False, data.get("error", "Unknown error in Django subprocess")
                
            return True, data
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from subprocess: {result.stdout}")
            return False, "Invalid response from Django subprocess"
            
    except subprocess.TimeoutExpired:
        # Clean up the temporary script
        os.unlink(script_path)
        return False, f"Django initialization timed out after {timeout} seconds"
        
    except Exception as e:
        # Clean up the temporary script
        try:
            os.unlink(script_path)
        except:
            pass
        
        return False, f"Error running Django in subprocess: {str(e)}"


def import_safely(module_path):
    """Safely import a module and return it or None"""
    try:
        return importlib.import_module(module_path)
    except (ImportError, ModuleNotFoundError):
        return None


class DjangoRefectionManager:
    """
    Manager for Django project reflection.
    
    Provides a unified interface to Django project information whether using
    direct reflection or subprocess isolation.
    """
    
    def __init__(self, backend_path, use_isolation=True, timeout=30):
        self.backend_path = os.path.abspath(backend_path)
        self.use_isolation = use_isolation
        self.timeout = timeout
        self.is_django_ready = False
        self.django_error = None
        self.django_info = {}
        self.django_apps = None
        self.django_models = {}
        self.django_urls = None
        
    def initialize(self):
        """Initialize Django environment using the selected method."""
        if self.use_isolation:
            self.is_django_ready, result = setup_django_environment_isolated(
                self.backend_path, self.timeout
            )
            
            if self.is_django_ready:
                self.django_info = result
            else:
                self.django_error = result
        else:
            self.is_django_ready, result = setup_django_environment(self.backend_path)
            
            if self.is_django_ready:
                # If successful, result contains version information
                self.django_info = result
                
                # Import Django-specific modules
                try:
                    import django
                    from django.apps import apps
                    from django.urls import get_resolver
                    
                    self.django_apps = apps
                    self.django_urls = get_resolver()
                except ImportError as e:
                    self.is_django_ready = False
                    self.django_error = f"Error importing Django modules: {str(e)}"
            else:
                self.django_error = result
        
        return self.is_django_ready
    
    def get_apps(self):
        """Get all Django apps from the project."""
        if not self.is_django_ready:
            return []
            
        if self.use_isolation:
            # Return app information from subprocess result
            return self.django_info.get("apps", [])
        else:
            # Use Django's app registry directly
            try:
                return [
                    {
                        "name": app_config.name,
                        "label": app_config.label,
                        "models": [model.__name__ for model in app_config.get_models()]
                    }
                    for app_config in self.django_apps.get_app_configs()
                ]
            except Exception as e:
                logger.error(f"Error getting apps: {str(e)}")
                return []
    
    def get_models(self):
        """Get all Django models from the project."""
        if not self.is_django_ready:
            return {}
            
        models = {}
        
        if self.use_isolation:
            # Process model information from subprocess result
            for app in self.django_info.get("apps", []):
                app_name = app["label"]
                for model_name in app.get("models", []):
                    models[f"{app_name}.{model_name}"] = {
                        "app": app_name,
                        "name": model_name
                    }
        else:
            # Use Django's model registry directly
            try:
                for model in self.django_apps.get_models():
                    app_name = model._meta.app_label
                    model_name = model.__name__
                    models[f"{app_name}.{model_name}"] = {
                        "app": app_name,
                        "name": model_name
                    }
            except Exception as e:
                logger.error(f"Error getting models: {str(e)}")
        
        return models
    
    def get_urls(self):
        """Get all URL patterns from the project."""
        if not self.is_django_ready:
            return []
            
        if self.use_isolation:
            # Return URL information from subprocess result
            return self.django_info.get("urls", [])
        else:
            # Process URL patterns from Django resolver directly
            try:
                from django.urls import URLPattern, URLResolver
                
                def extract_patterns(resolver, prefix=''):
                    patterns = []
                    
                    for pattern in resolver.url_patterns:
                        if isinstance(pattern, URLPattern):
                            if pattern.callback:
                                callback_name = pattern.callback.__name__
                                module_name = pattern.callback.__module__ if hasattr(pattern.callback, '__module__') else None
                                
                                patterns.append({
                                    "pattern": prefix + str(pattern.pattern),
                                    "name": pattern.name,
                                    "callback": callback_name,
                                    "module": module_name
                                })
                        elif isinstance(pattern, URLResolver):
                            # This is a URLResolver
                            new_prefix = prefix + str(pattern.pattern)
                            patterns.extend(extract_patterns(pattern, new_prefix))
                    
                    return patterns
                
                return extract_patterns(self.django_urls)
            except Exception as e:
                logger.error(f"Error getting URLs: {str(e)}")
                return [] 