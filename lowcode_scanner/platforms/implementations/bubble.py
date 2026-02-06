"""Bubble.io platform analyzer implementation."""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature
from ...models.performance_metrics import PerformanceTrace


class BubbleAnalyzer(PlatformAnalyzer):
    """Analyzer for Bubble.io applications."""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Bubble.io"
        self.platform_id = "bubble"
    
    def detect_platform(self, url: str, html_content: str = None) -> bool:
        """Detect if the application is built with Bubble.io."""
        url_indicators = ['bubbleapps.io', 'bubble.is']
        html_indicators = [
            'bubble.io',
            'bubble_page_load',
            'bubble_plugin_',
            'bubble_workflow_',
            'data-bubble'
        ]
        
        # Check URL patterns
        if any(indicator in url.lower() for indicator in url_indicators):
            return True
            
        # Check HTML content
        if html_content:
            content_lower = html_content.lower()
            if any(indicator in content_lower for indicator in html_indicators):
                return True
                
        return False
    
    def get_platform_signature(self, url: str, html_content: str = None) -> PlatformSignature:
        """Get Bubble.io platform signature."""
        return PlatformSignature(
            platform_id=self.platform_id,
            platform_name=self.platform_name,
            confidence=0.9 if self.detect_platform(url, html_content) else 0.0,
            indicators={
                'url_patterns': ['bubbleapps.io', 'bubble.is'],
                'html_patterns': ['bubble.io', 'bubble_page_load', 'bubble_plugin_'],
                'script_patterns': ['bubble_workflow_', 'data-bubble'],
                'api_patterns': ['api.bubbleapps.io']
            }
        )
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> PlatformMetrics:
        """Analyze Bubble.io specific performance metrics."""
        traces = metrics.get('performance_traces', [])
        network_metrics = metrics.get('network_metrics', {})
        
        # Bubble-specific analysis
        workflow_time = self._extract_workflow_time(traces)
        database_queries = self._count_database_queries(network_metrics)
        plugin_impact = self._analyze_plugin_impact(network_metrics)
        repeating_groups = self._analyze_repeating_groups(metrics)
        
        return PlatformMetrics(
            platform_specific_metrics={
                'workflow_execution_time_ms': workflow_time,
                'database_query_count': database_queries,
                'plugin_impact_score': plugin_impact,
                'repeating_group_performance': repeating_groups,
                'bubble_server_response_time': self._get_server_response_time(network_metrics)
            },
            performance_score=self._calculate_bubble_score(
                workflow_time, database_queries, plugin_impact, repeating_groups
            )
        )
    
    def get_recommendations(self, metrics: PlatformMetrics) -> List[PlatformRecommendation]:
        """Get Bubble.io specific performance recommendations."""
        recommendations = []
        platform_metrics = metrics.platform_specific_metrics
        
        # Workflow optimization
        if platform_metrics.get('workflow_execution_time_ms', 0) > 2000:
            recommendations.append(PlatformRecommendation(
                title="Optimize Bubble Workflows",
                description="Review and optimize workflow complexity and database queries to reduce execution time",
                priority="high",
                impact_score=8,
                effort_score=6,
                details={
                    'current_time_ms': platform_metrics.get('workflow_execution_time_ms', 0),
                    'target_time_ms': 2000,
                    'optimization_tips': [
                        'Reduce database query complexity',
                        'Use efficient search parameters',
                        'Minimize backend workflow steps'
                    ]
                }
            ))
        
        # Plugin optimization
        if platform_metrics.get('plugin_impact_score', 0) > 7:
            recommendations.append(PlatformRecommendation(
                title="Minimize Plugin Dependencies",
                description="Reduce the number of plugins to improve loading times and performance",
                priority="medium",
                impact_score=6,
                effort_score=4,
                details={
                    'current_impact_score': platform_metrics.get('plugin_impact_score', 0),
                    'target_impact_score': 5,
                    'optimization_tips': [
                        'Audit installed plugins for necessity',
                        'Combine multiple plugin functionalities',
                        'Use native Bubble features when possible'
                    ]
                }
            ))
        
        # Repeating groups optimization
        repeating_groups = platform_metrics.get('repeating_group_performance', {})
        if repeating_groups.get('render_time_ms', 0) > 1500:
            recommendations.append(PlatformRecommendation(
                title="Optimize Repeating Groups",
                description="Improve repeating group performance with pagination and efficient data loading",
                priority="high",
                impact_score=7,
                effort_score=5,
                details={
                    'current_render_time_ms': repeating_groups.get('render_time_ms', 0),
                    'target_render_time_ms': 1500,
                    'optimization_tips': [
                        'Implement pagination for large datasets',
                        'Use fixed number of rows',
                        'Optimize data source queries'
                    ]
                }
            ))
        
        return recommendations
    
    def _extract_workflow_time(self, traces: List[PerformanceTrace]) -> float:
        """Extract workflow execution time from performance traces."""
        # Look for Bubble-specific workflow events
        workflow_time = 0
        
        for trace in traces:
            if (trace.event_type.value == 'custom' and 
                'workflow' in trace.name.lower()):
                workflow_time += trace.duration or 0
        
        return workflow_time
    
    def _count_database_queries(self, network_metrics: Dict[str, Any]) -> int:
        """Count Bubble database queries from network metrics."""
        requests = network_metrics.get('requests', [])
        db_queries = 0
        
        for request in requests:
            url = request.get('url', '')
            if 'api.bubbleapps.io' in url and 'thing' in url:
                db_queries += 1
        
        return db_queries
    
    def _analyze_plugin_impact(self, network_metrics: Dict[str, Any]) -> float:
        """Analyze the impact of Bubble plugins on performance."""
        requests = network_metrics.get('requests', [])
        plugin_requests = 0
        total_size = 0
        
        for request in requests:
            url = request.get('url', '')
            if any(plugin in url for plugin in ['plugin', 'bubble_plugin']):
                plugin_requests += 1
                total_size += request.get('size', 0)
        
        # Calculate impact score based on request count and size
        request_impact = min(10, plugin_requests * 2)
        size_impact = min(10, total_size / (1024 * 1024) * 5)  # MB to impact
        
        return max(request_impact, size_impact)
    
    def _analyze_repeating_groups(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repeating group performance."""
        traces = metrics.get('performance_traces', {})
        
        # Look for repeating group rendering patterns
        render_time = 0
        element_count = 0
        
        # Estimate from DOM complexity and rendering time
        if 'rendering_time_ms' in traces:
            render_time = traces['rendering_time_ms']
            
        # Estimate element count from memory usage
        memory_metrics = metrics.get('memory_metrics', {})
        if 'dom_nodes_count' in memory_metrics:
            element_count = memory_metrics['dom_nodes_count']
        
        return {
            'render_time_ms': render_time,
            'estimated_element_count': element_count,
            'performance_score': max(0, 100 - (render_time / 50))  # 50ms per 100 elements
        }
    
    def _get_server_response_time(self, network_metrics: Dict[str, Any]) -> float:
        """Get average Bubble server response time."""
        requests = network_metrics.get('requests', [])
        response_times = []
        
        for request in requests:
            if 'api.bubbleapps.io' in request.get('url', ''):
                response_times.append(request.get('response_time', 0))
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_bubble_score(self, workflow_time: float, 
                              db_queries: int, plugin_impact: float, 
                              repeating_groups: Dict[str, Any]) -> float:
        """Calculate overall Bubble.io performance score."""
        # Workflow score (0-100)
        workflow_score = max(0, 100 - (workflow_time / 100))  # 10s = 0
        
        # Database score (0-100)
        db_score = max(0, 100 - (db_queries * 5))  # 20 queries = 0
        
        # Plugin score (0-100)
        plugin_score = max(0, 100 - (plugin_impact * 10))  # impact 10 = 0
        
        # Repeating groups score (0-100)
        rg_score = repeating_groups.get('performance_score', 100)
        
        # Weighted average
        return (
            workflow_score * 0.3 +
            db_score * 0.25 +
            plugin_score * 0.25 +
            rg_score * 0.2
        )
