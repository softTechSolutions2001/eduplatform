#!/usr/bin/env python3
"""
Frontend-Backend Analysis Tool

This script analyzes a React/Vite frontend codebase to extract information relevant 
to a Django/PostgreSQL backend. It generates a comprehensive report detailing:
1. Backend Data Requirements - Models, APIs, fields, relationships
2. Continuity Analysis - Compatibility issues, naming inconsistencies
3. Data Flow - How components, API calls, and models connect
4. Code Quality - Patterns and anti-patterns
5. Framework Suggestions - Ideal architecture for backend 

Usage: python frontend_backend_analyzer.py --frontend-dir <frontend_directory> --output <report_file.md>
       python frontend_backend_analyzer.py --frontend-dir <frontend_directory> --backend-dir <backend_directory> --output <report_file.md>
"""

import os
import re
import json
import argparse
import glob
import logging
import time
import hashlib
import multiprocessing
import concurrent.futures
from pathlib import Path
from collections import defaultdict, Counter
import ast
from typing import Dict, List, Set, Tuple, Any, Optional, Union, DefaultDict
import markdown
import networkx as nx
from dataclasses import dataclass, field, asdict
import html
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---- Better pluralization handling ----
def singular_form(word: str) -> str:
    """Convert a word from plural to singular form using common English rules"""
    if not word:
        return word
    
    # Common irregular plurals
    irregular_plurals = {
        'men': 'man',
        'women': 'woman',
        'children': 'child',
        'people': 'person',
        'mice': 'mouse',
        'geese': 'goose',
        'feet': 'foot',
        'teeth': 'tooth',
        'criteria': 'criterion',
        'phenomena': 'phenomenon',
        'statuses': 'status',  # Fix 'statu' issue
    }
    
    if word.lower() in irregular_plurals:
        return irregular_plurals[word.lower()]
    
    # Common endings
    if word.endswith('ies'):
        return word[:-3] + 'y'
    elif word.endswith('es') and word.endswith(('ches', 'shes', 'sses', 'xes')):
        return word[:-2]
    elif word.endswith('ves'):
        return word[:-3] + 'f'
    elif word.endswith('i'):
        return word[:-1] + 'us'
    elif word.endswith('a'):
        return word[:-1] + 'um'
    elif word.endswith('s') and not word.endswith(('ss', 'us', 'is')):
        return word[:-1]
    
    # Default case - return as is
    return word

# ---- Constants ----

REACT_HOOKS = [
    'useState', 'useEffect', 'useContext', 'useReducer',
    'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
    'useLayoutEffect', 'useDebugValue', 'useSyncExternalStore', 
    'useTransition', 'useDeferredValue', 'useId',
]

EXCLUDED_DIRS = ['node_modules', 'dist', 'build', '.git', '__pycache__', 'venv', '.venv']
TEST_FILE_PATTERNS = ['.test.', '.spec.', 'test_', 'tests/']

# ---- Data Classes for storing extracted information ----

@dataclass
class APIEndpoint:
    """Represents an API endpoint found in frontend code"""
    url: str
    method: str = "GET"
    file_locations: List[str] = field(default_factory=list)
    params: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    response_fields: Set[str] = field(default_factory=set)
    components: List[str] = field(default_factory=list)
    auth_required: bool = False  # New: Detect if endpoint requires auth
    resource_type: str = ""      # New: Resource category inferred from URL
    
    def __hash__(self):
        return hash(f"{self.method}:{self.url}")
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        result = asdict(self)
        # Convert sets to lists for JSON serialization
        result['response_fields'] = list(self.response_fields)
        result['params'] = {k: list(v) for k, v in self.params.items()}
        return result

@dataclass
class RelationshipInfo:
    """Represents a relationship between models"""
    related_model: str
    relation_type: str  # "one_to_many", "many_to_one", "many_to_many", "one_to_one", "extends"
    field_name: str = ""
    nullable: bool = True
    
    def __hash__(self):
        return hash(f"{self.related_model}:{self.relation_type}:{self.field_name}")

@dataclass
class DataModel:
    """Represents an inferred data model from frontend usage"""
    name: str
    fields: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    relationships: Dict[str, RelationshipInfo] = field(default_factory=dict)
    file_locations: List[str] = field(default_factory=list)
    api_endpoints: Set[str] = field(default_factory=set)
    required_fields: Set[str] = field(default_factory=set)  # New: Track fields that appear required
    model_description: str = ""  # New: Auto-generated description
    
    def __hash__(self):
        return hash(self.name)
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        result = asdict(self)
        # Convert sets to lists for JSON serialization
        result['api_endpoints'] = list(self.api_endpoints)
        result['required_fields'] = list(self.required_fields)
        result['fields'] = {k: list(v) for k, v in self.fields.items()}
        return result

@dataclass
class Component:
    """Represents a React component"""
    name: str
    file_path: str
    props: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    state_vars: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    api_calls: Set[str] = field(default_factory=set)
    imports: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)  # New: Track hook usage
    complexity: int = 0  # New: Estimate of component complexity
    libraries: Set[str] = field(default_factory=set)  # New: Third-party libraries used
    
    def __hash__(self):
        return hash(f"{self.name}:{self.file_path}")
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        result = asdict(self)
        # Convert sets to lists for JSON serialization
        result['api_calls'] = list(self.api_calls)
        result['libraries'] = list(self.libraries)
        result['props'] = {k: list(v) for k, v in self.props.items()}
        result['state_vars'] = {k: list(v) for k, v in self.state_vars.items()}
        return result

@dataclass
class NamingIssue:
    """Represents a naming inconsistency or issue"""
    type: str
    description: str
    location: str
    severity: str = "medium"  # low, medium, high
    suggestion: str = ""
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return asdict(self)

@dataclass
class CodePattern:
    """Represents a code pattern or anti-pattern found in the analysis"""
    name: str
    type: str  # "best_practice", "anti_pattern", "security", "performance"
    description: str
    occurrences: int = 0
    locations: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return asdict(self)

@dataclass
class BackendComparison:
    """Stores compatibility information between frontend and backend"""
    model_matches: Dict[str, Dict] = field(default_factory=dict)
    endpoint_matches: Dict[str, Dict] = field(default_factory=dict)
    field_mismatches: List[Dict] = field(default_factory=list)
    missing_endpoints: List[str] = field(default_factory=list)
    unexpected_endpoints: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return asdict(self)

# ---- Main Analyzer Class ----

