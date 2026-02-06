"""Platform detection and analysis module.

This module provides an extensible architecture for supporting multiple
low-code, no-code, and e-commerce platforms with platform-specific analysis.
"""

from .registry import PlatformRegistry, PlatformDefinition, PlatformCategory
from .base import (
    PlatformAnalyzer,
    PlatformMetrics,
    PlatformRecommendation,
    PlatformSignature
)
from .implementations import (
    ShopifyAnalyzer,
    WebflowAnalyzer,
    MendixAnalyzer,
    WixAnalyzer,
    BubbleAnalyzer,
    OutSystemsAnalyzer,
    AirtableAnalyzer,
    GenericPlatformAnalyzer,
)

# Register all supported platforms
def register_all_platforms():
    """Register all platform implementations."""
    
    # E-commerce
    PlatformRegistry.register(PlatformDefinition(
        id='shopify',
        name='Shopify',
        category=PlatformCategory.ECOMMERCE,
        url_patterns=['myshopify.com', 'shopify.com'],
        analyzer_class=ShopifyAnalyzer
    ))
    
    # Low-code Platforms
    PlatformRegistry.register(PlatformDefinition(
        id='bubble',
        name='Bubble.io',
        category=PlatformCategory.LOW_CODE,
        url_patterns=['bubbleapps.io', 'bubble.is'],
        analyzer_class=BubbleAnalyzer
    ))
    
    PlatformRegistry.register(PlatformDefinition(
        id='outsystems',
        name='OutSystems',
        category=PlatformCategory.LOW_CODE,
        url_patterns=['outsystems.app', 'outsystems.com', 'outsystemscloud.com'],
        analyzer_class=OutSystemsAnalyzer
    ))
    
    PlatformRegistry.register(PlatformDefinition(
        id='airtable',
        name='Airtable',
        category=PlatformCategory.LOW_CODE,
        url_patterns=['airtable.com', 'airtable.app', 'airtable.work'],
        analyzer_class=AirtableAnalyzer
    ))
    
    # No-code Website Builders
    PlatformRegistry.register(PlatformDefinition(
        id='webflow',
        name='Webflow',
        category=PlatformCategory.NO_CODE,
        url_patterns=['webflow.io', 'webflow.com'],
        analyzer_class=WebflowAnalyzer
    ))
    
    PlatformRegistry.register(PlatformDefinition(
        id='wix',
        name='Wix',
        category=PlatformCategory.NO_CODE,
        url_patterns=['wixsite.com', 'wix.com'],
        analyzer_class=WixAnalyzer
    ))
    
    # Low-code Enterprise
    PlatformRegistry.register(PlatformDefinition(
        id='mendix',
        name='Mendix',
        category=PlatformCategory.LOW_CODE,
        url_patterns=['mendixcloud.com', 'mendix.com'],
        analyzer_class=MendixAnalyzer
    ))
    
    # Generic fallback (lowest priority)
    PlatformRegistry.register(PlatformDefinition(
        id='generic',
        name='Generic Web Application',
        category=PlatformCategory.GENERIC,
        url_patterns=[],
        analyzer_class=GenericPlatformAnalyzer
    ), priority=0)

# Auto-register on import
register_all_platforms()

__all__ = [
    'PlatformRegistry',
    'PlatformDefinition',
    'PlatformCategory',
    'PlatformAnalyzer',
    'PlatformMetrics',
    'PlatformRecommendation',
    'PlatformSignature',
    'ShopifyAnalyzer',
    'BubbleAnalyzer',
    'OutSystemsAnalyzer',
    'AirtableAnalyzer',
    'WebflowAnalyzer',
    'MendixAnalyzer',
    'WixAnalyzer',
    'GenericPlatformAnalyzer',
]
