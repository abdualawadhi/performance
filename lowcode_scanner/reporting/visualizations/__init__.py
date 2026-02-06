"""
Visualization modules for performance reports.

This package provides advanced visualization capabilities:
- Advanced charts (waterfall, flame graphs, CDF, box plots)
- Chart.js integration
- SVG generation
"""

from .advanced_charts import (
    AdvancedChartGenerator,
    ChartType,
    TimingPhase,
    FlameNode,
    generate_waterfall_chart,
    generate_flame_graph,
    generate_cdf_chart,
    generate_box_plot,
    generate_correlation_heatmap,
)

__all__ = [
    "AdvancedChartGenerator",
    "ChartType",
    "TimingPhase",
    "FlameNode",
    "generate_waterfall_chart",
    "generate_flame_graph",
    "generate_cdf_chart",
    "generate_box_plot",
    "generate_correlation_heatmap",
]
