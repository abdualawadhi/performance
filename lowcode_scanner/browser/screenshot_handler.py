"""
Screenshot Handler Module for Low-Code Performance Scanner

This module provides comprehensive screenshot and video capture capabilities
during browser automation for performance testing documentation and analysis.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Page


class ScreenshotHandler:
    """Screenshot and visual capture handler for browser automation."""

    def __init__(self, page: Page, output_dir: Path):
        """Initialize screenshot handler."""
        self.page = page
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Screenshot tracking
        self.screenshots: List[Dict[str, Any]] = []
        self.video_path: Optional[Path] = None

        # Configuration
        self.screenshot_quality = 90
        self.full_page_screenshots = True
        self.capture_mobile_viewport = False

    async def capture_screenshot(
        self,
        name: str,
        full_page: Optional[bool] = None,
        quality: Optional[int] = None,
        element_selector: Optional[str] = None,
        annotations: Optional[List[str]] = None,
    ) -> Path:
        """Capture a screenshot with optional annotations."""
        try:
            timestamp = datetime.now(timezone.utc)
            safe_name = self._sanitize_filename(name)
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_name}.png"
            screenshot_path = self.output_dir / filename

            # Screenshot options (quality only works with JPEG)
            options = {
                "path": str(screenshot_path),
                "full_page": full_page
                if full_page is not None
                else self.full_page_screenshots,
                "type": "png",
            }

            # Capture specific element if selector provided
            if element_selector:
                try:
                    element = await self.page.wait_for_selector(
                        element_selector, timeout=5000
                    )
                    if element:
                        await element.screenshot(**options)
                    else:
                        # Fallback to full page
                        await self.page.screenshot(**options)
                except:
                    # Fallback to full page
                    await self.page.screenshot(**options)
            else:
                await self.page.screenshot(**options)

            # Store screenshot metadata
            screenshot_info = {
                "name": name,
                "path": screenshot_path,
                "timestamp": timestamp,
                "url": self.page.url,
                "viewport": await self._get_viewport_info(),
                "annotations": annotations or [],
                "element_selector": element_selector,
                "file_size_bytes": screenshot_path.stat().st_size
                if screenshot_path.exists()
                else 0,
            }

            self.screenshots.append(screenshot_info)

            self.logger.debug(f"Screenshot captured: {filename}")
            return screenshot_path

        except Exception as e:
            self.logger.error(f"Error capturing screenshot '{name}': {str(e)}")
            # Return a placeholder path
            return self.output_dir / "error_placeholder.png"

    async def capture_performance_timeline_screenshot(self, scenario_name: str) -> Path:
        """Capture a specialized screenshot showing performance timeline."""
        try:
            # First, inject CSS to highlight performance-critical elements
            await self.page.add_style_tag(
                content="""
                .performance-highlight {
                    outline: 3px solid #ff6b35 !important;
                    outline-offset: 2px !important;
                    background-color: rgba(255, 107, 53, 0.1) !important;
                }
                .performance-slow {
                    outline: 3px solid #ff1744 !important;
                    outline-offset: 2px !important;
                    background-color: rgba(255, 23, 68, 0.1) !important;
                }
                .performance-fast {
                    outline: 3px solid #00e676 !important;
                    outline-offset: 2px !important;
                    background-color: rgba(0, 230, 118, 0.1) !important;
                }
            """
            )

            # Highlight slow-loading elements
            await self.page.evaluate("""
                () => {
                    // Find images that might be slow loading
                    document.querySelectorAll('img').forEach(img => {
                        if (!img.complete) {
                            img.classList.add('performance-highlight');
                        }
                    });

                    // Highlight scripts that might be blocking
                    document.querySelectorAll('script[src]').forEach(script => {
                        script.classList.add('performance-highlight');
                    });

                    // Highlight elements with many children (complex DOM)
                    document.querySelectorAll('*').forEach(element => {
                        if (element.children.length > 20) {
                            element.classList.add('performance-slow');
                        }
                    });
                }
            """)

            # Add performance overlay
            await self.page.evaluate(f"""
                () => {{
                    const overlay = document.createElement('div');
                    overlay.id = 'performance-overlay';
                    overlay.innerHTML = `
                        <div style="
                            position: fixed;
                            top: 10px;
                            left: 10px;
                            background: rgba(0,0,0,0.8);
                            color: white;
                            padding: 15px;
                            border-radius: 8px;
                            font-family: monospace;
                            font-size: 12px;
                            z-index: 10000;
                            max-width: 300px;
                        ">
                            <h3 style="margin: 0 0 10px 0; color: #ff6b35;">Performance Timeline</h3>
                            <div><strong>Scenario:</strong> {scenario_name}</div>
                            <div><strong>Time:</strong> ${{new Date().toLocaleTimeString()}}</div>
                            <div><strong>URL:</strong> ${{location.hostname}}</div>
                            <div><strong>DOM Nodes:</strong> ${{document.querySelectorAll('*').length}}</div>
                            <div style="margin-top: 10px; font-size: 10px; color: #ccc;">
                                🟠 Highlighted: Performance-critical elements<br>
                                🔴 Red: Potentially slow elements<br>
                                🟢 Green: Optimized elements
                            </div>
                        </div>
                    `;
                    document.body.appendChild(overlay);
                }}
            """)

            # Wait a moment for DOM changes to render
            await self.page.wait_for_timeout(500)

            # Capture the annotated screenshot
            screenshot_path = await self.capture_screenshot(
                f"timeline_{scenario_name}",
                annotations=[
                    "Performance timeline visualization",
                    "Highlighted elements show performance impact",
                    f"Captured during {scenario_name} scenario",
                ],
            )

            # Remove the overlay and highlights
            await self.page.evaluate("""
                () => {
                    const overlay = document.getElementById('performance-overlay');
                    if (overlay) overlay.remove();

                    // Remove highlight classes
                    document.querySelectorAll('.performance-highlight, .performance-slow, .performance-fast')
                        .forEach(el => {
                            el.classList.remove('performance-highlight', 'performance-slow', 'performance-fast');
                        });
                }
            """)

            return screenshot_path

        except Exception as e:
            self.logger.error(f"Error capturing timeline screenshot: {str(e)}")
            # Fallback to regular screenshot
            return await self.capture_screenshot(f"timeline_{scenario_name}_fallback")

    async def capture_mobile_comparison(self, scenario_name: str) -> Tuple[Path, Path]:
        """Capture both desktop and mobile screenshots for comparison."""
        try:
            # Get current viewport
            current_viewport = await self._get_viewport_info()

            # Capture desktop version
            desktop_screenshot = await self.capture_screenshot(
                f"{scenario_name}_desktop", annotations=["Desktop viewport"]
            )

            # Switch to mobile viewport
            await self.page.set_viewport_size(375, 667)  # iPhone viewport
            await self.page.wait_for_timeout(1000)  # Allow reflow

            # Capture mobile version
            mobile_screenshot = await self.capture_screenshot(
                f"{scenario_name}_mobile", annotations=["Mobile viewport (375x667)"]
            )

            # Restore original viewport
            await self.page.set_viewport_size(
                current_viewport["width"], current_viewport["height"]
            )

            return desktop_screenshot, mobile_screenshot

        except Exception as e:
            self.logger.error(f"Error capturing mobile comparison: {str(e)}")
            # Return fallback screenshots
            fallback = await self.capture_screenshot(
                f"{scenario_name}_comparison_error"
            )
            return fallback, fallback

    async def capture_before_after_comparison(
        self, scenario_name: str, action_description: str, action_callback
    ) -> Tuple[Path, Path]:
        """Capture before/after screenshots around a specific action."""
        try:
            # Capture before state
            before_screenshot = await self.capture_screenshot(
                f"{scenario_name}_before",
                annotations=[f"Before: {action_description}"],
            )

            # Execute the action
            await action_callback()

            # Wait for changes to render
            await self.page.wait_for_timeout(1000)

            # Capture after state
            after_screenshot = await self.capture_screenshot(
                f"{scenario_name}_after",
                annotations=[f"After: {action_description}"],
            )

            return before_screenshot, after_screenshot

        except Exception as e:
            self.logger.error(f"Error capturing before/after comparison: {str(e)}")
            fallback = await self.capture_screenshot(
                f"{scenario_name}_comparison_error"
            )
            return fallback, fallback

    async def capture_element_focus_screenshot(
        self, element_selector: str, name: str, padding: int = 20
    ) -> Path:
        """Capture a screenshot focused on a specific element with padding."""
        try:
            element = await self.page.wait_for_selector(element_selector, timeout=5000)
            if not element:
                return await self.capture_screenshot(f"{name}_element_not_found")

            # Get element bounds
            bounding_box = await element.bounding_box()
            if not bounding_box:
                return await self.capture_screenshot(f"{name}_no_bounds")

            # Calculate clip area with padding
            clip = {
                "x": max(0, bounding_box["x"] - padding),
                "y": max(0, bounding_box["y"] - padding),
                "width": min(
                    await self.page.evaluate("() => window.innerWidth"),
                    bounding_box["width"] + 2 * padding,
                ),
                "height": min(
                    await self.page.evaluate("() => window.innerHeight"),
                    bounding_box["height"] + 2 * padding,
                ),
            }

            # Capture with clip area
            timestamp = datetime.now(timezone.utc)
            safe_name = self._sanitize_filename(name)
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_name}_focus.png"
            screenshot_path = self.output_dir / filename

            await self.page.screenshot(path=str(screenshot_path), clip=clip, type="png")

            # Store metadata
            screenshot_info = {
                "name": f"{name}_focus",
                "path": screenshot_path,
                "timestamp": timestamp,
                "url": self.page.url,
                "element_selector": element_selector,
                "clip_area": clip,
                "annotations": [f"Focused on element: {element_selector}"],
                "file_size_bytes": screenshot_path.stat().st_size
                if screenshot_path.exists()
                else 0,
            }

            self.screenshots.append(screenshot_info)
            return screenshot_path

        except Exception as e:
            self.logger.error(f"Error capturing element focus screenshot: {str(e)}")
            return await self.capture_screenshot(f"{name}_focus_error")

    async def create_screenshot_grid(
        self, screenshots: List[Path], grid_name: str, columns: int = 2
    ) -> Path:
        """Create a grid layout from multiple screenshots (requires PIL)."""
        try:
            from PIL import Image

            if not screenshots:
                raise ValueError("No screenshots provided")

            # Load images
            images = []
            for screenshot_path in screenshots:
                if screenshot_path.exists():
                    images.append(Image.open(screenshot_path))

            if not images:
                raise ValueError("No valid screenshot files found")

            # Calculate grid dimensions
            rows = (len(images) + columns - 1) // columns

            # Get maximum dimensions for consistent sizing
            max_width = max(img.width for img in images)
            max_height = max(img.height for img in images)

            # Create grid image
            grid_width = max_width * columns
            grid_height = max_height * rows
            grid_image = Image.new("RGB", (grid_width, grid_height), "white")

            # Paste images into grid
            for i, img in enumerate(images):
                row = i // columns
                col = i % columns
                x = col * max_width
                y = row * max_height

                # Resize image to fit grid cell if necessary
                if img.width != max_width or img.height != max_height:
                    img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)

                grid_image.paste(img, (x, y))

            # Save grid image
            timestamp = datetime.now(timezone.utc)
            safe_name = self._sanitize_filename(grid_name)
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_name}_grid.png"
            grid_path = self.output_dir / filename

            grid_image.save(str(grid_path), "PNG", quality=95)

            # Store metadata
            grid_info = {
                "name": f"{grid_name}_grid",
                "path": grid_path,
                "timestamp": timestamp,
                "source_screenshots": [str(p) for p in screenshots],
                "grid_dimensions": {"columns": columns, "rows": rows},
                "annotations": [f"Grid of {len(images)} screenshots"],
                "file_size_bytes": grid_path.stat().st_size
                if grid_path.exists()
                else 0,
            }

            self.screenshots.append(grid_info)
            return grid_path

        except ImportError:
            self.logger.warning(
                "PIL not available, cannot create screenshot grid. Install with: pip install Pillow"
            )
            return screenshots[0] if screenshots else Path()
        except Exception as e:
            self.logger.error(f"Error creating screenshot grid: {str(e)}")
            return screenshots[0] if screenshots else Path()

    async def capture_scrolling_screenshot(
        self, name: str, scroll_pause_time: float = 1.0
    ) -> Path:
        """Capture a full-page screenshot by scrolling and stitching."""
        try:
            # Get page dimensions
            dimensions = await self.page.evaluate("""
                () => ({
                    width: Math.max(document.body.scrollWidth, document.body.offsetWidth,
                                  document.documentElement.clientWidth, document.documentElement.scrollWidth,
                                  document.documentElement.offsetWidth),
                    height: Math.max(document.body.scrollHeight, document.body.offsetHeight,
                                   document.documentElement.clientHeight, document.documentElement.scrollHeight,
                                   document.documentElement.offsetHeight),
                    viewportHeight: window.innerHeight
                })
            """)

            # If page is not too tall, use regular full page screenshot
            if dimensions["height"] <= dimensions["viewportHeight"] * 10:
                return await self.capture_screenshot(name, full_page=True)

            # For very tall pages, capture in sections and stitch
            screenshots_paths = []
            scroll_position = 0
            section_count = 0

            while scroll_position < dimensions["height"]:
                # Scroll to position
                await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
                await self.page.wait_for_timeout(int(scroll_pause_time * 1000))

                # Capture section
                section_path = await self.capture_screenshot(
                    f"{name}_section_{section_count}",
                    full_page=False,
                    annotations=[f"Section {section_count} of scrolling page"],
                )
                screenshots_paths.append(section_path)

                scroll_position += dimensions["viewportHeight"]
                section_count += 1

                # Safety limit to prevent infinite loops
                if section_count > 50:
                    self.logger.warning(
                        "Reached maximum sections limit for scrolling screenshot"
                    )
                    break

            # Reset scroll position
            await self.page.evaluate("window.scrollTo(0, 0)")

            # If only one section, return it
            if len(screenshots_paths) == 1:
                return screenshots_paths[0]

            # Try to create a vertical stitch if PIL is available
            try:
                from PIL import Image

                images = []
                for path in screenshots_paths:
                    if path.exists():
                        images.append(Image.open(path))

                if images:
                    # Calculate total height
                    total_height = sum(img.height for img in images)
                    max_width = max(img.width for img in images)

                    # Create stitched image
                    stitched = Image.new("RGB", (max_width, total_height))
                    y_offset = 0

                    for img in images:
                        stitched.paste(img, (0, y_offset))
                        y_offset += img.height

                    # Save stitched image
                    timestamp = datetime.now(timezone.utc)
                    safe_name = self._sanitize_filename(name)
                    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_name}_stitched.png"
                    stitched_path = self.output_dir / filename

                    stitched.save(str(stitched_path), "PNG", quality=95)

                    # Clean up section files
                    for path in screenshots_paths:
                        try:
                            path.unlink()
                        except:
                            pass

                    return stitched_path

            except ImportError:
                pass

            # Return first section if stitching not possible
            return screenshots_paths[0] if screenshots_paths else Path()

        except Exception as e:
            self.logger.error(f"Error capturing scrolling screenshot: {str(e)}")
            return await self.capture_screenshot(f"{name}_scrolling_error")

    async def start_video_recording(self) -> None:
        """Start video recording if supported by browser context."""
        try:
            # Video recording is handled at the context level in Playwright
            # This method is for tracking video state
            self.logger.debug("Video recording started (handled by browser context)")

        except Exception as e:
            self.logger.error(f"Error starting video recording: {str(e)}")

    async def stop_video_recording(self) -> Optional[Path]:
        """Stop video recording and return video path."""
        try:
            # Get video path from page
            video_path = None
            if hasattr(self.page, "video") and self.page.video:
                video_path = await self.page.video.path()
                self.video_path = Path(video_path) if video_path else None

            return self.video_path

        except Exception as e:
            self.logger.error(f"Error stopping video recording: {str(e)}")
            return None

    async def _get_viewport_info(self) -> Dict[str, int]:
        """Get current viewport information."""
        try:
            return await self.page.evaluate("""
                () => ({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    devicePixelRatio: window.devicePixelRatio || 1
                })
            """)
        except:
            return {"width": 1920, "height": 1080, "devicePixelRatio": 1}

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename to be safe for filesystem."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = "".join(c if c not in invalid_chars else "_" for c in name)

        # Limit length
        max_length = 50
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]

        # Remove multiple underscores
        while "__" in safe_name:
            safe_name = safe_name.replace("__", "_")

        return safe_name.strip("_")

    def get_screenshot_summary(self) -> Dict[str, Any]:
        """Get summary of all captured screenshots."""
        try:
            if not self.screenshots:
                return {"total_screenshots": 0, "message": "No screenshots captured"}

            total_size = sum(
                screenshot.get("file_size_bytes", 0) for screenshot in self.screenshots
            )

            return {
                "total_screenshots": len(self.screenshots),
                "total_size_mb": total_size / (1024 * 1024),
                "average_size_kb": (total_size / len(self.screenshots)) / 1024
                if self.screenshots
                else 0,
                "screenshots_by_type": self._categorize_screenshots(),
                "video_recorded": self.video_path is not None,
                "video_path": str(self.video_path) if self.video_path else None,
            }

        except Exception as e:
            self.logger.error(f"Error getting screenshot summary: {str(e)}")
            return {"error": str(e)}

    def _categorize_screenshots(self) -> Dict[str, int]:
        """Categorize screenshots by type."""
        categories = {
            "timeline": 0,
            "mobile": 0,
            "desktop": 0,
            "before_after": 0,
            "focus": 0,
            "grid": 0,
            "scrolling": 0,
            "other": 0,
        }

        for screenshot in self.screenshots:
            name = screenshot.get("name", "").lower()

            if "timeline" in name:
                categories["timeline"] += 1
            elif "mobile" in name:
                categories["mobile"] += 1
            elif "desktop" in name:
                categories["desktop"] += 1
            elif "before" in name or "after" in name:
                categories["before_after"] += 1
            elif "focus" in name:
                categories["focus"] += 1
            elif "grid" in name:
                categories["grid"] += 1
            elif "scrolling" in name or "stitched" in name:
                categories["scrolling"] += 1
            else:
                categories["other"] += 1

        return categories

    def cleanup(self) -> None:
        """Clean up screenshot handler resources."""
        try:
            self.logger.debug(
                f"Screenshot handler cleanup completed. Captured {len(self.screenshots)} screenshots."
            )

        except Exception as e:
            self.logger.error(f"Error during screenshot handler cleanup: {str(e)}")
