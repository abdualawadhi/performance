"""
Critical Path Analyzer

This module provides critical path analysis for web performance, identifying
render-blocking resources, calculating critical path length, and providing
TTFB (Time to First Byte) contribution breakdowns.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from pathlib import Path


class ResourceType(Enum):
    """Types of web resources that affect critical path."""
    DOCUMENT = "document"
    CSS = "stylesheet"
    JAVASCRIPT = "script"
    FONT = "font"
    IMAGE = "image"
    PRELOAD = "preload"
    PRECONNECT = "preconnect"
    OTHER = "other"


class BlockingStatus(Enum):
    """Blocking status of a resource."""
    RENDER_BLOCKING = "render_blocking"
    PARSER_BLOCKING = "parser_blocking"
    NON_BLOCKING = "non_blocking"
    PRELOADED = "preloaded"


@dataclass
class ResourceNode:
    """A node in the resource dependency graph."""
    url: str
    resource_type: ResourceType
    size_bytes: int = 0
    
    # Timing information (milliseconds from navigation start)
    start_time_ms: float = 0.0
    end_time_ms: float = 0.0
    
    # Network timing breakdown
    dns_time_ms: float = 0.0
    tcp_time_ms: float = 0.0
    ssl_time_ms: float = 0.0
    ttfb_ms: float = 0.0
    download_time_ms: float = 0.0
    
    # Blocking status
    blocking_status: BlockingStatus = BlockingStatus.NON_BLOCKING
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # URLs this resource depends on
    required_by: List[str] = field(default_factory=list)  # URLs that depend on this resource
    
    @property
    def duration_ms(self) -> float:
        """Total duration from start to end."""
        return self.end_time_ms - self.start_time_ms
    
    @property
    def is_critical(self) -> bool:
        """Check if this resource is on the critical path."""
        return self.blocking_status in (BlockingStatus.RENDER_BLOCKING, BlockingStatus.PARSER_BLOCKING)


@dataclass
class TTFBBreakdown:
    """Breakdown of TTFB (Time to First Byte) contributions."""
    dns_lookup_ms: float = 0.0
    tcp_connection_ms: float = 0.0
    ssl_handshake_ms: float = 0.0
    server_processing_ms: float = 0.0
    network_latency_ms: float = 0.0
    
    @property
    def total_ttfb_ms(self) -> float:
        """Total TTFB."""
        return (self.dns_lookup_ms + self.tcp_connection_ms + self.ssl_handshake_ms + 
                self.server_processing_ms + self.network_latency_ms)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "dns_lookup_ms": self.dns_lookup_ms,
            "tcp_connection_ms": self.tcp_connection_ms,
            "ssl_handshake_ms": self.ssl_handshake_ms,
            "server_processing_ms": self.server_processing_ms,
            "network_latency_ms": self.network_latency_ms,
            "total_ttfb_ms": self.total_ttfb_ms
        }


@dataclass
class CriticalPathAnalysis:
    """Results of critical path analysis."""
    
    # Critical path metrics
    critical_path_length_ms: float = 0.0
    critical_path_resources: List[ResourceNode] = field(default_factory=list)
    critical_path_size_bytes: int = 0
    
    # Resource breakdown
    render_blocking_resources: List[ResourceNode] = field(default_factory=list)
    parser_blocking_resources: List[ResourceNode] = field(default_factory=list)
    
    # TTFB analysis
    ttfb_breakdown: TTFBBreakdown = field(default_factory=TTFBBreakdown)
    
    # Timing breakdown
    dns_total_ms: float = 0.0
    tcp_total_ms: float = 0.0
    ssl_total_ms: float = 0.0
    server_total_ms: float = 0.0
    download_total_ms: float = 0.0
    
    # Recommendations
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def critical_resource_count(self) -> int:
        """Count of resources on critical path."""
        return len(self.critical_path_resources)
    
    @property
    def render_blocking_count(self) -> int:
        """Count of render-blocking resources."""
        return len(self.render_blocking_resources)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            "critical_path": {
                "length_ms": self.critical_path_length_ms,
                "resource_count": self.critical_resource_count,
                "size_bytes": self.critical_path_size_bytes,
                "size_kb": round(self.critical_path_size_bytes / 1024, 2)
            },
            "blocking_resources": {
                "render_blocking_count": self.render_blocking_count,
                "parser_blocking_count": len(self.parser_blocking_resources),
                "total_blocking_count": self.render_blocking_count + len(self.parser_blocking_resources)
            },
            "ttfb_breakdown": self.ttfb_breakdown.to_dict(),
            "timing_breakdown": {
                "dns_total_ms": self.dns_total_ms,
                "tcp_total_ms": self.tcp_total_ms,
                "ssl_total_ms": self.ssl_total_ms,
                "server_total_ms": self.server_total_ms,
                "download_total_ms": self.download_total_ms
            },
            "optimization_opportunities": self.optimization_opportunities
        }


class CriticalPathAnalyzer:
    """
    Analyzer for critical rendering path and resource dependencies.
    
    This analyzer identifies:
    - Render-blocking resources (CSS, sync JS)
    - Critical path length
    - TTFB contribution breakdown
    - Resource dependency graph
    """
    
    def __init__(self):
        self.resource_graph: Dict[str, ResourceNode] = {}
        self.document_url: Optional[str] = None
    
    def add_resource(self, resource: ResourceNode):
        """Add a resource to the dependency graph."""
        self.resource_graph[resource.url] = resource
        
        # Track document URL
        if resource.resource_type == ResourceType.DOCUMENT:
            self.document_url = resource.url
    
    def build_from_network_data(self, network_data: List[Dict[str, Any]]) -> None:
        """
        Build resource graph from Chrome DevTools network data.
        
        Args:
            network_data: List of network entry dictionaries from DevTools
        """
        for entry in network_data:
            url = entry.get("name", "")
            
            # Determine resource type
            mime_type = entry.get("response", {}).get("mimeType", "")
            resource_type = self._determine_resource_type(mime_type, url)
            
            # Extract timing data
            timing = entry.get("timing", {})
            
            # Calculate timing breakdown
            dns_time = self._safe_get_timing(timing, "dnsEnd") - self._safe_get_timing(timing, "dnsStart")
            tcp_time = self._safe_get_timing(timing, "connectEnd") - self._safe_get_timing(timing, "connectStart")
            ssl_time = self._safe_get_timing(timing, "sslEnd") - self._safe_get_timing(timing, "sslStart")
            
            # TTFB calculation
            start_time = entry.get("startTime", 0)
            ttfb = entry.get("response", {}).get("timing", {}).get("receiveHeadersEnd", 0)
            
            # Determine blocking status
            blocking_status = self._determine_blocking_status(entry, resource_type)
            
            # Create resource node
            resource = ResourceNode(
                url=url,
                resource_type=resource_type,
                size_bytes=entry.get("transferSize", 0),
                start_time_ms=start_time,
                end_time_ms=entry.get("endTime", start_time),
                dns_time_ms=max(0, dns_time),
                tcp_time_ms=max(0, tcp_time),
                ssl_time_ms=max(0, ssl_time),
                ttfb_ms=ttfb,
                download_time_ms=entry.get("time", 0) - ttfb if entry.get("time", 0) > ttfb else 0,
                blocking_status=blocking_status
            )
            
            self.add_resource(resource)
        
        # Build dependencies
        self._build_dependencies()
    
    def _safe_get_timing(self, timing: Dict, key: str) -> float:
        """Safely get timing value, defaulting to 0."""
        value = timing.get(key, 0)
        return value if value and value > 0 else 0
    
    def _determine_resource_type(self, mime_type: str, url: str) -> ResourceType:
        """Determine resource type from MIME type and URL."""
        mime_lower = mime_type.lower()
        
        if "text/html" in mime_lower:
            return ResourceType.DOCUMENT
        elif "text/css" in mime_lower or url.endswith(".css"):
            return ResourceType.CSS
        elif "javascript" in mime_lower or url.endswith(".js"):
            return ResourceType.JAVASCRIPT
        elif "font" in mime_lower or any(url.endswith(ext) for ext in [".woff", ".woff2", ".ttf", ".otf"]):
            return ResourceType.FONT
        elif "image" in mime_lower:
            return ResourceType.IMAGE
        else:
            return ResourceType.OTHER
    
    def _determine_blocking_status(self, entry: Dict, resource_type: ResourceType) -> BlockingStatus:
        """Determine if a resource is render-blocking."""
        # CSS is typically render-blocking
        if resource_type == ResourceType.CSS:
            # Check for media queries that might make it non-blocking
            # For simplicity, assume CSS in head is blocking
            return BlockingStatus.RENDER_BLOCKING
        
        # JavaScript can be parser-blocking
        if resource_type == ResourceType.JAVASCRIPT:
            # Check if async or defer
            attrs = entry.get("_initiator", {}).get("stack", {}).get("callFrames", [{}])[0].get("url", "")
            # Simple heuristic: scripts in head without async/defer are blocking
            return BlockingStatus.PARSER_BLOCKING
        
        # Fonts can block rendering if used
        if resource_type == ResourceType.FONT:
            return BlockingStatus.RENDER_BLOCKING
        
        return BlockingStatus.NON_BLOCKING
    
    def _build_dependencies(self):
        """Build resource dependency graph."""
        # This is a simplified dependency analysis
        # In a real implementation, this would use the initiator chain
        
        for url, resource in self.resource_graph.items():
            if resource.resource_type == ResourceType.DOCUMENT:
                # Document depends on nothing
                continue
            
            # Simplified: resources depend on document
            if self.document_url:
                resource.depends_on.append(self.document_url)
                if self.document_url in self.resource_graph:
                    self.resource_graph[self.document_url].required_by.append(url)
    
    def analyze_critical_path(self) -> CriticalPathAnalysis:
        """
        Perform critical path analysis.
        
        Returns:
            CriticalPathAnalysis with detailed results
        """
        analysis = CriticalPathAnalysis()
        
        # Identify blocking resources
        for url, resource in self.resource_graph.items():
            if resource.blocking_status == BlockingStatus.RENDER_BLOCKING:
                analysis.render_blocking_resources.append(resource)
            elif resource.blocking_status == BlockingStatus.PARSER_BLOCKING:
                analysis.parser_blocking_resources.append(resource)
        
        # Sort by start time
        analysis.render_blocking_resources.sort(key=lambda r: r.start_time_ms)
        analysis.parser_blocking_resources.sort(key=lambda r: r.start_time_ms)
        
        # Calculate critical path (simplified: all blocking resources in order)
        all_blocking = analysis.render_blocking_resources + analysis.parser_blocking_resources
        all_blocking.sort(key=lambda r: r.start_time_ms)
        
        analysis.critical_path_resources = all_blocking
        analysis.critical_path_size_bytes = sum(r.size_bytes for r in all_blocking)
        
        # Calculate critical path length
        if all_blocking:
            analysis.critical_path_length_ms = max(r.end_time_ms for r in all_blocking)
        
        # Calculate TTFB breakdown from document
        if self.document_url and self.document_url in self.resource_graph:
            doc = self.resource_graph[self.document_url]
            analysis.ttfb_breakdown = TTFBBreakdown(
                dns_lookup_ms=doc.dns_time_ms,
                tcp_connection_ms=doc.tcp_time_ms,
                ssl_handshake_ms=doc.ssl_time_ms,
                server_processing_ms=doc.ttfb_ms - doc.dns_time_ms - doc.tcp_time_ms - doc.ssl_time_ms,
                network_latency_ms=0  # Would need more data to calculate
            )
        
        # Calculate timing totals
        for resource in self.resource_graph.values():
            analysis.dns_total_ms += resource.dns_time_ms
            analysis.tcp_total_ms += resource.tcp_time_ms
            analysis.ssl_total_ms += resource.ssl_time_ms
            analysis.download_total_ms += resource.download_time_ms
        
        # Generate optimization opportunities
        analysis.optimization_opportunities = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: CriticalPathAnalysis) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        # Check for excessive render-blocking resources
        if analysis.render_blocking_count > 5:
            recommendations.append({
                "type": "critical_css",
                "title": "Reduce Render-Blocking Resources",
                "description": f"Found {analysis.render_blocking_count} render-blocking resources. "
                              "Consider inlining critical CSS and deferring non-critical styles.",
                "impact": "High",
                "effort": "Medium"
            })
        
        # Check for large blocking resources
        large_blocking = [r for r in analysis.render_blocking_resources if r.size_bytes > 50000]
        if large_blocking:
            recommendations.append({
                "type": "resource_size",
                "title": "Optimize Large Blocking Resources",
                "description": f"Found {len(large_blocking)} blocking resources over 50KB. "
                              "Consider code splitting and lazy loading.",
                "impact": "High",
                "effort": "Medium"
            })
        
        # Check TTFB
        if analysis.ttfb_breakdown.total_ttfb_ms > 600:
            if analysis.ttfb_breakdown.server_processing_ms > 300:
                recommendations.append({
                    "type": "server_optimization",
                    "title": "Optimize Server Response Time",
                    "description": f"Server processing time is {analysis.ttfb_breakdown.server_processing_ms:.0f}ms. "
                                  "Consider server-side caching and query optimization.",
                    "impact": "High",
                    "effort": "High"
                })
        
        # Check for missing preconnect
        if analysis.ttfb_breakdown.dns_lookup_ms > 100:
            recommendations.append({
                "type": "preconnect",
                "title": "Add DNS Prefetch and Preconnect",
                "description": f"DNS lookup time is {analysis.ttfb_breakdown.dns_lookup_ms:.0f}ms. "
                              "Consider adding dns-prefetch and preconnect hints for external domains.",
                "impact": "Medium",
                "effort": "Low"
            })
        
        return recommendations
    
    def generate_dependency_graph_data(self) -> Dict[str, Any]:
        """
        Generate data for visualizing the resource dependency graph.
        
        Returns:
            Dictionary with nodes and edges for graph visualization
        """
        nodes = []
        edges = []
        
        for url, resource in self.resource_graph.items():
            nodes.append({
                "id": url,
                "type": resource.resource_type.value,
                "blocking": resource.blocking_status.value,
                "size_kb": resource.size_bytes / 1024,
                "duration_ms": resource.duration_ms,
                "start_ms": resource.start_time_ms
            })
            
            for dep_url in resource.depends_on:
                edges.append({
                    "source": dep_url,
                    "target": url,
                    "type": "dependency"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def generate_waterfall_data(self) -> List[Dict[str, Any]]:
        """
        Generate data for a waterfall chart.
        
        Returns:
            List of resource timing data
        """
        waterfall = []
        
        for url, resource in sorted(self.resource_graph.items(), key=lambda x: x[1].start_time_ms):
            waterfall.append({
                "name": url.split("/")[-1][:50] if "/" in url else url[:50],
                "url": url,
                "type": resource.resource_type.value,
                "start": resource.start_time_ms,
                "dns": resource.dns_time_ms,
                "tcp": resource.tcp_time_ms,
                "ssl": resource.ssl_time_ms,
                "ttfb": resource.ttfb_ms,
                "download": resource.download_time_ms,
                "end": resource.end_time_ms,
                "size_kb": resource.size_bytes / 1024,
                "blocking": resource.blocking_status.value
            })
        
        return waterfall


def analyze_from_scan_result(scan_result) -> CriticalPathAnalysis:
    """
    Convenience function to analyze critical path from a scan result.
    
    Args:
        scan_result: A ScanResult object containing performance data
        
    Returns:
        CriticalPathAnalysis
    """
    analyzer = CriticalPathAnalyzer()
    
    # Try to extract network data from scan result
    # This is a simplified version - real implementation would parse actual network logs
    
    # Create mock data based on scenario metrics
    scenarios = getattr(scan_result.performance_metrics, 'scenarios', {})
    
    for scenario_key, scenario in scenarios.items():
        # Add document
        doc_resource = ResourceNode(
            url=scan_result.url,
            resource_type=ResourceType.DOCUMENT,
            size_bytes=scenario.network_metrics.total_transfer_size_kb * 1024,
            start_time_ms=0,
            end_time_ms=scenario.core_web_vitals.load_event_ms,
            ttfb_ms=scenario.core_web_vitals.first_contentful_paint_ms * 0.3,
            blocking_status=BlockingStatus.PARSER_BLOCKING
        )
        analyzer.add_resource(doc_resource)
        
        # Add CSS resources (estimated)
        css_count = scenario.network_metrics.resource_breakdown.get("stylesheet", 3)
        for i in range(min(css_count, 5)):  # Cap at 5 for analysis
            css_resource = ResourceNode(
                url=f"{scan_result.url}/style{i}.css",
                resource_type=ResourceType.CSS,
                size_bytes=25000,
                start_time_ms=50 + i * 100,
                end_time_ms=200 + i * 150,
                blocking_status=BlockingStatus.RENDER_BLOCKING
            )
            analyzer.add_resource(css_resource)
        
        # Add JS resources (estimated)
        js_count = scenario.network_metrics.resource_breakdown.get("script", 8)
        for i in range(min(js_count, 10)):  # Cap at 10 for analysis
            js_resource = ResourceNode(
                url=f"{scan_result.url}/script{i}.js",
                resource_type=ResourceType.JAVASCRIPT,
                size_bytes=50000,
                start_time_ms=100 + i * 80,
                end_time_ms=300 + i * 120,
                blocking_status=BlockingStatus.PARSER_BLOCKING if i < 3 else BlockingStatus.NON_BLOCKING
            )
            analyzer.add_resource(js_resource)
    
    # Build dependencies and analyze
    analyzer._build_dependencies()
    return analyzer.analyze_critical_path()
