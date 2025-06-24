#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main script for the Backend Documentation Generator.
This script orchestrates the extraction and documentation process.

Author: nanthiniSanthanam
Generated: 2025-05-04 04:56:14
"""

import os
import sys
import logging
import argparse
import time
import json
from datetime import datetime
from pathlib import Path

# Import configuration
import config

# Import extractors
from extractors.model_extractor import ModelExtractor
from extractors.api_analyzer import ApiAnalyzer
from extractors.serializer_inspector import SerializerInspector
from extractors.authentication_analyzer import AuthenticationAnalyzer
from extractors.runtime_tester import RuntimeTester

# Import documentation generators
from generators.markdown_generator import MarkdownGenerator
from generators.html_generator import HtmlGenerator
from generators.typescript_generator import TypeScriptGenerator
from generators.react_hooks_generator import ReactHooksGenerator

# Import utilities
from utils.django_setup import setup_django_environment
from utils.logger import setup_logger


class BackendDocumentationGenerator:
    """Main class for generating backend documentation"""

    def __init__(self, config_override=None):
        """Initialize the documentation generator with configuration"""
        self.start_time = time.time()
        self.config = config

        # Apply any configuration overrides
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)

        # Setup logging
        self.logger = setup_logger(self.config.VERBOSITY)

        # Create output directory if it doesn't exist
        self.output_dir = Path(self.config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize extractors
        self.extractors = {
            'models': ModelExtractor(self.config),
            'apis': ApiAnalyzer(self.config),
            'serializers': SerializerInspector(self.config),
            'authentication': AuthenticationAnalyzer(self.config),
            'runtime': RuntimeTester(self.config)
        }

        # Initialize generators
        self.generators = {
            'markdown': MarkdownGenerator(self.config),
            'html': HtmlGenerator(self.config),
            'typescript': TypeScriptGenerator(self.config),
            'react_hooks': ReactHooksGenerator(self.config)
        }

        # Initialize data store for extracted information
        self.data = {
            'project_info': {
                'name': '',
                'apps': [],
                'extraction_date': datetime.now().isoformat(),
                'config': {k: v for k, v in vars(self.config).items() if not k.startswith('__')}
            },
            'models': {},
            'apis': {},
            'serializers': {},
            'authentication': {},
            'runtime_tests': {},
            'frontend_integration': {}
        }

    def run(self):
        """Run the complete documentation generation process"""
        self.logger.info("Starting backend documentation generation")

        # Step 1: Setup Django environment for static analysis
        self._setup_django()

        # Step 2: Extract project information
        self._extract_project_info()

        # Step 3: Run all extractors
        self._run_extractors()

        # Step 4: Generate documentation
        self._generate_documentation()

        # Step 5: Create index and navigation
        self._create_index()

        # Report completion
        elapsed_time = time.time() - self.start_time
        self.logger.info(
            f"Documentation generation completed in {elapsed_time:.2f} seconds")
        self.logger.info(f"Output available at: {self.output_dir.absolute()}")

        return self.output_dir

    def _setup_django(self):
        """Set up Django environment for static analysis"""
        self.logger.info("Setting up Django environment")
        try:
            setup_django_environment(self.config.BACKEND_PROJECT_PATH)
            self.logger.info("Django environment setup successful")
        except Exception as e:
            self.logger.error(f"Failed to set up Django environment: {str(e)}")
            sys.exit(1)

    def _extract_project_info(self):
        """Extract basic project information"""
        self.logger.info("Extracting project information")

        # Get project name from directory name if not specified
        project_path = Path(self.config.BACKEND_PROJECT_PATH)
        self.data['project_info']['name'] = project_path.name

        # Get Django apps (filtered by inclusion/exclusion settings)
        from django.apps import apps

        all_apps = [app.name for app in apps.get_app_configs()]

        # Apply filters
        filtered_apps = all_apps
        if self.config.INCLUDED_APPS:
            filtered_apps = [
                app for app in all_apps if app in self.config.INCLUDED_APPS]

        # Apply exclusions
        filtered_apps = [
            app for app in filtered_apps if app not in self.config.EXCLUDED_APPS]

        self.data['project_info']['apps'] = filtered_apps
        self.logger.info(f"Found {len(filtered_apps)} apps to document")

    def _run_extractors(self):
        """Run all extractors to gather information"""
        self.logger.info("Running extractors")

        # Models extraction
        self.logger.info("Extracting model information")
        try:
            self.data['models'] = self.extractors['models'].extract()
        except Exception as e:
            self.logger.error(f"Error extracting models: {str(e)}")

        # API endpoints extraction
        self.logger.info("Extracting API endpoint information")
        try:
            self.data['apis'] = self.extractors['apis'].extract()
        except Exception as e:
            self.logger.error(f"Error extracting APIs: {str(e)}")

        # Serializers extraction
        self.logger.info("Extracting serializer information")
        try:
            self.data['serializers'] = self.extractors['serializers'].extract()
        except Exception as e:
            self.logger.error(f"Error extracting serializers: {str(e)}")

        # Authentication extraction
        self.logger.info("Extracting authentication information")
        try:
            self.data['authentication'] = self.extractors['authentication'].extract()
        except Exception as e:
            self.logger.error(f"Error extracting authentication: {str(e)}")

        # Runtime API testing
        if self.config.BACKEND_URL:
            self.logger.info("Running runtime API tests")
            try:
                self.data['runtime_tests'] = self.extractors['runtime'].extract(
                    apis=self.data['apis'],
                    auth_info=self.data['authentication']
                )
            except Exception as e:
                self.logger.error(f"Error running API tests: {str(e)}")
        else:
            self.logger.warning(
                "Skipping runtime API tests (BACKEND_URL not configured)")

        # Save raw extracted data for reference
        raw_data_path = self.output_dir / "raw_extracted_data.json"
        with open(raw_data_path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)

        self.logger.info(f"Raw extracted data saved to {raw_data_path}")

    def _generate_documentation(self):
        """Generate documentation in specified formats"""
        self.logger.info("Generating documentation")

        # Generate Markdown documentation
        if self.config.OUTPUT_FORMAT in ["markdown", "all"]:
            self.logger.info("Generating Markdown documentation")
            markdown_dir = self.output_dir / "markdown"
            markdown_dir.mkdir(exist_ok=True)
            self.generators['markdown'].generate(self.data, markdown_dir)

        # Generate HTML documentation
        if self.config.OUTPUT_FORMAT in ["html", "all"]:
            self.logger.info("Generating HTML documentation")
            html_dir = self.output_dir / "html"
            html_dir.mkdir(exist_ok=True)
            self.generators['html'].generate(self.data, html_dir)

        # Generate TypeScript interfaces
        if self.config.GENERATE_TYPESCRIPT:
            self.logger.info("Generating TypeScript interfaces")
            typescript_dir = self.output_dir / "typescript"
            typescript_dir.mkdir(exist_ok=True)
            self.generators['typescript'].generate(
                models=self.data['models'],
                apis=self.data['apis'],
                serializers=self.data['serializers'],
                output_dir=typescript_dir
            )

        # Generate React hooks
        if self.config.GENERATE_REACT_HOOKS:
            self.logger.info("Generating React hook examples")
            hooks_dir = self.output_dir / "react_hooks"
            hooks_dir.mkdir(exist_ok=True)
            self.generators['react_hooks'].generate(
                apis=self.data['apis'],
                auth_info=self.data['authentication'],
                output_dir=hooks_dir
            )

    def _create_index(self):
        """Create index and navigation for the documentation"""
        self.logger.info("Creating documentation index and navigation")

        # Create an index file that links to all sections
        index_path = self.output_dir / "index.html"

        # Basic index HTML template
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.data['project_info']['name']} Backend Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .card {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .formats {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        .formats a {{
            padding: 5px 10px;
            background: #f5f5f5;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }}
        .formats a:hover {{
            background: #e0e0e0;
        }}
        .extraction-info {{
            font-size: 0.9em;
            color: #666;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <h1>{self.data['project_info']['name']} Backend Documentation</h1>
    <p>Comprehensive documentation of backend components for frontend development.</p>
    
    <div class="card">
        <h2>Documentation Formats</h2>
        <div class="formats">
            <a href="./html/index.html">HTML Documentation</a>
            <a href="./markdown/README.md">Markdown Documentation</a>
            <a href="./typescript/index.ts">TypeScript Interfaces</a>
            <a href="./react_hooks/index.tsx">React Hook Examples</a>
            <a href="./raw_extracted_data.json">Raw JSON Data</a>
        </div>
    </div>
    
    <div class="card">
        <h2>Documentation Sections</h2>
        <ul>
            <li><a href="./html/project_overview.html">Project Overview</a></li>
            <li><a href="./html/models_and_database.html">Models and Database Schema</a></li>
            <li><a href="./html/api_endpoints.html">API Endpoints</a></li>
            <li><a href="./html/authentication.html">Authentication and Authorization</a></li>
            <li><a href="./html/frontend_integration.html">Frontend Integration Guide</a></li>
        </ul>
    </div>
    
    <div class="extraction-info">
        <p>Extracted from {self.config.BACKEND_PROJECT_PATH}</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Backend Documentation Generator v1.0.0</p>
    </div>
</body>
</html>
"""

        with open(index_path, 'w') as f:
            f.write(index_html)

        self.logger.info(f"Documentation index created at {index_path}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Backend Documentation Generator")

    parser.add_argument("--backend-path", dest="BACKEND_PROJECT_PATH",
                        help="Path to Django project root directory")

    parser.add_argument("--backend-url", dest="BACKEND_URL",
                        help="URL of running backend server for runtime tests")

    parser.add_argument("--output-dir", dest="OUTPUT_DIR",
                        help="Directory where documentation will be generated")

    parser.add_argument("--format", dest="OUTPUT_FORMAT", choices=["markdown", "html", "json", "all"],
                        help="Output format for documentation")

    parser.add_argument("--detail-level", dest="DETAIL_LEVEL", choices=["basic", "standard", "comprehensive"],
                        help="Level of detail for documentation")

    parser.add_argument("--username", dest="AUTH_USERNAME",
                        help="Username for testing authenticated endpoints")

    parser.add_argument("--password", dest="AUTH_PASSWORD",
                        help="Password for testing authenticated endpoints")

    parser.add_argument("--token", dest="AUTH_TOKEN",
                        help="JWT token for testing authenticated endpoints")

    parser.add_argument("--verbose", "-v", action="count", default=0, dest="VERBOSITY",
                        help="Increase verbosity (can be used multiple times)")

    parser.add_argument("--no-typescript", dest="GENERATE_TYPESCRIPT", action="store_false",
                        help="Disable TypeScript interface generation")

    parser.add_argument("--no-examples", dest="INCLUDE_EXAMPLES", action="store_false",
                        help="Disable API response example generation")

    parser.add_argument("--no-hooks", dest="GENERATE_REACT_HOOKS", action="store_false",
                        help="Disable React hook example generation")

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Create dictionary of non-None arguments to override config
    config_override = {k: v for k, v in vars(args).items() if v is not None}

    # Run the documentation generator
    generator = BackendDocumentationGenerator(config_override)
    output_path = generator.run()

    print(
        f"Documentation generation complete! Output available at: {output_path}")
