"""
Browser Automation Module for Low-Code Performance Scanner

This module provides the main browser automation functionality using Playwright
for comprehensive performance testing of low-code web applications.
"""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
from pydantic import BaseModel, Field

from ..models.enums import (
    DeviceType,
    LowCodePlatform,
    NetworkCondition,
    ScenarioType,
    MetricSeverity,
)
from ..models.performance_metrics import (
    CoreWebVitals,
    MemoryUsageMetrics,
    NetworkMetrics,
    PerformanceTrace,
    ResourceMetrics,
    ScenarioMetrics,
)
from .memory_monitor import MemoryMonitor
from .network_monitor import NetworkMonitor
from .performance_tracer import PerformanceTracer
from .screenshot_handler import ScreenshotHandler
from .accessibility import AccessibilityMonitor


class BrowserConfig(BaseModel):
    """Configuration for browser automation."""

    # Browser Settings
    browser_type: str = Field(default="chromium", description="Browser type to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    disable_web_security: bool = Field(
        default=False, description="Disable web security for testing"
    )

    # Performance Settings
    enable_performance_logging: bool = Field(
        default=True, description="Enable performance logging"
    )
    enable_network_monitoring: bool = Field(
        default=True, description="Enable network monitoring"
    )
    enable_memory_monitoring: bool = Field(
        default=True, description="Enable memory monitoring"
    )

    # Timeouts
    page_timeout_ms: int = Field(
        default=30000, description="Page load timeout in milliseconds"
    )
    navigation_timeout_ms: int = Field(
        default=30000, description="Navigation timeout in milliseconds"
    )

    # Screenshots and Videos
    capture_screenshots: bool = Field(
        default=True, description="Capture screenshots during testing"
    )
    record_video: bool = Field(default=True, description="Record video during testing")
    video_size: Dict[str, int] = Field(
        default_factory=lambda: {"width": 1280, "height": 720},
        description="Video recording dimensions",
    )

    # Output Paths
    output_dir: Path = Field(
        default_factory=lambda: Path("performance_data"),
        description="Output directory for artifacts",
    )


