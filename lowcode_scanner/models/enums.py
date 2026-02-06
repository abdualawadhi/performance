"""
Enums for Low-Code Performance Scanner

This module contains all enumeration types used throughout the low-code
web application performance scanner.
"""

from enum import Enum, auto


class LowCodePlatform(Enum):
    """Low-code platforms supported by the scanner."""

    BUBBLE = "bubble"
    OUTSYSTEMS = "outsystems"
    AIRTABLE = "airtable"
    MENDIX = "mendix"
    APPIAN = "appian"
    POWERAPPS = "powerapps"
    SALESFORCE = "salesforce"
    GENERIC = "generic"

    @classmethod
    def detect_platform(cls, url: str) -> "LowCodePlatform":
        """Detect platform from URL."""
        url_lower = url.lower()

        if "bubbleapps.io" in url_lower:
            return cls.BUBBLE
        elif "outsystems.app" in url_lower or "outsystems.com" in url_lower:
            return cls.OUTSYSTEMS
        elif "airtable.com" in url_lower:
            return cls.AIRTABLE
        elif "mendixcloud.com" in url_lower:
            return cls.MENDIX
        elif "appian.com" in url_lower:
            return cls.APPIAN
        elif "powerapps.com" in url_lower:
            return cls.POWERAPPS
        elif "salesforce.com" in url_lower or "force.com" in url_lower:
            return cls.SALESFORCE
        else:
            return cls.GENERIC


class ScenarioType(Enum):
    """Performance testing scenarios for low-code applications."""

    HOMEPAGE_LOAD = "homepage_load"
    REGULAR_USE_CASE = "regular_use_case"
    HEAVY_LIST_LOAD = "heavy_list_load"
    UPFRONT_SCRIPTING = "upfront_scripting"
    FORM_SUBMISSION = "form_submission"
    DATA_FILTERING = "data_filtering"
    PAGE_NAVIGATION = "page_navigation"
    MOBILE_RESPONSIVE = "mobile_responsive"
    WORKFLOW_EXECUTION = "workflow_execution"
    DATABASE_QUERY = "database_query"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        return self.value.replace("_", " ").title()

    @property
    def description(self) -> str:
        """Detailed description of the scenario."""
        descriptions = {
            self.HOMEPAGE_LOAD: "Initial page load with all core resources",
            self.REGULAR_USE_CASE: "Typical user interaction patterns",
            self.HEAVY_LIST_LOAD: "Loading large datasets or lists",
            self.UPFRONT_SCRIPTING: "JavaScript execution and initialization",
            self.FORM_SUBMISSION: "Form processing and validation",
            self.DATA_FILTERING: "Client-side data filtering and sorting",
            self.PAGE_NAVIGATION: "Navigation between different pages",
            self.MOBILE_RESPONSIVE: "Mobile device performance testing",
            self.WORKFLOW_EXECUTION: "Business process automation",
            self.DATABASE_QUERY: "Backend database operations",
        }
        return descriptions.get(self, "Performance test scenario")


class PerformanceCategory(Enum):
    """Performance rating categories."""

    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"
    CRITICAL = "critical"

    @classmethod
    def from_score(cls, score: float) -> "PerformanceCategory":
        """Determine category from performance score (0-100)."""
        if score >= 95:
            return cls.EXCELLENT
        elif score >= 80:
            return cls.GOOD
        elif score >= 60:
            return cls.NEEDS_IMPROVEMENT
        elif score >= 30:
            return cls.POOR
        else:
            return cls.CRITICAL

    @property
    def color(self) -> str:
        """HTML color code for the category."""
        colors = {
            self.EXCELLENT: "#00C851",
            self.GOOD: "#39C0ED",
            self.NEEDS_IMPROVEMENT: "#FFB74D",
            self.POOR: "#FF5722",
            self.CRITICAL: "#D32F2F",
        }
        return colors[self]

    @property
    def emoji(self) -> str:
        """Emoji representation of the category."""
        emojis = {
            self.EXCELLENT: "🟢",
            self.GOOD: "🔵",
            self.NEEDS_IMPROVEMENT: "🟡",
            self.POOR: "🟠",
            self.CRITICAL: "🔴",
        }
        return emojis[self]


