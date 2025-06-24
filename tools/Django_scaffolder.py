#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# fmt: off
# isort: skip_file
"""
Django Backend Super‑Scaffolder (v 3.5.2)
========================================
A **fully‑runnable** script that scaffolds a complete Django REST backend,
produces a *front‑end bible* Markdown doc, and can optionally emit
OpenAPI YAML and Graphviz model diagrams.

### Recent Fixes (v 3.5.2)
- Fixed handling of string model references in collect_relationships
- Fixed API docs template to correctly display related model names
- Added 'creator' to DEFAULT_CONFIG owner fields list
- Removed unused code for better maintainability
- Improved documentation of enhance_jinja_env function

### Recent Fixes (v 3.5.1)
- Fixed ManyToMany relationship handling in serializers to prevent AttributeError
- Added safe handling for related_model references in graph generation
- Fixed admin list_display duplication issue that could trigger admin.E116 error
- Updated owner field filtering in views to use dict-style to avoid syntax errors
- Made sure empty field lists are handled properly in serializers
- Fixed backup directory creation in clean_old_backups
- Added 'creator' to owner_fields list in permissions
- Made sure owner_field is correctly included in the enhanced_collect_meta output
- Optimized formatter calls to run once per app instead of per file

### CLI flags
```
--app label       one or more app labels; defaults to all project apps
--depth N         nested‑serializer depth (default 2)
--swagger         write docs/openapi.yaml (needs PyYAML)
--graph           write docs/<app>_model_graph.svg (needs graphviz)
--dry-run         show diffs only, write nothing
--force           overwrite without timestamp backup
--skip-validation skip django check + makemigrations --check
--settings mod    Django settings module (default config.settings)
--update-templates force update template files
--clean-backups   remove old backup files
--config path     path to config file (YAML)
--post-process    run post-processing (linting/formatting)
--export-default-config export default configuration template
```

To run:
python super_scaffolder.py --app your_app --depth 3 --swagger --graph --dry-run

### Quick start
```bash
pip install django djangorestframework django-filter jinja2 pytest pyyaml graphviz black isort
python super_scaffolder.py --app myapp --depth 3 --swagger --graph --config scaffolder_config.yaml
```
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
import logging
from concurrent.futures import ThreadPoolExecutor
import re
import uuid
from dataclasses import dataclass, field

# ─── logging setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── constants ─────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.absolute()
SETTINGS_MODULE = "config.settings"
TEMPLATE_DIR = SCRIPT_DIR / "scaffolder_templates"
BACKUP_DIR = SCRIPT_DIR / "scaffolder_backups"
DOCS_DIR = SCRIPT_DIR / "docs"
CONFIG_DIR = SCRIPT_DIR / "scaffolder_config"
API_BASE = "api/v1"
BANNER = (
    "#!/usr/bin/env python3\n"
    "# -*- coding: utf-8 -*-\n"
    "# fmt: off\n"
    "# isort: skip_file\n"
    "# ==========  AUTO‑GENERATED – DO NOT EDIT MANUALLY  =========="
    "\n# Generated: {timestamp}\n"
)
MAX_BACKUP_AGE_DAYS = 30
REQUIRED_PYTHON_VERSION = (3, 7)

# Initialize inflect engine early for use in jenv function
try:
    import inflect
    INFLECT_ENGINE = inflect.engine()
except ImportError:
    INFLECT_ENGINE = None
    logger.warning("inflect package not installed. Using basic pluralization.")

# ─── default configuration ─────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "api_base": "api/v1",
    "max_backup_age_days": 30,
    "model_exclude_patterns": [r"^django\."],
    "field_types": {
        "search": ["CharField", "TextField", "EmailField", "SlugField"],
        "filter": ["BooleanField", "CharField", "IntegerField", "DateField", "DateTimeField"],
        "display": ["name", "title", "slug", "code", "email"],
        "owner": ["owner", "user", "created_by", "author", "creator"]
    },
    "formatters": {
        "black": {
            "enabled": True,
            "command": ["black", "-q", "{file}"],
            "file_patterns": [r"\.py$"]
        },
        "isort": {
            "enabled": True,
            "command": ["isort", "-q", "{file}"],
            "file_patterns": [r"\.py$"]
        }
    },
    "validation": {
        "run_django_check": True,
        "run_migration_check": True,
        "run_pylint": False
    },
    "features": {
        "swagger": True,
        "graph": True,
        "parallel": True
    }
}

# ─── dependency guard ──────────────────────────────────────────────────────
REQ = {
    "django": "django>=3.2",
    "rest_framework": "djangorestframework",
    "jinja2": "jinja2",
    "django_filters": "django-filter",
    "pyyaml": "pyyaml",  # Optional but recommended
    "graphviz": "graphviz",  # Optional but recommended
    "black": "black",  # Optional for formatting
    "isort": "isort",  # Optional for import sorting
}

def check_python_version() -> None:
    """Check if Python version meets requirements."""
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        sys.exit(f"Python {'.'.join(map(str, REQUIRED_PYTHON_VERSION))}+ required")

def check_dependencies() -> None:
    """Check and report missing dependencies."""
    missing = [pkg for pkg in REQ if importlib.util.find_spec(pkg) is None]
    if missing:
        sys.exit("Missing deps: " + ", ".join(missing) + "\nRun: pip install " + " ".join(REQ[pkg] for pkg in missing))

check_python_version()
check_dependencies()

import django  # type: ignore
from django.apps import apps  # type: ignore
from django.core.management import call_command  # type: ignore
from django.db import models  # type: ignore
from jinja2 import Environment, FileSystemLoader  # type: ignore

GV = importlib.util.find_spec("graphviz") is not None
YAML = importlib.util.find_spec("yaml") is not None

# Global config that will be loaded from file or defaults
CONFIG = DEFAULT_CONFIG.copy()

# ─── configuration loading ─────────────────────────────────────────────────
def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from YAML file or use defaults."""
    global CONFIG
    
    if not config_path:
        logger.info("No config file specified, using defaults")
        return CONFIG
    
    try:
        import yaml
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file {config_file} does not exist, using defaults")
            return CONFIG
            
        with open(config_file, 'r') as f:
            user_config = yaml.safe_load(f)
            
        if not isinstance(user_config, dict):
            logger.warning(f"Invalid config format in {config_file}, using defaults")
            return CONFIG
            
        # Recursively merge configurations
        merged_config = deep_merge(CONFIG.copy(), user_config)
        logger.info(f"Loaded configuration from {config_file}")
        
        # Update global CONFIG
        CONFIG = merged_config
        return CONFIG
        
    except ImportError:
        logger.warning("PyYAML not available, using default configuration")
        return CONFIG
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return CONFIG

def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Note: This implementation REPLACES lists rather than merging them.
    If you need to merge lists, you'll need to handle that case manually in your config.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
            
    return result

def save_default_config() -> None:
    """
    Save default configuration as a template file.
    This will not overwrite existing files.
    """
    if not YAML:
        logger.warning("PyYAML not available, cannot save default configuration")
        return
        
    try:
        import yaml
        CONFIG_DIR.mkdir(exist_ok=True)
        config_file = CONFIG_DIR / "default_config_template.yaml"
        
        # Only write if file doesn't exist
        if not config_file.exists():
            with open(config_file, 'w') as f:
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
                
            logger.info(f"Default configuration template saved to {config_file}")
    except Exception as e:
        logger.error(f"Error saving default configuration: {str(e)}")

# ─── bootstrap ─────────────────────────────────────────────────────────────
def bootstrap(settings: str) -> None:
    """Initialize Django environment."""
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings
    django.setup()

