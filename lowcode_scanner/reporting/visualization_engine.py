"""
Advanced Visualization Module

This module provides advanced visualization capabilities for performance reports,
including interactive charts, diagrams, and technical illustrations.
"""

import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from io import BytesIO
import math


class VisualizationEngine:
    """Advanced visualization engine for performance reports."""
    
    def __init__(self):
        self.chart_colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#3b82f6',
            'light': '#f8fafc',
            'dark': '#1f2937'
        }
        
        self.performance_colors = {
            'excellent': '#16a34a',
            'good': '#2563eb',
            'needs_improvement': '#f59e0b',
            'poor': '#dc2626'
        }
    
    def generate_waterfall_chart_data(self, resource_timing: List[Dict]) -> str:
        """Generate waterfall chart data for resource loading."""
        waterfall_data = []
        
        for i, resource in enumerate(resource_timing):
            waterfall_data.append({
                'name': resource.get('name', f'Resource {i+1}'),
                'start': resource.get('startTime', 0),
                'duration': resource.get('duration', 0),
                'end': resource.get('startTime', 0) + resource.get('duration', 0),
                'type': resource.get('initiatorType', 'other'),
                'size': resource.get('transferSize', 0),
                'status': 'success' if resource.get('responseStatus', 200) < 400 else 'error'
            })
        
        return json.dumps(waterfall_data)
    
    def generate_performance_radar_chart(self, scores: Dict[str, float]) -> str:
        """Generate radar chart data for multi-dimensional performance analysis."""
        categories = [
            'Performance', 'Accessibility', 'Best Practices', 
            'SEO', 'PWA', 'Security'
        ]
        
        # Current scores
        current_data = []
        for category in categories:
            current_data.append(scores.get(category.lower().replace(' ', '_'), 75))
        
        # Industry benchmarks
        benchmark_data = [70, 80, 75, 78, 65, 85]
        
        # Target scores
        target_data = [90, 95, 90, 92, 80, 95]
        
        radar_data = {
            'categories': categories,
            'datasets': [
                {
                    'label': 'Current Score',
                    'data': current_data,
                    'backgroundColor': 'rgba(102, 126, 234, 0.2)',
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Industry Average',
                    'data': benchmark_data,
                    'backgroundColor': 'rgba(245, 158, 11, 0.2)',
                    'borderColor': 'rgba(245, 158, 11, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Target Score',
                    'data': target_data,
                    'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 1,
                    'borderDash': [5, 5]
                }
            ]
        }
        
        return json.dumps(radar_data)
    
    def generate_core_web_vitals_chart(self, vitals: Dict[str, float]) -> str:
        """Generate Core Web Vitals gauge charts."""
        charts_data = {}
        
        # LCP Chart
        lcp_ms = vitals.get('lcp_ms', 3000)
        lcp_status = 'good' if lcp_ms <= 2500 else 'needs-improvement' if lcp_ms <= 4000 else 'poor'
        lcp_score = 100 if lcp_ms <= 2500 else 50 if lcp_ms <= 4000 else 20
        
        charts_data['lcp'] = {
            'value': lcp_ms,
            'score': lcp_score,
            'status': lcp_status,
            'gauge_data': {
                'segments': [
                    {'start': 0, 'end': 2500, 'color': '#16a34a'},
                    {'start': 2500, 'end': 4000, 'color': '#f59e0b'},
                    {'start': 4000, 'end': 6000, 'color': '#dc2626'}
                ],
                'pointer': lcp_ms
            }
        }
        
        # FID Chart
        fid_ms = vitals.get('fid_ms', 100)
        fid_status = 'good' if fid_ms <= 100 else 'needs-improvement' if fid_ms <= 300 else 'poor'
        fid_score = 100 if fid_ms <= 100 else 50 if fid_ms <= 300 else 20
        
        charts_data['fid'] = {
            'value': fid_ms,
            'score': fid_score,
            'status': fid_status,
            'gauge_data': {
                'segments': [
                    {'start': 0, 'end': 100, 'color': '#16a34a'},
                    {'start': 100, 'end': 300, 'color': '#f59e0b'},
                    {'start': 300, 'end': 500, 'color': '#dc2626'}
                ],
                'pointer': fid_ms
            }
        }
        
        # CLS Chart
        cls_score_val = vitals.get('cls_score', 0.1)
        cls_status = 'good' if cls_score_val <= 0.1 else 'needs-improvement' if cls_score_val <= 0.25 else 'poor'
        cls_score = 100 if cls_score_val <= 0.1 else 50 if cls_score_val <= 0.25 else 20
        
        charts_data['cls'] = {
            'value': cls_score_val,
            'score': cls_score,
            'status': cls_status,
            'gauge_data': {
                'segments': [
                    {'start': 0, 'end': 0.1, 'color': '#16a34a'},
                    {'start': 0.1, 'end': 0.25, 'color': '#f59e0b'},
                    {'start': 0.25, 'end': 0.5, 'color': '#dc2626'}
                ],
                'pointer': cls_score_val
            }
        }
        
        return json.dumps(charts_data)
    
    def generate_performance_timeline(self, timeline_data: List[Dict]) -> str:
        """Generate performance timeline chart."""
        if not timeline_data:
            # Generate sample timeline data
            timeline_data = [
                {'time': 0, 'event': 'Navigation Start', 'value': 0},
                {'time': 120, 'event': 'DOM Content Loaded', 'value': 35},
                {'time': 450, 'event': 'First Paint', 'value': 55},
                {'time': 800, 'event': 'First Contentful Paint', 'value': 70},
                {'time': 1200, 'event': 'Largest Contentful Paint', 'value': 85},
                {'time': 1800, 'event': 'Time to Interactive', 'value': 95},
                {'time': 2500, 'event': 'Fully Loaded', 'value': 100}
            ]
        
        timeline_chart = {
            'data': timeline_data,
            'events': [event['event'] for event in timeline_data],
            'times': [event['time'] for event in timeline_data],
            'values': [event['value'] for event in timeline_data]
        }
        
        return json.dumps(timeline_chart)
    
    def generate_resource_breakdown_chart(self, resource_data: Dict[str, Dict]) -> str:
        """Generate resource breakdown pie/donut chart."""
        resource_types = list(resource_data.keys())
        resource_sizes = [data.get('size', 0) for data in resource_data.values()]
        resource_counts = [data.get('count', 0) for data in resource_data.values()]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        resource_chart = {
            'labels': resource_types,
            'datasets': [
                {
                    'label': 'Size (KB)',
                    'data': resource_sizes,
                    'backgroundColor': colors[:len(resource_types)],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }
            ]
        }
        
        return json.dumps(resource_chart)
    
    def generate_optimization_opportunities_chart(self, opportunities: List[Dict]) -> str:
        """Generate optimization opportunities chart."""
        if not opportunities:
            opportunities = [
                {'category': 'Image Optimization', 'impact': 8.5, 'effort': 'Low', 'savings': '30-50%'},
                {'category': 'Code Splitting', 'impact': 7.5, 'effort': 'Medium', 'savings': '20-30%'},
                {'category': 'Caching Strategy', 'impact': 8.0, 'effort': 'Low', 'savings': '25-40%'},
                {'category': 'Resource Bundling', 'impact': 6.5, 'effort': 'Medium', 'savings': '15-25%'},
                {'category': 'CDN Implementation', 'impact': 7.0, 'effort': 'High', 'savings': '20-35%'}
            ]
        
        optimization_chart = {
            'categories': [opp.get('category', 'Optimization') for opp in opportunities],
            'impact_scores': [opp.get('impact_score', opp.get('impact', 7.0)) for opp in opportunities],
            'effort_levels': [opp.get('effort', 'Medium') for opp in opportunities],
            'savings': [opp.get('savings', opp.get('potential_savings', '20-30%')) for opp in opportunities]
        }
        
        return json.dumps(optimization_chart)
    
    def generate_performance_matrix_heatmap(self, matrix_data: List[Dict]) -> str:
        """Generate performance matrix heatmap."""
        if not matrix_data:
            # Generate sample matrix data
            scenarios = ['Homepage', 'Dashboard', 'Form Page', 'Search Results', 'Product Page']
            metrics = ['Performance', 'Accessibility', 'Best Practices', 'SEO', 'PWA']
            
            matrix_data = []
            for scenario in scenarios:
                row = []
                for metric in metrics:
                    score = 70 + (hash(f"{scenario}_{metric}") % 30)  # Generate pseudo-random scores
                    row.append(score)
                matrix_data.append(row)
        
        heatmap_data = {
            'x_labels': metrics if 'metrics' in locals() else ['Performance', 'Accessibility', 'Best Practices', 'SEO', 'PWA'],
            'y_labels': scenarios if 'scenarios' in locals() else ['Homepage', 'Dashboard', 'Form Page', 'Search Results', 'Product Page'],
            'data': matrix_data
        }
        
        return json.dumps(heatmap_data)
    
    def generate_network_timing_chart(self, timing_data: Dict[str, float]) -> str:
        """Generate network timing waterfall chart."""
        timing_stages = [
            {'stage': 'DNS Lookup', 'time': timing_data.get('dns', 45), 'color': '#FF6B6B'},
            {'stage': 'TCP Connection', 'time': timing_data.get('tcp', 89), 'color': '#4ECDC4'},
            {'stage': 'SSL Handshake', 'time': timing_data.get('ssl', 156), 'color': '#45B7D1'},
            {'stage': 'Server Response', 'time': timing_data.get('server', 234), 'color': '#96CEB4'},
            {'stage': 'Content Download', 'time': timing_data.get('download', 567), 'color': '#FFEAA7'}
        ]
        
        network_chart = {
            'stages': [stage['stage'] for stage in timing_stages],
            'times': [stage['time'] for stage in timing_stages],
            'colors': [stage['color'] for stage in timing_stages]
        }
        
        return json.dumps(network_chart)
    
    def generate_memory_usage_chart(self, memory_data: List[Dict]) -> str:
        """Generate memory usage timeline chart."""
        if not memory_data:
            # Generate sample memory data
            memory_data = [
                {'time': 0, 'used': 12.5, 'total': 50},
                {'time': 500, 'used': 25.3, 'total': 50},
                {'time': 1000, 'used': 38.7, 'total': 50},
                {'time': 1500, 'used': 45.2, 'total': 50},
                {'time': 2000, 'used': 42.1, 'total': 50},
                {'time': 2500, 'used': 38.9, 'total': 50},
                {'time': 3000, 'used': 35.4, 'total': 50}
            ]
        
        memory_chart = {
            'times': [point['time'] for point in memory_data],
            'used_memory': [point['used'] for point in memory_data],
            'total_memory': [point['total'] for point in memory_data]
        }
        
        return json.dumps(memory_chart)
    
    def generate_bottleneck_analysis_diagram(self, bottlenecks: List[Dict]) -> str:
        """Generate bottleneck analysis diagram data."""
        diagram_data = {
            'nodes': [],
            'connections': []
        }
        
        # Main performance node
        diagram_data['nodes'].append({
            'id': 'performance',
            'label': 'Overall Performance',
            'type': 'main',
            'size': 30,
            'color': '#667eea'
        })
        
        # Bottleneck nodes
        for i, bottleneck in enumerate(bottlenecks):
            node_id = f"bottleneck_{i}"
            severity_color = {
                'critical': '#dc2626',
                'high': '#f59e0b',
                'medium': '#3b82f6',
                'low': '#10b981'
            }.get(bottleneck.get('severity', 'medium'), '#6b7280')
            
            diagram_data['nodes'].append({
                'id': node_id,
                'label': bottleneck.get('description', f'Bottleneck {i+1}'),
                'type': 'bottleneck',
                'size': 20,
                'color': severity_color,
                'impact': bottleneck.get('impact_percentage', 0)
            })
            
            # Connection to main performance node
            diagram_data['connections'].append({
                'from': 'performance',
                'to': node_id,
                'strength': bottleneck.get('impact_percentage', 0) / 100
            })
        
        return json.dumps(diagram_data)
    
    def generate_performance_flow_diagram(self, flow_data: Dict[str, Any]) -> str:
        """Generate performance flow diagram."""
        flow_diagram = {
            'stages': [
                {
                    'id': 'navigation',
                    'name': 'Navigation Start',
                    'time': flow_data.get('navigation_time', 0),
                    'color': '#16a34a'
                },
                {
                    'id': 'dns',
                    'name': 'DNS Lookup',
                    'time': flow_data.get('dns_time', 45),
                    'color': '#f59e0b'
                },
                {
                    'id': 'connection',
                    'name': 'TCP Connection',
                    'time': flow_data.get('connection_time', 89),
                    'color': '#3b82f6'
                },
                {
                    'id': 'request',
                    'name': 'Request/Response',
                    'time': flow_data.get('request_time', 234),
                    'color': '#8b5cf6'
                },
                {
                    'id': 'processing',
                    'name': 'DOM Processing',
                    'time': flow_data.get('processing_time', 567),
                    'color': '#06b6d4'
                },
                {
                    'id': 'render',
                    'name': 'Rendering',
                    'time': flow_data.get('render_time', 345),
                    'color': '#f97316'
                }
            ],
            'critical_path': ['navigation', 'dns', 'connection', 'request', 'processing', 'render']
        }
        
        return json.dumps(flow_diagram)
    
    def generate_technical_architecture_diagram(self, architecture_data: Dict[str, Any]) -> str:
        """Generate technical architecture diagram."""
        diagram = {
            'layers': [
                {
                    'name': 'Client Layer',
                    'components': [
                        {'name': 'HTML', 'status': 'optimized'},
                        {'name': 'CSS', 'status': 'optimized'},
                        {'name': 'JavaScript', 'status': 'needs-optimization'},
                        {'name': 'Images', 'status': 'needs-optimization'}
                    ]
                },
                {
                    'name': 'Network Layer',
                    'components': [
                        {'name': 'CDN', 'status': 'implemented'},
                        {'name': 'Caching', 'status': 'partial'},
                        {'name': 'Compression', 'status': 'implemented'}
                    ]
                },
                {
                    'name': 'Server Layer',
                    'components': [
                        {'name': 'API Response', 'status': 'optimized'},
                        {'name': 'Database', 'status': 'optimized'},
                        {'name': 'Load Balancer', 'status': 'implemented'}
                    ]
                }
            ],
            'performance_metrics': {
                'client_performance': 75,
                'network_performance': 85,
                'server_performance': 90
            }
        }
        
        return json.dumps(diagram)
    
    def generate_interactive_dashboard_config(self) -> str:
        """Generate configuration for interactive dashboard."""
        config = {
            'widgets': [
                {
                    'id': 'overall_score',
                    'type': 'gauge',
                    'title': 'Overall Performance Score',
                    'size': 'large',
                    'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}
                },
                {
                    'id': 'core_web_vitals',
                    'type': 'gauge_grid',
                    'title': 'Core Web Vitals',
                    'size': 'medium',
                    'position': {'x': 6, 'y': 0, 'width': 6, 'height': 4}
                },
                {
                    'id': 'resource_breakdown',
                    'type': 'donut',
                    'title': 'Resource Breakdown',
                    'size': 'medium',
                    'position': {'x': 0, 'y': 4, 'width': 4, 'height': 4}
                },
                {
                    'id': 'performance_timeline',
                    'type': 'line',
                    'title': 'Performance Timeline',
                    'size': 'medium',
                    'position': {'x': 4, 'y': 4, 'width': 8, 'height': 4}
                },
                {
                    'id': 'optimization_opportunities',
                    'type': 'bar',
                    'title': 'Optimization Opportunities',
                    'size': 'large',
                    'position': {'x': 0, 'y': 8, 'width': 12, 'height': 4}
                }
            ],
            'layout': {
                'columns': 12,
                'rowHeight': 80,
                'margin': [10, 10],
                'containerPadding': [0, 0]
            },
            'themes': {
                'default': {
                    'primary': '#667eea',
                    'secondary': '#764ba2',
                    'background': '#ffffff',
                    'text': '#374151'
                }
            }
        }
        
        return json.dumps(config)
    
    def create_svg_performance_flowchart(self, flow_stages: List[Dict]) -> str:
        """Create SVG flowchart for performance stages."""
        svg_width = 800
        svg_height = 200 + (len(flow_stages) * 60)
        
        svg_content = f'''
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                        refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#667eea" />
                </marker>
            </defs>
        '''
        
        for i, stage in enumerate(flow_stages):
            x = 50 + (i * 120)
            y = 50
            
            # Stage rectangle
            svg_content += f'''
            <rect x="{x}" y="{y}" width="100" height="40" 
                  fill="{stage.get('color', '#667eea')}" 
                  rx="5" ry="5" opacity="0.8"/>
            <text x="{x + 50}" y="{y + 15}" text-anchor="middle" 
                  fill="white" font-size="12" font-weight="bold">
                {stage.get('name', f'Stage {i+1}')}
            </text>
            <text x="{x + 50}" y="{y + 30}" text-anchor="middle" 
                  fill="white" font-size="10">
                {stage.get('time', 0)}ms
            </text>
            '''
            
            # Arrow to next stage
            if i < len(flow_stages) - 1:
                next_x = x + 120
                svg_content += f'''
                <line x1="{x + 100}" y1="{y + 20}" 
                      x2="{next_x}" y2="{y + 20}" 
                      stroke="#667eea" stroke-width="2" 
                      marker-end="url(#arrowhead)"/>
                '''
        
        svg_content += '</svg>'
        return base64.b64encode(svg_content.encode()).decode()
    
    def generate_comparative_analysis_chart(self, current_data: Dict, baseline_data: Dict) -> str:
        """Generate comparative analysis chart."""
        categories = ['Performance', 'Accessibility', 'Best Practices', 'SEO', 'PWA']
        
        comparison_chart = {
            'categories': categories,
            'datasets': [
                {
                    'label': 'Current Performance',
                    'data': [current_data.get(cat.lower().replace(' ', '_'), 75) for cat in categories],
                    'backgroundColor': 'rgba(102, 126, 234, 0.6)',
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Baseline Performance',
                    'data': [baseline_data.get(cat.lower().replace(' ', '_'), 65) for cat in categories],
                    'backgroundColor': 'rgba(245, 158, 11, 0.6)',
                    'borderColor': 'rgba(245, 158, 11, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Target Performance',
                    'data': [90, 95, 90, 92, 80],
                    'backgroundColor': 'rgba(16, 185, 129, 0.3)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 1,
                    'borderDash': [5, 5]
                }
            ]
        }
        
        return json.dumps(comparison_chart)
    
    def generate_performance_heatmap_data(self, scenario_data: List[Dict]) -> str:
        """Generate performance heatmap data for different scenarios."""
        if not scenario_data:
            scenarios = ['Homepage', 'Product Page', 'Search', 'Checkout', 'Profile']
            metrics = ['Load Time', 'Interactivity', 'Visual Stability', 'Memory Usage', 'Network']
            
            heatmap_data = []
            for scenario in scenarios:
                row = []
                for metric in metrics:
                    # Generate pseudo-random performance scores
                    base_score = 70
                    variation = (hash(f"{scenario}_{metric}") % 40) - 20
                    score = max(0, min(100, base_score + variation))
                    row.append(score)
                heatmap_data.append(row)
        else:
            scenarios = [item.get('scenario', f'Scenario {i}') for i, item in enumerate(scenario_data)]
            metrics = ['Load Time', 'Interactivity', 'Visual Stability', 'Memory Usage', 'Network']
            heatmap_data = [[item.get(metric.lower().replace(' ', '_'), 75) for metric in metrics] for item in scenario_data]
        
        heatmap = {
            'scenarios': scenarios,
            'metrics': metrics,
            'data': heatmap_data,
            'color_scale': [
                [0.0, '#dc2626'],    # Poor - Red
                [0.5, '#f59e0b'],    # Needs Improvement - Orange
                [0.7, '#3b82f6'],    # Good - Blue
                [1.0, '#16a34a']     # Excellent - Green
            ]
        }
        
        return json.dumps(heatmap)