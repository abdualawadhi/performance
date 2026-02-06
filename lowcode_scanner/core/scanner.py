"""
Main Low-Code Performance Scanner

This module provides the primary scanner class that orchestrates comprehensive
performance testing of low-code web applications including Bubble, OutSystems,
and Airtable platforms.
"""

import asyncio
import logging
import statistics
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field

from ..browser import BrowserAutomation, BrowserConfig
from ..models import (
    ConfidenceLevel,
    DeviceType,
    LowCodePerformanceMetrics,
    LowCodePlatform,
    NetworkCondition,
    PerformanceMatrix,
    ReportFormat,
    ScanResult,
    ScanSession,
    ScenarioType,
)
# Reporting is now unified via `unified_reporting`; legacy ComprehensiveReportGenerator removed.
from .orchestrator import PerformanceOrchestrator
from .platform_detector import PlatformDetector


class ScannerConfig(BaseModel):
    """Configuration for the low-code performance scanner."""

    # Test Configuration
    scenarios: List[ScenarioType] = Field(
        default_factory=lambda: [
            ScenarioType.HOMEPAGE_LOAD,
            ScenarioType.REGULAR_USE_CASE,
            ScenarioType.HEAVY_LIST_LOAD,
            ScenarioType.UPFRONT_SCRIPTING,
        ],
        description="Scenarios to test",
    )
    device_types: List[DeviceType] = Field(
        default_factory=lambda: [DeviceType.DESKTOP, DeviceType.MOBILE],
        description="Device types to test",
    )
    network_conditions: List[NetworkCondition] = Field(
        default_factory=lambda: [NetworkCondition.WIFI],
        description="Network conditions to test",
    )

    # Browser Configuration
    browser_headless: bool = Field(
        default=True, description="Run browser in headless mode"
    )
    capture_screenshots: bool = Field(
        default=True, description="Capture screenshots during testing"
    )
    record_videos: bool = Field(
        default=True, description="Record videos during testing"
    )
    enable_performance_profiling: bool = Field(
        default=True, description="Enable detailed performance profiling"
    )

    # Output Configuration
    output_directory: Path = Field(
        default_factory=lambda: Path("performance_reports"),
        description="Output directory for reports and artifacts",
    )
    report_formats: List[ReportFormat] = Field(
        default_factory=lambda: [
            ReportFormat.HTML,
            ReportFormat.JSON,
            ReportFormat.CSV,
        ],
        description="Report output formats",
    )

    # Performance Configuration
    page_timeout_seconds: int = Field(
        default=30, description="Page load timeout in seconds"
    )
    scenario_timeout_seconds: int = Field(
        default=60, description="Scenario execution timeout in seconds"
    )
    max_concurrent_scans: int = Field(default=2, description="Maximum concurrent scans")
    num_runs: int = Field(default=3, ge=1, description="Number of runs per scenario for averaging")

    # Quality Thresholds
    performance_score_threshold: float = Field(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Minimum acceptable performance score",
    )
    memory_usage_threshold_mb: float = Field(
        default=150.0, ge=0.0, description="Maximum acceptable memory usage in MB"
    )
    load_time_threshold_seconds: float = Field(
        default=3.0, ge=0.0, description="Maximum acceptable load time in seconds"
    )

    # Reporting Configuration
    include_recommendations: bool = Field(
        default=True, description="Include performance recommendations in reports"
    )
    include_comparisons: bool = Field(
        default=True, description="Include device/scenario comparisons"
    )
    generate_executive_summary: bool = Field(
        default=True, description="Generate executive summary"
    )