class MetricSeverity(Enum):
    """Severity levels for performance metrics and recommendations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def priority(self) -> int:
        """Numeric priority for sorting."""
        priorities = {
            self.LOW: 1,
            self.MEDIUM: 2,
            self.HIGH: 3,
            self.CRITICAL: 4,
        }
        return priorities[self]


class ConfidenceLevel(Enum):
    """Confidence levels for performance measurements."""

    CERTAIN = "certain"
    FIRM = "firm"
    TENTATIVE = "tentative"

    @classmethod
    def from_std_dev(cls, std_dev: float, mean: float) -> "ConfidenceLevel":
        """Determine confidence level from standard deviation relative to mean."""
        if mean == 0:
            return cls.TENTATIVE
        variation = std_dev / mean
        if variation < 0.05:  # <5% variation
            return cls.CERTAIN
        elif variation < 0.15:  # <15% variation
            return cls.FIRM
        else:
            return cls.TENTATIVE

    @classmethod
    def from_confidence_interval(cls, ci_lower: float, ci_upper: float, mean: float) -> "ConfidenceLevel":
        """Determine confidence level from confidence interval relative to mean."""
        if mean == 0:
            return cls.TENTATIVE
        
        margin = (ci_upper - ci_lower) / 2
        relative_margin = margin / mean
        
        if relative_margin < 0.05:  # <5% margin
            return cls.CERTAIN
        elif relative_margin < 0.15:  # <15% margin
            return cls.FIRM
        else:
            return cls.TENTATIVE

    @property
    def icon(self) -> str:
        """Icon representation."""
        icons = {
            cls.CERTAIN: "🔒",
            cls.FIRM: "⚠️",
            cls.TENTATIVE: "❓",
        }
        return icons[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            ConfidenceLevel.CERTAIN: "High confidence - results are highly reliable",
            ConfidenceLevel.FIRM: "Moderate confidence - results are reasonably reliable",
            ConfidenceLevel.TENTATIVE: "Low confidence - results may vary significantly",
        }
        return descriptions[self]


class StatisticalSignificance(Enum):
    """Statistical significance levels for hypothesis testing."""

    NOT_SIGNIFICANT = "not_significant"
    MARGINALLY_SIGNIFICANT = "marginally_significant"
    SIGNIFICANT = "significant"
    HIGHLY_SIGNIFICANT = "highly_significant"

    @classmethod
    def from_p_value(cls, p_value: float) -> "StatisticalSignificance":
        """Determine significance level from p-value."""
        if p_value < 0.01:
            return cls.HIGHLY_SIGNIFICANT
        elif p_value < 0.05:
            return cls.SIGNIFICANT
        elif p_value < 0.10:
            return cls.MARGINALLY_SIGNIFICANT
        else:
            return cls.NOT_SIGNIFICANT

    @property
    def symbol(self) -> str:
        """Symbol representation for significance."""
        symbols = {
            StatisticalSignificance.NOT_SIGNIFICANT: "ns",
            StatisticalSignificance.MARGINALLY_SIGNIFICANT: "†",
            StatisticalSignificance.SIGNIFICANT: "*",
            StatisticalSignificance.HIGHLY_SIGNIFICANT: "**",
        }
        return symbols[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            StatisticalSignificance.NOT_SIGNIFICANT: "No statistically significant difference (p > 0.10)",
            StatisticalSignificance.MARGINALLY_SIGNIFICANT: "Marginally significant difference (p < 0.10)",
            StatisticalSignificance.SIGNIFICANT: "Statistically significant difference (p < 0.05)",
            StatisticalSignificance.HIGHLY_SIGNIFICANT: "Highly statistically significant difference (p < 0.01)",
        }
        return descriptions[self]


class TracingEvent(Enum):
    """Performance tracing event types."""

    # Navigation Events
    NAVIGATION_START = "navigationStart"
    DOM_LOADING = "domLoading"
    DOM_INTERACTIVE = "domInteractive"
    DOM_CONTENT_LOADED = "domContentLoadedEventStart"
    DOM_COMPLETE = "domComplete"
    LOAD_EVENT_START = "loadEventStart"
    LOAD_EVENT_END = "loadEventEnd"

    # Paint Events
    FIRST_PAINT = "firstPaint"
    FIRST_CONTENTFUL_PAINT = "firstContentfulPaint"
    LARGEST_CONTENTFUL_PAINT = "largestContentfulPaint"

    # Script Events
    SCRIPT_EVALUATION = "scriptEvaluation"
    SCRIPT_COMPILATION = "scriptCompilation"
    FUNCTION_CALL = "functionCall"

    # Layout Events
    LAYOUT = "layout"
    UPDATE_LAYOUT_TREE = "updateLayoutTree"
    RECALCULATE_STYLES = "recalculateStyles"

    # Render Events
    PAINT = "paint"
    COMPOSITE_LAYERS = "compositeLayers"
    RASTER_TASK = "rasterTask"

    # Network Events
    REQUEST_WILL_BE_SENT = "requestWillBeSent"
    RESPONSE_RECEIVED = "responseReceived"
    DATA_RECEIVED = "dataReceived"
    LOADING_FINISHED = "loadingFinished"

    # Memory Events
    MAJOR_GC = "majorGC"
    MINOR_GC = "minorGC"

    # Low-Code Specific Events
    BUBBLE_WORKFLOW = "bubbleWorkflow"
    OUTSYSTEMS_SCREEN_LOAD = "outsystemsScreenLoad"
    AIRTABLE_QUERY = "airtableQuery"

    @property
    def category(self) -> str:
        """Event category for grouping."""
        if self.value.endswith("GC"):
            return "memory"
        elif "paint" in self.value.lower() or "layout" in self.value.lower():
            return "rendering"
        elif "script" in self.value.lower() or "function" in self.value.lower():
            return "scripting"
        elif "request" in self.value.lower() or "response" in self.value.lower():
            return "network"
        elif any(
            platform in self.value.lower()
            for platform in ["bubble", "outsystems", "airtable"]
        ):
            return "platform"
        else:
            return "navigation"


class ResourceType(Enum):
    """Types of web resources."""

    DOCUMENT = "document"
    STYLESHEET = "stylesheet"
    IMAGE = "image"
    SCRIPT = "script"
    FONT = "font"
    MEDIA = "media"
    FETCH = "fetch"
    XHR = "xhr"
    WEBSOCKET = "websocket"
    MANIFEST = "manifest"
    OTHER = "other"


class DeviceType(Enum):
    """Device types for testing."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"

    @property
    def viewport(self) -> dict:
        """Default viewport dimensions."""
        viewports = {
            self.DESKTOP: {"width": 1920, "height": 1080},
            self.MOBILE: {"width": 375, "height": 667},
            self.TABLET: {"width": 768, "height": 1024},
        }
        return viewports[self]