# ─── template seeding ------------------------------------------------------
def seed_templates(force_update: bool = False) -> None:
    """Write default Jinja templates if they don't exist or force update."""
    TEMPLATE_DIR.mkdir(exist_ok=True)
    hdr = "AUTO‑GENERATED – DO NOT EDIT MANUALLY"
    templates: Dict[str, str] = {
        "serializers.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nfrom rest_framework import serializers\nfrom .models import {% for m in models %}{{ m.name }}{% if not loop.last %}, {% endif %}{% endfor %}\n\n"
            "{% for m in models %}"
            "class {{ m.name }}Serializer(serializers.ModelSerializer):\n"
            "    {% for rel in relationships.get(m.name, []) %}"
            "{% if not rel.reverse and rel.type in ('ForeignKey', 'OneToOneField') %}"
            "    {{ rel.field_name }}_display = serializers.StringRelatedField(source='{{ rel.field_name }}', read_only=True)\n"
            "{% endif %}"
            "    {% endfor %}"
            "\n    class Meta:\n"
            "        model = {{ m.name }}\n"
            "        # Use serializer config depth based on the calculated optimal value\n"
            "        depth = {{ serializer_config[m.name]['list']['depth'] if m.name in serializer_config else depth }}\n"
            "        # Use fields from serializer config if available\n"
            "        {% if m.name in serializer_config and serializer_config[m.name]['list']['fields'] and serializer_config[m.name]['list']['fields']|length > 0 %}"
            "        fields = {{ serializer_config[m.name]['list']['fields'] }}\n"
            "        {% else %}"
            "        fields = '__all__'\n"
            "        {% endif %}\n\n"
            "class {{ m.name }}DetailSerializer({{ m.name }}Serializer):\n"
            "    {% for rel in relationships.get(m.name, []) %}"
            "{% if rel.type in ('ForeignKey', 'OneToOneField', 'ManyToManyField') and not rel.reverse %}"
            "    # Add detailed serializers for related objects\n"
            "    {{ rel.field_name }}_detail = serializers.SerializerMethodField(read_only=True)\n"
            "{% endif %}"
            "    {% endfor %}"
            "\n    class Meta({{ m.name }}Serializer.Meta):\n"
            "        # Use deeper nesting for detail view\n"
            "        depth = {{ serializer_config[m.name]['detail']['depth'] if m.name in serializer_config else depth }}\n"
            "        # Use fields from serializer config if available\n"
            "        {% if m.name in serializer_config and serializer_config[m.name]['detail']['fields'] and serializer_config[m.name]['detail']['fields']|length > 0 %}"
            "        fields = {{ serializer_config[m.name]['detail']['fields'] }}\n"
            "        {% endif %}\n\n"
            "    {% for rel in relationships.get(m.name, []) %}"
            "{% if rel.type in ('ForeignKey', 'OneToOneField', 'ManyToManyField') and not rel.reverse %}"
            "    def get_{{ rel.field_name }}_detail(self, obj):\n"
            "{% if rel.type == 'ManyToManyField' %}"
            "        # Handle many-to-many relationship properly\n"
            "        rel = getattr(obj, '{{ rel.field_name }}').all()\n"
            "        return [{'id': r.id, 'str': str(r)} for r in rel]\n"
            "{% else %}"
            "        related = getattr(obj, '{{ rel.field_name }}', None)\n"
            "        if related:\n"
            "            return {'id': related.id, 'str': str(related)}\n"
            "        return None\n"
            "{% endif %}"
            "{% endif %}"
            "    {% endfor %}"
            "{% endfor %}"
        ),
        "views.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {'page_size': 50}\nfrom rest_framework import viewsets, filters\nfrom django_filters.rest_framework import DjangoFilterBackend\nfrom rest_framework.permissions import IsAuthenticatedOrReadOnly\nfrom .models import {% for m in models %}{{ m.name }}{% if not loop.last %}, {% endif %}{% endfor %}\nfrom .serializers import {% for m in models %}{{ m.name }}Serializer, {{ m.name }}DetailSerializer{% if not loop.last %}, {% endif %}{% endfor %}\n{% if needs_owner_perm %}from .permissions import IsOwnerOrReadOnly\n{% endif %}\n{% for m in models %}class {{ m.name }}ViewSet(viewsets.ModelViewSet):\n    queryset = {{ m.name }}.objects.all()\n    serializer_class = {{ m.name }}Serializer\n    permission_classes = [IsAuthenticatedOrReadOnly{% if m.owner %}, IsOwnerOrReadOnly{% endif %}]\n    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]\n    search_fields = {{ m.search }}\n    filterset_fields = {{ m.filters }}\n    ordering_fields = '__all__'\n\n    def get_serializer_class(self):\n        return {{ m.name }}DetailSerializer if self.action in ['retrieve', 'update', 'partial_update', 'create'] else {{ m.name }}Serializer\n\n    def get_queryset(self):\n        queryset = {{ m.name }}.objects.all()\n        {% if m.owner %}\n        # Filter by owner if requested\n        if self.request.query_params.get('my_items', False) and self.request.user.is_authenticated:\n            queryset = queryset.filter(**{'{{ m.owner_field }}': self.request.user})\n        {% endif %}\n        return queryset\n\n{% endfor %}"
        ),
        "urls.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nfrom django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\nfrom . import views\n\napp_name = '{{ app_label }}'\nrouter = DefaultRouter()\n{% for m in models %}router.register(r'{{ m.route }}', views.{{ m.name }}ViewSet, basename='{{ m.route }}')\n{% endfor %}\nurlpatterns = [path('', include(router.urls))]\n"
        ),
        "admin.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nfrom django.contrib import admin\nfrom .models import {% for m in models %}{{ m.name }}{% if not loop.last %}, {% endif %}{% endfor %}\n\n{% for m in models %}@admin.register({{ m.name }})\nclass {{ m.name }}Admin(admin.ModelAdmin):\n    list_display = tuple(dict.fromkeys(['id'{% for f in m.display %}, '{{ f }}'{% endfor %}]))\n    search_fields = {{ m.search }}\n    list_filter = {{ m.filters }}\n{% if m.owner %}\n    def get_queryset(self, request):\n        qs = super().get_queryset(request)\n        if request.user.is_superuser:\n            return qs\n        return qs.filter({{ m.owner_field }}=request.user)\n{% endif %}\n\n{% endfor %}"
        ),
        "permissions.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nfrom rest_framework.permissions import BasePermission, SAFE_METHODS\n\nclass IsOwnerOrReadOnly(BasePermission):\n    def has_object_permission(self, request, view, obj):\n        if request.method in SAFE_METHODS:\n            return True\n        # Check for various owner field names\n        owner_fields = ['owner', 'user', 'created_by', 'author', 'creator']\n        for field in owner_fields:\n            if hasattr(obj, f'{field}_id'):\n                return getattr(obj, f'{field}_id') == getattr(request.user, 'id', None)\n            elif hasattr(obj, field):\n                return getattr(obj, field) == request.user\n        return False\n"
        ),
        "api_docs.md.j2": (
            "# {{ app_label|capitalize }} API Documentation\n_Generated: {{ timestamp }}_\n\n## API Endpoints\n\nBase URL: `/{{ api_base }}/`\n\n## Files generated\n{% for f in file_list %}- {{ f }}{% endfor %}\n\n{% for m in models %}### {{ m.name }}\nEndpoint `/{{ api_base }}/{{ m.route }}/`\n\n#### Model Fields\n| Field | Type | Description |\n|-------|------|-------------|\n{% for fld in m.fields %}| {{ fld.name }} | {{ fld.type }} | {{ fld.description }} |\n{% endfor %}\n\n#### Relationships\n{% if relationships.get(m.name, []) %}\n| Field | Related Model | Type |\n|-------|--------------|------|\n{% for rel in relationships.get(m.name, []) %}| {{ rel.field_name }} | {% if '.' in rel.related_model %}{{ rel.related_model.split('.')[-1] }}{% else %}{{ rel.related_model }}{% endif %} | {{ rel.type }} |\n{% endfor %}\n{% else %}\nNo relationships defined.\n{% endif %}\n\n#### API Operations\n- `GET /{{ api_base }}/{{ m.route }}/` - List all {{ m.name }} objects\n- `POST /{{ api_base }}/{{ m.route }}/` - Create a new {{ m.name }}\n- `GET /{{ api_base }}/{{ m.route }}/{id}/` - Retrieve a {{ m.name }} by ID\n- `PUT /{{ api_base }}/{{ m.route }}/{id}/` - Update a {{ m.name }}\n- `PATCH /{{ api_base }}/{{ m.route }}/{id}/` - Partially update a {{ m.name }}\n- `DELETE /{{ api_base }}/{{ m.route }}/{id}/` - Delete a {{ m.name }}\n\n{% endfor %}"
        ),
        "tests.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nimport pytest\nfrom django.urls import reverse\nfrom rest_framework import status\nfrom rest_framework.test import APIClient\n\n# Simple fixtures for API testing\n@pytest.fixture\ndef api_client():\n    return APIClient()\n\n@pytest.fixture\ndef authenticated_user(db, django_user_model):\n    user = django_user_model.objects.create_user(username='testuser', password='password')\n    return user\n\n{% for m in models %}\n@pytest.mark.django_db\nclass Test{{ m.name }}API:\n    def test_list(self, api_client):\n        url = reverse('{{ app_label }}:{{ m.route }}-list')\n        response = api_client.get(url)\n        assert response.status_code == status.HTTP_200_OK\n\n    def test_create(self, api_client, authenticated_user):\n        api_client.force_authenticate(user=authenticated_user)\n        url = reverse('{{ app_label }}:{{ m.route }}-list')\n        data = {}\n        # TODO: Add required fields to the data dictionary\n        response = api_client.post(url, data, format='json')\n        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]\n\n{% endfor %}"
        ),
        "conftest.py.j2": (
            "{{ banner }}\n"+hdr+"\nCONFIG = {}\nimport pytest\nfrom rest_framework.test import APIClient\n\n@pytest.fixture\ndef api_client():\n    return APIClient()\n\n@pytest.fixture\ndef authenticated_user(db, django_user_model):\n    user = django_user_model.objects.create_user(username='testuser', password='password')\n    return user\n"
        ),
    }
    
    for name, txt in templates.items():
        p = TEMPLATE_DIR / name
        if not p.exists() or force_update:
            p.write_text(txt.strip(), encoding="utf-8")
            logger.info(f"Template {name} {'updated' if p.exists() else 'created'}")

