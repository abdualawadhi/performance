"""
Statistical Visualizations for Performance Reports

This module provides advanced statistical visualizations including box plots,
correlation matrices, and confidence interval charts for thesis-grade reporting.
"""

import json
from typing import Dict, List, Tuple, Any
import math


def generate_box_plot_data(metrics: List[float], title: str = "Performance Distribution") -> Dict[str, Any]:
    """
    Generate box plot data for performance metrics visualization.
    
    Args:
        metrics: List of performance metric values
        title: Title for the box plot
    
    Returns:
        Dictionary containing box plot data in Chart.js format
    """
    if not metrics:
        return {
            "title": title,
            "data": {
                "labels": ["Metrics"],
                "datasets": [{
                    "label": "Performance Scores",
                    "data": [],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {}
        }
    
    # Calculate quartiles and statistics
    sorted_metrics = sorted(metrics)
    n = len(sorted_metrics)
    
    q1_index = n // 4
    q2_index = n // 2
    q3_index = 3 * n // 4
    
    q1 = sorted_metrics[q1_index]
    q2 = sorted_metrics[q2_index]
    q3 = sorted_metrics[q3_index]
    
    iqr = q3 - q1
    
    # Calculate whiskers (1.5 * IQR rule)
    lower_whisker = max(min(sorted_metrics), q1 - 1.5 * iqr)
    upper_whisker = min(max(sorted_metrics), q3 + 1.5 * iqr)
    
    # Identify outliers
    outliers = [x for x in sorted_metrics if x < lower_whisker or x > upper_whisker]
    
    # Generate box plot data for Chart.js
    box_plot_data = {
        "title": title,
        "data": {
            "labels": ["Performance Scores"],
            "datasets": [
                {
                    "label": "Main Distribution",
                    "data": [
                        {
                            "min": min(sorted_metrics),
                            "q1": q1,
                            "median": q2,
                            "q3": q3,
                            "max": max(sorted_metrics),
                            "outliers": outliers
                        }
                    ],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 2,
                    "outlierColor": "#F44336",
                    "outlierRadius": 5,
                    "padding": 10
                }
            ]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "scales": {
                "y": {
                    "beginAtZero": False,
                    "title": {
                        "display": True,
                        "text": "Performance Score"
                    }
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": title,
                    "font": {
                        "size": 16
                    }
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) {\n                            const data = context.raw;\n                            return [\n                                'Min: ' + data.min.toFixed(2),\n                                'Q1: ' + data.q1.toFixed(2),\n                                'Median: ' + data.median.toFixed(2),\n                                'Q3: ' + data.q3.toFixed(2),\n                                'Max: ' + data.max.toFixed(2),\n                                'Outliers: ' + data.outliers.length\n                            ];\n                        }"
                    }
                }
            }
        }
    }
    
    return box_plot_data


def generate_correlation_heatmap_data(correlation_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """
    Generate correlation heatmap data for metric relationships.
    
    Args:
        correlation_matrix: Correlation matrix from statistical analysis
    
    Returns:
        Dictionary containing heatmap data for visualization
    """
    if not correlation_matrix:
        return {
            "title": "Metric Correlation Matrix",
            "data": [],
            "options": {}
        }
    
    metric_names = list(correlation_matrix.keys())
    n_metrics = len(metric_names)
    
    # Prepare data matrix
    data_matrix = []
    for i, row_name in enumerate(metric_names):
        row_data = []
        for j, col_name in enumerate(metric_names):
            correlation = correlation_matrix[row_name][col_name]
            row_data.append({
                "x": col_name,
                "y": row_name,
                "value": correlation,
                "formatted": f"{correlation:.2f}"
            })
        data_matrix.append(row_data)
    
    # Generate heatmap data
    heatmap_data = {
        "title": "Performance Metric Correlation Matrix",
        "data": {
            "metrics": metric_names,
            "matrix": data_matrix
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "legend": {
                "display": True,
                "position": "right"
            },
            "scales": {
                "x": {
                    "type": "category",
                    "labels": metric_names,
                    "title": {
                        "display": True,
                        "text": "Metrics"
                    }
                },
                "y": {
                    "type": "category",
                    "labels": metric_names,
                    "title": {
                        "display": True,
                        "text": "Metrics"
                    }
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Performance Metric Correlation Matrix",
                    "font": {
                        "size": 16
                    }
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) {\n                            const data = context.raw;\n                            return data.x + ' vs ' + data.y + ': ' + data.formatted;\n                        }"
                    }
                }
            },
            "colorScale": {
                "min": -1,
                "max": 1,
                "colors": ["#F44336", "#FFFFFF", "#4CAF50"]
            }
        }
    }
    
    return heatmap_data


