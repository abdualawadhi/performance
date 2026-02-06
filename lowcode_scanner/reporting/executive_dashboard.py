"""
Executive Dashboard HTML Report Generator

This module generates interactive executive dashboards with:
- Score cards with color-coded severity (red <50, yellow 50-70, green 70-90, blue 90+)
- Waterfall charts for resource loading using Chart.js
- Radar charts for multi-dimensional performance
- Heatmaps for scenario × metric matrices
- Memory usage time-series charts
- Benchmark percentile comparisons
- Before/after comparison views
"""

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class ScoreCard:
    """A score card for the executive dashboard."""
    title: str
    score: float
    subtitle: str = ""
    trend: Optional[float] = None  # Percentage change
    target: float = 90.0
    
    @property
    def color(self) -> str:
        """Get color based on 4-color severity system."""
        if self.score >= 90:
            return "#3b82f6"  # Blue
        elif self.score >= 70:
            return "#22c55e"  # Green
        elif self.score >= 50:
            return "#eab308"  # Yellow
        else:
            return "#ef4444"  # Red
    
    @property
    def bg_color(self) -> str:
        """Get background color."""
        if self.score >= 90:
            return "#eff6ff"  # Blue light
        elif self.score >= 70:
            return "#f0fdf4"  # Green light
        elif self.score >= 50:
            return "#fefce8"  # Yellow light
        else:
            return "#fef2f2"  # Red light
    
    @property
    def severity(self) -> str:
        """Get severity label."""
        if self.score >= 90:
            return "Excellent"
        elif self.score >= 70:
            return "Good"
        elif self.score >= 50:
            return "Needs Improvement"
        else:
            return "Critical"
    
    @property
    def icon(self) -> str:
        """Get icon based on severity."""
        if self.score >= 90:
            return "🌟"
        elif self.score >= 70:
            return "✅"
        elif self.score >= 50:
            return "⚠️"
        else:
            return "🚨"


@dataclass
class DashboardConfig:
    """Configuration for the executive dashboard."""
    title: str = "Performance Executive Dashboard"
    subtitle: str = ""
    show_benchmarks: bool = True
    show_comparisons: bool = True
    show_heatmap: bool = True
    show_waterfall: bool = True
    show_radar: bool = True
    show_memory_timeline: bool = True
    primary_color: str = "#3b82f6"


