# Platform Architecture Documentation

## Design Rationale

The platform detection and analysis system implements several established
design patterns to enable extensible, maintainable platform support:

### 1. Registry Pattern
**Purpose**: Decouple platform detection from analysis logic
**Benefits**:
- New platforms added without modifying existing code (Open/Closed Principle)
- Supports runtime platform registration for plugin architecture
- Centralized platform management

### 2. Strategy Pattern
**Purpose**: Enable polymorphic platform analysis
**Benefits**:
- Uniform interface across all platforms
- Platform-specific optimizations isolated
- Easy testing and mocking

### 3. Template Method Pattern
**Purpose**: Define analysis workflow while allowing customization
**Benefits**:
- Consistent analysis process
- Platform-specific hooks for customization
- Reduced code duplication

## Platform Taxonomy

For academic research, platforms are categorized:

### Low-Code Platforms
Platforms enabling rapid application development with visual tools
while allowing custom code when needed.

Examples: Mendix, OutSystems, Bubble

### No-Code Platforms
Platforms enabling complete application development through
visual interfaces without coding.

Examples: Webflow, Wix, Squarespace

### E-commerce Platforms
Platforms specialized for online commerce with integrated
payment, inventory, and fulfillment features.

Examples: Shopify, BigCommerce, WooCommerce

## Adding New Platforms

To add support for a new platform:

1. Create analyzer class inheriting from `PlatformAnalyzer`
2. Implement abstract methods for platform-specific logic
3. Register in `PlatformRegistry` with URL patterns
4. Add tests with sample data

Example:
```python
from lowcode_scanner.platforms import PlatformAnalyzer, PlatformRegistry, PlatformDefinition

class MyPlatformAnalyzer(PlatformAnalyzer):
    def detect_platform_signature(self, page_content, headers):
        # Implementation
        pass
    
    # ... other methods

PlatformRegistry.register(PlatformDefinition(
    id='myplatform',
    name='My Platform',
    category=PlatformCategory.LOW_CODE,
    url_patterns=['myplatform.com'],
    analyzer_class=MyPlatformAnalyzer
))
```

## Architecture Components

### Core Classes

#### PlatformAnalyzer (Abstract Base)
Defines the interface that all platform analyzers must implement:
- `detect_platform_signature()`: Identify platform-specific signatures
- `analyze_platform_overhead()`: Calculate framework overhead
- `identify_platform_bottlenecks()`: Find performance issues
- `calculate_custom_code_impact()`: Distinguish platform vs custom code
- `generate_platform_recommendations()`: Provide optimization guidance
- `extract_platform_metrics()`: Extract platform-specific metrics

#### PlatformRegistry
Central registry for platform management:
- `register()`: Add new platform definitions
- `detect_platform()`: Identify platform from URL
- `get_analyzer()`: Get appropriate analyzer instance
- `list_by_category()`: Filter platforms by category

#### PlatformDefinition
Immutable data class defining a supported platform:
- `id`: Unique identifier
- `name`: Human-readable name
- `category`: Platform classification
- `url_patterns`: URL detection patterns
- `analyzer_class`: Analyzer implementation

### Supported Platforms

| Platform | Category | Key Metrics |
|----------|----------|-------------|
| Shopify | E-commerce | Liquid render time, app impact, CDN usage |
| Webflow | No-Code | Animation complexity, CMS loading, DOM size |
| Mendix | Low-Code | Microflow/nanoflow performance, N+1 queries |
| Wix | No-Code | Velo code execution, dataset performance |
| Generic | Generic | Common web performance metrics |

## Integration

The new platform system integrates with the existing `PlatformDetector` class
while maintaining backward compatibility:

```python
# New usage - direct registry access
from lowcode_scanner.platforms import PlatformRegistry
analyzer = PlatformRegistry.get_analyzer("https://store.myshopify.com")

# Or via updated PlatformDetector
from lowcode_scanner.core import PlatformDetector
detector = PlatformDetector()
analyzer = detector.get_platform_analyzer("https://store.myshopify.com")
```

## Testing

Platform analyzers include comprehensive unit tests covering:
- URL pattern detection
- Signature identification
- Metric extraction
- Bottleneck detection
- Recommendation generation

Run tests with:
```bash
pytest tests/platforms/test_platform_analyzers.py -v
```

## Future Extensions

The architecture supports:
1. Plugin-based platform registration
2. Dynamic platform detection from page content
3. Custom metric definitions
4. Platform comparison reporting
5. Academic research categorization
