"""Shopify platform analyzer.

Shopify is an e-commerce platform using Liquid templating.
Key performance factors:
- Liquid template rendering time
- App/plugin impact on load time
- Image optimization (Shopify CDN)
- Checkout flow performance
"""

import re
import statistics
from typing import Dict, List, Any, Optional
from ..base import PlatformAnalyzer, PlatformMetrics, PlatformRecommendation, PlatformSignature


class ShopifyAnalyzer(PlatformAnalyzer):
    """Analyzer for Shopify e-commerce platforms."""
    
    # Shopify-specific performance thresholds
    LIQUID_RENDER_THRESHOLD_MS = 200  # Acceptable Liquid render time
    APP_IMPACT_THRESHOLD_MS = 300     # Per-app impact threshold
    IMAGE_OPTIMIZATION_BONUS = 10     # Score bonus for Shopify CDN images
    
    def detect_platform_signature(self, page_content: str, 
                                   headers: Dict[str, str]) -> PlatformSignature:
        """Detect Shopify platform signatures."""
        signatures = {
            'shopify_checkout': 'shopify-checkout' in page_content,
            'shopify_cdn': 'cdn.shopify.com' in page_content,
            'liquid_template': 'Liquid' in page_content or '{%' in page_content,
            'shopify_theme': 'Shopify.theme' in page_content,
            'storefront_api': 'storefront-api' in headers.get('powered-by', ''),
        }
        
        detected_features = [k for k, v in signatures.items() if v]
        confidence = len(detected_features) / len(signatures)
        
        # Version detection
        version_match = re.search(r'Shopify\.theme\s*=\s*\{[^}]*"version":\s*"([^"]+)"', page_content)
        version = version_match.group(1) if version_match else None
        
        return PlatformSignature(
            platform_id='shopify',
            detected_version=version,
            detected_features=detected_features,
            confidence_score=confidence,
            detection_method='content_analysis'
        )
    
    def analyze_platform_overhead(self, performance_entries: List[Dict]) -> float:
        """Calculate Shopify framework overhead."""
        overhead = 0.0
        
        # Shopify CDN asset loading
        shopify_assets = [e for e in performance_entries 
                         if 'cdn.shopify.com' in e.get('name', '')]
        for asset in shopify_assets:
            overhead += asset.get('duration', 0)
        
        # Shopify app assets
        app_assets = [e for e in performance_entries
                     if any(x in e.get('name', '') for x in ['apps.shopify', 'cdn.apps'])]
        for asset in app_assets:
            overhead += asset.get('duration', 0) * 0.5  # 50% attributed to platform
        
        return overhead
    
    def identify_platform_bottlenecks(self, traces: List[Dict]) -> List[Dict]:
        """Identify Shopify-specific bottlenecks."""
        bottlenecks = []
        
        # Check for excessive Liquid renders
        liquid_renders = [t for t in traces if 'liquid' in t.get('name', '').lower()]
        if liquid_renders:
            avg_render_time = statistics.mean([r.get('duration', 0) for r in liquid_renders])
            if avg_render_time > self.LIQUID_RENDER_THRESHOLD_MS:
                bottlenecks.append({
                    'bottleneck_type': 'liquid_rendering',
                    'severity': min(10, int(avg_render_time / 50)),
                    'location': 'server_side_template',
                    'evidence': f'Avg Liquid render: {avg_render_time:.0f}ms',
                    'recommendation': 'Simplify Liquid logic, use fragments, implement caching'
                })
        
        # Check for app bloat
        app_scripts = [t for t in traces if 'apps' in t.get('name', '')]
        if len(app_scripts) > 5:
            bottlenecks.append({
                'bottleneck_type': 'app_bloat',
                'severity': min(10, len(app_scripts)),
                'location': 'third_party_apps',
                'evidence': f'{len(app_scripts)} app scripts detected',
                'recommendation': 'Audit installed apps, remove unused ones, consolidate functionality'
            })
        
        # Check for unoptimized images
        images = [t for t in traces if t.get('initiatorType') == 'img']
        unoptimized = [i for i in images 
                      if 'cdn.shopify.com' not in i.get('name', '') 
                      and i.get('transferSize', 0) > 100000]
        if unoptimized:
            bottlenecks.append({
                'bottleneck_type': 'unoptimized_images',
                'severity': min(10, len(unoptimized)),
                'location': 'image_assets',
                'evidence': f'{len(unoptimized)} unoptimized images',
                'recommendation': 'Use Shopify CDN, implement lazy loading, compress images'
            })
        
        return bottlenecks
    
    def calculate_custom_code_impact(self, scripts: List[Dict]) -> Dict[str, float]:
        """Distinguish Shopify platform code from custom code."""
        shopify_patterns = ['cdn.shopify.com', 'shopify-checkout', 'shopify-payment']
        app_patterns = ['apps.shopify.com', 'cdn.apps']
        
        platform_time = 0.0
        custom_time = 0.0
        app_time = 0.0
        
        for script in scripts:
            duration = script.get('duration', 0)
            name = script.get('name', '')
            
            if any(p in name for p in shopify_patterns):
                platform_time += duration
            elif any(p in name for p in app_patterns):
                app_time += duration
            else:
                custom_time += duration
        
        return {
            'platform_code_ms': platform_time,
            'custom_code_ms': custom_time,
            'app_code_ms': app_time,
            'platform_ratio': platform_time / (platform_time + custom_time + app_time + 1),
            'custom_ratio': custom_time / (platform_time + custom_time + app_time + 1),
        }
    
    def generate_platform_recommendations(self) -> List[PlatformRecommendation]:
        """Generate Shopify-specific recommendations."""
        recommendations = []
        
        # Liquid optimization
        recommendations.append(PlatformRecommendation(
            category='Template Performance',
            title='Optimize Liquid Template Rendering',
            description='Complex Liquid logic increases server response time.',
            priority='high',
            effort='medium',
            impact_score=25.0,
            confidence=0.85,
            implementation_steps=[
                'Minimize Liquid loops and conditionals',
                'Use {% render %} with cache for fragments',
                'Implement section-level caching',
                'Avoid nested loops where possible'
            ],
            academic_rationale='Server-side rendering overhead directly impacts TTFB',
            references=['Shopify Performance Best Practices', 'Liquid Optimization Guide']
        ))
        
        # App audit
        recommendations.append(PlatformRecommendation(
            category='Third-Party Impact',
            title='Audit and Optimize Installed Apps',
            description='Each app adds JavaScript and potentially blocks rendering.',
            priority='high',
            effort='low',
            impact_score=30.0,
            confidence=0.90,
            implementation_steps=[
                'Review installed apps for redundancy',
                'Remove unused apps completely',
                'Consolidate functionality where possible',
                'Use Shopify-native features over apps'
            ],
            academic_rationale='Third-party scripts are primary contributor to performance variance',
            references=['Web Performance Research: Third-Party Impact']
        ))
        
        # Image optimization
        recommendations.append(PlatformRecommendation(
            category='Asset Optimization',
            title='Leverage Shopify CDN for Images',
            description='Shopify CDN provides automatic optimization.',
            priority='medium',
            effort='low',
            impact_score=20.0,
            confidence=0.95,
            implementation_steps=[
                'Upload images to Shopify (not external)',
                'Use responsive image sizes',
                'Enable lazy loading',
                'Use WebP format where supported'
            ],
            academic_rationale='CDN delivery reduces latency and improves caching',
            references=['Image Optimization Best Practices']
        ))
        
        return recommendations
    
    def extract_platform_metrics(self, raw_data: Dict) -> PlatformMetrics:
        """Extract Shopify-specific metrics."""
        metrics = PlatformMetrics()
        
        # Calculate from performance entries
        entries = raw_data.get('performance_entries', [])
        
        # Shopify overhead
        shopify_entries = [e for e in entries if 'shopify' in e.get('name', '').lower()]
        metrics.platform_overhead_ms = sum(e.get('duration', 0) for e in shopify_entries)
        
        # Asset sizes
        metrics.platform_assets_size_kb = sum(
            e.get('transferSize', 0) for e in shopify_entries
        ) / 1024
        
        # App count
        app_entries = [e for e in entries if 'apps' in e.get('name', '')]
        metrics.custom_script_count = len(app_entries)
        
        # Image optimization check
        images = [e for e in entries if e.get('initiatorType') == 'img']
        cdn_images = [i for i in images if 'cdn.shopify.com' in i.get('name', '')]
        metrics.cache_hit_ratio = len(cdn_images) / len(images) if images else 0
        
        return metrics
