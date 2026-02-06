"""
Core modules for the Low-Code Performance Scanner.

This package contains the main scanner components:
- LowCodePerformanceScanner: Main scanner class
- ScannerConfig: Configuration management
- PerformanceOrchestrator: Test orchestration
- PlatformDetector: Platform detection and analysis
- ScenarioRunner: Scenario execution
- PerformanceScoringEngine: Performance scoring and normalization
"""

from .scanner import (
    LowCodePerformanceScanner,
    ScannerConfig,
)

from .orchestrator import PerformanceOrchestrator
from .platform_detector import (
    PlatformDetector,
    BubbleAnalyzer,
    OutSystemsAnalyzer,
    AirtableAnalyzer,
    PlatformAnalysisResult,
)
from .scenario_runner import ScenarioRunner
from .scoring_engine import (
    PerformanceScoringEngine,
    ScoringWeights,
    MetricThreshold,
    SensitivityResult,
    get_default_scoring_engine,
    get_mobile_optimized_scoring_engine,
)

__all__ = [
    # Main scanner
    "LowCodePerformanceScanner",
    "ScannerConfig",
    
    # Components
    "PerformanceOrchestrator",
    "PlatformDetector",
    "ScenarioRunner",
    
    # Scoring Engine
    "PerformanceScoringEngine",
    "ScoringWeights",
    "MetricThreshold",
    "SensitivityResult",
    "get_default_scoring_engine",
    "get_mobile_optimized_scoring_engine",
    
    # Platform Analyzers
    "BubbleAnalyzer",
    "OutSystemsAnalyzer",
    "AirtableAnalyzer",
    "PlatformAnalysisResult",
]
