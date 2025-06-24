"""
Data models for Django backend analyzer.

This module contains dataclasses that represent Django components being analyzed.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Protocol


@dataclass
class ModelField:
    """Represents a field in a Django model"""
    name: str
    field_type: str
    options: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name}: {self.field_type}"


@dataclass
class Relationship:
    """Represents a relationship between Django models"""
    field_name: str
    relation_type: str
    related_model: str
    related_name: Optional[str] = None


@dataclass
class ModelInfo:
    """Information about a Django model"""
    name: str
    app_name: str
    fields: List[ModelField] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.app_name}.{self.name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'app_name': self.app_name,
            'fields': [{'name': f.name, 'field_type': f.field_type, 'options': f.options} for f in self.fields],
            'relationships': [
                {'field_name': r.field_name, 'relation_type': r.relation_type, 
                 'related_model': r.related_model, 'related_name': r.related_name}
                for r in self.relationships
            ],
            'meta': self.meta
        }


@dataclass
class SerializerInfo:
    """Information about a Django REST Framework serializer"""
    name: str
    model: Optional[str] = None
    fields: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    read_only_fields: List[str] = field(default_factory=list)
    write_only_fields: List[str] = field(default_factory=list)
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name} → {self.model}" if self.model else self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'model': self.model,
            'fields': self.fields,
            'meta': self.meta,
            'read_only_fields': self.read_only_fields,
            'write_only_fields': self.write_only_fields,
            'extra_kwargs': self.extra_kwargs
        }


@dataclass
class ViewInfo:
    """Information about a Django view or viewset"""
    name: str
    view_type: str  # APIView, ViewSet, ModelViewSet, etc.
    model: Optional[str] = None
    serializer: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.view_type})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'view_type': self.view_type,
            'model': self.model,
            'serializer': self.serializer,
            'methods': self.methods,
            'permissions': self.permissions
        }


@dataclass
class URLInfo:
    """Information about a Django URL pattern"""
    pattern: str
    view: str
    name: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.pattern} → {self.view} ({self.name})" if self.name else f"{self.pattern} → {self.view}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'pattern': self.pattern,
            'view': self.view,
            'name': self.name
        }


@dataclass
class APIEndpoint:
    """Represents an API endpoint derived from URLs and views"""
    path: str
    method: str
    view: str
    name: Optional[str] = None
    model: Optional[str] = None
    serializer: Optional[str] = None
    permissions: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.method} {self.path} → {self.view}"
    
    def get_endpoint_key(self) -> Tuple[str, str]:
        """Create a unique key for deduplication"""
        import re
        # Normalize the path to handle URL parameters consistently
        normalized_path = re.sub(r'<[^>]+>', '<param>', self.path)
        return (self.method, normalized_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'path': self.path,
            'method': self.method,
            'view': self.view,
            'name': self.name,
            'model': self.model,
            'serializer': self.serializer,
            'permissions': self.permissions
        }


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue between frontend and backend"""
    issue_type: str  # naming, field_mismatch, serializer_model, etc.
    description: str
    severity: str = "warning"  # info, warning, error
    file: Optional[str] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.issue_type}: {self.description}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'issue_type': self.issue_type,
            'description': self.description,
            'severity': self.severity,
            'file': self.file,
            'line': self.line
        }


class AnalyzerPlugin(Protocol):
    """
    Protocol for backend analyzer plugins.
    
    Plugins can provide custom checks or extensions to the analysis process.
    """
    
    def initialize(self, analyzer) -> None:
        """Initialize the plugin with the analyzer instance"""
        ...
    
    def check(self, analysis_data: Dict[str, Any]) -> List[CompatibilityIssue]:
        """
        Perform custom checks on the analysis data.
        
        Args:
            analysis_data: The analysis data to check
            
        Returns:
            List of compatibility issues found
        """
        ... 