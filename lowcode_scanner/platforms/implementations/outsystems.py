"""OutSystems platform analyzer implementation."""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature
from ...models.performance_metrics import PerformanceTrace


class OutSystemsAnalyzer(PlatformAnalyzer):
    """Analyzer for OutSystems applications."""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "OutSystems"
        self.platform_id = "outsystems"
    
    def detect_platform(self, url: str, html_content: str = None) -> bool:
        """Detect if the application is built with OutSystems."""
        url_indicators = ['outsystems.app', 'outsystems.com', 'outsystemscloud.com']
        html_indicators = [
            'outsystems',
            'os-ui',
            'os-mobile',
            'screen_preparation',
            'client_action',
            'data_fetch'
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
        """Get OutSystems platform signature."""
        return PlatformSignature(
            platform_id=self.platform_id,
            platform_name=self.platform_name,
            confidence=0.9 if self.detect_platform(url, html_content) else 0.0,
            indicators={
                'url_patterns': ['outsystems.app', 'outsystems.com', 'outsystemscloud.com'],
                'html_patterns': ['outsystems', 'os-ui', 'screen_preparation'],
                'script_patterns': ['client_action', 'data_fetch'],
                'api_patterns': ['/rest/', '/api/', 'OutSystems']
            }
        )
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> PlatformMetrics:
        """Analyze OutSystems specific performance metrics."""
        traces = metrics.get('performance_traces', [])
        network_metrics = metrics.get('network_metrics', {})
        
        # OutSystems-specific analysis
        screen_prep_time = self._extract_screen_preparation_time(traces)
        aggregate_performance = self._analyze_aggregate_queries(network_metrics)
        client_action_time = self._analyze_client_actions(traces)
        data_fetch_efficiency = self._analyze_data_fetch(network_metrics)
        
        return PlatformMetrics(
            platform_specific_metrics={
                'screen_preparation_time_ms': screen_prep_time,
                'aggregate_query_performance': aggregate_performance,
                'client_action_execution_time_ms': client_action_time,
                'data_fetch_efficiency_score': data_fetch_efficiency,
                'outsystems_server_response_time': self._get_server_response_time(network_metrics)
            },
            performance_score=self._calculate_outsystems_score(
                screen_prep_time, aggregate_performance, client_action_time, data_fetch_efficiency
            )
        )
    
    def get_recommendations(self, metrics: PlatformMetrics) -> List[PlatformRecommendation]:
        """Get OutSystems specific performance recommendations."""
        recommendations = []
        platform_metrics = metrics.platform_specific_metrics
        
        # Screen preparation optimization
        if platform_metrics.get('screen_preparation_time_ms', 0) > 3000:
            recommendations.append(PlatformRecommendation(
                title="Optimize Screen Preparation",
                description="Reduce screen preparation time by optimizing aggregates and data loading",
                priority="high",
                impact_score=8,
                effort_score=7,
                details={
                    'current_time_ms': platform_metrics.get('screen_preparation_time_ms', 0),
                    'target_time_ms': 3000,
                    'optimization_tips': [
                        'Optimize aggregate queries',
                        'Reduce screen complexity',
                        'Implement lazy loading for non-critical data',
                        'Use efficient data sources'
                    ]
                }
            ))
        
        # Aggregate query optimization
        agg_perf = platform_metrics.get('aggregate_query_performance', {})
        if agg_perf.get('execution_time_ms', 0) > 2000:
            recommendations.append(PlatformRecommendation(
                title="Optimize Aggregate Queries",
                description="Improve aggregate query performance for better screen loading",
                priority="high",
                impact_score=7,
                effort_score=6,
                details={
                    'current_execution_time_ms': agg_perf.get('execution_time_ms', 0),
                    'target_execution_time_ms': 2000,
                    'optimization_tips': [
                        'Review aggregate logic complexity',
                        'Add proper indexing',
                        'Limit data volume in aggregates',
                        'Use SQL optimization techniques'
                    ]
                }
            ))
        
        # Client action optimization
        if platform_metrics.get('client_action_execution_time_ms', 0) > 1500:
            recommendations.append(PlatformRecommendation(
                title="Optimize Client Actions",
                description="Improve client action execution performance",
                priority="medium",
                impact_score=6,
                effort_score=5,
                details={
                    'current_time_ms': platform_metrics.get('client_action_execution_time_ms', 0),
                    'target_time_ms': 1500,
                    'optimization_tips': [
                        'Reduce client action complexity',
                        'Minimize server-side calls',
                        'Use local variables efficiently',
                        'Implement proper error handling'
                    ]
                }
            ))
        
        # Data fetch optimization
        if platform_metrics.get('data_fetch_efficiency_score', 100) < 70:
            recommendations.append(PlatformRecommendation(
                title="Implement Efficient Data Fetching",
                description="Use efficient queries and avoid unnecessary data fetching",
                priority="medium",
                impact_score=6,
                effort_score=5,
                details={
                    'current_efficiency_score': platform_metrics.get('data_fetch_efficiency_score', 100),
                    'target_efficiency_score': 70,
                    'optimization_tips': [
                        'Fetch only required data',
                        'Implement pagination',
                        'Use data caching strategies',
                        'Optimize REST API calls'
                    ]
                }
            ))
        
        return recommendations
    
    def _extract_screen_preparation_time(self, traces: List[PerformanceTrace]) -> float:
        """Extract screen preparation time from performance traces."""
        # Look for OutSystems-specific screen preparation events
        prep_time = 0
        
        for trace in traces:
            if (trace.event_type.value == 'custom' and 
                'screen' in trace.name.lower() and 'prep' in trace.name.lower()):
                prep_time += trace.duration or 0
        
        # If no specific events, estimate from load time
        if prep_time == 0:
            # Estimate from first navigation event
            for trace in traces:
                if trace.event_type.value == 'navigation':
                    prep_time = (trace.duration or 0) * 0.4  # Estimate 40% of load time
                    break
        
        return prep_time
    
    def _analyze_aggregate_queries(self, network_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze OutSystems aggregate query performance."""
        requests = network_metrics.get('requests', [])
        aggregate_requests = []
        
        for request in requests:
            url = request.get('url', '')
            if any(pattern in url for pattern in ['/rest/', '/api/']) and 'aggregate' in url.lower():
                aggregate_requests.append(request)
        
        if not aggregate_requests:
            return {'execution_time_ms': 0, 'request_count': 0, 'avg_response_time_ms': 0}
        
        total_time = sum(req.get('response_time', 0) for req in aggregate_requests)
        avg_time = total_time / len(aggregate_requests)
        
        return {
            'execution_time_ms': total_time,
            'request_count': len(aggregate_requests),
            'avg_response_time_ms': avg_time,
            'performance_score': max(0, 100 - (avg_time / 50))  # 5s = 0
        }
    
    def _analyze_client_actions(self, traces: List[PerformanceTrace]) -> float:
        """Analyze client action execution time."""
        action_time = 0
        
        for trace in traces:
            if (trace.event_type.value == 'custom' and 
                ('action' in trace.name.lower() or 'client' in trace.name.lower())):
                action_time += trace.duration or 0
        
        return action_time
    
    def _analyze_data_fetch(self, network_metrics: Dict[str, Any]) -> float:
        """Analyze data fetch efficiency."""
        requests = network_metrics.get('requests', [])
        total_requests = len(requests)
        data_requests = 0
        total_size = 0
        cache_hits = 0
        
        for request in requests:
            url = request.get('url', '')
            if any(pattern in url for pattern in ['/rest/', '/api/', '/data/']):
                data_requests += 1
                total_size += request.get('size', 0)
                if request.get('cached', False):
                    cache_hits += 1
        
        if data_requests == 0:
            return 100
        
        # Calculate efficiency score
        cache_ratio = (cache_hits / data_requests) * 100
        avg_size = total_size / data_requests / 1024  # KB
        size_penalty = min(20, avg_size / 100)  # Penalty for large responses
        request_penalty = min(20, data_requests / 5)  # Penalty for too many requests
        
        efficiency = 100 - size_penalty - request_penalty + (cache_ratio * 0.2)
        return max(0, min(100, efficiency))
    
    def _get_server_response_time(self, network_metrics: Dict[str, Any]) -> float:
        """Get average OutSystems server response time."""
        requests = network_metrics.get('requests', [])
        response_times = []
        
        for request in requests:
            url = request.get('url', '')
            if any(pattern in url for pattern in ['/rest/', '/api/', 'outsystems']):
                response_times.append(request.get('response_time', 0))
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_outsystems_score(self, screen_prep_time: float,
                                  aggregate_perf: Dict[str, Any],
                                  client_action_time: float,
                                  data_fetch_efficiency: float) -> float:
        """Calculate overall OutSystems performance score."""
        # Screen preparation score (0-100)
        screen_score = max(0, 100 - (screen_prep_time / 100))  # 10s = 0
        
        # Aggregate query score (0-100)
        agg_score = aggregate_perf.get('performance_score', 100)
        
        # Client action score (0-100)
        action_score = max(0, 100 - (client_action_time / 50))  # 5s = 0
        
        # Data fetch score (0-100)
        fetch_score = data_fetch_efficiency
        
        # Weighted average
        return (
            screen_score * 0.3 +
            agg_score * 0.25 +
            action_score * 0.25 +
            fetch_score * 0.2
        )
