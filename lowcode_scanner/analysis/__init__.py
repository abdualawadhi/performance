"""
Analysis modules for low-code performance scanner.

This package provides advanced analysis capabilities:
- Critical path analysis
- Regression detection
- Platform-specific analyzers
"""

from .critical_path_analyzer import (
    CriticalPathAnalyzer,
    CriticalPathAnalysis,
    ResourceNode,
    TTFBBreakdown,
    analyze_from_scan_result,
)

from .regression_detector import (
    RegressionDetector,
    BaselineStore,
    RegressionReport,
    DeltaAnalysis,
    TrendAnalysis,
    MetricBaseline,
    RegressionSeverity,
    TrendDirection,
    compare_scan_results,
)

__all__ = [
    # Critical Path Analysis
    "CriticalPathAnalyzer",
    "CriticalPathAnalysis",
    "ResourceNode",
    "TTFBBreakdown",
    "analyze_from_scan_result",
    
    # Regression Detection
    "RegressionDetector",
    "BaselineStore",
    "RegressionReport",
    "DeltaAnalysis",
    "TrendAnalysis",
    "MetricBaseline",
    "RegressionSeverity",
    "TrendDirection",
    "compare_scan_results",
]
