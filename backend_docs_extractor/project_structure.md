backend_docs_extractor/
├── config.py # Configuration options
├── main.py # Main orchestration script
├── extractors/
│ ├── **init**.py # Package initialization
│ ├── model_extractor.py # Django model analysis
│ ├── api_analyzer.py # API endpoint extraction
│ ├── serializer_inspector.py # Serializer analysis
│ ├── authentication_analyzer.py # Auth requirement extraction
│ └── runtime_tester.py # Live API testing
├── generators/
│ ├── **init**.py # Package initialization
│ ├── markdown_generator.py # Markdown documentation
│ ├── html_generator.py # HTML documentation
│ ├── typescript_generator.py # TypeScript interface generation
│ └── react_hooks_generator.py # React hook examples
└── utils/
├── **init**.py # Package initialization
├── django_setup.py # Django environment setup
└── logger.py # Logging configuration