def generate_confidence_interval_chart_data(
    metrics: List[float], 
    title: str = "Performance Score with Confidence Intervals"
) -> Dict[str, Any]:
    """
    Generate confidence interval chart data for performance metrics.
    
    Args:
        metrics: List of performance metric values
        title: Title for the chart
    
    Returns:
        Dictionary containing confidence interval chart data
    """
    if not metrics or len(metrics) < 2:
        return {
            "title": title,
            "data": {
                "labels": [],
                "datasets": []
            },
            "options": {}
        }
    
    # Calculate statistics
    mean = sum(metrics) / len(metrics)
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in metrics) / (len(metrics) - 1))
    
    # Calculate 95% confidence interval using t-distribution approximation
    n = len(metrics)
    t_critical = 1.96  # Approximate for large samples
    if n <= 30:
        # Use more conservative t-value for small samples
        t_critical = 2.045  # Approximate for df=30, 95% CI
    
    margin_of_error = t_critical * (std_dev / math.sqrt(n))
    ci_lower = mean - margin_of_error
    ci_upper = mean + margin_of_error
    
    # Generate chart data
    chart_data = {
        "title": title,
        "data": {
            "labels": ["Performance Score"],
            "datasets": [
                {
                    "label": "Mean Score",
                    "data": [mean],
                    "type": "line",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 3,
                    "pointRadius": 6,
                    "pointBackgroundColor": "rgba(75, 192, 192, 1)",
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 2
                },
                {
                    "label": "95% Confidence Interval",
                    "data": [
                        {
                            "min": ci_lower,
                            "max": ci_upper
                        }
                    ],
                    "type": "box",
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 2
                },
                {
                    "label": "Individual Runs",
                    "data": [{"values": metrics}],
                    "type": "scatter",
                    "backgroundColor": "rgba(255, 99, 132, 0.5)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1,
                    "pointRadius": 4
                }
            ]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "scales": {
                "y": {
                    "beginAtZero": False,
                    "min": max(0, ci_lower - 5),
                    "max": min(100, ci_upper + 5),
                    "title": {
                        "display": True,
                        "text": "Performance Score"
                    }
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": title,
                    "font": {
                        "size": 16
                    }
                },
                "annotation": {
                    "annotations": {
                        "confidence_label": {
                            "type": "label",
                            "xValue": 0,
                            "yValue": mean + margin_of_error + 2,
                            "content": ["95% CI: " + mean.toFixed(2) + " ± " + margin_of_error.toFixed(2)],
                            "font": {
                                "size": 12
                            },
                            "color": "rgba(54, 162, 235, 1)",
                            "backgroundColor": "rgba(255, 255, 255, 0.8)",
                            "borderColor": "rgba(54, 162, 235, 1)",
                            "borderWidth": 1
                        }
                    }
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) {\n                            if (context.dataset.type === 'box') {\n                                const data = context.raw;\n                                return 'CI: ' + data.min.toFixed(2) + ' to ' + data.max.toFixed(2);\n                            } else if (context.dataset.type === 'line') {\n                                return 'Mean: ' + context.raw.toFixed(2);\n                            } else {\n                                return 'Run: ' + context.raw.toFixed(2);\n                            }\n                        }"
                    }
                }
            }
        }
    }
    
    return chart_data


