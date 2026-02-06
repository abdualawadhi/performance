"""Mendix platform analyzer.

Mendix is an enterprise low-code platform using microflows and nanoflows.
Key performance factors:
- Microflow execution time (server-side)
- Nanoflow execution time (client-side)
- Entity retrieval patterns
- Client-server communication
"""

import re
from typing import Dict, List, Any
from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature


class MendixAnalyzer(PlatformAnalyzer):
    """Analyzer for Mendix applications."""
    
    MICROFLOW_THRESHOLD_MS = 500
    NANO_THRESHOLD_MS = 100
    N_PLUS_ONE_THRESHOLD = 3  # Sequential retrieves suggesting N+1
    
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Detect Mendix platform signatures."""
        signatures = {
            'mendix_client': 'mxui' in page_content or 'mendix' in page_content.lower(),
            'mendix_bundle': 'mxclientsystem' in page_content,
            'mendix_data': 'mx.data' in page_content,
            'mendix_object': 'mendix.lib.MxObject' in page_content,
            'mendix_cloud': 'mendixcloud.com' in headers.get('host', ''),
        }
        
        detected = [k for k, v in signatures.items() if v]
        confidence = len(detected) / len(signatures)
        
        # Extract Mendix version
        version_match = re.search(r'mxui\s*[=:]\s*["\']([\d.]+)["\']', page_content)
        
        return PlatformSignature(
            platform_id='mendix',
            detected_version=version_match.group(1) if version_match else None,
            detected_features=detected,
            confidence_score=confidence,
            detection_method='javascript_detection'
        )
    
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Calculate Mendix client framework overhead."""
        overhead = 0.0
        
        # Mendix client bundle
        mendix_bundles = [e for e in performance_entries 
                         if 'mxclientsystem' in e.get('name', '').lower()]
        for bundle in mendix_bundles:
            overhead += bundle.get('duration', 0)
        
        # Widget loading
        widget_loads = [e for e in performance_entries
                       if 'widget' in e.get('name', '').lower()]
        for widget in widget_loads:
            overhead += widget.get('duration', 0) * 0.7  # 70% platform overhead
        
        return overhead
    
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Identify Mendix-specific bottlenecks."""
        bottlenecks = []
        
        # Microflow performance
        microflow_calls = [t for t in traces if 'microflow' in str(t).lower()]
        if microflow_calls:
            avg_time = sum(m.get('duration', 0) for m in microflow_calls) / len(microflow_calls)
            if avg_time > self.MICROFLOW_THRESHOLD_MS:
                bottlenecks.append({
                    'bottleneck_type': 'microflow_performance',
                    'severity': min(10, int(avg_time / 100)),
                    'location': 'server_side_logic',
                    'evidence': f'Avg microflow: {avg_time:.0f}ms',
                    'recommendation': 'Optimize microflow logic, reduce database calls, use caching'
                })
        
        # Nanoflow performance (client-side)
        nanoflow_calls = [t for t in traces if 'nanoflow' in str(t).lower()]
        if nanoflow_calls:
            avg_nano = sum(n.get('duration', 0) for n in nanoflow_calls) / len(nanoflow_calls)
            if avg_nano > self.NANO_THRESHOLD_MS:
                bottlenecks.append({
                    'bottleneck_type': 'nanoflow_performance',
                    'severity': min(10, int(avg_nano / 20)),
                    'location': 'client_side_logic',
                    'evidence': f'Avg nanoflow: {avg_nano:.0f}ms',
                    'recommendation': 'Move logic to microflows, optimize expressions'
                })
        
        # N+1 query pattern
        sequential_retrieves = self._detect_n_plus_one(traces)
        if sequential_retrieves > self.N_PLUS_ONE_THRESHOLD:
            bottlenecks.append({
                'bottleneck_type': 'n_plus_one_queries',
                'severity': min(10, sequential_retrieves * 2),
                'location': 'database_access',
                'evidence': f'{sequential_retrieves} sequential retrieves detected',
                'recommendation': 'Use associations instead of retrieves, implement batch fetching'
            })
        
        # Large page loads
        large_pages = [t for t in traces 
                      if t.get('transferSize', 0) > 500000]  # 500KB
        if len(large_pages) > 3:
            bottlenecks.append({
                'bottleneck_type': 'large_page_payload',
                'severity': min(10, len(large_pages)),
                'location': 'page_initialization',
                'evidence': f'{len(large_pages)} large resources',
                'recommendation': 'Implement lazy loading, pagination, optimize data views'
            })
        
        return bottlenecks
    
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Analyze custom JavaScript impact in Mendix."""
        mendix_patterns = ['mxui', 'mxclientsystem', 'mendix']
        
        platform_time = 0.0
        custom_time = 0.0
        
        for script in scripts:
            duration = script.get('duration', 0)
            name = script.get('name', '')
            
            if any(p in name.lower() for p in mendix_patterns):
                platform_time += duration
            else:
                custom_time += duration
        
        return {
            'platform_code_ms': platform_time,
            'custom_code_ms': custom_time,
            'platform_ratio': platform_time / (platform_time + custom_time + 1),
            'custom_ratio': custom_time / (platform_time + custom_time + 1),
        }
    
    def generate_platform_recommendations(self) -> List[PlatformRecommendation]:
        """Generate Mendix-specific recommendations."""
        recommendations = []
        
        recommendations.append(PlatformRecommendation(
            category='Database Optimization',
            title='Eliminate N+1 Query Patterns',
            description='Sequential database retrieves in loops severely impact performance.',
            priority='critical',
            effort='high',
            impact_score=40.0,
            confidence=0.95,
            implementation_steps=[
                'Replace loop retrieves with association retrieves',
                'Use batch retrieve activities',
                'Implement data source microflows with joins',
                'Add database indexes for foreign keys'
            ],
            academic_rationale='N+1 query pattern is O(n) database calls vs O(1) with joins',
            references=['Database Performance Anti-Patterns', 'Mendix Best Practices']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='Logic Optimization',
            title='Optimize Microflow Architecture',
            description='Complex microflows with many activities increase execution time.',
            priority='high',
            effort='medium',
            impact_score=30.0,
            confidence=0.85,
            implementation_steps=[
                'Split complex microflows into sub-microflows',
                'Minimize database commits',
                'Use caching for reference data',
                'Optimize XPath constraints'
            ],
            academic_rationale='Microflow execution time directly impacts user-perceived latency',
            references=['Mendix Performance Guide']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='Client Performance',
            title='Reduce Nanoflow Complexity',
            description='Heavy client-side processing blocks UI responsiveness.',
            priority='medium',
            effort='medium',
            impact_score=20.0,
            confidence=0.80,
            implementation_steps=[
                'Move data-heavy logic to microflows',
                'Optimize nanoflow expressions',
                'Use synchronous microflows for critical paths',
                'Minimize client-server round trips'
            ],
            academic_rationale='Client-side processing blocks main thread',
            references=['Client-Server Architecture Best Practices']
        ))
        
        return recommendations
    
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract Mendix-specific metrics."""
        metrics = PlatformMetrics()
        entries = raw_data.get('performance_entries', [])
        
        # Mendix client overhead
        mendix_entries = [e for e in entries 
                         if any(p in e.get('name', '').lower() 
                               for p in ['mxui', 'mendix', 'mxclientsystem'])]
        metrics.platform_overhead_ms = sum(e.get('duration', 0) for e in mendix_entries)
        
        # Microflow count
        microflow_data = raw_data.get('microflow_calls', [])
        metrics.custom_script_count = len(microflow_data)
        
        # Entity bindings
        entity_data = raw_data.get('entity_retrievals', [])
        metrics.data_binding_count = len(entity_data)
        
        return metrics
    
    def _detect_n_plus_one(self, traces: List[Dict]) -> int:
        """Detect potential N+1 query patterns."""
        retrieves = [t for t in traces if 'retrieve' in str(t).lower()]
        
        # Look for sequential retrieves without batching
        sequential = 0
        for i in range(1, len(retrieves)):
            time_diff = retrieves[i].get('startTime', 0) - retrieves[i-1].get('endTime', retrieves[i-1].get('startTime', 0))
            if time_diff < 50:  # Less than 50ms apart suggests sequential in loop
                sequential += 1
        
        return sequential
