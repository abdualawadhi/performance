"""Tests for platform analyzers."""

import pytest
from lowcode_scanner.platforms import (
    PlatformRegistry,
    PlatformCategory,
    ShopifyAnalyzer,
    WebflowAnalyzer,
    MendixAnalyzer,
    WixAnalyzer,
    GenericPlatformAnalyzer,
)


class TestPlatformDetection:
    """Test platform detection accuracy."""
    
    def test_detect_shopify(self):
        """Test Shopify URL detection."""
        url = "https://example.myshopify.com"
        platform = PlatformRegistry.detect_platform(url)
        assert platform.id == 'shopify'
        assert platform.category == PlatformCategory.ECOMMERCE
    
    def test_detect_webflow(self):
        """Test Webflow URL detection."""
        url = "https://example.webflow.io"
        platform = PlatformRegistry.detect_platform(url)
        assert platform.id == 'webflow'
        assert platform.category == PlatformCategory.NO_CODE
    
    def test_detect_mendix(self):
        """Test Mendix URL detection."""
        url = "https://example.mendixcloud.com"
        platform = PlatformRegistry.detect_platform(url)
        assert platform.id == 'mendix'
        assert platform.category == PlatformCategory.LOW_CODE
    
    def test_detect_wix(self):
        """Test Wix URL detection."""
        url = "https://example.wixsite.com"
        platform = PlatformRegistry.detect_platform(url)
        assert platform.id == 'wix'
        assert platform.category == PlatformCategory.NO_CODE
    
    def test_generic_fallback(self):
        """Test fallback to generic for unknown platforms."""
        url = "https://example.com"
        platform = PlatformRegistry.detect_platform(url)
        assert platform.id == 'generic'
        assert platform.category == PlatformCategory.GENERIC
    
    def test_list_by_category(self):
        """Test listing platforms by category."""
        no_code_platforms = PlatformRegistry.list_by_category(PlatformCategory.NO_CODE)
        platform_ids = [p.id for p in no_code_platforms]
        assert 'webflow' in platform_ids
        assert 'wix' in platform_ids


