"""Central registry for platform detection and management.

This module implements the Registry pattern for platform management,
enabling extensible platform support with clean separation of concerns.
"""

from typing import Dict, List, Type, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class PlatformCategory(Enum):
    """Classification of platform types for academic categorization."""
    LOW_CODE = "low_code"           # Visual development with some coding
    NO_CODE = "no_code"             # Pure visual development
    ECOMMERCE = "ecommerce"         # Commerce-focused platforms
    CMS = "cms"                     # Content management systems
    GENERIC = "generic"             # Unknown/unsupported platforms


@dataclass(frozen=True)
class PlatformDefinition:
    """Immutable definition of a supported platform.
    
    Attributes:
        id: Unique identifier (e.g., 'shopify', 'webflow')
        name: Human-readable name
        category: Platform classification for research taxonomy
        url_patterns: List of URL patterns for detection
        analyzer_class: Class implementing platform-specific analysis
        version_detection: Optional regex for version extraction
        feature_detection: Dict of feature identifiers to detection logic
    """
    id: str
    name: str
    category: PlatformCategory
    url_patterns: List[str]
    analyzer_class: Type['PlatformAnalyzer']
    version_detection: Optional[str] = None
    feature_detection: Dict[str, Callable] = field(default_factory=dict)
    
    def matches_url(self, url: str) -> bool:
        """Check if URL matches this platform."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.url_patterns)


class PlatformRegistry:
    """Central registry implementing the Registry pattern.
    
    Design Rationale:
    - Enables loose coupling between detection and analysis
    - Supports Open/Closed Principle (open for extension, closed for modification)
    - Facilitates academic research categorization
    - Allows runtime platform registration for plugin architecture
    """
    
    _platforms: Dict[str, PlatformDefinition] = {}
    _detection_order: List[str] = []  # Priority order for detection
    
    @classmethod
    def register(cls, definition: PlatformDefinition, priority: int = 0):
        """Register a platform with optional priority.
        
        Args:
            definition: Platform definition to register
            priority: Detection priority (higher = checked first)
        """
        cls._platforms[definition.id] = definition
        # Insert at appropriate priority position
        if priority > 0 and len(cls._detection_order) > 0:
            cls._detection_order.insert(0, definition.id)
        else:
            cls._detection_order.append(definition.id)
    
    @classmethod
    def detect_platform(cls, url: str) -> PlatformDefinition:
        """Detect platform from URL using registered patterns.
        
        Algorithm:
        1. Check URL against registered patterns in priority order
        2. Return first matching platform
        3. Return generic platform if no match
        
        Time Complexity: O(n*m) where n=platforms, m=patterns per platform
        """
        for platform_id in cls._detection_order:
            platform = cls._platforms.get(platform_id)
            if platform and platform.matches_url(url):
                return platform
        
        # Return generic fallback
        return cls._platforms.get('generic', cls._create_generic_definition())
    
    @classmethod
    def get_analyzer(cls, url: str) -> 'PlatformAnalyzer':
        """Get appropriate analyzer for URL."""
        platform = cls.detect_platform(url)
        return platform.analyzer_class(url, platform)
    
    @classmethod
    def list_by_category(cls, category: PlatformCategory) -> List[PlatformDefinition]:
        """List platforms by category for research taxonomy."""
        return [p for p in cls._platforms.values() if p.category == category]
    
    @classmethod
    def get_all_platforms(cls) -> Dict[str, PlatformDefinition]:
        """Get all registered platforms."""
        return cls._platforms.copy()
    
    @classmethod
    def _create_generic_definition(cls) -> PlatformDefinition:
        """Create default generic platform definition."""
        from .implementations.generic import GenericPlatformAnalyzer
        return PlatformDefinition(
            id='generic',
            name='Generic Web Application',
            category=PlatformCategory.GENERIC,
            url_patterns=[],
            analyzer_class=GenericPlatformAnalyzer
        )
