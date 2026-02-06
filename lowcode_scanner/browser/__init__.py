"""
Browser Automation Module for Low-Code Performance Scanner

This module provides comprehensive browser automation capabilities for performance
testing of low-code web applications, including memory monitoring, performance
tracing, and screenshot capture.
"""

from .automation import BrowserAutomation, BrowserConfig
from .memory_monitor import MemoryMonitor
from .network_monitor import NetworkMonitor
from .performance_tracer import PerformanceTracer
from .screenshot_handler import ScreenshotHandler

__all__ = [
    "BrowserAutomation",
    "BrowserConfig",
    "MemoryMonitor",
    "PerformanceTracer",
    "ScreenshotHandler",
    "NetworkMonitor",
]
