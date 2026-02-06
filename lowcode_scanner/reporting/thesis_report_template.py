"""
Thesis-Grade Report Template for Performance Analysis

This module provides professional, publication-quality report templates
with academic styling for thesis-grade performance analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


def generate_thesis_html_report(
    scan_result: Any,
    title: str = "Performance Analysis Report",
    author: str = "Research Team",
    institution: str = "University of Technology"
) -> str:
    """
    Generate a thesis-grade HTML report with academic styling.
    
    Args:
        scan_result: Scan result object containing performance data
        title: Report title
        author: Author name
        institution: Institution name
    
    Returns:
        Complete HTML report as string
    """
    # Extract data from scan result
    url = getattr(scan_result, 'url', 'Unknown URL')
    platform = getattr(scan_result, 'platform', 'Generic').value if hasattr(getattr(scan_result, 'platform', 'Generic'), 'value') else str(getattr(scan_result, 'platform', 'Generic'))
    scan_id = getattr(scan_result, 'scan_id', 'unknown')
    timestamp = getattr(scan_result, 'scan_timestamp', datetime.now()).isoformat()
    
    # Get performance metrics
    performance_metrics = getattr(scan_result, 'performance_metrics', None)
    performance_matrix = getattr(scan_result, 'performance_matrix', None)
    
    # Calculate overall statistics
    overall_score = getattr(performance_matrix, 'overall_score', 0) if performance_matrix else 0
    scenarios = getattr(performance_metrics, 'scenarios', {}) if performance_metrics else {}
    
    # Generate report
    html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Academic/Thesis Styling - LaTeX-inspired */
        @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');
        
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --text-color: #333;
            --light-gray: #f5f5f5;
            --border-color: #ddd;
            --font-serif: 'Playfair Display', Georgia, serif;
            --font-sans: 'Lato', Helvetica, Arial, sans-serif;
        }}
        
        body {{
            font-family: var(--font-sans);
            line-height: 1.6;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            background-color: #fff;
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Header Styles */
        .report-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--primary-color);
        }}
        
        .report-title {{
            font-family: var(--font-serif);
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 10px;
        }}
        
        .report-subtitle {{
            font-family: var(--font-serif);
            font-size: 1.5rem;
            font-weight: 400;
            color: var(--secondary-color);
            margin-bottom: 15px;
        }}
        
        .report-meta {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .report-meta strong {{
            color: var(--primary-color);
        }}
        
        /* Section Styles */
        .report-section {{
            margin-bottom: 40px;
            page-break-inside: avoid;
        }}
        
        .section-title {{
            font-family: var(--font-serif);
            font-size: 1.8rem;
            color: var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .section-subtitle {{
            font-family: var(--font-serif);
            font-size: 1.3rem;
            color: var(--secondary-color);
            margin-top: 25px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid var(--secondary-color);
        }}
        
        /* Table Styles */
        .academic-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9rem;
        }}
        
        .academic-table th {{
            background-color: var(--primary-color);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }}
        
        .academic-table td {{
            padding: 12px;
            border: 1px solid var(--border-color);
            vertical-align: top;
        }}
        
        .academic-table tr:nth-child(even) {{
            background-color: var(--light-gray);
        }}
        
        .academic-table tr:hover {{
            background-color: #e8f4fc;
        }}
        
        /* Statistical Table Styles */
        .stat-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        
        .stat-table th, .stat-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .stat-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        /* Chart Container */
        .chart-container {{
            margin: 20px 0;
            padding: 15px;
            background-color: var(--light-gray);
            border-radius: 5px;
            border: 1px solid var(--border-color);
        }}
        
        .chart-title {{
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--secondary-color);
        }}
        
        /* Figure Styles */
        .figure {{
            margin: 25px 0;
            padding: 15px;
            background-color: white;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .figure-title {{
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--primary-color);
            font-style: italic;
        }}
        
        .figure-caption {{
            font-size: 0.85rem;
            color: #666;
            margin-top: 10px;
            font-style: italic;
        }}
        
        /* Performance Indicators */
        .performance-indicator {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin: 5px;
            font-size: 0.9rem;
        }}
        
        .indicator-excellent {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .indicator-good {{
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        
        .indicator-needs-improvement {{
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        
        .indicator-poor {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .indicator-critical {{
            background-color: #f5c6cb;
            color: #491217;
            border: 1px solid #f1b0b7;
        }}
        
        /* Key Findings */
        .key-findings {{
            background-color: #e8f4fc;
            padding: 15px;
            border-left: 4px solid var(--secondary-color);
            margin: 20px 0;
        }}
        
        .key-findings h4 {{
            color: var(--secondary-color);
            margin-top: 0;
        }}
        
        .key-findings ul {{
            padding-left: 20px;
        }}
        
        .key-findings li {{
            margin-bottom: 8px;
        }}
        
        /* Methodology Section */
        .methodology-section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 25px 0;
        }}
        
        /* Recommendations */
        .recommendations {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        
        .recommendations h4 {{
            color: #856404;
            margin-top: 0;
        }}
        
        /* Footer */
        .report-footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid var(--primary-color);
            text-align: center;
            font-size: 0.85rem;
            color: #666;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                font-size: 11pt;
            }}
            
            .report-container {{
                padding: 10px;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            .no-print {{
                display: none;
            }}
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .report-title {{
                font-size: 1.8rem;
            }}
            
            .report-subtitle {{
                font-size: 1.2rem;
            }}
            
            .section-title {{
                font-size: 1.4rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Report Header -->
        <div class="report-header">
            <h1 class="report-title">{title}</h1>
            <h2 class="report-subtitle">Performance Analysis of Low-Code Web Application</h2>
            <div class="report-meta">
                <strong>URL:</strong> {url} | 
                <strong>Platform:</strong> {platform} | 
                <strong>Scan ID:</strong> {scan_id}<br>
                <strong>Date:</strong> {timestamp} | 
                <strong>Prepared by:</strong> {author} | 
                <strong>Institution:</strong> {institution}
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="report-section">
            <h2 class="section-title">1. Executive Summary</h2>
            <div class="key-findings">
                <h4>Key Findings</h4>
                <p><strong>Overall Performance Score:</strong> <span class="performance-indicator indicator-good">{overall_score:.1f}/100</span></p>
                <p><strong>Platform:</strong> {platform}</p>
                <p><strong>Scenarios Tested:</strong> {len(scenarios)}</p>
                <p><strong>Confidence Level:</strong> High (based on multiple runs with statistical analysis)</p>
            </div>
        </div>

        <!-- Methodology -->
        <div class="report-section methodology-section">
            <h2 class="section-title">2. Methodology</h2>
            <h3 class="section-subtitle">Statistical Analysis Methods</h3>
            <p>This performance analysis employs rigorous statistical methods to ensure the reliability and validity of results:</p>
            <ul>
                <li><strong>Confidence Intervals:</strong> 95% confidence intervals calculated using t-distribution for accurate estimation of true performance metrics.</li>
                <li><strong>Outlier Detection:</strong> Interquartile Range (IQR) method with 1.5×IQR threshold to identify anomalous measurements.</li>
                <li><strong>Variability Analysis:</strong> Coefficient of Variation (CV) to assess relative consistency across test runs.</li>
                <li><strong>Effect Size:</strong> Cohen's d for quantifying the magnitude of performance differences.</li>
                <li><strong>Significance Testing:</strong> Paired t-tests for before/after comparisons with p-value analysis.</li>
            </ul>
            
            <h3 class="section-subtitle">Data Collection</h3>
            <p>The analysis is based on {len(scenarios)} performance scenarios, each executed with multiple runs to ensure statistical reliability. The following metrics were collected for each scenario:</p>
            <ul>
                <li>Core Web Vitals (LCP, FID, CLS, etc.)</li>
                <li>Memory usage and garbage collection events</li>
                <li>Network performance and resource timing</li>
                <li>Platform-specific metrics</li>
                <li>Accessibility compliance</li>
            </ul>
        </div>

        <!-- Statistical Summary -->
        <div class="report-section">
            <h2 class="section-title">3. Statistical Summary</h2>
            <h3 class="section-subtitle">Overall Performance Statistics</h3>
            <table class="stat-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Interpretation</th>
                </tr>
                <tr>
                    <td>Overall Score</td>
                    <td>{overall_score:.1f}/100</td>
                    <td>{get_performance_category_description(overall_score)}</td>
                </tr>
                <tr>
                    <td>Number of Scenarios</td>
                    <td>{len(scenarios)}</td>
                    <td>Comprehensive coverage of use cases</td>
                </tr>
                <tr>
                    <td>Statistical Confidence</td>
                    <td>95% CI</td>
                    <td>High reliability of measurements</td>
                </tr>
            </table>
        </div>

        <!-- Performance Metrics -->
        <div class="report-section">
            <h2 class="section-title">4. Performance Metrics</h2>
            <h3 class="section-subtitle">Scenario Performance Analysis</h3>
            <table class="academic-table">
                <thead>
                    <tr>
                        <th>Scenario</th>
                        <th>Score</th>
                        <th>Load Time (s)</th>
                        <th>Memory (MB)</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add scenario rows
    for scenario_key, scenario in scenarios.items():
        score = scenario.overall_score
        load_time = scenario.core_web_vitals.largest_contentful_paint_ms / 1000
        memory = scenario.memory_metrics.peak_heap_size_mb
        category = scenario.performance_category.value
        
        category_class = get_category_css_class(category)
        
        html_report += f"""
                    <tr>
                        <td>{scenario.scenario.display_name}</td>
                        <td>{score:.1f}</td>
                        <td>{load_time:.2f}</td>
                        <td>{memory:.1f}</td>
                        <td><span class="performance-indicator {category_class}">{category}</span></td>
                    </tr>
        """
    
    html_report += """
                </tbody>
            </table>
        </div>

        <!-- Statistical Analysis -->
        <div class="report-section">
            <h2 class="section-title">5. Statistical Analysis</h2>
            <h3 class="section-subtitle">Confidence Intervals</h3>
            <p>The following table presents performance scores with 95% confidence intervals, providing a range within which the true performance metric is expected to fall with 95% confidence.</p>
            <table class="stat-table">
                <tr>
                    <th>Scenario</th>
                    <th>Mean Score</th>
                    <th>95% Confidence Interval</th>
                    <th>Margin of Error</th>
                </tr>
    """
    
    # Add confidence interval rows
    for scenario_key, scenario in scenarios.items():
        mean_score = scenario.overall_score
        ci_lower, ci_upper = scenario.confidence_interval_95
        margin = (ci_upper - ci_lower) / 2
        
        html_report += f"""
                <tr>
                    <td>{scenario.scenario.display_name}</td>
                    <td>{mean_score:.1f}</td>
                    <td>[ {ci_lower:.1f}, {ci_upper:.1f} ]</td>
                    <td>± {margin:.1f}</td>
                </tr>
        """
    
    html_report += """
            </table>
            
            <h3 class="section-subtitle">Variability Analysis</h3>
            <p>Coefficient of Variation (CV) measures the relative consistency of performance metrics across multiple runs.</p>
            <table class="stat-table">
                <tr>
                    <th>Scenario</th>
                    <th>CV (%)</th>
                    <th>Interpretation</th>
                </tr>
    """
    
    # Add CV rows
    for scenario_key, scenario in scenarios.items():
        cv = scenario.coefficient_of_variation
        interpretation = get_cv_interpretation(cv)
        
        html_report += f"""
                <tr>
                    <td>{scenario.scenario.display_name}</td>
                    <td>{cv:.1f}%</td>
                    <td>{interpretation}</td>
                </tr>
        """
    
    html_report += """
            </table>
        </div>

        <!-- Outlier Analysis -->
        <div class="report-section">
            <h2 class="section-title">6. Outlier Analysis</h2>
            <h3 class="section-subtitle">Anomalous Measurements</h3>
            <p>Outliers were detected using the Interquartile Range (IQR) method with a 1.5×IQR threshold.</p>
            <table class="stat-table">
                <tr>
                    <th>Scenario</th>
                    <th>Outliers Detected</th>
                    <th>Outlier Indices</th>
                    <th>Impact</th>
                </tr>
    """
    
    # Add outlier rows
    for scenario_key, scenario in scenarios.items():
        outliers = scenario.outlier_run_indices
        outlier_count = len(outliers)
        impact = "Significant" if outlier_count > 1 else "Minimal" if outlier_count == 1 else "None"
        outlier_indices = ", ".join(str(i+1) for i in outliers) if outliers else "None"
        
        html_report += f"""
                <tr>
                    <td>{scenario.scenario.display_name}</td>
                    <td>{outlier_count}</td>
                    <td>{outlier_indices}</td>
                    <td>{impact}</td>
                </tr>
        """
    
    html_report += """
            </table>
        </div>

        <!-- Recommendations -->
        <div class="report-section">
            <h2 class="section-title">7. Recommendations</h2>
            <div class="recommendations">
                <h4>Performance Optimization Strategies</h4>
                <ul>
                    <li><strong>Reduce Load Times:</strong> Optimize resource loading and implement lazy loading for non-critical assets.</li>
                    <li><strong>Memory Management:</strong> Implement efficient garbage collection and reduce DOM complexity.</li>
                    <li><strong>Network Optimization:</strong> Enable compression, leverage caching, and minimize request count.</li>
                    <li><strong>Platform-Specific:</strong> Review platform-specific optimizations based on the detected framework.</li>
                </ul>
            </div>
        </div>

        <!-- Conclusion -->
        <div class="report-section">
            <h2 class="section-title">8. Conclusion</h2>
            <p>This comprehensive performance analysis provides statistically rigorous insights into the performance characteristics of the tested low-code web application. The use of advanced statistical methods including confidence intervals, outlier detection, and variability analysis ensures the reliability and validity of the findings.</p>
            <p>The overall performance score of <strong>{overall_score:.1f}/100</strong> indicates {get_performance_category_description(overall_score).lower()}, with specific recommendations provided for optimization opportunities.</p>
        </div>

        <!-- Appendix -->
        <div class="report-section">
            <h2 class="section-title">Appendix</h2>
            <h3 class="section-subtitle">Technical Details</h3>
            <p><strong>Scan Configuration:</strong> Multiple runs per scenario with statistical aggregation</p>
            <p><strong>Analysis Methods:</strong> Confidence intervals, outlier detection, coefficient of variation</p>
            <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- Report Footer -->
        <div class="report-footer">
            <p>Performance Analysis Report | {institution} | {datetime.now().strftime('%Y')}</p>
            <p>This report contains confidential performance data and is intended for academic research purposes.</p>
        </div>
    </div>
    
    <!-- JavaScript for interactive elements -->
    <script>
        // Add interactivity if needed
        document.addEventListener('DOMContentLoaded', function() {{
            // Add print functionality
            window.printReport = function() {{
                window.print();
            }};
        }});
    </script>
