"""
Command-line interface for Django Backend Analyzer.

This module provides a command-line interface for running the analyzer
and generating reports.
"""

import os
import sys
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .analyzer import BackendAnalyzer
from .utils import setup_logging
from . import __version__

logger = logging.getLogger('backend_analyzer')


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Django backend for frontend integration"
    )
    
    parser.add_argument(
        '--backend_path', 
        type=str, 
        default='.',
        help='Path to the Django backend directory'
    )
    
    parser.add_argument(
        '--output_file', 
        type=str, 
        default='backend_analysis_report.md',
        help='Output file path'
    )
    
    parser.add_argument(
        '--output_format', 
        type=str, 
        default='markdown', 
        choices=['markdown', 'json'],
        help='Output format (markdown or json)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--log_file',
        type=str,
        help='Path to log file'
    )
    
    parser.add_argument(
        '--include_code_samples', 
        action='store_true',
        help='Include sample code in the report'
    )
    
    parser.add_argument(
        '--exclude_apps', 
        type=str, 
        nargs='+', 
        default=[],
        help='List of app names to exclude from analysis'
    )
    
    parser.add_argument(
        '--max_issues_to_show', 
        type=int, 
        default=100,
        help='Maximum number of issues to include in the report'
    )
    
    # Django reflection flags (mutually exclusive)
    reflection_group = parser.add_mutually_exclusive_group()
    reflection_group.add_argument(
        '--use_django_reflection', 
        action='store_true',
        help='Use Django introspection APIs (runs Django project)'
    )
    reflection_group.add_argument(
        '--no_django_reflection', 
        action='store_false', 
        dest='use_django_reflection',
        help='Disable Django introspection (use static analysis only)'
    )
    parser.set_defaults(use_django_reflection=True)
    
    parser.add_argument(
        '--use_subprocess_isolation',
        action='store_true',
        help='Use subprocess isolation for Django reflection to prevent side effects'
    )
    
    parser.add_argument(
        '--subprocess_timeout',
        type=int,
        default=30,
        help='Timeout for subprocess in seconds'
    )
    
    parser.add_argument(
        '--fail_on_error', 
        action='store_true',
        help='Exit with error code if critical issues are found'
    )
    
    parser.add_argument(
        '--output_openapi', 
        action='store_true',
        help='Generate OpenAPI schema and save to file'
    )
    
    parser.add_argument(
        '--openapi_file', 
        type=str, 
        default='openapi_schema.json',
        help='Output file path for OpenAPI schema'
    )
    
    parser.add_argument(
        '--output_typescript', 
        action='store_true',
        help='Generate TypeScript interfaces and React Query hooks'
    )
    
    parser.add_argument(
        '--typescript_file', 
        type=str, 
        default='api_types.ts',
        help='Output file path for TypeScript interfaces'
    )
    
    parser.add_argument(
        '--config_file', 
        type=str,
        help='Path to configuration file (JSON, TOML, or YAML)'
    )
    
    parser.add_argument(
        '--generate_config', 
        action='store_true',
        help='Generate a sample configuration file'
    )
    
    parser.add_argument(
        '--config_output', 
        type=str, 
        default='backend_analyzer_config.json',
        help='Output path for the sample configuration file'
    )
    
    parser.add_argument(
        '--plugins', 
        type=str, 
        nargs='+', 
        default=[],
        help='List of plugin module paths to load (format: package.module.PluginClass)'
    )
    
    parser.add_argument(
        '--plugins_config', 
        type=str,
        help='Path to plugins configuration file (JSON)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='Show version information and exit'
    )
    
    return parser.parse_args()