class TestShopifyAnalyzer:
    """Test Shopify-specific analysis."""
    
    def test_detect_signatures(self):
        """Test signature detection."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='shopify',
            name='Shopify',
            category=PlatformCategory.ECOMMERCE,
            url_patterns=['myshopify.com'],
            analyzer_class=ShopifyAnalyzer
        )
        analyzer = ShopifyAnalyzer("https://test.myshopify.com", platform_def)
        content = '<script src="//cdn.shopify.com/s/files/1/..."></script><div class="shopify-checkout"></div>'
        signature = analyzer.detect_platform_signature(content, {})
        assert signature.confidence_score > 0.3
        assert 'shopify_cdn' in signature.detected_features
    
    def test_calculate_efficiency_score(self):
        """Test efficiency score calculation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='shopify',
            name='Shopify',
            category=PlatformCategory.ECOMMERCE,
            url_patterns=['myshopify.com'],
            analyzer_class=ShopifyAnalyzer
        )
        analyzer = ShopifyAnalyzer("https://test.myshopify.com", platform_def)
        analyzer.metrics.platform_overhead_ms = 150
        analyzer.metrics.cache_hit_ratio = 0.85
        score = analyzer.calculate_efficiency_score()
        assert 0 <= score <= 100
        # With high cache hit ratio, score should be decent
        assert score > 70
    
    def test_analyze_platform_overhead(self):
        """Test platform overhead calculation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='shopify',
            name='Shopify',
            category=PlatformCategory.ECOMMERCE,
            url_patterns=['myshopify.com'],
            analyzer_class=ShopifyAnalyzer
        )
        analyzer = ShopifyAnalyzer("https://test.myshopify.com", platform_def)
        entries = [
            {'name': 'https://cdn.shopify.com/s/files/theme.js', 'duration': 100},
            {'name': 'https://cdn.shopify.com/s/files/app.js', 'duration': 50},
            {'name': 'https://other.com/script.js', 'duration': 200},
        ]
        overhead = analyzer.analyze_platform_overhead(entries)
        assert overhead == 150  # Only Shopify assets counted
    
    def test_identify_bottlenecks(self):
        """Test bottleneck identification."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='shopify',
            name='Shopify',
            category=PlatformCategory.ECOMMERCE,
            url_patterns=['myshopify.com'],
            analyzer_class=ShopifyAnalyzer
        )
        analyzer = ShopifyAnalyzer("https://test.myshopify.com", platform_def)
        traces = [
            {'name': 'apps.affiliate.js', 'initiatorType': 'script'},
            {'name': 'apps.review.js', 'initiatorType': 'script'},
            {'name': 'apps.chat.js', 'initiatorType': 'script'},
            {'name': 'apps.analytics.js', 'initiatorType': 'script'},
            {'name': 'apps.marketing.js', 'initiatorType': 'script'},
            {'name': 'apps.support.js', 'initiatorType': 'script'},
        ]
        bottlenecks = analyzer.identify_platform_bottlenecks(traces)
        assert len(bottlenecks) > 0
        assert any(b['bottleneck_type'] == 'app_bloat' for b in bottlenecks)
    
    def test_calculate_custom_code_impact(self):
        """Test custom code impact calculation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='shopify',
            name='Shopify',
            category=PlatformCategory.ECOMMERCE,
            url_patterns=['myshopify.com'],
            analyzer_class=ShopifyAnalyzer
        )
        analyzer = ShopifyAnalyzer("https://test.myshopify.com", platform_def)
        scripts = [
            {'name': 'https://cdn.shopify.com/theme.js', 'duration': 100},
            {'name': 'https://apps.shopify.com/app.js', 'duration': 50},
            {'name': 'https://example.com/custom.js', 'duration': 200},
        ]
        impact = analyzer.calculate_custom_code_impact(scripts)
        assert 'platform_code_ms' in impact
        assert 'custom_code_ms' in impact
        assert impact['platform_code_ms'] == 100
        assert impact['custom_code_ms'] == 200
        assert impact['app_code_ms'] == 50


class TestWebflowAnalyzer:
    """Test Webflow-specific analysis."""
    
    def test_detect_signatures(self):
        """Test signature detection."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='webflow',
            name='Webflow',
            category=PlatformCategory.NO_CODE,
            url_patterns=['webflow.io'],
            analyzer_class=WebflowAnalyzer
        )
        analyzer = WebflowAnalyzer("https://test.webflow.io", platform_def)
        content = '<html data-wf-page="123" data-wf-site="456"><script src="webflow.js"></script>'
        signature = analyzer.detect_platform_signature(content, {})
        assert signature.confidence_score > 0
        assert 'webflow_js' in signature.detected_features
    
    def test_analyze_platform_overhead(self):
        """Test platform overhead calculation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='webflow',
            name='Webflow',
            category=PlatformCategory.NO_CODE,
            url_patterns=['webflow.io'],
            analyzer_class=WebflowAnalyzer
        )
        analyzer = WebflowAnalyzer("https://test.webflow.io", platform_def)
        entries = [
            {'name': 'https://cdn.prod.website-files.com/webflow.js', 'duration': 80},
            {'name': 'https://cdn.prod.website-files.com/animations.js', 'duration': 40},
        ]
        overhead = analyzer.analyze_platform_overhead(entries)
        assert overhead == 120
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='webflow',
            name='Webflow',
            category=PlatformCategory.NO_CODE,
            url_patterns=['webflow.io'],
            analyzer_class=WebflowAnalyzer
        )
        analyzer = WebflowAnalyzer("https://test.webflow.io", platform_def)
        recommendations = analyzer.generate_platform_recommendations()
        assert len(recommendations) > 0
        categories = [r.category for r in recommendations]
        assert 'Animation Performance' in categories


class TestMendixAnalyzer:
    """Test Mendix-specific analysis."""
    
    def test_detect_signatures(self):
        """Test signature detection."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='mendix',
            name='Mendix',
            category=PlatformCategory.LOW_CODE,
            url_patterns=['mendixcloud.com'],
            analyzer_class=MendixAnalyzer
        )
        analyzer = MendixAnalyzer("https://test.mendixcloud.com", platform_def)
        content = '<script src="mxui.js"></script><script>var mxui = "8.0.0";</script>'
        signature = analyzer.detect_platform_signature(content, {})
        assert signature.confidence_score > 0
        assert 'mendix_client' in signature.detected_features
    
    def test_identify_microflow_bottleneck(self):
        """Test microflow bottleneck detection."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='mendix',
            name='Mendix',
            category=PlatformCategory.LOW_CODE,
            url_patterns=['mendixcloud.com'],
            analyzer_class=MendixAnalyzer
        )
        analyzer = MendixAnalyzer("https://test.mendixcloud.com", platform_def)
        traces = [
            {'name': 'microflow_GetData', 'duration': 600},
            {'name': 'microflow_ProcessOrder', 'duration': 700},
        ]
        bottlenecks = analyzer.identify_platform_bottlenecks(traces)
        assert any(b['bottleneck_type'] == 'microflow_performance' for b in bottlenecks)


class TestWixAnalyzer:
    """Test Wix-specific analysis."""
    
    def test_detect_signatures(self):
        """Test signature detection."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='wix',
            name='Wix',
            category=PlatformCategory.NO_CODE,
            url_patterns=['wixsite.com'],
            analyzer_class=WixAnalyzer
        )
        analyzer = WixAnalyzer("https://test.wixsite.com", platform_def)
        content = '<script src="https://static.wixstatic.com/..."></script>'
        headers = {'server': 'wix.com'}
        signature = analyzer.detect_platform_signature(content, headers)
        assert signature.confidence_score > 0
        assert 'wix_branding' in signature.detected_features
    
    def test_calculate_custom_code_impact(self):
        """Test Velo code impact calculation."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='wix',
            name='Wix',
            category=PlatformCategory.NO_CODE,
            url_patterns=['wixsite.com'],
            analyzer_class=WixAnalyzer
        )
        analyzer = WixAnalyzer("https://test.wixsite.com", platform_def)
        scripts = [
            {'name': 'https://static.wixstatic.com/main.js', 'duration': 100},
            {'name': 'https://site-123.pages--site.js', 'duration': 50},  # Editor-generated
            {'name': 'https://example.com/custom.js', 'duration': 200},
        ]
        impact = analyzer.calculate_custom_code_impact(scripts)
        assert impact['platform_code_ms'] == 125  # 100 + 50/2
        assert impact['custom_code_ms'] == 225  # 200 + 50/2


class TestGenericAnalyzer:
    """Test generic analyzer."""
    
    def test_generic_detection(self):
        """Test generic detection returns low confidence."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='generic',
            name='Generic',
            category=PlatformCategory.GENERIC,
            url_patterns=[],
            analyzer_class=GenericPlatformAnalyzer
        )
        analyzer = GenericPlatformAnalyzer("https://example.com", platform_def)
        signature = analyzer.detect_platform_signature("", {})
        assert signature.confidence_score == 0.0
        assert signature.detection_method == 'fallback'
    
    def test_generic_recommendations(self):
        """Test generic recommendations."""
        from lowcode_scanner.platforms import PlatformDefinition, PlatformCategory
        platform_def = PlatformDefinition(
            id='generic',
            name='Generic',
            category=PlatformCategory.GENERIC,
            url_patterns=[],
            analyzer_class=GenericPlatformAnalyzer
        )
        analyzer = GenericPlatformAnalyzer("https://example.com", platform_def)
        recommendations = analyzer.generate_platform_recommendations()
        assert len(recommendations) >= 1
        assert recommendations[0].category == 'General'


