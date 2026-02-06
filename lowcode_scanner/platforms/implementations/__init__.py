"""Platform implementations package."""

from .shopify import ShopifyAnalyzer
from .webflow import WebflowAnalyzer
from .mendix import MendixAnalyzer
from .wix import WixAnalyzer
from .bubble import BubbleAnalyzer
from .outsystems import OutSystemsAnalyzer
from .airtable import AirtableAnalyzer
from .generic import GenericPlatformAnalyzer

__all__ = [
    'ShopifyAnalyzer',
    'WebflowAnalyzer',
    'MendixAnalyzer',
    'WixAnalyzer',
    'BubbleAnalyzer',
    'OutSystemsAnalyzer',
    'AirtableAnalyzer',
    'GenericPlatformAnalyzer',
]