class NetworkCondition(Enum):
    """Network condition presets."""

    FAST_3G = "fast3g"
    SLOW_3G = "slow3g"
    REGULAR_4G = "regular4g"
    WIFI = "wifi"
    OFFLINE = "offline"

    @property
    def settings(self) -> dict:
        """Network throttling settings."""
        conditions = {
            self.FAST_3G: {
                "offline": False,
                "downloadThroughput": 1.6 * 1024 * 1024 / 8,
                "uploadThroughput": 750 * 1024 / 8,
                "latency": 150,
            },
            self.SLOW_3G: {
                "offline": False,
                "downloadThroughput": 500 * 1024 / 8,
                "uploadThroughput": 500 * 1024 / 8,
                "latency": 400,
            },
            self.REGULAR_4G: {
                "offline": False,
                "downloadThroughput": 4 * 1024 * 1024 / 8,
                "uploadThroughput": 3 * 1024 * 1024 / 8,
                "latency": 20,
            },
            self.WIFI: {
                "offline": False,
                "downloadThroughput": 30 * 1024 * 1024 / 8,
                "uploadThroughput": 15 * 1024 * 1024 / 8,
                "latency": 2,
            },
            self.OFFLINE: {
                "offline": True,
                "downloadThroughput": 0,
                "uploadThroughput": 0,
                "latency": 0,
            },
        }
        return conditions[self]


class ReportFormat(Enum):
    """Available report output formats."""

    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    MARKDOWN = "markdown"

    @property
    def extension(self) -> str:
        """File extension for the format."""
        extensions = {
            self.HTML: ".html",
            self.PDF: ".pdf",
            self.JSON: ".json",
            self.CSV: ".csv",
            self.EXCEL: ".xlsx",
            self.MARKDOWN: ".md",
        }
        return extensions[self]

    @property
    def mime_type(self) -> str:
        """MIME type for the format."""
        mime_types = {
            self.HTML: "text/html",
            self.PDF: "application/pdf",
            self.JSON: "application/json",
            self.CSV: "text/csv",
            self.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            self.MARKDOWN: "text/markdown",
        }
        return mime_types[self]