def generate_sample_config(output_file: str) -> bool:
    """Generate a sample configuration file."""
    logger.info(f"Generating sample configuration file: {output_file}")
    
    example_config = {
        "analysis": {
            "exclude_apps": ["admin", "auth", "contenttypes", "sessions"],
            "max_issues_to_show": 100
        },
        "output": {
            "include_code_samples": True,
            "output_format": "markdown",
            "output_file": "backend_analysis_report.md"
        },
        "django": {
            "use_reflection": True,
            "analyzer_mode": True,
            "use_subprocess_isolation": True,
            "subprocess_timeout": 30
        },
        "openapi": {
            "enabled": True,
            "output_file": "openapi_schema.json"
        },
        "typescript": {
            "enabled": True,
            "output_file": "api_types.ts"
        },
        "plugins": {
            "enabled": True,
            "paths": [
                "my_package.my_module.MyPlugin"
            ],
            "config": {
                "my_package.my_module.MyPlugin": {
                    "option1": "value1",
                    "option2": "value2"
                }
            }
        }
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        logger.success(f"Sample configuration file generated: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error generating sample configuration file: {str(e)}")
        return False


def merge_config_with_args(args: argparse.Namespace, config_file: str) -> argparse.Namespace:
    """Merge command line arguments with configuration file."""
    if not config_file or not os.path.exists(config_file):
        return args
    
    try:
        with open(config_file, 'r') as f:
            if config_file.endswith('.json'):
                config = json.load(f)
            elif config_file.endswith(('.toml', '.tml')):
                import toml
                config = toml.load(f)
            elif config_file.endswith(('.yaml', '.yml')):
                import yaml
                config = yaml.safe_load(f)
            else:
                logger.warning(f"Unknown config file format: {config_file}")
                return args
        
        # Create a new namespace to store merged arguments
        merged_args = argparse.Namespace()
        
        # Copy all args to merged_args
        for key, value in vars(args).items():
            setattr(merged_args, key, value)
        
        # Override with config values if not explicitly set in args
        arg_data = vars(args)
        
        # Analysis section
        if 'analysis' in config:
            if 'exclude_apps' in config['analysis'] and not arg_data.get('exclude_apps'):
                setattr(merged_args, 'exclude_apps', config['analysis']['exclude_apps'])
            if 'max_issues_to_show' in config['analysis'] and not arg_data.get('max_issues_to_show'):
                setattr(merged_args, 'max_issues_to_show', config['analysis']['max_issues_to_show'])
        
        # Output section
        if 'output' in config:
            if 'include_code_samples' in config['output'] and not arg_data.get('include_code_samples'):
                setattr(merged_args, 'include_code_samples', config['output']['include_code_samples'])
            if 'output_format' in config['output'] and not arg_data.get('output_format'):
                setattr(merged_args, 'output_format', config['output']['output_format'])
            if 'output_file' in config['output'] and not arg_data.get('output_file'):
                setattr(merged_args, 'output_file', config['output']['output_file'])
        
        # Django section
        if 'django' in config:
            if 'use_reflection' in config['django'] and not arg_data.get('use_django_reflection'):
                setattr(merged_args, 'use_django_reflection', config['django']['use_reflection'])
            if 'use_subprocess_isolation' in config['django'] and not arg_data.get('use_subprocess_isolation'):
                setattr(merged_args, 'use_subprocess_isolation', config['django']['use_subprocess_isolation'])
            if 'subprocess_timeout' in config['django'] and not arg_data.get('subprocess_timeout'):
                setattr(merged_args, 'subprocess_timeout', config['django']['subprocess_timeout'])
        
        # OpenAPI section
        if 'openapi' in config:
            if 'enabled' in config['openapi'] and not arg_data.get('output_openapi'):
                setattr(merged_args, 'output_openapi', config['openapi']['enabled'])
            if 'output_file' in config['openapi'] and not arg_data.get('openapi_file'):
                setattr(merged_args, 'openapi_file', config['openapi']['output_file'])
        
        # TypeScript section
        if 'typescript' in config:
            if 'enabled' in config['typescript'] and not arg_data.get('output_typescript'):
                setattr(merged_args, 'output_typescript', config['typescript']['enabled'])
            if 'output_file' in config['typescript'] and not arg_data.get('typescript_file'):
                setattr(merged_args, 'typescript_file', config['typescript']['output_file'])
        
        # Plugins section
        if 'plugins' in config:
            if 'enabled' in config['plugins'] and not arg_data.get('plugins'):
                setattr(merged_args, 'plugins', config['plugins']['enabled'])
            if 'paths' in config['plugins'] and not arg_data.get('plugins_paths'):
                setattr(merged_args, 'plugins_paths', config['plugins']['paths'])
            if 'config' in config['plugins'] and not arg_data.get('plugins_config'):
                setattr(merged_args, 'plugins_config', config['plugins']['config'])
        
        logger.info(f"Merged configuration from {config_file}")
        return merged_args
    
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {str(e)}")
        return args


def load_plugins(plugin_paths, config_file=None):
    """
    Load plugins from the specified paths.
    
    Args:
        plugin_paths: List of plugin module paths (format: package.module.PluginClass)
        config_file: Optional path to plugin configuration file
        
    Returns:
        List of initialized plugin instances
    """
    plugins = []
    
    # Load plugin config if provided
    plugin_config = {}
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                plugin_config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading plugin config file: {str(e)}")
    
    # Load each plugin
    for plugin_path in plugin_paths:
        try:
            # Split the path into module path and class name
            module_path, class_name = plugin_path.rsplit('.', 1)
            
            # Import the module
            module = __import__(module_path, fromlist=[class_name])
            
            # Get the plugin class
            plugin_class = getattr(module, class_name)
            
            # Create an instance with config if available
            plugin_instance = None
            if plugin_path in plugin_config:
                plugin_instance = plugin_class(**plugin_config[plugin_path])
            else:
                plugin_instance = plugin_class()
            
            plugins.append(plugin_instance)
            logger.info(f"Loaded plugin: {plugin_path}")
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
    return plugins


def main():
    """Main entry point for the command-line interface."""
    try:
        args = parse_args()
        
        # If just generating config, do that and exit
        if args.generate_config:
            generate_sample_config(args.config_output)
            print(f"Sample configuration generated: {args.config_output}")
            return 0
        
        # Setup basic logging
        setup_logging(verbose=args.verbose, log_file=args.log_file)
        
        # Merge config with args if provided
        if args.config_file:
            args = merge_config_with_args(args, args.config_file)
        
        # Load plugins if specified
        plugins = []
        if args.plugins:
            plugins = load_plugins(args.plugins, args.plugins_config)
        
        logger.info(f"Analyzing Django backend at: {args.backend_path}")
        analyzer = BackendAnalyzer(
            backend_path=args.backend_path,
            verbose=args.verbose,
            exclude_apps=args.exclude_apps,
            max_issues_to_show=args.max_issues_to_show,
            use_django_reflection=args.use_django_reflection,
            use_subprocess_isolation=args.use_subprocess_isolation,
            subprocess_timeout=args.subprocess_timeout,
            fail_on_error=args.fail_on_error,
            output_openapi=args.output_openapi,
            output_typescript=args.output_typescript,
            config_file=args.config_file,
            log_file=args.log_file,
            plugins=plugins
        )
        
        # Run the analysis
        analysis_data = analyzer.analyze()
        
        # Check for errors in analysis
        if 'error' in analysis_data:
            logger.error(f"Analysis failed: {analysis_data['error']}")
            return 1
        
        # Check for critical errors
        critical_errors = [i for i in analysis_data.get('backend_compatibility', {}).get('issues', []) 
                          if i.get('severity') == 'error']
        
        if args.include_code_samples:
            code_samples = analyzer.generate_code_samples()
            analysis_data['code_samples'] = code_samples
        
        # Generate the report
        from .reporting.report_generator import generate_report, save_report
        report = generate_report(analysis_data, args.output_format, args.max_issues_to_show)
        
        # Save the report
        save_report(report, args.output_file)
        print(f"Report generated: {args.output_file}")
        
        # Generate OpenAPI schema if requested
        if args.output_openapi:
            from .reporting.openapi_generator import generate_openapi_schema
            schema = generate_openapi_schema(analysis_data)
            if schema:
                with open(args.openapi_file, 'w') as f:
                    json.dump(schema, f, indent=2)
                print(f"OpenAPI schema generated: {args.openapi_file}")
            else:
                logger.warning("Failed to generate OpenAPI schema")
        
        # Generate TypeScript interfaces if requested
        if args.output_typescript:
            from .reporting.typescript_generator import generate_typescript
            typescript_output = generate_typescript(analysis_data)
            if typescript_output:
                # Save interfaces
                ts_file = args.typescript_file
                with open(ts_file, 'w') as f:
                    f.write(typescript_output['typescript_interfaces'])
                
                # Save services in a separate file
                ts_services_file = ts_file.replace('.ts', '.services.ts')
                with open(ts_services_file, 'w') as f:
                    f.write(typescript_output['typescript_services'])
                
                print(f"TypeScript interfaces generated: {ts_file}")
                print(f"TypeScript services generated: {ts_services_file}")
            else:
                logger.warning("Failed to generate TypeScript interfaces")
        
        # Exit with error code if critical errors found and fail_on_error is set
        if args.fail_on_error and critical_errors:
            print(f"Critical errors found: {len(critical_errors)}")
            return 1
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main()) 