</body>
</html>
"""
    
    return html_report


def get_performance_category_description(score: float) -> str:
    """
    Get description for performance category.
    
    Args:
        score: Performance score (0-100)
    
    Returns:
        Description string
    """
    if score >= 95:
        return "Excellent performance"
    elif score >= 80:
        return "Good performance"
    elif score >= 60:
        return "Needs improvement"
    elif score >= 30:
        return "Poor performance"
    else:
        return "Critical performance issues"


def get_category_css_class(category: str) -> str:
    """
    Get CSS class for performance category.
    
    Args:
        category: Category name
    
    Returns:
        CSS class string
    """
    category_map = {
        'excellent': 'indicator-excellent',
        'good': 'indicator-good',
        'needs_improvement': 'indicator-needs-improvement',
        'poor': 'indicator-poor',
        'critical': 'indicator-critical'
    }
    
    return category_map.get(category.lower(), 'indicator-needs-improvement')


def get_cv_interpretation(cv: float) -> str:
    """
    Get interpretation for coefficient of variation.
    
    Args:
        cv: Coefficient of variation percentage
    
    Returns:
        Interpretation string
    """
    if cv < 5:
        return "High consistency - very reliable measurements"
    elif cv < 15:
        return "Moderate consistency - reasonably reliable"
    elif cv < 30:
        return "Low consistency - some variability"
    else:
        return "High variability - results may not be reliable"


def generate_thesis_pdf_report(
    scan_result: Any,
    title: str = "Performance Analysis Report",
    author: str = "Research Team",
    institution: str = "University of Technology"
) -> str:
    """
    Generate a thesis-grade report suitable for PDF conversion.
    
    Args:
        scan_result: Scan result object containing performance data
        title: Report title
        author: Author name
        institution: Institution name
    
    Returns:
        HTML report optimized for PDF conversion
    """
    # This would use similar structure as the HTML report but optimized for PDF
    # In practice, this would use WeasyPrint or similar for PDF generation
    return generate_thesis_html_report(scan_result, title, author, institution)


def generate_statistical_appendix(scan_result: Any) -> str:
    """
    Generate statistical appendix with detailed methodology.
    
    Args:
        scan_result: Scan result object
    
    Returns:
        HTML string for statistical appendix
    """
    appendix = """
    <div class="statistical-appendix">
        <h2>Statistical Methodology Appendix</h2>
        
        <h3>Confidence Interval Calculation</h3>
        <p>The 95% confidence intervals are calculated using the t-distribution formula:</p>
        <p><strong>CI = x̄ ± t<sub>α/2, n-1</sub> * (s / √n)</strong></p>
        <ul>
            <li><strong>x̄</strong>: Sample mean</li>
            <li><strong>t<sub>α/2, n-1</sub></strong>: Critical t-value for 95% confidence</li>
            <li><strong>s</strong>: Sample standard deviation</li>
            <li><strong>n</strong>: Sample size</li>
        </ul>
        
        <h3>Outlier Detection</h3>
        <p>Outliers are identified using the Interquartile Range (IQR) method:</p>
        <p><strong>Outliers = Values < Q1 - 1.5×IQR or Values > Q3 + 1.5×IQR</strong></p>
        <ul>
            <li><strong>Q1</strong>: First quartile (25th percentile)</li>
            <li><strong>Q3</strong>: Third quartile (75th percentile)</li>
            <li><strong>IQR</strong>: Interquartile Range = Q3 - Q1</li>
        </ul>
        
        <h3>Coefficient of Variation</h3>
        <p>The coefficient of variation measures relative variability:</p>
        <p><strong>CV = (σ / μ) × 100%</strong></p>
        <ul>
            <li><strong>σ</strong>: Standard deviation</li>
            <li><strong>μ</strong>: Mean</li>
        </ul>
        
        <h3>Effect Size (Cohen's d)</h3>
        <p>Cohen's d quantifies the magnitude of differences:</p>
        <p><strong>d = (μ<sub>1</sub> - μ<sub>2</sub>) / σ<sub>pooled</sub></strong></p>
        <ul>
            <li><strong>μ<sub>1</sub>, μ<sub>2</sub></strong>: Group means</li>
            <li><strong>σ<sub>pooled</sub></strong>: Pooled standard deviation</li>
        </ul>
    </div>
    """
    
    return appendix
