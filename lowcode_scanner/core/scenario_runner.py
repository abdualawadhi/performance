"""
Scenario Runner for Low-Code Performance Scanner

This module handles the execution of different performance test scenarios
for low-code web applications.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from ..models import ScenarioMetrics, ScenarioType


class ScenarioRunner:
    """Executes performance test scenarios."""

    def __init__(self):
        """Initialize the scenario runner."""
        self.logger = logging.getLogger(__name__)
        self.active_scenarios: Dict[str, asyncio.Task] = {}

    async def run_scenario(
        self,
        scenario_type: ScenarioType,
        browser_automation,
        url: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> ScenarioMetrics:
        """
        Run a single performance test scenario.

        Args:
            scenario_type: Type of scenario to run
            browser_automation: Browser automation instance
            url: Target URL
            config: Optional scenario configuration

        Returns:
            Scenario metrics
        """
        self.logger.info(f"Running scenario: {scenario_type.value}")

        try:
            # Execute the scenario using browser automation
            # The actual execution is handled by BrowserAutomation.navigate_and_measure
            metrics = await browser_automation.navigate_and_measure(
                url=url,
                scenario_type=scenario_type,
            )

            self.logger.info(
                f"Scenario {scenario_type.value} completed with score: {metrics.overall_score:.1f}"
            )
            return metrics

        except Exception as e:
            self.logger.error(f"Scenario {scenario_type.value} failed: {str(e)}")
            raise

    async def run_scenarios_sequentially(
        self,
        scenarios: List[ScenarioType],
        browser_automation,
        url: str,
    ) -> List[ScenarioMetrics]:
        """
        Run multiple scenarios sequentially.

        Args:
            scenarios: List of scenarios to run
            browser_automation: Browser automation instance
            url: Target URL

        Returns:
            List of scenario metrics
        """
        results = []

        for scenario in scenarios:
            try:
                metrics = await self.run_scenario(scenario, browser_automation, url)
                results.append(metrics)
            except Exception as e:
                self.logger.error(f"Failed to run scenario {scenario.value}: {str(e)}")

        return results

    async def run_scenarios_parallel(
        self,
        scenarios: List[ScenarioType],
        browser_automation,
        url: str,
        max_concurrent: int = 2,
    ) -> List[ScenarioMetrics]:
        """
        Run multiple scenarios in parallel with controlled concurrency.

        Args:
            scenarios: List of scenarios to run
            browser_automation: Browser automation instance
            url: Target URL
            max_concurrent: Maximum concurrent scenario executions

        Returns:
            List of scenario metrics
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(scenario: ScenarioType):
            async with semaphore:
                return await self.run_scenario(scenario, browser_automation, url)

        tasks = [run_with_semaphore(scenario) for scenario in scenarios]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(
                    f"Scenario {scenarios[i].value} failed: {str(result)}"
                )
            else:
                valid_results.append(result)

        return valid_results

    def get_scenario_description(self, scenario_type: ScenarioType) -> Dict[str, str]:
        """
        Get description and details for a scenario type.

        Args:
            scenario_type: Scenario type

        Returns:
            Dictionary with scenario details
        """
        return {
            "type": scenario_type.value,
            "display_name": scenario_type.display_name,
            "description": scenario_type.description,
        }

    async def cleanup(self) -> None:
        """Clean up scenario runner resources."""
        try:
            # Cancel any active scenarios
            for scenario_id, task in self.active_scenarios.items():
                if not task.done():
                    self.logger.debug(f"Cancelling scenario: {scenario_id}")
                    task.cancel()

            # Wait for all tasks to complete
            if self.active_scenarios:
                await asyncio.gather(
                    *self.active_scenarios.values(), return_exceptions=True
                )

            self.active_scenarios.clear()
            self.logger.info("Scenario runner cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during scenario runner cleanup: {str(e)}")