class BrowserAutomation:
    """Main browser automation class for performance testing."""

    def __init__(self, config: BrowserConfig):
        """Initialize browser automation with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Browser instances
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Monitors and handlers
        self.memory_monitor: Optional[MemoryMonitor] = None
        self.network_monitor: Optional[NetworkMonitor] = None
        self.performance_tracer: Optional[PerformanceTracer] = None
        self.screenshot_handler: Optional[ScreenshotHandler] = None
        self.accessibility_monitor: Optional[AccessibilityMonitor] = None

        # State tracking
        self.is_initialized = False
        self.current_url: Optional[str] = None
        self.test_session_id: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize browser and monitoring systems."""
        try:
            self.logger.info("Initializing browser automation...")

            # Launch Playwright
            self.playwright = await async_playwright().start()

            # Launch browser
            browser_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--enable-precise-memory-info",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-background-networking",
            ]

            if self.config.disable_web_security:
                browser_args.extend(
                    [
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ]
                )

            self.browser = await getattr(
                self.playwright, self.config.browser_type
            ).launch(
                headless=self.config.headless,
                args=browser_args,
                chromium_sandbox=False,
            )

            # Create browser context
            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "ignore_https_errors": True,
            }

            if self.config.record_video:
                video_dir = self.config.output_dir / "videos"
                video_dir.mkdir(parents=True, exist_ok=True)
                context_options["record_video_dir"] = str(video_dir)
                context_options["record_video_size"] = self.config.video_size

            self.context = await self.browser.new_context(**context_options)

            # Set timeouts
            self.context.set_default_timeout(self.config.page_timeout_ms)
            self.context.set_default_navigation_timeout(
                self.config.navigation_timeout_ms
            )

            # Create page
            self.page = await self.context.new_page()

            # Add stealth mode scripts to hide automation
            await self.page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Override permissions query
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Hide automation in chrome runtime
                window.chrome = {
                    runtime: {},
                };
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ],
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)

            # Initialize monitors
            if self.config.enable_memory_monitoring:
                self.memory_monitor = MemoryMonitor(self.page)
                await self.memory_monitor.initialize()

            if self.config.enable_network_monitoring:
                self.network_monitor = NetworkMonitor(self.page)
                await self.network_monitor.initialize()

            if self.config.enable_performance_logging:
                self.performance_tracer = PerformanceTracer(self.page)
                await self.performance_tracer.initialize()

            if self.config.capture_screenshots:
                screenshot_dir = self.config.output_dir / "screenshots"
                self.screenshot_handler = ScreenshotHandler(self.page, screenshot_dir)

            self.accessibility_monitor = AccessibilityMonitor(self.page)

            self.is_initialized = True
            self.logger.info("Browser automation initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize browser automation: {str(e)}")
            await self.cleanup()
            raise

    async def configure_device(self, device_type: DeviceType) -> None:
        """Configure browser for specific device type."""
        if not self.is_initialized or not self.page:
            raise RuntimeError("Browser not initialized")

        viewport = device_type.viewport
        await self.page.set_viewport_size(
            {"width": viewport["width"], "height": viewport["height"]}
        )

        # Set user agent and additional headers to avoid bot detection
        if device_type == DeviceType.MOBILE:
            await self.page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                }
            )
        elif device_type == DeviceType.TABLET:
            await self.page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                }
            )
        else:  # Desktop
            await self.page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                }
            )

    async def configure_network(self, network_condition: NetworkCondition) -> None:
        """Configure network conditions for testing."""
        if not self.is_initialized or not self.context:
            raise RuntimeError("Browser not initialized")

        settings = network_condition.settings

        # Apply network throttling through CDP
        if self.page:
            await self.page.route("**/*", self._throttle_network)

            # Set network conditions via CDP
            cdp = await self.context.new_cdp_session(self.page)
            await cdp.send(
                "Network.emulateNetworkConditions",
                {
                    "offline": settings["offline"],
                    "downloadThroughput": settings["downloadThroughput"],
                    "uploadThroughput": settings["uploadThroughput"],
                    "latency": settings["latency"],
                },
            )

    async def _throttle_network(self, route):
        """Network throttling handler."""
        # Let the request proceed normally - throttling is handled by CDP
        await route.continue_()

    async def navigate_and_measure(
        self,
        url: str,
        scenario_type: ScenarioType,
        device_type: DeviceType = DeviceType.DESKTOP,
        network_condition: NetworkCondition = NetworkCondition.WIFI,
        wait_for_idle: bool = True,
    ) -> ScenarioMetrics:
        """Navigate to URL and measure performance metrics."""
        if not self.is_initialized or not self.page:
            raise RuntimeError("Browser not initialized")

        self.current_url = url
        platform = LowCodePlatform.detect_platform(url)

        self.logger.info(
            f"Starting performance measurement for {url} ({scenario_type.value})"
        )

        # Configure browser for test
        await self.configure_device(device_type)
        await self.configure_network(network_condition)

        # Start monitoring
        start_time = datetime.now(timezone.utc)

        if self.memory_monitor:
            await self.memory_monitor.start_monitoring()

        if self.network_monitor:
            await self.network_monitor.start_monitoring()

        if self.performance_tracer:
            await self.performance_tracer.start_tracing()

        # Take initial screenshot (for potential future use)
        if self.screenshot_handler:
            await self.screenshot_handler.capture_screenshot(
                f"{scenario_type.value}_initial"
            )

        try:
            # Navigate with retry mechanism
            max_retries = 3
            retry_delay = 3
            response = None

            for attempt in range(max_retries):
                try:
                    await self.page.wait_for_timeout(1500 + (attempt * 1000))

                    response = await self.page.goto(
                        url, wait_until="domcontentloaded", timeout=30000
                    )

                    if response and response.status == 200:
                        # Wait for network to settle
                        try:
                            await self.page.wait_for_load_state(
                                "networkidle", timeout=10000
                            )
                        except:
                            pass
                        break
                    elif response and response.status == 403:
                        print(f"Got 403 on attempt {attempt + 1}, retrying...")
                        if attempt < max_retries - 1:
                            await self.page.wait_for_timeout(retry_delay * 1000)
                            continue
                        else:
                            raise RuntimeError(f"Access denied (403) for {url}")
                    elif response and response.status >= 400:
                        raise RuntimeError(f"HTTP {response.status} for {url}")
                    else:
                        break

                except Exception as e:
                    error_str = str(e)
                    if "403" in error_str and attempt < max_retries - 1:
                        print(f"Got 403 on attempt {attempt + 1}, retrying...")
                        await self.page.wait_for_timeout(retry_delay * 1000)
                        continue
                    elif "ERR_NAME_NOT_RESOLVED" in error_str:
                        raise RuntimeError(f"DNS resolution failed for {url}")
                    elif "Timeout" in error_str and attempt < max_retries - 1:
                        self.logger.warning(
                            f"Timeout on attempt {attempt + 1}, retrying..."
                        )
                        continue
                    else:
                        raise

            if not response:
                raise RuntimeError(f"Failed to navigate to {url}")

            # Execute scenario-specific actions
            await self._execute_scenario_actions(scenario_type, platform)

            # Additional wait for stability
            await self.page.wait_for_timeout(2000)

            # Collect performance metrics
            performance_metrics = await self._collect_performance_metrics()
            memory_metrics = await self._collect_memory_metrics()
            network_metrics = await self._collect_network_metrics()
            traces = await self._collect_performance_traces()

            # Run accessibility scan
            accessibility_metrics = None
            if self.accessibility_monitor:
                accessibility_metrics = await self.accessibility_monitor.run_scan()

            # Take final screenshot
            final_screenshot = None
            if self.screenshot_handler:
                final_screenshot = await self.screenshot_handler.capture_screenshot(
                    f"{scenario_type.value}_final"
                )

            # Stop monitoring
            end_time = datetime.now(timezone.utc)
            test_duration_ms = (end_time - start_time).total_seconds() * 1000

            if self.memory_monitor:
                await self.memory_monitor.stop_monitoring()

            if self.network_monitor:
                await self.network_monitor.stop_monitoring()

            if self.performance_tracer:
                await self.performance_tracer.stop_tracing()

            # Create scenario metrics
            scenario_metrics = ScenarioMetrics(
                scenario=scenario_type,
                device_type=device_type,
                network_condition=network_condition,
                core_web_vitals=performance_metrics,
                memory_metrics=memory_metrics,
                network_metrics=network_metrics,
                accessibility_metrics=accessibility_metrics,
                platform_metrics=await self._collect_platform_metrics(platform),
                performance_traces=traces,
                resources=await self._collect_resource_metrics(),
                screenshot_path=final_screenshot,
                test_duration_ms=test_duration_ms,
                timestamp=start_time,
                user_agent=(
                    await self.page.evaluate("() => navigator.userAgent")
                    if self.page
                    else ""
                ),
                viewport_size=device_type.viewport,
            )

            # Add scenario-specific observations
            await self._add_scenario_observations(
                scenario_metrics, scenario_type, platform
            )

            return scenario_metrics

        except Exception as e:
            self.logger.error(f"Error during performance measurement: {str(e)}")
            raise
        finally:
            # Ensure monitoring is stopped
            if self.memory_monitor:
                await self.memory_monitor.stop_monitoring()
            if self.network_monitor:
                await self.network_monitor.stop_monitoring()
            if self.performance_tracer:
                await self.performance_tracer.stop_tracing()

    async def _execute_scenario_actions(
        self, scenario_type: ScenarioType, platform: LowCodePlatform
    ) -> None:
        """Execute actions specific to the test scenario."""
        if not self.page:
            return

        if scenario_type == ScenarioType.HOMEPAGE_LOAD:
            # Just wait for initial load - no additional actions
            await self.page.wait_for_timeout(1000)

        elif scenario_type == ScenarioType.REGULAR_USE_CASE:
            # Simulate typical user interactions
            await self._simulate_user_interactions(platform)

        elif scenario_type == ScenarioType.HEAVY_LIST_LOAD:
            # Try to trigger list loading
            await self._trigger_list_loading(platform)

        elif scenario_type == ScenarioType.UPFRONT_SCRIPTING:
            # Focus on script execution - minimal interaction
            await self.page.wait_for_timeout(3000)

        elif scenario_type == ScenarioType.FORM_SUBMISSION:
            # Try to find and interact with forms
            await self._interact_with_forms(platform)

        elif scenario_type == ScenarioType.DATA_FILTERING:
            # Try to filter or sort data
            await self._filter_data(platform)

        elif scenario_type == ScenarioType.PAGE_NAVIGATION:
            # Try to navigate to other pages
            await self._navigate_pages(platform)

    async def _simulate_user_interactions(self, platform: LowCodePlatform) -> None:
        """Simulate typical user interactions based on platform."""
        if not self.page:
            return

        try:
            # Look for common interactive elements
            selectors = [
                "button",
                "a",
                "[role='button']",
                ".btn",
                ".button",
                "input[type='text']",
                "input[type='search']",
                "textarea",
            ]

            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    # Click first few interactive elements
                    for i, element in enumerate(elements[:3]):
                        try:
                            if await element.is_visible():
                                await element.click(timeout=1000)
                                await self.page.wait_for_timeout(500)
                                break
                        except:
                            continue
                    break

            # Scroll the page to trigger lazy loading
            await self.page.evaluate("""
                () => {
                    window.scrollTo(0, document.body.scrollHeight / 2);
                }
            """)
            await self.page.wait_for_timeout(1000)

        except Exception as e:
            self.logger.debug(f"Error simulating user interactions: {str(e)}")

    async def _trigger_list_loading(self, platform: LowCodePlatform) -> None:
        """Attempt to trigger heavy list loading."""
        if not self.page:
            return

        try:
            # Platform-specific list triggers
            if platform == LowCodePlatform.BUBBLE:
                # Look for Bubble repeating groups
                await self.page.evaluate("""
                    () => {
                        const repeatingGroups = document.querySelectorAll('[data-type="RepeatingGroup"]');
                        repeatingGroups.forEach(rg => {
                            if (rg.scrollIntoView) rg.scrollIntoView();
                        });
                    }
                """)

            elif platform == LowCodePlatform.AIRTABLE:
                # Scroll to load more records
                await self.page.evaluate("""
                    () => {
                        const containers = document.querySelectorAll('.tableContainer, .gridContainer');
                        containers.forEach(container => {
                            container.scrollTop = container.scrollHeight;
                        });
                    }
                """)

            # Generic approach - scroll and look for pagination
            await self.page.evaluate(
                "() => window.scrollTo(0, document.body.scrollHeight)"
            )
            await self.page.wait_for_timeout(2000)

            # Look for load more buttons
            load_more_selectors = [
                "button:has-text('Load More')",
                "button:has-text('Show More')",
                ".load-more",
                ".show-more",
                "[aria-label*='load more']",
            ]

            for selector in load_more_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        await self.page.wait_for_timeout(2000)
                        break
                except:
                    continue

        except Exception as e:
            self.logger.debug(f"Error triggering list loading: {str(e)}")

    async def _interact_with_forms(self, platform: LowCodePlatform) -> None:
        """Interact with forms on the page."""
        if not self.page:
            return

        try:
            # Find text inputs and fill them
            inputs = await self.page.query_selector_all(
                "input[type='text'], input[type='email'], textarea"
            )
            for i, input_element in enumerate(inputs[:3]):  # Limit to first 3 inputs
                if await input_element.is_visible():
                    await input_element.fill(
                        f"test{i}@example.com" if "@" in str(i) else f"Test Value {i}"
                    )
                    await self.page.wait_for_timeout(200)

            # Look for submit buttons
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit')",
                "button:has-text('Save')",
                ".submit-btn",
            ]

            for selector in submit_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        # Don't actually submit - just hover to trigger validation
                        await element.hover()
                        await self.page.wait_for_timeout(500)
                        break
                except:
                    continue

        except Exception as e:
            self.logger.debug(f"Error interacting with forms: {str(e)}")

    async def _filter_data(self, platform: LowCodePlatform) -> None:
        """Interact with data filtering controls."""
        if not self.page:
            return

        try:
            # Look for select dropdowns (common for filters)
            selects = await self.page.query_selector_all("select")
            for select in selects[:2]:
                if await select.is_visible():
                    options = await select.query_selector_all("option")
                    if len(options) > 1:
                        # Select the second option
                        value = await options[1].get_attribute("value")
                        if value:
                            await select.select_option(value)
                            await self.page.wait_for_timeout(1000)

            # Look for sort headers
            sort_selectors = [
                "th.sortable",
                "[role='columnheader']",
                ".sort-header",
                "button[aria-label*='sort']",
            ]

            for selector in sort_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    for element in elements[:2]:
                        if await element.is_visible():
                            await element.click()
                            await self.page.wait_for_timeout(1000)
                    break

            # Look for search inputs
            search_inputs = await self.page.query_selector_all(
                "input[type='search'], input[placeholder*='Search'], input[placeholder*='search']"
            )
            if search_inputs:
                for input_el in search_inputs[:1]:
                    if await input_el.is_visible():
                        await input_el.fill("test")
                        await input_el.press("Enter")
                        await self.page.wait_for_timeout(1000)

        except Exception as e:
            self.logger.debug(f"Error filtering data: {str(e)}")

    async def _navigate_pages(self, platform: LowCodePlatform) -> None:
        """Navigate to different pages."""
        if not self.page:
            return

        try:
            # Look for navigation links
            nav_selectors = [
                "nav a",
                ".navbar a",
                ".menu a",
                "[role='navigation'] a",
                "a.nav-link",
            ]

            links_to_visit = []

            for selector in nav_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        if await element.is_visible():
                            href = await element.get_attribute("href")
                            if (
                                href
                                and href != "#"
                                and not href.startswith("javascript:")
                            ):
                                links_to_visit.append(element)
                    if links_to_visit:
                        break

            # Visit up to 2 links
            original_url = self.page.url
            for i, link in enumerate(links_to_visit[:2]):
                try:
                    await link.click()
                    await self.page.wait_for_load_state(
                        "domcontentloaded", timeout=10000
                    )
                    await self.page.wait_for_timeout(1000)

                    # Go back if we navigated away
                    if self.page.url != original_url:
                        await self.page.go_back()
                        await self.page.wait_for_load_state(
                            "domcontentloaded", timeout=10000
                        )
                except Exception as nav_e:
                    self.logger.debug(f"Navigation error: {str(nav_e)}")
                    # Try to recover by going to original URL
                    if self.page.url != original_url:
                        await self.page.goto(original_url)

        except Exception as e:
            self.logger.debug(f"Error navigating pages: {str(e)}")

    async def _collect_performance_metrics(self) -> CoreWebVitals:
        """Collect Core Web Vitals and performance metrics."""
        if not self.page:
            return CoreWebVitals()

        try:
            metrics = await self.page.evaluate("""
                () => {
                    const getMetric = (name) => {
                        const entries = performance.getEntriesByName(name);
                        return entries.length > 0 ? entries[entries.length - 1].value : 0;
                    };

                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    const timing = performance.timing || {};

                    let fcp = 0, lcp = 0;
                    paint.forEach(entry => {
                        if (entry.name === 'first-contentful-paint') fcp = entry.startTime;
                    });

                    // Calculate load event time more reliably
                    let loadEvent = 0;
                    if (navigation && navigation.loadEventEnd && navigation.loadEventStart) {
                        loadEvent = navigation.loadEventEnd - navigation.loadEventStart;
                    } else if (timing.loadEventEnd && timing.loadEventStart) {
                        loadEvent = timing.loadEventEnd - timing.loadEventStart;
                    } else if (navigation && navigation.domComplete && navigation.fetchStart) {
                        loadEvent = navigation.domComplete - navigation.fetchStart;
                    } else if (timing.domComplete && timing.navigationStart) {
                        loadEvent = timing.domComplete - timing.navigationStart;
                    }

                    return {
                        firstContentfulPaint: fcp,
                        largestContentfulPaint: getMetric('largest-contentful-paint') || lcp,
                        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
                        loadEvent: loadEvent,
                        speedIndex: navigation ? (navigation.loadEventEnd || navigation.domComplete || 0) * 0.85 : 0, 
                        timeToInteractive: getMetric('time-to-interactive') || 0,
                        firstInputDelay: getMetric('first-input-delay') || 0,
                        totalBlockingTime: getMetric('total-blocking-time') || 0,
                        cumulativeLayoutShift: getMetric('cumulative-layout-shift') || 0
                    };
                }
            """)

            return CoreWebVitals(
                first_contentful_paint_ms=metrics.get("firstContentfulPaint", 0),
                largest_contentful_paint_ms=metrics.get("largestContentfulPaint", 0),
                first_input_delay_ms=metrics.get("firstInputDelay", 0),
                time_to_interactive_ms=metrics.get("timeToInteractive", 0),
                total_blocking_time_ms=metrics.get("totalBlockingTime", 0),
                cumulative_layout_shift=metrics.get("cumulativeLayoutShift", 0),
                speed_index_ms=metrics.get("speedIndex", 0),
                dom_content_loaded_ms=metrics.get("domContentLoaded", 0),
                load_event_ms=metrics.get("loadEvent", 0),
            )

        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {str(e)}")
            return CoreWebVitals()

    async def _collect_memory_metrics(self) -> MemoryUsageMetrics:
        """Collect memory usage metrics."""
        if self.memory_monitor:
            return await self.memory_monitor.get_metrics()
        return MemoryUsageMetrics()

    async def _collect_network_metrics(self) -> NetworkMetrics:
        """Collect network performance metrics."""
        if self.network_monitor:
            return await self.network_monitor.get_metrics()
        return NetworkMetrics()

    async def _collect_performance_traces(self) -> List[PerformanceTrace]:
        """Collect performance tracing data."""
        if self.performance_tracer:
            return await self.performance_tracer.get_traces()
        return []

    async def _collect_resource_metrics(self) -> List[ResourceMetrics]:
        """Collect individual resource performance metrics."""
        if self.network_monitor:
            return await self.network_monitor.get_resource_metrics()
        return []

    async def _collect_platform_metrics(self, platform: LowCodePlatform):
        """Collect platform-specific metrics."""
        from ..models.performance_metrics import PlatformSpecificMetrics

        if not self.page:
            return PlatformSpecificMetrics(platform=platform)

        try:
            # Platform-specific metric collection
            if platform == LowCodePlatform.BUBBLE:
                bubble_metrics = await self.page.evaluate("""
                    () => {
                        return {
                            workflowCount: window.bubble_workflows ? window.bubble_workflows.length : 0,
                            databaseCalls: window.bubble_db_calls || 0,
                            pluginLoadTime: window.bubble_plugin_load_time || 0
                        };
                    }
                """)

                return PlatformSpecificMetrics(
                    platform=platform,
                    bubble_workflow_count=bubble_metrics.get("workflowCount", 0),
                    bubble_database_calls=bubble_metrics.get("databaseCalls", 0),
                    bubble_plugin_load_time_ms=bubble_metrics.get("pluginLoadTime", 0),
                )

            elif platform == LowCodePlatform.OUTSYSTEMS:
                outsystems_metrics = await self.page.evaluate("""
                    () => {
                        return {
                            screenPreparation: window.outsystems_screen_prep_time || 0,
                            aggregatesCount: window.outsystems_aggregates || 0
                        };
                    }
                """)

                return PlatformSpecificMetrics(
                    platform=platform,
                    outsystems_screen_preparation_ms=outsystems_metrics.get(
                        "screenPreparation", 0
                    ),
                    outsystems_aggregates_count=outsystems_metrics.get(
                        "aggregatesCount", 0
                    ),
                )

            elif platform == LowCodePlatform.AIRTABLE:
                airtable_metrics = await self.page.evaluate("""
                    () => {
                        return {
                            apiCalls: window.airtable_api_calls || 0,
                            recordCount: document.querySelectorAll('.record, .row').length
                        };
                    }
                """)

                return PlatformSpecificMetrics(
                    platform=platform,
                    airtable_api_calls=airtable_metrics.get("apiCalls", 0),
                    airtable_record_count=airtable_metrics.get("recordCount", 0),
                )

            # Generic low-code metrics
            generic_metrics = await self.page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script[src]');
                    const thirdPartyCount = Array.from(scripts).filter(script => {
                        const src = script.src;
                        return src && !src.includes(location.hostname);
                    }).length;

                    return {
                        thirdPartyIntegrations: thirdPartyCount,
                        clientSideProcessing: performance.now(),
                        serverSideProcessing: 0 // Would need server-side instrumentation
                    };
                }
            """)

            return PlatformSpecificMetrics(
                platform=platform,
                client_side_processing_ms=generic_metrics.get(
                    "clientSideProcessing", 0
                ),
                server_side_processing_ms=generic_metrics.get(
                    "serverSideProcessing", 0
                ),
                third_party_integrations=generic_metrics.get(
                    "thirdPartyIntegrations", 0
                ),
            )

        except Exception as e:
            self.logger.error(f"Error collecting platform metrics: {str(e)}")
            return PlatformSpecificMetrics(platform=platform)

    async def _add_scenario_observations(
        self,
        scenario_metrics: ScenarioMetrics,
        scenario_type: ScenarioType,
        platform: LowCodePlatform,
    ) -> None:
        """Add scenario-specific observations and recommendations."""
        score = scenario_metrics.overall_score
        cwv = scenario_metrics.core_web_vitals
        memory = scenario_metrics.memory_metrics
        network = scenario_metrics.network_metrics

        # General observations
        if score < 50:
            scenario_metrics.add_observation("Critical performance issues detected")
        elif score < 70:
            scenario_metrics.add_observation("Performance needs improvement")
        else:
            scenario_metrics.add_observation("Good performance detected")

        # Core Web Vitals observations
        if cwv.largest_contentful_paint_ms > 2500:
            scenario_metrics.add_observation(
                f"LCP is slow at {cwv.largest_contentful_paint_ms:.0f}ms"
            )

        if cwv.cumulative_layout_shift > 0.1:
            scenario_metrics.add_observation(
                f"Layout shift detected (CLS: {cwv.cumulative_layout_shift:.3f})"
            )

        # Memory observations
        if memory.peak_heap_size_mb > 100:
            scenario_metrics.add_observation(
                f"High memory usage: {memory.peak_heap_size_mb:.1f}MB"
            )

        if memory.major_gc_count > 3:
            scenario_metrics.add_observation(
                f"Frequent garbage collection: {memory.major_gc_count} major GCs"
            )

        # Network observations
        if network.total_requests > 100:
            scenario_metrics.add_observation(
                f"High request count: {network.total_requests} requests"
            )

        if network.total_transfer_size_kb > 2048:
            scenario_metrics.add_observation(
                f"Large page size: {network.total_transfer_size_kb:.0f}KB"
            )

        # Accessibility observations
        if scenario_metrics.accessibility_metrics:
            acc = scenario_metrics.accessibility_metrics
            if acc.score < 80:
                scenario_metrics.add_observation(
                    f"Accessibility issues detected (Score: {acc.score:.0f})"
                )
            if acc.critical_violations > 0:
                scenario_metrics.add_observation(
                    f"Critical accessibility violations: {acc.critical_violations}",
                    MetricSeverity.HIGH,
                )

        # Scenario-specific observations
        if scenario_type == ScenarioType.UPFRONT_SCRIPTING:
            scripting_time = sum(
                trace.duration_ms
                for trace in scenario_metrics.performance_traces
                if trace.event_type.category == "scripting"
            )
            if scripting_time > 1000:
                scenario_metrics.add_observation(
                    f"Heavy upfront scripting: {scripting_time:.0f}ms"
                )

        # Platform-specific observations
        if platform == LowCodePlatform.BUBBLE:
            if scenario_metrics.platform_metrics.bubble_database_calls > 10:
                scenario_metrics.add_observation(
                    "High number of database calls detected"
                )

        elif platform == LowCodePlatform.AIRTABLE:
            if scenario_metrics.platform_metrics.airtable_record_count > 100:
                scenario_metrics.add_observation("Large number of records loaded")

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.memory_monitor:
                await self.memory_monitor.cleanup()

            if self.network_monitor:
                await self.network_monitor.cleanup()

            if self.performance_tracer:
                await self.performance_tracer.cleanup()

            if self.page:
                await self.page.close()

            if self.context:
                await self.context.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()

            self.is_initialized = False
            self.logger.info("Browser automation cleaned up successfully")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
