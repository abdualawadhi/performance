"""
Performance Scoring Engine

This module provides a comprehensive scoring engine for normalizing performance
metrics to a 0-100 scale, with support for sensitivity analysis and weight
derivation using the Analytic Hierarchy Process (AHP).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class MetricType(Enum):
    """Types of performance metrics."""
    LOWER_IS_BETTER = "lower_is_better"  # e.g., load time, memory usage
    HIGHER_IS_BETTER = "higher_is_better"  # e.g., cache hit ratio
    TARGET_RANGE = "target_range"  # e.g., has an optimal range


@dataclass
class MetricThreshold:
    """Thresholds for scoring a specific metric."""
    excellent: float  # Score of 90-100
    good: float       # Score of 70-90
    fair: float       # Score of 50-70
    poor: float       # Score of 30-50
    critical: float   # Score of 0-30
    metric_type: MetricType = MetricType.LOWER_IS_BETTER
    unit: str = ""
    description: str = ""


@dataclass
class ScoringWeights:
    """Weights for different metric categories."""
    core_web_vitals: float = 0.35
    memory_efficiency: float = 0.25
    network_performance: float = 0.20
    accessibility: float = 0.10
    best_practices: float = 0.10
    
    def normalize(self) -> "ScoringWeights":
        """Normalize weights to sum to 1.0."""
        total = (self.core_web_vitals + self.memory_efficiency + 
                self.network_performance + self.accessibility + self.best_practices)
        if total == 0:
            return self
        return ScoringWeights(
            core_web_vitals=self.core_web_vitals / total,
            memory_efficiency=self.memory_efficiency / total,
            network_performance=self.network_performance / total,
            accessibility=self.accessibility / total,
            best_practices=self.best_practices / total
        )


@dataclass
class SensitivityResult:
    """Result of sensitivity analysis."""
    parameter_name: str
    base_value: float
    min_value: float
    max_value: float
    step_size: float
    scores_at_steps: List[Tuple[float, float]]  # (parameter_value, resulting_score)
    sensitivity_coefficient: float  # How much score changes per unit parameter change
    impact_rating: str  # "High", "Medium", "Low"


class PerformanceScoringEngine:
    """
    Comprehensive scoring engine for performance metrics.
    
    Normalizes various performance metrics to a 0-100 scale using industry
    standard thresholds, with support for sensitivity analysis.
    """
    
    # Industry-standard thresholds for Core Web Vitals and other metrics
    DEFAULT_THRESHOLDS = {
        # Core Web Vitals (in milliseconds)
        "largest_contentful_paint_ms": MetricThreshold(
            excellent=2500, good=2500, fair=4000, poor=4000, critical=6000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="Largest Contentful Paint - measures loading performance"
        ),
        "first_input_delay_ms": MetricThreshold(
            excellent=100, good=100, fair=300, poor=300, critical=500,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="First Input Delay - measures interactivity"
        ),
        "cumulative_layout_shift": MetricThreshold(
            excellent=0.1, good=0.1, fair=0.25, poor=0.25, critical=0.5,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="",
            description="Cumulative Layout Shift - measures visual stability"
        ),
        "time_to_interactive_ms": MetricThreshold(
            excellent=3800, good=3800, fair=7300, poor=7300, critical=10000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="Time to Interactive - measures time until page is fully interactive"
        ),
        "total_blocking_time_ms": MetricThreshold(
            excellent=200, good=200, fair=600, poor=600, critical=1000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="Total Blocking Time - measures main thread blocking"
        ),
        "speed_index_ms": MetricThreshold(
            excellent=3400, good=3400, fair=5800, poor=5800, critical=10000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="Speed Index - measures how quickly content is visually displayed"
        ),
        "first_contentful_paint_ms": MetricThreshold(
            excellent=1800, good=1800, fair=3000, poor=3000, critical=5000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="First Contentful Paint - measures time to first content"
        ),
        # Memory metrics (in MB)
        "peak_heap_size_mb": MetricThreshold(
            excellent=50, good=50, fair=100, poor=100, critical=200,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="MB",
            description="Peak JavaScript heap size"
        ),
        "memory_growth_rate": MetricThreshold(
            excellent=0.1, good=0.2, fair=0.5, poor=0.8, critical=1.0,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ratio",
            description="Rate of memory growth during page lifecycle"
        ),
        # Network metrics
        "total_transfer_size_kb": MetricThreshold(
            excellent=500, good=500, fair=1500, poor=1500, critical=3000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="KB",
            description="Total network transfer size"
        ),
        "total_requests": MetricThreshold(
            excellent=25, good=25, fair=60, poor=60, critical=100,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="requests",
            description="Total number of network requests"
        ),
        "cache_hit_ratio": MetricThreshold(
            excellent=0.8, good=0.6, fair=0.4, poor=0.2, critical=0.0,
            metric_type=MetricType.HIGHER_IS_BETTER,
            unit="ratio",
            description="Ratio of requests served from cache"
        ),
        # Load time
        "load_time_ms": MetricThreshold(
            excellent=1000, good=1000, fair=3000, poor=3000, critical=5000,
            metric_type=MetricType.LOWER_IS_BETTER,
            unit="ms",
            description="Total page load time"
        ),
    }
    
    def __init__(self, thresholds: Optional[Dict[str, MetricThreshold]] = None,
                 weights: Optional[ScoringWeights] = None):
        """
        Initialize the scoring engine.
        
        Args:
            thresholds: Custom thresholds for metrics (uses defaults if None)
            weights: Custom weights for scoring categories (uses defaults if None)
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.weights = (weights or ScoringWeights()).normalize()
        self._ahp_matrix: Optional[List[List[float]]] = None
        self._ahp_consistency_ratio: Optional[float] = None
    
    def normalize_metric(self, metric_name: str, value: float) -> float:
        """
        Normalize a metric value to a 0-100 score.
        
        Args:
            metric_name: Name of the metric
            value: Raw metric value
            
        Returns:
            Normalized score between 0 and 100
        """
        if metric_name not in self.thresholds:
            # Default linear scaling for unknown metrics
            return max(0, min(100, value))
        
        threshold = self.thresholds[metric_name]
        
        if threshold.metric_type == MetricType.LOWER_IS_BETTER:
            return self._score_lower_is_better(value, threshold)
        elif threshold.metric_type == MetricType.HIGHER_IS_BETTER:
            return self._score_higher_is_better(value, threshold)
        else:
            return self._score_target_range(value, threshold)
    
    def _score_lower_is_better(self, value: float, threshold: MetricThreshold) -> float:
        """Score a metric where lower values are better."""
        if value <= threshold.excellent:
            return 100.0
        elif value <= threshold.good:
            # Linear interpolation between 90 and 100
            return 90 + 10 * (threshold.good - value) / (threshold.good - threshold.excellent)
        elif value <= threshold.fair:
            # Linear interpolation between 70 and 90
            return 70 + 20 * (threshold.fair - value) / (threshold.fair - threshold.good)
        elif value <= threshold.poor:
            # Linear interpolation between 50 and 70
            return 50 + 20 * (threshold.poor - value) / (threshold.poor - threshold.fair)
        elif value <= threshold.critical:
            # Linear interpolation between 30 and 50
            return 30 + 20 * (threshold.critical - value) / (threshold.critical - threshold.poor)
        else:
            # Exponential decay below 30
            ratio = threshold.critical / value if value > 0 else 0
            return max(0, 30 * ratio)
    
    def _score_higher_is_better(self, value: float, threshold: MetricThreshold) -> float:
        """Score a metric where higher values are better."""
        if value >= threshold.excellent:
            return 100.0
        elif value >= threshold.good:
            return 90 + 10 * (value - threshold.good) / (threshold.excellent - threshold.good)
        elif value >= threshold.fair:
            return 70 + 20 * (value - threshold.fair) / (threshold.good - threshold.fair)
        elif value >= threshold.poor:
            return 50 + 20 * (value - threshold.poor) / (threshold.fair - threshold.poor)
        elif value >= threshold.critical:
            return 30 + 20 * (value - threshold.critical) / (threshold.poor - threshold.critical)
        else:
            ratio = value / threshold.critical if threshold.critical > 0 else 0
            return max(0, 30 * ratio)
    
    def _score_target_range(self, value: float, threshold: MetricThreshold) -> float:
        """Score a metric with an optimal target range."""
        # For target range, excellent is the optimal range
        # Good is near-optimal, etc.
        target = threshold.excellent
        distance = abs(value - target)
        
        if distance == 0:
            return 100.0
        elif distance <= (threshold.good - target):
            return 90 + 10 * (1 - distance / (threshold.good - target))
        elif distance <= (threshold.fair - target):
            return 70 + 20 * (1 - (distance - (threshold.good - target)) / 
                            (threshold.fair - threshold.good))
        elif distance <= (threshold.poor - target):
            return 50 + 20 * (1 - (distance - (threshold.fair - target)) / 
                            (threshold.poor - threshold.fair))
        elif distance <= (threshold.critical - target):
            return 30 + 20 * (1 - (distance - (threshold.poor - target)) / 
                            (threshold.critical - threshold.poor))
        else:
            return max(0, 30 * (threshold.critical - target) / distance)
    
    def calculate_overall_score(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate overall performance score from multiple metrics.
        
        Args:
            metrics: Dictionary of metric names to values
            
        Returns:
            Dictionary with overall score and category breakdowns
        """
        category_scores = {
            "core_web_vitals": [],
            "memory_efficiency": [],
            "network_performance": [],
            "accessibility": [],
            "best_practices": []
        }
        
        normalized_scores = {}
        
        # Categorize and normalize metrics
        for metric_name, value in metrics.items():
            score = self.normalize_metric(metric_name, value)
            normalized_scores[metric_name] = score
            
            # Categorize
            if any(vital in metric_name.lower() for vital in 
                   ["lcp", "fcp", "fid", "cls", "tti", "tbt", "speed_index"]):
                category_scores["core_web_vitals"].append(score)
            elif "memory" in metric_name.lower() or "heap" in metric_name.lower():
                category_scores["memory_efficiency"].append(score)
            elif any(net in metric_name.lower() for net in 
                    ["transfer", "request", "cache", "network"]):
                category_scores["network_performance"].append(score)
            elif "accessibility" in metric_name.lower():
                category_scores["accessibility"].append(score)
            else:
                category_scores["best_practices"].append(score)
        
        # Calculate category averages
        category_averages = {}
        for category, scores in category_scores.items():
            if scores:
                category_averages[category] = sum(scores) / len(scores)
            else:
                category_averages[category] = 75.0  # Default neutral score
        
        # Calculate weighted overall score
        overall_score = (
            category_averages["core_web_vitals"] * self.weights.core_web_vitals +
            category_averages["memory_efficiency"] * self.weights.memory_efficiency +
            category_averages["network_performance"] * self.weights.network_performance +
            category_averages["accessibility"] * self.weights.accessibility +
            category_averages["best_practices"] * self.weights.best_practices
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "category_scores": {k: round(v, 2) for k, v in category_averages.items()},
            "normalized_scores": normalized_scores,
            "weights": {
                "core_web_vitals": self.weights.core_web_vitals,
                "memory_efficiency": self.weights.memory_efficiency,
                "network_performance": self.weights.network_performance,
                "accessibility": self.weights.accessibility,
                "best_practices": self.weights.best_practices
            }
        }
    
    def perform_sensitivity_analysis(self, base_metrics: Dict[str, float],
                                     parameter: str,
                                     variation_range: Tuple[float, float] = (0.5, 1.5),
                                     steps: int = 10) -> SensitivityResult:
        """
        Perform sensitivity analysis on a specific parameter.
        
        Args:
            base_metrics: Base metric values
            parameter: Parameter to vary
            variation_range: Range of variation as multipliers (min, max)
            steps: Number of steps in analysis
            
        Returns:
            SensitivityResult with analysis data
        """
        if parameter not in base_metrics:
            raise ValueError(f"Parameter '{parameter}' not found in metrics")
        
        base_value = base_metrics[parameter]
        min_mult, max_mult = variation_range
        
        min_value = base_value * min_mult
        max_value = base_value * max_mult
        step_size = (max_value - min_value) / steps
        
        scores_at_steps = []
        
        for i in range(steps + 1):
            test_value = min_value + i * step_size
            test_metrics = base_metrics.copy()
            test_metrics[parameter] = test_value
            result = self.calculate_overall_score(test_metrics)
            scores_at_steps.append((test_value, result["overall_score"]))
        
        # Calculate sensitivity coefficient
        score_changes = [scores_at_steps[i+1][1] - scores_at_steps[i][1] 
                        for i in range(len(scores_at_steps) - 1)]
        avg_score_change = sum(score_changes) / len(score_changes) if score_changes else 0
        sensitivity_coefficient = abs(avg_score_change / step_size) if step_size != 0 else 0
        
        # Determine impact rating
        if sensitivity_coefficient > 0.1:
            impact_rating = "High"
        elif sensitivity_coefficient > 0.05:
            impact_rating = "Medium"
        else:
            impact_rating = "Low"
        
        return SensitivityResult(
            parameter_name=parameter,
            base_value=base_value,
            min_value=min_value,
            max_value=max_value,
            step_size=step_size,
            scores_at_steps=scores_at_steps,
            sensitivity_coefficient=sensitivity_coefficient,
            impact_rating=impact_rating
        )
    
    def derive_weights_ahp(self, pairwise_comparisons: List[List[float]]) -> ScoringWeights:
        """
        Derive weights using Analytic Hierarchy Process (AHP).
        
        AHP is a structured technique for organizing and analyzing complex decisions,
        based on mathematics and psychology.
        
        Args:
            pairwise_comparisons: 5x5 matrix of pairwise comparisons between categories:
                [Core Web Vitals, Memory, Network, Accessibility, Best Practices]
                Values: 1=equal, 3=moderate, 5=strong, 7=very strong, 9=extreme importance
                Reciprocals (1/3, 1/5, etc.) indicate the opposite relationship
                
        Returns:
            ScoringWeights derived from AHP
        """
        if len(pairwise_comparisons) != 5 or any(len(row) != 5 for row in pairwise_comparisons):
            raise ValueError("Pairwise comparison matrix must be 5x5")
        
        self._ahp_matrix = pairwise_comparisons
        
        # Calculate column sums
        col_sums = [sum(pairwise_comparisons[i][j] for i in range(5)) for j in range(5)]
        
        # Normalize matrix
        normalized = []
        for i in range(5):
            row = []
            for j in range(5):
                row.append(pairwise_comparisons[i][j] / col_sums[j] if col_sums[j] != 0 else 0)
            normalized.append(row)
        
        # Calculate priorities (row averages)
        priorities = [sum(normalized[i]) / 5 for i in range(5)]
        
        # Calculate consistency
        # 1. Multiply original matrix by priorities vector
        weighted_sums = []
        for i in range(5):
            weighted_sum = sum(pairwise_comparisons[i][j] * priorities[j] for j in range(5))
            weighted_sums.append(weighted_sum)
        
        # 2. Calculate lambda_max
        lambda_max = sum(weighted_sums[i] / priorities[i] for i in range(5) if priorities[i] != 0) / 5
        
        # 3. Calculate Consistency Index (CI)
        ci = (lambda_max - 5) / 4  # n=5, so n-1=4
        
        # 4. Random Index (RI) for n=5
        ri = 1.12
        
        # 5. Consistency Ratio (CR)
        self._ahp_consistency_ratio = ci / ri if ri != 0 else 0
        
        # Create weights from priorities
        self.weights = ScoringWeights(
            core_web_vitals=priorities[0],
            memory_efficiency=priorities[1],
            network_performance=priorities[2],
            accessibility=priorities[3],
            best_practices=priorities[4]
        )
        
        return self.weights
    
    def get_ahp_consistency_ratio(self) -> Optional[float]:
        """Get the consistency ratio from the last AHP calculation."""
        return self._ahp_consistency_ratio
    
    def is_ahp_consistent(self) -> bool:
        """Check if AHP matrix is consistent (CR < 0.1 is generally acceptable)."""
        if self._ahp_consistency_ratio is None:
            return False
        return self._ahp_consistency_ratio < 0.1
    
    def get_weight_rationale(self) -> str:
        """
        Get documented rationale for weight selection.
        
        Returns:
            Human-readable explanation of weight choices
        """
        return f"""
Performance Scoring Weight Rationale:

1. Core Web Vitals ({self.weights.core_web_vitals:.1%})
   - Rationale: Google's Core Web Vitals are the most important metrics for 
     user experience and search ranking. They directly impact SEO and user 
     satisfaction. LCP, FID, and CLS represent the fundamental pillars of 
     loading, interactivity, and visual stability.

2. Memory Efficiency ({self.weights.memory_efficiency:.1%})
   - Rationale: Memory usage directly impacts application performance, 
     especially on mobile devices and long-running sessions. Poor memory 
     management leads to crashes and degraded performance over time.

3. Network Performance ({self.weights.network_performance:.1%})
   - Rationale: Network efficiency affects load times and data costs for users. 
     While important, modern caching and CDN technologies mitigate some impact.

4. Accessibility ({self.weights.accessibility:.1%})
   - Rationale: Accessibility is crucial for inclusivity and often legally 
     required. However, it has less direct impact on raw performance metrics.

5. Best Practices ({self.weights.best_practices:.1%})
   - Rationale: Best practices ensure long-term maintainability and security 
     but have the least direct impact on immediate performance.

Consistency Check:
- AHP Consistency Ratio: {self._ahp_consistency_ratio:.4f if self._ahp_consistency_ratio else 'N/A'}
- Status: {'Consistent' if self.is_ahp_consistent() else 'Inconsistent (review comparisons)'}
"""
    
    def get_severity_color(self, score: float) -> str:
        """
        Get color code for a score based on 4-color severity system.
        
        Args:
            score: Performance score (0-100)
            
        Returns:
            Hex color code
        """
        if score >= 90:
            return "#3b82f6"  # Blue
        elif score >= 70:
            return "#22c55e"  # Green
        elif score >= 50:
            return "#eab308"  # Yellow
        else:
            return "#ef4444"  # Red
    
    def get_severity_label(self, score: float) -> str:
        """
        Get severity label for a score.
        
        Args:
            score: Performance score (0-100)
            
        Returns:
            Severity label
        """
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Critical"


def get_default_scoring_engine() -> PerformanceScoringEngine:
    """Get a scoring engine with default industry-standard weights."""
    # Default weights based on industry best practices
    weights = ScoringWeights(
        core_web_vitals=0.40,
        memory_efficiency=0.25,
        network_performance=0.20,
        accessibility=0.10,
        best_practices=0.05
    )
    return PerformanceScoringEngine(weights=weights)


def get_mobile_optimized_scoring_engine() -> PerformanceScoringEngine:
    """Get a scoring engine optimized for mobile performance evaluation."""
    # Mobile-optimized weights prioritize memory and network efficiency
    weights = ScoringWeights(
        core_web_vitals=0.35,
        memory_efficiency=0.30,
        network_performance=0.25,
        accessibility=0.07,
        best_practices=0.03
    )
    
    # Adjust thresholds for mobile (stricter requirements)
    thresholds = PerformanceScoringEngine.DEFAULT_THRESHOLDS.copy()
    
    # Stricter memory thresholds for mobile
    thresholds["peak_heap_size_mb"] = MetricThreshold(
        excellent=30, good=30, fair=60, poor=60, critical=120,
        metric_type=MetricType.LOWER_IS_BETTER,
        unit="MB",
        description="Peak JavaScript heap size (mobile-optimized)"
    )
    
    # Stricter transfer size for mobile
    thresholds["total_transfer_size_kb"] = MetricThreshold(
        excellent=250, good=250, fair=800, poor=800, critical=1500,
        metric_type=MetricType.LOWER_IS_BETTER,
        unit="KB",
        description="Total network transfer size (mobile-optimized)"
    )
    
    return PerformanceScoringEngine(thresholds=thresholds, weights=weights)
