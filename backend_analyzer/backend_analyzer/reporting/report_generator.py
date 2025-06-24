"""
Report generation module for Django backend analysis.

This module provides classes and functions for generating reports in
different formats based on analysis data.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger('backend_analyzer')


class ReportGenerator:
    """Base class for report generators."""
    
    def __init__(self, analysis_data: Dict[str, Any], max_issues: int = 100):
        """
        Initialize the report generator.
        
        Args:
            analysis_data: Data from backend analysis
            max_issues: Maximum number of issues to include in report
        """
        self.analysis_data = analysis_data
        self.max_issues = max_issues
        
    def generate(self) -> str:
        """Generate the report as a string. Should be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate()")


class MarkdownReportGenerator(ReportGenerator):
    """Generator for Markdown format reports."""
    
    def generate(self) -> str:
        """Generate a Markdown report."""
        lines = []
        
        # Report header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append("# Django Backend Analysis Report")
        lines.append(f"Generated: {timestamp}")
        lines.append("")
        
        # Metadata section
        metadata = self.analysis_data.get('metadata', {})
        django_version = metadata.get('django_version', 'Unknown')
        drf_version = metadata.get('drf_version', 'Unknown')
        
        lines.append("## System Information")
        lines.append(f"- **Django Version**: {django_version}")
        lines.append(f"- **DRF Version**: {drf_version}")
        lines.append(f"- **Analyzer Version**: {metadata.get('script_version', 'Unknown')}")
        if metadata.get('excluded_apps'):
            lines.append(f"- **Excluded Apps**: {', '.join(metadata.get('excluded_apps', []))}")
        lines.append("")
        
        # API Endpoints section
        frontend_data = self.analysis_data.get('frontend_data', {})
        api_endpoints = frontend_data.get('api_endpoints', [])
        
        lines.append("## API Endpoints")
        if api_endpoints:
            lines.append(f"Found {len(api_endpoints)} API endpoints.")
            lines.append("")
            lines.append("| Method | URL | View | Model | Serializer |")
            lines.append("|--------|-----|------|-------|------------|")
            
            for endpoint in api_endpoints:
                method = endpoint.get('method', '')
                path = endpoint.get('path', '')
                view = endpoint.get('view', '')
                model = endpoint.get('model', '-')
                serializer = endpoint.get('serializer', '-')
                
                lines.append(f"| {method} | {path} | {view} | {model} | {serializer} |")
        else:
            lines.append("No API endpoints found.")
        lines.append("")
        
        # Data Models section
        data_models = frontend_data.get('data_models', {})
        
        lines.append("## Data Models")
        if data_models:
            lines.append(f"Found {len(data_models)} data models.")
            lines.append("")
            
            for model_name, model_info in data_models.items():
                app_name = model_info.get('app_name', '')
                model_name_only = model_info.get('name', '')
                
                lines.append(f"### {app_name}.{model_name_only}")
                
                # Fields table
                lines.append("#### Fields")
                lines.append("| Name | Type | Options |")
                lines.append("|------|------|---------|")
                
                for field in model_info.get('fields', []):
                    field_name = field.get('name', '')
                    field_type = field.get('field_type', '')
                    
                    options_str = ''
                    if field.get('options'):
                        options_list = []
                        for key, value in field.get('options', {}).items():
                            options_list.append(f"{key}={value}")
                        options_str = ', '.join(options_list)
                    
                    lines.append(f"| {field_name} | {field_type} | {options_str} |")
                
                # Relationships
                if model_info.get('relationships'):
                    lines.append("")
                    lines.append("#### Relationships")
                    lines.append("| Field Name | Type | Related Model | Related Name |")
                    lines.append("|------------|------|--------------|--------------|")
                    
                    for rel in model_info.get('relationships', []):
                        field_name = rel.get('field_name', '')
                        rel_type = rel.get('relation_type', '')
                        related_model = rel.get('related_model', '')
                        related_name = rel.get('related_name', '-')
                        
                        lines.append(f"| {field_name} | {rel_type} | {related_model} | {related_name} |")
                
                lines.append("")
        else:
            lines.append("No data models found.")
        lines.append("")
        
        # Serializers section
        serializers = self.analysis_data.get('frontend_data', {}).get('serializers', {})
        
        lines.append("## Serializers")
        if serializers:
            lines.append(f"Found {len(serializers)} serializers.")
            lines.append("")
            
            for serializer_name, serializer_info in serializers.items():
                model = serializer_info.get('model', '-')
                
                lines.append(f"### {serializer_name}")
                lines.append(f"- **Model**: {model}")
                
                # Fields
                if serializer_info.get('fields'):
                    lines.append("- **Fields**: " + ", ".join(serializer_info.get('fields', [])))
                
                # Read-only fields
                if serializer_info.get('read_only_fields'):
                    lines.append("- **Read-only Fields**: " + ", ".join(serializer_info.get('read_only_fields', [])))
                
                # Write-only fields
                if serializer_info.get('write_only_fields'):
                    lines.append("- **Write-only Fields**: " + ", ".join(serializer_info.get('write_only_fields', [])))
                
                lines.append("")
        else:
            lines.append("No serializers found.")
        lines.append("")
        
        # Issues section
        issues = self.analysis_data.get('backend_compatibility', {}).get('issues', [])
        
        lines.append("## Compatibility Issues")
        if issues:
            limited_issues = issues[:self.max_issues]
            lines.append(f"Found {len(issues)} issues (showing {len(limited_issues)}).")
            lines.append("")
            
            for issue in limited_issues:
                severity = issue.get('severity', 'info').upper()
                issue_type = issue.get('issue_type', '')
                description = issue.get('description', '')
                
                lines.append(f"- **[{severity}]** ({issue_type}) {description}")
            
            if len(issues) > self.max_issues:
                lines.append(f"... and {len(issues) - self.max_issues} more issues (increase max_issues_to_show to see more)")
        else:
            lines.append("No compatibility issues found.")
        lines.append("")
        
        # ER Diagram section
        er_diagram = frontend_data.get('er_diagram', '')
        
        if er_diagram:
            lines.append("## Entity-Relationship Diagram")
            lines.append(er_diagram)
            lines.append("")
        
        return "\n".join(lines)