# ─── Jinja environment -----------------------------------------------------
def jenv() -> Environment:
    """Create and configure Jinja environment."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    # Add JSON serialization for both regular templates and enhanced ones
    env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)
    
    # Add pluralize filter (safely handle missing inflect)
    if INFLECT_ENGINE:
        env.filters["pluralize"] = INFLECT_ENGINE.plural
    else:
        # Simple pluralization if inflect not available
        def simple_pluralize(value):
            if value.endswith('s') or value.endswith('x') or value.endswith('z'):
                return value + 'es'
            elif value.endswith('y') and value[-2] not in 'aeiou':
                return value[:-1] + 'ies'
            else:
                return value + 's'
        env.filters["pluralize"] = simple_pluralize
    
    return env

# ─── meta collection -------------------------------------------------------
def get_field_description(field: models.Field) -> str:
    """Get a human-readable description of a field."""
    if hasattr(field, 'help_text') and field.help_text:
        return field.help_text
    if hasattr(field, 'verbose_name'):
        return str(field.verbose_name)
    return field.name.replace('_', ' ').title()

def enhanced_collect_meta(app_label: str) -> Tuple[List[Dict], bool]:
    """
    Enhanced collection of model metadata with dataclasses.
    
    Args:
        app_label: The app label to collect metadata for
        
    Returns:
        Tuple of (metadata, owner_flag)
    """
    app_config = apps.get_app_config(app_label)
    
    meta = []
    owner_flag = False
    
    # Get all models for this app
    for model in app_config.get_models():
        # Skip swappable models like User if they've been swapped
        if hasattr(model._meta, 'swapped') and model._meta.swapped:
            continue
        
        # Get field list
        field_infos = []
        owner_field = ""
        has_owner = False
        
        for field in model._meta.get_fields():
            # Skip auto-created fields from M2M relationships
            if field.auto_created and not field.concrete:
                continue
                
            field_info = extract_field_info(field)
            field_infos.append(field_info)
            
            # Check if this could be an owner field
            owner_fields = ('owner', 'user', 'created_by', 'author', 'creator')
            if field.name in owner_fields:
                has_owner = True
                owner_field = field.name
                owner_flag = True
        
        # Create model info dictionary
        model_dict = {
            "name": model.__name__,
            "route": model.__name__.lower(),
            "fields": [convert_field_info_to_dict(f) for f in field_infos],
            "search": [f.name for f in field_infos if f.searchable],
            "filters": [f.name for f in field_infos if f.filterable and not f.many_to_many],
            "display": get_admin_list_display(field_infos) or ["id"],
            "owner": has_owner,
            "owner_field": owner_field
        }
        
        # Add to result
        meta.append(model_dict)
    
    return meta, owner_flag

def collect_meta(label: str) -> Tuple[List[Dict], bool]:
    """
    Collect metadata about models in an app (fallback method).
    This function serves as a fallback for the enhanced_collect_meta function.
    """
    try:
        app_config = apps.get_app_config(label)
        meta = []
        owner_flag = False
        
        # Get field types from config
        search_types = CONFIG["field_types"]["search"]
        filter_types = CONFIG["field_types"]["filter"]
        display_names = CONFIG["field_types"]["display"]
        owner_names = CONFIG["field_types"]["owner"]
        
        # Explicitly list reverse relation types to avoid including in filters
        reverse_relation_types = ["ManyToOneRel", "ManyToManyRel", "OneToOneRel"]
        
        for model in app_config.get_models():
            if hasattr(model._meta, 'abstract') and model._meta.abstract:
                continue
                
            fields, search_fields, filter_fields, display_fields = [], [], [], []
            has_owner, owner_field = False, ""
            
            for field in model._meta.get_fields():
                field_type = type(field).__name__
                description = get_field_description(field)
                
                # Add to search fields if it's a text field
                if field_type in search_types:
                    search_fields.append(field.name)
                
                # Add to filter fields if it's appropriate, excluding reverse relations and M2M
                is_valid_filter = ((not field.is_relation and field_type in filter_types) or 
                                 (field.is_relation and field_type in ["ForeignKey", "OneToOneField"]))
                is_reverse = field_type in reverse_relation_types
                
                if is_valid_filter and not is_reverse:
                    filter_fields.append(field.name)
                
                # Add to display fields if it's a common identifier
                if field.name in display_names:
                    display_fields.append(field.name)
                
                # Check for ownership fields
                if field.name in owner_names:
                    has_owner = True
                    owner_field = field.name
                
                # Get related model for relation fields
                related_model = None
                if field.is_relation:
                    related_model = getattr(field, 'related_model', None)
                
                is_reverse_relation = field_type in reverse_relation_types
                
                fields.append({
                    "name": field.name,
                    "type": field_type,
                    "description": description,
                    "is_relation": field.is_relation,
                    "is_reverse_relation": is_reverse_relation,
                    "related_model": related_model,
                    "null": getattr(field, 'null', False),
                    "blank": getattr(field, 'blank', False),
                    "unique": getattr(field, 'unique', False)
                })
            
            owner_flag |= has_owner
            meta.append({
                "name": model.__name__,
                "route": model.__name__.lower(),
                "fields": fields,
                "search": search_fields or ["id"],
                "filters": filter_fields,
                "display": display_fields or ["id"],
                "owner": has_owner,
                "owner_field": owner_field
            })
            
    except Exception as e:
        logger.error(f"Error collecting metadata for {label}: {str(e)}")
        raise
        
    return meta, owner_flag

# ─── render ---------------------------------------------------------------
def render(label: str, meta: List[Dict], owner: bool, depth: int) -> Dict[str, str]:
    """Render templates with model metadata."""
    env = jenv()
    
    # Collect relationships between models
    relationships = collect_relationships(meta)
    
    # Generate nested serializer configurations
    serializer_config = generate_nested_serializers(meta, depth)
    
    ctx = {
        "banner": BANNER.format(timestamp=dt.datetime.now().isoformat(timespec="seconds")),
        "app_label": label,
        "models": meta,
        "api_base": CONFIG["api_base"],
        "needs_owner_perm": owner,
        "depth": depth,
        "relationships": relationships,
        "serializer_config": serializer_config
    }
    
    files: Dict[str, str] = {}
    for tpl in TEMPLATE_DIR.glob("*.j2"):
        try:
            name = tpl.stem + (".py" if not tpl.stem.endswith("md") else ".md")
            files[name] = env.get_template(tpl.name).render(**ctx, file_list=[])
        except Exception as e:
            logger.error(f"Error rendering template {tpl.name}: {str(e)}")
            raise
    
    # Create app-specific frontend bible to avoid race conditions in parallel mode
    files[f"{label}_frontend_bible.md"] = env.get_template("api_docs.md.j2").render(
        **ctx, file_list=sorted(files)
    )
    
    # Remove the generic frontend_bible.md to avoid race conditions
    if "frontend_bible.md" in files:
        del files["frontend_bible.md"]
            
    return files

# ─── writing --------------------------------------------------------------
def clean_old_backups() -> None:
    """Remove backup files older than MAX_BACKUP_AGE_DAYS."""
    BACKUP_DIR.mkdir(exist_ok=True)
    
    cutoff = dt.datetime.now() - dt.timedelta(days=MAX_BACKUP_AGE_DAYS)
    for backup in BACKUP_DIR.glob("*.bak"):
        if dt.datetime.fromtimestamp(backup.stat().st_mtime) < cutoff:
            backup.unlink()
            logger.info(f"Removed old backup: {backup}")

def atomic_write(path: Path, content: str, force: bool, dry: bool) -> None:
    """Write content to file atomically with optional backup."""
    if path.exists():
        diff = difflib.unified_diff(
            path.read_text().splitlines(1),
            content.splitlines(1),
            fromfile=str(path),
            tofile="NEW"
        )
        print("".join(diff))
        
    if dry:
        return
        
    if path.exists() and not force:
        BACKUP_DIR.mkdir(exist_ok=True)
        # Use microsecond precision and a UUID to ensure uniqueness
        unique_id = str(uuid.uuid4())[:8]
        timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
        backup_path = BACKUP_DIR / f"{path.name}.{timestamp}_{unique_id}.bak"
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
    try:
        fd, tmp = tempfile.mkstemp(dir=str(path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
        logger.info(f"Wrote file: {path}")
    except Exception as e:
        logger.error(f"Error writing {path}: {str(e)}")
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

def write_app(label: str, files: Dict[str, str], force: bool, dry: bool) -> None:
    """Write generated files for an app."""
    try:
        app_root = Path(apps.get_app_config(label).path)
        for fname, code in files.items():
            target = DOCS_DIR / fname if fname.endswith(".md") else app_root / fname
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, code, force, dry)
    except Exception as e:
        logger.error(f"Error writing files for {label}: {str(e)}")
        raise

# ─── extras ---------------------------------------------------------------
def generate_swagger(enabled: bool) -> None:
    """Generate OpenAPI schema if enabled."""
    if not enabled:
        return
        
    if not YAML:
        logger.warning("⚠️  PyYAML missing – skipping OpenAPI export")
        return
        
    try:
        DOCS_DIR.mkdir(exist_ok=True)
        out = DOCS_DIR / "openapi.yaml"
        call_command("generateschema", "--format", "openapi", "--output", str(out))
        logger.info(f"📝  Swagger schema written to {out}")
    except Exception as e:
        logger.error(f"Error generating Swagger schema: {str(e)}")
        raise

def graph_app(label: str, meta: List[Dict], enabled: bool) -> None:
    """Generate model relationship diagram if enabled."""
    if not enabled:
        return
        
    if not GV:
        logger.warning(f"⚠️  graphviz missing – skipping diagram for {label}")
        return
        
    try:
        from graphviz import Digraph  # type: ignore
        
        g = Digraph(label, graph_attr={"rankdir": "LR"})
        g.attr('node', shape='box')
        
        # Helper function to safely get model name
        def _get_model_name(model_obj):
            if hasattr(model_obj, "__name__"):
                return model_obj.__name__
            return str(model_obj).split('.')[-1] if '.' in str(model_obj) else str(model_obj)
        
        # Add nodes
        for m in meta:
            g.node(m["name"], shape="box")
            
        # Add edges with bidirectional arrows for clarity
        for m in meta:
            src = m["name"]
            for f in m["fields"]:
                if f["is_relation"] and f["related_model"]:
                    try:
                        tgt = _get_model_name(f["related_model"])
                        g.edge(src, tgt, label=f["name"], dir="both")
                    except Exception as e:
                        logger.warning(f"Could not add edge for {src}.{f['name']}: {str(e)}")
                    
        DOCS_DIR.mkdir(exist_ok=True)
        g.render((DOCS_DIR / f"{label}_model_graph").as_posix(), format="svg", cleanup=True)
        logger.info(f"📈  Diagram written for {label}")
    except Exception as e:
        logger.error(f"Error generating diagram for {label}: {str(e)}")
        raise

# ─── validation -----------------------------------------------------------
def validate(skip: bool) -> None:
    """Run Django validation checks."""
    if skip:
        return
        
    try:
        call_command("check", verbosity=0)
        subprocess.run(
            [sys.executable, "manage.py", "makemigrations", "--check", "--dry-run"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("✅  Validation passed")
    except subprocess.CalledProcessError as e:
        logger.error(f"Validation failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise

# ─── post-processing ------------------------------------------------------
def post_process_app(app_root: Path, formatters: Dict) -> None:
    """Run post-processing on generated files."""
    if not formatters:
        return
    
    # Run formatters once per app rather than per file for better performance
    if formatters.get("black", {}).get("enabled", False):
        try:
            # Use a single black call on the app directory instead of per-file
            logger.info(f"Running black on {app_root}")
            result = subprocess.run(
                ["black", str(app_root)],
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.warning(f"Black formatter failed on {app_root}: {result.stderr}")
            else:
                logger.info(f"Successfully formatted {app_root} with black")
        except Exception as e:
            logger.error(f"Error running black on {app_root}: {str(e)}")
    
    if formatters.get("isort", {}).get("enabled", False):
        try:
            # Use a single isort call on the app directory instead of per-file
            logger.info(f"Running isort on {app_root}")
            result = subprocess.run(
                ["isort", str(app_root)],
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.warning(f"Isort formatter failed on {app_root}: {result.stderr}")
            else:
                logger.info(f"Successfully formatted {app_root} with isort")
        except Exception as e:
            logger.error(f"Error running isort on {app_root}: {str(e)}")
            
    logger.info(f"Post-processed app directory: {app_root}")

# ─── relationship handling ---------------------------------------------------
def collect_relationships(meta_list: List[Dict]) -> Dict[str, List[Dict]]:
    """Collect and organize relationships between models."""
    relationships = {}
    
    # Helper function to safely get model name
    def _get_model_name(model_obj):
        if hasattr(model_obj, "__name__"):
            return model_obj.__name__
        return str(model_obj).split('.')[-1] if '.' in str(model_obj) else str(model_obj)
    
    # First pass: collect all model names
    model_names = {model["name"]: model for model in meta_list}
    
    # Second pass: analyze relationships
    for model in meta_list:
        model_name = model["name"]
        relationships[model_name] = []
        
        for field in model["fields"]:
            if not field["is_relation"] or not field["related_model"]:
                continue
                
            related_name = _get_model_name(field["related_model"])
            
            # Skip if related model not in our collected models
            if related_name not in model_names:
                continue
                
            field_type = field["type"]
            
            # Add relationship details
            relationships[model_name].append({
                "field_name": field["name"],
                "related_model": related_name,
                "type": field_type,
                "reverse": field_type in ("ManyToOneRel", "ManyToManyRel", "OneToOneRel")
            })
    
    return relationships

def should_include_serializer_field(field: Dict, serializer_type: str) -> bool:
    """Determine if a field should be included in a serializer."""
    # Skip certain fields in list serializers to prevent heavy responses
    if serializer_type == "list" and field["is_relation"]:
        # Include ForeignKey and OneToOne references in list views, but not reverse relations
        if field["type"] in ("ForeignKey", "OneToOneField"):
            return True
        return False
    
    # Include all fields in detail serializers
    return True

def generate_nested_serializers(models: List[Dict], depth: int = 2) -> Dict[str, Dict]:
    """Generate intelligent nested serializer configurations."""
    serializer_config = {}
    
    # Helper function to safely get model name
    def _safe_model_name(model_obj):
        if hasattr(model_obj, "__name__"):
            return model_obj.__name__
        return str(model_obj).split('.')[-1] if '.' in str(model_obj) else str(model_obj)
    
    for model in models:
        model_name = model["name"]
        
        # Configure list serializer (simplified)
        list_fields = []
        for field in model["fields"]:
            if should_include_serializer_field(field, "list"):
                list_fields.append(field["name"])
        
        # Configure detail serializer (with nesting)
        detail_fields = []
        nested_fields = {}
        
        # Add all fields to detail view
        for field in model["fields"]:
            detail_fields.append(field["name"])
            
            # Configure nested serializers for relations
            if field["is_relation"] and field["related_model"] and depth > 0:
                related_name = _safe_model_name(field["related_model"])
                nested_fields[field["name"]] = {
                    "depth": depth - 1,
                    "model": related_name
                }
        
        serializer_config[model_name] = {
            "list": {
                "fields": list_fields,
                "depth": 0  # No nesting in list view
            },
            "detail": {
                "fields": detail_fields,
                "depth": depth,
                "nested_fields": nested_fields
            }
        }
    
    return serializer_config

# ─── generate combined frontend bible ----------------------------------------
def generate_combined_frontend_bible(app_labels: List[str]) -> None:
    """Generate a master frontend bible that links to all app-specific files."""
    try:
        env = jenv()
        
        # Ensure docs directory exists
        DOCS_DIR.mkdir(exist_ok=True)
        
        # Create a master bible file that links to all app-specific files
        content = f"""# Master Frontend Bible
