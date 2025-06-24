# Django Backend Analyzer

A tool for analyzing Django backend codebases to facilitate frontend integration.

## Overview

The Django Backend Analyzer is a comprehensive tool designed to analyze Django backend codebases and provide useful information for frontend developers. It helps bridge the gap between frontend and backend development by generating documentation, identifying API endpoints, and detecting potential compatibility issues.

## Features

- **Django Model Analysis**: Extract information about models, fields, and relationships
- **Serializer Analysis**: Identify REST Framework serializers and their fields
- **View Analysis**: Extract information about views and viewsets
- **URL Analysis**: Map URLs to views and identify API endpoints
- **Compatibility Checking**: Detect potential issues between frontend and backend
- **Documentation Generation**: Generate documentation for API endpoints and data models
- **Optional TypeScript Interface Generation**: Generate TypeScript interfaces from Django models
- **Optional OpenAPI Schema Generation**: Generate OpenAPI schema from Django REST Framework APIs

## Installation

```bash
# Basic installation
pip install django-backend-analyzer

# With extra dependencies for YAML and TOML support
pip install "django-backend-analyzer[full]"

# Development installation
git clone https://github.com/example/django-backend-analyzer.git
cd django-backend-analyzer
pip install -e ".[dev]"
```

## Usage

```bash
# Basic usage
backend-analyzer --backend_path /path/to/django/project

# Generate TypeScript interfaces
backend-analyzer --backend_path /path/to/django/project --output_typescript

# Generate OpenAPI schema
backend-analyzer --backend_path /path/to/django/project --output_openapi

# Full analysis with all outputs
backend-analyzer \
  --backend_path /path/to/django/project \
  --output_typescript \
  --output_openapi \
  --verbose \
  --include_code_samples
```

## Configuration

You can configure the analyzer using a configuration file in JSON, TOML, or YAML format:

```bash
# Generate a sample configuration
backend-analyzer --generate_config

# Use the configuration file
backend-analyzer --config_file backend_analyzer_config.json
```

## License

MIT 