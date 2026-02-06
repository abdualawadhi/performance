"""Generic platform analyzer for unsupported platforms."""

from typing import Dict, List, Any
from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature


class GenericPlatformAnalyzer(PlatformAnalyzer):
    """Generic analyzer for any web application."""
    
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Generic detection with low confidence."""
        return PlatformSignature(
            platform_id='generic',
            detected_version=None,
            detected_features=[],
            confidence_score=0.0,
            detection_method='fallback'
        )
    
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Estimate framework overhead heuristically."""
        # Look for common framework signatures
        framework_patterns = ['react', 'vue', 'angular', 'jquery']
        overhead = 0.0
        
        for entry in performance_entries:
            name = entry.get('name', '').lower()
            if any(fw in name for fw in framework_patterns):
                overhead += entry.get('duration', 0)
        
        return overhead
    
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Generic bottleneck detection."""
        bottlenecks = []
        
        # Large resources
        large_resources = [t for t in traces if t.get('transferSize', 0) > 500000]
        if len(large_resources) > 3:
            bottlenecks.append({
                'bottleneck_type': 'large_resources',
                'severity': min(10, len(large_resources)),
                'location': 'assets',
                'evidence': f'{len(large_resources)} large resources',
                'recommendation': 'Compress images, minify code, enable compression'
            })
        
        # Render blocking
        blocking_scripts = [t for t in traces 
                           if t.get('initiatorType') == 'script' 
                           and t.get('startTime', 0) < 1000]
        if len(blocking_scripts) > 5:
            bottlenecks.append({
                'bottleneck_type': 'render_blocking',
                'severity': min(10, len(blocking_scripts) // 2),
                'location': 'scripts',
                'evidence': f'{len(blocking_scripts)} early-loading scripts',
                'recommendation': 'Defer non-critical scripts, use async loading'
            })
        
        return bottlenecks
    
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Generic code impact analysis."""
        total = sum(s.get('duration', 0) for s in scripts)
        return {
            'platform_code_ms': 0,
            'custom_code_ms': total,
            'platform_ratio': 0.0,
            'custom_ratio': 1.0,
        }
    
    def generate_platform_recommendations(self) -> List[PlatformRecommendation]:
        """Generic web performance recommendations."""
        return [
            PlatformRecommendation(
                category='General',
                title='Optimize Web Performance',
                description='General performance optimizations applicable to any platform.',
                priority='medium',
                effort='medium',
                impact_score=20.0,
                confidence=0.70,
                implementation_steps=[
                    'Enable compression (Gzip/Brotli)',
                    'Optimize images',
                    'Minify CSS/JavaScript',
                    'Enable browser caching'
                ],
                academic_rationale='Core Web Vitals best practices',
                references=['Web Performance Best Practices']
            )
        ]
    
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract generic metrics."""
        return PlatformMetrics()