_Generated: {dt.datetime.now().isoformat(timespec="seconds")}_

This document provides links to API documentation for all apps in the project.

## Available App Documentation

"""
        for label in app_labels:
            content += f"- [{label.capitalize()} API Documentation]({label}_frontend_bible.md)\n"
        
        # Write the master bible file
        master_file = DOCS_DIR / "master_frontend_bible.md"
        with open(master_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Generated master frontend bible at {master_file}")
    except Exception as e:
        logger.error(f"Error generating master frontend bible: {str(e)}")

# ─── CLI ------------------------------------------------------------------
def main() -> int:
    """Main entry point."""
    p = argparse.ArgumentParser(description="Generate DRF scaffold + docs")
    p.add_argument("--app", action="append", help="Target app (repeatable)")
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--swagger", action="store_true")
    p.add_argument("--graph", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--skip-validation", action="store_true")
    p.add_argument("--settings", default=SETTINGS_MODULE)
    p.add_argument("--update-templates", action="store_true")
    p.add_argument("--clean-backups", action="store_true")
    p.add_argument("--config", help="Path to configuration file (YAML)")
    p.add_argument("--post-process", action="store_true", help="Run post-processing (formatting)")
    p.add_argument("--export-default-config", action="store_true", help="Export default configuration template")
    p.add_argument("--use-standard", action="store_true", help="Use standard metadata collection instead of enhanced")
    p.add_argument("--check-dependencies", action="store_true", help="Check for circular dependencies between apps")
    p.add_argument("--enhanced-docs", action="store_true", help="Generate enhanced API documentation")
    args = p.parse_args()

    try:
        # Handle export-default-config flag first
        if args.export_default_config:
            if not YAML:
                logger.error("PyYAML not available, cannot export default configuration")
                return 1
                
            import yaml
            CONFIG_DIR.mkdir(exist_ok=True)
            config_file = CONFIG_DIR / "default_config_template.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
                
            logger.info(f"Default configuration template exported to {config_file}")
            return 0
        
        # Load configuration
        global CONFIG
        CONFIG = load_config(args.config)
        
        # Save default config for reference (won't overwrite existing)
        save_default_config()
        
        # Django setup
        bootstrap(args.settings)
        
        # Prepare templates
        seed_templates(args.update_templates)
        
        # Clean old backups if requested
        if args.clean_backups or CONFIG.get("auto_clean_backups", False):
            clean_old_backups()

        # Get target apps
        model_exclude = CONFIG.get("model_exclude_patterns", [r"^django\."])
        exclude_regex = re.compile("|".join(model_exclude))
        
        targets = args.app or [
            cfg.label for cfg in apps.get_app_configs()
            if list(cfg.get_models()) and not exclude_regex.match(cfg.label)
        ]
        
        if not targets:
            logger.error("No target apps found with models")
            return 1
            
        # Check for circular dependencies if requested
        if args.check_dependencies:
            check_app_dependencies(targets)
            
        # Process each app
        use_enhanced = not args.use_standard
        
        if CONFIG.get("features", {}).get("parallel", False) and len(targets) > 1:
            # Process apps in parallel
            with ThreadPoolExecutor(max_workers=min(os.cpu_count() or 4, len(targets))) as executor:
                futures = []
                for label in targets:
                    futures.append(executor.submit(
                        process_app, 
                        label, 
                        args.depth, 
                        args.force, 
                        args.dry_run, 
                        args.graph,
                        args.post_process,
                        use_enhanced
                    ))
                
                # Wait for all tasks to complete
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        if not args.force:
                            logger.error(f"App processing failed: {str(e)}")
                            return 1
        else:
            # Process apps sequentially
            for label in targets:
                try:
                    process_app(
                        label, 
                        args.depth, 
                        args.force, 
                        args.dry_run, 
                        args.graph,
                        args.post_process,
                        use_enhanced
                    )
                except Exception as e:
                    logger.error(f"Error processing app {label}: {str(e)}")
                    if not args.force:
                        return 1
                    
        # Generate OpenAPI schema
        use_swagger = args.swagger or CONFIG.get("features", {}).get("swagger", False)
        if use_swagger:
            generate_swagger(True)
            
        # Run validation
        if not args.skip_validation:
            validate_config = CONFIG.get("validation", {})
            run_django_check = validate_config.get("run_django_check", True)
            run_migration_check = validate_config.get("run_migration_check", True)
            
            if run_django_check or run_migration_check:
                validate(False)
        
        # Generate frontend bible
        if not args.dry_run:
            generate_combined_frontend_bible(targets)
            
        # Generate enhanced docs if requested
        if args.enhanced_docs and not args.dry_run:
            generate_enhanced_docs(targets)
        
        logger.info("✅  Done – scaffold + docs generated")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1

def process_app(label: str, depth: int, force: bool, dry_run: bool, graph: bool, post_process: bool, use_enhanced: bool = True) -> None:
    """Process a single app - can be run in parallel."""
    try:
        logger.info(f"Processing app: {label}")
        
        # Collect model metadata using either enhanced or regular method
        if use_enhanced:
            try:
                meta, owner_flag = enhanced_collect_meta(label)
                logger.info(f"Using enhanced metadata collection for {label}")
            except Exception as e:
                logger.warning(f"Enhanced metadata collection failed: {str(e)}, falling back to standard")
                meta, owner_flag = collect_meta(label)
        else:
            meta, owner_flag = collect_meta(label)
        
        # Add helper function for JSON examples to each field
        for model in meta:
            for field in model["fields"]:
                field["get_json_example"] = lambda f=field: field_json_example(f)
        
        # Render templates
        files = render(label, meta, owner_flag, depth)
        
        # Write files
        app_root = Path(apps.get_app_config(label).path)
        write_app(label, files, force, dry_run)
        
        # Smoke test imports if not in dry run mode
        if not dry_run:
            for module in ['serializers', 'views', 'urls']:
                try:
                    importlib.import_module(f"{label}.{module}")
                except ImportError as e:
                    logger.error(f"Error importing {label}.{module}: {str(e)}")
                    raise
        
        # Run post-processing if enabled
        if post_process and not dry_run:
            formatters = CONFIG.get("formatters", {})
            post_process_app(app_root, formatters)
            
        # Generate diagram if enabled
        use_graph = graph or CONFIG.get("features", {}).get("graph", False)
        if use_graph:
            graph_app(label, meta, True)
            
        logger.info(f"Finished processing app: {label}")
        
    except Exception as e:
        logger.error(f"Error processing app {label}: {str(e)}")
        raise

@dataclass
class FieldInfo:
    """Enhanced information about a model field."""
    name: str
    type: str
    null: bool = False
    blank: bool = False
    unique: bool = False
    related_model: Optional[Any] = None
    related_app: Optional[str] = None
    related_name: Optional[str] = None
    help_text: str = ""
    verbose_name: str = ""
    choices: List[Tuple[Any, str]] = field(default_factory=list)
    is_relation: bool = False
    is_reverse_relation: bool = False
    max_length: Optional[int] = None
    default: Any = None
    editable: bool = True
    auto_created: bool = False
    primary_key: bool = False
    many_to_many: bool = False
    one_to_one: bool = False
    searchable: bool = False
    filterable: bool = False
    
    def __post_init__(self):
        """Set searchable and filterable flags based on field type."""
        # Text fields are searchable
        if self.type in ("CharField", "TextField", "SlugField", "EmailField"):
            self.searchable = True
        
        # Most fields are filterable except large text/binary fields
        if self.type not in ("TextField", "FileField", "ImageField", "BinaryField"):
            self.filterable = True
    
    def get_json_example(self) -> Any:
        """Return an example value for this field suitable for documentation."""
        if self.type == "CharField" or self.type == "TextField":
            return f"Example {self.name}"
        elif self.type in ("IntegerField", "PositiveIntegerField", "AutoField"):
            return 42
        elif self.type in ("FloatField", "DecimalField"):
            return 3.14
        elif self.type == "BooleanField":
            return True
        elif self.type == "DateField":
            return "2025-05-02"
        elif self.type == "DateTimeField":
            return "2025-05-02T12:30:45+00:00"
        elif self.type == "EmailField":
            return "user@example.com"
        elif self.type == "URLField":
            return "https://example.com"
        elif self.type == "UUIDField":
            return "123e4567-e89b-12d3-a456-426655440000"
        elif self.type == "JSONField":
            return {"key": "value"}
        elif self.type in ("ForeignKey", "OneToOneField"):
            return 1
        elif self.type == "ManyToManyField":
            return [1, 2]
        elif self.choices:
            return self.choices[0][0] if self.choices else None
        else:
            return None

@dataclass
class ModelInfo:
    """Information about a Django model."""
    name: str
    app_label: str
    fields: List[FieldInfo] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    has_user_field: bool = False
    has_owner_field: bool = False
    
    @property
    def route_name(self) -> str:
        """Convert model name to URL route name (CamelCase to kebab-case)."""
        return re.sub(r'(?<!^)(?=[A-Z])', '-', self.name).lower()
    
    @property
    def plural_name(self) -> str:
        """Return plural form of the model name for URL routes."""
        if INFLECT_ENGINE:
            return INFLECT_ENGINE.plural(self.name)
        else:
            # Simple pluralization fallback
            if self.name.endswith(('s', 'x', 'z', 'ch', 'sh')):
                return f"{self.name}es"
            elif self.name.endswith('y') and not self.name[-2] in 'aeiou':
                return f"{self.name[:-1]}ies"
            else:
                return f"{self.name}s"
            
    @property
    def api_route(self) -> str:
        """Return the API route for this model."""
        return f"{self.route_name}s"
        
    @property
    def needs_owner_permission(self) -> bool:
        """Check if this model needs owner-based permissions."""
        owner_fields = ('owner', 'user', 'created_by', 'author', 'creator')
        for field in self.fields:
            if field.name in owner_fields:
                return True
        return False
    
    def get_related_models(self) -> List[Tuple[str, str, str]]:
        """Get list of related models as (app, model, field_name) tuples."""
        related = []
        for field in self.fields:
            if field.is_relation and field.related_app and field.related_model:
                model_name = field.related_model.__name__ if hasattr(field.related_model, '__name__') else str(field.related_model)
                related.append((field.related_app, model_name, field.name))
        return related

@dataclass
class AppInfo:
    """Information about a Django app and its models."""
    label: str
    name: str
    models: List[ModelInfo] = field(default_factory=list)
    
    def get_model_names(self) -> List[str]:
        """Get list of model names in this app."""
        return [m.name for m in self.models]
    
    def get_model_by_name(self, name: str) -> Optional[ModelInfo]:
        """Get a model by its name."""
        for model in self.models:
            if model.name == name:
                return model
        return None

@dataclass
class ProjectInfo:
    """Project-wide information about all apps and their dependencies."""
    apps: List[AppInfo] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_app_labels(self) -> List[str]:
        """Get list of app labels."""
        return [a.label for a in self.apps]
    
    def get_app_by_label(self, label: str) -> Optional[AppInfo]:
        """Get an app by its label."""
        for app in self.apps:
            if app.label == label:
                return app
        return None
    
    def get_model_by_path(self, app_label: str, model_name: str) -> Optional[ModelInfo]:
        """Get a model by its app label and name."""
        app = self.get_app_by_label(app_label)
        if app:
            return app.get_model_by_name(model_name)
        return None
    
    def find_dependencies(self, app_label: str) -> List[str]:
        """Find app labels that this app depends on."""
        dependencies = []
        app = self.get_app_by_label(app_label)
        if not app:
            return dependencies
            
        for model in app.models:
            for field in model.fields:
                if field.is_relation and field.related_app and field.related_app != app_label:
                    if field.related_app not in dependencies:
                        dependencies.append(field.related_app)
        
        return dependencies
    
    def find_dependent_apps(self, app_label: str) -> List[str]:
        """Find apps that depend on this app."""
        dependents = []
        
        for app in self.apps:
            if app.label == app_label:
                continue
                
            for model in app.models:
                for field in model.fields:
                    if field.is_relation and field.related_app == app_label:
                        if app.label not in dependents:
                            dependents.append(app.label)
                            break
        
        return dependents
    
    def has_circular_dependencies(self) -> bool:
        """Check if there are circular dependencies between apps."""
        # Build dependency graph
        graph = {}
        for app_label in self.get_app_labels():
            graph[app_label] = self.find_dependencies(app_label)
        
        # Check for cycles using DFS
        visited = set()
        path = set()
        
        def dfs(node):
            if node in path:
                return True  # Found a cycle
                
            if node in visited:
                return False
                
            visited.add(node)
            path.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
                    
            path.remove(node)
            return False
        
        for app_label in graph:
            if dfs(app_label):
                return True
                
        return False

def check_app_dependencies(targets: List[str]) -> None:
    """Check for circular dependencies between apps."""
    logger.info("Checking for circular dependencies...")
    
    try:
        app_dependencies = {}
        
        # Build dependency graph
        for label in targets:
            app_config = apps.get_app_config(label)
            dependencies = []
            
            for model in app_config.get_models():
                for field in model._meta.get_fields():
                    if field.is_relation and hasattr(field, 'related_model') and field.related_model:
                        related_app = field.related_model._meta.app_label
                        if related_app != label and related_app not in dependencies:
                            dependencies.append(related_app)
            
            app_dependencies[label] = dependencies
        
        # Check for cycles
        cycles = detect_circular_dependencies(app_dependencies)
        if cycles:
            logger.warning("⚠️  Circular dependencies detected between apps:")
            for cycle in cycles:
                logger.warning(f"  {' -> '.join(cycle)}")
            logger.warning("This may cause issues with serializer imports in generated files.")
            logger.warning("Consider using string references for related models in circular dependencies.")
        
    except Exception as e:
        logger.error(f"Error checking app dependencies: {str(e)}")

def field_json_example(field: Dict) -> Any:
    """Return an example value for a field suitable for documentation."""
    field_type = field.get("type", "")
    field_name = field.get("name", "")
    
    if field_type in ("CharField", "TextField"):
        return f"Example {field_name}"
    elif field_type in ("IntegerField", "PositiveIntegerField", "AutoField"):
        return 42
    elif field_type in ("FloatField", "DecimalField"):
        return 3.14
    elif field_type == "BooleanField":
        return True
    elif field_type == "DateField":
        return "2025-05-02"
    elif field_type == "DateTimeField":
        return "2025-05-02T12:30:45+00:00"
    elif field_type == "EmailField":
        return "user@example.com"
    elif field_type == "URLField":
        return "https://example.com"
    elif field_type == "UUIDField":
        return "123e4567-e89b-12d3-a456-426655440000"
    elif field_type == "JSONField":
        return {"key": "value"}
    elif field_type in ("ForeignKey", "OneToOneField"):
        return 1
    elif field_type == "ManyToManyField":
        return [1, 2]
    else:
        return None

def generate_enhanced_docs(app_labels: List[str]) -> None:
    """Generate enhanced API documentation."""
    logger.info("Generating enhanced API documentation...")
    
    try:
        app_infos = []
        for label in app_labels:
            try:
                meta, _ = enhanced_collect_meta(label)
                app_infos.append({
                    "app_config": apps.get_app_config(label),
                    "model_infos": meta
                })
            except Exception as e:
                logger.warning(f"Error collecting enhanced metadata for {label}: {str(e)}")
                logger.warning(f"Falling back to standard metadata collection for {label}")
                meta, _ = collect_meta(label)
                app_infos.append({
                    "app_config": apps.get_app_config(label),
                    "model_infos": meta
                })
        
        generate_api_report(app_infos)
        logger.info("✅ Enhanced API documentation generated")
    except Exception as e:
        logger.error(f"Error generating enhanced documentation: {str(e)}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())

def detect_circular_dependencies(app_dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """
    Find all circular dependencies between apps.
    
    Args:
        app_dependencies: Dictionary mapping app labels to their dependencies
        
    Returns:
        List of cycles, where each cycle is a list of app labels
    """
    cycles = []
    
    def find_cycles_from_node(start_node):
        stack = [(start_node, [start_node])]
        while stack:
            node, path = stack.pop()
            
            # Get neighbors
            neighbors = app_dependencies.get(node, [])
            
            for neighbor in neighbors:
                if neighbor == start_node:
                    # Found a cycle
                    cycle = path.copy()
                    cycle.append(neighbor)
                    # Check if this cycle is already in our list (regardless of starting point)
                    cycle_exists = False
                    for existing_cycle in cycles:
                        if set(cycle) == set(existing_cycle):
                            cycle_exists = True
                            break
                    if not cycle_exists:
                        cycles.append(cycle)
                elif neighbor not in path:
                    new_path = path.copy()
                    new_path.append(neighbor)
                    stack.append((neighbor, new_path))
    
    for app_label in app_dependencies:
        find_cycles_from_node(app_label)
        
    return cycles

def enhance_jinja_env(env: Environment) -> Environment:
    """Add additional filters and globals to the Jinja environment."""
    # The base jenv already has these filters, but this function provides
    # a way to enhance any Jinja environment that might need these filters.
    # We'll only add them if they don't already exist.
    if "tojson" not in env.filters:
        env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)
    
    if "pluralize" not in env.filters:
        if INFLECT_ENGINE:
            env.filters["pluralize"] = INFLECT_ENGINE.plural
        else:
            # Simple pluralization if inflect not available
            def simple_pluralize(value):
                if value.endswith('s') or value.endswith('x') or value.endswith('z'):
                    return value + 'es'
                elif value.endswith('y') and value[-2] not in 'aeiou':
                    return value[:-1] + 'ies'
                else:
                    return value + 's'
            env.filters["pluralize"] = simple_pluralize
    
    return env

api_docs_template = """
# {{ app_label|capitalize }} API Documentation
_Generated: {{ timestamp }}_

