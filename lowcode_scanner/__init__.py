"""
Professional Low-Code Performance Scanner
==========================================

A comprehensive performance testing solution specifically designed for low-code
web applications including Bubble.io, OutSystems, and Airtable.

This package provides:
- Comprehensive performance matrix generation
- Memory usage monitoring with peak tracking
- Performance traces (Scripting, Rendering, Paint)
- Timeline screenshots and video recordings
- Platform-specific optimizations
- Professional HTML/PDF/Excel report generation
- Executive summaries with actionable recommendations

Quick Start:
    >>> import asyncio
    >>> from lowcode_scanner.core import LowCodePerformanceScanner, ScannerConfig
    >>> from lowcode_scanner.models import ScenarioType, DeviceType
    >>>
    >>> config = ScannerConfig(
    ...     scenarios=[ScenarioType.HOMEPAGE_LOAD, ScenarioType.HEAVY_LIST_LOAD],
    ...     device_types=[DeviceType.DESKTOP, DeviceType.MOBILE],
    ...     capture_screenshots=True,
    ... )
    >>>
    >>> scanner = LowCodePerformanceScanner(config)
    >>> result = asyncio.run(scanner.scan_url("https://myapp.bubbleapps.io/"))
    >>> print(f"Performance Score: {result.performance_matrix.overall_score}/100")

For more information, see the documentation at:
https://docs.lowcode-performance-scanner.com
"""

__version__ = "1.0.2"
__author__ = "Professional Performance Scanner Team"
__license__ = "MIT"
__email__ = "support@lowcode-scanner.com"

# Core exports for convenient imports
from .core import (
    LowCodePerformanceScanner,
    PerformanceOrchestrator,
    PlatformDetector,
    ScannerConfig,
    ScenarioRunner,
)
from .models import (
    CoreWebVitals,
    DeviceType,
    LowCodePerformanceMetrics,
    LowCodePlatform,
    MemoryUsageMetrics,
    NetworkCondition,
    NetworkMetrics,
    PerformanceCategory,
    PerformanceMatrix,
    PerformanceTrace,
    ReportFormat,
    ResourceMetrics,
    ScanResult,
    ScanSession,
    ScenarioMetrics,
    ScenarioType,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core scanner
    "LowCodePerformanceScanner",
    "ScannerConfig",
    "PerformanceOrchestrator",
    "PlatformDetector",
    "ScenarioRunner",
    # Performance models
    "LowCodePerformanceMetrics",
    "ScenarioMetrics",
    "CoreWebVitals",
    "MemoryUsageMetrics",
    "NetworkMetrics",
    "ResourceMetrics",
    "PerformanceTrace",
    # Results models
    "ScanResult",
    "ScanSession",
    "PerformanceMatrix",
    # Enums
    "LowCodePlatform",
    "ScenarioType",
    "DeviceType",
    "NetworkCondition",
    "ReportFormat",
    "PerformanceCategory",
]


def get_version():
    """Get the current version of the scanner."""
    return __version__


def get_supported_platforms():
    """Get list of supported low-code platforms."""
    return [platform.value for platform in LowCodePlatform]


def get_available_scenarios():
    """Get list of available test scenarios."""
    return [scenario.value for scenario in ScenarioType]


# Package-level configuration
DEFAULT_CONFIG = {
    "scenarios": [
        ScenarioType.HOMEPAGE_LOAD,
        ScenarioType.REGULAR_USE_CASE,
        ScenarioType.HEAVY_LIST_LOAD,
        ScenarioType.UPFRONT_SCRIPTING,
    ],
    "device_types": [DeviceType.DESKTOP, DeviceType.MOBILE],
    "network_conditions": [NetworkCondition.WIFI],
    "capture_screenshots": True,
    "record_videos": True,
    "enable_performance_profiling": True,
}
