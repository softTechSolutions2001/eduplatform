#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML Documentation Generator for Backend API Documentation

This module generates comprehensive HTML documentation from extracted backend information.
It creates a set of interlinked HTML pages with navigation, syntax highlighting, and interactive
API testing features.

Features:
- Responsive HTML documentation with mobile-friendly design
- Dark/light theme switching based on user preference
- Interactive API endpoint testing interface
- Syntax highlighting for code examples
- Search functionality across documentation
- Comprehensive navigation with sidebar
- Properly structured content with sections and subsections

Configuration Variables (set in config.py):
- HTML_THEME: Theme for HTML output ("light", "dark", "auto") - Default: "auto"
- INCLUDE_EXAMPLES: Whether to include API examples in documentation - Default: True
- DETAIL_LEVEL: Controls amount of detail ("basic", "standard", "comprehensive") - Default: "standard"
- BACKEND_URL: URL of backend server for interactive API testing - Default: ""
- DOCUMENTATION_SECTIONS: Sections to include in documentation - Default: All sections
- CUSTOM_TEMPLATES_DIR: Path to custom HTML templates (optional) - Default: None
- OUTPUT_DIR: Directory where documentation will be generated - Default: "./backend_docs"

Generated Files:
- index.html: Main entry point for documentation
- project_overview.html: System architecture and project overview
- models_and_database.html: Database schema and model relationships
- api_endpoints.html: API endpoints with testing capability
- authentication.html: Auth mechanisms and requirements
- frontend_integration.html: Guide for frontend developers
- typescript_interfaces.html: TypeScript interfaces documentation

Generated Assets:
- resources/css/main.css: Main styling
- resources/css/prism.css: Syntax highlighting
- resources/js/main.js: Core functionality
- resources/js/prism.js: Syntax highlighting
- resources/js/api-testing.js: API testing functionality

Current Date and Time (UTC): 2025-05-04 17:01:45
Author: nanthiniSanthanam
Version: 1.0.0
"""

import logging
import json
import shutil
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class HtmlGenerator:
    """Generate HTML documentation from extracted backend information"""

    def __init__(self, config):
        """Initialize with configuration

        Args:
            config: Configuration object with document generation settings
        """
        self.config = config
        self.detail_level = getattr(config, 'DETAIL_LEVEL', 'standard')
        self.html_theme = getattr(config, 'HTML_THEME', 'auto')
        self.custom_templates_dir = getattr(
            config, 'CUSTOM_TEMPLATES_DIR', None)
        self.include_examples = getattr(config, 'INCLUDE_EXAMPLES', True)
        self.backend_url = getattr(config, 'BACKEND_URL', '')

        # Default sections if not specified
        self.documentation_sections = getattr(config, 'DOCUMENTATION_SECTIONS', [
            "project_overview",
            "models_and_database",
            "api_endpoints",
            "authentication",
            "frontend_integration",
            "typescript_interfaces"
        ])

        # Resources directory embedded in the package
        self.resources_dir = Path(__file__).parent / 'resources'

        # Search data for documentation search functionality
        self.search_data = []

    def generate(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate HTML documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        logger.info("Generating HTML documentation")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create resources directory and copy assets
        self._setup_resources(output_dir)

        # Create index.html (main page)
        self._generate_index(data, output_dir)

        # Generate sections based on configuration
        for section in self.documentation_sections:
            if section == 'project_overview':
                self._generate_project_overview(data, output_dir)
            elif section == 'models_and_database':
                self._generate_models_documentation(data, output_dir)
            elif section == 'api_endpoints':
                self._generate_api_documentation(data, output_dir)
            elif section == 'authentication':
                self._generate_authentication_documentation(data, output_dir)
            elif section == 'frontend_integration':
                self._generate_frontend_integration(data, output_dir)
            elif section == 'typescript_interfaces':
                self._generate_typescript_overview(data, output_dir)

        # Generate search index
        self._generate_search_data(output_dir)

        logger.info(f"HTML documentation generated in {output_dir}")

    def _setup_resources(self, output_dir: Path) -> None:
        """Set up resources directory with CSS, JS and images

        Args:
            output_dir: Directory where HTML files will be generated
        """
        # Create resources directory
        resources_dir = output_dir / "resources"
        resources_dir.mkdir(exist_ok=True)

        # Create necessary subdirectories
        css_dir = resources_dir / "css"
        js_dir = resources_dir / "js"
        img_dir = resources_dir / "img"

        css_dir.mkdir(exist_ok=True)
        js_dir.mkdir(exist_ok=True)
        img_dir.mkdir(exist_ok=True)

        # Generate CSS files
        self._generate_main_css(css_dir)
        self._generate_prism_css(css_dir)

        # Generate JavaScript files
        self._generate_main_js(js_dir)
        self._generate_prism_js(js_dir)
        self._generate_api_testing_js(js_dir)

        # Copy any static assets from templates directory if it exists
        if self.custom_templates_dir:
            custom_resources = Path(self.custom_templates_dir) / "resources"
            if custom_resources.exists():
                # Copy CSS files
                for css_file in custom_resources.glob('css/*.css'):
                    shutil.copy(css_file, css_dir)

                # Copy JS files
                for js_file in custom_resources.glob('js/*.js'):
                    shutil.copy(js_file, js_dir)

                # Copy image files
                for img_file in custom_resources.glob('img/*'):
                    shutil.copy(img_file, img_dir)

        logger.info("Set up resources directory for HTML documentation")

    def _generate_main_css(self, css_dir: Path) -> None:
        """Generate main CSS file for the HTML documentation

        Args:
            css_dir: Directory where CSS files will be created
        """
        main_css = css_dir / "main.css"

        css_content = """
/*
 * Main documentation styling
 * Backend Documentation Generator
 * Generated: 2025-05-04 17:01:45
 */

:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --text-color: #334155;
    --bg-color: #ffffff;
    --card-bg: #f8fafc;
    --border-color: #e2e8f0;
    --code-bg: #f1f5f9;
    --heading-color: #1e293b;
    --sidebar-bg: #f1f5f9;
    --sidebar-active: #e2e8f0;
    --badge-bg: #e2e8f0;
    --badge-color: #1e293b;
}

/* Dark theme */
[data-theme="dark"] {
    --primary-color: #3b82f6;
    --primary-hover: #60a5fa;
    --text-color: #e2e8f0;
    --bg-color: #0f172a;
    --card-bg: #1e293b;
    --border-color: #334155;
    --code-bg: #1e293b;
    --heading-color: #f8fafc;
    --sidebar-bg: #1e293b;
    --sidebar-active: #334155;
    --badge-bg: #334155;
    --badge-color: #e2e8f0;
}

/* Base styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
    margin: 0;
    padding: 0;
    transition: background-color 0.3s ease, color 0.3s ease;
}

.container {
    display: flex;
    min-height: 100vh;
}

/* Sidebar styles */
.sidebar {
    width: 280px;
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
    padding: 1rem;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    transition: transform 0.3s ease;
    z-index: 100;
}

.sidebar-header {
    padding: 1rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.sidebar h1 {
    font-size: 1.5rem;
    margin: 0;
    color: var(--heading-color);
}

.sidebar-nav {
    list-style: none;
    padding: 0;
    margin: 0;
}

.sidebar-nav li {
    margin-bottom: 0.5rem;
}

.sidebar-nav a {
    display: block;
    padding: 0.5rem 1rem;
    color: var(--text-color);
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.sidebar-nav a:hover, .sidebar-nav a.active {
    background-color: var(--sidebar-active);
}

.sidebar-nav .section-title {
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    padding-left: 1rem;
    color: var(--heading-color);
}

.sidebar-nav .subsection {
    margin-left: 1rem;
}

.sidebar-toggle {
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 101;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    width: 40px;
    height: 40px;
    cursor: pointer;
    font-size: 1.5rem;
    line-height: 1;
}

/* Main content styles */
.content {
    flex: 1;
    padding: 2rem;
    margin-left: 280px;
    max-width: 100%;
}

.content-inner {
    max-width: 1200px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--heading-color);
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

h1 {
    font-size: 2.25rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

h2 {
    font-size: 1.8rem;
    margin-top: 2rem;
}

h3 {
    font-size: 1.5rem;
}

h4 {
    font-size: 1.25rem;
}

p {
    margin-bottom: 1rem;
}

a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    color: var(--primary-hover);
    text-decoration: underline;
}

code {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    background-color: var(--code-bg);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
}

pre {
    background-color: var(--code-bg);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin-bottom: 1.5rem;
}

pre code {
    background-color: transparent;
    padding: 0;
}

ul, ol {
    margin: 0 0 1.5rem 1.5rem;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1.5rem;
    overflow-x: auto;
    display: block;
}

@media (min-width: 768px) {
    table {
        display: table;
    }
}

th, td {
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    text-align: left;
}

th {
    background-color: var(--card-bg);
    font-weight: 600;
}

.card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.5rem;
    background-color: var(--badge-bg);
    color: var(--badge-color);
}

.badge-get {
    background-color: #10b981;
    color: white;
}

.badge-post {
    background-color: #3b82f6;
    color: white;
}

.badge-put, .badge-patch {
    background-color: #f59e0b;
    color: white;
}

.badge-delete {
    background-color: #ef4444;
    color: white;
}

.endpoint-card {
    margin-bottom: 2rem;
    border-left: 4px solid var(--border-color);
    padding-left: 1rem;
}

.endpoint-card.get {
    border-left-color: #10b981;
}

.endpoint-card.post {
    border-left-color: #3b82f6;
}

.endpoint-card.put, .endpoint-card.patch {
    border-left-color: #f59e0b;
}

.endpoint-card.delete {
    border-left-color: #ef4444;
}

.endpoint-description, .endpoint-auth, .endpoint-params, .endpoint-response, .endpoint-example {
    margin-bottom: 1.5rem;
}

.theme-switch-container {
    display: flex;
    align-items: center;
    margin-top: 1rem;
    padding: 0.5rem 1rem;
}

.theme-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
    margin-left: auto;
}