def generate_qq_plot_data(metrics: List[float], title: str = "Normality Q-Q Plot") -> Dict[str, Any]:
    """
    Generate Q-Q plot data for normality testing.
    
    Args:
        metrics: List of performance metric values
        title: Title for the Q-Q plot
    
    Returns:
        Dictionary containing Q-Q plot data
    """
    if not metrics or len(metrics) < 3:
        return {
            "title": title,
            "data": {
                "labels": [],
                "datasets": []
            },
            "options": {}
        }
    
    # Sort the data
    sorted_data = sorted(metrics)
    n = len(sorted_data)
    
    # Calculate theoretical quantiles from standard normal distribution
    theoretical_quantiles = []
    for i in range(1, n + 1):
        # Use Blom's formula for normal quantile plot
        p = (i - 3/8) / (n + 1/4)
        # Approximate inverse CDF of standard normal (simplified)
        # For thesis purposes, use a simple approximation
        # In production, use scipy.stats.norm.ppf
        z = math.sqrt(2) * math.erfinv(2 * p - 1) if p > 0.5 else -math.sqrt(2) * math.erfinv(1 - 2 * p)
        theoretical_quantiles.append(z)
    
    # Generate Q-Q plot data
    qq_plot_data = {
        "title": title,
        "data": {
            "datasets": [
                {
                    "label": "Theoretical Normal",
                    "data": [{"x": tq, "y": tq} for tq in theoretical_quantiles],
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 2,
                    "showLine": True
                },
                {
                    "label": "Sample Data",
                    "data": [{"x": tq, "y": sd} for tq, sd in zip(theoretical_quantiles, sorted_data)],
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1,
                    "pointRadius": 4
                }
            ]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "scales": {
                "x": {
                    "type": "linear",
                    "title": {
                        "display": True,
                        "text": "Theoretical Quantiles"
                    }
                },
                "y": {
                    "type": "linear",
                    "title": {
                        "display": True,
                        "text": "Sample Quantiles"
                    }
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": title,
                    "font": {
                        "size": 16
                    }
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) {\n                            return 'Theoretical: ' + context.raw.x.toFixed(2) + ', Sample: ' + context.raw.y.toFixed(2);\n                        }"
                    }
                }
            }
        }
    }
    
    return qq_plot_data


def generate_statistical_summary_table(metrics_data: Dict[str, Any]) -> str:
    """
    Generate HTML table for statistical summary.
    
    Args:
        metrics_data: Dictionary containing statistical measures
    
    Returns:
        HTML table string
    """
    if not metrics_data:
        return "<p>No statistical data available</p>"
    
    # Extract data
    count = metrics_data.get('count', 0)
    mean = metrics_data.get('mean', 0.0)
    median = metrics_data.get('median', 0.0)
    std_dev = metrics_data.get('std_dev', 0.0)
    min_val = metrics_data.get('min', 0.0)
    max_val = metrics_data.get('max', 0.0)
    range_val = metrics_data.get('range', 0.0)
    cv = metrics_data.get('coefficient_of_variation', 0.0)
    ci_95 = metrics_data.get('confidence_interval_95', (0.0, 0.0))
    
    # Generate HTML table
    html_table = f"""
    <div class="statistical-summary">
        <h3>Statistical Summary</h3>
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Interpretation</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Sample Size (n)</td>
                    <td>{count}</td>
                    <td>{'Adequate sample size' if count >= 5 else 'Small sample size'}</td>
                </tr>
                <tr>
                    <td>Mean</td>
                    <td>{mean:.2f}</td>
                    <td>Average performance score</td>
                </tr>
                <tr>
                    <td>Median</td>
                    <td>{median:.2f}</td>
                    <td>Middle value of distribution</td>
                </tr>
                <tr>
                    <td>Standard Deviation</td>
                    <td>{std_dev:.2f}</td>
                    <td>{'Low variability' if std_dev < 5 else 'Moderate variability' if std_dev < 10 else 'High variability'}</td>
                </tr>
                <tr>
                    <td>Range</td>
                    <td>{min_val:.2f} - {max_val:.2f}</td>
                    <td>Minimum to maximum observed values</td>
                </tr>
                <tr>
                    <td>Coefficient of Variation</td>
                    <td>{cv:.2f}%</td>
                    <td>{'High consistency' if cv < 5 else 'Moderate consistency' if cv < 15 else 'Low consistency'}</td>
                </tr>
                <tr>
                    <td>95% Confidence Interval</td>
                    <td>{ci_95[0]:.2f} - {ci_95[1]:.2f}</td>
                    <td>Expected range for true mean (95% confidence)</td>
                </tr>
                <tr>
                    <td>CI Notation</td>
                    <td>{mean:.2f} ± {abs(ci_95[1] - ci_95[0])/2:.2f}</td>
                    <td>Academic notation format</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    
    return html_table


def generate_outlier_analysis_table(outliers: List[int], metrics: List[float]) -> str:
    """
    Generate HTML table for outlier analysis.
    
    Args:
        outliers: List of outlier indices
        metrics: List of all metric values
    
    Returns:
        HTML table string
    """
    if not outliers:
        return "<p class='text-success'>No outliers detected in the dataset.</p>"
    
    # Calculate statistics
    outlier_values = [metrics[i] for i in outliers]
    mean_outliers = sum(outlier_values) / len(outlier_values) if outlier_values else 0
    mean_all = sum(metrics) / len(metrics)
    
    # Generate HTML table
    html_table = f"""
    <div class="outlier-analysis">
        <h3>Outlier Analysis</h3>
        <table class="table table-bordered table-warning">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Analysis</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Number of Outliers</td>
                    <td>{len(outliers)}</td>
                    <td>{'Multiple outliers detected' if len(outliers) > 2 else 'Few outliers detected'}</td>
                </tr>
                <tr>
                    <td>Outlier Indices</td>
                    <td>{', '.join(str(i+1) for i in outliers)}</td>
                    <td>Run numbers with anomalous results</td>
                </tr>
                <tr>
                    <td>Outlier Values</td>
                    <td>{', '.join(f'{val:.2f}' for val in outlier_values)}</td>
                    <td>Performance scores of outlier runs</td>
                </tr>
                <tr>
                    <td>Mean of Outliers</td>
                    <td>{mean_outliers:.2f}</td>
                    <td>{'Outliers are higher' if mean_outliers > mean_all else 'Outliers are lower'} than overall mean</td>
                </tr>
                <tr>
                    <td>Overall Mean</td>
                    <td>{mean_all:.2f}</td>
                    <td>Mean of all runs</td>
                </tr>
                <tr>
                    <td>Impact</td>
                    <td colspan="2">
                        {'Significant impact on results' if len(outliers) > 1 else 'Minimal impact on results'}
                        {' - consider investigating root causes' if len(outliers) > 1 else ''}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    
    return html_table


