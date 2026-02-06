"""Platform Detector for Low-Code Applications

This module provides platform detection capabilities for identifying
low-code platforms like Bubble, OutSystems, and Airtable, along with
platform-specific analyzers for detailed performance insights.
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse

from ..models import LowCodePlatform
from ..platforms import PlatformRegistry, PlatformAnalyzer


@dataclass
class PlatformAnalysisResult:
    """Result of platform-specific analysis."""
    platform: LowCodePlatform
    detected_patterns: List[str] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)


class LegacyPlatformAnalyzer(ABC):
    """Base class for platform-specific analyzers (Legacy interface)."""
    
    @abstractmethod
    def analyze(self, html_content: str, network_data: List[Dict], 
                performance_metrics: Dict[str, Any]) -> PlatformAnalysisResult:
        """
        Analyze platform-specific characteristics.
        
        Args:
            html_content: HTML content of the page
            network_data: Network request/response data
            performance_metrics: Collected performance metrics
            
        Returns:
            PlatformAnalysisResult with findings
        """
        pass
    
    @abstractmethod
    def get_optimization_recommendations(self, analysis: PlatformAnalysisResult) -> List[Dict[str, Any]]:
        """Get platform-specific optimization recommendations."""
        pass


class BubbleAnalyzer(LegacyPlatformAnalyzer):
    """
    Analyzer for Bubble.io applications.
    
    Analyzes:
    - Workflow complexity
    - Plugin impact
    - Database query profiling
    - Repeating group performance
    """
    
    def analyze(self, html_content: str, network_data: List[Dict],
                performance_metrics: Dict[str, Any]) -> PlatformAnalysisResult:
        """Analyze Bubble-specific characteristics."""
        result = PlatformAnalysisResult(platform=LowCodePlatform.BUBBLE)
        
        # Detect Bubble patterns
        result.detected_patterns = self._detect_patterns(html_content, network_data)
        
        # Analyze workflow complexity
        workflow_analysis = self._analyze_workflows(html_content, network_data)
        result.metrics['workflow_count'] = workflow_analysis.get('count', 0)
        result.metrics['avg_workflow_complexity'] = workflow_analysis.get('avg_complexity', 0)
        
        # Analyze plugin impact
        plugin_analysis = self._analyze_plugins(network_data)
        result.metrics['plugin_count'] = plugin_analysis.get('count', 0)
        result.metrics['plugin_load_time_ms'] = plugin_analysis.get('load_time_ms', 0)
        
        # Analyze database queries
        db_analysis = self._analyze_database_queries(network_data)
        result.metrics['db_query_count'] = db_analysis.get('query_count', 0)
        result.metrics['avg_query_time_ms'] = db_analysis.get('avg_time_ms', 0)
        result.metrics['slow_query_count'] = db_analysis.get('slow_queries', 0)
        
        # Analyze repeating groups
        rg_analysis = self._analyze_repeating_groups(html_content, network_data)
        result.metrics['repeating_group_count'] = rg_analysis.get('count', 0)
        result.metrics['heavy_rg_count'] = rg_analysis.get('heavy_count', 0)
        
        # Identify issues
        if result.metrics['slow_query_count'] > 5:
            result.issues.append({
                'type': 'slow_queries',
                'severity': 'high',
                'description': f"{result.metrics['slow_query_count']} slow database queries detected",
                'recommendation': 'Consider adding database indexes and optimizing search constraints'
            })
        
        if result.metrics['plugin_load_time_ms'] > 1000:
            result.issues.append({
                'type': 'heavy_plugins',
                'severity': 'medium',
                'description': f"Plugins taking {result.metrics['plugin_load_time_ms']:.0f}ms to load",
                'recommendation': 'Review plugin usage and remove unnecessary plugins'
            })
        
        if result.metrics['heavy_rg_count'] > 3:
            result.issues.append({
                'type': 'heavy_repeating_groups',
                'severity': 'high',
                'description': f"{result.metrics['heavy_rg_count']} heavy repeating groups detected",
                'recommendation': 'Implement pagination and limit items per page'
            })
        
        # Generate recommendations
        result.recommendations = self.get_optimization_recommendations(result)
        
        return result
    
    def _detect_patterns(self, html_content: str, network_data: List[Dict]) -> List[str]:
        """Detect Bubble-specific patterns."""
        patterns = []
        
        # Check HTML for Bubble indicators
        bubble_patterns = [
            (r'data-bubble', 'data-bubble attributes'),
            (r'class="[^"]*bubble', 'Bubble CSS classes'),
            (r'bubble_[a-z_]+', 'Bubble element IDs'),
            (r'RepeatingGroup', 'Repeating Group elements'),
        ]
        
        for pattern, description in bubble_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                patterns.append(description)
        
        # Check network requests
        for req in network_data:
            url = req.get('name', '')
            if 'bubble.io' in url or 'bubbleapps.io' in url:
                patterns.append('Bubble API endpoints')
                break
        
        return patterns
    
    def _analyze_workflows(self, html_content: str, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze workflow complexity."""
        # Count workflow-related patterns
        workflow_count = len(re.findall(r'workflow|action|event', html_content, re.IGNORECASE))
        
        # Estimate complexity based on patterns
        complexity_indicators = [
            len(re.findall(r'condition|when', html_content, re.IGNORECASE)),
            len(re.findall(r'loop|forEach|filter', html_content, re.IGNORECASE)),
            len(re.findall(r'schedule|delay', html_content, re.IGNORECASE))
        ]
        
        avg_complexity = sum(complexity_indicators) / max(len(complexity_indicators), 1)
        
        return {
            'count': min(workflow_count, 100),  # Cap at reasonable number
            'avg_complexity': avg_complexity
        }
    
    def _analyze_plugins(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze plugin impact."""
        plugin_requests = [req for req in network_data 
                          if 'plugin' in req.get('name', '').lower()]
        
        total_time = sum(req.get('time', 0) for req in plugin_requests)
        
        return {
            'count': len(plugin_requests),
            'load_time_ms': total_time
        }
    
    def _analyze_database_queries(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze database query performance."""
        # Look for database API calls
        db_requests = [req for req in network_data 
                      if any(x in req.get('name', '').lower() 
                            for x in ['api/1.1/obj', 'db', 'query', 'search'])]
        
        query_times = [req.get('time', 0) for req in db_requests]
        slow_queries = sum(1 for t in query_times if t > 500)
        
        return {
            'query_count': len(db_requests),
            'avg_time_ms': sum(query_times) / len(query_times) if query_times else 0,
            'slow_queries': slow_queries
        }
    
    def _analyze_repeating_groups(self, html_content: str, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze repeating group performance."""
        rg_count = len(re.findall(r'RepeatingGroup', html_content))
        
        # Estimate heavy groups based on data patterns
        heavy_indicators = len(re.findall(r'items\s*:\s*\d{3,}', html_content))
        
        return {
            'count': rg_count,
            'heavy_count': heavy_indicators
        }
    
    def get_optimization_recommendations(self, analysis: PlatformAnalysisResult) -> List[Dict[str, Any]]:
        """Get Bubble-specific optimization recommendations."""
        recommendations = []
        
        if analysis.metrics.get('slow_query_count', 0) > 3:
            recommendations.append({
                'category': 'Database',
                'title': 'Optimize Database Queries',
                'description': f"{analysis.metrics['slow_query_count']} slow queries detected. Add indexes and optimize constraints.",
                'priority': 'High',
                'effort': 'Medium'
            })
        
        if analysis.metrics.get('plugin_load_time_ms', 0) > 500:
            recommendations.append({
                'category': 'Plugins',
                'title': 'Review Plugin Usage',
                'description': 'Plugins are contributing significantly to load time. Remove unused plugins.',
                'priority': 'Medium',
                'effort': 'Low'
            })
        
        if analysis.metrics.get('heavy_rg_count', 0) > 0:
            recommendations.append({
                'category': 'UI',
                'title': 'Implement Pagination',
                'description': 'Use pagination in repeating groups to improve rendering performance.',
                'priority': 'High',
                'effort': 'Low'
            })
        
        if analysis.metrics.get('avg_workflow_complexity', 0) > 10:
            recommendations.append({
                'category': 'Workflows',
                'title': 'Simplify Complex Workflows',
                'description': 'Break complex workflows into smaller, manageable actions.',
                'priority': 'Medium',
                'effort': 'High'
            })
        
        return recommendations


class OutSystemsAnalyzer(LegacyPlatformAnalyzer):
    """
    Analyzer for OutSystems applications.
    
    Analyzes:
    - Aggregate efficiency
    - Screen preparation breakdown
    - Client/server action balance
    """
    
    def analyze(self, html_content: str, network_data: List[Dict],
                performance_metrics: Dict[str, Any]) -> PlatformAnalysisResult:
        """Analyze OutSystems-specific characteristics."""
        result = PlatformAnalysisResult(platform=LowCodePlatform.OUTSYSTEMS)
        
        # Detect OutSystems patterns
        result.detected_patterns = self._detect_patterns(html_content, network_data)
        
        # Analyze aggregates
        aggregate_analysis = self._analyze_aggregates(network_data)
        result.metrics['aggregate_count'] = aggregate_analysis.get('count', 0)
        result.metrics['avg_aggregate_time_ms'] = aggregate_analysis.get('avg_time_ms', 0)
        result.metrics['slow_aggregate_count'] = aggregate_analysis.get('slow_count', 0)
        
        # Analyze screen preparation
        prep_analysis = self._analyze_screen_preparation(network_data)
        result.metrics['screen_prep_time_ms'] = prep_analysis.get('time_ms', 0)
        result.metrics['prep_steps'] = prep_analysis.get('steps', 0)
        
        # Analyze client vs server actions
        action_analysis = self._analyze_actions(network_data)
        result.metrics['client_actions'] = action_analysis.get('client_count', 0)
        result.metrics['server_actions'] = action_analysis.get('server_count', 0)
        result.metrics['client_server_ratio'] = action_analysis.get('ratio', 0)
        
        # Identify issues
        if result.metrics['slow_aggregate_count'] > 2:
            result.issues.append({
                'type': 'slow_aggregates',
                'severity': 'high',
                'description': f"{result.metrics['slow_aggregate_count']} slow aggregates detected",
                'recommendation': 'Add indexes, filter early, and reduce data fetched'
            })
        
        if result.metrics['screen_prep_time_ms'] > 1000:
            result.issues.append({
                'type': 'slow_screen_prep',
                'severity': 'medium',
                'description': f"Screen preparation takes {result.metrics['screen_prep_time_ms']:.0f}ms",
                'recommendation': 'Optimize preparation logic and cache data'
            })
        
        if result.metrics.get('client_server_ratio', 0) < 0.3:
            result.issues.append({
                'type': 'server_heavy',
                'severity': 'medium',
                'description': 'Application is server-heavy, consider client-side logic',
                'recommendation': 'Move appropriate logic to client actions'
            })
        
        # Generate recommendations
        result.recommendations = self.get_optimization_recommendations(result)
        
        return result
    
    def _detect_patterns(self, html_content: str, network_data: List[Dict]) -> List[str]:
        """Detect OutSystems-specific patterns."""
        patterns = []
        
        os_patterns = [
            (r'OutSystems', 'OutSystems references'),
            (r'osjs-OS', 'OutSystems JavaScript'),
            (r'_osPerformAjax', 'OutSystems AJAX calls'),
            (r'aggregate|Aggregate', 'Aggregate operations'),
        ]
        
        for pattern, description in os_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                patterns.append(description)
        
        return patterns
    
    def _analyze_aggregates(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze aggregate efficiency."""
        aggregate_requests = [req for req in network_data 
                             if 'aggregate' in req.get('name', '').lower()]
        
        times = [req.get('time', 0) for req in aggregate_requests]
        slow_count = sum(1 for t in times if t > 500)
        
        return {
            'count': len(aggregate_requests),
            'avg_time_ms': sum(times) / len(times) if times else 0,
            'slow_count': slow_count
        }
    
    def _analyze_screen_preparation(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze screen preparation performance."""
        prep_requests = [req for req in network_data 
                        if any(x in req.get('name', '').lower() 
                              for x in ['screen', 'preparation', 'init'])]
        
        total_time = sum(req.get('time', 0) for req in prep_requests)
        
        return {
            'time_ms': total_time,
            'steps': len(prep_requests)
        }
    
    def _analyze_actions(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze client vs server actions."""
        client_actions = len([req for req in network_data 
                             if 'client' in req.get('name', '').lower()])
        server_actions = len([req for req in network_data 
                             if 'server' in req.get('name', '').lower()])
        
        total = client_actions + server_actions
        ratio = client_actions / total if total > 0 else 0
        
        return {
            'client_count': client_actions,
            'server_count': server_actions,
            'ratio': ratio
        }
    
    def get_optimization_recommendations(self, analysis: PlatformAnalysisResult) -> List[Dict[str, Any]]:
        """Get OutSystems-specific optimization recommendations."""
        recommendations = []
        
        if analysis.metrics.get('slow_aggregate_count', 0) > 0:
            recommendations.append({
                'category': 'Aggregates',
                'title': 'Optimize Slow Aggregates',
                'description': 'Add database indexes and filter data at the query level.',
                'priority': 'High',
                'effort': 'Medium'
            })
        
        if analysis.metrics.get('screen_prep_time_ms', 0) > 500:
            recommendations.append({
                'category': 'Screen',
                'title': 'Optimize Screen Preparation',
                'description': 'Move non-critical logic to After Fetch or On Ready.',
                'priority': 'Medium',
                'effort': 'Low'
            })
        
        if analysis.metrics.get('client_server_ratio', 0) < 0.5:
            recommendations.append({
                'category': 'Architecture',
                'title': 'Balance Client/Server Logic',
                'description': 'Move validation and UI logic to client actions.',
                'priority': 'Medium',
                'effort': 'Medium'
            })
        
        return recommendations


class AirtableAnalyzer(LegacyPlatformAnalyzer):
    """
    Analyzer for Airtable applications.
    
    Analyzes:
    - API call efficiency
    - View rendering optimization
    - Record loading patterns
    """
    
    def analyze(self, html_content: str, network_data: List[Dict],
                performance_metrics: Dict[str, Any]) -> PlatformAnalysisResult:
        """Analyze Airtable-specific characteristics."""
        result = PlatformAnalysisResult(platform=LowCodePlatform.AIRTABLE)
        
        # Detect Airtable patterns
        result.detected_patterns = self._detect_patterns(html_content, network_data)
        
        # Analyze API calls
        api_analysis = self._analyze_api_calls(network_data)
        result.metrics['api_call_count'] = api_analysis.get('count', 0)
        result.metrics['avg_api_time_ms'] = api_analysis.get('avg_time_ms', 0)
        result.metrics['batch_efficiency'] = api_analysis.get('batch_efficiency', 0)
        
        # Analyze record loading
        record_analysis = self._analyze_record_loading(network_data)
        result.metrics['records_loaded'] = record_analysis.get('count', 0)
        result.metrics['records_per_request'] = record_analysis.get('per_request', 0)
        result.metrics['large_view_count'] = record_analysis.get('large_views', 0)
        
        # Analyze view rendering
        view_analysis = self._analyze_view_rendering(network_data)
        result.metrics['view_count'] = view_analysis.get('count', 0)
        result.metrics['avg_render_time_ms'] = view_analysis.get('avg_time_ms', 0)
        
        # Identify issues
        if result.metrics['api_call_count'] > 20:
            result.issues.append({
                'type': 'excessive_api_calls',
                'severity': 'medium',
                'description': f"{result.metrics['api_call_count']} API calls detected",
                'recommendation': 'Batch requests and implement client-side caching'
            })
        
        if result.metrics.get('records_per_request', 0) < 50:
            result.issues.append({
                'type': 'inefficient_pagination',
                'severity': 'low',
                'description': 'API pagination may be inefficient',
                'recommendation': 'Increase page size for bulk operations'
            })
        
        if result.metrics.get('large_view_count', 0) > 0:
            result.issues.append({
                'type': 'large_views',
                'severity': 'medium',
                'description': f"{result.metrics['large_view_count']} views with large datasets",
                'recommendation': 'Implement filtering and pagination in views'
            })
        
        # Generate recommendations
        result.recommendations = self.get_optimization_recommendations(result)
        
        return result
    
    def _detect_patterns(self, html_content: str, network_data: List[Dict]) -> List[str]:
        """Detect Airtable-specific patterns."""
        patterns = []
        
        at_patterns = [
            (r'airtable', 'Airtable references'),
            (r'api\.airtable\.com', 'Airtable API calls'),
            (r'viewGrid|viewGallery', 'Airtable view types'),
        ]
        
        for pattern, description in at_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                patterns.append(description)
        
        return patterns
    
    def _analyze_api_calls(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze API call efficiency."""
        api_requests = [req for req in network_data 
                       if 'airtable' in req.get('name', '').lower()]
        
        times = [req.get('time', 0) for req in api_requests]
        
        # Check for batch requests
        batch_requests = [req for req in api_requests 
                         if 'batch' in req.get('name', '').lower()]
        
        efficiency = len(batch_requests) / len(api_requests) if api_requests else 0
        
        return {
            'count': len(api_requests),
            'avg_time_ms': sum(times) / len(times) if times else 0,
            'batch_efficiency': efficiency
        }
    
    def _analyze_record_loading(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze record loading patterns."""
        record_requests = [req for req in network_data 
                          if 'record' in req.get('name', '').lower()]
        
        # Estimate records from response sizes (rough approximation)
        total_records = sum(req.get('response', {}).get('bodySize', 0) // 500 
                           for req in record_requests)
        
        per_request = total_records / len(record_requests) if record_requests else 0
        
        # Count large views (>1000 records)
        large_views = sum(1 for req in record_requests 
                         if req.get('response', {}).get('bodySize', 0) > 500000)
        
        return {
            'count': total_records,
            'per_request': per_request,
            'large_views': large_views
        }
    
    def _analyze_view_rendering(self, network_data: List[Dict]) -> Dict[str, Any]:
        """Analyze view rendering performance."""
        view_requests = [req for req in network_data 
                        if 'view' in req.get('name', '').lower()]
        
        times = [req.get('time', 0) for req in view_requests]
        
        return {
            'count': len(view_requests),
            'avg_time_ms': sum(times) / len(times) if times else 0
        }
    
    def get_optimization_recommendations(self, analysis: PlatformAnalysisResult) -> List[Dict[str, Any]]:
        """Get Airtable-specific optimization recommendations."""
        recommendations = []
        
        if analysis.metrics.get('api_call_count', 0) > 15:
            recommendations.append({
                'category': 'API',
                'title': 'Batch API Requests',
                'description': 'Combine multiple operations into batch requests.',
                'priority': 'High',
                'effort': 'Medium'
            })
        
        if analysis.metrics.get('large_view_count', 0) > 0:
            recommendations.append({
                'category': 'Views',
                'title': 'Implement View Filtering',
                'description': 'Add filters to limit records loaded in views.',
                'priority': 'Medium',
                'effort': 'Low'
            })
        
        if analysis.metrics.get('batch_efficiency', 0) < 0.3:
            recommendations.append({
                'category': 'API',
                'title': 'Use Batch Operations',
                'description': 'Replace individual API calls with batch operations.',
                'priority': 'Medium',
                'effort': 'Low'
            })
        
        return recommendations


class PlatformDetector:
    """Detects low-code platforms from URLs and page characteristics."""

    def __init__(self):
        """Initialize the platform detector."""
        self.logger = logging.getLogger(__name__)
        self._analyzers: Dict[LowCodePlatform, LegacyPlatformAnalyzer] = {
            LowCodePlatform.BUBBLE: BubbleAnalyzer(),
            LowCodePlatform.OUTSYSTEMS: OutSystemsAnalyzer(),
            LowCodePlatform.AIRTABLE: AirtableAnalyzer(),
        }

    async def detect_platform_async(self, url: str) -> LowCodePlatform:
        """
        Detect the low-code platform from a URL asynchronously.
        Also integrates with the new PlatformRegistry for extended platform support.

        Args:
            url: The URL to analyze

        Returns:
            Detected low-code platform
        """
        # First try the legacy detection
        try:
            platform = LowCodePlatform.detect_platform(url)
            if platform != LowCodePlatform.GENERIC:
                return platform
        except Exception as e:
            self.logger.error(f"Error in legacy platform detection: {str(e)}")
        
        # Fall back to new registry detection
        try:
            platform_def = PlatformRegistry.detect_platform(url)
            # Map new registry platforms to existing enum for backward compatibility
            platform_map = {
                'shopify': LowCodePlatform.GENERIC,
                'webflow': LowCodePlatform.GENERIC,
                'mendix': LowCodePlatform.MENDIX,
                'wix': LowCodePlatform.GENERIC,
            }
            mapped = platform_map.get(platform_def.id)
            if mapped:
                return mapped
        except Exception as e:
            self.logger.error(f"Error in registry platform detection: {str(e)}")
        
        return LowCodePlatform.GENERIC

    def detect_platform(self, url: str) -> LowCodePlatform:
        """
        Detect the low-code platform from a URL.

        Args:
            url: The URL to analyze

        Returns:
            Detected low-code platform
        """
        try:
            return LowCodePlatform.detect_platform(url)
        except Exception as e:
            self.logger.error(f"Error detecting platform: {str(e)}")
            return LowCodePlatform.GENERIC
    
    def get_analyzer(self, platform: LowCodePlatform) -> Optional[LegacyPlatformAnalyzer]:
        """
        Get the appropriate analyzer for a platform.
        
        Args:
            platform: The platform to get analyzer for
            
        Returns:
            LegacyPlatformAnalyzer instance or None
        """
        return self._analyzers.get(platform)
    
    def get_platform_analyzer(self, url: str) -> PlatformAnalyzer:
        """
        Get the new platform-specific analyzer for a URL.
        This uses the new registry system for extensible platform support.
        
        Args:
            url: The URL to analyze
            
        Returns:
            PlatformAnalyzer instance from the new registry system
        """
        return PlatformRegistry.get_analyzer(url)
    
    def analyze_platform(self, platform: LowCodePlatform, html_content: str,
                        network_data: List[Dict], 
                        performance_metrics: Dict[str, Any]) -> Optional[PlatformAnalysisResult]:
        """
        Perform platform-specific analysis.
        
        Args:
            platform: The detected platform
            html_content: HTML content of the page
            network_data: Network request/response data
            performance_metrics: Performance metrics
            
        Returns:
            PlatformAnalysisResult or None if no analyzer available
        """
        analyzer = self.get_analyzer(platform)
        if analyzer:
            return analyzer.analyze(html_content, network_data, performance_metrics)
        return None

    def get_platform_characteristics(self, platform: LowCodePlatform) -> dict:
        """
        Get characteristics for a specific platform.

        Args:
            platform: The low-code platform

        Returns:
            Dictionary of platform characteristics
        """
        characteristics = {
            LowCodePlatform.BUBBLE: {
                "name": "Bubble.io",
                "typical_indicators": ["bubbleapps.io", "bubble.io"],
                "optimization_focus": ["workflows", "database_queries", "plugins"],
                "common_issues": ["heavy_repeating_groups", "plugin_overload"],
                "analysis_features": ["workflow_complexity", "plugin_impact", "db_query_profiling"],
            },
            LowCodePlatform.OUTSYSTEMS: {
                "name": "OutSystems",
                "typical_indicators": ["outsystems.app", "outsystems.com"],
                "optimization_focus": [
                    "screen_preparation",
                    "aggregates",
                    "client_actions",
                ],
                "common_issues": ["slow_aggregates", "screen_complexity"],
                "analysis_features": ["aggregate_efficiency", "screen_preparation_breakdown"],
            },
            LowCodePlatform.AIRTABLE: {
                "name": "Airtable",
                "typical_indicators": ["airtable.com"],
                "optimization_focus": ["record_loading", "api_calls", "views"],
                "common_issues": ["large_record_sets", "api_rate_limits"],
                "analysis_features": ["api_call_efficiency", "view_rendering_optimization"],
            },
        }

        return characteristics.get(
            platform,
            {
                "name": "Generic",
                "typical_indicators": [],
                "optimization_focus": ["general_performance"],
                "common_issues": [],
                "analysis_features": [],
            },
        )