.theme-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 24px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: var(--primary-color);
}

input:focus + .slider {
    box-shadow: 0 0 1px var(--primary-color);
}

input:checked + .slider:before {
    transform: translateX(26px);
}

.search-container {
    margin: 1rem 0;
    position: relative;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    border: 1px solid var(--border-color);
    background-color: var(--bg-color);
    color: var(--text-color);
    font-size: 1rem;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 0 0 4px 4px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 10;
}

.search-result-item {
    padding: 0.5rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid var(--border-color);
}

.search-result-item:hover {
    background-color: var(--sidebar-active);
}

.search-result-path {
    font-size: 0.8rem;
    opacity: 0.7;
}

.footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
    text-align: center;
    font-size: 0.875rem;
    color: var(--text-color);
}

/* API testing */
.api-test-panel {
    margin-top: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.api-test-header {
    padding: 0.5rem 1rem;
    background-color: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
    cursor: pointer;
    font-weight: 600;
}

.api-test-content {
    padding: 1rem;
    display: none;
}

.api-test-content.active {
    display: block;
}

.api-test-form {
    margin-bottom: 1rem;
}

.api-test-form input, .api-test-form textarea, .api-test-form select {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: var(--bg-color);
    color: var(--text-color);
}

.api-test-form label {
    display: block;
    margin-bottom: 0.25rem;
}

.api-test-form button {
    padding: 0.5rem 1rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
}

.api-test-form button:hover {
    background-color: var(--primary-hover);
}

.api-test-response {
    margin-top: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 1rem;
    background-color: var(--code-bg);
    overflow-x: auto;
}

.api-test-response.success {
    border-color: #10b981;
}

.api-test-response.error {
    border-color: #ef4444;
}

.tabs {
    display: flex;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.tab {
    padding: 0.5rem 1rem;
    cursor: pointer;
    border: 1px solid transparent;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    margin-right: 0.25rem;
}

.tab.active {
    background-color: var(--card-bg);
    border-color: var(--border-color);
    color: var(--primary-color);
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

/* Breadcrumbs */
.breadcrumbs {
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
}

.breadcrumbs ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
}

.breadcrumbs li {
    display: inline-block;
}

.breadcrumbs li:not(:last-child)::after {
    content: "/";
    margin: 0 0.5rem;
    color: var(--border-color);
}

.breadcrumbs a {
    color: var(--primary-color);
}

.breadcrumbs a:hover {
    text-decoration: underline;
}

/* Responsive styles */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        width: 240px;
    }

    .sidebar.active {
        transform: translateX(0);
    }

    .content {
        margin-left: 0;
        padding: 1rem;
    }

    .sidebar-toggle {
        display: block;
    }

    h1 {
        font-size: 1.8rem;
    }

    h2 {
        font-size: 1.5rem;
    }

    h3 {
        font-size: 1.25rem;
    }
}

/* Print styles */
@media print {
    .sidebar, .sidebar-toggle, .theme-switch-container, .api-test-panel, .search-container {
        display: none !important;
    }

    .content {
        margin-left: 0;
        padding: 0;
    }

    .container {
        display: block;
    }

    body {
        color: black;
        background: white;
    }

    a {
        color: blue;
    }

    h1, h2, h3, h4, h5, h6 {
        color: black;
        break-after: avoid;
    }

    table {
        break-inside: avoid;
    }
}
"""

        # Write main CSS
        with open(main_css, 'w') as f:
            f.write(css_content)

    def _generate_prism_css(self, css_dir: Path) -> None:
        """Generate Prism CSS file for syntax highlighting

        Args:
            css_dir: Directory where CSS files will be created
        """
        prism_css = css_dir / "prism.css"

        prism_css_content = """
/* PrismJS 1.24.1 - Syntax highlighting
 * Theme: Custom theme with light/dark mode support
 * Backend Documentation Generator
 * Generated: 2025-05-04 17:01:45
 */

code[class*="language-"],
pre[class*="language-"] {
    color: #f8f8f2;
    background: none;
    text-shadow: 0 1px rgba(0, 0, 0, 0.3);
    font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
    font-size: 1em;
    text-align: left;
    white-space: pre;
    word-spacing: normal;
    word-break: normal;
    word-wrap: normal;
    line-height: 1.5;

    -moz-tab-size: 4;
    -o-tab-size: 4;
    tab-size: 4;

    -webkit-hyphens: none;
    -moz-hyphens: none;
    -ms-hyphens: none;
    hyphens: none;
}

pre[class*="language-"] {
    padding: 1em;
    margin: .5em 0;
    overflow: auto;
    border-radius: 0.3em;
}

:not(pre) > code[class*="language-"],
pre[class*="language-"] {
    background: #282a36;
}

:not(pre) > code[class*="language-"] {
    padding: .1em;
    border-radius: .3em;
    white-space: normal;
}

.token.comment,
.token.prolog,
.token.doctype,
.token.cdata {
    color: #6272a4;
}

.token.punctuation {
    color: #f8f8f2;
}

.namespace {
    opacity: .7;
}

.token.property,
.token.tag,
.token.constant,
.token.symbol,
.token.deleted {
    color: #ff79c6;
}

.token.boolean,
.token.number {
    color: #bd93f9;
}

.token.selector,
.token.attr-name,
.token.string,
.token.char,
.token.builtin,
.token.inserted {
    color: #50fa7b;
}

.token.operator,
.token.entity,
.token.url,
.language-css .token.string,
.style .token.string,
.token.variable {
    color: #f8f8f2;
}

.token.atrule,
.token.attr-value,
.token.function,
.token.class-name {
    color: #f1fa8c;
}

.token.keyword {
    color: #8be9fd;
}

.token.regex,
.token.important {
    color: #ffb86c;
}

.token.important,
.token.bold {
    font-weight: bold;
}

.token.italic {
    font-style: italic;
}

.token.entity {
    cursor: help;
}

/* Override for light theme */
[data-theme="light"] code[class*="language-"],
[data-theme="light"] pre[class*="language-"] {
    color: #24292e;
    text-shadow: none;
}

[data-theme="light"] :not(pre) > code[class*="language-"],
[data-theme="light"] pre[class*="language-"] {
    background: #f6f8fa;
}

[data-theme="light"] .token.comment,
[data-theme="light"] .token.prolog,
[data-theme="light"] .token.doctype,
[data-theme="light"] .token.cdata {
    color: #6a737d;
}

[data-theme="light"] .token.punctuation {
    color: #24292e;
}

[data-theme="light"] .token.property,
[data-theme="light"] .token.tag,
[data-theme="light"] .token.constant,
[data-theme="light"] .token.symbol,
[data-theme="light"] .token.deleted {
    color: #d73a49;
}

[data-theme="light"] .token.boolean,
[data-theme="light"] .token.number {
    color: #6f42c1;
}

[data-theme="light"] .token.selector,
[data-theme="light"] .token.attr-name,
[data-theme="light"] .token.string,
[data-theme="light"] .token.char,
[data-theme="light"] .token.builtin,
[data-theme="light"] .token.inserted {
    color: #22863a;
}

[data-theme="light"] .token.operator,
[data-theme="light"] .token.entity,
[data-theme="light"] .token.url,
[data-theme="light"] .language-css .token.string,
[data-theme="light"] .style .token.string,
[data-theme="light"] .token.variable {
    color: #24292e;
}

[data-theme="light"] .token.atrule,
[data-theme="light"] .token.attr-value,
[data-theme="light"] .token.function,
[data-theme="light"] .token.class-name {
    color: #6f42c1;
}

[data-theme="light"] .token.keyword {
    color: #d73a49;
}

[data-theme="light"] .token.regex,
[data-theme="light"] .token.important {
    color: #e36209;
}
"""

        # Write Prism CSS
        with open(prism_css, 'w') as f:
            f.write(prism_css_content)

    def _generate_main_js(self, js_dir: Path) -> None:
        """Generate main JavaScript file for the HTML documentation

        Args:
            js_dir: Directory where JS files will be created
        """
        main_js = js_dir / "main.js"

        main_js_content = """
/**
 * Backend Documentation HTML Generator - Main JavaScript
 *
 * This script provides interactive functionality for the generated HTML documentation:
 * - Theme switching between dark/light modes
 * - Mobile-responsive sidebar navigation
 * - Search functionality across documentation
 * - Active link highlighting based on current page
 * - Integration with API testing functionality
 *
 * Configuration Variables (set in the HTML):
 * - window.searchData: Array of searchable content objects with structure:
 *   {title: string, content: string, url: string, section: string}
 * - window.backendUrl: Base URL for API testing (optional)
 *
 * Author: nanthiniSanthanam
 * Generated: 2025-05-04 17:01:45
 */

// Initialize all components when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get theme preference from localStorage or system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Set theme based on preference
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(theme);

    // Initialize theme switch
    const themeSwitch = document.getElementById('theme-switch');
    if (themeSwitch) {
        themeSwitch.checked = theme === 'dark';

        themeSwitch.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Mobile menu toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 768 &&
                !sidebar.contains(event.target) &&
                !sidebarToggle.contains(event.target) &&
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Init search functionality
    initSearch();

    // Set active link in sidebar
    setActiveLink();

    // Initialize API interaction if available
    if (typeof initApiTesting === 'function') {
        initApiTesting();
    }

    // Initialize tabs if present
    initTabs();

    // Initialize collapsible elements
    initCollapsible();
});

/**
 * Sets the theme for the documentation
 * @param {string} theme - 'dark' or 'light'
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

/**
 * Highlights the active link in sidebar based on current page
 */
function setActiveLink() {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');

    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.classList.add('active');
        }
    });
}

