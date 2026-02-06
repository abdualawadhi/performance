"""
Statistical Analysis Utilities for Performance Metrics

This module provides advanced statistical functions for calculating confidence intervals,
detecting outliers, and performing hypothesis testing on performance metrics.
"""

import math
from typing import List, Tuple, Dict, Optional


def confidence_interval(data: List[float], confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for a dataset using t-distribution.
    
    Args:
        data: List of numerical values
        confidence_level: Desired confidence level (default: 0.95 for 95% CI)
    
    Returns:
        Tuple of (lower_bound, upper_bound) for the confidence interval
    """
    if len(data) < 2:
        mean_val = data[0] if data else 0.0
        return (mean_val, mean_val)
    
    n = len(data)
    mean = sum(data) / n
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))
    
    # Calculate t-value for 95% confidence interval
    # Using simplified approximation for t-distribution
    # For small samples, use more conservative approach
    if n <= 30:
        # Use t-distribution approximation
        # Degrees of freedom = n - 1
        df = n - 1
        # Critical t-values for common confidence levels
        t_critical = {
            0.90: [6.314, 2.920, 2.353, 2.132, 2.015, 1.943, 1.895, 1.860, 1.833, 1.812, 1.796, 1.782, 1.771, 1.761, 1.753, 1.746, 1.740, 1.734, 1.729, 1.725, 1.721, 1.717, 1.714, 1.711, 1.708, 1.706, 1.703, 1.701, 1.699, 1.697, 1.696][min(df, 30) - 1]
            if df >= 1 else 12.706,
            0.95: [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042, 2.040][min(df, 30) - 1]
            if df >= 1 else 63.656,
            0.99: [63.656, 9.925, 5.841, 4.604, 4.032, 3.707, 3.499, 3.355, 3.250, 3.169, 3.106, 3.055, 3.012, 2.977, 2.947, 2.921, 2.898, 2.878, 2.861, 2.845, 2.831, 2.819, 2.807, 2.797, 2.787, 2.779, 2.771, 2.763, 2.756, 2.750, 2.744][min(df, 30) - 1]
            if df >= 1 else 636.619
        }[confidence_level]
    else:
        # For larger samples, use z-distribution (normal approximation)
        z_critical = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }[confidence_level]
        t_critical = z_critical
    
    # Calculate margin of error
    margin_of_error = t_critical * (std_dev / math.sqrt(n))
    
    return (mean - margin_of_error, mean + margin_of_error)


def detect_outliers_iqr(data: List[float], threshold: float = 1.5) -> List[int]:
    """
    Detect outliers using the Interquartile Range (IQR) method.
    
    Args:
        data: List of numerical values
        threshold: Multiplier for IQR to determine outlier boundaries (default: 1.5)
    
    Returns:
        List of indices of outlier values
    """
    if len(data) < 4:
        return []
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    # Calculate quartiles
    q1_index = n // 4
    q3_index = 3 * n // 4
    
    q1 = sorted_data[q1_index]
    q3 = sorted_data[q3_index]
    
    iqr = q3 - q1
    
    # Calculate outlier boundaries
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr
    
    # Find outliers
    outliers = []
    for i, value in enumerate(data):
        if value < lower_bound or value > upper_bound:
            outliers.append(i)
    
    return outliers


def coefficient_of_variation(data: List[float]) -> float:
    """
    Calculate coefficient of variation (CV) for a dataset.
    
    Args:
        data: List of numerical values
    
    Returns:
        Coefficient of variation as percentage
    """
    if not data or len(data) < 2:
        return 0.0
    
    mean = sum(data) / len(data)
    if mean == 0:
        return 0.0
    
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in data) / (len(data) - 1))
    
    return (std_dev / mean) * 100  # Return as percentage


def cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Calculate Cohen's d effect size for comparing two groups.
    
    Args:
        group1: First group of numerical values
        group2: Second group of numerical values
    
    Returns:
        Cohen's d effect size
    """
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    
    mean1 = sum(group1) / len(group1)
    mean2 = sum(group2) / len(group2)
    
    # Calculate pooled standard deviation
    var1 = sum((x - mean1) ** 2 for x in group1) / (len(group1) - 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / (len(group2) - 1)
    
    n1, n2 = len(group1), len(group2)
    pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
    pooled_std = math.sqrt(pooled_var)
    
    if pooled_std == 0:
        return 0.0
    
    return (mean1 - mean2) / pooled_std


def paired_t_test(group1: List[float], group2: List[float]) -> Dict[str, float]:
    """
    Perform paired t-test to compare two related groups.
    
    Args:
        group1: First group of numerical values
        group2: Second group of numerical values
    
    Returns:
        Dictionary with t-statistic, p-value, and degrees of freedom
    """
    if len(group1) != len(group2) or len(group1) < 2:
        return {
            't_statistic': 0.0,
            'p_value': 1.0,
            'degrees_of_freedom': 0,
            'significant': False
        }
    
    # Calculate differences
    differences = [g1 - g2 for g1, g2 in zip(group1, group2)]
    n = len(differences)
    
    mean_diff = sum(differences) / n
    std_diff = math.sqrt(sum((d - mean_diff) ** 2 for d in differences) / (n - 1))
    
    if std_diff == 0:
        return {
            't_statistic': 0.0,
            'p_value': 1.0,
            'degrees_of_freedom': n - 1,
            'significant': False
        }
    
    # Calculate t-statistic
    t_statistic = mean_diff / (std_diff / math.sqrt(n))
    
    # Calculate p-value using simplified approximation
    # For thesis purposes, we'll use a simplified approach
    # In production, scipy.stats.t.sf would be more accurate
    df = n - 1
    
    # Simple p-value approximation
    # This is a placeholder - in real implementation, use proper statistical tables
    p_value = 2 * (1 - 0.5 * (1 + math.atan(t_statistic / math.sqrt(df)) / (math.pi / 2)))
    
    return {
        't_statistic': t_statistic,
        'p_value': p_value,
        'degrees_of_freedom': df,
        'significant': p_value < 0.05  # Significant at 95% confidence
    }


def calculate_quartiles(data: List[float]) -> Tuple[float, float, float]:
    """
    Calculate quartiles (Q1, Q2, Q3) for box plot generation.
    
    Args:
        data: List of numerical values
    
    Returns:
        Tuple of (q1, q2, q3) values
    """
    if len(data) < 4:
        if len(data) == 0:
            return (0.0, 0.0, 0.0)
        mean_val = sum(data) / len(data)
        return (mean_val, mean_val, mean_val)
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    # Calculate quartile positions
    q1_pos = n // 4
    q2_pos = n // 2
    q3_pos = 3 * n // 4
    
    return (sorted_data[q1_pos], sorted_data[q2_pos], sorted_data[q3_pos])


def calculate_correlation_matrix(metrics: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate correlation matrix for multiple performance metrics.
    
    Args:
        metrics: Dictionary of metric names to lists of values
    
    Returns:
        Correlation matrix as nested dictionary
    """
    if not metrics or len(metrics) < 2:
        return {}
    
    metric_names = list(metrics.keys())
    n_metrics = len(metric_names)
    n_samples = len(next(iter(metrics.values())))
    
    if n_samples < 2:
        return {}
    
    # Initialize correlation matrix
    correlation_matrix = {}
    
    for i, metric1 in enumerate(metric_names):
        correlation_matrix[metric1] = {}
        for j, metric2 in enumerate(metric_names):
            if i == j:
                correlation_matrix[metric1][metric2] = 1.0
            else:
                # Calculate Pearson correlation coefficient
                x = metrics[metric1]
                y = metrics[metric2]
                
                mean_x = sum(x) / n_samples
                mean_y = sum(y) / n_samples
                
                covariance = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
                std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
                std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
                
                if std_x == 0 or std_y == 0:
                    correlation = 0.0
                else:
                    correlation = covariance / (std_x * std_y)
                
                correlation_matrix[metric1][metric2] = correlation
    
    return correlation_matrix


def interpret_effect_size(cohens_d: float) -> str:
    """
    Interpret Cohen's d effect size according to standard conventions.
    
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


def interpret_confidence_interval(ci_lower: float, ci_upper: float, mean: float) -> str:
    """
    Interpret confidence interval in relation to mean.
    
    Args:
        ci_lower: Lower bound of confidence interval
        ci_upper: Upper bound of confidence interval
        mean: Mean value
    
    Returns:
        Interpretation string
    """
    margin = (ci_upper - ci_lower) / 2
    relative_margin = margin / mean if mean != 0 else 0
    
    if relative_margin < 0.05:
        return "High precision"
    elif relative_margin < 0.15:
        return "Moderate precision"
    elif relative_margin < 0.30:
        return "Low precision"
    else:
        return "Very low precision"


def calculate_statistical_summary(data: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive statistical summary for a dataset.
    
    Args:
        data: List of numerical values
    
    Returns:
        Dictionary with statistical measures
    """
    if not data:
        return {
            'count': 0,
            'mean': 0.0,
            'median': 0.0,
            'std_dev': 0.0,
            'min': 0.0,
            'max': 0.0,
            'range': 0.0,
            'coefficient_of_variation': 0.0,
            'confidence_interval_95': (0.0, 0.0)
        }
    
    n = len(data)
    mean = sum(data) / n
    
    sorted_data = sorted(data)
    median = sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1)) if n > 1 else 0.0
    
    ci_95 = confidence_interval(data, 0.95)
    
    return {
        'count': n,
        'mean': mean,
        'median': median,
        'std_dev': std_dev,
        'min': min(data),
        'max': max(data),
        'range': max(data) - min(data),
        'coefficient_of_variation': coefficient_of_variation(data),
        'confidence_interval_95': ci_95
    }