class ExecutiveDashboardGenerator:
    """
    Generates interactive executive dashboards with rich visualizations.
    """
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.chart_colors = ["#3b82f6", "#22c55e", "#eab308", "#ef4444", "#8b5cf6", "#f97316"]
    
    def generate_dashboard(self, result, url: str, session_name: str,
                          comparison_result=None) -> str:
        """
        Generate a complete executive dashboard HTML.
        
        Args:
            result: The scan result to visualize
            url: URL that was scanned
            session_name: Name of the session
            comparison_result: Optional previous result for comparison
            
        Returns:
            HTML string
        """
        # Extract metrics
        overall_score = getattr(result.performance_matrix, 'overall_score', 0)
        platform = getattr(result, 'platform', 'generic')
        platform_str = platform.value if hasattr(platform, 'value') else str(platform)
        
        # Create score cards
        score_cards = self._create_score_cards(result)
        
        # Generate charts data
        radar_data = self._generate_radar_data(result)
        heatmap_data = self._generate_heatmap_data(result)
        memory_timeline_data = self._generate_memory_timeline_data(result)
        waterfall_data = self._generate_waterfall_data(result)
        comparison_data = self._generate_comparison_data(result, comparison_result)
        benchmark_data = self._generate_benchmark_data(result)
        
        # Build HTML
        return self._build_html(
            url=url,
            session_name=session_name,
            platform=platform_str,
            score_cards=score_cards,
            radar_data=radar_data,
            heatmap_data=heatmap_data,
            memory_timeline_data=memory_timeline_data,
            waterfall_data=waterfall_data,
            comparison_data=comparison_data,
            benchmark_data=benchmark_data,
            result=result
        )
    
    def _create_score_cards(self, result) -> List[ScoreCard]:
        """Create score cards from result data."""
        cards = []
        
        # Overall score
        overall = getattr(result.performance_matrix, 'overall_score', 0)
        cards.append(ScoreCard(
            title="Overall Performance",
            score=overall,
            subtitle="Aggregate score across all metrics",
            target=90.0
        ))
        
        # Scenario scores
        rows = getattr(result.performance_matrix, 'rows', [])
        for row in rows[:4]:  # Top 4 scenarios
            score = getattr(row, 'performance_score', 0)
            scenario_name = getattr(row.scenario, 'display_name', str(row.scenario))
            cards.append(ScoreCard(
                title=scenario_name,
                score=score,
                subtitle=f"Scenario performance",
                target=85.0
            ))
        
        # Core Web Vitals scores
        if rows:
            row = rows[0]
            lcp = getattr(row, 'largest_contentful_paint_ms', 0)
            lcp_score = max(0, 100 - (lcp - 2500) * 0.02) if lcp > 2500 else 100
            cards.append(ScoreCard(
                title="LCP Score",
                score=min(100, lcp_score),
                subtitle=f"LCP: {lcp:.0f}ms",
                target=90.0
            ))
            
            cls = getattr(row, 'cumulative_layout_shift', 0)
            cls_score = max(0, 100 - cls * 400)
            cards.append(ScoreCard(
                title="CLS Score",
                score=min(100, cls_score),
                subtitle=f"CLS: {cls:.3f}",
                target=90.0
            ))
        
        return cards
    
    def _generate_radar_data(self, result) -> Dict[str, Any]:
        """Generate data for radar chart."""
        rows = getattr(result.performance_matrix, 'rows', [])
        
        if not rows:
            return {"labels": [], "datasets": []}
        
        # Calculate average metrics across scenarios
        metrics = {
            "Performance": [],
            "Load Time": [],
            "Memory": [],
            "Network": [],
            "Accessibility": []
        }
        
        for row in rows:
            metrics["Performance"].append(getattr(row, 'performance_score', 0))
            
            # Convert load time to score (inverse)
            load_time = getattr(row, 'load_time_s', 0)
            load_score = max(0, 100 - load_time * 10)
            metrics["Load Time"].append(load_score)
            
            # Convert memory to score (inverse)
            memory = getattr(row, 'memory_usage_max_mb', 0)
            memory_score = max(0, 100 - memory * 0.5)
            metrics["Memory"].append(memory_score)
            
            # Accessibility
            acc = getattr(row, 'accessibility_score', 100)
            metrics["Accessibility"].append(acc)
            
            # Network efficiency (estimate)
            requests = getattr(row, 'total_requests', 50)
            network_score = max(0, 100 - requests * 0.5)
            metrics["Network"].append(network_score)
        
        labels = list(metrics.keys())
        data = [sum(values) / len(values) if values else 75 for values in metrics.values()]
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Current Performance",
                    "data": data,
                    "backgroundColor": "rgba(59, 130, 246, 0.2)",
                    "borderColor": "#3b82f6",
                    "borderWidth": 2,
                    "pointBackgroundColor": "#3b82f6"
                },
                {
                    "label": "Target",
                    "data": [90, 90, 90, 90, 90],
                    "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    "borderColor": "#22c55e",
                    "borderWidth": 1,
                    "borderDash": [5, 5],
                    "pointBackgroundColor": "#22c55e"
                }
            ]
        }
    
    def _generate_heatmap_data(self, result) -> Dict[str, Any]:
        """Generate heatmap data for scenario × metric matrix."""
        rows = getattr(result.performance_matrix, 'rows', [])
        
        scenarios = []
        metrics_labels = ["Score", "Load", "Memory", "LCP", "CLS", "TTFB"]
        data = []
        
        for row in rows:
            scenario_name = getattr(row.scenario, 'display_name', str(row.scenario))[:15]
            scenarios.append(scenario_name)
            
            row_data = [
                getattr(row, 'performance_score', 0),
                max(0, 100 - getattr(row, 'load_time_s', 0) * 10),  # Inverted load time
                max(0, 100 - getattr(row, 'memory_usage_max_mb', 0) * 0.5),  # Inverted memory
                max(0, 100 - (getattr(row, 'largest_contentful_paint_ms', 0) - 2500) * 0.02),
                max(0, 100 - getattr(row, 'cumulative_layout_shift', 0) * 400),
                75  # Placeholder for TTFB
            ]
            data.append(row_data)
        
        return {
            "scenarios": scenarios,
            "metrics": metrics_labels,
            "data": data
        }
    
    def _generate_memory_timeline_data(self, result) -> Dict[str, Any]:
        """Generate memory timeline data."""
        # Generate timeline data based on scenarios
        scenarios = getattr(result.performance_metrics, 'scenarios', {})
        
        labels = []
        heap_data = []
        dom_nodes = []
        
        for i, (key, scenario) in enumerate(scenarios.items()):
            labels.append(f"Run {i+1}")
            heap_data.append(scenario.memory_metrics.peak_heap_size_mb)
            dom_nodes.append(scenario.memory_metrics.dom_nodes_count / 100)  # Scale for visualization
        
        if not labels:
            labels = ["N/A"]
            heap_data = [0]
            dom_nodes = [0]
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Heap Size (MB)",
                    "data": heap_data,
                    "borderColor": "#3b82f6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "fill": True,
                    "tension": 0.4
                },
                {
                    "label": "DOM Nodes (x100)",
                    "data": dom_nodes,
                    "borderColor": "#22c55e",
                    "backgroundColor": "transparent",
                    "borderDash": [5, 5],
                    "tension": 0.4
                }
            ]
        }
    
    def _generate_waterfall_data(self, result) -> List[Dict[str, Any]]:
        """Generate waterfall chart data."""
        rows = getattr(result.performance_matrix, 'rows', [])
        
        if not rows:
            return []
        
        # Use first row's timing data
        row = rows[0]
        
        # Extract real timing if available, otherwise return empty
        # This avoids mock data as per latest requirements
        if hasattr(row, 'network_metrics') and row.network_metrics:
            # Building a simplified waterfall from network metrics
            return [
                {"name": "Total Load", "duration": getattr(row, 'load_time_s', 0) * 1000, "color": "#3b82f6", "start": 0}
            ]
            
        return []
    
    def _generate_comparison_data(self, result, comparison_result) -> Optional[Dict[str, Any]]:
        """Generate before/after comparison data."""
        if not comparison_result:
            return None
        
        current_score = getattr(result.performance_matrix, 'overall_score', 0)
        previous_score = getattr(comparison_result.performance_matrix, 'overall_score', 0)
        
        return {
            "labels": ["Previous", "Current"],
            "datasets": [{
                "label": "Overall Score",
                "data": [previous_score, current_score],
                "backgroundColor": ["#9ca3af", self._get_score_color(current_score)],
                "borderColor": ["#6b7280", "#374151"],
                "borderWidth": 2
            }],
            "delta": current_score - previous_score,
            "percent_change": ((current_score - previous_score) / previous_score * 100) if previous_score else 0
        }
    
    def _generate_benchmark_data(self, result) -> Dict[str, Any]:
        """Generate benchmark percentile comparison data."""
        score = getattr(result.performance_matrix, 'overall_score', 0)
        
        # Estimate percentile based on score
        if score >= 90:
            percentile = 90 + (score - 90) * 0.5
        elif score >= 70:
            percentile = 50 + (score - 70) * 2
        elif score >= 50:
            percentile = 25 + (score - 50) * 1.25
        else:
            percentile = score * 0.5
        
        return {
            "percentile": min(99, percentile),
            "score": score,
            "benchmarks": {
                "p50": 65,
                "p75": 78,
                "p90": 88,
                "p95": 93
            },
            "labels": ["Your Score", "P50", "P75", "P90", "P95"],
            "data": [score, 65, 78, 88, 93],
            "colors": [self._get_score_color(score), "#9ca3af", "#9ca3af", "#9ca3af", "#9ca3af"]
        }
    
    def _get_score_color(self, score: float) -> str:
        """Get color for a score."""
        if score >= 90:
            return "#3b82f6"
        elif score >= 70:
            return "#22c55e"
        elif score >= 50:
            return "#eab308"
        else:
            return "#ef4444"
    
    def _build_html(self, url: str, session_name: str, platform: str,
                   score_cards: List[ScoreCard], radar_data: Dict,
                   heatmap_data: Dict, memory_timeline_data: Dict,
                   waterfall_data: List[Dict], comparison_data: Optional[Dict],
                   benchmark_data: Dict, result) -> str:
        """Build the complete HTML dashboard."""
        
        # Generate score cards HTML
        score_cards_html = ""
        for card in score_cards[:6]:  # Limit to 6 cards
            trend_html = ""
            if card.trend is not None:
                trend_color = "#22c55e" if card.trend < 0 else "#ef4444"
                trend_icon = "↓" if card.trend < 0 else "↑"
                trend_html = f'<div style="color: {trend_color}; font-size: 0.875rem; margin-top: 0.25rem;">{trend_icon} {abs(card.trend):.1f}%</div>'
            
            score_cards_html += f"""
            <div class="score-card" style="background: {card.bg_color}; border-left: 4px solid {card.color};">
                <div class="score-card-header">
                    <span class="score-icon">{card.icon}</span>
                    <span class="score-severity" style="color: {card.color};">{card.severity}</span>
                </div>
                <div class="score-value" style="color: {card.color};">{card.score:.1f}</div>
                <div class="score-title">{card.title}</div>
                <div class="score-subtitle">{card.subtitle}</div>
                {trend_html}
            </div>
            """
        
        # Generate unique IDs for charts
        import uuid
        radar_id = f"radar_{uuid.uuid4().hex[:8]}"
        heatmap_id = f"heatmap_{uuid.uuid4().hex[:8]}"
        memory_id = f"memory_{uuid.uuid4().hex[:8]}"
        waterfall_id = f"waterfall_{uuid.uuid4().hex[:8]}"
        comparison_id = f"comparison_{uuid.uuid4().hex[:8]}"
        benchmark_id = f"benchmark_{uuid.uuid4().hex[:8]}"
        
        # Generate heatmap HTML
        heatmap_html = self._generate_heatmap_html(heatmap_data, heatmap_id)
        
        comparison_section = ""
        if comparison_data:
            delta = comparison_data.get("delta", 0)
            delta_color = "#22c55e" if delta >= 0 else "#ef4444"
            delta_sign = "+" if delta >= 0 else ""
            comparison_section = f"""
            <div class="comparison-section">
                <h3>📊 Before/After Comparison</h3>
                <div class="comparison-summary" style="background: {delta_color}15; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <span style="color: {delta_color}; font-size: 1.5rem; font-weight: bold;">{delta_sign}{delta:.1f} points</span>
                    <span style="color: #666;">({comparison_data.get('percent_change', 0):+.1f}%)</span>
                </div>
                <canvas id="{comparison_id}"></canvas>
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .header-meta {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        .content {{
            padding: 2rem;
        }}
        
        .score-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .score-card {{
            padding: 1.5rem;
            border-radius: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .score-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }}
        
        .score-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        
        .score-icon {{
            font-size: 1.25rem;
        }}
        
        .score-severity {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .score-value {{
            font-size: 2.5rem;
            font-weight: bold;
            line-height: 1;
            margin-bottom: 0.5rem;
        }}
        
        .score-title {{
            font-size: 0.875rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.25rem;
        }}
        
        .score-subtitle {{
            font-size: 0.75rem;
            color: #6b7280;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .chart-container {{
            background: #f9fafb;
            border-radius: 12px;
            padding: 1.5rem;
        }}
        
        .chart-container h3 {{
            margin-bottom: 1rem;
            color: #111827;
            font-size: 1.1rem;
        }}
        
        .heatmap-container {{
            background: #f9fafb;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            overflow-x: auto;
        }}
        
        .heatmap {{
            display: grid;
            gap: 2px;
            min-width: 600px;
        }}
        
        .heatmap-cell {{
            padding: 0.75rem;
            text-align: center;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .heatmap-label {{
            font-weight: 600;
            color: #374151;
            padding: 0.5rem;
        }}
        
        .waterfall-container {{
            background: #f9fafb;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .waterfall-bar {{
            height: 30px;
            margin: 4px 0;
            border-radius: 4px;
            display: flex;
            align-items: center;
            color: white;
            font-size: 0.75rem;
            padding: 0 8px;
            position: relative;
        }}
        
        .waterfall-label {{
            position: absolute;
            left: -100px;
            width: 90px;
            text-align: right;
            color: #374151;
            font-size: 0.75rem;
        }}
        
        .benchmark-bar {{
            display: flex;
            align-items: center;
            margin: 1rem 0;
        }}
        
        .benchmark-label {{
            width: 80px;
            font-size: 0.875rem;
            color: #374151;
        }}
        
        .benchmark-track {{
            flex: 1;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            position: relative;
            margin: 0 1rem;
        }}
        
        .benchmark-fill {{
            height: 100%;
            border-radius: 12px;
            transition: width 1s ease-out;
        }}
        
        .benchmark-value {{
            width: 50px;
            text-align: right;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .legend {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .score-cards-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header class="header">
            <h1>🚀 {self.config.title}</h1>
            <div class="header-meta">
                {url} • Platform: {platform.title()} • Session: {session_name} • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </header>
        
        <div class="content">
            <div class="score-cards-grid">
                {score_cards_html}
            </div>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>📡 Performance Radar</h3>
                    <canvas id="{radar_id}"></canvas>
                </div>
                
                <div class="chart-container">
                    <h3>📈 Memory Timeline</h3>
                    <canvas id="{memory_id}"></canvas>
                </div>
            </div>
            
            <div class="heatmap-container">
                <h3>🔥 Scenario × Metric Heatmap</h3>
                {heatmap_html}
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ef4444;"></div>
                        <span>Critical (&lt;50)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #eab308;"></div>
                        <span>Needs Improvement (50-70)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #22c55e;"></div>
                        <span>Good (70-90)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3b82f6;"></div>
                        <span>Excellent (90+)</span>
                    </div>
                </div>
            </div>
            
            <div class="waterfall-container">
                <h3>⏱️ Critical Path Waterfall</h3>
                <div style="position: relative; padding-left: 110px;">
                    {self._generate_waterfall_bars(waterfall_data)}
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>📊 Benchmark Comparison</h3>
                    {self._generate_benchmark_bars(benchmark_data)}
                </div>
                
                {comparison_section}
            </div>
        </div>
    </div>
    
    <script>
        // Radar Chart
        new Chart(document.getElementById('{radar_id}'), {{
            type: 'radar',
            data: {json.dumps(radar_data)},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 20
                        }}
                    }}
                }}
            }}
        }});
        
        // Memory Timeline Chart
        new Chart(document.getElementById('{memory_id}'), {{
            type: 'line',
            data: {json.dumps(memory_timeline_data)},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Comparison Chart
        {f"""
        new Chart(document.getElementById('{comparison_id}'), {{
            type: 'bar',
            data: {json.dumps(comparison_data)},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
        """ if comparison_data else ""}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_heatmap_html(self, data: Dict[str, Any], container_id: str) -> str:
        """Generate HTML for heatmap visualization."""
        if not data.get("scenarios"):
            return "<p>No data available</p>"
        
        scenarios = data["scenarios"]
        metrics = data["metrics"]
        values = data["data"]
        
        # Create grid CSS
        cols = len(metrics) + 1
        html = f'<div class="heatmap" style="grid-template-columns: 120px repeat({len(metrics)}, 1fr);">'
        
        # Header row
        html += '<div class="heatmap-label">Scenario</div>'
        for metric in metrics:
            html += f'<div class="heatmap-label">{metric}</div>'
        
        # Data rows
        for i, scenario in enumerate(scenarios):
            html += f'<div class="heatmap-label">{scenario}</div>'
            for j, metric in enumerate(metrics):
                value = values[i][j] if i < len(values) and j < len(values[i]) else 0
                color = self._get_heatmap_color(value)
                text_color = "white" if value < 50 or value > 90 else "#374151"
                html += f'<div class="heatmap-cell" style="background: {color}; color: {text_color};">{value:.0f}</div>'
        
        html += '</div>'
        return html
    
    def _get_heatmap_color(self, value: float) -> str:
        """Get color for heatmap cell based on value."""
        if value >= 90:
            return "#3b82f6"  # Blue
        elif value >= 70:
            return "#22c55e"  # Green
        elif value >= 50:
            return "#eab308"  # Yellow
        else:
            return "#ef4444"  # Red
    
    def _generate_waterfall_bars(self, data: List[Dict[str, Any]]) -> str:
        """Generate HTML for waterfall bars."""
        html = ""
        total_duration = sum(d["duration"] for d in data) if data else 1
        
        for item in data:
            width_pct = (item["duration"] / total_duration) * 100
            html += f"""
            <div class="waterfall-bar" style="background: {item['color']}; width: {width_pct}%; margin-left: {(item.get('start', 0) / total_duration) * 100}%;">
                <span class="waterfall-label">{item['name']}</span>
                {item['duration']:.0f}ms
            </div>
            """
        
        return html
    
    def _generate_benchmark_bars(self, data: Dict[str, Any]) -> str:
        """Generate HTML for benchmark comparison bars."""
        html = ""
        max_val = max(data["data"])
        
        for i, (label, value, color) in enumerate(zip(data["labels"], data["data"], data["colors"])):
            width_pct = (value / max_val) * 100
            html += f"""
            <div class="benchmark-bar">
                <div class="benchmark-label">{label}</div>
                <div class="benchmark-track">
                    <div class="benchmark-fill" style="width: {width_pct}%; background: {color};"></div>
                </div>
                <div class="benchmark-value">{value:.0f}</div>
            </div>
            """
        
        # Percentile indicator
        percentile = data.get("percentile", 50)
        html += f"""
        <div style="margin-top: 1.5rem; text-align: center; padding: 1rem; background: {'#f0fdf4' if percentile > 75 else '#fef3c7' if percentile > 50 else '#fef2f2'}; border-radius: 8px;">
            <div style="font-size: 2rem; font-weight: bold; color: {'#22c55e' if percentile > 75 else '#eab308' if percentile > 50 else '#ef4444'};">{percentile:.0f}th</div>
            <div style="color: #6b7280; font-size: 0.875rem;">Performance Percentile</div>
        </div>
        """
        
        return html


def generate_executive_dashboard(result, url: str, session_name: str,
                                 output_path: Optional[Path] = None,
                                 comparison_result=None) -> str:
    """
    Convenience function to generate an executive dashboard.
    
    Args:
        result: Scan result to visualize
        url: URL that was scanned
        session_name: Session name
        output_path: Optional path to save the HTML
        comparison_result: Optional previous result for comparison
        
    Returns:
        HTML string
    """
    generator = ExecutiveDashboardGenerator()
    html = generator.generate_dashboard(result, url, session_name, comparison_result)
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    return html
