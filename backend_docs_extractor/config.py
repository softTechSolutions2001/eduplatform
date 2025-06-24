#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration file for backend documentation generator.
Customize these settings before running the extraction scripts.

Author: nanthiniSanthanam
Generated: 2025-05-04 04:56:14
"""

import os
from pathlib import Path

# ========== REQUIRED CONFIGURATION ==========
# Path to Django project root directory
BACKEND_PROJECT_PATH = "C:/path/to/your/django/project"

# URL of running backend server for runtime API testing
BACKEND_URL = "http://localhost:8000"

# ========== OUTPUT CONFIGURATION ==========
# Directory where documentation will be generated
OUTPUT_DIR = "./backend_docs"

# Output format options: "markdown", "html", "json", or "all"
OUTPUT_FORMAT = "all"

# ========== AUTHENTICATION CONFIGURATION ==========
# Credentials for testing authenticated endpoints
AUTH_USERNAME = "test_user"
AUTH_PASSWORD = "test_password"
# Alternative: JWT token if your API uses token-based auth
AUTH_TOKEN = ""

# ========== SCOPE CONFIGURATION ==========
# Django apps to include (empty list means all apps)
INCLUDED_APPS = []

# Django apps to exclude from analysis
EXCLUDED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
                 "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles"]

# ========== ANALYSIS DETAIL CONFIGURATION ==========
# Level of detail: "basic", "standard", "comprehensive"
DETAIL_LEVEL = "comprehensive"

# ========== FRONTEND INTEGRATION OPTIONS ==========
# Generate TypeScript interfaces for models and API responses
GENERATE_TYPESCRIPT = True

# Include sample API requests and responses
INCLUDE_EXAMPLES = True

# Generate React hook examples for API calls
GENERATE_REACT_HOOKS = True

# ========== DATABASE CONFIGURATION ==========
# Override Django's database settings (optional)
DATABASE_CONFIG = {
    # If empty, uses Django's settings
}

# ========== RUNTIME TESTING CONFIGURATION ==========
# Maximum number of items to fetch for list endpoints
MAX_ITEMS_PER_ENDPOINT = 5

# Whether to test error scenarios (e.g., invalid inputs)
TEST_ERROR_SCENARIOS = True

# Timeout for API requests in seconds
REQUEST_TIMEOUT = 10

# ========== DOCUMENTATION STYLE ==========
# Theme for HTML output: "light", "dark", "auto"
HTML_THEME = "auto"

# Organization sections (customize order and inclusion)
DOCUMENTATION_SECTIONS = [
    "project_overview",
    "models_and_database",
    "api_endpoints",
    "authentication",
    "frontend_integration",
    "typescript_interfaces"
]

# ========== ADVANCED CONFIGURATION ==========
# Custom extractors (paths to Python modules implementing the extractor interface)
CUSTOM_EXTRACTORS = []

# Path to custom templates for documentation generation
CUSTOM_TEMPLATES_DIR = ""

# Verbosity level for logging: 0 (quiet), 1 (normal), 2 (verbose), 3 (debug)
VERBOSITY = 1