/**
 * Initializes the search functionality
 * Searches through window.searchData to find matching content
 */
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (!searchInput || !searchResults) return;

    // Search data (populated by the backend)
    const searchData = window.searchData || [];

    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();

        if (query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        // Filter results
        const results = searchData.filter(item =>
            item.title.toLowerCase().includes(query) ||
            item.content.toLowerCase().includes(query)
        ).slice(0, 10); // Limit to 10 results

        // Display results
        if (results.length > 0) {
            searchResults.innerHTML = results.map(result => `
                <div class="search-result-item" data-href="${result.url}">
                    <div>${result.title}</div>
                    <div class="search-result-path">${result.section}</div>
                </div>
            `).join('');

            searchResults.style.display = 'block';

            // Add click event to results
            document.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', function() {
                    window.location.href = this.getAttribute('data-href');
                });
            });
        } else {
            searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
            searchResults.style.display = 'block';
        }
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

/**
 * Initialize tabbed content
 */
function initTabs() {
    document.querySelectorAll('.tabs').forEach(tabGroup => {
        const tabs = tabGroup.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll(tabGroup.getAttribute('data-tab-content'));

        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                // Deactivate all tabs
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                // Activate the clicked tab
                tab.classList.add('active');
                tabContents[index].classList.add('active');
            });
        });

        // Activate first tab by default
        if (tabs.length > 0 && tabContents.length > 0) {
            tabs[0].classList.add('active');
            tabContents[0].classList.add('active');
        }
    });
}

/**
 * Initialize collapsible elements
 */
function initCollapsible() {
    document.querySelectorAll('.api-test-header').forEach(header => {
        header.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            if (content.classList.contains('active')) {
                content.classList.remove('active');
            } else {
                content.classList.add('active');
            }
        });
    });
}
"""

        # Write main JS
        with open(main_js, 'w') as f:
            f.write(main_js_content)

    def _generate_prism_js(self, js_dir: Path) -> None:
        """Generate Prism JS file for syntax highlighting

        Args:
            js_dir: Directory where JS files will be created
        """
        prism_js = js_dir / "prism.js"

        # We're providing a simplified version of Prism for documentation
        prism_js_content = """
/* PrismJS 1.24.1
 * Simplified version for documentation
 * Backend Documentation Generator
 * Generated: 2025-05-04 17:01:45
 */

