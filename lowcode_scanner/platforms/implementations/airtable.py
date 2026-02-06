"""Airtable platform analyzer implementation."""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature
from ...models.performance_metrics import PerformanceTrace


class AirtableAnalyzer(PlatformAnalyzer):
    """Analyzer for Airtable applications."""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Airtable"
        self.platform_id = "airtable"
    
    def detect_platform(self, url: str, html_content: str = None) -> bool:
        """Detect if the application is built with Airtable."""
        url_indicators = ['airtable.com', 'airtable.app', 'airtable.work']
        html_indicators = [
            'airtable',
            'airtable.com',
            'data-airtable',
            'airtable-api',
            'airtable-embed'
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
        """Get Airtable platform signature."""
        return PlatformSignature(
            platform_id=self.platform_id,
            platform_name=self.platform_name,
            confidence=0.9 if self.detect_platform(url, html_content) else 0.0,
            indicators={
                'url_patterns': ['airtable.com', 'airtable.app', 'airtable.work'],
                'html_patterns': ['airtable', 'data-airtable', 'airtable-api'],
                'script_patterns': ['airtable-api', 'airtable-embed'],
                'api_patterns': ['api.airtable.com', 'airtable.com/v0']
            }
        )
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> PlatformMetrics:
        """Analyze Airtable specific performance metrics."""
        traces = metrics.get('performance_traces', [])
        network_metrics = metrics.get('network_metrics', {})
        
        # Airtable-specific analysis
        record_loading = self._analyze_record_loading(network_metrics)
        api_frequency = self._analyze_api_frequency(network_metrics)
        view_rendering = self._analyze_view_rendering(traces)
        formula_calculation = self._analyze_formula_calculation(network_metrics)
        
        return PlatformMetrics(
            platform_specific_metrics={
                'record_loading_performance': record_loading,
                'api_call_frequency': api_frequency,
                'view_rendering_time_ms': view_rendering,
                'formula_calculation_time_ms': formula_calculation,
                'airtable_api_response_time': self._get_api_response_time(network_metrics)
            },
            performance_score=self._calculate_airtable_score(
                record_loading, api_frequency, view_rendering, formula_calculation
            )
        )
    
    def get_recommendations(self, metrics: PlatformMetrics) -> List[PlatformRecommendation]:
        """Get Airtable specific performance recommendations."""
        recommendations = []
        platform_metrics = metrics.platform_specific_metrics
        
        # Record loading optimization
        record_perf = platform_metrics.get('record_loading_performance', {})
        if record_perf.get('load_time_ms', 0) > 3000:
            recommendations.append(PlatformRecommendation(
                title="Optimize Record Loading",
                description="Implement pagination and filtering to reduce initial load time",
                priority="high",
                impact_score=8,
                effort_score=6,
                details={
                    'current_load_time_ms': record_perf.get('load_time_ms', 0),
                    'target_load_time_ms': 3000,
                    'optimization_tips': [
                        'Implement pagination for large datasets',
                        'Use view filters to limit records',
                        'Optimize field selection',
                        'Use linked records efficiently'
                    ]
                }
            ))
        
        # API call optimization
        api_freq = platform_metrics.get('api_call_frequency', {})
        if api_freq.get('calls_per_second', 0) > 5:
            recommendations.append(PlatformRecommendation(
                title="Minimize API Calls",
                description="Batch API requests and implement client-side caching",
                priority="medium",
                impact_score=7,
                effort_score=5,
                details={
                    'current_calls_per_second': api_freq.get('calls_per_second', 0),
                    'target_calls_per_second': 5,
                    'optimization_tips': [
                        'Batch multiple record operations',
                        'Implement client-side caching',
                        'Use webhooks for real-time updates',
                        'Optimize polling frequency'
                    ]
                }
            ))
        
        # View rendering optimization
        if platform_metrics.get('view_rendering_time_ms', 0) > 2000:
            recommendations.append(PlatformRecommendation(
                title="Optimize View Rendering",
                description="Improve view performance by optimizing layout and calculations",
                priority="medium",
                impact_score=6,
                effort_score=5,
                details={
                    'current_render_time_ms': platform_metrics.get('view_rendering_time_ms', 0),
                    'target_render_time_ms': 2000,
                    'optimization_tips': [
                        'Simplify view layouts',
                        'Reduce complex formulas',
                        'Minimize conditional formatting',
                        'Optimize field types'
                    ]
                }
            ))
        
        # Formula calculation optimization
        if platform_metrics.get('formula_calculation_time_ms', 0) > 1500:
            recommendations.append(PlatformRecommendation(
                title="Optimize Formula Calculations",
                description="Reduce formula complexity to improve calculation performance",
                priority="medium",
                impact_score=6,
                effort_score=4,
                details={
                    'current_calculation_time_ms': platform_metrics.get('formula_calculation_time_ms', 0),
                    'target_calculation_time_ms': 1500,
                    'optimization_tips': [
                        'Simplify formula logic',
                        'Avoid nested formulas',
                        'Use lookup fields efficiently',
                        'Minimize rollup calculations'
                    ]
                }
            ))
        
        return recommendations
    
    def _analyze_record_loading(self, network_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Airtable record loading performance."""
        requests = network_metrics.get('requests', [])
        record_requests = []
        
        for request in requests:
            url = request.get('url', '')
            if 'api.airtable.com' in url and ('records' in url or 'read' in url):
                record_requests.append(request)
        
        if not record_requests:
            return {'load_time_ms': 0, 'record_count': 0, 'avg_response_time_ms': 0}
        
        total_time = sum(req.get('response_time', 0) for req in record_requests)
        total_size = sum(req.get('size', 0) for req in record_requests)
        avg_time = total_time / len(record_requests)
        
        # Estimate record count from response size (rough estimate)
        avg_record_size = 1024  # 1KB per record estimate
        estimated_records = total_size / avg_record_size
        
        return {
            'load_time_ms': total_time,
            'record_count': int(estimated_records),
            'avg_response_time_ms': avg_time,
            'performance_score': max(0, 100 - (avg_time / 100))  # 10s = 0
        }
    
    def _analyze_api_frequency(self, network_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Airtable API call frequency."""
        requests = network_metrics.get('requests', [])
        api_requests = []
        
        for request in requests:
            url = request.get('url', '')
            if 'api.airtable.com' in url:
                api_requests.append(request)
        
        if not api_requests:
            return {'calls_per_second': 0, 'total_calls': 0, 'unique_endpoints': 0}
        
        # Calculate frequency over the page load duration
        page_duration = network_metrics.get('page_load_duration_ms', 5000) / 1000  # Convert to seconds
        calls_per_second = len(api_requests) / page_duration if page_duration > 0 else 0
        
        # Count unique endpoints
        endpoints = set()
        for request in api_requests:
            url = request.get('url', '')
            # Extract endpoint (remove query parameters)
            endpoint = url.split('?')[0]
            endpoints.add(endpoint)
        
        return {
            'calls_per_second': calls_per_second,
            'total_calls': len(api_requests),
            'unique_endpoints': len(endpoints),
            'efficiency_score': max(0, 100 - (calls_per_second * 10))  # 10 calls/sec = 0
        }
    
    def _analyze_view_rendering(self, traces: List[PerformanceTrace]) -> float:
        """Analyze Airtable view rendering time."""
        # Look for Airtable-specific view rendering events
        render_time = 0
        
        for trace in traces:
            if (trace.event_type.value == 'custom' and 
                any(keyword in trace.name.lower() 
                   for keyword in ['view', 'render', 'grid', 'kanban', 'form'])):
                render_time += trace.duration or 0
        
        # If no specific events, estimate from rendering time
        if render_time == 0:
            # Estimate from first paint event
            for trace in traces:
                if trace.event_type.value == 'paint':
                    render_time = (trace.duration or 0) * 0.6  # Estimate 60% of paint time
                    break
        
        return render_time
    
    def _analyze_formula_calculation(self, network_metrics: Dict[str, Any]) -> float:
        """Analyze Airtable formula calculation time."""
        requests = network_metrics.get('requests', [])
        formula_time = 0
        
        for request in requests:
            url = request.get('url', '')
            if 'api.airtable.com' in url and any(keyword in url.lower() 
                                             for keyword in ['formula', 'calc', 'compute']):
                formula_time += request.get('response_time', 0)
        
        return formula_time
    
    def _get_api_response_time(self, network_metrics: Dict[str, Any]) -> float:
        """Get average Airtable API response time."""
        requests = network_metrics.get('requests', [])
        response_times = []
        
        for request in requests:
            url = request.get('url', '')
            if 'api.airtable.com' in url:
                response_times.append(request.get('response_time', 0))
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_airtable_score(self, record_loading: Dict[str, Any],
                                api_frequency: Dict[str, Any],
                                view_rendering: float,
                                formula_calculation: float) -> float:
        """Calculate overall Airtable performance score."""
        # Record loading score (0-100)
        record_score = record_loading.get('performance_score', 100)
        
        # API frequency score (0-100)
        api_score = api_frequency.get('efficiency_score', 100)
        
        # View rendering score (0-100)
        view_score = max(0, 100 - (view_rendering / 50))  # 5s = 0
        
        # Formula calculation score (0-100)
        formula_score = max(0, 100 - (formula_calculation / 50))  # 5s = 0
        
        # Weighted average
        return (
            record_score * 0.3 +
            api_score * 0.3 +
            view_score * 0.2 +
            formula_score * 0.2
        )
