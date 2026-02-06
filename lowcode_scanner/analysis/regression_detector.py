"""
Regression Detector

This module provides regression detection capabilities for performance monitoring,
including baseline establishment, delta analysis, trend analysis, and anomaly detection.
"""

import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from enum import Enum


class RegressionSeverity(Enum):
    """Severity levels for performance regressions."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_delta(cls, delta_percentage: float) -> "RegressionSeverity":
        """Determine severity from delta percentage."""
        if delta_percentage <= 0:
            return cls.NONE
        elif delta_percentage < 5:
            return cls.LOW
        elif delta_percentage < 10:
            return cls.MEDIUM
        elif delta_percentage < 20:
            return cls.HIGH
        else:
            return cls.CRITICAL


class TrendDirection(Enum):
    """Direction of performance trend."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    UNKNOWN = "unknown"


@dataclass
class MetricBaseline:
    """Baseline data for a specific metric."""
    metric_name: str
    baseline_value: float
    std_dev: float = 0.0
    sample_count: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    min_value: float = 0.0
    max_value: float = 0.0
    
    @property
    def confidence_interval_95(self) -> Tuple[float, float]:
        """Calculate 95% confidence interval."""
        if self.sample_count < 2:
            return (self.baseline_value, self.baseline_value)
        margin = 1.96 * self.std_dev / math.sqrt(self.sample_count)
        return (self.baseline_value - margin, self.baseline_value + margin)


@dataclass
class DeltaAnalysis:
    """Analysis of the delta between current and baseline values."""
    metric_name: str
    baseline_value: float
    current_value: float
    absolute_delta: float
    percentage_delta: float
    severity: RegressionSeverity
    is_regression: bool
    is_improvement: bool
    within_confidence_interval: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "baseline_value": round(self.baseline_value, 2),
            "current_value": round(self.current_value, 2),
            "absolute_delta": round(self.absolute_delta, 2),
            "percentage_delta": round(self.percentage_delta, 2),
            "severity": self.severity.value,
            "is_regression": self.is_regression,
            "is_improvement": self.is_improvement,
            "within_confidence_interval": self.within_confidence_interval
        }


@dataclass
class TrendAnalysis:
    """Trend analysis results."""
    metric_name: str
    direction: TrendDirection
    slope: float  # Change per unit time
    r_squared: float  # Coefficient of determination
    projected_value: float  # Projected value at next measurement
    confidence: float  # Confidence in trend (0-1)
    data_points: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "direction": self.direction.value,
            "slope": round(self.slope, 4),
            "r_squared": round(self.r_squared, 4),
            "projected_value": round(self.projected_value, 2),
            "confidence": round(self.confidence, 2),
            "data_point_count": len(self.data_points)
        }


@dataclass
class RegressionReport:
    """Complete regression analysis report."""
    url: str
    timestamp: datetime
    overall_status: RegressionSeverity
    delta_analyses: List[DeltaAnalysis] = field(default_factory=list)
    trend_analyses: List[TrendAnalysis] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def regression_count(self) -> int:
        """Count of metrics showing regression."""
        return sum(1 for d in self.delta_analyses if d.is_regression)
    
    @property
    def improvement_count(self) -> int:
        """Count of metrics showing improvement."""
        return sum(1 for d in self.delta_analyses if d.is_improvement)
    
    @property
    def has_critical_regression(self) -> bool:
        """Check if any critical regressions exist."""
        return any(d.severity == RegressionSeverity.CRITICAL for d in self.delta_analyses)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status.value,
            "summary": {
                "regression_count": self.regression_count,
                "improvement_count": self.improvement_count,
                "anomaly_count": len(self.anomalies),
                "has_critical_regression": self.has_critical_regression
            },
            "delta_analysis": [d.to_dict() for d in self.delta_analyses],
            "trend_analysis": [t.to_dict() for t in self.trend_analyses],
            "anomalies": self.anomalies,
            "recommendations": self.recommendations
        }


