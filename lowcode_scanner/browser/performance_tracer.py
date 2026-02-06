"""
Performance Tracer Module for Low-Code Performance Scanner

This module provides comprehensive performance tracing during browser automation,
including timeline events, JavaScript profiling, and rendering performance tracking.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from playwright.async_api import Page

from ..models.enums import TracingEvent
from ..models.performance_metrics import PerformanceTrace


class PerformanceTracer:
    """Performance tracer for detailed browser performance analysis."""

    def __init__(self, page: Page):
        """Initialize performance tracer."""
        self.page = page
        self.logger = logging.getLogger(__name__)

        # Tracing state
        self.is_tracing = False
        self.cdp = None

        # Performance data collection
        self.timeline_events: List[Dict[str, Any]] = []
        self.performance_traces: List[PerformanceTrace] = []
        self.console_messages: List[Dict[str, Any]] = []

        # Performance marks and measures
        self.performance_marks: List[Dict[str, Any]] = []
        self.performance_measures: List[Dict[str, Any]] = []

        # Script execution tracking
        self.script_executions: List[Dict[str, Any]] = []
        self.function_calls: List[Dict[str, Any]] = []

        # Layout and paint events
        self.layout_events: List[Dict[str, Any]] = []
        self.paint_events: List[Dict[str, Any]] = []

        # Timing reference
        self.tracing_start_time: Optional[float] = None
        self.navigation_start_time: Optional[float] = None

    async def initialize(self) -> None:
        """Initialize performance tracing."""
        try:
            # Create CDP session for detailed performance monitoring
            self.cdp = await self.page.context.new_cdp_session(self.page)

            # Enable necessary domains
            await self.cdp.send("Runtime.enable")
            await self.cdp.send("Performance.enable")

            # Get browser version to determine available features
            browser_version = await self.page.evaluate("navigator.userAgent")
            self.logger.debug(f"Browser version: {browser_version}")

            # Listen to console messages for performance insights
            self.page.on("console", self._handle_console_message)

            # Set up performance metrics collection
            await self.page.add_init_script("""
            window.performanceMetrics = [];
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                for (const entry of entries) {
                    window.performanceMetrics.push({
                        name: entry.name,
                        entryType: entry.entryType,
                        startTime: entry.startTime,
                        duration: entry.duration,
                        ...(entry.toJSON ? entry.toJSON() : {})
                    });
                }
            });

            // Observe various performance entry types
            observer.observe({ entryTypes: [
                'navigation', 'resource', 'paint', 'longtask',
                'mark', 'measure', 'layout-shift', 'largest-contentful-paint',
                'first-input', 'element', 'event', 'first-paint'
            ]});
            """)

            self.logger.debug("Performance tracer initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize performance tracer: {str(e)}")
            raise

    async def start_tracing(self) -> None:
        """Start performance tracing."""
        if self.is_tracing:
            return

        self.is_tracing = True
        self.tracing_start_time = datetime.now(timezone.utc).timestamp() * 1000

        # Clear previous data
        self.timeline_events.clear()
        self.performance_traces.clear()
        self.console_messages.clear()
        self.performance_marks.clear()
        self.performance_measures.clear()
        self.script_executions.clear()
        self.function_calls.clear()
        self.layout_events.clear()
        self.paint_events.clear()

        try:
            # Clear any existing performance marks/measures
            await self.page.evaluate("""
                if (window.performance) {
                    performance.clearMarks();
                    performance.clearMeasures();
                    performance.clearResourceTimings();
                    if (window.performanceMetrics) {
                        window.performanceMetrics = [];
                    }
                }
            """)

            # Record navigation start time
            self.navigation_start_time = await self.page.evaluate(
                "performance.timing.navigationStart || Date.now()"
            )

            # Add custom performance mark for the start of tracing
            await self.page.evaluate("performance.mark('tracing_start')")

            # Start collecting performance metrics
            if self.cdp:
                await self.cdp.send("Performance.enable")

            # Inject performance monitoring code
            await self._inject_performance_monitoring()

            # Get navigation start time
            self.navigation_start_time = await self.page.evaluate(
                "() => performance.timeOrigin || performance.timing.navigationStart"
            )

            self.logger.debug("Started performance tracing")

        except Exception as e:
            self.logger.error(f"Error starting performance tracing: {str(e)}")

    async def stop_tracing(self) -> Dict[str, Any]:
        """Stop performance tracing and return collected metrics."""
        if not self.is_tracing:
            return {}

        try:
            # Add custom performance mark for the end of tracing
            await self.page.evaluate("performance.mark('tracing_end')")

            # Collect performance metrics
            metrics = await self._collect_metrics()

            # Get all performance entries
            performance_entries = await self.page.evaluate("""() => {
                if (window.performanceMetrics && window.performanceMetrics.length > 0) {
                    return window.performanceMetrics;
                }
                // Fallback to performance.getEntries() if our observer didn't capture anything
                return performance.getEntriesByType('navigation')
                    .concat(performance.getEntriesByType('resource'))
                    .concat(performance.getEntriesByType('paint'))
                    .concat(performance.getEntriesByType('mark'))
                    .concat(performance.getEntriesByType('measure'))
                    .concat(performance.getEntriesByType('longtask'))
                    .map(entry => ({
                        name: entry.name,
                        entryType: entry.entryType,
                        startTime: entry.startTime,
                        duration: entry.duration,
                        ...(entry.toJSON ? entry.toJSON() : {})
                    }));
            }""")

            # Process performance entries
            self._process_performance_entries(performance_entries)

            # Generate performance report
            report = self._generate_performance_report()
            report.update(metrics)

            # Add Web Vitals metrics
            web_vitals = await self._get_web_vitals()
            report.update(web_vitals)

            return report

        except Exception as e:
            self.logger.error(f"Error during performance tracing: {str(e)}")
            raise

        finally:
            self.is_tracing = False

    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report from collected data.

        Returns:
            Dictionary containing performance report summary
        """
        return {
            "summary": {
                "paint_events": len(self.paint_events),
                "layout_events": len(self.layout_events),
                "script_executions": len(self.script_executions),
                "performance_marks": len(self.performance_marks),
                "performance_measures": len(self.performance_measures),
                "console_messages": len(self.console_messages),
                "timeline_events": len(self.timeline_events),
                "performance_traces": len(self.performance_traces),
            },
            "timeline": {
                "total_events": len(self.timeline_events),
                "console_messages": len(self.console_messages),
            },
            "timestamp": int(time.time() * 1000),
        }

    async def _get_web_vitals(self) -> Dict[str, Any]:
        """Get Core Web Vitals metrics."""
        try:
            # Get Web Vitals using the newer web-vitals.js polyfill if available
            return await self.page.evaluate("""() => {
                try {
                    // Fallback values
                    const result = {
                        fcp: 0,
                        lcp: 0,
                        cls: 0,
                        fid: 0,
                        tbt: 0
                    };

                    // Get navigation timing
                    const navigation = performance.getEntriesByType('navigation')[0] || {};

                    // Get First Contentful Paint
                    const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0];
                    if (fcpEntry) {
                        result.fcp = fcpEntry.startTime;
                    }

                    // Get Largest Contentful Paint
                    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
                    if (lcpEntries.length > 0) {
                        const lcp = lcpEntries[lcpEntries.length - 1];
                        result.lcp = lcp.renderTime || lcp.loadTime;
                    }

                    // Calculate Cumulative Layout Shift
                    const layoutShiftEntries = performance.getEntriesByType('layout-shift') || [];
                    result.cls = layoutShiftEntries
                        .filter(entry => !entry.hadRecentInput)
                        .reduce((sum, entry) => sum + entry.value, 0);

                    // Get First Input Delay
                    const firstInputEntries = performance.getEntriesByType('first-input');
                    if (firstInputEntries.length > 0) {
                        const fid = firstInputEntries[0];
                        result.fid = fid.processingStart - fid.startTime;
                    }

                    // Calculate Total Blocking Time (approximation)
                    const longTasks = performance.getEntriesByType('longtask') || [];
                    result.tbt = longTasks
                        .filter(task => task.startTime < (result.fcp || 3000))
                        .reduce((sum, task) => sum + Math.max(task.duration - 50, 0), 0);

                    return result;
                } catch (e) {
                    console.error('Error collecting Web Vitals:', e);
                    return {};
                }
            }""")
        except Exception as e:
            self.logger.warning(f"Could not collect Web Vitals: {str(e)}")
            return {}

    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from the browser.

        Returns:
            Dictionary containing collected performance metrics
        """
        try:
            # Get performance timing metrics
            timing = await self.page.evaluate("""
                () => {
                    const timing = performance.timing || {};
                    const navEntries = performance.getEntriesByType('navigation');
                    const navigation = navEntries.length > 0 ? navEntries[0] : {};
                    const paintEntries = performance.getEntriesByType('paint') || [];

                    let fcp = 0, lcp = 0;
                    paintEntries.forEach(entry => {
                        if (entry.name === 'first-contentful-paint') fcp = entry.startTime;
                        if (entry.name === 'largest-contentful-paint') lcp = entry.startTime;
                    });

                    // Calculate load time using multiple approaches
                    let loadTime = 0;
                    
                    // For SPAs, use First Contentful Paint as the primary load time metric
                    // This is more meaningful than loadEventEnd for single-page applications
                    if (fcp > 0) {
                        loadTime = fcp;
                    }
                    // Method 2: Use Navigation Timing API v2
                    else if (navigation && navigation.loadEventEnd && navigation.fetchStart) {
                        loadTime = navigation.loadEventEnd - navigation.fetchStart;
                    }
                    // Method 3: Fallback to legacy timing API
                    else if (timing.loadEventEnd && timing.navigationStart) {
                        loadTime = timing.loadEventEnd - timing.navigationStart;
                    }
                    // Method 4: Use domComplete as fallback
                    else if (timing.domComplete && timing.navigationStart) {
                        loadTime = timing.domComplete - timing.navigationStart;
                    }

                    // Debug logging
                    console.log('Performance timing data:', {
                        navigationStart: timing.navigationStart,
                        loadEventEnd: timing.loadEventEnd,
                        domComplete: timing.domComplete,
                        loadEventStart: timing.loadEventStart,
                        navigationLoadEventEnd: navigation.loadEventEnd,
                        navigationFetchStart: navigation.fetchStart,
                        fcp: fcp,
                        calculatedLoadTime: loadTime
                    });

                    return {
                        navigationStart: timing.navigationStart || 0,
                        loadEventEnd: timing.loadEventEnd || 0,
                        domLoading: timing.domLoading || 0,
                        domInteractive: timing.domInteractive || 0,
                        domContentLoadedEventStart: timing.domContentLoadedEventStart || 0,
                        domContentLoadedEventEnd: timing.domContentLoadedEventEnd || 0,
                        domComplete: timing.domComplete || 0,
                        loadEventStart: timing.loadEventStart || 0,
                        firstPaint: timing.firstPaint || fcp,
                        firstContentfulPaint: timing.firstContentfulPaint || fcp,
                        largestContentfulPaint: lcp,
                        timeToInteractive: timing.timeToInteractive || 0,
                        domContentLoaded: (navigation.domContentLoadedEventEnd - navigation.startTime) || 0,
                        loadTime: loadTime,
                        dnsTime: (navigation.domainLookupEnd - navigation.domainLookupStart) || (timing.domainLookupEnd - timing.domainLookupStart) || 0,
                        tcpTime: (navigation.connectEnd - navigation.connectStart) || (timing.connectEnd - timing.connectStart) || 0,
                        requestTime: (navigation.responseStart - navigation.requestStart) || (timing.responseStart - timing.requestStart) || 0,
                        responseTime: (navigation.responseEnd - navigation.responseStart) || (timing.responseEnd - timing.responseStart) || 0,
                        domProcessing: (navigation.domComplete - navigation.domInteractive) || (timing.domComplete - timing.domInteractive) || 0
                    };
                }
            """)

            # Get memory usage if available
            memory = {}
            try:
                memory = await self.page.evaluate("""() => {
                    try {
                        if (window.performance && window.performance.memory) {
                            return {
                                usedJSHeapSize: window.performance.memory.usedJSHeapSize || 0,
                                totalJSHeapSize: window.performance.memory.totalJSHeapSize || 0,
                                jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit || 0
                            };
                        }
                    } catch (e) {}
                    return {
                        usedJSHeapSize: 0,
                        totalJSHeapSize: 0,
                        jsHeapSizeLimit: 0
                    };
                })""")
            except Exception as e:
                self.logger.debug(f"Could not collect memory metrics: {e}")

            # Calculate core metrics
            metrics = {
                # Timing metrics
                "load_time": timing.get("loadTime", 0),
                "dom_loading": timing.get("dom_loading", 0),
                "dom_interactive": timing.get("domInteractive", 0)
                - timing.get("navigationStart", 0),
                "dom_content_loaded": timing.get("domContentLoaded", 0),
                "dom_complete": timing.get("domComplete", 0)
                - timing.get("navigationStart", 0),
                "first_paint": timing.get("firstPaint", 0),
                "first_contentful_paint": timing.get("firstContentfulPaint", 0),
                "largest_contentful_paint": timing.get("largestContentfulPaint", 0),
                "time_to_interactive": timing.get("timeToInteractive", 0),
                "dns_time": timing.get("dnsTime", 0),
                "tcp_time": timing.get("tcpTime", 0),
                "request_time": timing.get("requestTime", 0),
                "response_time": timing.get("responseTime", 0),
                "dom_processing": timing.get("domProcessing", 0),
                # Memory metrics (in MB)
                "memory_usage_mb": round(
                    (memory.get("usedJSHeapSize", 0) / (1024 * 1024)), 2
                ),
                "total_memory_mb": round(
                    (memory.get("totalJSHeapSize", 0) / (1024 * 1024)), 2
                ),
                "memory_limit_mb": round(
                    (memory.get("jsHeapSizeLimit", 0) / (1024 * 1024)), 2
                ),
                "memory_used_percent": round(
                    (memory.get("usedJSHeapSize", 0) / memory.get("jsHeapSizeLimit", 1))
                    * 100,
                    2,
                )
                if memory.get("jsHeapSizeLimit")
                else 0,
                # Performance entries
                "paint_events": len(self.paint_events),
                "layout_shifts": len(self.layout_events),
                "script_executions": len(self.script_executions),
                "performance_marks": len(self.performance_marks),
                "performance_measures": len(self.performance_measures),
                # Timestamps
                "navigation_start": timing.get("navigationStart", 0),
                "timestamp": int(time.time() * 1000),  # Current time in ms
            }

            # Debug logging
            self.logger.debug(f"Collected timing metrics: {timing}")
            self.logger.debug(f"Calculated load_time: {metrics['load_time']}")

            # Add any additional metrics or processing here
            return metrics

        except Exception as e:
            import traceback

            self.logger.error(
                f"Error collecting performance metrics: {str(e)}\n{traceback.format_exc()}"
            )
            # Return minimal metrics in case of error
            return {
                "error": str(e),
                "load_time": 0,
                "first_contentful_paint": 0,
                "largest_contentful_paint": 0,
                "time_to_interactive": 0,
                "memory_usage_mb": 0,
                "timestamp": int(time.time() * 1000),
            }

    def _process_performance_entries(self, entries: List[Dict[str, Any]]) -> None:
        """Process performance entries and categorize them."""
        for entry in entries:
            if not entry:
                continue

            entry_type = entry.get("entryType", "")

            if entry_type == "mark":
                self.performance_marks.append(entry)
            elif entry_type == "measure":
                self.performance_measures.append(entry)
            elif entry_type == "paint":
                self.paint_events.append(entry)
            elif entry_type == "layout-shift":
                self.layout_events.append(entry)
            elif entry_type in ["resource", "navigation"]:
                self.timeline_events.append(entry)
            elif entry_type == "longtask":
                self.script_executions.append(entry)

    async def _inject_performance_monitoring(self) -> None:
        """Inject performance monitoring JavaScript into the page."""
        try:
            monitoring_script = """
                (() => {
                    // Store original console methods
                    const originalLog = console.log;
                    const originalWarn = console.warn;
                    const originalError = console.error;

                    // Performance mark wrapper
                    window.__performanceTracer = {
                        marks: [],
                        measures: [],
                        scriptExecutions: [],

                        mark: (name) => {
                            const timestamp = performance.now();
                            performance.mark(name);
                            window.__performanceTracer.marks.push({
                                name: name,
                                timestamp: timestamp,
                                time: Date.now()
                            });
                        },

                        measure: (name, startMark, endMark) => {
                            const timestamp = performance.now();
                            performance.measure(name, startMark, endMark);
                            window.__performanceTracer.measures.push({
                                name: name,
                                timestamp: timestamp,
                                time: Date.now()
                            });
                        },

                        trackScriptExecution: (scriptName, duration) => {
                            window.__performanceTracer.scriptExecutions.push({
                                name: scriptName,
                                duration: duration,
                                timestamp: performance.now(),
                                time: Date.now()
                            });
                        }
                    };

                    // Monitor script loading
                    const scriptObserver = new MutationObserver((mutations) => {
                        mutations.forEach((mutation) => {
                            mutation.addedNodes.forEach((node) => {
                                if (node.tagName === 'SCRIPT' && node.src) {
                                    const startTime = performance.now();
                                    node.addEventListener('load', () => {
                                        const loadTime = performance.now() - startTime;
                                        window.__performanceTracer.trackScriptExecution(node.src, loadTime);
                                    });
                                }
                            });
                        });
                    });

                    scriptObserver.observe(document, { childList: true, subtree: true });

                    // Monitor long tasks
                    if ('PerformanceObserver' in window) {
                        try {
                            const longTaskObserver = new PerformanceObserver((list) => {
                                for (const entry of list.getEntries()) {
                                    console.log('LongTask:', JSON.stringify({
                                        name: entry.name,
                                        duration: entry.duration,
                                        startTime: entry.startTime,
                                        attribution: entry.attribution ? entry.attribution.map(attr => ({
                                            name: attr.name,
                                            containerType: attr.containerType,
                                            containerSrc: attr.containerSrc,
                                            containerId: attr.containerId,
                                            containerName: attr.containerName
                                        })) : []
                                    }));
                                }
                            });
                            longTaskObserver.observe({ entryTypes: ['longtask'] });

                            // Monitor layout shifts
                            const clsObserver = new PerformanceObserver((list) => {
                                for (const entry of list.getEntries()) {
                                    console.log('LayoutShift:', JSON.stringify({
                                        value: entry.value,
                                        startTime: entry.startTime,
                                        hadRecentInput: entry.hadRecentInput,
                                        sources: entry.sources ? entry.sources.map(source => ({
                                            node: source.node ? source.node.tagName : 'unknown',
                                            currentRect: source.currentRect,
                                            previousRect: source.previousRect
                                        })) : []
                                    }));
                                }
                            });
                            clsObserver.observe({ entryTypes: ['layout-shift'] });

                            // Monitor paint events
                            const paintObserver = new PerformanceObserver((list) => {
                                for (const entry of list.getEntries()) {
                                    console.log('Paint:', JSON.stringify({
                                        name: entry.name,
                                        startTime: entry.startTime,
                                        duration: entry.duration
                                    }));
                                }
                            });
                            paintObserver.observe({ entryTypes: ['paint'] });

                            // Monitor navigation timing
                            const navigationObserver = new PerformanceObserver((list) => {
                                for (const entry of list.getEntries()) {
                                    console.log('Navigation:', JSON.stringify({
                                        name: entry.name,
                                        startTime: entry.startTime,
                                        duration: entry.duration,
                                        domContentLoadedEventStart: entry.domContentLoadedEventStart,
                                        domContentLoadedEventEnd: entry.domContentLoadedEventEnd,
                                        loadEventStart: entry.loadEventStart,
                                        loadEventEnd: entry.loadEventEnd
                                    }));
                                }
                            });
                            navigationObserver.observe({ entryTypes: ['navigation'] });

                        } catch (e) {
                            console.warn('Performance monitoring setup failed:', e);
                        }
                    }

                    // Mark initialization complete
                    window.__performanceTracer.mark('performance-monitoring-initialized');
                })();
            """

            await self.page.add_init_script(monitoring_script)

        except Exception as e:
            self.logger.error(f"Error injecting performance monitoring: {str(e)}")

    def _handle_console_message(self, message) -> None:
        """Handle console messages that contain performance data."""
        if not self.is_tracing:
            return

        try:
            text = message.text

            # Store all console messages
            self.console_messages.append(
                {
                    "type": message.type,
                    "text": text,
                    "timestamp": datetime.now(timezone.utc).timestamp() * 1000,
                    "url": message.location.get("url", "") if message.location else "",
                    "line": message.location.get("lineNumber", 0)
                    if message.location
                    else 0,
                }
            )

            # Parse performance-related console messages
            if text.startswith("LongTask:"):
                try:
                    task_data = json.loads(text[9:])  # Remove "LongTask:" prefix
                    self._process_long_task_event(task_data)
                except Exception as e:
                    self.logger.debug(f"Error processing script entry: {e}")
            elif text.startswith("LayoutShift:"):
                try:
                    shift_data = json.loads(text[12:])  # Remove "LayoutShift:" prefix
                    self._process_layout_shift_event(shift_data)
                except Exception as e:
                    self.logger.debug(f"Error processing layout entry: {e}")
            elif text.startswith("Paint:"):
                try:
                    paint_data = json.loads(text[6:])  # Remove "Paint:" prefix
                    self._process_paint_event(paint_data)
                except Exception as e:
                    self.logger.debug(f"Error processing paint entry: {e}")
            elif text.startswith("Navigation:"):
                try:
                    nav_data = json.loads(text[11:])  # Remove "Navigation:" prefix
                    self._process_navigation_event(nav_data)
                except Exception as e:
                    self.logger.debug(f"Error processing resource entry: {e}")

        except Exception as e:
            self.logger.debug(f"Error handling console message: {str(e)}")

    def _handle_timeline_event(self, event: Dict[str, Any]) -> None:
        """Handle Chrome DevTools timeline events."""
        if not self.is_tracing:
            return

        try:
            self.timeline_events.append(event)

        except Exception as e:
            self.logger.debug(f"Error handling timeline event: {str(e)}")

    def _process_long_task_event(self, task_data: Dict[str, Any]) -> None:
        """Process long task performance event."""
        try:
            trace = PerformanceTrace(
                event_type=TracingEvent.SCRIPT_EVALUATION,
                timestamp_ms=self.tracing_start_time + task_data.get("startTime", 0),
                duration_ms=task_data.get("duration", 0),
                name="LongTask",
                category="scripting",
                details={
                    "attribution": task_data.get("attribution", []),
                    "type": "longtask",
                },
                cpu_time_ms=task_data.get("duration", 0),
            )
            self.performance_traces.append(trace)

        except Exception as e:
            self.logger.debug(f"Error processing long task event: {str(e)}")

    def _process_layout_shift_event(self, shift_data: Dict[str, Any]) -> None:
        """Process layout shift event."""
        try:
            trace = PerformanceTrace(
                event_type=TracingEvent.LAYOUT,
                timestamp_ms=self.tracing_start_time + shift_data.get("startTime", 0),
                duration_ms=0,  # Layout shifts are instantaneous
                name="CumulativeLayoutShift",
                category="rendering",
                details={
                    "value": shift_data.get("value", 0),
                    "hadRecentInput": shift_data.get("hadRecentInput", False),
                    "sources": shift_data.get("sources", []),
                },
            )
            self.performance_traces.append(trace)

        except Exception as e:
            self.logger.debug(f"Error processing layout shift event: {str(e)}")

    def _process_paint_event(self, paint_data: Dict[str, Any]) -> None:
        """Process paint event."""
        try:
            # Determine paint event type
            paint_name = paint_data.get("name", "")
            if "first-contentful-paint" in paint_name:
                event_type = TracingEvent.FIRST_CONTENTFUL_PAINT
            elif "first-paint" in paint_name:
                event_type = TracingEvent.FIRST_PAINT
            else:
                event_type = TracingEvent.PAINT

            trace = PerformanceTrace(
                event_type=event_type,
                timestamp_ms=self.tracing_start_time + paint_data.get("startTime", 0),
                duration_ms=paint_data.get("duration", 0),
                name=paint_name,
                category="rendering",
                details={"paintType": paint_name},
            )
            self.performance_traces.append(trace)

        except Exception as e:
            self.logger.debug(f"Error processing paint event: {str(e)}")

    def _process_navigation_event(self, nav_data: Dict[str, Any]) -> None:
        """Process navigation timing event."""
        try:
            # Create traces for key navigation milestones
            milestones = [
                ("domContentLoadedEventStart", TracingEvent.DOM_CONTENT_LOADED),
                ("loadEventStart", TracingEvent.LOAD_EVENT_START),
                ("loadEventEnd", TracingEvent.LOAD_EVENT_END),
            ]

            for milestone_key, event_type in milestones:
                if milestone_key in nav_data:
                    trace = PerformanceTrace(
                        event_type=event_type,
                        timestamp_ms=self.tracing_start_time + nav_data[milestone_key],
                        duration_ms=0,
                        name=milestone_key,
                        category="navigation",
                        details={"navigationType": nav_data.get("name", "navigate")},
                    )
                    self.performance_traces.append(trace)

        except Exception as e:
            self.logger.debug(f"Error processing navigation event: {str(e)}")

    async def _collect_performance_entries(self) -> None:
        """Collect performance entries from the browser."""
        try:
            # Get performance entries
            entries = await self.page.evaluate("""
                () => {
                    const entries = performance.getEntries();
                    const marks = performance.getEntriesByType('mark');
                    const measures = performance.getEntriesByType('measure');
                    const resources = performance.getEntriesByType('resource');

                    // Get custom performance data if available
                    const customData = window.__performanceTracer || {};

                    return {
                        entries: entries.map(entry => ({
                            name: entry.name,
                            entryType: entry.entryType,
                            startTime: entry.startTime,
                            duration: entry.duration
                        })),
                        marks: marks.map(mark => ({
                            name: mark.name,
                            startTime: mark.startTime
                        })),
                        measures: measures.map(measure => ({
                            name: measure.name,
                            startTime: measure.startTime,
                            duration: measure.duration
                        })),
                        resources: resources.slice(0, 50).map(resource => ({  // Limit to first 50
                            name: resource.name,
                            startTime: resource.startTime,
                            duration: resource.duration,
                            transferSize: resource.transferSize || 0,
                            decodedBodySize: resource.decodedBodySize || 0
                        })),
                        customMarks: customData.marks || [],
                        customMeasures: customData.measures || [],
                        scriptExecutions: customData.scriptExecutions || []
                    };
                }
            """)

            # Process marks
            for mark in entries.get("marks", []):
                trace = PerformanceTrace(
                    event_type=TracingEvent.SCRIPT_EVALUATION,
                    timestamp_ms=self.tracing_start_time + mark["startTime"],
                    duration_ms=0,
                    name=mark["name"],
                    category="mark",
                    details={"type": "performance-mark"},
                )
                self.performance_traces.append(trace)

            # Process measures
            for measure in entries.get("measures", []):
                trace = PerformanceTrace(
                    event_type=TracingEvent.SCRIPT_EVALUATION,
                    timestamp_ms=self.tracing_start_time + measure["startTime"],
                    duration_ms=measure["duration"],
                    name=measure["name"],
                    category="measure",
                    details={"type": "performance-measure"},
                )
                self.performance_traces.append(trace)

            # Process script executions
            for script in entries.get("scriptExecutions", []):
                trace = PerformanceTrace(
                    event_type=TracingEvent.SCRIPT_EVALUATION,
                    timestamp_ms=script["timestamp"],
                    duration_ms=script["duration"],
                    name=script["name"],
                    category="scripting",
                    details={"type": "script-execution", "src": script["name"]},
                )
                self.performance_traces.append(trace)

        except Exception as e:
            self.logger.error(f"Error collecting performance entries: {str(e)}")

    async def _process_timeline_events(self) -> None:
        """Process Chrome DevTools timeline events."""
        try:
            for event in self.timeline_events:
                event_record = event.get("record", {})
                event_type_str = event_record.get("type", "")

                # Map Chrome event types to our tracing events
                event_mapping = {
                    "FunctionCall": TracingEvent.FUNCTION_CALL,
                    "EvaluateScript": TracingEvent.SCRIPT_EVALUATION,
                    "CompileScript": TracingEvent.SCRIPT_COMPILATION,
                    "Layout": TracingEvent.LAYOUT,
                    "UpdateLayoutTree": TracingEvent.UPDATE_LAYOUT_TREE,
                    "Paint": TracingEvent.PAINT,
                    "CompositeLayers": TracingEvent.COMPOSITE_LAYERS,
                    "RecalculateStyles": TracingEvent.RECALCULATE_STYLES,
                }

                if event_type_str in event_mapping:
                    trace = PerformanceTrace(
                        event_type=event_mapping[event_type_str],
                        timestamp_ms=event_record.get("startTime", 0),
                        duration_ms=event_record.get("endTime", 0)
                        - event_record.get("startTime", 0),
                        name=event_type_str,
                        category=event_mapping[event_type_str].category,
                        details={
                            "url": event_record.get("url", ""),
                            "lineNumber": event_record.get("lineNumber", 0),
                            "callFrame": event_record.get("callFrame", {}),
                        },
                    )
                    self.performance_traces.append(trace)

        except Exception as e:
            self.logger.error(f"Error processing timeline events: {str(e)}")

    async def get_traces(self) -> List[PerformanceTrace]:
        """Get all collected performance traces."""
        # Sort traces by timestamp
        sorted_traces = sorted(self.performance_traces, key=lambda t: t.timestamp_ms)
        return sorted_traces

    async def get_scripting_metrics(self) -> Dict[str, Any]:
        """Get scripting performance metrics."""
        try:
            scripting_traces = [
                trace
                for trace in self.performance_traces
                if trace.event_type.category == "scripting"
            ]

            total_scripting_time = sum(trace.duration_ms for trace in scripting_traces)
            script_count = len(scripting_traces)

            longest_script = max(
                scripting_traces, key=lambda t: t.duration_ms, default=None
            )

            # Analyze script sources
            script_sources = {}
            for trace in scripting_traces:
                source = trace.details.get("src", trace.name)
                if source not in script_sources:
                    script_sources[source] = {"count": 0, "total_time": 0}
                script_sources[source]["count"] += 1
                script_sources[source]["total_time"] += trace.duration_ms

            return {
                "total_scripting_time_ms": total_scripting_time,
                "script_execution_count": script_count,
                "average_script_time_ms": total_scripting_time / script_count
                if script_count > 0
                else 0,
                "longest_script": {
                    "name": longest_script.name if longest_script else None,
                    "duration_ms": longest_script.duration_ms if longest_script else 0,
                },
                "script_sources": dict(
                    sorted(
                        script_sources.items(),
                        key=lambda x: x[1]["total_time"],
                        reverse=True,
                    )[:10]
                ),  # Top 10 sources
            }

        except Exception as e:
            self.logger.error(f"Error getting scripting metrics: {str(e)}")
            return {}

    async def get_rendering_metrics(self) -> Dict[str, Any]:
        """Get rendering performance metrics."""
        try:
            rendering_traces = [
                trace
                for trace in self.performance_traces
                if trace.event_type.category == "rendering"
            ]

            layout_traces = [t for t in rendering_traces if "layout" in t.name.lower()]
            paint_traces = [t for t in rendering_traces if "paint" in t.name.lower()]

            total_rendering_time = sum(trace.duration_ms for trace in rendering_traces)
            total_layout_time = sum(trace.duration_ms for trace in layout_traces)
            total_paint_time = sum(trace.duration_ms for trace in paint_traces)

            layout_shift_traces = [
                t
                for t in rendering_traces
                if t.event_type == TracingEvent.LAYOUT and "shift" in t.name.lower()
            ]

            return {
                "total_rendering_time_ms": total_rendering_time,
                "total_layout_time_ms": total_layout_time,
                "total_paint_time_ms": total_paint_time,
                "layout_count": len(layout_traces),
                "paint_count": len(paint_traces),
                "layout_shifts_count": len(layout_shift_traces),
                "average_layout_time_ms": total_layout_time / len(layout_traces)
                if layout_traces
                else 0,
                "average_paint_time_ms": total_paint_time / len(paint_traces)
                if paint_traces
                else 0,
            }

        except Exception as e:
            self.logger.error(f"Error getting rendering metrics: {str(e)}")
            return {}

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            scripting_metrics = await self.get_scripting_metrics()
            rendering_metrics = await self.get_rendering_metrics()

            # Calculate performance breakdown
            total_time = scripting_metrics.get(
                "total_scripting_time_ms", 0
            ) + rendering_metrics.get("total_rendering_time_ms", 0)

            return {
                "total_traces": len(self.performance_traces),
                "total_performance_time_ms": total_time,
                "scripting_breakdown": scripting_metrics,
                "rendering_breakdown": rendering_metrics,
                "console_messages": len(self.console_messages),
                "timeline_events": len(self.timeline_events),
                "performance_breakdown_percentage": {
                    "scripting": (
                        scripting_metrics.get("total_scripting_time_ms", 0)
                        / total_time
                        * 100
                    )
                    if total_time > 0
                    else 0,
                    "rendering": (
                        rendering_metrics.get("total_rendering_time_ms", 0)
                        / total_time
                        * 100
                    )
                    if total_time > 0
                    else 0,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting performance summary: {str(e)}")
            return {}

    async def export_trace_data(self) -> Dict[str, Any]:
        """Export all trace data for analysis."""
        try:
            return {
                "traces": [trace.dict() for trace in self.performance_traces],
                "console_messages": self.console_messages,
                "timeline_events": self.timeline_events,
                "summary": await self.get_performance_summary(),
                "tracing_duration_ms": (
                    datetime.now(timezone.utc).timestamp() * 1000
                    - self.tracing_start_time
                )
                if self.tracing_start_time
                else 0,
            }

        except Exception as e:
            self.logger.error(f"Error exporting trace data: {str(e)}")
            return {}

    async def cleanup(self) -> None:
        """Clean up performance tracer resources."""
        try:
            await self.stop_tracing()

            # Remove event listener
            self.page.remove_listener("console", self._handle_console_message)

            if self.cdp:
                await self.cdp.detach()

            self.logger.debug("Performance tracer cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during performance tracer cleanup: {str(e)}")