## Overview

This document provides comprehensive documentation for the {{ app_label }} API endpoints.

## Base URL

All endpoints are prefixed with `/{{ api_base }}/`.

{% for m in models %}
## {{ m.name }}

**Endpoint**: `/{{ api_base }}/{{ m.route }}/`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
{% for field in m.fields %}
| `{{ field.name }}` | `{{ field.type }}` | {{ "Yes" if not field.null else "No" }} | {{ field.description or field.name }} |
{% endfor %}

### Example Object

```json
{
{% for field in m.fields %}
    "{{ field.name }}": {{ field.get_json_example() | tojson }}{% if not loop.last %},{% endif %}
{% endfor %}
}
```

### Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/{{ api_base }}/{{ m.route }}/` | List all {{ m.name }} objects |
| `POST` | `/{{ api_base }}/{{ m.route }}/` | Create a new {{ m.name }} |
| `GET` | `/{{ api_base }}/{{ m.route }}/{id}/` | Retrieve a specific {{ m.name }} |
| `PUT` | `/{{ api_base }}/{{ m.route }}/{id}/` | Update a {{ m.name }} |
| `PATCH` | `/{{ api_base }}/{{ m.route }}/{id}/` | Partially update a {{ m.name }} |
| `DELETE` | `/{{ api_base }}/{{ m.route }}/{id}/` | Delete a {{ m.name }} |

