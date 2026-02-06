"""
Unit tests for website performance scanner.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from lowcode_scanner.core.scanner import LowCodePerformanceScanner
from lowcode_scanner.core.api_client import APIClient
from lowcode_scanner.core.validator import APIKeyValidator, URLValidator
from lowcode_scanner.models.performance_metrics import PerformanceMetrics
from lowcode_scanner.models.enums import ScanConfig, ScanStrategy


class TestURLValidator:
    """Test URL validator."""

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        validator = URLValidator()

        valid_urls = [
            "https://example.com",
            "http://example.com",
            "example.com",
            "https://www.example.com/path",
            "https://example.com:8080",
        ]

        for url in valid_urls:
            assert validator.validate_url(url) == True

    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        validator = URLValidator()

        invalid_urls = ["", "not-a-url", "http://", "https://.com"]

        for url in invalid_urls:
            assert validator.validate_url(url) == False

    def test_normalize_url(self):
        """Test URL normalization."""
        validator = URLValidator()

        test_cases = [
            ("example.com", "https://example.com"),
            ("http://example.com", "http://example.com"),
            ("https://example.com", "https://example.com"),
        ]

        for input_url, expected in test_cases:
            assert validator.normalize_url(input_url) == expected

    def test_extract_domain(self):
        """Test domain extraction."""
        validator = URLValidator()

        test_cases = [
            ("https://example.com", "example.com"),
            ("http://www.example.com/path", "www.example.com"),
            ("example.com:8080", "example.com:8080"),
        ]

        for url, expected in test_cases:
            assert validator.extract_domain(url) == expected


class TestAPIKeyValidator:
    """Test API key validator."""

    def test_validate_format_valid(self):
        """Test valid API key format."""
        validator = APIKeyValidator("AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        is_valid, error = validator.validate_format()
        assert is_valid == True
        assert error is None

    def test_validate_format_invalid(self):
        """Test invalid API key format."""
        test_cases = [
            ("", "API key cannot be empty"),
            ("short", "API key appears too short"),
            ("NotAGoogleKey123", "API key format appears invalid"),
        ]

        for api_key, expected_error in test_cases:
            validator = APIKeyValidator(api_key)
            is_valid, error = validator.validate_format()
            assert is_valid == False
            assert expected_error in error

    def test_mask_key(self):
        """Test API key masking."""
        test_cases = [
            (None, "None"),
            ("short", "***"),
            ("AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "AIza...6789"),
        ]

        for api_key, expected in test_cases:
            validator = APIKeyValidator(api_key)
            assert validator.mask_key() == expected


class TestPerformanceMetrics:
    """Test performance metrics model."""

    def test_create_metrics(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            url="https://example.com",
            strategy="mobile",
            score=95.5,
            first_contentful_paint_s=1.2,
            largest_contentful_paint_s=2.3,
            cumulative_layout_shift=0.05,
            total_blocking_time_s=0.1,
            speed_index_s=3.2,
            time_to_interactive_s=4.5,
            total_requests=50,
            total_bytes_kb=1200.5,
            success=True,
            scan_duration_ms=1500,
        )

        assert metrics.url == "https://example.com"
        assert metrics.strategy == "mobile"
        assert metrics.score == 95.5
        assert metrics.success == True
        assert metrics.performance_category == "good"

    def test_core_web_vitals(self):
        """Test Core Web Vitals property."""
        metrics = PerformanceMetrics(
            url="https://example.com",
            strategy="mobile",
            first_contentful_paint_s=1.2,
            largest_contentful_paint_s=2.3,
            cumulative_layout_shift=0.05,
            total_blocking_time_s=0.1,
        )

        vitals = metrics.core_web_vitals
        assert vitals["fcp"] == 1.2
        assert vitals["lcp"] == 2.3
        assert vitals["cls"] == 0.05
        assert vitals["tbt"] == 0.1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = PerformanceMetrics(
            url="https://example.com", strategy="mobile", score=85.0
        )

        data = metrics.to_dict()
        assert "url" in data
        assert data["url"] == "https://example.com"
        assert "score" in data
        assert data["score"] == 85.0
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)  # ISO format string


class TestScanConfig:
    """Test scanner configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = ScanConfig()

        assert config.api_key is None
        assert (
            config.base_url
            == "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        )
        assert config.categories == ["performance"]
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.rate_limit_delay == 1.0
        assert config.concurrent_scans == 3
        assert config.debug_mode == False
        assert config.cache_enabled == True

    def test_config_with_api_key(self):
        """Test configuration with API key."""
        config = ScanConfig(api_key="AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

        assert config.api_key == "AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def test_config_properties(self):
        """Test configuration properties."""
        config = ScanConfig(rate_limit_delay=2.0, cache_ttl_minutes=120)

        assert config.rate_limit_delay_ms == 2000
        assert config.cache_ttl.total_seconds() == 120 * 60


class MockAPIClient:
    """Mock API client for testing."""

    def __init__(self):
        self.mock_response = {
            "lighthouseResult": {
                "categories": {"performance": {"score": 0.9}},
                "audits": {
                    "first-contentful-paint": {"numericValue": 1200},
                    "largest-contentful-paint": {"numericValue": 2300},
                    "cumulative-layout-shift": {"numericValue": 0.05},
                    "total-blocking-time": {"numericValue": 100},
                    "speed-index": {"numericValue": 3200},
                    "interactive": {"numericValue": 4500},
                    "resource-summary": {
                        "details": {"items": [{"requestCount": 50, "size": 1200500}]}
                    },
                },
            }
        }

    async def make_request(self, url, strategy):
        return self.mock_response

    def extract_metrics(self, response, url, strategy):
        return PerformanceMetrics(
            url=url,
            strategy=strategy,
            score=90.0,
            first_contentful_paint_s=1.2,
            largest_contentful_paint_s=2.3,
            cumulative_layout_shift=0.05,
            total_blocking_time_s=0.1,
            speed_index_s=3.2,
            time_to_interactive_s=4.5,
            total_requests=50,
            total_bytes_kb=1200.5,
            success=True,
        )


class TestWebsitePerformanceScanner:
    """Test website performance scanner."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ScanConfig(debug_mode=True)

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        logger = Mock()
        logger.debug = Mock()
        logger.info = Mock()
        logger.error = Mock()
        logger.warning = Mock()
        return logger

    @pytest.fixture
    def scanner(self, config, mock_logger):
        """Create scanner with mocked dependencies."""
        with (
            patch(
                "website_performance_scanner.core.scanner.APIClient"
            ) as mock_client_class,
            patch("website_performance_scanner.core.scanner.Progress") as mock_progress,
        ):
            mock_client = MockAPIClient()
            mock_client_class.return_value = mock_client
            scanner = WebsitePerformanceScanner(config, mock_logger)
            scanner.api_client = mock_client
            return scanner

    @pytest.mark.asyncio
    async def test_scan_single_async(self, scanner):
        """Test scanning a single website."""
        result = await scanner.scan_single_async("https://example.com", "mobile")

        assert result.url == "https://example.com"
        assert result.strategy == "mobile"
        assert result.success == True
        assert result.score == 90.0

    @pytest.mark.asyncio
    async def test_scan_batch_async(self, scanner):
        """Test batch scanning."""
        urls = ["https://example.com", "https://example.org"]

        results = await scanner.scan_batch_async(urls, ["mobile", "desktop"])

        assert len(results) == 4  # 2 URLs × 2 strategies
        assert all(r.success for r in results)

    def test_load_urls_from_args(self, scanner):
        """Test loading URLs from arguments."""

        class MockArgs:
            urls = ["https://example.com", "example.org"]
            file = None

        args = MockArgs()
        urls = scanner.load_urls_from_args(args)

        assert len(urls) == 2
        assert "https://example.com" in urls
        assert "https://example.org" in urls

    def test_load_urls_from_file(self, scanner, tmp_path):
        """Test loading URLs from file."""
        # Create temp file with URLs
        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://example1.com\nhttps://example2.com\n# Comment\n")

        class MockArgs:
            urls = []
            file = str(url_file)

        args = MockArgs()
        urls = scanner.load_urls_from_args(args)

        assert len(urls) == 2
        assert "https://example1.com" in urls
        assert "https://example2.com" in urls

    def test_get_scan_stats(self, scanner):
        """Test getting scan statistics."""
        # Create some mock results
        scanner.results = [
            PerformanceMetrics(
                url="https://example.com", strategy="mobile", score=90, success=True
            ),
            PerformanceMetrics(
                url="https://example.com", strategy="desktop", score=85, success=True
            ),
            PerformanceMetrics(
                url="https://example.org", strategy="mobile", score=0, success=False
            ),
        ]
        scanner._scan_stats = {
            "total_scans": 3,
            "successful_scans": 2,
            "failed_scans": 1,
            "total_duration_ms": 5000,
        }

        stats = scanner.get_scan_stats()

        assert stats["total_scans"] == 3
        assert stats["successful_scans"] == 2
        assert stats["failed_scans"] == 1
        assert stats["success_rate"] == (2 / 3) * 100
        assert stats["avg_score"] == (90 + 85) / 2

    def test_generate_error_report(self, scanner):
        """Test error report generation."""
        # Create results with errors
        scanner.results = [
            PerformanceMetrics(
                url="https://example.com",
                strategy="mobile",
                success=False,
                error_message="Rate limit exceeded",
            ),
            PerformanceMetrics(
                url="https://example.org",
                strategy="desktop",
                success=False,
                error_message="API key invalid",
            ),
            PerformanceMetrics(
                url="https://example.net", strategy="mobile", success=True, score=95
            ),
        ]

        error_report = scanner.generate_error_report()

        assert error_report["summary"]["total_failed"] == 2
        assert "RATE_LIMIT" in error_report["errors_by_type"]
        assert "AUTHENTICATION" in error_report["errors_by_type"]
        assert len(error_report["recommendations"]) > 0


@pytest.mark.integration
class TestIntegration:
    """Integration tests (requires actual API calls)."""

    @pytest.mark.skipif(True, reason="Requires actual API calls")
    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """Test actual API call (requires internet connection)."""
        config = ScanConfig(debug_mode=True)

        async with APIClient(config) as client:
            # Test with a known URL
            response = await client.make_request("https://example.com", "mobile")

            assert "lighthouseResult" in response or "error" in response

    @pytest.mark.skipif(True, reason="Requires actual API calls")
    def test_end_to_end_scan(self, tmp_path):
        """Test end-to-end scanning (requires internet connection)."""
        config = ScanConfig(debug_mode=True)
        scanner = WebsitePerformanceScanner(config)

        # Test with a small batch
        urls = ["https://example.com"]
        results = scanner.scan_multiple_sync(urls, ["mobile"])

        assert len(results) == 1
        assert results[0].url == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
