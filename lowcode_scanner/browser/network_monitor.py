"""
Network Monitoring Module for Low-Code Performance Scanner

This module provides comprehensive network performance monitoring during browser
automation, including request tracking, resource analysis, and network timing metrics.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from playwright.async_api import Page, Request, Response

from ..models.enums import ResourceType
from ..models.performance_metrics import NetworkMetrics, ResourceMetrics


class NetworkMonitor:
    """Network performance monitor for browser automation."""

    def __init__(self, page: Page):
        """Initialize network monitor."""
        self.page = page
        self.logger = logging.getLogger(__name__)

        # Monitoring state
        self.is_monitoring = False

        # Request tracking
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.failed_requests: List[Dict[str, Any]] = []

        # Resource tracking
        self.resources: List[ResourceMetrics] = []
        self.resource_breakdown: Dict[str, int] = {}

        # Network statistics
        self.total_requests = 0
        self.total_transfer_size_bytes = 0
        self.total_resource_size_bytes = 0
        self.cached_resources = 0

        # Timing tracking
        self.request_timings: List[float] = []
        self.slowest_request_ms = 0.0

        # Domains tracking
        self.domains: Set[str] = set()
        self.third_party_requests = 0

    async def initialize(self) -> None:
        """Initialize network monitoring."""
        try:
            # Set up event listeners
            self.page.on("request", self._handle_request)
            self.page.on("response", self._handle_response)
            self.page.on("requestfailed", self._handle_request_failed)

            self.logger.debug("Network monitor initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize network monitor: {str(e)}")
            raise

    async def start_monitoring(self) -> None:
        """Start network monitoring."""
        if self.is_monitoring:
            return

        self.is_monitoring = True

        # Reset all tracking data
        self.requests.clear()
        self.responses.clear()
        self.failed_requests.clear()
        self.resources.clear()
        self.resource_breakdown.clear()
        self.request_timings.clear()
        self.domains.clear()

        # Reset counters
        self.total_requests = 0
        self.total_transfer_size_bytes = 0
        self.total_resource_size_bytes = 0
        self.cached_resources = 0
        self.third_party_requests = 0
        self.slowest_request_ms = 0.0

        self.logger.debug("Started network monitoring")

    async def stop_monitoring(self) -> None:
        """Stop network monitoring."""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        self.logger.debug("Stopped network monitoring")

    def _handle_request(self, request: Request) -> None:
        """Handle outgoing request."""
        if not self.is_monitoring:
            return

        try:
            timestamp = datetime.now(timezone.utc).timestamp() * 1000
            url = request.url
            parsed_url = urlparse(url)

            # Track domain
            domain = parsed_url.netloc
            self.domains.add(domain)

            # Check if third-party request
            page_domain = urlparse(self.page.url).netloc if self.page.url else ""
            is_third_party = domain != page_domain and domain != ""
            if is_third_party:
                self.third_party_requests += 1

            # Determine resource type
            resource_type = self._classify_resource_type(url, request.resource_type)

            # Update resource breakdown
            resource_type_str = resource_type.value
            self.resource_breakdown[resource_type_str] = (
                self.resource_breakdown.get(resource_type_str, 0) + 1
            )

            # Store request info
            request_info = {
                "url": url,
                "method": request.method,
                "resource_type": resource_type,
                "timestamp": timestamp,
                "headers": dict(request.headers),
                "is_third_party": is_third_party,
                "domain": domain,
                "post_data": request.post_data if request.post_data else None,
            }

            self.requests.append(request_info)
            self.total_requests += 1

        except Exception as e:
            self.logger.debug(f"Error handling request: {str(e)}")

    def _handle_response(self, response: Response) -> None:
        """Handle response received."""
        if not self.is_monitoring:
            return

        try:
            timestamp = datetime.now(timezone.utc).timestamp() * 1000

            # Find matching request using Playwright's built-in link
            matching_request = None
            for req in self.requests:
                # Use URL and some timing context to match, as we don't have a unique ID here
                # but Playwright's response object is linked to its request
                if req["url"] == response.url and not any(
                    res.get("url") == response.url
                    for res in self.responses
                    if res.get("timestamp", 0) > req["timestamp"]
                ):
                    matching_request = req
                    break

            if not matching_request:
                # Fallback to direct request object if available (Playwright >= 1.12)
                try:
                    request = response.request
                    for req in self.requests:
                        if (
                            req["url"] == request.url
                            and abs(req["timestamp"] - timestamp) < 60000
                        ):
                            matching_request = req
                            break
                except:
                    pass

            if not matching_request:
                return

            # Calculate response time
            response_time_ms = timestamp - matching_request["timestamp"]
            self.request_timings.append(response_time_ms)
            self.slowest_request_ms = max(self.slowest_request_ms, response_time_ms)

            # Check if from cache
            from_cache = self._is_from_cache(response)
            if from_cache:
                self.cached_resources += 1

            # Get content length
            content_length = 0
            try:
                content_length = int(response.headers.get("content-length", 0))
            except (ValueError, TypeError):
                pass

            # Estimate transfer size (compressed)
            transfer_size = content_length
            if response.headers.get("content-encoding"):
                # Rough estimate for compressed content
                transfer_size = int(content_length * 0.7)  # Assume ~30% compression

            self.total_transfer_size_bytes += transfer_size
            self.total_resource_size_bytes += content_length

            # Store response info
            response_info = {
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "headers": dict(response.headers),
                "content_length": content_length,
                "transfer_size": transfer_size,
                "response_time_ms": response_time_ms,
                "from_cache": from_cache,
                "timestamp": timestamp,
            }

            self.responses.append(response_info)

            # Create resource metrics
            resource_metrics = ResourceMetrics(
                url=response.url,
                resource_type=matching_request["resource_type"],
                transfer_size_kb=transfer_size / 1024,
                resource_size_kb=content_length / 1024,
                start_time_ms=matching_request["timestamp"],
                response_time_ms=response_time_ms,
                status_code=response.status,
                from_cache=from_cache,
                blocking_time_ms=self._calculate_blocking_time(
                    matching_request["resource_type"]
                ),
            )

            self.resources.append(resource_metrics)

        except Exception as e:
            self.logger.debug(f"Error handling response: {str(e)}")

    def _handle_request_failed(self, request: Request) -> None:
        """Handle failed request."""
        if not self.is_monitoring:
            return

        try:
            failure_info = {
                "url": request.url,
                "method": request.method,
                "failure_text": request.failure,
                "timestamp": datetime.now(timezone.utc).timestamp() * 1000,
            }

            self.failed_requests.append(failure_info)

        except Exception as e:
            self.logger.debug(f"Error handling failed request: {str(e)}")

    def _classify_resource_type(self, url: str, playwright_type: str) -> ResourceType:
        """Classify resource type based on URL and Playwright type."""
        url_lower = url.lower()

        # Map Playwright resource types to our enum
        type_mapping = {
            "document": ResourceType.DOCUMENT,
            "stylesheet": ResourceType.STYLESHEET,
            "image": ResourceType.IMAGE,
            "script": ResourceType.SCRIPT,
            "font": ResourceType.FONT,
            "media": ResourceType.MEDIA,
            "fetch": ResourceType.FETCH,
            "xhr": ResourceType.XHR,
            "websocket": ResourceType.WEBSOCKET,
            "manifest": ResourceType.MANIFEST,
        }

        if playwright_type in type_mapping:
            return type_mapping[playwright_type]

        # Fallback to URL-based detection
        if any(ext in url_lower for ext in [".css"]):
            return ResourceType.STYLESHEET
        elif any(ext in url_lower for ext in [".js"]):
            return ResourceType.SCRIPT
        elif any(
            ext in url_lower
            for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]
        ):
            return ResourceType.IMAGE
        elif any(ext in url_lower for ext in [".woff", ".woff2", ".ttf", ".otf"]):
            return ResourceType.FONT
        elif any(ext in url_lower for ext in [".mp4", ".webm", ".ogg", ".mp3", ".wav"]):
            return ResourceType.MEDIA
        else:
            return ResourceType.OTHER

    def _is_from_cache(self, response: Response) -> bool:
        """Determine if response was served from cache."""
        # Check cache-related headers
        cache_control = response.headers.get("cache-control", "").lower()
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        # Check for cache hit indicators
        cf_cache_status = response.headers.get("cf-cache-status", "").lower()
        if cf_cache_status in ["hit", "expired"]:
            return True

        # Check age header (indicates cached response)
        age = response.headers.get("age")
        if age and int(age) > 0:
            return True

        # Check x-cache headers
        x_cache = response.headers.get("x-cache", "").lower()
        if "hit" in x_cache:
            return True

        # For now, assume 304 responses are from cache
        return response.status == 304

    def _calculate_blocking_time(self, resource_type: ResourceType) -> float:
        """Calculate blocking time based on resource type."""
        # This is a simplified calculation
        # In reality, you'd need more sophisticated timing from Performance API
        if resource_type in [ResourceType.SCRIPT, ResourceType.STYLESHEET]:
            return 50.0  # Assume blocking resources take some time
        return 0.0

    async def get_metrics(self) -> NetworkMetrics:
        """Get comprehensive network metrics."""
        try:
            # Calculate average response time
            avg_response_time = (
                sum(self.request_timings) / len(self.request_timings)
                if self.request_timings
                else 0.0
            )

            # Calculate compression ratio
            compression_ratio = 0.0
            if self.total_resource_size_bytes > 0:
                compression_ratio = 1.0 - (
                    self.total_transfer_size_bytes / self.total_resource_size_bytes
                )

            # Calculate cache hit ratio
            cache_hit_ratio = 0.0
            if self.total_requests > 0:
                cache_hit_ratio = self.cached_resources / self.total_requests

            return NetworkMetrics(
                total_requests=self.total_requests,
                failed_requests=len(self.failed_requests),
                total_transfer_size_kb=self.total_transfer_size_bytes / 1024,
                total_resource_size_kb=self.total_resource_size_bytes / 1024,
                avg_response_time_ms=avg_response_time,
                slowest_request_ms=self.slowest_request_ms,
                resource_breakdown=self.resource_breakdown.copy(),
                compression_ratio=compression_ratio,
                cached_resources=self.cached_resources,
                cache_hit_ratio=cache_hit_ratio,
            )

        except Exception as e:
            self.logger.error(f"Error getting network metrics: {str(e)}")
            return NetworkMetrics()

    async def get_resource_metrics(self) -> List[ResourceMetrics]:
        """Get individual resource metrics."""
        return self.resources.copy()

    async def get_third_party_analysis(self) -> Dict[str, Any]:
        """Analyze third-party resource usage."""
        try:
            third_party_domains = []
            third_party_size_bytes = 0
            third_party_count = 0

            page_domain = urlparse(self.page.url).netloc if self.page.url else ""

            for response in self.responses:
                domain = urlparse(response["url"]).netloc
                if domain != page_domain and domain != "":
                    if domain not in [d["domain"] for d in third_party_domains]:
                        third_party_domains.append(
                            {"domain": domain, "requests": 0, "size_bytes": 0}
                        )

                    # Find domain entry and update
                    for domain_entry in third_party_domains:
                        if domain_entry["domain"] == domain:
                            domain_entry["requests"] += 1
                            domain_entry["size_bytes"] += response["transfer_size"]
                            break

                    third_party_size_bytes += response["transfer_size"]
                    third_party_count += 1

            # Sort by size
            third_party_domains.sort(key=lambda x: x["size_bytes"], reverse=True)

            return {
                "third_party_requests": third_party_count,
                "third_party_size_kb": third_party_size_bytes / 1024,
                "third_party_percentage": (
                    (third_party_count / self.total_requests * 100)
                    if self.total_requests > 0
                    else 0
                ),
                "domains": third_party_domains[:10],  # Top 10 domains
                "unique_domains": len(self.domains),
                "recommendations": self._generate_third_party_recommendations(
                    third_party_count, third_party_size_bytes, len(third_party_domains)
                ),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing third-party resources: {str(e)}")
            return {}

    def _generate_third_party_recommendations(
        self, count: int, size_bytes: int, domain_count: int
    ) -> List[Dict[str, str]]:
        """Generate recommendations for third-party resource optimization."""
        recommendations = []

        if count > 50:
            recommendations.append(
                {
                    "issue": "High Third-Party Request Count",
                    "description": f"{count} third-party requests detected",
                    "suggestion": "Reduce number of third-party services or combine requests",
                    "priority": "high" if count > 100 else "medium",
                }
            )

        if size_bytes > 1024 * 1024:  # 1MB
            recommendations.append(
                {
                    "issue": "Large Third-Party Resources",
                    "description": f"{size_bytes / 1024 / 1024:.1f}MB from third-party sources",
                    "suggestion": "Optimize third-party resource loading or consider self-hosting",
                    "priority": "medium",
                }
            )

        if domain_count > 10:
            recommendations.append(
                {
                    "issue": "Too Many Third-Party Domains",
                    "description": f"Resources loaded from {domain_count} different domains",
                    "suggestion": "Reduce number of external domains to minimize DNS lookups",
                    "priority": "medium",
                }
            )

        return recommendations

    async def get_performance_waterfall(self) -> List[Dict[str, Any]]:
        """Generate performance waterfall data."""
        try:
            waterfall_data = []

            # Combine requests and responses
            for request in self.requests:
                matching_response = None
                for response in self.responses:
                    if response["url"] == request["url"]:
                        matching_response = response
                        break

                entry = {
                    "url": request["url"],
                    "method": request["method"],
                    "resource_type": request["resource_type"].value,
                    "domain": request["domain"],
                    "is_third_party": request["is_third_party"],
                    "start_time": request["timestamp"],
                }

                if matching_response:
                    entry.update(
                        {
                            "status": matching_response["status"],
                            "response_time_ms": matching_response["response_time_ms"],
                            "content_length": matching_response["content_length"],
                            "from_cache": matching_response["from_cache"],
                            "end_time": matching_response["timestamp"],
                        }
                    )
                else:
                    # Check if it's a failed request
                    failed = next(
                        (f for f in self.failed_requests if f["url"] == request["url"]),
                        None,
                    )
                    if failed:
                        entry.update(
                            {
                                "status": 0,
                                "failed": True,
                                "failure_text": failed.get(
                                    "failure_text", "Unknown error"
                                ),
                            }
                        )

                waterfall_data.append(entry)

            # Sort by start time
            waterfall_data.sort(key=lambda x: x["start_time"])

            return waterfall_data

        except Exception as e:
            self.logger.error(f"Error generating performance waterfall: {str(e)}")
            return []

    async def get_slow_requests(
        self, threshold_ms: float = 1000.0
    ) -> List[Dict[str, Any]]:
        """Get requests that took longer than the threshold."""
        try:
            slow_requests = []

            for response in self.responses:
                if response["response_time_ms"] > threshold_ms:
                    slow_requests.append(
                        {
                            "url": response["url"],
                            "response_time_ms": response["response_time_ms"],
                            "status": response["status"],
                            "content_length": response["content_length"],
                            "from_cache": response["from_cache"],
                        }
                    )

            # Sort by response time (slowest first)
            slow_requests.sort(key=lambda x: x["response_time_ms"], reverse=True)

            return slow_requests

        except Exception as e:
            self.logger.error(f"Error getting slow requests: {str(e)}")
            return []

    async def generate_network_report(self) -> Dict[str, Any]:
        """Generate comprehensive network performance report."""
        try:
            metrics = await self.get_metrics()
            third_party_analysis = await self.get_third_party_analysis()
            slow_requests = await self.get_slow_requests()

            return {
                "summary": {
                    "total_requests": metrics.total_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": (
                        (
                            (metrics.total_requests - metrics.failed_requests)
                            / metrics.total_requests
                            * 100
                        )
                        if metrics.total_requests > 0
                        else 0
                    ),
                    "total_size_kb": metrics.total_transfer_size_kb,
                    "average_response_time_ms": metrics.avg_response_time_ms,
                    "slowest_request_ms": metrics.slowest_request_ms,
                    "cache_hit_rate": metrics.cache_hit_ratio * 100,
                    "compression_ratio": metrics.compression_ratio * 100,
                    "efficiency_score": metrics.network_efficiency_score,
                },
                "resource_breakdown": metrics.resource_breakdown,
                "third_party_analysis": third_party_analysis,
                "slow_requests": slow_requests[:10],  # Top 10 slowest
                "failed_requests": self.failed_requests,
                "performance_recommendations": self._generate_network_recommendations(
                    metrics
                ),
            }

        except Exception as e:
            self.logger.error(f"Error generating network report: {str(e)}")
            return {}

    def _generate_network_recommendations(
        self, metrics: NetworkMetrics
    ) -> List[Dict[str, str]]:
        """Generate network performance recommendations."""
        recommendations = []

        # Too many requests
        if metrics.total_requests > 100:
            recommendations.append(
                {
                    "issue": "High Request Count",
                    "description": f"{metrics.total_requests} HTTP requests made",
                    "suggestion": "Combine resources using bundling or HTTP/2 server push",
                    "priority": "high" if metrics.total_requests > 200 else "medium",
                }
            )

        # Large page size
        if metrics.total_transfer_size_kb > 2048:  # 2MB
            recommendations.append(
                {
                    "issue": "Large Page Size",
                    "description": f"Total page size is {metrics.total_transfer_size_kb:.0f}KB",
                    "suggestion": "Optimize images, minify assets, and implement lazy loading",
                    "priority": (
                        "high" if metrics.total_transfer_size_kb > 5120 else "medium"
                    ),
                }
            )

        # Poor compression
        if metrics.compression_ratio < 0.3:
            recommendations.append(
                {
                    "issue": "Poor Compression",
                    "description": f"Only {metrics.compression_ratio * 100:.1f}% compression achieved",
                    "suggestion": "Enable gzip/brotli compression on server",
                    "priority": "medium",
                }
            )

        # Low cache hit rate
        if metrics.cache_hit_ratio < 0.5 and metrics.total_requests > 10:
            recommendations.append(
                {
                    "issue": "Low Cache Hit Rate",
                    "description": f"Only {metrics.cache_hit_ratio * 100:.1f}% of resources cached",
                    "suggestion": "Implement proper caching headers and CDN",
                    "priority": "medium",
                }
            )

        # Slow average response time
        if metrics.avg_response_time_ms > 500:
            recommendations.append(
                {
                    "issue": "Slow Response Times",
                    "description": f"Average response time is {metrics.avg_response_time_ms:.0f}ms",
                    "suggestion": "Optimize server performance and use a CDN",
                    "priority": (
                        "high" if metrics.avg_response_time_ms > 1000 else "medium"
                    ),
                }
            )

        # Failed requests
        if metrics.failed_requests > 0:
            failure_rate = metrics.failed_requests / metrics.total_requests * 100
            recommendations.append(
                {
                    "issue": "Failed Requests",
                    "description": f"{metrics.failed_requests} requests failed ({failure_rate:.1f}%)",
                    "suggestion": "Fix broken links and ensure all resources are accessible",
                    "priority": "high" if failure_rate > 5 else "medium",
                }
            )

        return recommendations

    async def cleanup(self) -> None:
        """Clean up network monitor resources."""
        try:
            await self.stop_monitoring()

            # Remove event listeners
            self.page.remove_listener("request", self._handle_request)
            self.page.remove_listener("response", self._handle_response)
            self.page.remove_listener("requestfailed", self._handle_request_failed)

            self.logger.debug("Network monitor cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during network monitor cleanup: {str(e)}")
