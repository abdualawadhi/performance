"""
Memory Monitoring Module for Low-Code Performance Scanner

This module provides comprehensive memory usage monitoring during browser
automation, including heap size tracking, garbage collection monitoring,
and memory leak detection.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Page

from ..models.performance_metrics import MemoryUsageMetrics


class MemoryMonitor:
    """Memory usage monitor for browser performance testing."""

    def __init__(self, page: Page):
        """Initialize memory monitor."""
        self.page = page
        self.logger = logging.getLogger(__name__)

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None

        # Memory data collection
        self.memory_samples: List[Dict[str, float]] = []
        self.gc_events: List[Dict[str, Any]] = []

        # Peak tracking
        self.peak_heap_size_mb = 0.0
        self.initial_heap_size_mb = 0.0
        self.final_heap_size_mb = 0.0

        # DOM tracking
        self.peak_dom_nodes = 0
        self.peak_event_listeners = 0

        # GC tracking
        self.major_gc_count = 0
        self.minor_gc_count = 0
        self.total_gc_time_ms = 0.0

        # Sampling configuration
        self.sample_interval_ms = 1000  # Sample every 1 second
        self.max_samples = 300  # Maximum samples to keep in memory

    async def initialize(self) -> None:
        """Initialize memory monitoring."""
        try:
            # Enable Chrome DevTools Protocol for memory monitoring
            self.cdp = await self.page.context.new_cdp_session(self.page)

            # Enable runtime domain for memory info
            await self.cdp.send("Runtime.enable")

            # Enable heap profiler for detailed memory tracking
            await self.cdp.send("HeapProfiler.enable")

            # Listen to GC events
            self.cdp.on("HeapProfiler.lastSeenObjectId", self._handle_heap_event)

            # Get initial memory baseline
            await self._sample_memory()
            if self.memory_samples:
                self.initial_heap_size_mb = self.memory_samples[0].get(
                    "heap_used_mb", 0.0
                )

            self.logger.debug("Memory monitor initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize memory monitor: {str(e)}")
            raise

    async def start_monitoring(self) -> None:
        """Start continuous memory monitoring."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.memory_samples.clear()
        self.gc_events.clear()

        # Reset counters
        self.peak_heap_size_mb = 0.0
        self.peak_dom_nodes = 0
        self.peak_event_listeners = 0
        self.major_gc_count = 0
        self.minor_gc_count = 0
        self.total_gc_time_ms = 0.0

        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.debug("Started memory monitoring")

    async def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

        # Get final memory reading
        await self._sample_memory()
        if self.memory_samples:
            self.final_heap_size_mb = self.memory_samples[-1].get("heap_used_mb", 0.0)

        self.logger.debug("Stopped memory monitoring")

    async def _monitoring_loop(self) -> None:
        """Main memory monitoring loop."""
        try:
            while self.is_monitoring:
                await self._sample_memory()
                await asyncio.sleep(self.sample_interval_ms / 1000)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error in memory monitoring loop: {str(e)}")

    async def _sample_memory(self) -> None:
        """Take a memory usage sample."""
        try:
            timestamp = datetime.now(timezone.utc).timestamp() * 1000

            # Get heap usage from Chrome DevTools
            heap_usage = await self.cdp.send("Runtime.getHeapUsage")

            # Get memory info from JavaScript
            memory_info = await self.page.evaluate("""
                () => {
                    const memInfo = performance.memory || {};
                    const domNodes = document.querySelectorAll('*').length;
                    const eventListeners = window.getEventListeners ?
                        Object.keys(window.getEventListeners(document)).length : 0;

                    return {
                        jsHeapSizeLimit: memInfo.jsHeapSizeLimit || 0,
                        totalJSHeapSize: memInfo.totalJSHeapSize || 0,
                        usedJSHeapSize: memInfo.usedJSHeapSize || 0,
                        domNodes: domNodes,
                        eventListeners: eventListeners
                    };
                }
            """)

            # Convert bytes to MB - use only CDP reported usage to avoid double counting
            # with performance.memory which reports the same JS heap
            heap_used_mb = heap_usage.get("usedSize", 0) / (1024 * 1024)
            heap_total_mb = heap_usage.get("totalSize", 0) / (1024 * 1024)
            heap_limit_mb = memory_info.get("jsHeapSizeLimit", 0) / (1024 * 1024)

            # Create memory sample
            sample = {
                "timestamp": timestamp,
                "heap_used_mb": heap_used_mb,
                "heap_total_mb": heap_total_mb,
                "heap_limit_mb": heap_limit_mb,
                "dom_nodes": memory_info.get("domNodes", 0),
                "event_listeners": memory_info.get("eventListeners", 0),
            }

            # Add sample to collection
            self.memory_samples.append(sample)

            # Update peaks
            self.peak_heap_size_mb = max(self.peak_heap_size_mb, heap_used_mb)
            self.peak_dom_nodes = max(self.peak_dom_nodes, sample["dom_nodes"])
            self.peak_event_listeners = max(
                self.peak_event_listeners, sample["event_listeners"]
            )

            # Limit sample count
            if len(self.memory_samples) > self.max_samples:
                self.memory_samples.pop(0)

        except Exception as e:
            self.logger.debug(f"Error sampling memory: {str(e)}")

    async def _handle_heap_event(self, event: Dict[str, Any]) -> None:
        """Handle heap profiler events."""
        try:
            # This is a simplified GC event handler
            # In practice, you'd need more sophisticated GC event detection
            self.minor_gc_count += 1

        except Exception as e:
            self.logger.debug(f"Error handling heap event: {str(e)}")

    async def force_garbage_collection(self) -> Dict[str, float]:
        """Force garbage collection and return before/after memory usage."""
        try:
            # Get memory before GC
            before_sample = await self.page.evaluate("""
                () => {
                    const memInfo = performance.memory || {};
                    return {
                        usedJSHeapSize: memInfo.usedJSHeapSize || 0,
                        totalJSHeapSize: memInfo.totalJSHeapSize || 0
                    };
                }
            """)

            # Force GC through CDP
            await self.cdp.send("HeapProfiler.collectGarbage")

            # Wait a bit for GC to complete
            await asyncio.sleep(0.1)

            # Get memory after GC
            after_sample = await self.page.evaluate("""
                () => {
                    const memInfo = performance.memory || {};
                    return {
                        usedJSHeapSize: memInfo.usedJSHeapSize || 0,
                        totalJSHeapSize: memInfo.totalJSHeapSize || 0
                    };
                }
            """)

            before_mb = before_sample.get("usedJSHeapSize", 0) / (1024 * 1024)
            after_mb = after_sample.get("usedJSHeapSize", 0) / (1024 * 1024)
            freed_mb = before_mb - after_mb

            # Update GC stats
            self.major_gc_count += 1

            return {"before_mb": before_mb, "after_mb": after_mb, "freed_mb": freed_mb}

        except Exception as e:
            self.logger.error(f"Error forcing garbage collection: {str(e)}")
            return {}

    async def detect_memory_leaks(
        self, threshold_mb: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Detect potential memory leaks based on growth patterns."""
        if len(self.memory_samples) < 10:
            return []

        leaks = []

        try:
            # Analyze memory growth trend
            recent_samples = self.memory_samples[-10:]  # Last 10 samples
            initial_memory = recent_samples[0]["heap_used_mb"]
            final_memory = recent_samples[-1]["heap_used_mb"]
            growth_mb = final_memory - initial_memory

            if growth_mb > threshold_mb:
                leaks.append(
                    {
                        "type": "heap_growth",
                        "description": f"Heap grew by {growth_mb:.1f}MB in recent samples",
                        "severity": "high" if growth_mb > 50 else "medium",
                        "initial_mb": initial_memory,
                        "final_mb": final_memory,
                        "growth_mb": growth_mb,
                    }
                )

            # Check DOM node growth
            initial_nodes = recent_samples[0]["dom_nodes"]
            final_nodes = recent_samples[-1]["dom_nodes"]
            node_growth = final_nodes - initial_nodes

            if node_growth > 1000:
                leaks.append(
                    {
                        "type": "dom_growth",
                        "description": f"DOM nodes increased by {node_growth}",
                        "severity": "medium",
                        "initial_nodes": initial_nodes,
                        "final_nodes": final_nodes,
                        "growth": node_growth,
                    }
                )

            # Check event listener growth
            initial_listeners = recent_samples[0]["event_listeners"]
            final_listeners = recent_samples[-1]["event_listeners"]
            listener_growth = final_listeners - initial_listeners

            if listener_growth > 100:
                leaks.append(
                    {
                        "type": "listener_growth",
                        "description": f"Event listeners increased by {listener_growth}",
                        "severity": "medium",
                        "initial_listeners": initial_listeners,
                        "final_listeners": final_listeners,
                        "growth": listener_growth,
                    }
                )

        except Exception as e:
            self.logger.error(f"Error detecting memory leaks: {str(e)}")

        return leaks

    async def get_memory_timeline(self) -> List[Tuple[float, float]]:
        """Get memory usage timeline as (timestamp, memory_mb) pairs."""
        return [
            (sample["timestamp"], sample["heap_used_mb"])
            for sample in self.memory_samples
        ]

    async def get_detailed_memory_breakdown(self) -> Dict[str, Any]:
        """Get detailed memory usage breakdown."""
        try:
            # Get current memory state
            current_memory = await self.page.evaluate("""
                () => {
                    const memInfo = performance.memory || {};
                    const scripts = document.querySelectorAll('script').length;
                    const stylesheets = document.querySelectorAll('link[rel="stylesheet"], style').length;
                    const images = document.querySelectorAll('img').length;
                    const iframes = document.querySelectorAll('iframe').length;

                    // Estimate memory usage by resource type
                    return {
                        jsHeapSize: memInfo.usedJSHeapSize || 0,
                        totalHeapSize: memInfo.totalJSHeapSize || 0,
                        heapLimit: memInfo.jsHeapSizeLimit || 0,
                        domNodes: document.querySelectorAll('*').length,
                        scripts: scripts,
                        stylesheets: stylesheets,
                        images: images,
                        iframes: iframes,
                        eventListeners: window.getEventListeners ?
                            Object.keys(window.getEventListeners(document)).length : 0
                    };
                }
            """)

            return {
                "heap_usage_mb": current_memory.get("jsHeapSize", 0) / (1024 * 1024),
                "heap_total_mb": current_memory.get("totalHeapSize", 0) / (1024 * 1024),
                "heap_limit_mb": current_memory.get("heapLimit", 0) / (1024 * 1024),
                "dom_nodes": current_memory.get("domNodes", 0),
                "resource_counts": {
                    "scripts": current_memory.get("scripts", 0),
                    "stylesheets": current_memory.get("stylesheets", 0),
                    "images": current_memory.get("images", 0),
                    "iframes": current_memory.get("iframes", 0),
                },
                "event_listeners": current_memory.get("eventListeners", 0),
                "gc_stats": {
                    "major_gc_count": self.major_gc_count,
                    "minor_gc_count": self.minor_gc_count,
                    "total_gc_time_ms": self.total_gc_time_ms,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting memory breakdown: {str(e)}")
            return {}

    async def get_metrics(self) -> MemoryUsageMetrics:
        """Get comprehensive memory usage metrics."""
        try:
            # Detect potential memory leaks
            memory_leaks = await self.detect_memory_leaks()

            # Get current DOM stats
            dom_stats = await self.page.evaluate("""
                () => {
                    return {
                        domNodes: document.querySelectorAll('*').length,
                        eventListeners: window.getEventListeners ?
                            Object.keys(window.getEventListeners(document)).length : 0
                    };
                }
            """)

            return MemoryUsageMetrics(
                initial_heap_size_mb=self.initial_heap_size_mb,
                peak_heap_size_mb=self.peak_heap_size_mb,
                final_heap_size_mb=self.final_heap_size_mb,
                dom_nodes_count=dom_stats.get("domNodes", 0),
                dom_listeners_count=dom_stats.get("eventListeners", 0),
                major_gc_count=self.major_gc_count,
                minor_gc_count=self.minor_gc_count,
                total_gc_time_ms=self.total_gc_time_ms,
                memory_samples=[
                    {
                        "timestamp": sample["timestamp"],
                        "heap_used_mb": sample["heap_used_mb"],
                        "dom_nodes": sample["dom_nodes"],
                    }
                    for sample in self.memory_samples
                ],
            )

        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {str(e)}")
            return MemoryUsageMetrics()

    async def generate_memory_report(self) -> Dict[str, Any]:
        """Generate a comprehensive memory usage report."""
        try:
            metrics = await self.get_metrics()
            memory_leaks = await self.detect_memory_leaks()
            breakdown = await self.get_detailed_memory_breakdown()

            # Calculate memory statistics
            memory_values = [sample["heap_used_mb"] for sample in self.memory_samples]
            avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0

            growth_rate = 0.0
            if self.initial_heap_size_mb > 0:
                growth_rate = (
                    (self.peak_heap_size_mb - self.initial_heap_size_mb)
                    / self.initial_heap_size_mb
                ) * 100

            return {
                "summary": {
                    "initial_memory_mb": self.initial_heap_size_mb,
                    "peak_memory_mb": self.peak_heap_size_mb,
                    "final_memory_mb": self.final_heap_size_mb,
                    "average_memory_mb": avg_memory,
                    "memory_growth_rate_percent": growth_rate,
                    "efficiency_score": metrics.memory_efficiency_score,
                },
                "garbage_collection": {
                    "major_collections": self.major_gc_count,
                    "minor_collections": self.minor_gc_count,
                    "total_gc_time_ms": self.total_gc_time_ms,
                },
                "dom_statistics": {
                    "peak_dom_nodes": self.peak_dom_nodes,
                    "peak_event_listeners": self.peak_event_listeners,
                    "final_dom_nodes": breakdown.get("dom_nodes", 0),
                    "final_event_listeners": breakdown.get("event_listeners", 0),
                },
                "memory_leaks": memory_leaks,
                "resource_breakdown": breakdown.get("resource_counts", {}),
                "timeline_samples": len(self.memory_samples),
                "recommendations": self._generate_memory_recommendations(
                    metrics, memory_leaks
                ),
            }

        except Exception as e:
            self.logger.error(f"Error generating memory report: {str(e)}")
            return {}

    def _generate_memory_recommendations(
        self, metrics: MemoryUsageMetrics, memory_leaks: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate memory optimization recommendations."""
        recommendations = []

        # High memory usage
        if metrics.peak_heap_size_mb > 100:
            recommendations.append(
                {
                    "issue": "High Memory Usage",
                    "description": f"Peak memory usage was {metrics.peak_heap_size_mb:.1f}MB",
                    "suggestion": "Optimize data structures and implement lazy loading",
                    "priority": "high" if metrics.peak_heap_size_mb > 200 else "medium",
                }
            )

        # Excessive DOM nodes
        if metrics.dom_nodes_count > 5000:
            recommendations.append(
                {
                    "issue": "Large DOM Size",
                    "description": f"Page contains {metrics.dom_nodes_count} DOM nodes",
                    "suggestion": "Reduce DOM complexity and use virtual scrolling for lists",
                    "priority": "medium",
                }
            )

        # Frequent garbage collection
        if metrics.major_gc_count > 5:
            recommendations.append(
                {
                    "issue": "Frequent Garbage Collection",
                    "description": f"{metrics.major_gc_count} major GC events detected",
                    "suggestion": "Reduce object creation and reuse objects where possible",
                    "priority": "medium",
                }
            )

        # Memory leaks detected
        if memory_leaks:
            for leak in memory_leaks:
                recommendations.append(
                    {
                        "issue": f"Potential Memory Leak: {leak['type']}",
                        "description": leak["description"],
                        "suggestion": "Review code for unreleased references and event listeners",
                        "priority": leak.get("severity", "medium"),
                    }
                )

        return recommendations

    async def cleanup(self) -> None:
        """Clean up memory monitor resources."""
        try:
            await self.stop_monitoring()

            if hasattr(self, "cdp") and self.cdp:
                await self.cdp.detach()

            self.logger.debug("Memory monitor cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during memory monitor cleanup: {str(e)}")