def generate_comparison_table(
    baseline_metrics: List[float], 
    current_metrics: List[float], 
    title: str = "Before/After Comparison"
) -> str:
    """
    Generate HTML table for baseline comparison with statistical significance.
    
    Args:
        baseline_metrics: List of baseline metric values
        current_metrics: List of current metric values
        title: Title for the comparison table
    
    Returns:
        HTML table string
    """
    if not baseline_metrics or not current_metrics:
        return "<p>Insufficient data for comparison</p>"
    
    # Calculate statistics
    from ..utils.statistics import paired_t_test, cohens_d
    
    t_test_result = paired_t_test(baseline_metrics, current_metrics)
    effect_size = cohens_d(baseline_metrics, current_metrics)
    
    baseline_mean = sum(baseline_metrics) / len(baseline_metrics)
    current_mean = sum(current_metrics) / len(current_metrics)
    delta = current_mean - baseline_mean
    delta_percent = (delta / baseline_mean * 100) if baseline_mean != 0 else 0
    
    # Generate HTML table
    html_table = f"""
    <div class="comparison-analysis">
        <h3>{title}</h3>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Baseline</th>
                    <th>Current</th>
                    <th>Change</th>
                    <th>Significance</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Mean Score</td>
                    <td>{baseline_mean:.2f}</td>
                    <td>{current_mean:.2f}</td>
                    <td>{delta:+.2f} ({delta_percent:+.1f}%)</td>
                    <td>{'↑ Improved' if delta > 0 else '↓ Declined' if delta < 0 else '→ No change'}</td>
                </tr>
                <tr>
                    <td>t-statistic</td>
                    <td colspan="2">{t_test_result['t_statistic']:.3f}</td>
                    <td>df = {t_test_result['degrees_of_freedom']}</td>
                    <td>{'Significant' if t_test_result['significant'] else 'Not significant'}</td>
                </tr>
                <tr>
                    <td>p-value</td>
                    <td colspan="2">{t_test_result['p_value']:.4f}</td>
                    <td colspan="2">{'p < 0.05' if t_test_result['significant'] else 'p ≥ 0.05'}</td>
                </tr>
                <tr>
                    <td>Cohen's d</td>
                    <td colspan="2">{effect_size:.3f}</td>
                    <td colspan="2">{interpret_effect_size(effect_size)}</td>
                </tr>
                <tr>
                    <td>Conclusion</td>
                    <td colspan="4">
                        <strong>
                        {'The change is statistically significant with a ' + interpret_effect_size(effect_size) + ' effect size.' if t_test_result['significant'] else 'No statistically significant change detected.'}
                        </strong>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    
    return html_table


def interpret_effect_size(cohens_d: float) -> str:
    """
    Interpret Cohen's d effect size.
    
    Args:
        cohens_d: Cohen's d value
    
    Returns:
        Interpretation string
    """
    abs_d = abs(cohens_d)
    
    if abs_d < 0.2:
        return "Negligible"
    elif abs_d < 0.5:
        return "Small"
    elif abs_d < 0.8:
        return "Medium"
    elif abs_d < 1.2:
        return "Large"
    else:
        return "Very Large"
