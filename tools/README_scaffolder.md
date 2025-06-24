# Django Backend Super-Scaffolder

A zero-touch system for scaffolding complete Django REST framework backends for complex domains with minimal configuration.

## Features

- **Zero-touch operation**: Generate complete API backends with one command
- **Intelligent relationship handling**: Automatically detects and configures model relationships
- **Customizable templates**: Extend the default templates to match your project requirements
- **Post-generation formatting**: Automatically format generated code to maintain project standards
- **Parallel processing**: Process multiple apps simultaneously for faster generation
- **Configuration-driven**: Control all aspects of generation via YAML configuration
- **Comprehensive documentation**: Generates frontend bible documentation and OpenAPI specs
- **Visual model diagrams**: Generate SVG diagrams of your model relationships
- **Thread-safe operations**: Safe for parallel execution with no race conditions

## Quick Start

```bash
# Install dependencies
pip install django djangorestframework django-filter jinja2 pyyaml graphviz black isort

# Export default configuration template
python Django_scaffolder.py --export-default-config

# Run with specific apps
python Django_scaffolder.py --app myapp1 --app myapp2

# Run with custom configuration and post-processing
python Django_scaffolder.py --config scaffolder_config.yaml --post-process
```

## Zero-Touch Generation for Complex Domains

The scaffolder is designed to handle complex domains with minimal configuration:

1. **Automatic relationship detection**: The system inspects your models and identifies relationships
2. **Intelligent serializer generation**: Creates appropriate serializers based on relationship types
3. **Permission handling**: Automatically detects ownership fields and applies proper permissions
4. **Customized views**: Generates views with appropriate filtering and search capabilities
5. **Admin integration**: Creates admin interfaces with sensible defaults
6. **Complete test skeletons**: Generates pytest test fixtures for your API endpoints

## Configuration

The scaffolder's behavior can be customized through a YAML configuration file:

```yaml
# Example configuration
api_base: "api/v1"
features:
  swagger: true
  graph: true
  parallel: true
```

See `scaffolder_config.yaml` for a complete example with all available options.

### Configuration Merging Behavior

When merging your custom configuration with defaults:

- Dictionary values are deeply merged
- List values are **replaced**, not merged
- Scalar values are replaced

For example, if you want to add a new field type to the search list, you need to include all the default types as well:

```yaml
field_types:
  search:
    - "CharField"
    - "TextField" 
    - "EmailField"
    - "SlugField"
    - "UUIDField"  # <- Your additional field type
```

## Template Customization

You can customize the generated code by:

1. **Modifying templates**: Edit the Jinja templates in `scaffolder_templates/`
2. **Creating a configuration file**: Override default behavior with a YAML config file
3. **Post-processing**: Apply formatting and linting after generation

Templates are created the first time you run the scaffolder and can be updated with `--update-templates`.

## Command-Line Options

```
--app label            One or more app labels; defaults to all project apps
--depth N              Nested serializer depth (default 2)
--swagger              Write docs/openapi.yaml (needs PyYAML)
--graph                Write docs/<app>_model_graph.svg (needs graphviz)
--dry-run              Show diffs only, write nothing
--force                Overwrite without timestamp backup
--skip-validation      Skip django check + makemigrations --check
--settings mod         Django settings module (default config.settings)
--update-templates     Force update template files
--clean-backups        Remove old backup files
--config path          Path to configuration file (YAML)
--post-process         Run post-processing (formatting)
--export-default-config Export default configuration template
```

## Generated Files

For each app, the scaffolder generates:

- `serializers.py`: Model serializers with nested relationships
- `views.py`: ViewSets with filtering, search, and permission handling
- `urls.py`: Routing configuration
- `admin.py`: Admin interface with sensible defaults
- `permissions.py`: Custom permission classes (if needed)
- `tests.py`: API test skeletons with safeguarded fixtures

Plus documentation:
- `<app>_frontend_bible.md`: App-specific API documentation
- `master_frontend_bible.md`: Combined documentation linking to all app docs
- `openapi.yaml`: OpenAPI specification (if --swagger)
- `<app>_model_graph.svg`: Visual model diagrams (if --graph)

## Parallel Processing

The scaffolder supports parallel processing of multiple apps for faster generation. When parallel processing is enabled:

- Each app is processed in a separate thread
- File operations are thread-safe with unique backup filenames
- Documentation is generated per-app to avoid race conditions
- A master documentation file links all app-specific docs

To enable parallel processing, set `parallel: true` in your config file or use the default configuration.

## Test Generation

Test files include safeguarded fixtures that handle environments where the fixtures may already be defined:

- API client fixture for making requests
- Authenticated user fixture for testing protected endpoints
- Automatic fallbacks if fixtures are already defined

A `conftest.py` template is also available for project-wide fixture definitions.

## Best Practices

1. **Start with a dry run**: Use `--dry-run` to preview changes
2. **Create a configuration file**: Set up a `scaffolder_config.yaml` for your project
3. **Export the default config**: Use `--export-default-config` to create a reference template
4. **Customize templates**: Adjust templates to match your project's coding style
5. **Enable post-processing**: Use `--post-process` to ensure code quality
6. **Run regularly**: Re-run the scaffolder when your models change

## Extending the Scaffolder

The scaffolder is designed to be extended through:

1. **Custom templates**: Add or modify Jinja templates
2. **Config file overrides**: Customize behavior through configuration
3. **Post-processors**: Add custom code formatters and validators

For advanced customization, you can modify the scaffolder code itself.

## License

MIT License 