class TestPlatformRegistry:
    """Test platform registry functionality."""
    
    def test_get_all_platforms(self):
        """Test getting all registered platforms."""
        platforms = PlatformRegistry.get_all_platforms()
        assert 'shopify' in platforms
        assert 'webflow' in platforms
        assert 'mendix' in platforms
        assert 'wix' in platforms
        assert 'generic' in platforms
    
    def test_get_analyzer(self):
        """Test getting analyzer for URL."""
        analyzer = PlatformRegistry.get_analyzer("https://test.myshopify.com")
        assert isinstance(analyzer, ShopifyAnalyzer)
        
        analyzer = PlatformRegistry.get_analyzer("https://test.webflow.io")
        assert isinstance(analyzer, WebflowAnalyzer)
        
        analyzer = PlatformRegistry.get_analyzer("https://unknown.com")
        assert isinstance(analyzer, GenericPlatformAnalyzer)


class TestPlatformIntegration:
    """Test integration with existing platform detector."""
    
    def test_new_registry_in_detector(self):
        """Test that PlatformDetector integrates with new registry."""
        from lowcode_scanner.core.platform_detector import PlatformDetector
        detector = PlatformDetector()
        
        # Test getting new-style analyzer
        analyzer = detector.get_platform_analyzer("https://test.myshopify.com")
        assert isinstance(analyzer, ShopifyAnalyzer)
    
    def test_async_detection_integration(self):
        """Test async detection uses new registry."""
        import asyncio
        from lowcode_scanner.core.platform_detector import PlatformDetector
        from lowcode_scanner.models import LowCodePlatform
        
        detector = PlatformDetector()
        
        # Test that Mendix is still detected correctly
        result = asyncio.run(detector.detect_platform_async("https://test.mendixcloud.com"))
        assert result == LowCodePlatform.MENDIX
