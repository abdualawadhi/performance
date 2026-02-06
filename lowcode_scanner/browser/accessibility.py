"""
Accessibility Monitor for Low-Code Performance Scanner

This module provides accessibility testing functionality using Axe-core.
"""

import logging
from typing import Dict, List, Optional

from playwright.async_api import Page

from ..models.performance_metrics import AccessibilityMetrics, AccessibilityViolation


class AccessibilityMonitor:
    """Monitors accessibility using Axe-core."""

    AXE_CDN_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js"

    def __init__(self, page: Page):
        """Initialize accessibility monitor."""
        self.page = page
        self.logger = logging.getLogger(__name__)

    async def inject_axe(self) -> None:
        """Inject Axe-core script into the page."""
        try:
            # Check if axe is already defined
            is_defined = await self.page.evaluate("() => typeof window.axe !== 'undefined'")
            if is_defined:
                return

            # Inject from CDN
            await self.page.add_script_tag(url=self.AXE_CDN_URL)
            self.logger.debug("Axe-core injected successfully")
        except Exception as e:
            self.logger.error(f"Failed to inject Axe-core: {str(e)}")

    async def run_scan(self) -> Optional[AccessibilityMetrics]:
        """Run accessibility scan."""
        try:
            await self.inject_axe()

            # Run axe
            results = await self.page.evaluate("""
                () => {
                    return new Promise((resolve, reject) => {
                        if (typeof window.axe === 'undefined') {
                            reject(new Error('Axe not loaded'));
                            return;
                        }
                        
                        window.axe.run(document, {
                            runOnly: {
                                type: 'tag',
                                values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']
                            }
                        }, (err, results) => {
                            if (err) reject(err);
                            else resolve(results);
                        });
                    });
                }
            """)

            if not results:
                return None

            violations = []
            for v in results.get("violations", []):
                violations.append(
                    AccessibilityViolation(
                        id=v.get("id"),
                        impact=v.get("impact"),
                        description=v.get("description"),
                        help_url=v.get("helpUrl"),
                        nodes=[
                            {
                                "html": node.get("html"),
                                "target": node.get("target"),
                                "failureSummary": node.get("failureSummary"),
                            }
                            for node in v.get("nodes", [])
                        ],
                    )
                )

            # Calculate a basic score (simple deduction)
            # Start with 100, deduct points based on impact
            score = 100.0
            impact_weights = {
                "critical": 10.0,
                "serious": 5.0,
                "moderate": 2.0,
                "minor": 1.0,
            }

            for v in violations:
                weight = impact_weights.get(v.impact, 1.0)
                # Cap deduction per rule to avoid negative score from one rule with many nodes
                deduction = weight * len(v.nodes)
                # Normalize deduction
                score -= min(deduction, 20.0) 

            score = max(0.0, score)

            return AccessibilityMetrics(
                score=score,
                violations=violations,
                passes=len(results.get("passes", [])),
                incomplete=len(results.get("incomplete", [])),
                inapplicable=len(results.get("inapplicable", [])),
            )

        except Exception as e:
            self.logger.error(f"Error running accessibility scan: {str(e)}")
            return None