class JSONReportGenerator(ReportGenerator):
    """Generator for JSON format reports."""
    
    def generate(self) -> str:
        """Generate a JSON report."""
        # Add timestamp to the data
        report_data = self.analysis_data.copy()
        report_data['report_generated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Limit issues if needed
        if 'backend_compatibility' in report_data and 'issues' in report_data['backend_compatibility']:
            issues = report_data['backend_compatibility']['issues']
            if len(issues) > self.max_issues:
                report_data['backend_compatibility']['issues'] = issues[:self.max_issues]
                report_data['backend_compatibility']['issues_truncated'] = True
                report_data['backend_compatibility']['total_issues'] = len(issues)
        
        # Convert to JSON string with proper formatting
        return json.dumps(report_data, indent=2)


def generate_report(analysis_data: Dict[str, Any], output_format: str = 'markdown', 
                    max_issues: int = 100) -> str:
    """
    Generate a report in the specified format.
    
    Args:
        analysis_data: Data from backend analysis
        output_format: Format of the report ('markdown' or 'json')
        max_issues: Maximum number of issues to include in report
        
    Returns:
        The generated report as a string
    """
    if output_format == 'json':
        generator = JSONReportGenerator(analysis_data, max_issues)
    else:
        # Default to markdown
        generator = MarkdownReportGenerator(analysis_data, max_issues)
    
    return generator.generate()


def save_report(report: str, output_file: str) -> bool:
    """
    Save a report to a file.
    
    Args:
        report: The report string
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.success(f"Report saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving report to {output_file}: {str(e)}")
        return False 