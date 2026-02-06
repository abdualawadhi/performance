"""
Comprehensive Performance Metrics Models for Low-Code Applications

This module contains detailed data models for capturing performance metrics
specifically tailored for low-code web applications like Bubble, OutSystems,
and Airtable.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, computed_field, field_validator

from .enums import (
    ConfidenceLevel,
    DeviceType,
    LowCodePlatform,
    MetricSeverity,
    NetworkCondition,
    PerformanceCategory,
    ResourceType,
    ScenarioType,
    TracingEvent,
)


class CoreWebVitals(BaseModel):
    """Core Web Vitals metrics as defined by Google."""

    # Loading Performance
    first_contentful_paint_ms: float = Field(
        default=0.0, ge=0, description="Time to First Contentful Paint in milliseconds"
    )
    largest_contentful_paint_ms: float = Field(
        default=0.0,
        ge=0,
        description="Time to Largest Contentful Paint in milliseconds",
    )

    # Interactivity
    first_input_delay_ms: float = Field(
        default=0.0, ge=0, description="First Input Delay in milliseconds"
    )
    time_to_interactive_ms: float = Field(
        default=0.0, ge=0, description="Time to Interactive in milliseconds"
    )
    total_blocking_time_ms: float = Field(
        default=0.0, ge=0, description="Total Blocking Time in milliseconds"
    )

    # Visual Stability
    cumulative_layout_shift: float = Field(
        default=0.0, ge=0, description="Cumulative Layout Shift score"
    )

    # Additional Performance Metrics
    speed_index_ms: float = Field(
        default=0.0, ge=0, description="Speed Index in milliseconds"
    )
    dom_content_loaded_ms: float = Field(
        default=0.0, ge=0, description="DOMContentLoaded event timing in milliseconds"
    )
    load_event_ms: float = Field(
        default=0.0, ge=0, description="Load event timing in milliseconds"
    )

    @computed_field
    @property
    def performance_score(self) -> float:
        """Calculate overall performance score based on Core Web Vitals."""
        # Core Web Vitals scoring
        lcp_score = max(0, 100 - (self.largest_contentful_paint_ms - 2500) * 0.02)
        fid_score = max(0, 100 - (self.first_input_delay_ms - 100) * 0.3)
        cls_score = max(0, 100 - self.cumulative_layout_shift * 1500)
        speed_score = max(0, 100 - self.speed_index_ms * 0.01)

        # Use speed_index_ms as primary metric for load performance
        # If speed_index_ms is 0, use a default poor score
        if self.speed_index_ms == 0:
            load_score = 30  # Poor score for unmeasured load time
        else:
            load_score = max(0, 100 - (self.speed_index_ms - 3000) * 0.02)  # 3s = 100, 53s = 0

        # Weighted average - prioritize load performance
        cwv_score = (
            load_score * 0.4
            + lcp_score * 0.2
            + fid_score * 0.2
            + cls_score * 0.1
            + speed_score * 0.1
        )

        return min(100, max(0, cwv_score))

    @computed_field
    @property
    def category(self) -> PerformanceCategory:
        """Performance category based on the overall score."""
        return PerformanceCategory.from_score(self.performance_score)


class MemoryUsageMetrics(BaseModel):
    """Memory usage metrics during performance testing."""

    initial_heap_size_mb: float = Field(
        default=0.0, ge=0, description="Initial JavaScript heap size in MB"
    )
    peak_heap_size_mb: float = Field(
        default=0.0, ge=0, description="Peak JavaScript heap size in MB"
    )
    final_heap_size_mb: float = Field(
        default=0.0, ge=0, description="Final JavaScript heap size in MB"
    )

    # DOM Memory
    dom_nodes_count: int = Field(
        default=0, ge=0, description="Total number of DOM nodes"
    )
    dom_listeners_count: int = Field(
        default=0, ge=0, description="Total number of event listeners"
    )

    # Memory Events
    major_gc_count: int = Field(
        default=0, ge=0, description="Number of major garbage collections"
    )
    minor_gc_count: int = Field(
        default=0, ge=0, description="Number of minor garbage collections"
    )
    total_gc_time_ms: float = Field(
        default=0.0, ge=0, description="Total time spent in garbage collection"
    )

    # Memory Timeline
    memory_samples: List[Dict[str, float]] = Field(
        default_factory=list, description="Memory usage samples over time"
    )

    @computed_field
    @property
    def memory_efficiency_score(self) -> float:
        """Calculate memory efficiency score (0-100)."""
        # Penalize high peak memory usage more aggressively
        base_score = 100

        # Peak memory penalty - start penalizing above 15MB (more realistic threshold)
        if self.peak_heap_size_mb > 15:
            base_score -= (self.peak_heap_size_mb - 15) * 2  # 2 points per MB over 15MB
        
        # Additional penalty for very high memory usage (>50MB)
        if self.peak_heap_size_mb > 50:
            base_score -= (self.peak_heap_size_mb - 50) * 1  # Additional penalty

        # GC penalty
        base_score -= self.major_gc_count * 2
        base_score -= self.minor_gc_count * 0.1

        # DOM complexity penalty
        if self.dom_nodes_count > 5000:
            base_score -= (self.dom_nodes_count - 5000) * 0.001

        return max(0, min(100, base_score))

    @computed_field
    @property
    def memory_growth_rate(self) -> float:
        """Calculate memory growth rate from initial to peak."""
        if self.initial_heap_size_mb == 0:
            return 0.0
        return (
            self.peak_heap_size_mb - self.initial_heap_size_mb
        ) / self.initial_heap_size_mb


class NetworkMetrics(BaseModel):
    """Network performance metrics."""

    total_requests: int = Field(
        default=0, ge=0, description="Total number of network requests"
    )
    failed_requests: int = Field(
        default=0, ge=0, description="Number of failed requests"
    )

    # Transfer Metrics
    total_transfer_size_kb: float = Field(
        default=0.0, ge=0, description="Total transfer size in KB"
    )
    total_resource_size_kb: float = Field(
        default=0.0, ge=0, description="Total uncompressed resource size in KB"
    )

    # Timing Metrics
    avg_response_time_ms: float = Field(
        default=0.0, ge=0, description="Average response time in milliseconds"
    )
    slowest_request_ms: float = Field(
        default=0.0, ge=0, description="Slowest request time in milliseconds"
    )

    # Resource Breakdown
    resource_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Breakdown of requests by resource type"
    )

    # Compression Metrics
    compression_ratio: float = Field(
        default=0.0, ge=0, le=1, description="Overall compression ratio"
    )

    # Caching Metrics
    cached_resources: int = Field(
        default=0, ge=0, description="Number of resources served from cache"
    )
    cache_hit_ratio: float = Field(
        default=0.0, ge=0, le=1, description="Cache hit ratio"
    )

    @computed_field
    @property
    def network_efficiency_score(self) -> float:
        """Calculate network efficiency score (0-100)."""
        base_score = 100

        # Request count penalty - start penalizing above 25 requests (more realistic)
        if self.total_requests > 25:
            base_score -= (self.total_requests - 25) * 0.5  # 0.5 points per request over 25

        # Transfer size penalty - start penalizing above 500KB (more realistic)
        if self.total_transfer_size_kb > 500:
            base_score -= (self.total_transfer_size_kb - 500) * 0.02  # 0.02 points per KB over 500KB

        # Failed requests penalty
        if self.total_requests > 0:
            failure_rate = self.failed_requests / self.total_requests
            base_score -= failure_rate * 50

        # Bonus for good compression and caching
        base_score += self.compression_ratio * 10
        base_score += self.cache_hit_ratio * 10

        return max(0, min(100, base_score))


class ResourceMetrics(BaseModel):
    """Individual resource performance metrics."""

    url: str = Field(..., description="Resource URL")
    resource_type: ResourceType = Field(..., description="Type of resource")

    # Size Metrics
    transfer_size_kb: float = Field(
        default=0.0, ge=0, description="Transfer size in KB"
    )
    resource_size_kb: float = Field(
        default=0.0, ge=0, description="Uncompressed resource size in KB"
    )

    # Timing Metrics
    start_time_ms: float = Field(
        default=0.0, ge=0, description="Request start time relative to navigation start"
    )
    response_time_ms: float = Field(
        default=0.0, ge=0, description="Total response time in milliseconds"
    )

    # HTTP Metrics
    status_code: int = Field(default=200, description="HTTP status code")
    from_cache: bool = Field(
        default=False, description="Whether resource was served from cache"
    )

    # Performance Impact
    blocking_time_ms: float = Field(
        default=0.0, ge=0, description="Time this resource blocked the main thread"
    )


class PerformanceTrace(BaseModel):
    """Performance tracing information."""

    event_type: TracingEvent = Field(..., description="Type of tracing event")
    timestamp_ms: float = Field(
        ..., ge=0, description="Event timestamp in milliseconds"
    )
    duration_ms: float = Field(
        default=0.0, ge=0, description="Event duration in milliseconds"
    )

    # Event Details
    name: str = Field(default="", description="Event name or identifier")
    category: str = Field(default="", description="Event category")

    # Context Information
    stack_trace: Optional[List[str]] = Field(
        default=None, description="JavaScript stack trace if applicable"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event details"
    )

    # Performance Impact
    cpu_time_ms: float = Field(
        default=0.0, ge=0, description="CPU time consumed by this event"
    )

    @computed_field
    @property
    def relative_timestamp_s(self) -> float:
        """Timestamp in seconds for easier reading."""
        return self.timestamp_ms / 1000


class PlatformSpecificMetrics(BaseModel):
    """Platform-specific performance metrics for low-code applications."""

    platform: LowCodePlatform = Field(..., description="Detected platform")

    # Bubble-specific metrics
    bubble_workflow_count: int = Field(
        default=0, ge=0, description="Number of Bubble workflows executed"
    )
    bubble_database_calls: int = Field(
        default=0, ge=0, description="Number of database calls made"
    )
    bubble_plugin_load_time_ms: float = Field(
        default=0.0, ge=0, description="Time to load Bubble plugins"
    )

    # OutSystems-specific metrics
    outsystems_screen_preparation_ms: float = Field(
        default=0.0, ge=0, description="OutSystems screen preparation time"
    )
    outsystems_aggregates_count: int = Field(
        default=0, ge=0, description="Number of aggregates executed"
    )

    # Airtable-specific metrics
    airtable_api_calls: int = Field(
        default=0, ge=0, description="Number of Airtable API calls"
    )
    airtable_record_count: int = Field(
        default=0, ge=0, description="Number of records loaded"
    )

    # Generic low-code metrics
    client_side_processing_ms: float = Field(
        default=0.0, ge=0, description="Time spent on client-side processing"
    )
    server_side_processing_ms: float = Field(
        default=0.0, ge=0, description="Time spent on server-side processing"
    )
    third_party_integrations: int = Field(
        default=0, ge=0, description="Number of third-party integrations used"
    )


class AccessibilityViolation(BaseModel):
    """Accessibility violation details."""

    id: str = Field(..., description="Rule ID")
    impact: Optional[str] = Field(None, description="Impact level (minor, moderate, serious, critical)")
    description: str = Field(..., description="Rule description")
    help_url: str = Field(..., description="URL for more help")
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Failing DOM nodes")


class AccessibilityMetrics(BaseModel):
    """Accessibility metrics from Axe."""

    score: float = Field(default=100.0, description="Accessibility score (0-100)")
    violations: List[AccessibilityViolation] = Field(default_factory=list, description="List of violations")
    passes: int = Field(default=0, description="Number of passed rules")
    incomplete: int = Field(default=0, description="Number of incomplete rules")
    inapplicable: int = Field(default=0, description="Number of inapplicable rules")

    @computed_field
    @property
    def critical_violations(self) -> int:
        """Count of critical violations."""
        return sum(1 for v in self.violations if v.impact == "critical")


class ScenarioMetrics(BaseModel):
    """Performance metrics for a specific test scenario."""

    scenario: ScenarioType = Field(..., description="Test scenario type")
    device_type: DeviceType = Field(..., description="Device type used for testing")
    network_condition: NetworkCondition = Field(..., description="Network condition")

    # Core Metrics
    core_web_vitals: CoreWebVitals = Field(..., description="Core Web Vitals metrics")
    memory_metrics: MemoryUsageMetrics = Field(..., description="Memory usage metrics")
    network_metrics: NetworkMetrics = Field(
        ..., description="Network performance metrics"
    )
    accessibility_metrics: Optional[AccessibilityMetrics] = Field(
        None, description="Accessibility metrics"
    )
    
    # Load Time Metrics
    load_time_s: float = Field(default=0.0, ge=0, description="Total page load time in seconds")

    # Platform Metrics
    platform_metrics: PlatformSpecificMetrics = Field(
        ..., description="Platform-specific metrics"
    )

    # Tracing Data
    performance_traces: List[PerformanceTrace] = Field(
        default_factory=list, description="Performance tracing events"
    )

    # Resource Details
    resources: List[ResourceMetrics] = Field(
        default_factory=list, description="Individual resource metrics"
    )

    # Screenshots and Videos
    screenshot_path: Optional[Path] = Field(
        default=None, description="Path to screenshot file"
    )
    video_path: Optional[Path] = Field(
        default=None, description="Path to video recording file"
    )
    timeline_path: Optional[Path] = Field(
        default=None, description="Path to performance timeline file"
    )

    # Key Observations
    key_observations: List[str] = Field(
        default_factory=list, description="Key performance observations"
    )
    recommendations: List[Dict[str, Union[str, MetricSeverity]]] = Field(
        default_factory=list, description="Performance recommendations"
    )

    # Test Metadata
    test_duration_ms: float = Field(
        default=0.0, ge=0, description="Total test duration in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Test execution timestamp",
    )
    user_agent: str = Field(default="", description="Browser user agent string")
    viewport_size: Dict[str, int] = Field(
        default_factory=dict, description="Browser viewport dimensions"
    )

    # Multi-run statistics
    standard_deviation: float = Field(
        default=0.0, ge=0, description="Standard deviation of performance scores across runs"
    )
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.TENTATIVE, description="Confidence level of measurements"
    )
    num_runs: int = Field(default=1, ge=1, description="Number of test runs averaged")
    
    # Advanced statistical measures
    confidence_interval_95: Tuple[float, float] = Field(
        default=(0.0, 0.0), 
        description="95% confidence interval for performance score (lower, upper)"
    )
    coefficient_of_variation: float = Field(
        default=0.0, ge=0, 
        description="Coefficient of variation (percentage) for performance metrics"
    )
    outlier_run_indices: List[int] = Field(
        default_factory=list, 
        description="Indices of runs identified as outliers using IQR method"
    )
    interquartile_range: float = Field(
        default=0.0, ge=0, 
        description="Interquartile range (Q3 - Q1) for performance score distribution"
    )
    quartiles: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0), 
        description="Quartiles (Q1, Q2, Q3) for performance score distribution"
    )

    @computed_field
    @property
    def overall_score(self) -> float:
        """Calculate overall performance score for this scenario."""
        # Calculate load time score (primary metric)
        if self.load_time_s == 0:
            load_score = 30  # Poor score for unmeasured load time
        else:
            load_score = max(0, 100 - (self.load_time_s - 3) * 8)  # 3s = 100, 15.5s = 0
        
        # Component scores
        cwv_score = self.core_web_vitals.performance_score * 0.3
        memory_score = self.memory_metrics.memory_efficiency_score * 0.2
        network_score = self.network_metrics.network_efficiency_score * 0.2
        load_score_weighted = load_score * 0.3  # Give load time significant weight

        return cwv_score + memory_score + network_score + load_score_weighted

    @computed_field
    @property
    def performance_category(self) -> PerformanceCategory:
        """Overall performance category for this scenario."""
        return PerformanceCategory.from_score(self.overall_score)

    def add_observation(
        self, observation: str, severity: MetricSeverity = MetricSeverity.MEDIUM
    ):
        """Add a key observation with optional severity."""
        self.key_observations.append(observation)

    def add_recommendation(
        self,
        title: str,
        description: str,
        severity: MetricSeverity = MetricSeverity.MEDIUM,
        category: str = "performance",
    ):
        """Add a performance recommendation."""
        self.recommendations.append(
            {
                "title": title,
                "description": description,
                "severity": severity,
                "category": category,
            }
        )

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone information."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class LowCodePerformanceMetrics(BaseModel):
    """Complete performance metrics for a low-code application URL."""

    url: str = Field(..., description="Target URL")
    platform: LowCodePlatform = Field(..., description="Detected platform")

    # Test Configuration
    test_session_id: str = Field(..., description="Unique test session identifier")
    test_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Test execution timestamp",
    )

    # Scenario Results
    scenarios: Dict[str, ScenarioMetrics] = Field(
        default_factory=dict, description="Results for each tested scenario"
    )

    # Aggregated Metrics
    average_score: float = Field(
        default=0.0, ge=0, le=100, description="Average performance score"
    )
    best_scenario: Optional[str] = Field(
        default=None, description="Best performing scenario"
    )
    worst_scenario: Optional[str] = Field(
        default=None, description="Worst performing scenario"
    )

    # Executive Summary
    executive_summary: str = Field(
        default="", description="Executive summary of findings"
    )
    critical_issues: List[str] = Field(
        default_factory=list, description="Critical performance issues identified"
    )
    improvement_opportunities: List[str] = Field(
        default_factory=list, description="Key improvement opportunities"
    )

    # Test Metadata
    test_duration_total_ms: float = Field(
        default=0.0, ge=0, description="Total test duration across all scenarios"
    )
    test_environment: Dict[str, Any] = Field(
        default_factory=dict, description="Test environment details"
    )

    def add_scenario_result(self, scenario_result: ScenarioMetrics):
        """Add results for a specific scenario."""
        scenario_key = (
            f"{scenario_result.scenario.value}_{scenario_result.device_type.value}"
        )
        self.scenarios[scenario_key] = scenario_result
        self._update_aggregated_metrics()

    def _update_aggregated_metrics(self):
        """Update aggregated metrics based on scenario results."""
        if not self.scenarios:
            return

        scores = [scenario.overall_score for scenario in self.scenarios.values()]
        self.average_score = sum(scores) / len(scores)

        # Find best and worst scenarios
        best_score = max(scores)
        worst_score = min(scores)

        for key, scenario in self.scenarios.items():
            if scenario.overall_score == best_score:
                self.best_scenario = key
            elif scenario.overall_score == worst_score:
                self.worst_scenario = key

    def get_scenario_by_type(
        self, scenario_type: ScenarioType, device_type: DeviceType = DeviceType.DESKTOP
    ) -> Optional[ScenarioMetrics]:
        """Get scenario results by type and device."""
        scenario_key = f"{scenario_type.value}_{device_type.value}"
        return self.scenarios.get(scenario_key)

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report for this URL."""
        return {
            "url": self.url,
            "platform": self.platform.value,
            "overall_score": self.average_score,
            "performance_category": PerformanceCategory.from_score(
                self.average_score
            ).value,
            "scenarios_tested": len(self.scenarios),
            "best_scenario": self.best_scenario,
            "worst_scenario": self.worst_scenario,
            "critical_issues_count": len(self.critical_issues),
            "test_timestamp": self.test_timestamp.isoformat(),
            "executive_summary": self.executive_summary,
        }

    @field_validator("test_timestamp")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone information."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Basic URL validation."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v
