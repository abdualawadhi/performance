"""
Report Configuration Module

This module handles report configuration, customization, and template management
for comprehensive performance reports.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ReportTheme(Enum):
    """Available report themes."""
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    DEVELOPER = "developer"
    CUSTOM = "custom"


class ChartType(Enum):
    """Available chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    RADAR = "radar"
    GAUGE = "gauge"
    WATERFALL = "waterfall"
    HEATMAP = "heatmap"
    TIMELINE = "timeline"
    SCATTER = "scatter"


@dataclass
class ReportSection:
    """Configuration for a report section."""
    id: str
    title: str
    enabled: bool = True
    order: int = 0
    chart_types: List[ChartType] = None
    custom_html: str = ""
    data_source: str = ""
    
    def __post_init__(self):
        if self.chart_types is None:
            self.chart_types = []


@dataclass
class ReportTemplate:
    """Configuration for a report template."""
    id: str
    name: str
    theme: ReportTheme
    description: str
    sections: List[ReportSection]
    logo_path: str = ""
    company_name: str = ""
    report_footer: str = ""
    custom_css: str = ""
    custom_js: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class VisualizationConfig:
    """Configuration for visualizations."""
    chart_library: str = "chartjs"  # chartjs, plotly, d3
    default_colors: List[str] = None
    color_scheme: str = "default"
    animations_enabled: bool = True
    interactive_charts: bool = True
    responsive_design: bool = True
    
    def __post_init__(self):
        if self.default_colors is None:
            self.default_colors = [
                "#667eea", "#764ba2", "#10b981", "#f59e0b", 
                "#ef4444", "#3b82f6", "#8b5cf6", "#06b6d4"
            ]


@dataclass
class ReportBranding:
    """Configuration for report branding."""
    logo_url: str = ""
    company_name: str = ""
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: str = "#10b981"
    background_color: str = "#ffffff"
    text_color: str = "#374151"
    font_family: str = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"


@dataclass
class ExportSettings:
    """Configuration for export options."""
    formats: List[str] = None  # html, pdf, json, csv, xlsx
    include_raw_data: bool = True
    include_charts: bool = True
    include_recommendations: bool = True
    watermark: str = ""
    page_size: str = "A4"
    orientation: str = "portrait"
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = ["html", "pdf", "json"]


