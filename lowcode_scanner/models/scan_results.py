"""
Scan Results and Performance Matrix Models

This module contains models for organizing and presenting scan results,
including the comprehensive performance matrix requested for low-code
web application analysis.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, computed_field, field_validator

from .enums import (
    ConfidenceLevel,
    DeviceType,
    LowCodePlatform,
    MetricSeverity,
    NetworkCondition,
    PerformanceCategory,
    ReportFormat,
    ScenarioType,
)
from .performance_metrics import LowCodePerformanceMetrics, ScenarioMetrics


class PerformanceMatrixRow(BaseModel):
    """A single row in the performance matrix representing a scenario test."""

    scenario: ScenarioType = Field(..., description="Test scenario")
    load_time_s: float = Field(default=0.0, ge=0, description="Load time in seconds")
    memory_usage_max_mb: float = Field(
        default=0.0, ge=0, description="Maximum memory usage in MB"
    )

    # Performance Traces
    scripting_time_ms: float = Field(
        default=0.0, ge=0, description="Time spent in scripting"
    )
    rendering_time_ms: float = Field(
        default=0.0, ge=0, description="Time spent in rendering"
    )
    painting_time_ms: float = Field(
        default=0.0, ge=0, description="Time spent in painting"
    )

    # Visual Evidence
    timeline_screenshot_path: Optional[Path] = Field(
        default=None, description="Path to timeline screenshot"
    )
    video_recording_path: Optional[Path] = Field(
        default=None, description="Path to video recording"
    )
    performance_timeline_path: Optional[Path] = Field(
        default=None, description="Path to performance timeline data"
    )

    # Key Observations
    key_observations: List[str] = Field(
        default_factory=list, description="Key observations for this scenario"
    )
    performance_score: float = Field(
        default=0.0, ge=0, le=100, description="Overall performance score"
    )
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.TENTATIVE, description="Confidence level of measurements"
    )
    standard_deviation: float = Field(
        default=0.0, ge=0, description="Standard deviation of performance scores"
    )

    # Detailed Metrics
    first_contentful_paint_ms: float = Field(
        default=0.0, ge=0, description="First Contentful Paint"
    )
    largest_contentful_paint_ms: float = Field(
        default=0.0, ge=0, description="Largest Contentful Paint"
    )
    time_to_interactive_ms: float = Field(
        default=0.0, ge=0, description="Time to Interactive"
    )
    cumulative_layout_shift: float = Field(
        default=0.0, ge=0, description="Cumulative Layout Shift"
    )
    accessibility_score: float = Field(
        default=100.0, ge=0, le=100, description="Accessibility Score"
    )

    # Resource Metrics
    total_requests: int = Field(default=0, ge=0, description="Total number of requests")
    total_size_kb: float = Field(default=0.0, ge=0, description="Total page size in KB")

    # Platform-specific
    platform_specific_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Platform-specific performance metrics"
    )

    @computed_field
    @property
    def performance_category(self) -> PerformanceCategory:
        """Performance category based on score."""
        return PerformanceCategory.from_score(self.performance_score)

    @computed_field
    @property
    def performance_traces_summary(self) -> Dict[str, float]:
        """Summary of performance traces."""
        return {
            "scripting": self.scripting_time_ms,
            "rendering": self.rendering_time_ms,
            "painting": self.painting_time_ms,
            "total": self.scripting_time_ms
            + self.rendering_time_ms
            + self.painting_time_ms,
        }

    def add_observation(self, observation: str):
        """Add a key observation for this scenario."""
        if observation not in self.key_observations:
            self.key_observations.append(observation)

    @classmethod
    def from_scenario_metrics(
        cls, scenario_metrics: ScenarioMetrics
    ) -> "PerformanceMatrixRow":
        """Create a matrix row from scenario metrics."""
        # Extract scripting, rendering, and painting times from traces
        scripting_time = sum(
            trace.duration_ms
            for trace in scenario_metrics.performance_traces
            if trace.event_type.category == "scripting"
        )
        rendering_time = sum(
            trace.duration_ms
            for trace in scenario_metrics.performance_traces
            if trace.event_type.category == "rendering"
            and "layout" in trace.event_type.value.lower()
        )
        painting_time = sum(
            trace.duration_ms
            for trace in scenario_metrics.performance_traces
            if trace.event_type.category == "rendering"
            and "paint" in trace.event_type.value.lower()
        )

        # If no traces found, estimate based on typical performance breakdown
        if scripting_time == 0 and rendering_time == 0 and painting_time == 0:
            total_time = scenario_metrics.test_duration_ms
            # Typical breakdown: 40% scripting, 35% rendering, 25% painting
            scripting_time = total_time * 0.4
            rendering_time = total_time * 0.35
            painting_time = total_time * 0.25

        return cls(
            scenario=scenario_metrics.scenario,
            load_time_s=scenario_metrics.test_duration_ms / 1000,
            memory_usage_max_mb=scenario_metrics.memory_metrics.peak_heap_size_mb,
            scripting_time_ms=scripting_time,
            rendering_time_ms=rendering_time,
            painting_time_ms=painting_time,
            timeline_screenshot_path=scenario_metrics.screenshot_path,
            video_recording_path=scenario_metrics.video_path,
            performance_timeline_path=scenario_metrics.timeline_path,
            key_observations=scenario_metrics.key_observations.copy(),
            performance_score=scenario_metrics.overall_score,
            first_contentful_paint_ms=scenario_metrics.core_web_vitals.first_contentful_paint_ms,
            largest_contentful_paint_ms=scenario_metrics.core_web_vitals.largest_contentful_paint_ms,
            time_to_interactive_ms=scenario_metrics.core_web_vitals.time_to_interactive_ms,
            cumulative_layout_shift=scenario_metrics.core_web_vitals.cumulative_layout_shift,
            accessibility_score=scenario_metrics.accessibility_metrics.score if scenario_metrics.accessibility_metrics else 100.0,
            total_requests=scenario_metrics.network_metrics.total_requests,
            total_size_kb=scenario_metrics.network_metrics.total_transfer_size_kb,
            platform_specific_metrics={
                "platform": scenario_metrics.platform_metrics.platform.value,
                "client_side_processing_ms": scenario_metrics.platform_metrics.client_side_processing_ms,
                "server_side_processing_ms": scenario_metrics.platform_metrics.server_side_processing_ms,
                "third_party_integrations": scenario_metrics.platform_metrics.third_party_integrations,
            },
        )


class PerformanceMatrix(BaseModel):
    """
    Comprehensive performance matrix as requested by the user.

    This matrix provides a structured view of performance metrics across
    different scenarios including HomePage Load, Regular Use Case,
    Heavy List Load, and Upfront Scripting.
    """

    url: str = Field(..., description="Target URL being analyzed")
    platform: LowCodePlatform = Field(..., description="Detected low-code platform")

    # Matrix Rows - One for each scenario
    rows: List[PerformanceMatrixRow] = Field(
        default_factory=list, description="Matrix rows for each scenario"
    )

    # Test Configuration
    device_type: DeviceType = Field(
        default=DeviceType.DESKTOP, description="Device type used for testing"
    )
    network_condition: NetworkCondition = Field(
        default=NetworkCondition.WIFI, description="Network condition"
    )
    test_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the test was performed",
    )

    # Summary Metrics
    overall_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Overall performance score across all scenarios",
    )
    critical_scenarios: List[str] = Field(
        default_factory=list, description="Scenarios with critical performance issues"
    )
    best_performing_scenario: Optional[str] = Field(
        default=None, description="Best performing scenario"
    )
    worst_performing_scenario: Optional[str] = Field(
        default=None, description="Worst performing scenario"
    )

    # Executive Insights
    executive_summary: str = Field(
        default="", description="Executive summary of performance findings"
    )
    key_recommendations: List[Dict[str, Union[str, MetricSeverity]]] = Field(
        default_factory=list, description="Key performance recommendations"
    )

    def add_scenario_result(self, scenario_metrics: ScenarioMetrics):
        """Add a scenario result to the matrix."""
        matrix_row = PerformanceMatrixRow.from_scenario_metrics(scenario_metrics)
        self.rows.append(matrix_row)
        self._update_summary_metrics()

    def get_scenario_row(
        self, scenario_type: ScenarioType
    ) -> Optional[PerformanceMatrixRow]:
        """Get the matrix row for a specific scenario."""
        for row in self.rows:
            if row.scenario == scenario_type:
                return row
        return None

    def _update_summary_metrics(self):
        """Update summary metrics based on current rows."""
        if not self.rows:
            return

        # Calculate overall score
        scores = [row.performance_score for row in self.rows]
        self.overall_score = sum(scores) / len(scores)

        # Identify critical scenarios (score < 50)
        self.critical_scenarios = [
            row.scenario.display_name for row in self.rows if row.performance_score < 50
        ]

        # Find best and worst scenarios
        best_row = max(self.rows, key=lambda r: r.performance_score)
        worst_row = min(self.rows, key=lambda r: r.performance_score)

        self.best_performing_scenario = best_row.scenario.display_name
        self.worst_performing_scenario = worst_row.scenario.display_name

    def add_recommendation(
        self,
        title: str,
        description: str,
        severity: MetricSeverity = MetricSeverity.MEDIUM,
    ):
        """Add a performance recommendation."""
        self.key_recommendations.append(
            {"title": title, "description": description, "severity": severity}
        )

    @computed_field
    @property
    def matrix_summary(self) -> Dict[str, Any]:
        """Generate a summary of the performance matrix."""
        return {
            "total_scenarios": len(self.rows),
            "overall_score": self.overall_score,
            "performance_category": PerformanceCategory.from_score(
                self.overall_score
            ).value,
            "critical_scenarios_count": len(self.critical_scenarios),
            "average_load_time_s": sum(row.load_time_s for row in self.rows)
            / len(self.rows)
            if self.rows
            else 0,
            "average_memory_usage_mb": sum(row.memory_usage_max_mb for row in self.rows)
            / len(self.rows)
            if self.rows
            else 0,
            "total_recommendations": len(self.key_recommendations),
        }

    def to_html_table(self) -> str:
        """Generate HTML table representation of the matrix."""
        if not self.rows:
            return "<p>No scenario data available</p>"

        html = """
        <table class="performance-matrix-table">
            <thead>
                <tr>
                    <th>Scenario</th>
                    <th>Load Time (s)</th>
                    <th>Memory Usage (MB, max)</th>
                    <th>Performance Traces</th>
                    <th>Key Observations</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
        """

        for row in self.rows:
            traces = row.performance_traces_summary
            traces_text = f"Scripting: {traces['scripting']:.0f}ms, Rendering: {traces['rendering']:.0f}ms, Paint: {traces['painting']:.0f}ms"
            if row.timeline_screenshot_path:
                traces_text += "<br>Timeline Screenshot Available"

            observations = "<br>".join(
                row.key_observations[:3]
            )  # Show first 3 observations
            if len(row.key_observations) > 3:
                observations += f"<br>... and {len(row.key_observations) - 3} more"

            category_color = row.performance_category.color

            html += f"""
                <tr>
                    <td><strong>{row.scenario.display_name}</strong></td>
                    <td>{row.load_time_s:.2f}</td>
                    <td>{row.memory_usage_max_mb:.1f}</td>
                    <td>{traces_text}</td>
                    <td>{observations}</td>
                    <td style="color: {category_color}; font-weight: bold;">{row.performance_score:.1f}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        return html

    @field_validator("test_timestamp")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone information."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ScanResult(BaseModel):
    """Complete scan result for a single URL with all scenarios and analysis."""

    url: str = Field(..., description="Scanned URL")
    platform: LowCodePlatform = Field(..., description="Detected platform")

    # Core Performance Data
    performance_metrics: LowCodePerformanceMetrics = Field(
        ..., description="Detailed performance metrics"
    )
    performance_matrix: PerformanceMatrix = Field(
        ..., description="Performance matrix for reporting"
    )

    # Scan Metadata
    scan_id: str = Field(..., description="Unique scan identifier")
    scan_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Scan execution timestamp",
    )
    scan_duration_total_s: float = Field(
        default=0.0, ge=0, description="Total scan duration in seconds"
    )

    # Test Configuration
    test_configuration: Dict[str, Any] = Field(
        default_factory=dict, description="Test configuration used"
    )

    # Analysis Results
    success: bool = Field(
        default=True, description="Whether the scan completed successfully"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if scan failed"
    )
    warnings: List[str] = Field(default_factory=list, description="Scan warnings")

    # Generated Artifacts
    report_paths: Dict[ReportFormat, Path] = Field(
        default_factory=dict, description="Paths to generated report files"
    )
    screenshot_paths: List[Path] = Field(
        default_factory=list, description="Paths to screenshot files"
    )
    video_paths: List[Path] = Field(
        default_factory=list, description="Paths to video recording files"
    )

    @computed_field
    @property
    def executive_summary_brief(self) -> str:
        """Brief executive summary for dashboard display."""
        if not self.success:
            return f"Scan failed: {self.error_message}"

        score = self.performance_matrix.overall_score
        category = PerformanceCategory.from_score(score)

        return (
            f"{self.platform.value.title()} app scored {score:.1f}/100 ({category.value}). "
            f"Tested {len(self.performance_matrix.rows)} scenarios. "
            f"Critical issues: {len(self.performance_matrix.critical_scenarios)}."
        )

    def add_warning(self, message: str):
        """Add a warning to the scan result."""
        if message not in self.warnings:
            self.warnings.append(message)

    def add_report_path(self, format_type: ReportFormat, path: Path):
        """Add a generated report file path."""
        self.report_paths[format_type] = path

    @field_validator("scan_timestamp")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone information."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ScanSession(BaseModel):
    """A complete scanning session covering multiple URLs and generating comparative reports."""

    session_id: str = Field(..., description="Unique session identifier")
    session_name: str = Field(default="", description="Human-readable session name")

    # Scan Results
    scan_results: List[ScanResult] = Field(
        default_factory=list, description="Individual scan results"
    )

    # Session Metadata
    start_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Session start time",
    )
    end_timestamp: Optional[datetime] = Field(
        default=None, description="Session end time"
    )
    total_duration_s: float = Field(
        default=0.0, ge=0, description="Total session duration"
    )

    # Configuration
    test_configuration: Dict[str, Any] = Field(
        default_factory=dict, description="Global test configuration"
    )

    # Session Summary
    total_urls_scanned: int = Field(default=0, ge=0, description="Total URLs scanned")
    successful_scans: int = Field(
        default=0, ge=0, description="Number of successful scans"
    )
    failed_scans: int = Field(default=0, ge=0, description="Number of failed scans")

    # Platform Distribution
    platform_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Distribution of platforms scanned"
    )

    # Generated Reports
    comparative_report_path: Optional[Path] = Field(
        default=None, description="Path to comparative analysis report"
    )
    executive_dashboard_path: Optional[Path] = Field(
        default=None, description="Path to executive dashboard"
    )

    def add_scan_result(self, scan_result: ScanResult):
        """Add a scan result to the session."""
        self.scan_results.append(scan_result)
        self._update_session_metrics()

    def finalize_session(self):
        """Mark the session as complete and update final metrics."""
        self.end_timestamp = datetime.now(timezone.utc)
        if self.start_timestamp:
            self.total_duration_s = (
                self.end_timestamp - self.start_timestamp
            ).total_seconds()
        self._update_session_metrics()

    def _update_session_metrics(self):
        """Update session-level metrics based on scan results."""
        self.total_urls_scanned = len(self.scan_results)
        self.successful_scans = sum(1 for result in self.scan_results if result.success)
        self.failed_scans = self.total_urls_scanned - self.successful_scans

        # Update platform distribution
        self.platform_distribution.clear()
        for result in self.scan_results:
            if result.success:
                platform = result.platform.value
                self.platform_distribution[platform] = (
                    self.platform_distribution.get(platform, 0) + 1
                )

    def get_successful_results(self) -> List[ScanResult]:
        """Get all successful scan results."""
        return [result for result in self.scan_results if result.success]

    def get_failed_results(self) -> List[ScanResult]:
        """Get all failed scan results."""
        return [result for result in self.scan_results if not result.success]

    def get_results_by_platform(self, platform: LowCodePlatform) -> List[ScanResult]:
        """Get scan results for a specific platform."""
        return [
            result
            for result in self.scan_results
            if result.platform == platform and result.success
        ]

    @computed_field
    @property
    def session_summary(self) -> Dict[str, Any]:
        """Generate a summary of the entire scanning session."""
        successful_results = self.get_successful_results()

        if not successful_results:
            return {
                "session_id": self.session_id,
                "total_scans": self.total_urls_scanned,
                "success_rate": 0.0,
                "message": "No successful scans completed",
            }

        average_score = sum(
            result.performance_matrix.overall_score for result in successful_results
        ) / len(successful_results)

        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "total_scans": self.total_urls_scanned,
            "successful_scans": self.successful_scans,
            "failed_scans": self.failed_scans,
            "success_rate": (self.successful_scans / self.total_urls_scanned * 100)
            if self.total_urls_scanned > 0
            else 0,
            "average_performance_score": average_score,
            "performance_category": PerformanceCategory.from_score(average_score).value,
            "platforms_tested": len(self.platform_distribution),
            "platform_distribution": self.platform_distribution,
            "total_duration_s": self.total_duration_s,
            "start_time": self.start_timestamp.isoformat()
            if self.start_timestamp
            else None,
            "end_time": self.end_timestamp.isoformat() if self.end_timestamp else None,
        }

    @field_validator("start_timestamp")
    @classmethod
    def ensure_start_timezone(cls, v):
        """Ensure start timestamp has timezone information."""
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("end_timestamp")
    @classmethod
    def ensure_end_timezone(cls, v):
        """Ensure end timestamp has timezone information."""
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ComparisonReport(BaseModel):
    """Comparative analysis report for multiple URLs or time periods."""

    report_id: str = Field(..., description="Unique report identifier")
    report_title: str = Field(..., description="Report title")
    report_type: str = Field(
        default="comparison", description="Type of comparison report"
    )

    # Comparison Data
    baseline_result: Optional[ScanResult] = Field(
        default=None, description="Baseline scan result"
    )
    comparison_results: List[ScanResult] = Field(
        default_factory=list, description="Results to compare against baseline"
    )

    # Analysis Results
    performance_improvements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Identified performance improvements"
    )
    performance_regressions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Identified performance regressions"
    )

    # Key Insights
    key_findings: List[str] = Field(
        default_factory=list, description="Key findings from comparison"
    )
    recommendations: List[Dict[str, Union[str, MetricSeverity]]] = Field(
        default_factory=list, description="Recommendations based on comparison"
    )

    # Report Metadata
    generated_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Report generation timestamp",
    )

    def add_comparison_result(self, result: ScanResult):
        """Add a result to compare against the baseline."""
        self.comparison_results.append(result)

    def set_baseline(self, result: ScanResult):
        """Set the baseline result for comparison."""
        self.baseline_result = result

    def analyze_differences(self):
        """Analyze differences between baseline and comparison results."""
        if not self.baseline_result or not self.comparison_results:
            return

        baseline_score = self.baseline_result.performance_matrix.overall_score

        for result in self.comparison_results:
            comparison_score = result.performance_matrix.overall_score
            score_diff = comparison_score - baseline_score

            if score_diff > 5:  # Significant improvement
                self.performance_improvements.append(
                    {
                        "url": result.url,
                        "score_improvement": score_diff,
                        "baseline_score": baseline_score,
                        "new_score": comparison_score,
                        "analysis": f"Performance improved by {score_diff:.1f} points",
                    }
                )
            elif score_diff < -5:  # Significant regression
                self.performance_regressions.append(
                    {
                        "url": result.url,
                        "score_regression": abs(score_diff),
                        "baseline_score": baseline_score,
                        "new_score": comparison_score,
                        "analysis": f"Performance regressed by {abs(score_diff):.1f} points",
                    }
                )

    @field_validator("generated_timestamp")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone information."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