{% if m.filters %}
### Supported Filters

You can filter results using the following query parameters:

{% for field in m.filters %}
- `{{ field }}`: Filter by {{ field }}
{% endfor %}

Example: `/{{ api_base }}/{{ m.route }}/?{{ m.filters[0] }}=value`
{% endif %}

{% if m.search %}
### Search Fields

You can search across these fields by adding `?search=query` to the URL:

{% for field in m.search %}
- `{{ field }}`
{% endfor %}

Example: `/{{ api_base }}/{{ m.route }}/?search=search_term`
{% endif %}

{% endfor %}
"""

def generate_api_report(app_infos: List[Dict], output_dir: Path = DOCS_DIR) -> Path:
    """
    Generate a comprehensive API report including examples and documentation.
    
    Args:
        app_infos: List of app information dictionaries
        output_dir: Directory to write the report
        
    Returns:
        Path to the generated report file
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    report_path = output_dir / "api_documentation.md"
    
    env = jenv()
    env = enhance_jinja_env(env)
    
    content = ["# API Documentation\n"]
    content.append(f"_Generated: {dt.datetime.now().isoformat(timespec='seconds')}_\n")
    content.append("## Table of Contents\n")
    
    # Generate table of contents
    for app_info in app_infos:
        app_name = app_info['app_config'].name
        app_label = app_name.split('.')[-1]
        content.append(f"- [{app_label.capitalize()}](#{app_label.lower()})")
        
    # Generate documentation for each app
    for app_info in app_infos:
        app_name = app_info['app_config'].name
        app_label = app_name.split('.')[-1]
        model_infos = app_info.get('model_infos', [])
        
        content.append(f"\n<a name='{app_label.lower()}'></a>")
        
        # Render app-specific template
        template = env.from_string(api_docs_template)
        rendered = template.render(
            app_label=app_label,
            timestamp=dt.datetime.now().isoformat(timespec='seconds'),
            api_base=CONFIG["api_base"],
            models=model_infos
        )
        
        content.append(rendered)
    
    # Write the report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
        
    logger.info(f"API documentation generated at {report_path}")
    return report_path

