#!/usr/bin/env python3
"""
Comprehensive Reporting Demo Script

This script demonstrates the new comprehensive reporting capabilities of the
LowCode Performance Scanner, showing various report formats and analysis features.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from lowcode_scanner.reporting import (
    EnhancedReportingEngine,
    ReportConfigManager,
    ReportTheme,
    generate_comprehensive_report
)


class MockScanResult:
    """Mock scan result for demonstration purposes."""
    
    def __init__(self):
        self.performance_matrix = MockPerformanceMatrix()
        self.platform = "web"
        self.scan_id = "demo-scan-123"
    
    def __str__(self):
        return f"MockScanResult(id={self.scan_id})"


class MockPerformanceMatrix:
    """Mock performance matrix for demonstration."""
    
    def __init__(self):
        self.rows = [
            MockPerformanceRow("Homepage", 85.5, 3.2, 45.0, 1200, 2500, 3200, 0.12, 95.0, 45, 1250),
            MockPerformanceRow("Dashboard", 78.2, 4.1, 52.0, 1450, 3100, 4100, 0.18, 92.0, 62, 1680),
            MockPerformanceRow("Form Page", 82.1, 2.9, 38.0, 980, 2200, 2900, 0.08, 98.0, 32, 890),
            MockPerformanceRow("Search Results", 76.8, 3.7, 48.0, 1320, 2800, 3700, 0.15, 89.0, 58, 1420)
        ]
        self.overall_score = 80.7
    
    def __str__(self):
        return f"MockPerformanceMatrix(score={self.overall_score})"


class MockPerformanceRow:
    """Mock performance row for demonstration."""
    
    def __init__(self, scenario_name, score, load_time, memory, fcp, lcp, tti, cls, accessibility, requests, size):
        self.scenario = MockScenario(scenario_name)
        self.performance_score = score
        self.load_time_s = load_time
        self.memory_usage_max_mb = memory
        self.first_contentful_paint_ms = fcp
        self.largest_contentful_paint_ms = lcp
        self.time_to_interactive_ms = tti
        self.cumulative_layout_shift = cls
        self.accessibility_score = accessibility
        self.total_requests = requests
        self.total_size_kb = size
        self.key_observations = [
            f"Good performance for {scenario_name}",
            "Consider image optimization",
            "JavaScript bundle could be smaller"
        ]
    
    def __str__(self):
        return f"MockPerformanceRow(scenario={self.scenario.name}, score={self.performance_score})"


class MockScenario:
    """Mock scenario for demonstration."""
    
    def __init__(self, name):
        self.name = name
        self.display_name = name
    
    def __str__(self):
        return f"MockScenario({self.name})"


async def demonstrate_comprehensive_reporting():
    """Demonstrate the comprehensive reporting capabilities."""
    
    print("🚀 Comprehensive Reporting Demo")
    print("=" * 50)
    
    # Create mock scan result
    result = MockScanResult()
    url = "https://example-lowcode-app.com"
    session_name = "demo_comprehensive_report"
    output_dir = "demo_reports"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"📊 Target URL: {url}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🔍 Session ID: {session_name}")
    print()
    
    # Initialize enhanced reporting engine
    print("🔧 Initializing Enhanced Reporting Engine...")
    enhanced_engine = EnhancedReportingEngine()
    
    # Show available templates
    print("\n📋 Available Report Templates:")
    templates = enhanced_engine.config_manager.list_templates()
    for template in templates:
        print(f"  • {template['name']} ({template['id']}) - {template['description']}")
    
    # Generate comprehensive report with all features
    print("\n🎯 Generating Comprehensive Report...")
    print("  ✓ Executive Dashboard")
    print("  ✓ Core Web Vitals Analysis")
    print("  ✓ Performance Matrix")
    print("  ✓ Network Analysis")
    print("  ✓ Resource Breakdown")
    print("  ✓ Optimization Recommendations")
    print("  ✓ Technical Analysis")
    print("  ✓ Benchmark Comparison")
    print("  ✓ Interactive Visualizations")
    
    try:
        # Generate comprehensive report
        generated_files = await enhanced_engine.generate_comprehensive_report(
            result=result,
            url=url,
            session_name=session_name,
            output_dir=output_dir,
            template_id="professional",
            formats=["html", "json", "csv", "pdf"],
            include_raw_data=True,
            custom_branding={
                "company_name": "Demo Company",
                "primary_color": "#2563eb",
                "secondary_color": "#7c3aed"
            }
        )
        
        print("\n✅ Report Generation Complete!")
        print("\n📁 Generated Files:")
        for format_type, file_path in generated_files.items():
            print(f"  📄 {format_type.upper()}: {file_path}")
        
        # Show report summary
        print("\n📈 Report Summary:")
        print(f"  • Overall Performance Score: {result.performance_matrix.overall_score:.1f}/100")
        print(f"  • Test Scenarios: {len(result.performance_matrix.rows)}")
        print(f"  • Report Formats: {len(generated_files)}")
        print(f"  • Report Template: Professional")
        
        # Demonstrate different templates
        await demonstrate_different_templates(result, url, session_name, output_dir)
        
        # Demonstrate configuration options
        await demonstrate_configuration_options()
        
        print("\n🎉 Comprehensive Reporting Demo Complete!")
        print(f"\n📂 Check the '{output_dir}' directory for all generated reports.")
        
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()


async def demonstrate_different_templates(result, url, session_name, output_dir):
    """Demonstrate different report templates."""
    
    print("\n🎨 Demonstrating Different Report Templates...")
    
    templates_to_demo = ["technical", "executive", "developer"]
    
    for template_id in templates_to_demo:
        print(f"\n  🔧 Generating {template_id.title()} template...")
        try:
            output_subdir = Path(output_dir) / template_id
            output_subdir.mkdir(exist_ok=True)
            
            generated_files = await enhanced_reporting.generate_comprehensive_report(
                result=result,
                url=url,
                session_name=f"{session_name}_{template_id}",
                output_dir=str(output_subdir),
                template_id=template_id,
                formats=["html", "json"]
            )
            
            print(f"    ✅ {template_id.title()} template generated successfully")
            
        except Exception as e:
            print(f"    ❌ Error generating {template_id} template: {e}")


async def demonstrate_configuration_options():
    """Demonstrate configuration and customization options."""
    
    print("\n⚙️  Configuration & Customization Options:")
    
    # Show configuration summary
    config_summary = enhanced_reporting.config_manager.generate_report_config_summary()
    
    print(f"  📊 Available Templates: {config_summary['templates']['count']}")
    print(f"  🎨 Visualization Configs: {config_summary['visualization_configs']['count']}")
    print(f"  🎭 Branding Configs: {config_summary['branding_configs']['count']}")
    print(f"  📤 Export Settings: {config_summary['export_settings']['count']}")
    
    # Show visualization options
    viz_config = enhanced_reporting.config_manager.get_visualization_config()
    print(f"\n  📈 Chart Library: {viz_config.chart_library}")
    print(f"  🎯 Color Scheme: {viz_config.color_scheme}")
    print(f"  ✨ Animations: {'Enabled' if viz_config.animations_enabled else 'Disabled'}")
    print(f"  🔄 Interactive Charts: {'Yes' if viz_config.interactive_charts else 'No'}")
    
    # Show branding options
    branding = enhanced_reporting.config_manager.get_branding_config()
    print(f"\n  🏢 Company: {branding.company_name}")
    print(f"  🎨 Primary Color: {branding.primary_color}")
    print(f"  🌈 Accent Color: {branding.accent_color}")
    
    # Show export options
    export_settings = enhanced_reporting.config_manager.get_export_settings()
    print(f"\n  📋 Available Formats: {', '.join(export_settings.formats)}")
    print(f"  📊 Include Raw Data: {'Yes' if export_settings.include_raw_data else 'No'}")
    print(f"  🖼️  Include Charts: {'Yes' if export_settings.include_charts else 'No'}")


def demonstrate_simple_api():
    """Demonstrate the simple API for backward compatibility."""
    
    print("\n🔄 Simple API (Backward Compatibility)")
    
    # Create mock result
    result = MockScanResult()
    url = "https://example-lowcode-app.com"
    session_name = "demo_simple_api"
    output_dir = "demo_reports/simple_api"
    
    try:
        # Use the simple generate_comprehensive_report function
        generated_files = generate_comprehensive_report(
            result=result,
            url=url,
            session_name=session_name,
            output_dir=output_dir,
            template_id="professional",
            formats=["html", "json"]
        )
        
        print("  ✅ Simple API call successful")
        print(f"  📁 Generated {len(generated_files)} files")
        
    except Exception as e:
        print(f"  ❌ Simple API error: {e}")


def show_report_examples():
    """Show examples of report content."""
    
    print("\n📋 Report Content Examples:")
    
    # Executive Summary Example
    print("\n  📊 Executive Summary Preview:")
    print("    • Overall Performance: 80.7/100 (Better than 75% of websites)")
    print("    • Core Web Vitals: LCP 2.8s (Needs Improvement), FID 75ms (Good)")
    print("    • Key Findings:")
    print("      - Image optimization could reduce LCP by 30-40%")
    print("      - JavaScript bundle size impacts performance")
    print("      - Good accessibility scores across all pages")
    
    # Technical Analysis Example
    print("\n  🔧 Technical Analysis Preview:")
    print("    • Loading Performance: 82/100")
    print("    • Interactivity: 78/100")
    print("    • Visual Stability: 85/100")
    print("    • Resource Efficiency: 75/100")
    
    # Optimization Recommendations Example
    print("\n  🎯 Optimization Roadmap Preview:")
    print("    • High Priority: Optimize hero images (1-2 weeks)")
    print("    • Medium Priority: Implement code splitting (2-4 weeks)")
    print("    • Quick Win: Enable browser caching (3-5 days)")
    
    # Benchmark Comparison Example
    print("\n  📈 Industry Benchmark Preview:")
    print("    • Performance Score: 80.7 vs Industry Average: 70")
    print("    • LCP: 2.8s vs Industry Average: 3.2s")
    print("    • Requests: 49 vs Industry Average: 65")
    print("    • Page Size: 1.3MB vs Industry Average: 2.1MB")


def create_sample_data_files():
    """Create sample data files for demonstration."""
    
    print("\n📁 Creating Sample Data Files...")
    
    # Create sample performance data
    sample_data = {
        "scan_results": [
            {
                "url": "https://example-app.com",
                "timestamp": "2024-01-15T10:30:00Z",
                "performance_score": 85.7,
                "lcp_ms": 2800,
                "fid_ms": 75,
                "cls_score": 0.12,
                "accessibility_score": 95,
                "total_requests": 45,
                "page_size_kb": 1250
            },
            {
                "url": "https://example-app.com/dashboard",
                "timestamp": "2024-01-15T10:35:00Z", 
                "performance_score": 78.2,
                "lcp_ms": 3100,
                "fid_ms": 120,
                "cls_score": 0.18,
                "accessibility_score": 92,
                "total_requests": 62,
                "page_size_kb": 1680
            }
        ],
        "optimization_opportunities": [
            {
                "category": "Image Optimization",
                "impact_score": 8.5,
                "potential_savings": "30-50%",
                "effort": "Low",
                "timeline": "1-2 weeks"
            },
            {
                "category": "JavaScript Optimization",
                "impact_score": 7.5,
                "potential_savings": "20-30%",
                "effort": "Medium",
                "timeline": "2-4 weeks"
            }
        ],
        "benchmark_comparison": {
            "overall_percentile": 75,
            "comparisons": {
                "performance_score": {"current_value": 85.7, "percentile": 80},
                "lcp_ms": {"current_value": 2800, "percentile": 70}
            }
        }
    }
    
    # Save sample data
    sample_file = Path("demo_reports/sample_data.json")
    sample_file.parent.mkdir(exist_ok=True)
    
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"  ✅ Sample data saved to: {sample_file}")


async def main():
    """Main demo function."""
    
    print("🎯 LowCode Performance Scanner - Comprehensive Reporting Demo")
    print("=" * 70)
    
    try:
        # Create sample data files
        create_sample_data_files()
        
        # Show report content examples
        show_report_examples()
        
        # Demonstrate simple API
        demonstrate_simple_api()
        
        # Run comprehensive demonstration
        await demonstrate_comprehensive_reporting()
        
        print("\n" + "=" * 70)
        print("🎉 Demo Complete! Explore the generated reports to see the comprehensive analysis.")
        print("\nNext Steps:")
        print("1. Open the HTML reports in your browser for interactive experience")
        print("2. Check the JSON files for detailed technical data")
        print("3. Import CSV files into Excel for further analysis")
        print("4. Try different templates and configurations")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())