/* Core Prism functionality */
var _self="undefined"!=typeof window?window:"undefined"!=typeof WorkerGlobalScope&&self instanceof WorkerGlobalScope?self:{},Prism=function(u){var c=/\\blang(?:uage)?-(\\w+)\\b/i,n=0,e={},M={util:{encode:function(n){return n instanceof W?new W(n.type,M.util.encode(n.content),n.alias):Array.isArray(n)?n.map(M.util.encode):n.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/\\u00a0/g," ")}}};function W(e,n,t){this.type=e,this.content=n,this.alias=t}Prism.languages={markup:{comment:/<!--[\\s\\S]*?-->/,prolog:/<\\?[\\s\\S]+?\\?>/,doctype:{pattern:/<!DOCTYPE(?:[^>"'[\\]]|"[^"]*"|'[^']*')+(?:\\[(?:[^<"'\\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\\]\\s*)?>/i,greedy:!0},cdata:/<![CDATA[[\\s\\S]*?]]>/i,tag:{pattern:/<\\/?(?!\\d)[^\\s>\\/=$<%]+(?:\\s(?:\\s*[^\\s>\\/=]+(?:\\s*=\\s*(?:"[^"]*"|'[^']*'|[^\\s'">=]+(?=[\\s>]))|(?=[\\s/>])))+)?\\s*\\/?>/,greedy:!0,inside:{tag:{pattern:/^<\\/?[^\\s>\\/]+/,inside:{punctuation:/^<\\/?/,namespace:/^[^\\s>\\/:]+:/}},"attr-value":{pattern:/=\\s*(?:"[^"]*"|'[^']*'|[^\\s'">=]+)/,inside:{punctuation:[{pattern:/^=/,alias:"attr-equals"},/"|'/]}},punctuation:/\\/?>/,"attr-name":{pattern:/[^\\s>\\/]+/,inside:{namespace:/^[^\\s>\\/:]+:/}}}},entity:/&#?[\\da-z]{1,8};/i},css:{comment:/\\/\\*[\\s\\S]*?\\*\\//,atrule:{pattern:/@[\\w-](?:[^;{\\s]|\\s+(?![\\s{]))*(?:;|(?=\\s*\\{))/,inside:{rule:/^@[\\w-]+/,"selector-function-argument":{pattern:/(\([^)]*\))/,lookbehind:!0,alias:"selector"},keyword:{pattern:/(^|[^\\w-])(?:and|not|only|or)(?![\\w-])/,lookbehind:!0}}},url:{pattern:RegExp("\\\\burl\\\\((?:[^\\\\\\\\\\\\)\"']|\\\\\\\\[\\\\s\\\\S])*\\\\)","i"),greedy:!0,inside:{function:/^url/i,punctuation:/^\\(|\\)$/,string:{pattern:RegExp("^[^\\\\s]$"),alias:"url"}}},selector:/[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|"(?:\\\\.|[^\\\\\\r\\n"])*"|'(?:\\\\.|[^\\\\\\r\\n'])*')*/,property:/(?!\\s)[-_a-z\\xA0-\\uFFFF](?:(?!\\s)[-\\w\\xA0-\\uFFFF])*(?=\\s*:)/i,important:/!important\\b/i,function:/[-a-z0-9]+(?=\\()/i,punctuation:/[(){};:,]/},javascript:{comment:/\\/\\/.*|\\/\\*[\\s\\S]*?\\*\\//,string:{pattern:/(["'])(?:\\\\(?:\\r\\n|[\\s\\S])|(?!\\1)[^\\\\\\r\\n])*\\1/,greedy:!0},keyword:/\\b(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\\b/,"boolean":/\\b(?:false|true)\\b/,"function":/\\w+(?=\\()/,number:/\\b0x[\\da-f]+\\b|(?:\\b\\d+\\.?\\d*|\\B\\.\\d+)(?:e[+-]?\\d+)?/i,operator:/[<>]=?|[!=]=?=?|--?|\\+\\+?|&&?|\\|\\|?|[?*/~^%]/,punctuation:/[{}[\\];(),.:]/},python:{comment:{pattern:/(^|[^\\\\])#.*/,lookbehind:!0},"string-interpolation":{pattern:/(?:f|rf|fr)(?:(""" | ''')[\\s\\S]*?\\1|("|')(?:\\\\.|(?!\\2)[^\\\\\\r\\n])*\\2)/i,greedy:!0,inside:{interpolation:{pattern:/((?:^|[^{])(?:{{)*){(?!{)(?:[^{}]|{(?!{)(?:[^{}]|{(?!{)(?:[^{}])+})+})+}/,lookbehind:!0,inside:{"format-spec":{pattern:/(:)[^:(){}]+(?=}$)/,lookbehind:!0},"conversion-option":{pattern:/![sra](?=[:}]$)/,alias:"punctuation"},rest:null}},string:/[\\s\\S]+/}},"triple-quoted-string":{pattern:/(?:[rub]|rb|br)?"""|'''/i, greedy: !0, alias: "string"}, string: {pattern: / (?: [rub] | rb | br)?("|')(?:\\\\.|(?!\\1)[^\\\\\\r\\n])*\\1/i,greedy:!0},keyword:/\\b(?:and|as|assert|async|await|break|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\\b/,"function":/\\b[a-z_]\\w*(?=\\s*\\()/i},json:{property:{pattern:/"(?: \\\\.|[^\\\\"])*"(?=\\s*:)/,greedy:!0},string:{pattern:/"(?:\\\\.|[^\\\\"])*"/,greedy:!0},comment:/\\/\\/.*|\\/\\*[\\s\\S]*?(?:\\*\\/|$)/,number:/-?\\d+\\.?\\d*(?:e[+-]?\\d+)?/i,punctuation:/[{}[\\],]/,operator:/:/,"boolean":/\\b(?:true|false)\\b/,"null":{pattern:/\\bnull\\b/,alias:"keyword"}}};

// Initialize Prism for syntax highlighting
document.addEventListener('DOMContentLoaded', function() {
    // Helper function to highlight code blocks
    function highlightAll() {
        if (typeof Prism !== 'undefined') {
            // Select all pre > code elements
            document.querySelectorAll('pre code').forEach(function(block) {
                // Get language class if specified
                let langClass = Array.from(block.classList).find(cls => cls.startsWith('language-'));
                
                if (!langClass) {
                    // Default to language-javascript if none specified
                    block.classList.add('language-javascript');
                }

                // Apply highlighting
                Prism.highlightElement(block);
            });
        }
    }

    // Run highlighting
    highlightAll();
});
"""

        # Write Prism JS
        with open(prism_js, 'w') as f:
            f.write(prism_js_content)

    def _generate_api_testing_js(self, js_dir: Path) -> None:
        """Generate API Testing JS file for interactive API testing

        Args:
            js_dir: Directory where JS files will be created
        """
        api_test_js = js_dir / "api-testing.js"
        
        api_test_js_content = """
/**
 * Backend Documentation HTML Generator - API Testing JavaScript
 * 
 * This script provides interactive API testing functionality:
 * - Send requests to API endpoints directly from documentation
 * - Support for different HTTP methods (GET, POST, PUT, DELETE, etc.)
 * - Authentication header management
 * - Query parameters and request body handling
 * - File upload support
 * - Pretty response formatting
 * 
 * Author: nanthiniSanthanam
 * Generated: 2025-05-04 17:01:45
 */

// Initialize API testing functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initApiTesting();
});

/**
 * Initialize API testing panels and forms
 */
function initApiTesting() {
    // Toggle test panels
    document.querySelectorAll('.api-test-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            content.classList.toggle('active');
        });
    });
    
    // Set up test forms
    document.querySelectorAll('.api-test-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const endpoint = this.getAttribute('data-endpoint');
            const method = this.getAttribute('data-method') || 'GET';
            const responseElement = document.getElementById(`${this.id}-response`);
            
            // Show loading state
            responseElement.textContent = 'Sending request...';
            responseElement.className = 'api-test-response';
            
            // Gather form data
            sendApiRequest(this, endpoint, method, responseElement);
        });
    });
}

/**
 * Send API request based on form data
 * 
 * @param {HTMLFormElement} form - The form element containing the request data
 * @param {string} endpoint - The API endpoint to send the request to
 * @param {string} method - The HTTP method to use (GET, POST, etc.)
 * @param {HTMLElement} responseElement - Element to display the response
 */
function sendApiRequest(form, endpoint, method, responseElement) {
    // Get form data
    const formData = new FormData(form);
    const queryParams = new URLSearchParams();
    const bodyParams = {};
    let hasFiles = false;
    
    // Process form fields
    formData.forEach((value, key) => {
        // Query parameters start with "query-"
        if (key.startsWith('query-')) {
            const paramName = key.replace('query-', '');
            if (value) queryParams.append(paramName, value);
        } 
        // Body parameters start with "body-"
        else if (key.startsWith('body-')) {
            const paramName = key.replace('body-', '');
            if (value instanceof File) {
                if (value.size > 0) {
                    hasFiles = true;
                }
            } else if (value) {
                // Try to parse JSON if the value looks like JSON
                if (value.trim().startsWith('{') || value.trim().startsWith('[')) {
                    try {
                        bodyParams[paramName] = JSON.parse(value);
                    } catch (e) {
                        bodyParams[paramName] = value;
                    }
                } else {
                    bodyParams[paramName] = value;
                }
            }
        }
    });
    
    // Build URL with query params
    let url = endpoint;
    if (queryParams.toString()) {
        url += (url.includes('?') ? '&' : '?') + queryParams.toString();
    }
    
    // Build request options
    const options = {
        method: method,
        headers: {},
    };
    
    // Add auth token if available
    const authToken = document.getElementById('auth-token')?.value;
    if (authToken) {
        // Try to determine token type
        if (authToken.split('.').length === 3) {
            // Looks like JWT
            options.headers['Authorization'] = `Bearer ${authToken}`;
        } else {
            options.headers['Authorization'] = `Token ${authToken}`;
        }
    }
    
    // Add body if not GET
    if (method !== 'GET') {
        if (hasFiles) {
            // Use FormData for files
            const requestFormData = new FormData();
            formData.forEach((value, key) => {
                if (key.startsWith('body-') && (!(value instanceof File) || value.size > 0)) {
                    requestFormData.append(key.replace('body-', ''), value);
                }
            });
            options.body = requestFormData;
        } else {
            // Use JSON for regular requests
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(bodyParams);
        }
    }
    
    // Make request
    fetch(url, options)
        .then(response => {
            // Get content type
            const contentType = response.headers.get('content-type');
            
            // Add status to response element
            responseElement.dataset.status = response.status;
            responseElement.classList.add(response.ok ? 'success' : 'error');
            
            // Try to parse response based on content type
            if (contentType && contentType.includes('application/json')) {
                return response.json().then(data => {
                    return {
                        data: data,
                        status: response.status,
                        statusText: response.statusText,
                        headers: Object.fromEntries(response.headers.entries())
                    };
                });
            } else {
                return response.text().then(text => {
                    return {
                        data: text,
                        status: response.status,
                        statusText: response.statusText,
                        headers: Object.fromEntries(response.headers.entries())
                    };
                });
            }
        })
        .then(result => {
            // Format the response
            const responseObj = {
                status: result.status,
                statusText: result.statusText,
                headers: result.headers,
                data: result.data
            };
            
            // Display the response
            responseElement.innerHTML = `<pre><code class="language-json">${JSON.stringify(responseObj, null, 2)}</code></pre>`;
            
            // Apply syntax highlighting
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(responseElement.querySelector('code'));
            }
        })
        .catch(error => {
            responseElement.textContent = `Error: ${error.message}`;
            responseElement.className = 'api-test-response error';
        });
}
"""

        # Write API testing JS
        with open(api_test_js, 'w') as f:
            f.write(api_test_js_content)

    def _generate_html_template(self, title: str, content: str, active_page: str, breadcrumbs: List[Dict[str, str]] = None) -> str:
        """Generate an HTML template with common elements

        Args:
            title: Page title
            content: Main content HTML
            active_page: Current page filename for active navigation
            breadcrumbs: Optional list of breadcrumb items [{title, url}]

        Returns:
            str: Complete HTML document
        """
        # Prepare navigation items based on documentation sections
        nav_items = []
        
        sections_map = {
            "project_overview": {"title": "Project Overview", "file": "project_overview.html"},
            "models_and_database": {"title": "Models & Database", "file": "models_and_database.html"},
            "api_endpoints": {"title": "API Endpoints", "file": "api_endpoints.html"},
            "authentication": {"title": "Authentication", "file": "authentication.html"},
            "frontend_integration": {"title": "Frontend Integration", "file": "frontend_integration.html"},
            "typescript_interfaces": {"title": "TypeScript Interfaces", "file": "typescript_interfaces.html"}
        }
        
        nav_items.append(f'<li><a href="index.html" class="{"active" if active_page == "index.html" else ""}">Home</a></li>')
        
        for section in self.documentation_sections:
            if section in sections_map:
                info = sections_map[section]
                nav_items.append(
                    f'<li><a href="{info["file"]}" class="{"active" if active_page == info["file"] else ""}">{info["title"]}</a></li>'
                )
        
        # Prepare breadcrumbs HTML
        breadcrumbs_html = ""
        if breadcrumbs:
            breadcrumbs_html = """
            <div class="breadcrumbs">
                <ul>
                    <li><a href="index.html">Home</a></li>
            """
            
            for crumb in breadcrumbs:
                if "url" in crumb:
                    breadcrumbs_html += f'<li><a href="{crumb["url"]}">{crumb["title"]}</a></li>'
                else:
                    breadcrumbs_html += f'<li>{crumb["title"]}</li>'
            
            breadcrumbs_html += """
                </ul>
            </div>
            """
        
        # Generate HTML with template
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - API Documentation</title>
    <meta name="description" content="API documentation generated by Backend Documentation Generator">
    <meta name="generator" content="Backend Documentation Generator 1.0.0">
    <link rel="stylesheet" href="resources/css/main.css">
    <link rel="stylesheet" href="resources/css/prism.css">
</head>
<body>
    <button id="sidebar-toggle" class="sidebar-toggle" aria-label="Toggle menu">≡</button>
    
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>API Docs</h1>
            </div>
            
            <div class="search-container">
                <input type="text" id="search-input" class="search-input" placeholder="Search documentation..." aria-label="Search documentation">
                <div id="search-results" class="search-results" style="display:none;"></div>
            </div>
            
            <ul class="sidebar-nav">
                {' '.join(nav_items)}
            </ul>
            
            <div class="theme-switch-container">
                <span>Dark Theme</span>
                <label class="theme-switch" for="theme-switch">
                    <input type="checkbox" id="theme-switch" aria-label="Toggle dark theme">
                    <span class="slider"></span>
                </label>
            </div>
        </div>
        
        <div class="content">
            <div class="content-inner">
                {breadcrumbs_html}
                {content}
                
                <footer class="footer">
                    <p>Generated with Backend Documentation Generator | Detail Level: {self.detail_level.capitalize()}</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </footer>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="resources/js/prism.js"></script>
    <script src="resources/js/main.js"></script>
    <script src="resources/js/api-testing.js"></script>
    
    <script>
        // Initialize search data
        window.searchData = window.searchData || [];
    </script>
</body>
</html>"""
        
        return html_template

    def _generate_search_data(self, output_dir: Path) -> None:
        """Generate search data file for documentation search

        Args:
            output_dir: Directory where HTML files are generated
        """
        if not self.search_data:
            return
            
        search_js = output_dir / "resources" / "js" / "search-data.js"
        
        # Convert search data to JSON
        search_json = json.dumps(self.search_data, indent=2)
        
        search_js_content = f"""
/**
 * Search data for documentation search
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */
 
window.searchData = {search_json};
"""
        
        # Write search data
        with open(search_js, 'w') as f:
            f.write(search_js_content)
        
        logger.info("Generated search data")
        
        # Add search data script to all HTML files
        for html_file in output_dir.glob("*.html"):
            with open(html_file, 'r') as f:
                content = f.read()
                
            # Add search-data.js before closing body tag if not already present
            if "search-data.js" not in content:
                content = content.replace(
                    "    <script>\n        // Initialize search data",
                    '    <script src="resources/js/search-data.js"></script>\n    <script>\n        // Initialize search data'
                )
                
                with open(html_file, 'w') as f:
                    f.write(content)

    def _add_to_search_data(self, title: str, content: str, url: str, section: str) -> None:
        """Add page content to search data

        Args:
            title: Page title
            content: Plain text content (HTML stripped)
            url: Page URL
            section: Section name
        """
        # Strip HTML and clean up text
        content = re.sub(r'<.*?>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Limit content length for search
        content = content[:300] + '...' if len(content) > 300 else content
        
        self.search_data.append({
            "title": title,
            "content": content,
            "url": url,
            "section": section
        })

    def _generate_index(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate index.html with project overview

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get project info
        project_info = data.get('project_info', {})
        project_name = project_info.get('name', 'Django Project')
        
        # Get counts for key statistics
        model_count = sum(len(app_info.get('models', {})) 
                          for app_info in data.get('models', {}).values())
        api_count = len(data.get('apis', {}).get('endpoints', []))
        serializer_count = data.get('serializers', {}).get('count', 0)
        
        # Create content
        content = f"""
        <h1>{project_name} Backend Documentation</h1>
        
        <p>This documentation provides comprehensive information about the backend system for frontend development.</p>
        
        <div class="card">
            <h2>Quick Statistics</h2>
            <ul>
                <li><strong>Django Apps:</strong> {len(project_info.get('apps', []))}</li>
                <li><strong>Models:</strong> {model_count}</li>
                <li><strong>API Endpoints:</strong> {api_count}</li>
                <li><strong>Serializers:</strong> {serializer_count}</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Documentation Sections</h2>
            <ul>
                <li><a href="project_overview.html">Project Overview</a> - System architecture and components</li>
                <li><a href="models_and_database.html">Models and Database Schema</a> - Data structure and relationships</li>
                <li><a href="api_endpoints.html">API Endpoints</a> - Available endpoints with request/response formats</li>
                <li><a href="authentication.html">Authentication and Authorization</a> - Security mechanisms</li>
                <li><a href="frontend_integration.html">Frontend Integration Guide</a> - How to connect frontend applications</li>
        """
        
        if "typescript_interfaces" in self.documentation_sections:
            content += """
                <li><a href="typescript_interfaces.html">TypeScript Interfaces</a> - Generated TypeScript types</li>
            """
            
        content += """
            </ul>
        </div>
        
        <div class="card">
            <h2>How to Use This Documentation</h2>
            <p>This documentation is designed for frontend developers working with this backend system. It provides detailed information about the data models, API endpoints, authentication requirements, and more. For effective integration, we recommend the following approach:</p>
            <ol>
                <li>Start with the <strong>Project Overview</strong> to understand the system architecture</li>
                <li>Review the <strong>Models and Database Schema</strong> to understand the data structures</li>
                <li>Explore the <strong>API Endpoints</strong> to see available operations and request/response formats</li>
                <li>Check the <strong>Authentication</strong> section to implement proper auth flows</li>
                <li>Use the <strong>Frontend Integration Guide</strong> for best practices and examples</li>
            </ol>
        </div>
        
        <div class="card">
            <h2>Notes for Frontend Developers</h2>
            <p>When implementing frontend components that interact with this backend:</p>
            <ul>
                <li>Always check authentication requirements for endpoints</li>
                <li>Use the TypeScript interfaces to ensure type safety</li>
                <li>Follow the pagination patterns described in the API documentation</li>
                <li>Reference the example React hooks for common data fetching patterns</li>
            </ul>
        </div>
        """
        
        # Generate HTML
        html = self._generate_html_template(
            f"{project_name} Backend Documentation",
            content,
            "index.html"
        )
        
        # Write file
        output_path = output_dir / "index.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            f"{project_name} Backend Documentation",
            "Backend documentation home page with overview of API, models, and integration guides.",
            "index.html",
            "Home"
        )
            
        logger.info("Generated index.html")

    def _generate_project_overview(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate project overview documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get project info
        project_info = data.get('project_info', {})
        project_name = project_info.get('name', 'Django Project')
        
        # Create content
        content = f"""
        <h1>{project_name} Project Overview</h1>
        
        <div class="card">
            <h2>System Architecture</h2>
            <p>This Django application follows a standard architectural pattern with the following components:</p>
            <ul>
                <li><strong>Models</strong>: Define the database schema and data relationships</li>
                <li><strong>Views/ViewSets</strong>: Handle API requests and responses</li>
                <li><strong>Serializers</strong>: Transform data between Python objects and API formats</li>
                <li><strong>URLs</strong>: Define the API endpoints</li>
                <li><strong>Settings</strong>: Configure the application behavior</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Django Apps</h2>
        """
        
        # Add apps information
        apps = project_info.get('apps', [])
        if apps:
            content += "<p>The project consists of the following Django apps:</p><ul>"
            
            for app in apps:
                content += f"<li><strong>{app}</strong></li>"
            
            content += "</ul>"
        else:
            content += "<p>No Django apps information available.</p>"
        
        content += """
        </div>
        
        <div class="card">
            <h2>Environment Configuration</h2>
            <p>The application requires the following environment configuration:</p>
            <ul>
                <li><strong>Database</strong>: PostgreSQL database connection details</li>
                <li><strong>Secret Key</strong>: Django secret key for cryptographic signing</li>
                <li><strong>Debug Mode</strong>: Set to False in production</li>
                <li><strong>Allowed Hosts</strong>: Domains that can serve the application</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Backend Technologies</h2>
            <p>The backend is built with the following core technologies:</p>
            <ul>
                <li><strong>Django</strong>: Web framework for building the application</li>
                <li><strong>Django REST Framework</strong>: Library for building RESTful APIs</li>
                <li><strong>PostgreSQL</strong>: Relational database management system</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>External Services</h2>
            <p>The system may integrate with the following external services (check settings for details):</p>
            <ul>
                <li><strong>Email Provider</strong>: For sending notifications and password resets</li>
                <li><strong>File Storage</strong>: For storing media files</li>
                <li><strong>Authentication Providers</strong>: For social authentication (if configured)</li>
            </ul>
        </div>
        """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "Project Overview"}
        ]
        
        html = self._generate_html_template(
            f"{project_name} Project Overview",
            content,
            "project_overview.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "project_overview.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            f"{project_name} Project Overview",
            "System architecture, Django apps, environment configuration, and technology stack.",
            "project_overview.html",
            "Project Overview"
        )
        
        logger.info("Generated project_overview.html")

    def _generate_models_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate documentation for models and database schema

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get models data
        models_data = data.get('models', {})
        
        # Create content
        content = """
        <h1>Models and Database Schema</h1>
        
        <p>This document describes all models in the system and their relationships.</p>
        
        <div class="card">
            <h2>Table of Contents</h2>
            <ul>
        """
        
        # Generate table of contents
        app_count = 0
        for app_label in sorted(models_data.keys()):
            app_count += 1
            app_id = app_label.lower().replace('.', '-')
            content += f'<li><a href="#app-{app_id}">{app_label}</a></li>'
        
        content += """
            </ul>
        </div>
        """
        
        # Generate detailed documentation for each app
        if app_count > 0:
            for app_label, app_info in sorted(models_data.items()):
                app_id = app_label.lower().replace('.', '-')
                content += f"""
                <div class="card">
                    <h2 id="app-{app_id}">{app_label}</h2>
                """
                
                # Add models for this app
                for model_name, model_info in sorted(app_info.get('models', {}).items()):
                    content += f"""
                    <div class="endpoint-card">
                        <h3>{model_name}</h3>
                        <p><strong>Table Name:</strong> <code>{model_info.get('table_name')}</code></p>
                        <p>{model_info.get('verbose_name_plural', model_name)}</p>
                        
                        <h4>Fields</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Type</th>
                                    <th>Required</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    # Add fields
                    for field_name, field_info in sorted(model_info.get('fields', {}).items()):
                        required = "Yes" if not field_info.get('null', True) and not field_info.get('blank', True) else "No"
                        description = field_info.get('help_text', '') or field_info.get('verbose_name', '')
                        field_type = field_info.get('type', '')
                        
                        # Add extra type info
                        if field_type == 'CharField' and 'max_length' in field_info:
                            field_type += f" (max_length={field_info['max_length']})"
                        elif field_type == 'DecimalField' and 'max_digits' in field_info:
                            field_type += f" (max_digits={field_info['max_digits']}, decimal_places={field_info.get('decimal_places', 0)})"
                        
                        content += f"""
                                <tr>
                                    <td>{field_name}</td>
                                    <td><code>{field_type}</code></td>
                                    <td>{required}</td>
                                    <td>{description}</td>
                                </tr>
                        """
                    
                    content += """
                            </tbody>
                        </table>
                    """
                    
                    # Add relationships
                    relationships = model_info.get('relationships', {})
                    
                    # Foreign keys
                    foreign_keys = relationships.get('foreign_keys', [])
                    if foreign_keys:
                        content += """
                        <h4>Foreign Keys</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>References</th>
                                    <th>On Delete</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        
                        for fk in foreign_keys:
                            target = f"{fk.get('target_app')}.{fk.get('target_model')}"
                            on_delete = fk.get('on_delete', '')
                            description = fk.get('help_text', '') or fk.get('verbose_name', '')
                            
                            content += f"""
                                <tr>
                                    <td>{fk.get('name')}</td>
                                    <td>{target}</td>
                                    <td>{on_delete}</td>
                                    <td>{description}</td>
                                </tr>
                            """
                        
                        content += """
                            </tbody>
                        </table>
                        """
                    
                    # Many to many
                    many_to_many = relationships.get('many_to_many', [])
                    if many_to_many:
                        content += """
                        <h4>Many-to-Many Relationships</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Related Model</th>
                                    <th>Through</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        
                        for m2m in many_to_many:
                            target = f"{m2m.get('target_app')}.{m2m.get('target_model')}"
                            through = m2m.get('through', '') or '-'
                            description = m2m.get('help_text', '') or m2m.get('verbose_name', '')
                            
                            content += f"""
                                <tr>
                                    <td>{m2m.get('name')}</td>
                                    <td>{target}</td>
                                    <td>{through}</td>
                                    <td>{description}</td>
                                </tr>
                            """
                        
                        content += """
                            </tbody>
                        </table>
                        """
                    
                    # One to one
                    one_to_one = relationships.get('one_to_one', [])
                    if one_to_one:
                        content += """
                        <h4>One-to-One Relationships</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Related Model</th>
                                    <th>On Delete</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        
                        for o2o in one_to_one:
                            target = f"{o2o.get('target_app')}.{o2o.get('target_model')}"
                            on_delete = o2o.get('on_delete', '')
                            description = o2o.get('help_text', '') or o2o.get('verbose_name', '')
                            
                            content += f"""
                                <tr>
                                    <td>{o2o.get('name')}</td>
                                    <td>{target}</td>
                                    <td>{on_delete}</td>
                                    <td>{description}</td>
                                </tr>
                            """
                        
                        content += """
                            </tbody>
                        </table>
                        """
                    
                    # Meta options
                    meta = model_info.get('meta_options', {})
                    if meta and (meta.get('ordering') or meta.get('unique_together') or meta.get('index_together')):
                        content += """
                        <h4>Meta Options</h4>
                        """
                        
                        if meta.get('ordering'):
                            ordering_str = ", ".join(str(field) for field in meta.get('ordering', []))
                            content += f"<p><strong>Ordering:</strong> {ordering_str}</p>"
                        
                        if meta.get('unique_together'):
                            content += "<p><strong>Unique Together:</strong></p><ul>"
                            for ut in meta.get('unique_together', []):
                                ut_str = ", ".join(str(field) for field in ut)
                                content += f"<li>{ut_str}</li>"
                            content += "</ul>"
                        
                        if meta.get('index_together'):
                            content += "<p><strong>Index Together:</strong></p><ul>"
                            for it in meta.get('index_together', []):
                                it_str = ", ".join(str(field) for field in it)
                                content += f"<li>{it_str}</li>"
                            content += "</ul>"
                    
                    content += """
                    </div>
                    """
                
                content += """
                </div>
                """
        else:
            content += """
            <div class="card">
                <p>No model information available.</p>
            </div>
            """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "Models and Database Schema"}
        ]
        
        html = self._generate_html_template(
            "Models and Database Schema",
            content,
            "models_and_database.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "models_and_database.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            "Models and Database Schema",
            "Database models, relationships, fields, and schema information.",
            "models_and_database.html",
            "Models & Database"
        )
        
        logger.info("Generated models_and_database.html")

    def _generate_api_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate API endpoints documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get API data
        apis = data.get('apis', {})
        endpoints = apis.get('endpoints', [])
        grouped_endpoints = apis.get('grouped', {})
        backend_url = self.backend_url
        
        # Create content
        content = """
        <h1>API Endpoints</h1>
        
        <p>This document describes all available API endpoints in the system.</p>
        """
        
        # Add API testing section if a backend URL is provided
        if backend_url:
            content += f"""
            <div class="card">
                <h2>API Testing</h2>
                <p>You can test API endpoints directly from this documentation. Each endpoint section includes a "Test Endpoint" section where you can make requests.</p>
                
                <div class="api-test-panel">
                    <div class="api-test-header">Authentication Settings</div>
                    <div class="api-test-content">
                        <p>Enter your authentication token to use when testing endpoints:</p>
                        <input type="text" id="auth-token" placeholder="JWT or Token value" style="width:100%; padding:8px; margin-bottom:10px;">
                        <p><small>This token will be stored in your browser for this session only.</small></p>
                        <p>Backend URL: <code>{backend_url}</code></p>
                    </div>
                </div>
            </div>
            """
            
        content += """
        <div class="card">
            <h2>Table of Contents</h2>
        """
        
        # Generate table of contents
        if grouped_endpoints:
            content += "<ul>"
            app_index = 1
            for app_name in sorted(grouped_endpoints.keys()):
                app_id = app_name.lower().replace('.', '-')
                content += f'<li><a href="#app-{app_id}">{app_name}</a></li>'
                app_index += 1
            content += "</ul>"
        else:
            # Simple list of endpoints if not grouped
            content += '<ul><li><a href="#all-endpoints">All Endpoints</a></li></ul>'
        
        content += """
        </div>
        """
        
        # Generate detailed documentation
        if grouped_endpoints:
            for app_name, app_info in sorted(grouped_endpoints.items()):
                app_id = app_name.lower().replace('.', '-')
                content += f"""
                <div class="card">
                    <h2 id="app-{app_id}">{app_name}</h2>
                """
                
                # Add endpoints for this app
                for endpoint in app_info.get('endpoints', []):
                    content += self._format_endpoint_html(endpoint, data, backend_url)
                
                content += """
                </div>
                """
        elif endpoints:
            # Simple list if not grouped
            content += """
            <div class="card">
                <h2 id="all-endpoints">All Endpoints</h2>
            """
            
            for endpoint in endpoints:
                content += self._format_endpoint_html(endpoint, data, backend_url)
            
            content += """
            </div>
            """
        else:
            content += """
            <div class="card">
                <p>No API endpoint information available.</p>
            </div>
            """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "API Endpoints"}
        ]
        
        html = self._generate_html_template(
            "API Endpoints",
            content,
            "api_endpoints.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "api_endpoints.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            "API Endpoints",
            "Available API endpoints, parameters, authentication requirements, and response formats.",
            "api_endpoints.html",
            "API Endpoints"
        )
        
        logger.info("Generated api_endpoints.html")

    def _format_endpoint_html(self, endpoint: Dict[str, Any], data: Dict[str, Any], backend_url: str) -> str:
        """Format an API endpoint for HTML documentation

        Args:
            endpoint: Endpoint data
            data: Complete extracted data
            backend_url: Backend server URL for testing

        Returns:
            str: HTML for the endpoint
        """
        # Get basic endpoint info
        path = endpoint.get('path', '')
        http_methods = endpoint.get('http_methods', [])
        
        # Determine endpoint class for styling based on first method
        endpoint_class = http_methods[0].lower() if http_methods else ''
        
        # Create badges for HTTP methods
        method_badges = ""
        for method in http_methods:
            method_upper = method.upper()
            method_badges += f'<span class="badge badge-{method.lower()}">{method_upper}</span>'
        
        # Start endpoint HTML
        result = f"""
        <div class="endpoint-card {endpoint_class}">
            <h3><code>{path}</code> {method_badges}</h3>
        """
        
        # Add endpoint description from docstring
        view_info = endpoint.get('view', {})
        docstring = view_info.get('docstring', '')
        if not docstring and 'method_docstrings' in view_info:
            # Try to get method docstring for the first HTTP method
            for method in http_methods:
                if method in view_info.get('method_docstrings', {}):
                    docstring = view_info['method_docstrings'][method]
                    break

        if docstring:
            result += f"""
            <div class="endpoint-description">
                <h4>Description</h4>
                <p>{docstring}</p>
            </div>
            """
        
        # Add authentication requirements
        auth_info = endpoint.get('authentication', {})
        requires_auth = auth_info.get('requires_authentication', False)
        
        result += f"""
        <div class="endpoint-auth">
            <h4>Authentication</h4>
            <p><strong>Requires Authentication:</strong> {'Yes' if requires_auth else 'No'}</p>
        """
        
        if requires_auth and auth_info.get('permission_classes'):
            result += "<p><strong>Permission Classes:</strong></p><ul>"
            for permission in auth_info.get('permission_classes', []):
                result += f"<li><code>{permission.get('class', '')}</code></li>"
            result += "</ul>"
        
        result += """
        </div>
        """
        
        # Add query parameters
        query_params = endpoint.get('query_params', [])
        if query_params:
            result += """
            <div class="endpoint-params">
                <h4>Query Parameters</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for param in query_params:
                name = param.get('name', '')
                param_type = param.get('type', '')
                required = "Yes" if param.get('required', False) else "No"
                description = param.get('description', '')
                
                result += f"""
                    <tr>
                        <td><code>{name}</code></td>
                        <td>{param_type}</td>
                        <td>{required}</td>
                        <td>{description}</td>
                    </tr>
                """
            
            result += """
                    </tbody>
                </table>
            </div>
            """
        
        # Add response format from serializer
        serializer_info = endpoint.get('serializer', {})
        if serializer_info and 'fields' in serializer_info:
            result += """
            <div class="endpoint-response">
                <h4>Response Format</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Type</th>
                            <th>Read Only</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for field_name, field_info in sorted(serializer_info.get('fields', {}).items()):
                field_type = field_info.get('type', '')
                read_only = "Yes" if field_info.get('read_only', False) else "No"
                description = field_info.get('help_text', '')
                
                result += f"""
                    <tr>
                        <td><code>{field_name}</code></td>
                        <td>{field_type}</td>
                        <td>{read_only}</td>
                        <td>{description}</td>
                    </tr>
                """
            
            result += """
                    </tbody>
                </table>
            </div>
            """
        
        # Add example response if available from runtime tests
        if self.include_examples:
            runtime_tests = data.get('runtime_tests', {}).get('endpoints', {})
            if path in runtime_tests and runtime_tests[path].get('success', False):
                response_example = runtime_tests[path].get('response')
                if response_example:
                    # Format response as JSON
                    if isinstance(response_example, (dict, list)):
                        try:
                            response_str = json.dumps(response_example, indent=2)
                        except:
                            response_str = str(response_example)
                    else:
                        response_str = str(response_example)
                    
                    result += f"""
                    <div class="endpoint-example">
                        <h4>Example Response</h4>
                        <pre><code class="language-json">{response_str}</code></pre>
                    </div>
                    """
        
        # Add API testing interface if backend URL is provided
        if backend_url:
            form_id = f"test-form-{hash(path) & 0xFFFFFFFF}"
            
            result += f"""
            <div class="api-test-panel">
                <div class="api-test-header">Test Endpoint</div>
                <div class="api-test-content">
                    <form id="{form_id}" class="api-test-form" data-endpoint="{backend_url}{path}" data-method="{http_methods[0] if http_methods else 'GET'}">
            """
            
            # Add query parameters for testing
            if query_params:
                result += "<h5>Query Parameters</h5>"
                for param in query_params:
                    name = param.get('name', '')
                    required = param.get('required', False)
                    result += f'<div><label for="query-{name}">{name}{" (required)" if required else ""}:</label><input type="text" id="query-{name}" name="query-{name}" placeholder="{name}{" (required)" if required else ""}"></div>'
            
            # Add body parameters for POST/PUT/PATCH
            if any(method in ['POST', 'PUT', 'PATCH'] for method in http_methods):
                result += "<h5>Request Body</h5>"
                
                # If we have serializer fields, use them for the form
                if serializer_info and 'fields' in serializer_info:
                    for field_name, field_info in sorted(serializer_info.get('fields', {}).items()):
                        # Skip read-only fields for request body
                        if field_info.get('read_only', False):
                            continue
                            
                        field_type = field_info.get('type', '').lower()
                        
                        # Handle different field types
                        if 'file' in field_type or field_type == 'imagefield':
                            result += f'<div><label for="body-{field_name}">{field_name}:</label><input type="file" id="body-{field_name}" name="body-{field_name}"></div>'
                        elif field_type in ('textarea', 'textfield'):
                            result += f'<div><label for="body-{field_name}">{field_name}:</label><textarea id="body-{field_name}" name="body-{field_name}" placeholder="{field_name}"></textarea></div>'
                        else:
                            result += f'<div><label for="body-{field_name}">{field_name}:</label><input type="text" id="body-{field_name}" name="body-{field_name}" placeholder="{field_name}"></div>'
                else:
                    # Generic JSON body input
                    result += '<label for="body-data">Request Body JSON:</label><textarea name="body-data" id="body-data" placeholder="Enter request body as JSON"></textarea>'
            
            result += f"""
                    <button type="submit">Send Request</button>
                    </form>
                    <div id="{form_id}-response" class="api-test-response"></div>
                </div>
            </div>
            """
        
        # Close endpoint card
        result += """
        </div>
        """
        
        return result

    def _generate_authentication_documentation(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate authentication and authorization documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get authentication data
        auth_data = data.get('authentication', {})
        
        # Create content
        content = """
        <h1>Authentication and Authorization</h1>
        
        <p>This document describes the authentication and authorization mechanisms used in the system.</p>
        """
        
        # Add primary authentication method
        primary_method = auth_data.get('auth_flows', {}).get('primary_method', '')
        if primary_method:
            content += f"""
            <div class="card">
                <h2>Primary Authentication Method</h2>
                <p>The primary authentication method used in this system is <strong>{primary_method.upper()}</strong>.</p>
            </div>
            """
        
        # Add authentication flows
        auth_flows = auth_data.get('auth_flows', {})
        if auth_flows:
            content += """
            <div class="card">
                <h2>Supported Authentication Methods</h2>
            """
            
            if auth_flows.get('token_based_auth'):
                content += """
                <div class="endpoint-card">
                    <h3>Token Authentication</h3>
                    <p>The system supports token-based authentication. To authenticate:</p>
                    <ol>
                        <li>Obtain a token by sending credentials to the token endpoint</li>
                        <li>Include the token in the <code>Authorization</code> header with all subsequent requests</li>
                    </ol>
                    <pre><code class="language-http">Authorization: Token your_token_here</code></pre>
                </div>
                """
            
            if auth_flows.get('jwt_auth'):
                content += """
                <div class="endpoint-card">
                    <h3>JWT Authentication</h3>
                    <p>The system uses JSON Web Tokens (JWT) for authentication. The process is:</p>
                    <ol>
                        <li>Obtain access and refresh tokens by sending credentials to the JWT endpoint</li>
                        <li>Include the access token in the <code>Authorization</code> header with all requests</li>
                        <li>When the access token expires, use the refresh token to get a new one</li>
                    </ol>
                    <pre><code class="language-http">Authorization: Bearer your_jwt_access_token</code></pre>
                """
                
                # Add JWT settings if available
                jwt_settings = auth_data.get('jwt_auth', {})
                if jwt_settings:
                    token_lifetime = jwt_settings.get('access_token_lifetime', '')
                    refresh_lifetime = jwt_settings.get('refresh_token_lifetime', '')
                    
                    content += """
                    <h4>Token Lifetimes:</h4>
                    <ul>
                    """
                    
                    if token_lifetime:
                        content += f"<li><strong>Access Token:</strong> {token_lifetime}</li>"
                    if refresh_lifetime:
                        content += f"<li><strong>Refresh Token:</strong> {refresh_lifetime}</li>"
                    
                    content += """
                    </ul>
                    """
                
                content += """
                </div>
                """
            
            if auth_flows.get('session_auth'):
                content += """
                <div class="endpoint-card">
                    <h3>Session Authentication</h3>
                    <p>The system supports session-based authentication for browser clients.
                    This method uses cookies to maintain the session state.</p>
                </div>
                """
            
            if auth_flows.get('oauth2'):
                content += """
                <div class="endpoint-card">
                    <h3>OAuth2</h3>
                    <p>The system supports OAuth2 for authentication with external providers.</p>
                </div>
                """
            
            if auth_flows.get('basic_auth'):
                content += """
                <div class="endpoint-card">
                    <h3>Basic Authentication</h3>
                    <p>The system supports HTTP Basic Authentication. To authenticate:</p>
                    <pre><code class="language-http">Authorization: Basic base64(username:password)</code></pre>
                    <p><em>Note: Basic authentication should only be used over HTTPS.</em></p>
                </div>
                """
            
            content += """
            </div>
            """
        
        # Add permission classes
        permission_classes = auth_data.get('permission_classes', [])
        if permission_classes:
            content += """
            <div class="card">
                <h2>Permission Classes</h2>
                <p>The system uses the following permission classes to control access:</p>
            """
            
            for permission in permission_classes:
                name = permission.get('name', '')
                docstring = permission.get('docstring', '')
                
                content += f"""
                <div class="endpoint-card">
                    <h3>{name}</h3>
                    <p>{docstring}</p>
                </div>
                """
            
            content += """
            </div>
            """
        
        # Add authentication endpoints
        content += """
        <div class="card">
            <h2>Authentication Endpoints</h2>
            <h3>Login and Token Acquisition</h3>
        """
        
        # Add JWT endpoints if used
        if auth_flows.get('jwt_auth'):
            content += """
            <h4>JWT Authentication Endpoints</h4>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>/api/token/</code></td>
                        <td>POST</td>
                        <td>Obtain JWT access and refresh tokens</td>
                    </tr>
                    <tr>
                        <td><code>/api/token/refresh/</code></td>
                        <td>POST</td>
                        <td>Refresh JWT access token</td>
                    </tr>
                    <tr>
                        <td><code>/api/token/verify/</code></td>
                        <td>POST</td>
                        <td>Verify JWT token validity</td>
                    </tr>
                </tbody>
            </table>
            """
        
        # Add token endpoints if used
        if auth_flows.get('token_based_auth'):
            content += """
            <h4>Token Authentication Endpoints</h4>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>/api/auth-token/</code></td>
                        <td>POST</td>
                        <td>Obtain authentication token</td>
                    </tr>
                </tbody>
            </table>
            """
        
        # Add session endpoints if used
        if auth_flows.get('session_auth'):
            content += """
            <h4>Session Authentication Endpoints</h4>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>/accounts/login/</code></td>
                        <td>POST</td>
                        <td>Log in and create session</td>
                    </tr>
                    <tr>
                        <td><code>/accounts/logout/</code></td>
                        <td>POST</td>
                        <td>Log out and destroy session</td>
                    </tr>
                </tbody>
            </table>
            """
        
        content += """
        </div>
        """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "Authentication and Authorization"}
        ]
        
        html = self._generate_html_template(
            "Authentication and Authorization",
            content,
            "authentication.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "authentication.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            "Authentication and Authorization",
            "Authentication flows, permission classes, and security mechanisms used in the API.",
            "authentication.html",
            "Authentication"
        )
        
        logger.info("Generated authentication.html")

    def _generate_frontend_integration(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate frontend integration documentation

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Get authentication data
        auth_data = data.get('authentication', {})
        primary_auth_method = auth_data.get('auth_flows', {}).get('primary_method', '')
        
        # Create content
        content = """
        <h1>Frontend Integration Guide</h1>
        
        <p>This document provides guidelines and examples for integrating the backend with frontend applications.</p>
        
        <div class="card">
            <h2>API Base URL</h2>
            <p>All API endpoints are relative to the base URL of the backend server. For example, if the backend is hosted at <code>https://api.example.com</code>, then the full URL for an endpoint would be <code>https://api.example.com/api/endpoint/</code>.</p>
        </div>
        
        <div class="card">
            <h2>Authentication Integration</h2>
        """
        
        # Add authentication integration details based on primary method
        if primary_auth_method == 'jwt':
            content += """
            <div class="endpoint-card">
                <h3>JWT Authentication</h3>
                <p>This backend uses JSON Web Tokens (JWT) for authentication. Here's how to implement it in your frontend:</p>
                
                <h4>1. Login and Token Storage</h4>
                <pre><code class="language-javascript">// Example using fetch API
async function login(username, password) {
  try {
    const response = await fetch('/api/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store tokens securely
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      return true;
    } else {
      // Handle error
      console.error('Login failed:', data);
      return false;
    }
  } catch (error) {
    console.error('Login error:', error);
    return false;
  }
}</code></pre>

                <h4>2. Authenticated Requests</h4>
                <pre><code class="language-javascript">// Example of making authenticated API calls
async function fetchData(url) {
  const accessToken = localStorage.getItem('accessToken');

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 401) {
      // Token expired, try to refresh
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry the request with the new token
        return fetchData(url);
      } else {
        // Refresh failed, redirect to login
        redirectToLogin();
        return null;
      }
    }

    return response.json();
  } catch (error) {
    console.error('API request failed:', error);
    return null;
  }
}</code></pre>

                <h4>3. Token Refresh</h4>
                <pre><code class="language-javascript">// Example of refreshing the JWT token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');

  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch('/api/token/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access);
      return true;
    } else {
      // Refresh failed, clear tokens
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      return false;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
}</code></pre>
            </div>
            """
        elif primary_auth_method == 'token':
            content += """
            <div class="endpoint-card">
                <h3>Token Authentication</h3>
                <p>This backend uses token-based authentication. Here's how to implement it in your frontend:</p>
                
                <h4>1. Login and Token Storage</h4>
                <pre><code class="language-javascript">// Example using fetch API
async function login(username, password) {
  try {
    const response = await fetch('/api/auth-token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store token securely
      localStorage.setItem('authToken', data.token);
      return true;
    } else {
      // Handle error
      console.error('Login failed:', data);
      return false;
    }
  } catch (error) {
    console.error('Login error:', error);
    return false;
  }
}</code></pre>

                <h4>2. Authenticated Requests</h4>
                <pre><code class="language-javascript">// Example of making authenticated API calls
async function fetchData(url) {
  const authToken = localStorage.getItem('authToken');

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Token ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 401) {
      // Token expired, redirect to login
      redirectToLogin();
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('API request failed:', error);
    return null;
  }
}</code></pre>
            </div>
            """
        elif primary_auth_method == 'session':
            content += """
            <div class="endpoint-card">
                <h3>Session Authentication</h3>
                <p>This backend uses session-based authentication. Here's how to implement it in your frontend:</p>
                
                <h4>1. Login</h4>
                <pre><code class="language-javascript">// Example using fetch API with credentials
async function login(username, password) {
  try {
    const response = await fetch('/accounts/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
      // Important for session cookies
      credentials: 'include',
    });

    if (response.ok) {
      return true;
    } else {
      // Handle error
      console.error('Login failed');
      return false;
    }
  } catch (error) {
    console.error('Login error:', error);
    return false;
  }
}</code></pre>

                <h4>2. Authenticated Requests</h4>
                <pre><code class="language-javascript">// Example of making authenticated API calls with session
async function fetchData(url) {
  try {
    const response = await fetch(url, {
      // Important for session cookies
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 403 || response.status === 401) {
      // Session expired, redirect to login
      redirectToLogin();
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('API request failed:', error);
    return null;
  }
}</code></pre>
            </div>
            """
        else:
            content += """
            <div class="endpoint-card">
                <h3>Authentication</h3>
                <p>Check the <a href="authentication.html">Authentication</a> section for details on the authentication system.</p>
            </div>
            """
        
        content += """
        </div>
        
        <div class="card">
            <h2>Data Fetching Patterns</h2>
            
            <div class="endpoint-card">
                <h3>Handling Paginated Responses</h3>
                <p>Many API endpoints return paginated results. Here's how to handle them:</p>
                <pre><code class="language-javascript">// Example of fetching paginated data
async function fetchPaginatedData(baseUrl) {
  let url = baseUrl;
  let allResults = [];

  while (url) {
    const response = await fetchData(url);
    
    if (!response) break;
    
    // Add results to the array
    allResults = [...allResults, ...response.results];
    
    // Update URL to next page or null
    url = response.next;
  }
  
  return allResults;
}</code></pre>
            </div>
            
            <div class="endpoint-card">
                <h3>Error Handling</h3>
                <p>It's important to handle errors consistently in your frontend application:</p>
                <pre><code class="language-javascript">// Example of API call with comprehensive error handling
async function apiRequest(url, options = {}) {
  try {
    // Set default headers and credentials
    const requestOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(getAuthHeader()), // Get auth header based on your auth method
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, requestOptions);

    // Parse the response based on content type
    const contentType = response.headers.get('content-type');
    let data;

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle different response statuses
    if (response.ok) {
      return { success: true, data, status: response.status };
    } else {
      // Handle specific error codes
      if (response.status === 401) {
        // Handle authentication errors
        handleAuthError();
      }

      return {
        success: false,
        error: data,
        status: response.status,
        message: data.detail || data.message || 'An error occurred',
      };
    }
  } catch (error) {
    // Handle network errors
    return {
      success: false,
      error,
      message: 'Network error',
    };
  }
}</code></pre>
            </div>
        </div>
        
        <div class="card">
            <h2>React Integration</h2>
            
            <div class="endpoint-card">
                <h3>React Hooks for API Calls</h3>
                <p>Here are some example React hooks for interacting with the API:</p>
                <h4>useFetch Hook</h4>
                <pre><code class="language-jsx">import { useState, useEffect } from 'react';

export function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refetchIndex, setRefetchIndex] = useState(0);

  const refetch = () => setRefetchIndex(prev => prev + 1);

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    const signal = controller.signal;

    const fetchData = async () => {
      setLoading(true);

      try {
        // Add auth header to options
        const authHeader = getAuthHeader();
        const fetchOptions = {
          ...options,
          headers: {
            ...options.headers,
            ...authHeader,
          },
          signal,
        };

        const response = await fetch(url, fetchOptions);
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || 'An error occurred');
        }

        if (isMounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (isMounted && err.name !== 'AbortError') {
          setError(err.message);
          setData(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [url, refetchIndex, JSON.stringify(options)]);

  return { data, loading, error, refetch };
}</code></pre>

                <h4>Usage Example</h4>
                <pre><code class="language-jsx">function UserList() {
  const { data, loading, error } = useFetch('/api/users/');

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {data?.results.map(user => (
        <li key={user.id}>{user.username}</li>
      ))}
    </ul>
  );
}</code></pre>
            </div>
        </div>
        
        <div class="card">
            <h2>File Upload</h2>
            
            <div class="endpoint-card">
                <h3>Uploading Files</h3>
                <p>For file uploads, use the following pattern:</p>
                <pre><code class="language-javascript">async function uploadFile(file, url) {
  const formData = new FormData();
  formData.append('file', file);

  const authHeader = getAuthHeader();

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...authHeader,
        // Do NOT set Content-Type when using FormData
        // Browser will set it automatically with boundary
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('File upload failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}</code></pre>
            </div>
        </div>
        
        <div class="card">
            <h2>Best Practices</h2>
            
            <div class="endpoint-card">
                <h3>State Management</h3>
                <p>For complex applications, consider using a state management library:</p>
                <ul>
                    <li><strong>Redux Toolkit</strong>: For large applications with complex state</li>
                    <li><strong>Zustand</strong>: For simpler applications with less boilerplate</li>
                    <li><strong>React Context</strong>: For small to medium applications</li>
                </ul>
            </div>
            
            <div class="endpoint-card">
                <h3>TypeScript Integration</h3>
                <p>Use the TypeScript interfaces generated in the <code>typescript</code> directory to ensure type safety:</p>
                <pre><code class="language-typescript">// Example usage of generated types
import { User, UserResponse } from '../types/api';

async function fetchUserById(userId: number): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${userId}/`);
    const data: UserResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user:', error);
    return null;
  }
}</code></pre>
            </div>
            
            <div class="endpoint-card">
                <h3>Performance Optimization</h3>
                <ul>
                    <li>Use <code>React.memo</code> for components that render frequently with the same props</li>
                    <li>Implement request caching for frequently used data</li>
                    <li>Use pagination and infinite scrolling for large data sets</li>
                    <li>Implement debouncing for search inputs and other frequent user interactions</li>
                </ul>
            </div>
        </div>
        """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "Frontend Integration Guide"}
        ]
        
        html = self._generate_html_template(
            "Frontend Integration Guide",
            content,
            "frontend_integration.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "frontend_integration.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            "Frontend Integration Guide",
            "Guidelines and examples for integrating frontend applications with the backend API.",
            "frontend_integration.html",
            "Frontend Integration"
        )
        
        logger.info("Generated frontend_integration.html")

    def _generate_typescript_overview(self, data: Dict[str, Any], output_dir: Path) -> None:
        """Generate documentation about TypeScript interfaces

        Args:
            data: Extracted data from backend analysis
            output_dir: Directory where HTML files will be generated
        """
        # Create content
        content = """
        <h1>TypeScript Interfaces</h1>
        
        <p>This document describes the TypeScript interfaces generated for this backend.</p>
        
        <div class="card">
            <h2>Using TypeScript Interfaces</h2>
            <p>TypeScript interfaces that match the backend models and API responses have been generated in the <code>typescript</code> directory. These interfaces can be imported into your frontend project to ensure type safety when working with API data.</p>
            
            <h3>Example Usage</h3>
            <pre><code class="language-typescript">// Import model interfaces
import { User, Post, Comment } from './interfaces';

// Type-safe API response handling
async function fetchUsers(): Promise<User[]> {
  const response = await fetch('/api/users/');
  const data = await response.json();
  return data.results as User[];
}

// Component with typed props
function UserCard({ user }: { user: User }) {
  return (
    <div>
      <h2>{user.username}</h2>
      <p>{user.email}</p>
    </div>
  );
}</code></pre>
        </div>
        
        <div class="card">
            <h2>Interface Files</h2>
            <p>The following TypeScript interface files have been generated:</p>
            <ul>
                <li><code>models.ts</code> - Interfaces for all database models</li>
                <li><code>api.ts</code> - Interfaces for API requests and responses</li>
                <li><code>enums.ts</code> - Enumerated types from model choices</li>
                <li><code>index.ts</code> - Barrel file exporting all interfaces</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Customizing Types</h2>
            <p>If you need to extend or modify the generated types, create a separate file with your custom types rather than editing the generated files directly. This will allow you to regenerate the interfaces when the backend changes without losing your customizations.</p>
            
            <h3>Example Custom Types</h3>
            <pre><code class="language-typescript">// custom-types.ts
import { User } from './interfaces';

// Extend a generated interface
export interface UserWithPermissions extends User {
  hasAdminAccess: boolean;
  permissions: string[];
}

// Create a utility type
export type EntityID = number | string;

// Create a generic response type
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}</code></pre>
        </div>
        """
        
        # Generate HTML
        breadcrumbs = [
            {"title": "TypeScript Interfaces"}
        ]
        
        html = self._generate_html_template(
            "TypeScript Interfaces",
            content,
            "typescript_interfaces.html",
            breadcrumbs
        )
        
        # Write file
        output_path = output_dir / "typescript_interfaces.html"
        with open(output_path, 'w') as f:
            f.write(html)
            
        # Add to search data
        self._add_to_search_data(
            "TypeScript Interfaces",
            "TypeScript interfaces generated from backend models and API responses for type-safe frontend development.",
            "typescript_interfaces.html",
            "TypeScript Interfaces"
        )
        
        logger.info("Generated typescript_interfaces.html")