def convert_field_info_to_dict(field_info: FieldInfo) -> Dict:
    """Convert a FieldInfo dataclass to the dictionary format used by existing code."""
    return {
        "name": field_info.name,
        "type": field_info.type,
        "description": field_info.help_text or field_info.verbose_name,
        "is_relation": field_info.is_relation,
        "is_reverse_relation": field_info.is_reverse_relation,
        "related_model": field_info.related_model,
        "null": field_info.null,
        "blank": field_info.blank,
        "unique": field_info.unique,
        "searchable": field_info.searchable,
        "filterable": field_info.filterable
    }

def convert_model_infos_to_dict(model_infos: List[Any]) -> List[Dict]:
    """Convert model info objects to the dictionary format used by existing code."""
    result = []
    
    for model_info in model_infos:
        fields = [convert_field_info_to_dict(f) for f in model_info.fields]
        
        # Determine searchable and filterable fields
        search_fields = [f.name for f in model_info.fields if f.searchable]
        filter_fields = [f.name for f in model_info.fields if f.filterable]
        display_fields = get_admin_list_display(model_info.fields)
        
        owner_field = None
        has_owner = False
        owner_fields = ('owner', 'user', 'created_by', 'author', 'creator')
        for field in model_info.fields:
            if field.name in owner_fields:
                has_owner = True
                owner_field = field.name
                break
        
        result.append({
            "name": model_info.name,
            "route": model_info.name.lower(),
            "fields": fields,
            "search": search_fields or ["id"],
            "filters": filter_fields,
            "display": display_fields or ["id"],
            "owner": has_owner,
            "owner_field": owner_field
        })
    
    return result