class ReportConfigManager:
    """Manages report configuration and templates."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.templates = {}
        self.visualization_configs = {}
        self.branding_configs = {}
        self.export_settings = {}
        
        self._load_default_templates()
        self._load_default_configs()
    
    def _load_default_templates(self):
        """Load default report templates."""
        
        # Professional Template
        professional_template = ReportTemplate(
            id="professional",
            name="Professional Report",
            theme=ReportTheme.PROFESSIONAL,
            description="Comprehensive professional report with executive summary and detailed analysis",
            sections=[
                ReportSection("executive_summary", "Executive Summary", order=1),
                ReportSection("core_web_vitals", "Core Web Vitals", order=2),
                ReportSection("performance_matrix", "Performance Matrix", order=3),
                ReportSection("network_analysis", "Network Analysis", order=4),
                ReportSection("resource_breakdown", "Resource Breakdown", order=5),
                ReportSection("optimization_recommendations", "Optimization Recommendations", order=6),
                ReportSection("technical_analysis", "Technical Analysis", order=7),
                ReportSection("benchmark_comparison", "Industry Benchmark Comparison", order=8)
            ],
            custom_css="""
                .professional-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem 0;
                }
                .executive-card {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                    margin: 1rem 0;
                }
            """
        )
        
        # Technical Template
        technical_template = ReportTemplate(
            id="technical",
            name="Technical Deep Dive",
            theme=ReportTheme.TECHNICAL,
            description="Technical report focused on detailed metrics, bottleneck analysis, and optimization opportunities",
            sections=[
                ReportSection("performance_matrix", "Detailed Performance Matrix", order=1),
                ReportSection("waterfall_analysis", "Waterfall Analysis", order=2),
                ReportSection("bottleneck_analysis", "Performance Bottlenecks", order=3),
                ReportSection("memory_analysis", "Memory Usage Analysis", order=4),
                ReportSection("network_timing", "Network Timing Analysis", order=5),
                ReportSection("rendering_pipeline", "Rendering Pipeline Analysis", order=6),
                ReportSection("optimization_opportunities", "Technical Optimization", order=7),
                ReportSection("code_analysis", "Code Performance Analysis", order=8)
            ],
            custom_css="""
                .technical-section {
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 1.5rem;
                    margin: 1rem 0;
                }
                .metrics-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1rem 0;
                }
                .metrics-table th,
                .metrics-table td {
                    padding: 0.75rem;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }
            """
        )
        
        # Executive Template
        executive_template = ReportTemplate(
            id="executive",
            name="Executive Summary",
            theme=ReportTheme.EXECUTIVE,
            description="Executive-focused report with high-level insights and business impact analysis",
            sections=[
                ReportSection("executive_dashboard", "Executive Dashboard", order=1),
                ReportSection("business_impact", "Business Impact Assessment", order=2),
                ReportSection("key_findings", "Key Findings", order=3),
                ReportSection("priority_recommendations", "Priority Recommendations", order=4),
                ReportSection("cost_benefit_analysis", "Cost-Benefit Analysis", order=5)
            ],
            custom_css="""
                .executive-summary {
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 12px;
                    margin: 1rem 0;
                }
                .business-metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin: 1.5rem 0;
                }
                .metric-card {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
            """
        )
        
        # Developer Template
        developer_template = ReportTemplate(
            id="developer",
            name="Developer Report",
            theme=ReportTheme.DEVELOPER,
            description="Developer-focused report with detailed technical implementation guidance",
            sections=[
                ReportSection("performance_metrics", "Performance Metrics", order=1),
                ReportSection("code_quality", "Code Quality Analysis", order=2),
                ReportSection("resource_optimization", "Resource Optimization", order=3),
                ReportSection("caching_strategy", "Caching Strategy", order=4),
                ReportSection("progressive_enhancement", "Progressive Enhancement", order=5),
                ReportSection("monitoring_setup", "Monitoring Setup", order=6),
                ReportSection("implementation_guide", "Implementation Guide", order=7)
            ],
            custom_css="""
                .developer-section {
                    background: #1f2937;
                    color: #f9fafb;
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                }
                .code-block {
                    background: #374151;
                    color: #e5e7eb;
                    padding: 1rem;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    overflow-x: auto;
                }
                .api-endpoint {
                    background: #059669;
                    color: white;
                    padding: 0.5rem;
                    border-radius: 4px;
                    font-family: monospace;
                }
            """
        )
        
        self.templates = {
            "professional": professional_template,
            "technical": technical_template,
            "executive": executive_template,
            "developer": developer_template
        }
    
    def _load_default_configs(self):
        """Load default configuration settings."""
        
        # Default visualization config
        self.visualization_configs["default"] = VisualizationConfig(
            chart_library="chartjs",
            color_scheme="professional",
            animations_enabled=True,
            interactive_charts=True,
            responsive_design=True
        )
        
        # Technical visualization config
        self.visualization_configs["technical"] = VisualizationConfig(
            chart_library="plotly",
            color_scheme="technical",
            animations_enabled=False,
            interactive_charts=True,
            responsive_design=True
        )
        
        # Default branding config
        self.branding_configs["default"] = ReportBranding(
            company_name="Performance Analytics",
            primary_color="#667eea",
            secondary_color="#764ba2",
            accent_color="#10b981"
        )
        
        # Default export settings
        self.export_settings["default"] = ExportSettings(
            formats=["html", "pdf", "json", "csv"],
            include_raw_data=True,
            include_charts=True,
            include_recommendations=True,
            watermark="Generated by LowCode Performance Scanner"
        )
        
        # Professional export settings
        self.export_settings["professional"] = ExportSettings(
            formats=["html", "pdf"],
            include_raw_data=False,
            include_charts=True,
            include_recommendations=True,
            watermark="Confidential - Performance Analysis Report"
        )
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get a report template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {
                "id": template.id,
                "name": template.name,
                "theme": template.theme.value,
                "description": template.description,
                "sections_count": len(template.sections)
            }
            for template in self.templates.values()
        ]
    
    def create_custom_template(self, template: ReportTemplate):
        """Create a custom report template."""
        self.templates[template.id] = template
        self.save_template(template)
    
    def update_template(self, template_id: str, updates: Dict[str, Any]):
        """Update an existing template."""
        if template_id in self.templates:
            template = self.templates[template_id]
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
    
    def delete_template(self, template_id: str):
        """Delete a custom template."""
        if template_id in self.templates and template_id not in ["professional", "technical", "executive", "developer"]:
            del self.templates[template_id]
            template_file = self.config_dir / f"{template_id}_template.json"
            if template_file.exists():
                template_file.unlink()
    
    def get_visualization_config(self, config_id: str = "default") -> Optional[VisualizationConfig]:
        """Get visualization configuration."""
        return self.visualization_configs.get(config_id)
    
    def update_visualization_config(self, config_id: str, updates: Dict[str, Any]):
        """Update visualization configuration."""
        if config_id in self.visualization_configs:
            config = self.visualization_configs[config_id]
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    def get_branding_config(self, config_id: str = "default") -> Optional[ReportBranding]:
        """Get branding configuration."""
        return self.branding_configs.get(config_id)
    
    def update_branding_config(self, config_id: str, updates: Dict[str, Any]):
        """Update branding configuration."""
        if config_id in self.branding_configs:
            config = self.branding_configs[config_id]
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    def get_export_settings(self, settings_id: str = "default") -> Optional[ExportSettings]:
        """Get export settings."""
        return self.export_settings.get(settings_id)
    
    def update_export_settings(self, settings_id: str, updates: Dict[str, Any]):
        """Update export settings."""
        if settings_id in self.export_settings:
            settings = self.export_settings[settings_id]
            for key, value in updates.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
    
    def save_template(self, template: ReportTemplate):
        """Save template to file."""
        template_file = self.config_dir / f"{template.id}_template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2)
    
    def load_template(self, template_id: str):
        """Load template from file."""
        template_file = self.config_dir / f"{template_id}_template.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                template_dict = json.load(f)
                
                # Convert section data back to ReportSection objects
                sections = []
                for section_dict in template_dict.get('sections', []):
                    section = ReportSection(**section_dict)
                    sections.append(section)
                template_dict['sections'] = sections
                
                template = ReportTemplate(**template_dict)
                self.templates[template_id] = template
    
    def export_configuration(self, output_file: str):
        """Export all configurations to a file."""
        config_export = {
            "templates": {tid: template.to_dict() for tid, template in self.templates.items()},
            "visualization_configs": {kid: asdict(config) for kid, config in self.visualization_configs.items()},
            "branding_configs": {bid: asdict(config) for bid, config in self.branding_configs.items()},
            "export_settings": {eid: asdict(settings) for eid, settings in self.export_settings.items()}
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_export, f, indent=2)
    
    def import_configuration(self, input_file: str):
        """Import configurations from a file."""
        with open(input_file, 'r', encoding='utf-8') as f:
            config_import = json.load(f)
        
        # Import templates
        for tid, template_dict in config_import.get("templates", {}).items():
            sections = []
            for section_dict in template_dict.get('sections', []):
                section = ReportSection(**section_dict)
                sections.append(section)
            template_dict['sections'] = sections
            
            template = ReportTemplate(**template_dict)
            self.templates[tid] = template
        
        # Import other configs
        for config_dict in config_import.get("visualization_configs", {}).values():
            config = VisualizationConfig(**config_dict)
            self.visualization_configs[config_dict.get('id', 'default')] = config
    
    def get_report_css_theme(self, theme: ReportTheme, custom_css: str = "") -> str:
        """Generate CSS for report theme."""
        base_css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        """
        
        theme_css = ""
        if theme == ReportTheme.PROFESSIONAL:
            theme_css = """
            .report-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem 0;
            }
            """
        elif theme == ReportTheme.TECHNICAL:
            theme_css = """
            .report-header {
                background: #1f2937;
                color: #f9fafb;
                padding: 2rem 0;
            }
            .technical-section {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 1.5rem;
                margin: 1rem 0;
            }
            """
        elif theme == ReportTheme.EXECUTIVE:
            theme_css = """
            .report-header {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 2rem 0;
            }
            .executive-summary {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 2rem;
                border-radius: 12px;
                margin: 1rem 0;
            }
            """
        
        return f"{base_css}\n{theme_css}\n{custom_css}"
    
    def generate_report_config_summary(self) -> Dict[str, Any]:
        """Generate a summary of current configuration."""
        return {
            "templates": {
                "count": len(self.templates),
                "available": list(self.templates.keys())
            },
            "visualization_configs": {
                "count": len(self.visualization_configs),
                "available": list(self.visualization_configs.keys())
            },
            "branding_configs": {
                "count": len(self.branding_configs),
                "available": list(self.branding_configs.keys())
            },
            "export_settings": {
                "count": len(self.export_settings),
                "available": list(self.export_settings.keys())
            }
        }