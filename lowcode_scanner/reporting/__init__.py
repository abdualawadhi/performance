"""
Reporting modules for Low-Code Performance Scanner.

This package provides comprehensive reporting capabilities:
- Executive Dashboard: Interactive HTML with score cards and charts
- Academic Reports: LaTeX-quality PDF reports
- Excel Export: Multi-sheet Excel with metadata
- Advanced Charts: Waterfall, flame graphs, CDF, box plots
"""

from .executive_dashboard import (
    ExecutiveDashboardGenerator,
    ScoreCard,
    DashboardConfig,
    generate_executive_dashboard,
)

from .academic_report_generator import (
    AcademicReportGenerator,
    StatisticalTable,
    Figure,
    Reference,
    generate_academic_report,
)

from .excel_export import (
    DataExporter,
    ExcelExportGenerator,
    ExportMetadata,
    export_all_formats,
    SCHEMA_VERSION,
)

from .visualizations.advanced_charts import (
    AdvancedChartGenerator,
    generate_waterfall_chart,
    generate_flame_graph,
    generate_cdf_chart,
    generate_box_plot,
    generate_correlation_heatmap,
)

__all__ = [
    # Executive Dashboard
    "ExecutiveDashboardGenerator",
    "ScoreCard",
    "DashboardConfig",
    "generate_executive_dashboard",
    
    # Academic Reports
    "AcademicReportGenerator",
    "StatisticalTable",
    "Figure",
    "Reference",
    "generate_academic_report",
    
    # Excel Export
    "DataExporter",
    "ExcelExportGenerator",
    "ExportMetadata",
    "export_all_formats",
    "SCHEMA_VERSION",
    
    # Advanced Charts
    "AdvancedChartGenerator",
    "generate_waterfall_chart",
    "generate_flame_graph",
    "generate_cdf_chart",
    "generate_box_plot",
    "generate_correlation_heatmap",
]