class FrontendBackendAnalyzer:
    """Main analyzer class that processes frontend files and generates a report"""
    
    def __init__(self, frontend_dir: str, backend_dir: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize analyzer with directories and configuration"""
        self.frontend_dir = os.path.abspath(frontend_dir)
        self.backend_dir = os.path.abspath(backend_dir) if backend_dir else None
        
        # Default configuration
        self.config = {
            'parallel_processing': True,
            'max_workers': multiprocessing.cpu_count(),
            'excluded_dirs': EXCLUDED_DIRS,
            'excluded_files': TEST_FILE_PATTERNS,
            'include_tests': False,
            'cache_results': True,
            'cache_dir': '.analyzer_cache',
            'verbose': False,
            'use_ast': True,  # Enable AST-based parsing
            'ast_timeout': 5,  # Timeout for AST parsing in seconds
        }
        
        # Override with provided config
        if config:
            self.config.update(config)
            
        # Initialize data stores
        self.api_endpoints = set()
        self.data_models = {}
        self.components = {}
        self.naming_issues = []
        self.code_patterns = []
        self.graph = nx.DiGraph()
        self.backend_comparison = BackendComparison() if self.backend_dir else None
        
        # Analysis statistics
        self.stats = {
            'start_time': 0,
            'end_time': 0,
            'file_count': 0,
            'error_count': 0,
            'processed_files': [],
            'error_files': [],
            'ast_parse_errors': 0,
            'ast_parse_timeouts': 0,
        }
        
        # Setup caching
        if self.config['cache_results']:
            os.makedirs(self.config['cache_dir'], exist_ok=True)
            
        # Initialize AST parser
        if self.config['use_ast']:
            try:
                import esprima
                self.ast_parser = esprima
            except ImportError:
                logger.warning("esprima not found, falling back to regex-based parsing")
                self.config['use_ast'] = False

    def _parse_with_ast(self, content: str) -> Optional[Dict]:
        """Parse JavaScript/TypeScript content using AST"""
        if not self.config['use_ast']:
            return None
            
        try:
            # Set timeout for AST parsing
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("AST parsing timed out")
                
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config['ast_timeout'])
            
            try:
                ast = self.ast_parser.parseScript(content, {'loc': True, 'range': True})
                signal.alarm(0)  # Disable alarm
                return ast
            except TimeoutError:
                self.stats['ast_parse_timeouts'] += 1
                logger.warning("AST parsing timed out, falling back to regex")
                return None
            except Exception as e:
                self.stats['ast_parse_errors'] += 1
                logger.warning(f"AST parsing failed: {str(e)}, falling back to regex")
                return None
                
        except Exception as e:
            logger.error(f"Error setting up AST parsing: {str(e)}")
            return None

    def extract_api_endpoints(self, content: str, file_path: str, component_name: Optional[str] = None):
        """Extract API endpoints from content using AST or regex"""
        if self.config['use_ast']:
            ast = self._parse_with_ast(content)
            if ast:
                # Extract endpoints using AST traversal
                for node in ast.body:
                    if node.type == 'CallExpression':
                        if (hasattr(node.callee, 'property') and 
                            node.callee.property.name in ('get', 'post', 'put', 'delete', 'patch')):
                            if len(node.arguments) > 0:
                                url = node.arguments[0].value
                                method = node.callee.property.name.upper()
                                self._add_endpoint(url, method, file_path, component_name)
                        elif (hasattr(node.callee, 'name') and 
                              node.callee.name in ('useSWR', 'useQuery')):
                            if len(node.arguments) > 0:
                                url = node.arguments[0].value
                                self._add_endpoint(url, 'GET', file_path, component_name)
                return
                
        # Fallback to regex-based extraction
        for regex in API_REGEXES:
            for match in regex.finditer(content):
                url = match.group(1)
                method = 'GET'  # Default to GET
                if 'post' in match.group(0).lower():
                    method = 'POST'
                elif 'put' in match.group(0).lower():
                    method = 'PUT'
                elif 'delete' in match.group(0).lower():
                    method = 'DELETE'
                elif 'patch' in match.group(0).lower():
                    method = 'PATCH'
                self._add_endpoint(url, method, file_path, component_name)

    def _add_endpoint(self, url: str, method: str, file_path: str, component_name: Optional[str] = None):
        """Add an API endpoint to the collection"""
        endpoint = APIEndpoint(
            url=url,
            method=method,
            file_locations=[file_path]
        )
        
        if component_name:
            endpoint.components.append(component_name)
            
        # Check for auth requirements
        if any(pattern in url.lower() for pattern in ['auth', 'login', 'logout', 'token']):
            endpoint.auth_required = True
            
        # Infer resource type from URL
        parts = url.strip('/').split('/')
        if parts:
            endpoint.resource_type = parts[-1]
            
        self.api_endpoints.add(endpoint)

    def extract_component_name(self, file_path: str) -> str:
        """Extract React component name from file path or content using AST or regex"""
        # First try from filename (common convention)
        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        
        # Guard against empty names
        if not name:
            return ""
            
        # PascalCase convention for components
        if name[0].isupper():
            return name
            
        # Try to read file to find component name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if self.config['use_ast']:
                ast = self._parse_with_ast(content)
                if ast:
                    # Look for component definitions in AST
                    for node in ast.body:
                        if (node.type == 'FunctionDeclaration' and 
                            node.id and node.id.name[0].isupper()):
                            return node.id.name
                        elif (node.type == 'VariableDeclaration' and 
                              node.declarations and 
                              node.declarations[0].id.name[0].isupper()):
                            return node.declarations[0].id.name
                        elif (node.type == 'ClassDeclaration' and 
                              node.id and node.id.name[0].isupper()):
                            return node.id.name
            else:
                # Fallback to regex-based extraction
                for regex in COMPONENT_REGEXES:
                    match = regex.search(content)
                    if match and match.group(1)[0].isupper():
                        return match.group(1)
        except:
            pass
            
        # Fallback: use filename with first letter capitalized
        return name[0].upper() + name[1:] if name else ""

    def extract_hooks(self, content: str) -> List[str]:
        """Extract React hooks used in the component using AST or regex"""
        hooks_used = []
        
        if self.config['use_ast']:
            ast = self._parse_with_ast(content)
            if ast:
                # Extract hooks using AST traversal
                for node in ast.body:
                    if (node.type == 'CallExpression' and 
                        hasattr(node.callee, 'name') and 
                        node.callee.name.startswith('use')):
                        hooks_used.append(node.callee.name)
                return hooks_used
                
        # Fallback to regex-based extraction
        # Check standard React hooks
        for hook in REACT_HOOKS:
            if re.search(r'\b' + hook + r'\s*\(', content):
                hooks_used.append(hook)
                
        # Look for custom hooks
        for match in HOOK_REGEX.finditer(content):
            hook_name = match.group(0).split('(')[0].strip()
            if hook_name not in REACT_HOOKS and hook_name not in hooks_used:
                hooks_used.append(hook_name)
                
        return hooks_used

    def analyze(self):
        """Main analysis entry point"""
        self.stats['start_time'] = time.time()
        logger.info(f"Analyzing frontend code in: {self.frontend_dir}")
        
        # Find all JS/JSX/TS/TSX files
        js_files = self.find_js_files()
        self.stats['file_count'] = len(js_files)
        logger.info(f"Found {len(js_files)} JavaScript/TypeScript files to analyze")
        
        # Process files (with parallel processing if enabled)
        if self.config['parallel_processing'] and len(js_files) > 5:
            self._parallel_process_files(js_files)
        else:
            self._sequential_process_files(js_files)
        
        # Build relationships between components and models
        self.build_relationships()
        
        # Detect code patterns
        self.detect_code_patterns()
        
        # Find naming inconsistencies and other issues
        self.check_naming_consistency()
        
        # Compare with backend if provided
        if self.backend_dir:
            self.compare_with_backend()
        
        self.stats['end_time'] = time.time()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info(f"Analysis complete in {duration:.2f} seconds:")
        logger.info(f"- {len(self.api_endpoints)} API endpoints identified")
        logger.info(f"- {len(self.data_models)} data models inferred")
        logger.info(f"- {len(self.components)} React components analyzed")
        logger.info(f"- {len(self.naming_issues)} naming/consistency issues found")
        logger.info(f"- {len(self.code_patterns)} code patterns detected")
        
        # Cache results
        if self.config['cache_results']:
            self._save_analysis_results()
    
    def _save_analysis_results(self):
        """Save analysis results to cache"""
        # Convert complex objects to serializable format
        api_endpoints = [endpoint.to_dict() for endpoint in self.api_endpoints]
        data_models = {name: model.to_dict() for name, model in self.data_models.items()}
        components = {name: comp.to_dict() for name, comp in self.components.items()}
        naming_issues = [issue.to_dict() for issue in self.naming_issues]
        code_patterns = [pattern.to_dict() for pattern in self.code_patterns]
        
        # Save each type of data
        self._save_to_cache(api_endpoints, "api_endpoints")
        self._save_to_cache(data_models, "data_models")
        self._save_to_cache(components, "components")
        self._save_to_cache(naming_issues, "naming_issues")
        self._save_to_cache(code_patterns, "code_patterns")
        self._save_to_cache(self.stats, "stats")
    
    def _parallel_process_files(self, files: List[str]):
        """Process files in parallel using a process pool"""
        # Use ProcessPoolExecutor for CPU-bound operations to bypass GIL
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Create serializable data for multiprocessing
            file_configs = [
                {
                    'file_path': file_path,
                    'frontend_dir': self.frontend_dir,
                }
                for file_path in files
            ]
            
            # Map to a static method that can be pickled
            future_to_file = {
                executor.submit(self._process_file_static, file_config): 
                file_config['file_path'] for file_config in file_configs
            }
            
            completed = 0
            total = len(files)
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        # Integrate results from worker process
                        self._integrate_worker_results(result, file_path)
                    self.stats['processed_files'].append(file_path)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    self.stats['error_files'].append(file_path)
                    self.stats['error_count'] += 1
                
                completed += 1
                if completed % 20 == 0 or completed == total:
                    logger.info(f"Progress: {completed}/{total} files ({completed/total*100:.1f}%)")
    
    @staticmethod
    def _process_file_static(file_config):
        """Static method for processing a file in a separate process"""
        file_path = file_config['file_path']
        frontend_dir = file_config['frontend_dir']
        
        try:
            rel_path = os.path.relpath(file_path, frontend_dir)
            
            # Basic component name extraction from filename
            base_name = os.path.basename(file_path)
            name, _ = os.path.splitext(base_name)
            component_name = name[0].upper() + name[1:] if name else ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Return extracted data in a serializable format
            return {
                'file_path': file_path,
                'rel_path': rel_path,
                'component_name': component_name,
                'content': content,
            }
        except Exception as e:
            # Return the error to be handled in the main process
            return {
                'file_path': file_path,
                'error': str(e)
            }
    
    def _integrate_worker_results(self, result, file_path):
        """Integrate results from worker processes"""
        if 'error' in result:
            # Error was already logged in _parallel_process_files
            return
            
        # Extract file info
        rel_path = result['rel_path']
        component_name = result['component_name']
        content = result['content']
        
        # Now process the file content in the main process
        if component_name:
            component = Component(
                name=component_name,
                file_path=rel_path
            )
            
            # Extract imports and libraries
            imports = self.extract_imports(content)
            component.imports = imports
            component.libraries = self.extract_libraries(imports)
            
            # Extract props and state
            component.props = self.extract_props(content)
            component.state_vars = self.extract_state(content)
            
            # Extract hooks
            component.hooks = self.extract_hooks(content)
            
            # Estimate complexity
            component.complexity = self.estimate_complexity(content)
            
            self.components[component_name] = component
            
        # Extract API endpoints
        self.extract_api_endpoints(content, rel_path, component_name)
        
        # Extract data models/structures
        self.extract_data_models(content, rel_path, component_name)
    
    def _sequential_process_files(self, files: List[str]):
        """Process files sequentially"""
        for i, file_path in enumerate(files):
            try:
                self.process_file(file_path)
                self.stats['processed_files'].append(file_path)
                
                # Log progress every 10 files
                if (i+1) % 10 == 0 or i+1 == len(files):
                    logger.info(f"Progress: {i+1}/{len(files)} files ({(i+1)/len(files)*100:.1f}%)")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                self.stats['error_files'].append(file_path)
                self.stats['error_count'] += 1
    
    def find_js_files(self) -> List[str]:
        """Find all JavaScript and TypeScript files in the frontend directory"""
        js_files = []
        
        # Use pathlib for more robust directory traversal
        frontend_path = Path(self.frontend_dir)
        
        # Extensions to include
        extensions = ['.js', '.jsx', '.ts', '.tsx']
        
        # Walk directory recursively
        for file_path in frontend_path.rglob('*.*'):
            # Check if it's a file with a relevant extension
            if (file_path.is_file() and 
                file_path.suffix.lower() in extensions and
                not self._should_exclude_file(str(file_path))):
                js_files.append(str(file_path))
        
        return js_files
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from analysis"""
        # Skip excluded directories
        for excluded_dir in self.config['excluded_dirs']:
            if f"/{excluded_dir}/" in file_path.replace("\\", "/"):
                return True
                
        # Skip test files unless explicitly included
        if not self.config['include_tests']:
            for test_pattern in self.config['excluded_files']:
                if test_pattern in file_path:
                    return True
        
        return False
    
    def process_file(self, file_path: str):
        """Process a single JavaScript/JSX/TS/TSX file"""
        rel_path = os.path.relpath(file_path, self.frontend_dir)
        component_name = self.extract_component_name(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component information
            if component_name:
                component = Component(
                    name=component_name,
                    file_path=rel_path
                )
                
                # Extract imports and libraries
                imports = self.extract_imports(content)
                component.imports = imports
                component.libraries = self.extract_libraries(imports)
                
                # Extract props and state
                component.props = self.extract_props(content)
                component.state_vars = self.extract_state(content)
                
                # Extract hooks
                component.hooks = self.extract_hooks(content)
                
                # Estimate complexity
                component.complexity = self.estimate_complexity(content)
                
                self.components[component_name] = component
                
            # Extract API endpoints
            self.extract_api_endpoints(content, rel_path, component_name)
            
            # Extract data models/structures
            self.extract_data_models(content, rel_path, component_name)
            
        except Exception as e:
            logger.error(f"Error processing file {rel_path}: {str(e)}")
            raise
    
    def extract_libraries(self, imports: List[str]) -> Set[str]:
        """Extract third-party libraries from import paths"""
        libraries = set()
        
        for import_path in imports:
            # Check if it's a library (doesn't start with . or /)
            if not import_path.startswith('.') and not import_path.startswith('/'):
                # Extract library name (before any / character)
                lib_name = import_path.split('/')[0]
                libraries.add(lib_name)
                
        return libraries
    
    def estimate_complexity(self, content: str) -> int:
        """Estimate the complexity of a component based on various factors"""
        complexity = 0
        
        # Count hooks
        hook_count = sum(1 for hook in REACT_HOOKS if re.search(r'\b' + hook + r'\s*\(', content))
        complexity += hook_count * 2
        
        # Count conditionals and loops (more specific matching)
        conditional_patterns = [
            r'\bif\s*\(',  # if statements
            r'\bswitch\s*\(',  # switch statements
            r'\bwhile\s*\(',  # while loops
            r'\bfor\s*\(',  # for loops
            r'\.map\s*\(',  # array.map
            r'\.filter\s*\(',  # array.filter
            r'\.reduce\s*\(',  # array.reduce
            r'\?',  # ternary operator
        ]
        
        conditionals = sum(len(re.findall(pattern, content)) for pattern in conditional_patterns)
        complexity += conditionals * 2
        
        # Count JSX elements (more specific matching to avoid counting import statements)
        jsx_patterns = [
            r'<[A-Z][a-zA-Z0-9]*\s*[^>]*>',  # Opening tags with attributes
            r'<[A-Z][a-zA-Z0-9]*\s*>',  # Simple opening tags
            r'<[A-Z][a-zA-Z0-9]*\s*/>'  # Self-closing tags
        ]
        
        # Exclude patterns from imports
        import_jsx = len(re.findall(r'import\s+[^;]*<[A-Z][^>]*>', content))
        
        jsx_elements = sum(len(re.findall(pattern, content)) for pattern in jsx_patterns) - import_jsx
        complexity += jsx_elements
        
        # Count event handlers
        event_handlers = len(re.findall(r'on[A-Z][a-zA-Z]*\s*=', content))
        complexity += event_handlers
        
        # Count state updates
        state_updates = len(re.findall(r'set[A-Z][a-zA-Z]*\s*\(', content))
        complexity += state_updates * 2
        
        # Count useEffect dependencies
        effect_deps_pattern = r'useEffect\s*\(\s*(?:\(\)\s*=>\s*)?{[^}]*}\s*,\s*\[(.*?)\]'
        effect_matches = re.findall(effect_deps_pattern, content)
        
        for deps in effect_matches:
            if deps.strip():  # Non-empty dependency array
                dep_count = len(re.split(r',\s*', deps))
                complexity += dep_count
        
        # Count nesting level
        nesting_level = 0
        max_nesting = 0
        for line in content.split('\n'):
            opened = line.count('{') - line.count('}')
            nesting_level += opened
            max_nesting = max(max_nesting, nesting_level)
        
        complexity += max_nesting * 3
        
        return complexity
    
    def detect_code_patterns(self):
        """Detect patterns and anti-patterns in the code"""
        logger.info("Detecting code patterns...")
        
        # 1. Check for components with too many props
        for name, component in self.components.items():
            if len(component.props) > 10:
                self.code_patterns.append(CodePattern(
                    name="Too Many Props",
                    type="anti_pattern",
                    description=f"Component {name} has {len(component.props)} props which may indicate it's doing too much",
                    occurrences=1,
                    locations=[component.file_path],
                    severity="medium"
                ))
        
        # 2. Check for components with high complexity
        for name, component in self.components.items():
            if component.complexity > 30:
                self.code_patterns.append(CodePattern(
                    name="High Complexity Component",
                    type="anti_pattern",
                    description=f"Component {name} has high complexity score ({component.complexity})",
                    occurrences=1,
                    locations=[component.file_path],
                    severity="high"
                ))
        
        # 3. Check for inconsistent API call patterns
        api_patterns = defaultdict(list)
        for endpoint in self.api_endpoints:
            parts = endpoint.url.strip('/').split('/')
            if parts:
                pattern = '/'.join([p if not (p.startswith(':') or (p.startswith('{') and p.endswith('}'))) else '*' for p in parts])
                api_patterns[pattern].append(endpoint.url)
        
        # Look for inconsistent patterns
        for pattern, urls in api_patterns.items():
            if len(urls) > 3:  # Only check patterns with multiple instances
                rest_count = sum(1 for url in urls if self._is_restful(url))
                non_rest_count = len(urls) - rest_count
                
                if rest_count > 0 and non_rest_count > 0:
                    self.code_patterns.append(CodePattern(
                        name="Inconsistent API Design",
                        type="anti_pattern",
                        description=f"Mix of RESTful and non-RESTful endpoints for pattern {pattern}",
                        occurrences=len(urls),
                        locations=urls,
                        severity="medium"
                    ))
        
        # 4. Check for duplicate data models
        model_fields = defaultdict(list)
        for name, model in self.data_models.items():
            # Create a signature of field names
            field_sig = tuple(sorted(model.fields.keys()))
            if field_sig:  # Only check non-empty models
                model_fields[field_sig].append(name)
        
        # Find potential duplicates
        for field_sig, names in model_fields.items():
            if len(names) > 1 and len(field_sig) > 3:  # Only report if significant overlap
                self.code_patterns.append(CodePattern(
                    name="Duplicate Data Models",
                    type="anti_pattern",
                    description=f"Models {', '.join(names)} have identical fields and may be duplicates",
                    occurrences=len(names),
                    locations=[model.file_locations[0] for name, model in self.data_models.items() if name in names],
                    severity="medium"
                ))
        
        logger.info(f"Detected {len(self.code_patterns)} code patterns")
    
    def _is_restful(self, url: str) -> bool:
        """Check if a URL follows RESTful conventions"""
        parts = url.strip('/').split('/')
        
        # Check for ID pattern at the end (/:id, /{id})
        if len(parts) >= 2:
            last_part = parts[-1]
            if last_part.startswith(':') or (last_part.startswith('{') and last_part.endswith('}')):
                return True
                
        # Check for standard REST operations
        rest_operations = ['create', 'read', 'update', 'delete', 'list']
        for part in parts:
            if part in rest_operations:
                return True
                
        return False
    
    def compare_with_backend(self):
        """Compare frontend models and endpoints with backend implementation"""
        if not self.backend_dir:
            logger.warning("No backend directory provided for comparison")
            return
            
        logger.info(f"Comparing with backend implementation in {self.backend_dir}")
        
        # Extract backend models and endpoints from Django files
        backend_models = self._extract_backend_models()
        backend_endpoints = self._extract_backend_endpoints()
        
        # Compare models
        for model_name, model in self.data_models.items():
            # Try different naming conventions
            model_variants = [
                model_name,
                self._to_snake_case(model_name),
                self._to_camel_case(model_name),
                f"{self._to_snake_case(model_name)}s",  # Plural
            ]
            
            found = False
            for variant in model_variants:
                if variant in backend_models:
                    # Record match
                    self.backend_comparison.model_matches[model_name] = {
                        'backend_name': variant,
                        'match_quality': self._calculate_model_match_quality(model, backend_models[variant])
                    }
                    found = True
                    break
                    
            if not found:
                logger.warning(f"Frontend model {model_name} has no corresponding backend model")
                
        # Compare endpoints
        for endpoint in self.api_endpoints:
            normalized_url = self._normalize_endpoint_url(endpoint.url)
            found = False
            
            for backend_url in backend_endpoints:
                if self._endpoints_match(normalized_url, backend_url):
                    # Record match
                    key = f"{endpoint.method} {endpoint.url}"
                    self.backend_comparison.endpoint_matches[key] = {
                        'backend_url': backend_url,
                        'match_quality': self._calculate_endpoint_match_quality(endpoint, backend_url, backend_endpoints[backend_url])
                    }
                    found = True
                    break
                    
            if not found:
                self.backend_comparison.missing_endpoints.append(f"{endpoint.method} {endpoint.url}")
                
        # Check for unexpected backend endpoints
        for backend_url in backend_endpoints:
            found = False
            for endpoint in self.api_endpoints:
                normalized_url = self._normalize_endpoint_url(endpoint.url)
                if self._endpoints_match(normalized_url, backend_url):
                    found = True
                    break
                    
            if not found:
                self.backend_comparison.unexpected_endpoints.append(backend_url)
                
        logger.info(f"Comparison complete: {len(self.backend_comparison.model_matches)} model matches, " + 
                   f"{len(self.backend_comparison.endpoint_matches)} endpoint matches, " +
                   f"{len(self.backend_comparison.missing_endpoints)} missing endpoints, " +
                   f"{len(self.backend_comparison.unexpected_endpoints)} unexpected endpoints")
    
    def _extract_backend_models(self) -> Dict[str, Dict]:
        """Extract model definitions from Django backend"""
        models = {}
        models_file_pattern = os.path.join(self.backend_dir, "**", "models.py")
        
        for file_path in glob.glob(models_file_pattern, recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse Python AST to extract model classes
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Check if it's a Django model (inherits from models.Model)
                            is_django_model = False
                            for base in node.bases:
                                # Check for direct inheritance: Model
                                if isinstance(base, ast.Name) and base.id == 'Model':
                                    is_django_model = True
                                    break
                                # Check for attribute inheritance: models.Model
                                elif (isinstance(base, ast.Attribute) and 
                                      isinstance(base.value, ast.Name) and
                                      base.value.id == 'models' and 
                                      base.attr == 'Model'):
                                    is_django_model = True
                                    break
                                # Check for imported base: from .models import ModelBase
                                elif isinstance(base, ast.Name) and base.id.endswith(('Model', 'ModelBase')):
                                    is_django_model = True
                                    break
                            
                            if is_django_model:
                                model_name = node.name
                                fields = {}
                                
                                for child in node.body:
                                    if isinstance(child, ast.Assign):
                                        for target in child.targets:
                                            if isinstance(target, ast.Name):
                                                field_name = target.id
                                                # Skip Django Meta and other magic attrs
                                                if not field_name.startswith('_'):
                                                    fields[field_name] = self._extract_field_type(child.value)
                                                    
                                models[model_name] = {
                                    'fields': fields,
                                    'file_path': file_path
                                }
                except SyntaxError:
                    logger.warning(f"Syntax error parsing {file_path}, skipping")
                    
            except Exception as e:
                logger.error(f"Error processing backend model file {file_path}: {str(e)}")
                
        return models
    
    def _extract_field_type(self, value_node) -> str:
        """Extract field type from AST node"""
        if isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Attribute):
                if isinstance(value_node.func.value, ast.Name) and value_node.func.value.id == 'models':
                    return value_node.func.attr
        return "unknown"
    
    def _extract_backend_endpoints(self) -> Dict[str, Dict]:
        """Extract API endpoints from Django backend"""
        endpoints = {}
        
        # Check for urls.py files
        urls_file_pattern = os.path.join(self.backend_dir, "**", "urls.py")
        
        for file_path in glob.glob(urls_file_pattern, recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract URL patterns using regex for common Django patterns
                # path('api/users/', views.UserListView.as_view(), name='user-list'),
                url_pattern = r"(?:path|url|re_path)\s*\(\s*['\"]([^'\"]*)['\"]"
                for match in re.finditer(url_pattern, content):
                    url = match.group(1)
                    # Add to results
                    endpoints[url] = {
                        'file_path': file_path,
                        'methods': self._extract_view_methods(content, url)
                    }
                    
            except Exception as e:
                logger.error(f"Error processing backend URL file {file_path}: {str(e)}")
                
        # Check for DRF ViewSets and Routers
        viewsets_pattern = os.path.join(self.backend_dir, "**", "views*.py")
        
        for file_path in glob.glob(viewsets_pattern, recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for ViewSet classes
                viewset_pattern = r"class\s+(\w+)ViewSet\s*\("
                for match in re.finditer(viewset_pattern, content):
                    resource_name = match.group(1).lower()
                    
                    # Add standard REST endpoints
                    endpoints[f"api/{resource_name}/"] = {
                        'file_path': file_path,
                        'methods': ['GET'],
                        'viewset': True
                    }
                    
                    endpoints[f"api/{resource_name}/{{id}}/"] = {
                        'file_path': file_path,
                        'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                        'viewset': True
                    }
                    
            except Exception as e:
                logger.error(f"Error processing backend views file {file_path}: {str(e)}")
                
        return endpoints
    
    def _extract_view_methods(self, content: str, url: str) -> List[str]:
        """Extract HTTP methods supported by a view"""
        methods = []
        
        # Look for view class referenced in URL pattern
        view_pattern = rf"['\"]?{re.escape(url)}['\"]?.*?views\.(\w+)"
        view_match = re.search(view_pattern, content)
        
        if view_match:
            view_name = view_match.group(1)
            
            # Check common HTTP method handlers
            if re.search(rf"def get.*?class {view_name}", content, re.DOTALL):
                methods.append('GET')
            if re.search(rf"def post.*?class {view_name}", content, re.DOTALL):
                methods.append('POST')
            if re.search(rf"def put.*?class {view_name}", content, re.DOTALL):
                methods.append('PUT')
            if re.search(rf"def patch.*?class {view_name}", content, re.DOTALL):
                methods.append('PATCH')
            if re.search(rf"def delete.*?class {view_name}", content, re.DOTALL):
                methods.append('DELETE')
        
        # Default to GET if no methods found
        if not methods:
            methods = ['GET']
            
        return methods
    
    def _normalize_endpoint_url(self, url: str) -> str:
        """Normalize an endpoint URL for comparison"""
        # Strip leading/trailing slashes
        url = url.strip('/')
        
        # Replace parameter placeholders with {param} format
        url = re.sub(r':(\w+)', r'{\1}', url)
        
        # Add api/ prefix if not present
        if not url.startswith('api/') and not url.startswith('v1/') and not url.startswith('v2/'):
            url = 'api/' + url
            
        # Add trailing slash for Django
        url = url + '/'
            
        return url
    
    def _endpoints_match(self, frontend_url: str, backend_url: str) -> bool:
        """Check if frontend and backend endpoints match"""
        # Convert to pattern format (parameters become wildcards)
        frontend_pattern = re.sub(r'{[^}]+}', r'[^/]+', frontend_url)
        frontend_pattern = f"^{frontend_pattern}$"
        
        backend_pattern = re.sub(r'{[^}]+}', r'[^/]+', backend_url)
        backend_pattern = f"^{backend_pattern}$"
        
        # Check if either pattern matches the other URL
        return (re.match(frontend_pattern, backend_url) is not None or
                re.match(backend_pattern, frontend_url) is not None)
    
    def _calculate_model_match_quality(self, frontend_model, backend_model) -> float:
        """Calculate match quality between frontend and backend models"""
        # Count matching fields
        frontend_fields = set(frontend_model.fields.keys())
        backend_fields = set(backend_model['fields'].keys())
        
        # Common fields / union of all fields
        if not frontend_fields or not backend_fields:
            return 0.0
            
        common_fields = frontend_fields.intersection(backend_fields)
        all_fields = frontend_fields.union(backend_fields)
        
        # Calculate match quality (Jaccard similarity)
        return len(common_fields) / len(all_fields)
    
    def _calculate_endpoint_match_quality(self, frontend_endpoint, backend_url, backend_info) -> float:
        """Calculate match quality between frontend and backend endpoints"""
        # Check method match
        method_match = 1.0 if frontend_endpoint.method in backend_info['methods'] else 0.5
        
        # Calculate parameter match
        frontend_params = set(re.findall(r'{([^}]+)}', self._normalize_endpoint_url(frontend_endpoint.url)))
        backend_params = set(re.findall(r'{([^}]+)}', backend_url))
        
        param_match = 1.0
        if frontend_params or backend_params:
            common_params = frontend_params.intersection(backend_params)
            all_params = frontend_params.union(backend_params)
            param_match = len(common_params) / len(all_params)
            
        # Combine scores
        return (method_match * 0.4) + (param_match * 0.6)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase or PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def build_relationships(self):
        """Build relationships between components, models, and API endpoints"""
        # Connect components based on imports
        for component_name, component in self.components.items():
            self.graph.add_node(component_name, type="component")
            
            # Look for imports of other components
            for imp in component.imports:
                # Extract component name from import path
                imported_name = os.path.basename(imp).split('.')[0]
                imported_name = imported_name[0].upper() + imported_name[1:] if imported_name else ""
                
                if imported_name in self.components:
                    self.graph.add_edge(component_name, imported_name, type="imports")
        
        # Connect models to API endpoints
        for endpoint in self.api_endpoints:
            endpoint_key = f"{endpoint.method}:{endpoint.url}"
            self.graph.add_node(endpoint_key, type="endpoint")
            
            # Connect to components that use this endpoint
            for component_name in endpoint.components:
                if component_name in self.components:
                    self.graph.add_edge(component_name, endpoint_key, type="calls")
            
            # Try to infer model from endpoint
            parts = endpoint.url.strip('/').split('/')
            if parts:
                # Try to infer model name (usually last non-parameter part of URL)
                model_candidates = []
                for part in parts:
                    if not part.startswith(':') and not part.startswith('{'):
                        # Convert plural to singular and snake_case to PascalCase
                        singular = singular_form(part)
                        pascal_case = ''.join(w.capitalize() for w in re.split(r'[-_]', singular))
                        model_candidates.append(pascal_case)
                
                # Connect endpoint to potential models
                for model_name in self.data_models:
                    if model_name in model_candidates or any(model_name.lower() in c.lower() for c in model_candidates):
                        self.graph.add_edge(endpoint_key, model_name, type="references")
                        self.data_models[model_name].api_endpoints.add(endpoint.url)

    def check_naming_consistency(self):
        """Find naming inconsistencies and other potential issues"""
        logger.info("Checking naming consistency...")
        
        # Check for snake_case vs camelCase inconsistencies in API endpoints
        url_format_patterns = {
            'snake_case': r'_\w',
            'camelCase': r'[a-z][A-Z]',
            'kebab-case': r'-\w',
        }
        
        url_formats = defaultdict(set)
        for endpoint in self.api_endpoints:
            for format_name, pattern in url_format_patterns.items():
                if re.search(pattern, endpoint.url):
                    url_formats[format_name].add(endpoint.url)
        
        # If multiple formats are used, flag as inconsistency
        if len(url_formats) > 1:
            formats_str = ', '.join(url_formats.keys())
            self.naming_issues.append(NamingIssue(
                type="API URL Format",
                description=f"Inconsistent URL formats used: {formats_str}",
                location="API Endpoints",
                severity="medium",
                suggestion="Standardize on one URL format for all API endpoints"
            ))
            
        # Check for inconsistencies between model names and endpoint URLs
        for model_name, model in self.data_models.items():
            model_snake = self._to_snake_case(model_name)
            model_plural = model_snake + 's'
            
            for endpoint in self.api_endpoints:
                if model_plural in endpoint.url:
                    # Check if fields referenced in API match model fields
                    for param in endpoint.params:
                        if param not in model.fields:
                            self.naming_issues.append(NamingIssue(
                                type="Field Mismatch",
                                description=f"API param '{param}' not found in model '{model_name}'",
                                location=f"Endpoint {endpoint.url}",
                                severity="high",
                                suggestion=f"Add '{param}' field to {model_name} model or update API"
                            ))
        
        # Check for inconsistent field naming patterns within models
        for model_name, model in self.data_models.items():
            camel_case_count = 0
            snake_case_count = 0
            
            for field in model.fields:
                if '_' in field:
                    snake_case_count += 1
                elif field and field[0].islower() and any(c.isupper() for c in field):
                    camel_case_count += 1
            
            if camel_case_count > 0 and snake_case_count > 0:
                self.naming_issues.append(NamingIssue(
                    type="Field Naming",
                    description=f"Mixed camelCase and snake_case fields in model '{model_name}'",
                    location=f"Model {model_name}",
                    severity="medium",
                    suggestion="Standardize on one naming convention for all fields"
                ))
                
        logger.info(f"Found {len(self.naming_issues)} naming consistency issues")

    def generate_report(self, output_file: str = "frontend_backend_report.md"):
        """Generate a markdown report with the analysis results"""
        report = []
        
        # Header
        report.append("# Frontend-Backend Analysis Report")
        report.append(f"\nGenerated from: `{self.frontend_dir}`\n")
        
        # Section 1: Backend Data
        report.append("## 1. Backend Data")
        
        # Data Models
        report.append("\n### 1.1 Data Models")
        if self.data_models:
            for model_name, model in sorted(self.data_models.items()):
                report.append(f"\n#### {model_name}")
                
                # Model fields
                if model.fields:
                    report.append("\n**Fields:**\n")
                    report.append("| Field | Types | Used In |")
                    report.append("|-------|-------|---------|")
                    
                    for field_name, types in sorted(model.fields.items()):
                        types_str = ", ".join(sorted(types))
                        
                        # Find where this field is used
                        used_in = []
                        for endpoint in self.api_endpoints:
                            if field_name in endpoint.params or field_name in endpoint.response_fields:
                                used_in.append(f"`{endpoint.method} {endpoint.url}`")
                        
                        used_str = "<br>".join(used_in) if used_in else "-"
                        report.append(f"| {field_name} | {types_str} | {used_str} |")
                
                # Model relationships
                if model.relationships:
                    report.append("\n**Relationships:**\n")
                    for related_model, rel_info in sorted(model.relationships.items()):
                        report.append(f"- {rel_info.relation_type} `{related_model}`")
                
                # Associated API endpoints
                if model.api_endpoints:
                    report.append("\n**API Endpoints:**\n")
                    for endpoint in sorted(model.api_endpoints):
                        report.append(f"- `{endpoint}`")
                
                # File locations
                if model.file_locations:
                    report.append("\n**Referenced in:**\n")
                    for location in sorted(model.file_locations):
                        report.append(f"- `{location}`")
        else:
            report.append("\nNo data models could be inferred from the frontend code.\n")
        
        # API Endpoints
        report.append("\n### 1.2 API Endpoints")
        if self.api_endpoints:
            endpoints_by_prefix = defaultdict(list)
            
            # Group endpoints by prefix for better organization
            for endpoint in sorted(self.api_endpoints, key=lambda e: e.url):
                parts = endpoint.url.strip('/').split('/')
                prefix = parts[0] if parts else ""
                endpoints_by_prefix[prefix].append(endpoint)
            
            for prefix, endpoints in sorted(endpoints_by_prefix.items()):
                if prefix:
                    report.append(f"\n#### /{prefix}\n")
                else:
                    report.append("\n#### Root Endpoints\n")
                
                for endpoint in endpoints:
                    report.append(f"##### `{endpoint.method} {endpoint.url}`\n")
                    
                    # Request parameters
                    if endpoint.params:
                        report.append("**Request Parameters:**\n")
                        report.append("| Parameter | Types |")
                        report.append("|-----------|-------|")
                        
                        for param, types in sorted(endpoint.params.items()):
                            types_str = ", ".join(sorted(types))
                            report.append(f"| {param} | {types_str} |")
                        
                        report.append("")
                    
                    # Response fields
                    if endpoint.response_fields:
                        report.append("**Response Fields:**\n")
                        report.append("- " + "\n- ".join(sorted(endpoint.response_fields)))
                        report.append("")
                    
                    # Components using this endpoint
                    if endpoint.components:
                        report.append("**Used in Components:**\n")
                        report.append("- " + "\n- ".join(sorted(endpoint.components)))
                        report.append("")
                    
                    # File locations
                    if endpoint.file_locations:
                        report.append("**Referenced in:**\n")
                        report.append("- " + "\n- ".join(sorted(endpoint.file_locations)))
                        report.append("")
        else:
            report.append("\nNo API endpoints were found in the frontend code.\n")
        
        # URL Patterns
        report.append("\n### 1.3 URL Patterns")
        all_urls = [endpoint.url for endpoint in self.api_endpoints]
        if all_urls:
            url_patterns = self.extract_url_patterns(all_urls)
            report.append("\nBased on the API endpoints found, the following Django URL pattern structure is suggested:\n")
            report.append("```python")
            report.append("# urls.py")
            report.append("from django.urls import path, include")
            report.append("\nurlpatterns = [")
            
            for pattern in url_patterns:
                report.append(f"    {pattern}")
                
            report.append("]")
            report.append("```")
        else:
            report.append("\nNo URL patterns could be inferred from the frontend code.\n")

        # Suggested Models
        report.append("\n### 1.4 Suggested Django Models")
        if self.data_models:
            report.append("\nBased on the data structures found in the frontend, here are suggested Django model definitions:\n")
            report.append("```python")
            report.append("# models.py")
            report.append("from django.db import models\n")
            
            # Sort models to put base models first
            sorted_models = []
            model_deps = {model_name: set(model.relationships.keys()) 
                         for model_name, model in self.data_models.items()}
            
            while model_deps:
                # Find models with no dependencies or dependencies already processed
                independent = [m for m, deps in model_deps.items()
                              if not deps or deps.issubset(set(m.name for m in sorted_models))]
                
                if not independent:
                    # Handle circular dependencies
                    independent = [next(iter(model_deps.keys()))]
                    
                for model_name in independent:
                    if model_name in self.data_models:
                        sorted_models.append(self.data_models[model_name])
                    model_deps.pop(model_name, None)
            
            # Generate model code
            for model in sorted_models:
                report.append(f"class {model.name}(models.Model):")
                
                if not model.fields:
                    report.append("    # No fields could be inferred")
                    report.append("    pass\n")
                    continue
                    
                for field_name, types in sorted(model.fields.items()):
                    field_type = next(iter(types)) if types else "unknown"
                    django_field = self.get_django_field_type(field_type, field_name)
                    report.append(f"    {field_name} = {django_field}")
                
                report.append("")
                report.append("    def __str__(self):")
                report.append(f"        return str(self.id)  # Consider using a name field if available")
                report.append("")
            
            report.append("```")
        else:
            report.append("\nNo Django models could be inferred from the frontend code.\n")
        
        # Section 2: Continuity and Connectivity
        report.append("\n## 2. Continuity and Connectivity")
        
        # Naming Issues
        report.append("\n### 2.1 Naming Consistency Issues")
        if self.naming_issues:
            report.append("\n| Type | Description | Location | Severity | Suggestion |")
            report.append("|------|-------------|----------|----------|------------|")
            
            for issue in sorted(self.naming_issues, key=lambda i: i.severity):
                severity_marker = {
                    "high": "🔴",
                    "medium": "🟠",
                    "low": "🟡"
                }.get(issue.severity, "")
                
                report.append(f"| {issue.type} | {issue.description} | {issue.location} | {severity_marker} {issue.severity} | {issue.suggestion} |")
        else:
            report.append("\nNo naming consistency issues were found.\n")
        
        # Component Relationships
        report.append("\n### 2.2 Component Relationships")
        if self.components:
            report.append("\nThe following diagram shows the relationships between components and API endpoints:\n")
            
            report.append("```")
            report.append("Component Hierarchy:")
            
            # Build simplified tree
            top_level = [node for node in self.graph.nodes if self.graph.in_degree(node) == 0 and node in self.components]
            if not top_level and self.components:
                # If no clear top level, just use components with fewest dependencies
                top_level = sorted(self.components.keys(), 
                                  key=lambda n: self.graph.in_degree(n))[:3]
            
            for i, component in enumerate(sorted(top_level)):
                self._print_component_tree(component, "", i == len(top_level) - 1, report, set())
            
            report.append("```")
            
            # API usage statistics
            report.append("\n**API Usage by Component:**\n")
            report.append("| Component | API Endpoints Used |")
            report.append("|-----------|-------------------|")
            
            for component_name, component in sorted(self.components.items()):
                if component.api_calls:
                    api_list = "<br>".join(f"`{api}`" for api in sorted(component.api_calls))
                    report.append(f"| {component_name} | {api_list} |")
        else:
            report.append("\nNo component relationships could be inferred.\n")
        
        # Data Flow Analysis
        report.append("\n### 2.3 Data Flow Analysis")
        if self.api_endpoints and self.data_models:
            report.append("\n**Data Flow Diagram:**\n")
            
            report.append("```")
            report.append("Frontend Components → API Endpoints → Backend Models")
            report.append("")
            
            # Group endpoints by model they likely affect
            model_endpoints = defaultdict(list)
            for endpoint in self.api_endpoints:
                endpoint_key = f"{endpoint.method} {endpoint.url}"
                
                # Try to associate endpoint with models
                assigned = False
                for model_name, model in self.data_models.items():
                    model_snake = ''.join('_' + c.lower() if c.isupper() else c.lower() for c in model_name).lstrip('_')
                    if model_snake in endpoint.url or model_name.lower() in endpoint.url.lower():
                        model_endpoints[model_name].append(endpoint_key)
                        assigned = True
                
                if not assigned:
                    model_endpoints["Other"].append(endpoint_key)
            
            # Print model-endpoint relationships
            for model_name, endpoints in sorted(model_endpoints.items()):
                report.append(f"{model_name}:")
                for endpoint in sorted(endpoints):
                    report.append(f"  ← {endpoint}")
                report.append("")
                
            report.append("```")
        else:
            report.append("\nInsufficient data to generate data flow analysis.\n")

        # Code Patterns
        report.append("\n### 2.4 Code Patterns")
        if self.code_patterns:
            # Group patterns by type
            patterns_by_type = defaultdict(list)
            for pattern in self.code_patterns:
                patterns_by_type[pattern.type].append(pattern)
                
            # Report patterns by type
            for pattern_type, patterns in sorted(patterns_by_type.items()):
                report.append(f"\n#### {pattern_type.replace('_', ' ').title()}\n")
                
                report.append("| Pattern | Description | Severity | Occurrences |")
                report.append("|---------|-------------|----------|------------|")
                
                for pattern in sorted(patterns, key=lambda p: p.severity):
                    severity_marker = {
                        "high": "🔴",
                        "medium": "🟠",
                        "low": "🟡"
                    }.get(pattern.severity, "")
                    
                    report.append(f"| {pattern.name} | {pattern.description} | {severity_marker} {pattern.severity} | {pattern.occurrences} |")
                    
                    # List some example locations
                    if pattern.locations:
                        report.append("\nExample locations:\n")
                        for location in pattern.locations[:5]:  # Limit to 5 examples
                            report.append(f"- `{location}`")
                        if len(pattern.locations) > 5:
                            report.append(f"- ...and {len(pattern.locations) - 5} more")
        else:
            report.append("\nNo code patterns or anti-patterns were detected.\n")
        
        # Backend Comparison
        if self.backend_dir and self.backend_comparison:
            report.append("\n### 2.5 Backend Compatibility Analysis")
            
            # Model matches
            report.append("\n#### Model Compatibility\n")
            if self.backend_comparison.model_matches:
                report.append("| Frontend Model | Backend Model | Match Quality |")
                report.append("|---------------|---------------|---------------|")
                
                for model_name, match_info in sorted(self.backend_comparison.model_matches.items()):
                    quality = match_info['match_quality']
                    quality_str = f"{quality*100:.1f}%"
                    quality_indicator = "✅" if quality > 0.7 else "⚠️" if quality > 0.4 else "❌"
                    
                    report.append(f"| {model_name} | {match_info['backend_name']} | {quality_indicator} {quality_str} |")
            else:
                report.append("No matching models found between frontend and backend.")
                
            # Endpoint matches
            report.append("\n#### API Endpoint Compatibility\n")
            if self.backend_comparison.endpoint_matches:
                report.append("| Frontend Endpoint | Backend Endpoint | Match Quality |")
                report.append("|------------------|------------------|---------------|")
                
                for endpoint_key, match_info in sorted(self.backend_comparison.endpoint_matches.items()):
                    quality = match_info['match_quality']
                    quality_str = f"{quality*100:.1f}%"
                    quality_indicator = "✅" if quality > 0.7 else "⚠️" if quality > 0.4 else "❌"
                    
                    report.append(f"| {endpoint_key} | {match_info['backend_url']} | {quality_indicator} {quality_str} |")
            else:
                report.append("No matching endpoints found between frontend and backend.")
                
            # Missing endpoints
            if self.backend_comparison.missing_endpoints:
                report.append("\n#### Missing Backend Endpoints\n")
                report.append("The following endpoints are used in frontend but not found in backend:")
                
                for endpoint in sorted(self.backend_comparison.missing_endpoints):
                    report.append(f"- `{endpoint}`")
                    
            # Unexpected endpoints
            if self.backend_comparison.unexpected_endpoints:
                report.append("\n#### Unexpected Backend Endpoints\n")
                report.append("The following endpoints exist in backend but are not used in frontend:")
                
                for endpoint in sorted(self.backend_comparison.unexpected_endpoints[:10]):  # Limit to 10
                    report.append(f"- `{endpoint}`")
                    
                if len(self.backend_comparison.unexpected_endpoints) > 10:
                    report.append(f"- ...and {len(self.backend_comparison.unexpected_endpoints) - 10} more")
        
        # Recommendations
        report.append("\n## 3. Recommendations")
        
        # Generate general recommendations
        recommendations = [
            "Ensure consistent naming conventions between frontend and backend",
            "Implement proper error handling for all API endpoints",
            "Add authentication middleware for protected endpoints",
            "Use Django serializers that match the frontend data structures",
            "Implement proper validation for all incoming data"
        ]
        
        # Add code pattern recommendations
        if self.code_patterns:
            for pattern in sorted(self.code_patterns, key=lambda p: p.severity):
                if pattern.severity == "high":
                    recommendations.append(f"Fix **{pattern.name}**: {pattern.description}")
        
        # Add model-specific recommendations
        for model_name, model in self.data_models.items():
            if len(model.fields) > 10:
                recommendations.append(f"Consider breaking down the {model_name} model as it has many fields")
        
        # Add API-specific recommendations
        http_method_counts = defaultdict(int)
        for endpoint in self.api_endpoints:
            http_method_counts[endpoint.method] += 1
            
        if http_method_counts.get("GET", 0) > 0 and http_method_counts.get("POST", 0) == 0:
            recommendations.append("The frontend only uses GET requests - ensure proper data modification methods are implemented")
        
        report.append("\n".join(f"- {recommendation}" for recommendation in recommendations))
        
        # Write report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
            
        logger.info(f"Report generated: {output_file}")
        
        return output_file

    def extract_component_name(self, file_path: str) -> str:
        """Extract React component name from file path or content using AST or regex"""
        # First try from filename (common convention)
        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        
        # Guard against empty names
        if not name:
            return ""
            
        # PascalCase convention for components
        if name[0].isupper():
            return name
            
        # Try to read file to find component name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if self.config['use_ast']:
                ast = self._parse_with_ast(content)
                if ast:
                    # Look for component definitions in AST
                    for node in ast.body:
                        if (node.type == 'FunctionDeclaration' and 
                            node.id and node.id.name[0].isupper()):
                            return node.id.name
                        elif (node.type == 'VariableDeclaration' and 
                              node.declarations and 
                              node.declarations[0].id.name[0].isupper()):
                            return node.declarations[0].id.name
                        elif (node.type == 'ClassDeclaration' and 
                              node.id and node.id.name[0].isupper()):
                            return node.id.name
            else:
                # Fallback to regex-based extraction
                for regex in COMPONENT_REGEXES:
                    match = regex.search(content)
                    if match and match.group(1)[0].isupper():
                        return match.group(1)
        except:
            pass
            
        # Fallback: use filename with first letter capitalized
        return name[0].upper() + name[1:] if name else ""

    def _print_component_tree(self, node: str, prefix: str, is_last: bool, report: List[str], visited: Set[str]):
        """Helper to print component tree structure"""
        if node in visited:
            report.append(f"{prefix}{'└── ' if is_last else '├── '}{node} (circular reference)")
            return
            
        visited.add(node)
        report.append(f"{prefix}{'└── ' if is_last else '├── '}{node}")
        
        # Get children that are components
        children = [n for n in self.graph.neighbors(node) 
                   if n in self.components and n != node]
        
        if not children:
            return
            
        new_prefix = prefix + ('    ' if is_last else '│   ')
        for i, child in enumerate(sorted(children)):
            # Pass the same visited set (don't copy it) to avoid quadratic time complexity
            self._print_component_tree(
                child, new_prefix, i == len(children) - 1, report, visited
            )

    def generate_json_report(self, output_file: str = "frontend_backend_report.json"):
        """Generate a JSON report with the analysis results"""
        # Create a serializable structure
        report = {
            "meta": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "frontend_directory": self.frontend_dir,
                "backend_directory": self.backend_dir,
                "analysis_time": self.stats['end_time'] - self.stats['start_time'],
            },
            "summary": {
                "api_endpoints": len(self.api_endpoints),
                "data_models": len(self.data_models),
                "components": len(self.components),
                "naming_issues": len(self.naming_issues),
                "code_patterns": len(self.code_patterns),
            },
            "api_endpoints": [endpoint.to_dict() for endpoint in self.api_endpoints],
            "data_models": {name: model.to_dict() for name, model in self.data_models.items()},
            "components": {name: comp.to_dict() for name, comp in self.components.items()},
            "naming_issues": [issue.to_dict() for issue in self.naming_issues],
            "code_patterns": [pattern.to_dict() for pattern in self.code_patterns],
        }
        
        # Add backend comparison if available
        if self.backend_dir and self.backend_comparison:
            report["backend_comparison"] = self.backend_comparison.to_dict()
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"JSON report generated: {output_file}")
        return output_file
    
    def generate_html_report(self, output_file: str = "frontend_backend_report.html"):
        """Generate an HTML report with the analysis results"""
        content = []
        
        # HTML header with CSS
        content.append("""<!DOCTYPE html>
<html>
<head>
    <title>Frontend-Backend Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #333; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .endpoint { background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .model { background: #f0f0f0; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .component { background: #e8e8e8; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .issue { color: #d32f2f; }
        .warning { color: #f57c00; }
        .success { color: #388e3c; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; }
        .stats { display: flex; flex-wrap: wrap; gap: 20px; }
        .stat-box { background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>""")
        
        # Title
        content.append(f"<h1>Frontend-Backend Analysis Report</h1>")
        content.append(f"<p>Generated from: <code>{self._escape_html(self.frontend_dir)}</code></p>")
        
        # Statistics
        content.append("<div class='stats'>")
        content.append(f"<div class='stat-box'><h3>Files Analyzed</h3><p>{self.stats['file_count']}</p></div>")
        content.append(f"<div class='stat-box'><h3>API Endpoints</h3><p>{len(self.api_endpoints)}</p></div>")
        content.append(f"<div class='stat-box'><h3>Data Models</h3><p>{len(self.data_models)}</p></div>")
        content.append(f"<div class='stat-box'><h3>Components</h3><p>{len(self.components)}</p></div>")
        content.append(f"<div class='stat-box'><h3>Issues Found</h3><p>{len(self.naming_issues)}</p></div>")
        content.append("</div>")
        
        # API Endpoints
        content.append("<div class='section'>")
        content.append("<h2>API Endpoints</h2>")
        if self.api_endpoints:
            content.append("<table>")
            content.append("<tr><th>Method</th><th>URL</th><th>Auth Required</th><th>Used By</th></tr>")
            for endpoint in sorted(self.api_endpoints, key=lambda x: (x.method, x.url)):
                content.append(f"<tr>")
                content.append(f"<td>{self._escape_html(endpoint.method)}</td>")
                content.append(f"<td><code>{self._escape_html(endpoint.url)}</code></td>")
                content.append(f"<td>{'Yes' if endpoint.auth_required else 'No'}</td>")
                content.append(f"<td>{', '.join(self._escape_html(c) for c in endpoint.components)}</td>")
                content.append("</tr>")
            content.append("</table>")
        else:
            content.append("<p>No API endpoints found.</p>")
        content.append("</div>")
        
        # Data Models
        content.append("<div class='section'>")
        content.append("<h2>Data Models</h2>")
        if self.data_models:
            for model_name, model in sorted(self.data_models.items()):
                content.append(f"<div class='model'>")
                content.append(f"<h3>{self._escape_html(model_name)}</h3>")
                if model.fields:
                    content.append("<table>")
                    content.append("<tr><th>Field</th><th>Type</th></tr>")
                    for field_name, types in sorted(model.fields.items()):
                        content.append(f"<tr>")
                        content.append(f"<td>{self._escape_html(field_name)}</td>")
                        content.append(f"<td>{', '.join(self._escape_html(t) for t in types)}</td>")
                        content.append("</tr>")
                    content.append("</table>")
                content.append("</div>")
        else:
            content.append("<p>No data models found.</p>")
        content.append("</div>")
        
        # Components
        content.append("<div class='section'>")
        content.append("<h2>React Components</h2>")
        if self.components:
            for component_name, component in sorted(self.components.items()):
                content.append(f"<div class='component'>")
                content.append(f"<h3>{self._escape_html(component_name)}</h3>")
                content.append(f"<p>File: <code>{self._escape_html(component.file_path)}</code></p>")
                if component.hooks:
                    content.append(f"<p>Hooks: {', '.join(self._escape_html(h) for h in component.hooks)}</p>")
                if component.complexity:
                    content.append(f"<p>Complexity: {component.complexity}</p>")
                content.append("</div>")
        else:
            content.append("<p>No React components found.</p>")
        content.append("</div>")
        
        # Issues
        if self.naming_issues:
            content.append("<div class='section'>")
            content.append("<h2>Issues Found</h2>")
            for issue in sorted(self.naming_issues, key=lambda x: x.severity):
                severity_class = {
                    'high': 'issue',
                    'medium': 'warning',
                    'low': 'success'
                }.get(issue.severity, '')
                
                content.append(f"<div class='{severity_class}'>")
                content.append(f"<h3>{self._escape_html(issue.type)}</h3>")
                content.append(f"<p>{self._escape_html(issue.description)}</p>")
                content.append(f"<p>Location: {self._escape_html(issue.location)}</p>")
                if issue.suggestion:
                    content.append(f"<p>Suggestion: {self._escape_html(issue.suggestion)}</p>")
                content.append("</div>")
            content.append("</div>")
        
        # Footer
        content.append("</body></html>")
        
        # Write report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
        logger.info(f"HTML report generated: {output_file}")
        return output_file
    
    def _generate_html_summary(self, content: List[str]):
        """Generate the summary section of the HTML report"""
        content.append("""
    <h2>Summary</h2>
    <div class="result-box">
        <table>
            <tr>
                <th>Metric</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>API Endpoints</td>
                <td>""" + str(len(self.api_endpoints)) + """</td>
            </tr>
            <tr>
                <td>Data Models</td>
                <td>""" + str(len(self.data_models)) + """</td>
            </tr>
            <tr>
                <td>React Components</td>
                <td>""" + str(len(self.components)) + """</td>
            </tr>
            <tr>
                <td>Naming Issues</td>
                <td>""" + str(len(self.naming_issues)) + """</td>
            </tr>
            <tr>
                <td>Code Patterns</td>
                <td>""" + str(len(self.code_patterns)) + """</td>
            </tr>
        </table>
    </div>
""")
    
    def _generate_html_models(self, content: List[str]):
        """Generate the data models section of the HTML report"""
        content.append("<h2>Data Models</h2>")
        
        if not self.data_models:
            content.append("<p>No data models could be inferred from the frontend code.</p>")
            return
            
        # Create a tab for each model
        content.append('<div class="tab-container">')
        content.append('<div class="tab-buttons">')
        
        for i, (model_name, _) in enumerate(sorted(self.data_models.items())):
            active = ' active' if i == 0 else ''
            content.append(f'<button class="tab-button{active}" onclick="showTab(\'model-{i}\')">{model_name}</button>')
            
        content.append('</div>') # Close tab buttons
        
        # Create tab content for each model
        for i, (model_name, model) in enumerate(sorted(self.data_models.items())):
            active = ' active' if i == 0 else ''
            content.append(f'<div id="model-{i}" class="tab-content{active}">')
            
            # Model fields
            if model.fields:
                content.append("<h3>Fields</h3>")
                content.append("<table>")
                content.append("<tr><th>Field</th><th>Types</th></tr>")
                
                for field_name, types in sorted(model.fields.items()):
                    types_str = ", ".join(sorted(types))
                    content.append(f"<tr><td>{field_name}</td><td>{types_str}</td></tr>")
                    
                content.append("</table>")
                
            # Model relationships
            if model.relationships:
                content.append("<h3>Relationships</h3>")
                content.append("<ul>")
                
                for related_model, rel_info in sorted(model.relationships.items()):
                    content.append(f"<li>{rel_info.relation_type} <code>{related_model}</code></li>")
                    
                content.append("</ul>")
                
            # Associated API endpoints
            if model.api_endpoints:
                content.append("<h3>API Endpoints</h3>")
                content.append("<ul>")
                
                for endpoint in sorted(model.api_endpoints):
                    content.append(f"<li><code>{endpoint}</code></li>")
                    
                content.append("</ul>")
                
            content.append("</div>") # Close tab content
            
        content.append("</div>") # Close tab container
        
        # Add JavaScript for tabs
        content.append("""
<script>
function showTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`button[onclick="showTab('${tabId}')"]`).classList.add('active');
}
</script>
""")
    
    def _generate_html_endpoints(self, content: List[str]):
        """Generate the API endpoints section of the HTML report"""
        content.append("<h2>API Endpoints</h2>")
        
        if not self.api_endpoints:
            content.append("<p>No API endpoints were found in the frontend code.</p>")
            return
            
        # Group endpoints by prefix for better organization
        endpoints_by_prefix = defaultdict(list)
        for endpoint in sorted(self.api_endpoints, key=lambda e: e.url):
            parts = endpoint.url.strip('/').split('/')
            prefix = parts[0] if parts else ""
            endpoints_by_prefix[prefix].append(endpoint)
            
        for prefix, endpoints in sorted(endpoints_by_prefix.items()):
            if prefix:
                content.append(f"<h3>/{prefix}</h3>")
            else:
                content.append("<h3>Root Endpoints</h3>")
                
            for endpoint in endpoints:
                content.append(f"""
<div class="result-box">
    <h4>{endpoint.method} {endpoint.url}</h4>
""")
                
                # Request parameters
                if endpoint.params:
                    content.append("<h5>Request Parameters</h5>")
                    content.append("<table>")
                    content.append("<tr><th>Parameter</th><th>Types</th></tr>")
                    
                    for param, types in sorted(endpoint.params.items()):
                        types_str = ", ".join(sorted(types))
                        content.append(f"<tr><td>{param}</td><td>{types_str}</td></tr>")
                        
                    content.append("</table>")
                
                # Response fields
                if endpoint.response_fields:
                    content.append("<h5>Response Fields</h5>")
                    content.append("<ul>")
                    
                    for field in sorted(endpoint.response_fields):
                        content.append(f"<li>{field}</li>")
                        
                    content.append("</ul>")
                
                content.append("</div>") # Close result box
    
    def _generate_html_patterns(self, content: List[str]):
        """Generate the code patterns section of the HTML report"""
        content.append("<h2>Code Patterns</h2>")
        
        if not self.code_patterns:
            content.append("<p>No code patterns or anti-patterns were detected.</p>")
            return
            
        # Group patterns by type
        patterns_by_type = defaultdict(list)
        for pattern in self.code_patterns:
            patterns_by_type[pattern.type].append(pattern)
            
        for pattern_type, patterns in sorted(patterns_by_type.items()):
            content.append(f"<h3>{pattern_type.replace('_', ' ').title()}</h3>")
            
            for pattern in sorted(patterns, key=lambda p: p.severity):
                severity_class = f"severity-{pattern.severity}"
                
                content.append(f"""
<div class="result-box">
    <h4>{pattern.name} <span class="{severity_class}">({pattern.severity})</span></h4>
    <p>{pattern.description}</p>
    <p>Occurrences: {pattern.occurrences}</p>
""")
                
                if pattern.locations:
                    content.append("<h5>Example Locations:</h5>")
                    content.append("<ul>")
                    
                    for location in pattern.locations[:5]:
                        content.append(f"<li><code>{location}</code></li>")
                        
                    if len(pattern.locations) > 5:
                        content.append(f"<li>...and {len(pattern.locations) - 5} more</li>")
                        
                    content.append("</ul>")
                    
                content.append("</div>") # Close result box
    
    def _generate_html_backend_comparison(self, content: List[str]):
        """Generate the backend comparison section of the HTML report"""
        content.append("<h2>Backend Compatibility</h2>")
        
        if not self.backend_comparison:
            content.append("<p>No backend compatibility analysis available.</p>")
            return
            
        # Model matches
        content.append("<h3>Model Compatibility</h3>")
        
        if self.backend_comparison.model_matches:
            content.append("<table>")
            content.append("<tr><th>Frontend Model</th><th>Backend Model</th><th>Match Quality</th></tr>")
            
            for model_name, match_info in sorted(self.backend_comparison.model_matches.items()):
                quality = match_info['match_quality']
                quality_str = f"{quality*100:.1f}%"
                quality_class = "severity-high" if quality > 0.7 else "severity-medium" if quality > 0.4 else "severity-low"
                
                content.append(f"""
<tr>
    <td>{model_name}</td>
    <td>{match_info['backend_name']}</td>
    <td class="{quality_class}">{quality_str}</td>
</tr>""")
                
            content.append("</table>")
        else:
            content.append("<p>No matching models found between frontend and backend.</p>")
            
        # Endpoint matches
        content.append("<h3>API Endpoint Compatibility</h3>")
        
        if self.backend_comparison.endpoint_matches:
            content.append("<table>")
            content.append("<tr><th>Frontend Endpoint</th><th>Backend Endpoint</th><th>Match Quality</th></tr>")
            
            for endpoint_key, match_info in sorted(self.backend_comparison.endpoint_matches.items()):
                quality = match_info['match_quality']
                quality_str = f"{quality*100:.1f}%"
                quality_class = "severity-high" if quality > 0.7 else "severity-medium" if quality > 0.4 else "severity-low"
                
                content.append(f"""
<tr>
    <td>{endpoint_key}</td>
    <td>{match_info['backend_url']}</td>
    <td class="{quality_class}">{quality_str}</td>
</tr>""")
                
            content.append("</table>")
        else:
            content.append("<p>No matching endpoints found between frontend and backend.</p>")

    # ---- Caching Functions ----

    def _get_cache_path(self, name: str) -> str:
        """Get a path for a cache file"""
        cache_dir = self.config['cache_dir']
        return os.path.join(cache_dir, f"{name}.json")

    def _cache_key(self, file_path: str) -> str:
        """Generate a cache key for a file based on its content hash"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Error generating cache key for {file_path}: {str(e)}")
            # Fallback to path-based key
            return hashlib.md5(file_path.encode()).hexdigest()

    def _save_to_cache(self, data: Any, name: str) -> None:
        """Save data to cache with proper serialization"""
        if not self.config['cache_results']:
            return
            
        cache_path = self._get_cache_path(name)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                if isinstance(data, (list, dict)):
                    json.dump(data, f, default=self._json_serializer)
                else:
                    # Try to convert to dict first
                    try:
                        if hasattr(data, 'to_dict'):
                            json.dump(data.to_dict(), f, default=self._json_serializer)
                        elif hasattr(data, '__dict__'):
                            json.dump(data.__dict__, f, default=self._json_serializer)
                    except:
                        logger.warning(f"Could not cache data of type {type(data)}")
        except Exception as e:
            logger.warning(f"Error saving to cache: {str(e)}")

    def _load_from_cache(self, name: str) -> Any:
        """Load data from cache with proper deserialization"""
        if not self.config['cache_results']:
            return None
            
        cache_path = self._get_cache_path(name)
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f, object_hook=self._json_deserializer)
        except Exception as e:
            logger.warning(f"Error loading from cache: {str(e)}")
            return None

    def _json_serializer(self, obj):
        """Custom JSON serializer for complex objects"""
        if isinstance(obj, (APIEndpoint, DataModel, ReactComponent, NamingIssue, CodePattern)):
            return obj.__dict__
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def _json_deserializer(self, obj):
        """Custom JSON deserializer for complex objects"""
        if 'url' in obj and 'method' in obj:
            return APIEndpoint(**obj)
        if 'name' in obj and 'fields' in obj:
            return DataModel(**obj)
        if 'name' in obj and 'file_path' in obj:
            return ReactComponent(**obj)
        if 'type' in obj and 'description' in obj:
            if 'severity' in obj:
                return CodePattern(**obj)
            return NamingIssue(**obj)
        return obj

    # ---- Report Generation ----

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters to prevent XSS"""
        return html.escape(text)

# ---- Pre-compiled regex patterns ----
API_REGEXES = [re.compile(p) for p in [
    r'(?:axios|fetch)\s*\.\s*(?:get|post|put|delete|patch)\s*\(\s*[\'"`](.*?)[\'"`]',
    r'(?:axios|fetch)\s*\(\s*[\'"`](.*?)[\'"`]',
    r'(?:axios|fetch)\s*\(\s*{\s*url\s*:\s*[\'"`](.*?)[\'"`]',
    r'const\s+\w+\s*=\s*await\s+(?:axios|fetch)\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.request\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.get\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.post\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.put\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.delete\s*\(\s*[\'"`](.*?)[\'"`]',
    r'\.patch\s*\(\s*[\'"`](.*?)[\'"`]',
    r'useSWR\s*\(\s*[\'"`](.*?)[\'"`]',
    r'useQuery\s*\(\s*[\'"`](.*?)[\'"`]',
]]

HOOK_REGEX = re.compile(r'\buse[A-Z]\w*\(')
COMPONENT_REGEXES = [
    re.compile(r'function\s+([A-Z]\w+)\s*\('),
    re.compile(r'const\s+([A-Z]\w+)\s*='),
    re.compile(r'class\s+([A-Z]\w+)\s+extends'),
]
URL_PATTERN_REGEX = re.compile(r"(?:path|url|re_path)\s*\(\s*['\"]([^'\"]*)['\"]")
VIEWSET_REGEX = re.compile(r"class\s+(\w+)ViewSet\s*\(")

# ---- Helper Functions ----

def extract_url_patterns(urls: List[str]) -> List[str]:
    """Extract Django URL patterns from a list of URLs"""
    patterns = []
    seen_prefixes = set()
    
    for url in urls:
        parts = url.strip('/').split('/')
        if not parts:
            continue
            
        # Handle API versioning
        if parts[0] in ('api', 'v1', 'v2'):
            prefix = parts[0]
            if prefix not in seen_prefixes:
                patterns.append(f"path('{prefix}/', include('{prefix}.urls'))")
                seen_prefixes.add(prefix)
            parts = parts[1:]
            
        # Build pattern for remaining parts
        pattern_parts = []
        for part in parts:
            if part.startswith(':') or (part.startswith('{') and part.endswith('}')):
                # Convert :id or {id} to <int:id> or <str:id>
                param_name = part.strip('{}:')
                pattern_parts.append(f"<int:{param_name}>")
            else:
                pattern_parts.append(part)
                
        if pattern_parts:
            pattern = f"path('{'/'.join(pattern_parts)}/', views.{''.join(p.title() for p in pattern_parts)}View.as_view())"
            patterns.append(pattern)
            
    return patterns

def get_django_field_type(js_type: str, field_name: str) -> str:
    """Convert JavaScript/TypeScript type to Django field type"""
    # Common type mappings
    type_map = {
        'string': 'CharField',
        'number': 'IntegerField',
        'boolean': 'BooleanField',
        'date': 'DateField',
        'datetime': 'DateTimeField',
        'array': 'ArrayField',
        'object': 'JSONField',
        'email': 'EmailField',
        'url': 'URLField',
        'text': 'TextField',
        'float': 'FloatField',
        'decimal': 'DecimalField',
        'uuid': 'UUIDField',
        'file': 'FileField',
        'image': 'ImageField',
    }
    
    # Special field name patterns
    if field_name.endswith('_at'):
        return 'DateTimeField(auto_now=True)'
    if field_name.endswith('_by'):
        return 'ForeignKey(User, on_delete=models.SET_NULL, null=True)'
    if field_name.endswith('_id'):
        return 'ForeignKey(null=True, blank=True)'
    if field_name == 'id':
        return 'AutoField(primary_key=True)'
    if field_name == 'created_at':
        return 'DateTimeField(auto_now_add=True)'
    if field_name == 'updated_at':
        return 'DateTimeField(auto_now=True)'
        
    # Default to CharField if type not found
    return type_map.get(js_type.lower(), 'CharField(max_length=255)')

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Frontend-Backend Analysis Tool')
    parser.add_argument('--frontend-dir', '-f', required=True, help='Frontend directory path')
    parser.add_argument('--backend-dir', '-b', help='Optional backend directory for comparison')
    parser.add_argument('--output', '-o', default='frontend_backend_report.md', help='Output report file')
    parser.add_argument('--parallel', '-p', action='store_true', help='Enable parallel processing')
    parser.add_argument('--include-tests', '-t', action='store_true', help='Include test files in analysis')
    parser.add_argument('--cache', '-c', action='store_true', help='Enable result caching')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-level', '-l', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set logging level')
    parser.add_argument('--format', 
                        choices=['md', 'json', 'html'],
                        default='md',
                        help='Output format (markdown, JSON, or HTML)')
    parser.add_argument('--use-ast',
                        action='store_true',
                        help='Use AST-based parsing (requires esprima)')
    parser.add_argument('--ast-timeout',
                        type=int,
                        default=5,
                        help='Timeout in seconds for AST parsing')
    parser.add_argument('--max-workers',
                        type=int,
                        default=multiprocessing.cpu_count(),
                        help='Maximum number of worker processes')
    parser.add_argument('--exclude-dirs',
                        nargs='+',
                        default=EXCLUDED_DIRS,
                        help='Directories to exclude from analysis')
    parser.add_argument('--exclude-files',
                        nargs='+',
                        default=TEST_FILE_PATTERNS,
                        help='File patterns to exclude from analysis')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = getattr(logging, args.log_level)
    if args.verbose:
        log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    
    # Add file handler for logging
    log_file = 'analyzer.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    try:
        # Configure analyzer
        config = {
            'parallel_processing': args.parallel,
            'max_workers': args.max_workers,
            'include_tests': args.include_tests,
            'cache_results': args.cache,
            'verbose': args.verbose,
            'output_format': args.format,
            'use_ast': args.use_ast,
            'ast_timeout': args.ast_timeout,
            'excluded_dirs': args.exclude_dirs,
            'excluded_files': args.exclude_files,
        }
        
        # Validate directories
        if not os.path.isdir(args.frontend_dir):
            raise ValueError(f"Frontend directory does not exist: {args.frontend_dir}")
        if args.backend_dir and not os.path.isdir(args.backend_dir):
            raise ValueError(f"Backend directory does not exist: {args.backend_dir}")
            
        # Create analyzer instance
        analyzer = FrontendBackendAnalyzer(args.frontend_dir, args.backend_dir, config)
        
        # Run analysis
        start_time = time.time()
        analyzer.analyze()
        duration = time.time() - start_time
        
        # Generate appropriate output format
        if args.format == 'md':
            report_path = analyzer.generate_report(args.output)
            logger.info(f"Analysis complete in {duration:.2f} seconds. Markdown report saved to: {report_path}")
        elif args.format == 'json':
            json_path = args.output.replace('.md', '.json')
            analyzer.generate_json_report(json_path)
            logger.info(f"Analysis complete in {duration:.2f} seconds. JSON report saved to: {json_path}")
        elif args.format == 'html':
            html_path = args.output.replace('.md', '.html')
            analyzer.generate_html_report(html_path)
            logger.info(f"Analysis complete in {duration:.2f} seconds. HTML report saved to: {html_path}")
            
        # Print summary
        print("\nAnalysis Summary:")
        print(f"- Files analyzed: {analyzer.stats['file_count']}")
        print(f"- API endpoints found: {len(analyzer.api_endpoints)}")
        print(f"- Data models inferred: {len(analyzer.data_models)}")
        print(f"- React components analyzed: {len(analyzer.components)}")
        print(f"- Issues found: {len(analyzer.naming_issues)}")
        print(f"- AST parse errors: {analyzer.stats['ast_parse_errors']}")
        print(f"- AST parse timeouts: {analyzer.stats['ast_parse_timeouts']}")
        print(f"- Total duration: {duration:.2f} seconds")
        
        # Exit with error if issues found
        if analyzer.naming_issues:
            high_severity = sum(1 for i in analyzer.naming_issues if i.severity == 'high')
            if high_severity > 0:
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        print(f"See {log_file} for details")
        sys.exit(1)
    finally:
        # Clean up logging handlers
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)

if __name__ == '__main__':
    main()