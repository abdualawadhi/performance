"""
Advanced Visualization Charts

This module provides advanced performance visualizations:
- Waterfall diagrams showing DNS, TCP, SSL, TTFB phases
- Flame graphs for performance trace visualization
- Cumulative distribution charts for percentile rankings
- Box plots with quartiles and outliers
- Correlation matrix heatmaps
"""

import json
import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ChartType(Enum):
    """Types of advanced charts."""
    WATERFALL = "waterfall"
    FLAME_GRAPH = "flame_graph"
    CDF = "cumulative_distribution"
    BOX_PLOT = "box_plot"
    CORRELATION_HEATMAP = "correlation_heatmap"


@dataclass
class TimingPhase:
    """A timing phase for waterfall charts."""
    name: str
    duration_ms: float
    start_ms: float
    color: str
    category: str = "network"


@dataclass
class FlameNode:
    """A node in a flame graph."""
    name: str
    duration_ms: float
    start_ms: float
    children: List["FlameNode"] = None
    color: str = "#3b82f6"
    category: str = "script"
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class AdvancedChartGenerator:
    """
    Generator for advanced performance visualization charts.
    """
    
    def __init__(self):
        self.color_palette = {
            "dns": "#3b82f6",      # Blue
            "tcp": "#22c55e",      # Green
            "ssl": "#eab308",      # Yellow
            "ttfb": "#f97316",     # Orange
            "download": "#8b5cf6", # Purple
            "processing": "#ef4444", # Red
            "rendering": "#06b6d4", # Cyan
            "painting": "#ec4899", # Pink
            "scripting": "#6366f1", # Indigo
        }
    
    def generate_waterfall(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate waterfall chart data for resource loading.
        
        Args:
            resources: List of resource timing data
            
        Returns:
            Chart data dictionary
        """
        phases = []
        
        for resource in resources:
            start = resource.get('start_time_ms', 0)
            
            # DNS phase
            if resource.get('dns_time_ms', 0) > 0:
                phases.append(TimingPhase(
                    name=f"{resource.get('name', 'Resource')} - DNS",
                    duration_ms=resource['dns_time_ms'],
                    start_ms=start,
                    color=self.color_palette['dns'],
                    category='dns'
                ))
            
            # TCP phase
            tcp_start = start + resource.get('dns_time_ms', 0)
            if resource.get('tcp_time_ms', 0) > 0:
                phases.append(TimingPhase(
                    name=f"{resource.get('name', 'Resource')} - TCP",
                    duration_ms=resource['tcp_time_ms'],
                    start_ms=tcp_start,
                    color=self.color_palette['tcp'],
                    category='tcp'
                ))
            
            # SSL phase
            ssl_start = tcp_start + resource.get('tcp_time_ms', 0)
            if resource.get('ssl_time_ms', 0) > 0:
                phases.append(TimingPhase(
                    name=f"{resource.get('name', 'Resource')} - SSL",
                    duration_ms=resource['ssl_time_ms'],
                    start_ms=ssl_start,
                    color=self.color_palette['ssl'],
                    category='ssl'
                ))
            
            # TTFB phase
            ttfb_start = ssl_start + resource.get('ssl_time_ms', 0)
            if resource.get('ttfb_ms', 0) > 0:
                phases.append(TimingPhase(
                    name=f"{resource.get('name', 'Resource')} - TTFB",
                    duration_ms=resource['ttfb_ms'],
                    start_ms=ttfb_start,
                    color=self.color_palette['ttfb'],
                    category='ttfb'
                ))
            
            # Download phase
            download_start = ttfb_start + resource.get('ttfb_ms', 0)
            if resource.get('download_time_ms', 0) > 0:
                phases.append(TimingPhase(
                    name=f"{resource.get('name', 'Resource')} - Download",
                    duration_ms=resource['download_time_ms'],
                    start_ms=download_start,
                    color=self.color_palette['download'],
                    category='download'
                ))
        
        return {
            "type": "waterfall",
            "phases": [
                {
                    "name": p.name,
                    "duration_ms": p.duration_ms,
                    "start_ms": p.start_ms,
                    "end_ms": p.start_ms + p.duration_ms,
                    "color": p.color,
                    "category": p.category
                }
                for p in phases
            ],
            "categories": list(self.color_palette.keys())[:5],
            "colors": list(self.color_palette.values())[:5]
        }
    
    def generate_flame_graph(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate flame graph data from performance traces.
        
        Args:
            traces: List of performance trace events
            
        Returns:
            Hierarchical flame graph data
        """
        # Build hierarchical structure
        root = FlameNode(
            name="Total",
            duration_ms=0,
            start_ms=0,
            color="#1f2937"
        )
        
        # Group traces by category
        categories = {}
        for trace in traces:
            category = trace.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(trace)
        
        # Create category nodes
        total_duration = 0
        for category, cat_traces in categories.items():
            cat_duration = sum(t.get('duration_ms', 0) for t in cat_traces)
            total_duration = max(total_duration, max((t.get('start_ms', 0) + t.get('duration_ms', 0) for t in cat_traces), default=0))
            
            cat_node = FlameNode(
                name=category.title(),
                duration_ms=cat_duration,
                start_ms=min((t.get('start_ms', 0) for t in cat_traces), default=0),
                color=self._get_category_color(category)
            )
            
            # Add individual trace nodes
            for trace in cat_traces:
                trace_node = FlameNode(
                    name=trace.get('name', 'Unknown')[:30],
                    duration_ms=trace.get('duration_ms', 0),
                    start_ms=trace.get('start_ms', 0),
                    color=self._get_category_color(category)
                )
                cat_node.children.append(trace_node)
            
            root.children.append(cat_node)
        
        root.duration_ms = total_duration
        
        return self._flame_node_to_dict(root)
    
    def _get_category_color(self, category: str) -> str:
        """Get color for a category."""
        color_map = {
            "scripting": self.color_palette['scripting'],
            "rendering": self.color_palette['rendering'],
            "painting": self.color_palette['painting'],
            "network": self.color_palette['download'],
            "parsing": "#84cc16",
            "other": "#9ca3af"
        }
        return color_map.get(category.lower(), "#9ca3af")
    
    def _flame_node_to_dict(self, node: FlameNode) -> Dict[str, Any]:
        """Convert flame node to dictionary."""
        return {
            "name": node.name,
            "duration_ms": node.duration_ms,
            "start_ms": node.start_ms,
            "color": node.color,
            "category": node.category,
            "children": [self._flame_node_to_dict(child) for child in node.children]
        }
    
    def generate_cdf(self, data: List[float], label: str = "Metric") -> Dict[str, Any]:
        """
        Generate cumulative distribution function data.
        
        Args:
            data: List of values
            label: Label for the metric
            
        Returns:
            CDF chart data
        """
        if not data:
            return {"type": "cdf", "data": [], "percentiles": {}}
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        # Calculate CDF points
        cdf_points = []
        for i, value in enumerate(sorted_data):
            percentile = (i + 1) / n * 100
            cdf_points.append({
                "value": value,
                "percentile": percentile,
                "cumulative_probability": (i + 1) / n
            })
        
        # Calculate key percentiles
        percentiles = {
            "p50": self._percentile(sorted_data, 50),
            "p75": self._percentile(sorted_data, 75),
            "p90": self._percentile(sorted_data, 90),
            "p95": self._percentile(sorted_data, 95),
            "p99": self._percentile(sorted_data, 99),
            "mean": statistics.mean(sorted_data),
            "median": statistics.median(sorted_data),
            "std_dev": statistics.stdev(sorted_data) if len(sorted_data) > 1 else 0
        }
        
        return {
            "type": "cdf",
            "label": label,
            "data": cdf_points,
            "percentiles": percentiles,
            "min": min(sorted_data),
            "max": max(sorted_data),
            "count": len(sorted_data)
        }
    
    def _percentile(self, sorted_data: List[float], p: float) -> float:
        """Calculate percentile value."""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)
    
    def generate_box_plot(self, data_groups: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Generate box plot data with quartiles and outliers.
        
        Args:
            data_groups: Dictionary mapping group names to lists of values
            
        Returns:
            Box plot data
        """
        boxes = []
        
        for name, data in data_groups.items():
            if not data:
                continue
            
            sorted_data = sorted(data)
            n = len(sorted_data)
            
            # Calculate quartiles
            q1 = self._percentile(sorted_data, 25)
            q2 = self._percentile(sorted_data, 50)
            q3 = self._percentile(sorted_data, 75)
            iqr = q3 - q1
            
            # Calculate whiskers
            lower_whisker = max(min(sorted_data), q1 - 1.5 * iqr)
            upper_whisker = min(max(sorted_data), q3 + 1.5 * iqr)
            
            # Find outliers
            outliers = [x for x in sorted_data if x < lower_whisker or x > upper_whisker]
            
            boxes.append({
                "name": name,
                "min": min(sorted_data),
                "max": max(sorted_data),
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "iqr": iqr,
                "lower_whisker": lower_whisker,
                "upper_whisker": upper_whisker,
                "outliers": outliers,
                "outlier_count": len(outliers),
                "mean": statistics.mean(sorted_data),
                "std_dev": statistics.stdev(sorted_data) if len(sorted_data) > 1 else 0,
                "count": n
            })
        
        return {
            "type": "box_plot",
            "boxes": boxes
        }
    
    def generate_correlation_heatmap(self, metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Generate correlation matrix heatmap data.
        
        Args:
            metrics: Dictionary mapping metric names to lists of values
            
        Returns:
            Correlation heatmap data
        """
        metric_names = list(metrics.keys())
        n_metrics = len(metric_names)
        
        if n_metrics < 2:
            return {"type": "correlation_heatmap", "labels": [], "matrix": []}
        
        # Calculate correlation matrix
        matrix = []
        for i, name1 in enumerate(metric_names):
            row = []
            for j, name2 in enumerate(metric_names):
                if i == j:
                    row.append(1.0)
                else:
                    corr = self._pearson_correlation(
                        metrics[name1],
                        metrics[name2]
                    )
                    row.append(corr)
            matrix.append(row)
        
        return {
            "type": "correlation_heatmap",
            "labels": metric_names,
            "matrix": matrix,
            "interpretation": self._interpret_correlations(matrix, metric_names)
        }
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = math.sqrt(sum((xi - mean_x) ** 2 for xi in x)) * \
                     math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _interpret_correlations(self, matrix: List[List[float]], 
                                labels: List[str]) -> List[Dict[str, Any]]:
        """Interpret correlation matrix and find significant relationships."""
        interpretations = []
        
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                corr = matrix[i][j]
                
                if abs(corr) > 0.7:
                    strength = "Strong"
                elif abs(corr) > 0.5:
                    strength = "Moderate"
                elif abs(corr) > 0.3:
                    strength = "Weak"
                else:
                    continue
                
                direction = "positive" if corr > 0 else "negative"
                
                interpretations.append({
                    "metric1": labels[i],
                    "metric2": labels[j],
                    "correlation": round(corr, 3),
                    "strength": strength,
                    "direction": direction,
                    "description": f"{strength} {direction} correlation between {labels[i]} and {labels[j]}"
                })
        
        return sorted(interpretations, key=lambda x: abs(x['correlation']), reverse=True)
    
    def generate_performance_comparison(self, current: Dict[str, float],
                                       baseline: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate comparison chart data between current and baseline.
        
        Args:
            current: Current metric values
            baseline: Baseline metric values
            
        Returns:
            Comparison chart data
        """
        metrics = set(current.keys()) | set(baseline.keys())
        
        comparison = []
        for metric in sorted(metrics):
            curr_val = current.get(metric, 0)
            base_val = baseline.get(metric, 0)
            
            if base_val != 0:
                change_pct = ((curr_val - base_val) / base_val) * 100
            else:
                change_pct = 0 if curr_val == 0 else 100
            
            comparison.append({
                "metric": metric,
                "current": curr_val,
                "baseline": base_val,
                "absolute_change": curr_val - base_val,
                "percentage_change": change_pct,
                "improved": change_pct < 0 if metric in ["load_time", "lcp", "memory"] else change_pct > 0
            })
        
        return {
            "type": "comparison",
            "metrics": comparison,
            "overall_change": sum(c['percentage_change'] for c in comparison) / len(comparison) if comparison else 0
        }
    
    def generate_svg_waterfall(self, resources: List[Dict[str, Any]], 
                               width: int = 800, height: int = 400) -> str:
        """
        Generate SVG waterfall chart.
        
        Args:
            resources: Resource timing data
            width: SVG width
            height: SVG height
            
        Returns:
            SVG string
        """
        if not resources:
            return "<svg></svg>"
        
        # Calculate scale
        max_time = max(r.get('start_time_ms', 0) + r.get('duration_ms', 0) 
                      for r in resources)
        scale = (width - 150) / max_time if max_time > 0 else 1
        
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.resource-label { font-size: 10px; fill: #374151; }',
            '.phase-label { font-size: 8px; fill: white; text-anchor: middle; }',
            '</style>',
            '</defs>'
        ]
        
        y = 30
        bar_height = 20
        
        for resource in resources:
            name = resource.get('name', 'Resource')[:30]
            start = resource.get('start_time_ms', 0)
            duration = resource.get('duration_ms', 0)
            
            # Draw resource name
            svg_parts.append(f'<text x="10" y="{y + 14}" class="resource-label">{name}</text>')
            
            # Draw phases
            phases = [
                ('dns', resource.get('dns_time_ms', 0)),
                ('tcp', resource.get('tcp_time_ms', 0)),
                ('ssl', resource.get('ssl_time_ms', 0)),
                ('ttfb', resource.get('ttfb_ms', 0)),
                ('download', resource.get('download_time_ms', 0))
            ]
            
            x = 150 + start * scale
            for phase_name, phase_duration in phases:
                if phase_duration > 0:
                    phase_width = phase_duration * scale
                    color = self.color_palette.get(phase_name, '#9ca3af')
                    
                    svg_parts.append(
                        f'<rect x="{x}" y="{y}" width="{max(phase_width, 1)}" '
                        f'height="{bar_height}" fill="{color}" rx="2"/>'
                    )
                    
                    if phase_width > 30:
                        svg_parts.append(
                            f'<text x="{x + phase_width/2}" y="{y + 14}" '
                            f'class="phase-label">{phase_duration:.0f}</text>'
                        )
                    
                    x += phase_width
            
            y += 35
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)


# Convenience functions
def generate_waterfall_chart(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate waterfall chart data."""
    generator = AdvancedChartGenerator()
    return generator.generate_waterfall(resources)


def generate_flame_graph(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate flame graph data."""
    generator = AdvancedChartGenerator()
    return generator.generate_flame_graph(traces)


def generate_cdf_chart(data: List[float], label: str = "Metric") -> Dict[str, Any]:
    """Generate CDF chart data."""
    generator = AdvancedChartGenerator()
    return generator.generate_cdf(data, label)


def generate_box_plot(data_groups: Dict[str, List[float]]) -> Dict[str, Any]:
    """Generate box plot data."""
    generator = AdvancedChartGenerator()
    return generator.generate_box_plot(data_groups)


def generate_correlation_heatmap(metrics: Dict[str, List[float]]) -> Dict[str, Any]:
    """Generate correlation heatmap data."""
    generator = AdvancedChartGenerator()
    return generator.generate_correlation_heatmap(metrics)