def extract_field_info(field) -> FieldInfo:
    """Extract detailed information about a model field."""
    field_info = FieldInfo(
        name=field.name,
        type=type(field).__name__,
        null=getattr(field, 'null', False),
        blank=getattr(field, 'blank', False),
        unique=getattr(field, 'unique', False),
        help_text=str(getattr(field, 'help_text', '')),
        verbose_name=str(getattr(field, 'verbose_name', '')),
        is_relation=field.is_relation if hasattr(field, 'is_relation') else False,
        max_length=getattr(field, 'max_length', None),
        editable=getattr(field, 'editable', True),
        primary_key=getattr(field, 'primary_key', False),
        auto_created=getattr(field, 'auto_created', False),
    )
    
    # Handle choices if they exist
    if hasattr(field, 'choices') and field.choices:
        field_info.choices = field.choices
    
    # Handle default value
    if hasattr(field, 'has_default') and field.has_default():
        default_value = field.get_default()
        # Skip callable defaults which can't be easily represented
        if not callable(default_value):
            field_info.default = default_value
    
    # Handle relation fields
    if field.is_relation:
        field_info.is_relation = True
        related_model = field.related_model
        
        if related_model:
            field_info.related_model = related_model
            field_info.related_app = related_model._meta.app_label
            
        if hasattr(field, 'remote_field') and hasattr(field.remote_field, 'related_name'):
            field_info.related_name = field.remote_field.related_name
            
        # Set relationship type flags
        if isinstance(field, models.ManyToManyField):
            field_info.many_to_many = True
        elif isinstance(field, models.OneToOneField):
            field_info.one_to_one = True
            
        # Check for reverse relations
        reverse_relation_types = ("ManyToOneRel", "ManyToManyRel", "OneToOneRel")
        if field_info.type in reverse_relation_types:
            field_info.is_reverse_relation = True
            
    return field_info

def get_admin_list_display(fields: List[FieldInfo], max_fields: int = 5) -> List[str]:
    """Generate a suitable list_display for the admin."""
    display = []
    
    # Always include the primary key
    pk_field = next((f.name for f in fields if f.primary_key), "id")
    display.append(pk_field)
    
    # Add name/title fields if they exist
    common_display_fields = ('name', 'title', 'slug', 'email', 'username')
    for field_name in common_display_fields:
        if field_name in [f.name for f in fields] and len(display) < max_fields:
            display.append(field_name)
            
    # Add timestamp fields
    timestamp_fields = ('created_at', 'updated_at', 'date_joined', 'last_modified')
    for field_name in timestamp_fields:
        if field_name in [f.name for f in fields] and len(display) < max_fields:
            display.append(field_name)
            
    # Add any string fields until we reach the limit
    for field in fields:
        if (field.searchable and field.name not in display and len(display) < max_fields):
            display.append(field.name)
            
    # If we still don't have enough, add other fields
    if len(display) < max_fields:
        for field in fields:
            if field.name not in display and not field.many_to_many and len(display) < max_fields:
                display.append(field.name)
                
    return display

if __name__ == "__main__":
    sys.exit(main())
