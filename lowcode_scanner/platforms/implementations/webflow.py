"""Webflow platform analyzer.

Webflow is a visual web design platform generating clean HTML/CSS/JS.
Key performance factors:
- Animation and interaction complexity
- CMS collection loading
- Asset optimization
- Custom code integration
"""

import re
from typing import Dict, List, Any
from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature


class WebflowAnalyzer(PlatformAnalyzer):
    """Analyzer for Webflow-designed websites."""
    
    ANIMATION_THRESHOLD = 10  # Max recommended animations per page
    CMS_THRESHOLD_MS = 200    # CMS collection load threshold
    
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Detect Webflow platform signatures."""
        signatures = {
            'webflow_js': 'webflow.js' in page_content or 'data-wf-page' in page_content,
            'webflow_css': 'data-wf-stylesheet' in page_content,
            'webflow_cms': 'w-dyn-list' in page_content or 'w-dyn-item' in page_content,
            'webflow_animations': 'animations.js' in page_content or 'data-w-id' in page_content,
            'webflow_ecommerce': 'w-commerce' in page_content,
        }
        
        detected = [k for k, v in signatures.items() if v]
        confidence = len(detected) / len(signatures)
        
        # Extract Webflow site ID
        site_id_match = re.search(r'data-wf-site="([^"]+)"', page_content)
        
        return PlatformSignature(
            platform_id='webflow',
            detected_version=None,
            detected_features=detected,
            confidence_score=confidence,
            detection_method='html_attributes'
        )
    
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Calculate Webflow framework overhead."""
        overhead = 0.0
        
        # Webflow JS files
        webflow_js = [e for e in performance_entries 
                     if 'webflow' in e.get('name', '').lower()]
        for entry in webflow_js:
            overhead += entry.get('duration', 0)
        
        # Animation engine
        animation_js = [e for e in performance_entries
                       if 'animations' in e.get('name', '').lower()]
        for entry in animation_js:
            overhead += entry.get('duration', 0)
        
        return overhead
    
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Identify Webflow-specific bottlenecks."""
        bottlenecks = []
        
        # Animation complexity
        animation_events = [t for t in traces if 'animation' in t.get('name', '').lower()]
        if len(animation_events) > self.ANIMATION_THRESHOLD:
            bottlenecks.append({
                'bottleneck_type': 'excessive_animations',
                'severity': min(10, len(animation_events) // 3),
                'location': 'client_interactions',
                'evidence': f'{len(animation_events)} animation events detected',
                'recommendation': 'Reduce animations, use CSS transforms, throttle scroll events'
            })
        
        # CMS loading issues
        cms_requests = [t for t in traces if 'cdn.prod.website-files.com' in t.get('name', '')]
        cms_load_time = sum(r.get('duration', 0) for r in cms_requests)
        if cms_load_time > self.CMS_THRESHOLD_MS:
            bottlenecks.append({
                'bottleneck_type': 'cms_collection_loading',
                'severity': min(10, int(cms_load_time / 100)),
                'location': 'cms_dynamic_content',
                'evidence': f'CMS load time: {cms_load_time:.0f}ms',
                'recommendation': 'Paginate collections, lazy load images, optimize collection structure'
            })
        
        # Large DOM from visual design
        dom_elements = self._estimate_dom_complexity(traces)
        if dom_elements > 1500:
            bottlenecks.append({
                'bottleneck_type': 'dom_complexity',
                'severity': min(10, dom_elements // 300),
                'location': 'html_structure',
                'evidence': f'Estimated {dom_elements} DOM elements',
                'recommendation': 'Simplify structure, remove unused classes, consolidate elements'
            })
        
        return bottlenecks
    
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Analyze custom code impact in Webflow."""
        webflow_patterns = ['webflow.com', 'website-files.com']
        
        platform_time = 0.0
        custom_time = 0.0
        
        for script in scripts:
            duration = script.get('duration', 0)
            name = script.get('name', '')
            
            if any(p in name for p in webflow_patterns):
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
        """Generate Webflow-specific recommendations."""
        recommendations = []
        
        recommendations.append(PlatformRecommendation(
            category='Animation Performance',
            title='Optimize Interaction Animations',
            description='Webflow animations can cause layout thrashing and jank.',
            priority='high',
            effort='medium',
            impact_score=25.0,
            confidence=0.85,
            implementation_steps=[
                'Use transform and opacity for animations',
                'Avoid animating layout properties',
                'Reduce animation duration',
                'Throttle mouse move and scroll events',
                'Use will-change sparingly'
            ],
            academic_rationale='Layout thrashing from style recalculations impacts frame rate',
            references=['Webflow University: Animation Performance']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='CMS Optimization',
            title='Optimize CMS Collection Loading',
            description='Large CMS collections can significantly impact load time.',
            priority='high',
            effort='low',
            impact_score=30.0,
            confidence=0.90,
            implementation_steps=[
                'Implement pagination for large collections',
                'Lazy load images below the fold',
                'Limit items per collection list',
                'Use reference fields efficiently'
            ],
            academic_rationale='Dynamic content loading blocks critical rendering path',
            references=['CMS Performance Best Practices']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='Asset Delivery',
            title='Optimize Asset Delivery',
            description='Webflow CDN is optimized but asset sizing still matters.',
            priority='medium',
            effort='low',
            impact_score=20.0,
            confidence=0.90,
            implementation_steps=[
                'Compress images before upload',
                'Use responsive image variants',
                'Lazy load non-critical images',
                'Minimize custom font families'
            ],
            academic_rationale='Asset size directly correlates with load time and bandwidth',
            references=['Web Asset Optimization Research']
        ))
        
        return recommendations
    
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract Webflow-specific metrics."""
        metrics = PlatformMetrics()
        entries = raw_data.get('performance_entries', [])
        
        # Webflow-specific assets
        webflow_entries = [e for e in entries if 'webflow' in e.get('name', '').lower()]
        metrics.platform_overhead_ms = sum(e.get('duration', 0) for e in webflow_entries)
        
        # Animation count
        animation_data = raw_data.get('animation_data', [])
        metrics.component_count = len(animation_data)
        
        # CMS items
        cms_items = [e for e in entries if 'w-dyn-item' in str(e)]
        metrics.data_binding_count = len(cms_items)
        
        return metrics
    
    def _estimate_dom_complexity(self, traces: List[Dict]) -> int:
        """Estimate DOM element count from trace data."""
        # Simplified estimation based on style recalculations
        style_recalcs = [t for t in traces if 'Recalculate Style' in t.get('name', '')]
        return len(style_recalcs) * 50  # Rough estimate
