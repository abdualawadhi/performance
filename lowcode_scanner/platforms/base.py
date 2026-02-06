"""Base platform analyzer implementing the Strategy pattern.

This module provides the abstract base class for all platform analyzers,
enabling consistent analysis across different low-code/no-code platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import statistics


@dataclass
class PlatformMetrics:
    """Universal metrics applicable to all platforms.
    
    These metrics provide a common baseline for cross-platform comparison,
    essential for comparative analysis in academic research.
    """
    # Timing Metrics
    platform_overhead_ms: float = 0.0
    framework_bootstrap_ms: float = 0.0
    custom_code_execution_ms: float = 0.0
    third_party_impact_ms: float = 0.0
    
    # Resource Metrics
    generated_code_size_kb: float = 0.0
    platform_assets_size_kb: float = 0.0
    
    # Complexity Metrics
    component_count: int = 0
    data_binding_count: int = 0
    custom_script_count: int = 0
    
    # Performance Indicators
    cache_hit_ratio: float = 0.0
    lazy_load_efficiency: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            'platform_overhead_ms': self.platform_overhead_ms,
            'framework_bootstrap_ms': self.framework_bootstrap_ms,
            'custom_code_execution_ms': self.custom_code_execution_ms,
            'third_party_impact_ms': self.third_party_impact_ms,
            'generated_code_size_kb': self.generated_code_size_kb,
            'platform_assets_size_kb': self.platform_assets_size_kb,
            'component_count': self.component_count,
            'data_binding_count': self.data_binding_count,
            'custom_script_count': self.custom_script_count,
            'cache_hit_ratio': self.cache_hit_ratio,
            'lazy_load_efficiency': self.lazy_load_efficiency,
        }


@dataclass
class PlatformRecommendation:
    """Platform-specific optimization recommendation.
    
    Structured according to academic best practices for
    reproducible performance optimization research.
    """
    category: str
    title: str
    description: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    effort: str    # 'low', 'medium', 'high'
    impact_score: float  # 0-100
    confidence: float    # 0-1 based on evidence
    implementation_steps: List[str] = field(default_factory=list)
    academic_rationale: str = ""  # Research-backed justification
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'effort': self.effort,
            'impact_score': self.impact_score,
            'confidence': self.confidence,
            'implementation_steps': self.implementation_steps,
            'academic_rationale': self.academic_rationale,
        }


@dataclass
class PlatformSignature:
    """Detected platform signature for verification."""
    platform_id: str
    detected_version: Optional[str]
    detected_features: List[str]
    confidence_score: float  # 0-1 detection confidence
    detection_method: str    # How platform was identified


class PlatformAnalyzer(ABC):
    """Abstract base class for platform-specific analysis.
    
    Implements the Strategy pattern to enable polymorphic platform analysis.
    This design allows the scanner to treat all platforms uniformly while
    enabling platform-specific optimizations.
    
    Design Principles:
    1. Open/Closed: New platforms added without modifying existing code
    2. Single Responsibility: Each analyzer handles one platform
    3. Liskov Substitution: All analyzers interchangeable
    """
    
    def __init__(self, url: str, platform_def: 'PlatformDefinition'):
        self.url = url
        self.platform_def = platform_def
        self.metrics = PlatformMetrics()
        self._detection_data: Dict[str, Any] = {}
        self._performance_traces: List[Dict] = []
    
    @abstractmethod
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Detect platform-specific signatures.
        
        Args:
            page_content: HTML/JS content of the page
            headers: HTTP response headers
            
        Returns:
            PlatformSignature with detection confidence
        """
        pass
    
    @abstractmethod
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Calculate platform framework overhead in milliseconds.
        
        This isolates the performance cost of the platform itself
        versus application-specific code.
        """
        pass
    
    @abstractmethod
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Identify platform-specific performance bottlenecks.
        
        Returns structured bottleneck data with:
        - bottleneck_type: Category of bottleneck
        - severity: Impact level (1-10)
        - location: Where in the platform it occurs
        - evidence: Performance data supporting identification
        """
        pass
    
    @abstractmethod
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Calculate impact of custom code vs platform code.
        
        Distinguishes between:
        - Platform-generated code overhead
        - User custom code impact
        - Third-party integration cost
        """
        pass
    
    @abstractmethod
    def generate_platform_recommendations(self) -> List[PlatformRecommendation]:
        """Generate platform-specific optimization recommendations.
        
        Each recommendation must include academic rationale
        citing performance best practices.
        """
        pass
    
    @abstractmethod
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract platform-specific metrics from raw performance data."""
        pass
    
    def calculate_efficiency_score(self) -> float:
        """Calculate overall platform efficiency score (0-100).
        
        Algorithm:
        - Base score: 100
        - Deduct for platform overhead (>100ms: -10 per 100ms)
        - Deduct for custom code inefficiency
        - Bonus for effective caching (>80% hit rate: +10)
        """
        score = 100.0
        
        # Platform overhead penalty
        if self.metrics.platform_overhead_ms > 100:
            score -= (self.metrics.platform_overhead_ms / 100) * 10
        
        # Custom code inefficiency
        if self.metrics.custom_code_execution_ms > self.metrics.platform_overhead_ms:
            score -= 15
        
        # Third-party impact
        if self.metrics.third_party_impact_ms > 500:
            score -= 10
        
        # Caching bonus
        if self.metrics.cache_hit_ratio > 0.8:
            score += 10
        
        return max(0, min(100, score))
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Generate comprehensive analysis summary."""
        return {
            'platform': self.platform_def.name,
            'platform_id': self.platform_def.id,
            'category': self.platform_def.category.value,
            'efficiency_score': self.calculate_efficiency_score(),
            'metrics': self.metrics.to_dict(),
            'recommendations_count': len(self.generate_platform_recommendations()),
            'analysis_timestamp': datetime.utcnow().isoformat(),
        }