class BaselineStore:
    """
    Store for managing performance baselines.
    
    Baselines can be persisted to disk and loaded for comparison.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize baseline store.
        
        Args:
            storage_path: Path to store baseline files (default: ~/.lowcode_scanner/baselines)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".lowcode_scanner" / "baselines"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._baselines: Dict[str, Dict[str, MetricBaseline]] = {}
    
    def _get_baseline_file(self, url: str) -> Path:
        """Get the file path for a URL's baselines."""
        # Create a safe filename from URL
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        return self.storage_path / f"{safe_name}.json"
    
    def save_baseline(self, url: str, baseline: Dict[str, MetricBaseline]) -> None:
        """
        Save baselines for a URL.
        
        Args:
            url: The URL being measured
            baseline: Dictionary of metric names to MetricBaseline objects
        """
        self._baselines[url] = baseline
        
        # Convert to serializable format
        data = {
            "url": url,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                name: {
                    "metric_name": b.metric_name,
                    "baseline_value": b.baseline_value,
                    "std_dev": b.std_dev,
                    "sample_count": b.sample_count,
                    "timestamp": b.timestamp.isoformat(),
                    "min_value": b.min_value,
                    "max_value": b.max_value
                }
                for name, b in baseline.items()
            }
        }
        
        baseline_file = self._get_baseline_file(url)
        with open(baseline_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_baseline(self, url: str) -> Optional[Dict[str, MetricBaseline]]:
        """
        Load baselines for a URL.
        
        Args:
            url: The URL to load baselines for
            
        Returns:
            Dictionary of metric names to MetricBaseline objects, or None if not found
        """
        # Check in-memory cache
        if url in self._baselines:
            return self._baselines[url]
        
        # Load from disk
        baseline_file = self._get_baseline_file(url)
        if not baseline_file.exists():
            return None
        
        try:
            with open(baseline_file, 'r') as f:
                data = json.load(f)
            
            baseline = {}
            for name, b_data in data.get("metrics", {}).items():
                baseline[name] = MetricBaseline(
                    metric_name=b_data["metric_name"],
                    baseline_value=b_data["baseline_value"],
                    std_dev=b_data.get("std_dev", 0.0),
                    sample_count=b_data.get("sample_count", 1),
                    timestamp=datetime.fromisoformat(b_data["timestamp"]),
                    min_value=b_data.get("min_value", 0.0),
                    max_value=b_data.get("max_value", 0.0)
                )
            
            self._baselines[url] = baseline
            return baseline
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading baseline for {url}: {e}")
            return None
    
    def update_baseline(self, url: str, metric_name: str, new_value: float) -> MetricBaseline:
        """
        Update a baseline with a new measurement using exponential moving average.
        
        Args:
            url: The URL being measured
            metric_name: Name of the metric
            new_value: New measurement value
            
        Returns:
            Updated MetricBaseline
        """
        baseline = self.load_baseline(url) or {}
        
        if metric_name in baseline:
            existing = baseline[metric_name]
            n = existing.sample_count + 1
            
            # Update using Welford's online algorithm
            delta = new_value - existing.baseline_value
            new_mean = existing.baseline_value + delta / n
            
            # Update standard deviation
            if n > 1:
                delta2 = new_value - new_mean
                new_variance = ((existing.std_dev ** 2) * (n - 2) + delta * delta2) / (n - 1)
                new_std = math.sqrt(max(0, new_variance))
            else:
                new_std = 0.0
            
            updated = MetricBaseline(
                metric_name=metric_name,
                baseline_value=new_mean,
                std_dev=new_std,
                sample_count=n,
                timestamp=datetime.now(timezone.utc),
                min_value=min(existing.min_value, new_value) if existing.min_value else new_value,
                max_value=max(existing.max_value, new_value) if existing.max_value else new_value
            )
        else:
            updated = MetricBaseline(
                metric_name=metric_name,
                baseline_value=new_value,
                std_dev=0.0,
                sample_count=1,
                timestamp=datetime.now(timezone.utc),
                min_value=new_value,
                max_value=new_value
            )
        
        baseline[metric_name] = updated
        self.save_baseline(url, baseline)
        return updated
    
    def list_baselines(self) -> List[str]:
        """List all URLs with stored baselines."""
        urls = []
        for f in self.storage_path.glob("*.json"):
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                urls.append(data.get("url", f.stem))
            except:
                pass
        return urls
    
    def delete_baseline(self, url: str) -> bool:
        """Delete baseline for a URL."""
        baseline_file = self._get_baseline_file(url)
        if baseline_file.exists():
            baseline_file.unlink()
            if url in self._baselines:
                del self._baselines[url]
            return True
        return False


class RegressionDetector:
    """
    Detector for performance regressions and anomalies.
    
    Provides capabilities for:
    - Establishing and managing baselines
    - Delta analysis with severity classification
    - Trend analysis using linear regression
    - Anomaly detection using statistical methods
    """
    
    def __init__(self, baseline_store: Optional[BaselineStore] = None):
        """
        Initialize regression detector.
        
        Args:
            baseline_store: Optional custom baseline store
        """
        self.baseline_store = baseline_store or BaselineStore()
        self._metric_history: Dict[str, List[Tuple[datetime, float]]] = {}
    
    def establish_baseline(self, url: str, metrics: Dict[str, float],
                          std_devs: Optional[Dict[str, float]] = None) -> Dict[str, MetricBaseline]:
        """
        Establish a new baseline for a URL.
        
        Args:
            url: The URL being measured
            metrics: Dictionary of metric names to values
            std_devs: Optional dictionary of standard deviations for each metric
            
        Returns:
            Dictionary of created MetricBaseline objects
        """
        baseline = {}
        timestamp = datetime.now(timezone.utc)
        
        for metric_name, value in metrics.items():
            baseline[metric_name] = MetricBaseline(
                metric_name=metric_name,
                baseline_value=value,
                std_dev=std_devs.get(metric_name, 0.0) if std_devs else 0.0,
                sample_count=1,
                timestamp=timestamp,
                min_value=value,
                max_value=value
            )
        
        self.baseline_store.save_baseline(url, baseline)
        return baseline
    
    def analyze_delta(self, url: str, current_metrics: Dict[str, float],
                     lower_is_better: Optional[Set[str]] = None) -> RegressionReport:
        """
        Analyze deltas between current metrics and baseline.
        
        Args:
            url: The URL being measured
            current_metrics: Current metric values
            lower_is_better: Set of metric names where lower is better (e.g., load_time)
            
        Returns:
            RegressionReport with analysis results
        """
        baseline = self.baseline_store.load_baseline(url)
        
        if not baseline:
            # No baseline exists, create one from current metrics
            baseline = self.establish_baseline(url, current_metrics)
            return RegressionReport(
                url=url,
                timestamp=datetime.now(timezone.utc),
                overall_status=RegressionSeverity.NONE,
                recommendations=["Initial baseline established. Future scans will be compared against these values."]
            )
        
        lower_is_better = lower_is_better or {"load_time_ms", "largest_contentful_paint_ms",
                                             "first_input_delay_ms", "cumulative_layout_shift",
                                             "total_blocking_time_ms", "memory_peak_mb",
                                             "total_transfer_size_kb", "ttfb_ms"}
        
        delta_analyses = []
        max_severity = RegressionSeverity.NONE
        
        for metric_name, current_value in current_metrics.items():
            if metric_name not in baseline:
                # New metric not in baseline
                self.baseline_store.update_baseline(url, metric_name, current_value)
                continue
            
            base = baseline[metric_name]
            
            # Calculate delta
            absolute_delta = current_value - base.baseline_value
            
            if base.baseline_value != 0:
                percentage_delta = (absolute_delta / abs(base.baseline_value)) * 100
            else:
                percentage_delta = 0 if current_value == 0 else 100
            
            # Determine if this is a regression
            is_regression = False
            is_improvement = False
            
            if metric_name in lower_is_better:
                is_regression = current_value > base.baseline_value
                is_improvement = current_value < base.baseline_value
            else:
                is_regression = current_value < base.baseline_value
                is_improvement = current_value > base.baseline_value
            
            # Check confidence interval
            ci_lower, ci_upper = base.confidence_interval_95
            within_ci = ci_lower <= current_value <= ci_upper
            
            # Determine severity
            severity = RegressionSeverity.from_delta(abs(percentage_delta)) if is_regression else RegressionSeverity.NONE
            
            analysis = DeltaAnalysis(
                metric_name=metric_name,
                baseline_value=base.baseline_value,
                current_value=current_value,
                absolute_delta=absolute_delta,
                percentage_delta=percentage_delta,
                severity=severity,
                is_regression=is_regression,
                is_improvement=is_improvement,
                within_confidence_interval=within_ci
            )
            
            delta_analyses.append(analysis)
            
            if severity.value > max_severity.value:
                max_severity = severity
            
            # Update baseline with new measurement
            self.baseline_store.update_baseline(url, metric_name, current_value)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(delta_analyses)
        
        return RegressionReport(
            url=url,
            timestamp=datetime.now(timezone.utc),
            overall_status=max_severity,
            delta_analyses=delta_analyses,
            recommendations=recommendations
        )
    
    def analyze_trends(self, url: str, metric_name: str,
                      history: Optional[List[Tuple[datetime, float]]] = None) -> TrendAnalysis:
        """
        Analyze trends for a specific metric using linear regression.
        
        Args:
            url: The URL being measured
            metric_name: Name of the metric to analyze
            history: Optional list of (timestamp, value) tuples
            
        Returns:
            TrendAnalysis with trend information
        """
        # Get history from storage or parameter
        if history is None:
            key = f"{url}:{metric_name}"
            history = self._metric_history.get(key, [])
        
        if len(history) < 3:
            return TrendAnalysis(
                metric_name=metric_name,
                direction=TrendDirection.UNKNOWN,
                slope=0.0,
                r_squared=0.0,
                projected_value=history[-1][1] if history else 0.0,
                confidence=0.0,
                data_points=history
            )
        
        # Convert timestamps to numeric values (days since first measurement)
        base_time = history[0][0]
        x_values = [(t - base_time).total_seconds() / 86400 for t, _ in history]  # Days
        y_values = [v for _, v in history]
        
        n = len(x_values)
        
        # Calculate linear regression
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0
            intercept = sum_y / n
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))
        ss_tot = sum((y - sum_y / n) ** 2 for y in y_values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine direction
        if slope > 0.01:
            direction = TrendDirection.DEGRADING
        elif slope < -0.01:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.STABLE
        
        # Project next value
        next_x = x_values[-1] + 1  # Next day
        projected = slope * next_x + intercept
        
        # Confidence based on R-squared and sample size
        confidence = min(1.0, r_squared * (1 - 1/n))
        
        return TrendAnalysis(
            metric_name=metric_name,
            direction=direction,
            slope=slope,
            r_squared=r_squared,
            projected_value=projected,
            confidence=confidence,
            data_points=history
        )
    
    def detect_anomalies(self, url: str, current_metrics: Dict[str, float],
                        threshold_std_dev: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in current metrics using statistical methods.
        
        Args:
            url: The URL being measured
            current_metrics: Current metric values
            threshold_std_dev: Number of standard deviations for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        baseline = self.baseline_store.load_baseline(url)
        if not baseline:
            return []
        
        anomalies = []
        
        for metric_name, current_value in current_metrics.items():
            if metric_name not in baseline:
                continue
            
            base = baseline[metric_name]
            
            # Skip if not enough data
            if base.sample_count < 5 or base.std_dev == 0:
                continue
            
            # Calculate z-score
            z_score = (current_value - base.baseline_value) / base.std_dev
            
            # Check if anomaly
            if abs(z_score) > threshold_std_dev:
                anomaly_type = "high" if z_score > 0 else "low"
                
                anomalies.append({
                    "metric_name": metric_name,
                    "current_value": round(current_value, 2),
                    "baseline_value": round(base.baseline_value, 2),
                    "z_score": round(z_score, 2),
                    "threshold": threshold_std_dev,
                    "type": anomaly_type,
                    "severity": "critical" if abs(z_score) > 3 else "warning"
                })
        
        return anomalies
    
    def _generate_recommendations(self, delta_analyses: List[DeltaAnalysis]) -> List[str]:
        """Generate recommendations based on delta analysis."""
        recommendations = []
        
        # Count by severity
        critical_count = sum(1 for d in delta_analyses if d.severity == RegressionSeverity.CRITICAL)
        high_count = sum(1 for d in delta_analyses if d.severity == RegressionSeverity.HIGH)
        
        if critical_count > 0:
            recommendations.append(
                f"URGENT: {critical_count} critical regression(s) detected. "
                "Immediate investigation required."
            )
        
        if high_count > 0:
            recommendations.append(
                f"WARNING: {high_count} high-severity regression(s) detected. "
                "Prioritize fixes in next sprint."
            )
        
        # Specific metric recommendations
        for delta in delta_analyses:
            if delta.is_regression:
                if "lcp" in delta.metric_name.lower() and delta.severity.value >= RegressionSeverity.MEDIUM.value:
                    recommendations.append(
                        f"Largest Contentful Paint increased by {delta.percentage_delta:.1f}%. "
                        "Consider optimizing images and critical rendering path."
                    )
                elif "memory" in delta.metric_name.lower() and delta.severity.value >= RegressionSeverity.MEDIUM.value:
                    recommendations.append(
                        f"Memory usage increased by {delta.percentage_delta:.1f}%. "
                        "Check for memory leaks and unnecessary object retention."
                    )
                elif "ttfb" in delta.metric_name.lower() and delta.severity.value >= RegressionSeverity.MEDIUM.value:
                    recommendations.append(
                        f"Time to First Byte increased by {delta.percentage_delta:.1f}%. "
                        "Review server-side performance and caching strategies."
                    )
        
        if not recommendations:
            recommendations.append("No significant regressions detected. Performance is stable.")
        
        return recommendations
    
    def get_historical_data(self, url: str, metric_name: str) -> List[Tuple[datetime, float]]:
        """Get historical data for a metric."""
        key = f"{url}:{metric_name}"
        return self._metric_history.get(key, [])
    
    def add_historical_data(self, url: str, metric_name: str, 
                           timestamp: datetime, value: float) -> None:
        """Add a historical data point."""
        key = f"{url}:{metric_name}"
        if key not in self._metric_history:
            self._metric_history[key] = []
        self._metric_history[key].append((timestamp, value))
        # Keep only last 100 data points
        self._metric_history[key] = self._metric_history[key][-100:]


def compare_scan_results(baseline_result, current_result, 
                        baseline_store: Optional[BaselineStore] = None) -> RegressionReport:
    """
    Convenience function to compare two scan results.
    
    Args:
        baseline_result: Baseline ScanResult
        current_result: Current ScanResult
        baseline_store: Optional baseline store
        
    Returns:
        RegressionReport
    """
    detector = RegressionDetector(baseline_store)
    
    # Extract metrics from baseline
    baseline_metrics = {}
    if hasattr(baseline_result, 'performance_matrix'):
        baseline_metrics['overall_score'] = baseline_result.performance_matrix.overall_score
    
    # Establish baseline
    detector.establish_baseline(baseline_result.url, baseline_metrics)
    
    # Extract current metrics
    current_metrics = {}
    if hasattr(current_result, 'performance_matrix'):
        current_metrics['overall_score'] = current_result.performance_matrix.overall_score
    
    # Analyze
    return detector.analyze_delta(current_result.url, current_metrics)
