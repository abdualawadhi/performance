"""Wix platform analyzer.

Wix is a popular no-code website builder with Velo development platform.
Key performance factors:
- Velo code execution
- Dataset performance
- App market widget impact
- Editor vs production differences
"""

import re
from typing import Dict, List, Any
from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature


class WixAnalyzer(PlatformAnalyzer):
    """Analyzer for Wix websites."""
    
    VELO_THRESHOLD_MS = 150
    DATASET_THRESHOLD_MS = 200
    WIDGET_LIMIT = 10
    
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Detect Wix platform signatures."""
        signatures = {
            'wix_branding': 'wix.com' in headers.get('server', '').lower(),
            'wix_data': 'wix-data' in page_content or 'wixData' in page_content,
            'wix_location': 'wix-location' in page_content,
            'wix_window': 'wix-window' in page_content,
            'wix_site': 'static.wixstatic.com' in page_content or 'wixsite.com' in page_content,
            'wix_bo': 'wix-bo' in page_content or 'bolt-on' in page_content,
        }
        
        detected = [k for k, v in signatures.items() if v]
        confidence = len(detected) / len(signatures)
        
        return PlatformSignature(
            platform_id='wix',
            detected_version=None,
            detected_features=detected,
            confidence_score=confidence,
            detection_method='header_and_content'
        )
    
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Calculate Wix platform overhead."""
        overhead = 0.0
        
        # Wix static assets
        wix_static = [e for e in performance_entries 
                     if 'wixstatic.com' in e.get('name', '')]
        for entry in wix_static:
            overhead += entry.get('duration', 0) * 0.8  # 80% platform
        
        # Wix apps/widgets
        wix_apps = [e for e in performance_entries
                   if 'wixapps' in e.get('name', '').lower()]
        for app in wix_apps:
            overhead += app.get('duration', 0) * 0.5
        
        return overhead
    
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Identify Wix-specific bottlenecks."""
        bottlenecks = []
        
        # Velo code performance
        velo_calls = [t for t in traces if any(x in str(t) for x in ['wix-', '$w'])]
        if velo_calls:
            avg_velo = sum(v.get('duration', 0) for v in velo_calls) / len(velo_calls)
            if avg_velo > self.VELO_THRESHOLD_MS:
                bottlenecks.append({
                    'bottleneck_type': 'velo_code_performance',
                    'severity': min(10, int(avg_velo / 30)),
                    'location': 'custom_code',
                    'evidence': f'Avg Velo execution: {avg_velo:.0f}ms',
                    'recommendation': 'Optimize Velo code, reduce dataset operations, debounce event handlers'
                })
        
        # Dataset performance
        dataset_ops = [t for t in traces if 'dataset' in str(t).lower()]
        if dataset_ops:
            avg_dataset = sum(d.get('duration', 0) for d in dataset_ops) / len(dataset_ops)
            if avg_dataset > self.DATASET_THRESHOLD_MS:
                bottlenecks.append({
                    'bottleneck_type': 'dataset_performance',
                    'severity': min(10, int(avg_dataset / 40)),
                    'location': 'data_binding',
                    'evidence': f'Avg dataset op: {avg_dataset:.0f}ms',
                    'recommendation': 'Filter on server, reduce items per page, use efficient queries'
                })
        
        # Widget bloat
        widgets = [t for t in traces if 'wixapps' in t.get('name', '').lower()]
        if len(widgets) > self.WIDGET_LIMIT:
            bottlenecks.append({
                'bottleneck_type': 'excessive_widgets',
                'severity': min(10, len(widgets) // 2),
                'location': 'app_market_widgets',
                'evidence': f'{len(widgets)} widgets detected',
                'recommendation': 'Remove unused widgets, consolidate functionality'
            })
        
        # Image optimization
        images = [t for t in traces if t.get('initiatorType') == 'img']
        non_wix_images = [i for i in images if 'wixstatic.com' not in i.get('name', '')]
        if non_wix_images:
            bottlenecks.append({
                'bottleneck_type': 'external_images',
                'severity': min(10, len(non_wix_images)),
                'location': 'image_assets',
                'evidence': f'{len(non_wix_images)} non-Wix images',
                'recommendation': 'Upload images to Wix for automatic optimization'
            })
        
        return bottlenecks
    
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Analyze Velo custom code impact."""
        wix_patterns = ['wixstatic.com', 'wixapps', 'wix-bo']
        velo_patterns = ['pages--', 'site--']  # Wix editor generated
        
        platform_time = 0.0
        custom_time = 0.0
        
        for script in scripts:
            duration = script.get('duration', 0)
            name = script.get('name', '')
            
            if any(p in name for p in wix_patterns):
                platform_time += duration
            elif any(p in name for p in velo_patterns):
                # Editor-generated code is 50/50 platform/custom
                platform_time += duration * 0.5
                custom_time += duration * 0.5
            else:
                custom_time += duration
        
        return {
            'platform_code_ms': platform_time,
            'custom_code_ms': custom_time,
            'platform_ratio': platform_time / (platform_time + custom_time + 1),
            'custom_ratio': custom_time / (platform_time + custom_time + 1),
        }
    
    def generate_platform_recommendations(self) -> List[PlatformRecommendation]:
        """Generate Wix-specific recommendations."""
        recommendations = []
        
        recommendations.append(PlatformRecommendation(
            category='Custom Code',
            title='Optimize Velo Code Performance',
            description='Custom Velo code can significantly impact page performance.',
            priority='high',
            effort='medium',
            impact_score=25.0,
            confidence=0.85,
            implementation_steps=[
                'Minimize dataset operations in page load',
                'Use debouncing for event handlers',
                'Implement lazy loading for dynamic content',
                'Cache reference data in memory'
            ],
            academic_rationale='Custom code execution blocks main thread and increases TTI',
            references=['Wix Velo Performance Guide']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='Data Performance',
            title='Optimize Dataset Configuration',
            description='Dataset settings directly impact data loading performance.',
            priority='high',
            effort='low',
            impact_score=30.0,
            confidence=0.90,
            implementation_steps=[
                'Set appropriate page size (10-50 items)',
                'Filter data on server side',
                'Sort data at collection level',
                'Use reference fields efficiently'
            ],
            academic_rationale='Client-side data manipulation increases processing time',
            references=['Dataset Performance Best Practices']
        ))
        
        recommendations.append(PlatformRecommendation(
            category='Widget Management',
            title='Audit and Optimize App Market Widgets',
            description='Each widget adds JavaScript and potentially blocks rendering.',
            priority='medium',
            effort='low',
            impact_score=20.0,
            confidence=0.85,
            implementation_steps=[
                'Remove unused widgets',
                'Consolidate similar functionality',
                'Check widget load times in performance tab',
                'Prioritize above-fold widgets'
            ],
            academic_rationale='Third-party widgets contribute significantly to total blocking time',
            references=['Widget Performance Impact Study']
        ))
        
        return recommendations
    
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract Wix-specific metrics."""
        metrics = PlatformMetrics()
        entries = raw_data.get('performance_entries', [])
        
        # Wix assets
        wix_entries = [e for e in entries 
                      if 'wix' in e.get('name', '').lower()]
        metrics.platform_overhead_ms = sum(e.get('duration', 0) for e in wix_entries)
        
        # Velo operations
        velo_ops = raw_data.get('velo_operations', [])
        metrics.custom_script_count = len(velo_ops)
        
        # Dataset bindings
        datasets = [e for e in entries if 'dataset' in str(e).lower()]
        metrics.data_binding_count = len(datasets)
        
        return metrics