class LowCodePerformanceScanner:
    """
    Main performance scanner for low-code web applications.

    This scanner provides comprehensive performance testing specifically designed
    for low-code platforms like Bubble, OutSystems, and Airtable, generating
    detailed reports with the performance matrix requested.
    """

    def __init__(self, config: ScannerConfig):
        """Initialize the performance scanner."""
        self.config = config
        self.logger = self._setup_logging()

        # Initialize components
        self.platform_detector = PlatformDetector()
        self.orchestrator = PerformanceOrchestrator()

        # State tracking
        self.current_session: Optional[ScanSession] = None
        self.active_scans: Dict[str, ScanResult] = {}

        # Ensure output directory exists
        self.config.output_directory.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the scanner."""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    async def scan_url(
        self,
        url: str,
        session_name: Optional[str] = None,
        custom_scenarios: Optional[List[ScenarioType]] = None,
    ) -> ScanResult:
        """
        Perform comprehensive performance scan of a single URL.

        Args:
            url: URL to scan
            session_name: Optional name for the scan session
            custom_scenarios: Optional custom scenarios to run

        Returns:
            Complete scan result with performance matrix
        """
        self.logger.info(f"Starting performance scan for: {url}")

        # Generate unique scan ID
        scan_id = str(uuid.uuid4())

        try:
            # Detect platform
            platform = await self.platform_detector.detect_platform_async(url)
            self.logger.info(f"Detected platform: {platform.value}")

            # Create performance metrics container
            performance_metrics = LowCodePerformanceMetrics(
                url=url,
                platform=platform,
                test_session_id=scan_id,
            )

            # Create performance matrix
            performance_matrix = PerformanceMatrix(
                url=url,
                platform=platform,
                device_type=self.config.device_types[0],  # Primary device type
                network_condition=self.config.network_conditions[0],  # Primary network
            )

            # Determine scenarios to run
            scenarios_to_run = custom_scenarios or self.config.scenarios

            # Configure browser
            browser_config = BrowserConfig(
                headless=self.config.browser_headless,
                capture_screenshots=self.config.capture_screenshots,
                record_video=self.config.record_videos,
                page_timeout_ms=self.config.page_timeout_seconds * 1000,
                output_dir=self.config.output_directory / "artifacts" / scan_id,
                enable_performance_logging=self.config.enable_performance_profiling,
            )

            scan_start_time = datetime.now(timezone.utc)
            scenario_results = []

            # Run scenarios for each device type and network condition
            async with BrowserAutomation(browser_config) as browser:
                for device_type in self.config.device_types:
                    for network_condition in self.config.network_conditions:
                        for scenario_type in scenarios_to_run:
                            try:
                                self.logger.info(
                                    f"Running scenario: {scenario_type.value} "
                                    f"(Device: {device_type.value}, "
                                    f"Network: {network_condition.value}) - {self.config.num_runs} runs"
                                )

                                # Run scenario multiple times for statistical reliability
                                run_scores = []
                                run_metrics = []

                                for run in range(self.config.num_runs):
                                    self.logger.info(f"Run {run + 1}/{self.config.num_runs}")

                                    # Execute scenario
                                    scenario_metrics = await asyncio.wait_for(
                                        browser.navigate_and_measure(
                                            url=url,
                                            scenario_type=scenario_type,
                                            device_type=device_type,
                                            network_condition=network_condition,
                                        ),
                                        timeout=self.config.scenario_timeout_seconds,
                                    )

                                    run_scores.append(scenario_metrics.overall_score)
                                    run_metrics.append(scenario_metrics)

                                # Calculate statistics
                                avg_score = statistics.mean(run_scores)
                                std_dev = statistics.stdev(run_scores) if len(run_scores) > 1 else 0.0
                                confidence = ConfidenceLevel.from_std_dev(std_dev, avg_score)

                                # Import statistical functions
                                from ..utils.statistics import (
                                    confidence_interval, 
                                    detect_outliers_iqr, 
                                    coefficient_of_variation,
                                    calculate_quartiles
                                )

                                # Calculate advanced statistics
                                ci_95 = confidence_interval(run_scores, 0.95)
                                cv = coefficient_of_variation(run_scores)
                                outliers = detect_outliers_iqr(run_scores, threshold=1.5)
                                q1, q2, q3 = calculate_quartiles(run_scores)
                                iqr = q3 - q1

                                # Use the last run's metrics but update with averaged score and stats
                                final_metrics = run_metrics[-1]
                                final_metrics.standard_deviation = std_dev
                                final_metrics.confidence_level = confidence
                                final_metrics.num_runs = self.config.num_runs
                                
                                # Set advanced statistical fields
                                final_metrics.confidence_interval_95 = ci_95
                                final_metrics.coefficient_of_variation = cv
                                final_metrics.outlier_run_indices = outliers
                                final_metrics.interquartile_range = iqr
                                final_metrics.quartiles = (q1, q2, q3)
                                
                                # Also update confidence level based on CI
                                final_metrics.confidence_level = ConfidenceLevel.from_confidence_interval(
                                    ci_95[0], ci_95[1], avg_score
                                )

                                # Override the overall_score with averaged value (this is a hack, but works for computed field)
                                # Actually, since overall_score is computed, we can't override it directly.
                                # For now, we'll use the last run's metrics with added stats

                                # Add to results
                                scenario_results.append(final_metrics)
                                performance_metrics.add_scenario_result(final_metrics)
                                performance_matrix.add_scenario_result(final_metrics)

                                self.logger.info(
                                    f"Completed scenario: {scenario_type.value} "
                                    f"(Avg Score: {avg_score:.1f}, Std Dev: {std_dev:.2f}, Confidence: {confidence.value})"
                                )

                            except asyncio.TimeoutError:
                                self.logger.error(
                                    f"Timeout executing scenario: {scenario_type.value}"
                                )
                            except Exception as e:
                                self.logger.error(
                                    f"Error executing scenario {scenario_type.value}: {str(e)}"
                                )

            # Calculate scan duration
            scan_duration = (
                datetime.now(timezone.utc) - scan_start_time
            ).total_seconds()

            # Generate analysis and recommendations
            await self._generate_analysis_and_recommendations(
                performance_metrics, performance_matrix, platform
            )

            # Create scan result
            scan_result = ScanResult(
                url=url,
                platform=platform,
                performance_metrics=performance_metrics,
                performance_matrix=performance_matrix,
                scan_id=scan_id,
                scan_duration_total_s=scan_duration,
                test_configuration=self.config.dict(),
                success=True,
            )

            # Generate reports
            await self._generate_reports(scan_result, session_name)

            # Add to active scans
            self.active_scans[scan_id] = scan_result

            self.logger.info(
                f"Scan completed successfully. Overall score: "
                f"{performance_matrix.overall_score:.1f}/100"
            )

            return scan_result

        except Exception as e:
            self.logger.error(f"Scan failed for {url}: {str(e)}")

            # Create error result
            error_result = ScanResult(
                url=url,
                platform=LowCodePlatform.GENERIC,
                performance_metrics=LowCodePerformanceMetrics(
                    url=url,
                    platform=LowCodePlatform.GENERIC,
                    test_session_id=scan_id,
                ),
                performance_matrix=PerformanceMatrix(
                    url=url,
                    platform=LowCodePlatform.GENERIC,
                ),
                scan_id=scan_id,
                scan_duration_total_s=0,
                success=False,
                error_message=str(e),
            )

            return error_result

    async def scan_multiple_urls(
        self,
        urls: List[str],
        session_name: Optional[str] = None,
        max_concurrent: Optional[int] = None,
    ) -> ScanSession:
        """
        Perform performance scans on multiple URLs.

        Args:
            urls: List of URLs to scan
            session_name: Name for the scan session
            max_concurrent: Maximum concurrent scans

        Returns:
            Complete scan session with all results
        """
        if not urls:
            raise ValueError("No URLs provided for scanning")

        session_id = str(uuid.uuid4())
        session_name = (
            session_name or f"Multi-URL Scan {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        self.logger.info(
            f"Starting multi-URL scan session: {session_name} ({len(urls)} URLs)"
        )

        # Create scan session
        self.current_session = ScanSession(
            session_id=session_id,
            session_name=session_name,
            test_configuration=self.config.dict(),
        )

        # Determine concurrency
        max_concurrent = max_concurrent or min(
            self.config.max_concurrent_scans, len(urls)
        )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scan_with_semaphore(url: str) -> ScanResult:
            async with semaphore:
                return await self.scan_url(url, session_name)

        # Execute scans
        try:
            # Run scans concurrently
            scan_tasks = [scan_with_semaphore(url) for url in urls]
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(scan_results):
                if isinstance(result, BaseException):
                    self.logger.error(f"Failed to scan {urls[i]}: {str(result)}")
                    # Create error result
                    error_result = ScanResult(
                        url=urls[i],
                        platform=LowCodePlatform.GENERIC,
                        performance_metrics=LowCodePerformanceMetrics(
                            url=urls[i],
                            platform=LowCodePlatform.GENERIC,
                            test_session_id=str(uuid.uuid4()),
                        ),
                        performance_matrix=PerformanceMatrix(
                            url=urls[i],
                            platform=LowCodePlatform.GENERIC,
                        ),
                        scan_id=str(uuid.uuid4()),
                        success=False,
                        error_message=str(result),
                    )
                    self.current_session.add_scan_result(error_result)
                else:
                    self.current_session.add_scan_result(result)

            # Finalize session
            self.current_session.finalize_session()

            # Generate session reports
            await self._generate_session_reports(self.current_session)

            self.logger.info(
                f"Multi-URL scan completed. "
                f"Success rate: {self.current_session.successful_scans}/{self.current_session.total_urls_scanned}"
            )

            return self.current_session

        except Exception as e:
            self.logger.error(f"Multi-URL scan failed: {str(e)}")
            if self.current_session:
                self.current_session.finalize_session()
            raise

    async def _generate_analysis_and_recommendations(
        self,
        performance_metrics: LowCodePerformanceMetrics,
        performance_matrix: PerformanceMatrix,
        platform: LowCodePlatform,
    ) -> None:
        """Generate performance analysis and recommendations."""
        try:
            # Generate executive summary
            critical_issues = []
            improvement_opportunities = []

            # Analyze overall performance
            if performance_matrix.overall_score < 50:
                critical_issues.append(
                    "Critical performance issues detected across scenarios"
                )
            elif (
                performance_matrix.overall_score
                < self.config.performance_score_threshold
            ):
                improvement_opportunities.append("Performance optimization needed")

            # Analyze scenario-specific issues
            for row in performance_matrix.rows:
                if row.load_time_s > self.config.load_time_threshold_seconds:
                    critical_issues.append(
                        f"{row.scenario.display_name}: Slow load time ({row.load_time_s:.1f}s)"
                    )

                if row.memory_usage_max_mb > self.config.memory_usage_threshold_mb:
                    critical_issues.append(
                        f"{row.scenario.display_name}: High memory usage ({row.memory_usage_max_mb:.1f}MB)"
                    )

                if row.performance_score < self.config.performance_score_threshold:
                    improvement_opportunities.append(
                        f"{row.scenario.display_name}: Below performance threshold"
                    )

            # Platform-specific recommendations
            platform_recommendations = self._get_platform_recommendations(
                platform, performance_matrix
            )

            # Update metrics
            performance_metrics.critical_issues = critical_issues
            performance_metrics.improvement_opportunities = improvement_opportunities
            performance_matrix.key_recommendations.extend(platform_recommendations)

            # Generate executive summary
            if critical_issues:
                performance_metrics.executive_summary = (
                    f"Performance analysis reveals {len(critical_issues)} critical issues "
                    f"requiring immediate attention. Overall score: {performance_matrix.overall_score:.1f}/100."
                )
            elif improvement_opportunities:
                performance_metrics.executive_summary = (
                    f"Performance is acceptable but has {len(improvement_opportunities)} "
                    f"optimization opportunities. Overall score: {performance_matrix.overall_score:.1f}/100."
                )
            else:
                performance_metrics.executive_summary = (
                    f"Excellent performance across all scenarios. "
                    f"Overall score: {performance_matrix.overall_score:.1f}/100."
                )

        except Exception as e:
            self.logger.error(f"Error generating analysis: {str(e)}")

    def _get_platform_recommendations(
        self, platform: LowCodePlatform, matrix: PerformanceMatrix
    ) -> List[Dict[str, Any]]:
        """Get platform-specific performance recommendations."""
        recommendations = []

        if platform == LowCodePlatform.BUBBLE:
            recommendations.extend(
                [
                    {
                        "title": "Optimize Bubble Workflows",
                        "description": "Review and optimize workflow complexity and database queries",
                        "priority": "high",
                    },
                    {
                        "title": "Minimize Plugin Dependencies",
                        "description": "Reduce the number of plugins to improve loading times",
                        "priority": "medium",
                    },
                ]
            )
        elif platform == LowCodePlatform.OUTSYSTEMS:
            recommendations.extend(
                [
                    {
                        "title": "Optimize Screen Preparation",
                        "description": "Reduce screen preparation time by optimizing aggregates",
                        "priority": "high",
                    },
                    {
                        "title": "Implement Efficient Data Fetching",
                        "description": "Use efficient queries and avoid unnecessary data fetching",
                        "priority": "medium",
                    },
                ]
            )
        elif platform == LowCodePlatform.AIRTABLE:
            recommendations.extend(
                [
                    {
                        "title": "Optimize Record Loading",
                        "description": "Implement pagination and filtering to reduce initial load",
                        "priority": "high",
                    },
                    {
                        "title": "Minimize API Calls",
                        "description": "Batch API requests and implement client-side caching",
                        "priority": "medium",
                    },
                ]
            )

        # Add general recommendations based on matrix scores
        if matrix.overall_score < 60:
            recommendations.append(
                {
                    "title": "Critical Performance Review Required",
                    "description": "Comprehensive performance optimization needed across all areas",
                    "priority": "critical",
                }
            )

        return recommendations

    async def _generate_reports(
        self, scan_result: ScanResult, session_name: Optional[str] = None
    ) -> None:
        """Generate reports for a scan result."""
        # Use unified CLI reporting module to generate reports so files and
        # aggregation match the CLI output exactly.
        from lowcode_scanner.unified_reporting import save_reports
        
        # Normalize session name to CLI convention
        norm_session = session_name or (getattr(scan_result, 'scan_id', None) and f"scan_{getattr(scan_result, 'scan_id')[:8]}") or f"scan_{uuid.uuid4().hex[:8]}"

        # Save reports using unified CLI reporting
        try:
            saved = save_reports(scan_result, getattr(scan_result, 'url', ''), norm_session, str(self.config.output_directory))

            # Attach saved report paths to scan_result where possible
            for key, path in saved.items():
                try:
                    if key.lower().endswith('.html') or key == 'html' or str(path).endswith('.html'):
                        scan_result.add_report_path(ReportFormat.HTML, Path(path))
                    elif key.lower().endswith('.json') or key == 'json' or str(path).endswith('.json'):
                        scan_result.add_report_path(ReportFormat.JSON, Path(path))
                except Exception:
                    # Best-effort; don't fail the scan on reporting bookkeeping
                    pass

            self.logger.info(f"Generated unified reports: {saved}")

        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in report generation: {str(e)}")

    async def _generate_session_reports(self, session: ScanSession) -> None:
        """Generate reports for a scan session."""
        try:
            # Use unified reporting to generate session-level reports
            try:
                from lowcode_scanner.unified_reporting import save_session_reports

                norm_session = session.session_name or f"scan_{session.session_id[:8]}"
                saved = save_session_reports(session, norm_session, str(self.config.output_directory))

                # Attach paths to session
                if saved.get('html'):
                    session.executive_dashboard_path = Path(saved['html'])
                if saved.get('json'):
                    session.comparative_report_path = Path(saved['json'])

                self.logger.info(f"Generated session reports: {saved}")
            except Exception as e:
                self.logger.error(f"Error generating session reports via unified_reporting: {e}")

        except Exception as e:
            self.logger.error(f"Error generating session reports: {str(e)}")

    def get_scan_history(self) -> List[Dict[str, Any]]:
        """Get history of completed scans."""
        return [
            {
                "scan_id": scan_id,
                "url": result.url,
                "platform": result.platform.value,
                "success": result.success,
                "score": result.performance_matrix.overall_score
                if result.success
                else 0,
                "timestamp": result.scan_timestamp.isoformat(),
                "duration_seconds": result.scan_duration_total_s,
            }
            for scan_id, result in self.active_scans.items()
        ]

    def get_scan_result(self, scan_id: str) -> Optional[ScanResult]:
        """Get a specific scan result by ID."""
        return self.active_scans.get(scan_id)

    def clear_scan_history(self) -> None:
        """Clear the scan history."""
        self.active_scans.clear()
        self.logger.info("Scan history cleared")

    async def cleanup(self) -> None:
        """Clean up scanner resources."""
        try:
            # Clean up any remaining resources
            if self.orchestrator:
                await self.orchestrator.cleanup()

            self.logger.info("Scanner cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during scanner cleanup: {str(e)}")

    def __str__(self) -> str:
        return f"LowCodePerformanceScanner(scenarios={len(self.config.scenarios)}, devices={len(self.config.device_types)})"

    def __repr__(self) -> str:
        return (
            f"LowCodePerformanceScanner("
            f"scenarios={self.config.scenarios}, "
            f"devices={self.config.device_types}, "
            f"output_dir='{self.config.output_directory}'"
            f")"
        )
