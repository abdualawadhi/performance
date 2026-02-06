#!/usr/bin/env python3
"""
Low-Code Performance Scanner CLI

Professional command-line interface for comprehensive performance testing
of low-code web applications including Bubble, OutSystems, and Airtable.

Usage:
    python -m lowcode_scanner --help
    python -m lowcode_scanner scan-url https://example.bubbleapps.io/
    python -m lowcode_scanner scan-multiple --file urls.txt
    python -m lowcode_scanner dashboard --session-id <session_id>
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from .core import LowCodePerformanceScanner, ScannerConfig
from .models import DeviceType, NetworkCondition, ReportFormat, ScenarioType

# Initialize Rich console
console = Console()

# Version info
__version__ = "1.0.2"


def print_banner():
    """Print application banner."""
    banner = f"""
========================================
    Low-Code Performance Scanner
    Version {__version__}
========================================
    Professional performance testing for low-code platforms
         * Bubble.io  * OutSystems  * Airtable
========================================
    """
    console.print(banner, style="bold blue")


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, verbose, debug):
    """
    Low-Code Performance Scanner - Professional performance testing for low-code web applications.

    This tool provides comprehensive performance analysis specifically designed for
    platforms like Bubble.io, OutSystems, and Airtable, generating detailed reports
    with actionable recommendations.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug

    if not verbose and not debug:
        print_banner()


@cli.command()
@click.argument("url")
@click.option(
    "--scenarios",
    "-s",
    multiple=True,
    type=click.Choice([s.value for s in ScenarioType], case_sensitive=False),
    help="Scenarios to test (can be specified multiple times)",
)
@click.option(
    "--devices",
    "-d",
    multiple=True,
    type=click.Choice([d.value for d in DeviceType], case_sensitive=False),
    help="Device types to test (can be specified multiple times)",
)
@click.option(
    "--network",
    "-n",
    multiple=True,
    type=click.Choice([n.value for n in NetworkCondition], case_sensitive=False),
    help="Network conditions to test (can be specified multiple times)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="performance_reports",
    help="Output directory for reports",
)
@click.option(
    "--formats",
    "-f",
    multiple=True,
    type=click.Choice([f.value for f in ReportFormat], case_sensitive=False),
    help="Report formats to generate",
)
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
@click.option(
    "--screenshots/--no-screenshots",
    default=True,
    help="Capture screenshots during testing",
)
@click.option("--video/--no-video", default=True, help="Record video during testing")
@click.option("--timeout", type=int, default=30, help="Page load timeout in seconds")
@click.option("--session-name", type=str, help="Name for the scan session")
@click.option('--executive', is_flag=True, help='Generate executive dashboard with interactive charts')
@click.option('--academic', is_flag=True, help='Generate academic report with statistical analysis')
@click.option('--baseline', type=str, help='Compare against baseline (path to baseline file)')
@click.option('--export', multiple=True, type=click.Choice(['excel', 'csv', 'markdown', 'all']), 
              help='Export formats to generate (can be specified multiple times)')
@click.pass_context
def scan_url(
    ctx,
    url,
    scenarios,
    devices,
    network,
    output_dir,
    formats,
    headless,
    screenshots,
    video,
    timeout,
    session_name,
    executive,
    academic,
    baseline,
    export,
):
    """
    Perform comprehensive performance scan of a single URL.

    This command runs a complete performance analysis including:
    - Core Web Vitals measurement
    - Memory usage monitoring
    - Network performance analysis
    - Platform-specific optimizations
    - Performance timeline with screenshots
    - Executive dashboard with interactive charts (optional)
    - Academic reports with statistical analysis (optional)

    Example:
        lowcode_scanner scan-url https://myapp.bubbleapps.io/ \\
            --scenarios homepage_load regular_use_case \\
            --devices desktop mobile \\
            --formats html json csv \\
            --executive --academic --export excel --export csv
    """
    try:
        console.print(
            f"\n[bold green]🔍 Starting performance scan for:[/bold green] {url}"
        )

        # Build configuration
        config = _build_scanner_config(
            scenarios,
            devices,
            network,
            output_dir,
            formats,
            headless,
            screenshots,
            video,
            timeout,
        )

        # Create scanner
        scanner = LowCodePerformanceScanner(config)

        # Convert scenarios
        scenario_types = [ScenarioType(s) for s in scenarios] if scenarios else None

        # Run scan with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task("Scanning...", total=None)

            # Execute scan
            result = asyncio.run(scanner.scan_url(url, session_name, scenario_types))

        if result.success:
            _display_scan_results(result)
            
            # Generate reports using the unified CLI-based reporting resource
            from .unified_reporting import save_reports
            # Use full scan ID for session name
            session_name = getattr(result, 'scan_id', 'cli_scan') or 'cli_scan'
            url = getattr(result, 'url', 'Unknown URL')
            
            # Process export formats
            export_formats = []
            if export:
                if 'all' in export:
                    export_formats = ['excel', 'csv', 'markdown']
                else:
                    export_formats = list(export)
            
            saved_reports = save_reports(
                result, url, session_name, output_dir,
                generate_executive=executive,
                generate_academic=academic,
                export_formats=export_formats
            )
            
            console.print("\n[bold green]✅ Scan completed successfully![/bold green]")
            console.print(f"[dim]Reports saved to: {output_dir}[/dim]")
            console.print(f"[dim]HTML: {saved_reports['html']}[/dim]")
            console.print(f"[dim]JSON: {saved_reports['json']}[/dim]")
            
            if executive and 'executive_dashboard' in saved_reports:
                console.print(f"[dim]Executive Dashboard: {saved_reports['executive_dashboard']}[/dim]")
            
            if academic and 'academic_report' in saved_reports:
                console.print(f"[dim]Academic Report: {saved_reports['academic_report']}[/dim]")
            
            for key, path in saved_reports.items():
                if key.startswith('export_'):
                    console.print(f"[dim]{key.replace('export_', '').title()}: {path}[/dim]")
        else:
            console.print(
                f"\n[bold red]❌ Scan failed:[/bold red] {result.error_message}"
            )
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Scan interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]💥 Error:[/bold red] {str(e)}")
        if ctx.obj.get("debug"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--file",
    "-f",
    "url_file",
    type=click.File("r"),
    help="File containing URLs to scan (one per line)",
)
@click.option(
    "--urls", "-u", multiple=True, help="URLs to scan (can be specified multiple times)"
)
@click.option(
    "--scenarios",
    "-s",
    multiple=True,
    type=click.Choice([s.value for s in ScenarioType], case_sensitive=False),
    help="Scenarios to test",
)
@click.option(
    "--devices",
    "-d",
    multiple=True,
    type=click.Choice([d.value for d in DeviceType], case_sensitive=False),
    help="Device types to test",
)
@click.option(
    "--network",
    "-n",
    multiple=True,
    type=click.Choice([n.value for n in NetworkCondition], case_sensitive=False),
    help="Network conditions to test",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="performance_reports",
    help="Output directory for reports",
)
@click.option(
    "--formats",
    "-f",
    multiple=True,
    type=click.Choice([f.value for f in ReportFormat], case_sensitive=False),
    help="Report formats to generate",
)
@click.option(
    "--concurrent", "-c", type=int, default=2, help="Maximum concurrent scans"
)
@click.option("--session-name", type=str, help="Name for the scan session")
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
@click.pass_context
def scan_multiple(
    ctx,
    url_file,
    urls,
    scenarios,
    devices,
    network,
    output_dir,
    formats,
    concurrent,
    session_name,
    headless,
):
    """
    Perform performance scans on multiple URLs.

    URLs can be provided either through a file (one URL per line) or
    directly via the --urls option.

    Example:
        lowcode_scanner scan-multiple --file urls.txt --concurrent 3
        lowcode_scanner scan-multiple --urls https://app1.com --urls https://app2.com
    """
    try:
        # Collect URLs
        url_list = []

        if url_file:
            url_list.extend(line.strip() for line in url_file if line.strip())

        if urls:
            url_list.extend(urls)

        if not url_list:
            console.print(
                "[red]❌ No URLs provided. Use --file or --urls option.[/red]"
            )
            sys.exit(1)

        console.print(
            f"\n[bold green]🔍 Starting batch scan for {len(url_list)} URLs[/bold green]"
        )

        # Build configuration
        config = _build_scanner_config(
            scenarios, devices, network, output_dir, formats, headless
        )
        config.max_concurrent_scans = concurrent

        # Create scanner
        scanner = LowCodePerformanceScanner(config)

        # Run batch scan
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task("Batch scanning...", total=len(url_list))

            session = asyncio.run(
                scanner.scan_multiple_urls(url_list, session_name, concurrent)
            )

        _display_session_results(session)
        console.print("\n[bold green]✅ Batch scan completed![/bold green]")
        console.print(f"[dim]Reports saved to: {output_dir}[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Batch scan interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]💥 Error:[/bold red] {str(e)}")
        if ctx.obj.get("debug"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--baseline", type=int, default=0, help="Index of URL to use as baseline (0-based)"
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="performance_reports",
    help="Output directory for comparison report",
)
@click.pass_context
def compare(ctx, urls, baseline, output_dir):
    """
    Compare performance between multiple URLs or versions.

    This command generates a detailed comparison report showing
    performance differences, regressions, and improvements.

    Example:
        lowcode_scanner compare https://v1.myapp.com https://v2.myapp.com
    """
    try:
        if len(urls) < 2:
            console.print("[red]❌ At least 2 URLs required for comparison[/red]")
            sys.exit(1)

        console.print(f"\n[bold blue]📊 Comparing {len(urls)} URLs[/bold blue]")

        # Display URLs
        table = Table(title="URLs to Compare")
        table.add_column("Index", style="cyan")
        table.add_column("URL", style="green")
        table.add_column("Role", style="yellow")

        for i, url in enumerate(urls):
            role = "Baseline" if i == baseline else "Comparison"
            table.add_row(str(i), url, role)

        console.print(table)
        console.print(
            "\n[dim]Comparison functionality will be implemented in future versions[/dim]"
        )

    except Exception as e:
        console.print(f"\n[bold red]💥 Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--session-id", type=str, help="Session ID to display dashboard for")
@click.option("--port", type=int, default=8080, help="Port for dashboard server")
@click.option("--host", default="localhost", help="Host for dashboard server")
def dashboard(session_id, port, host):
    """
    Launch interactive performance dashboard.

    Opens a web-based dashboard showing scan results, trends,
    and interactive performance analysis.
    """
    try:
        console.print("\n[bold blue]📊 Starting performance dashboard...[/bold blue]")
        console.print(f"[dim]Dashboard will be available at http://{host}:{port}[/dim]")
        console.print(
            "\n[yellow]⚠️  Dashboard functionality will be implemented in future versions[/yellow]"
        )

    except Exception as e:
        console.print(f"\n[bold red]💥 Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--config-file", type=click.Path(), help="Path to configuration file")
@click.option(
    "--output", "-o", type=click.Path(), help="Output path for generated configuration"
)
def init_config(config_file, output):
    """
    Initialize configuration file with default settings.

    Creates a configuration file that can be customized for
    your specific testing requirements.
    """
    try:
        console.print("\n[bold blue]⚙️  Initializing configuration...[/bold blue]")

        # Create default configuration
        default_config = ScannerConfig()

        # Output path
        output_path = Path(output or "lowcode_scanner_config.yaml")

        # Generate YAML content
        config_yaml = f"""# Low-Code Performance Scanner Configuration
# Generated on {asyncio.run(_get_current_datetime())}

# Test Scenarios
scenarios:
{_yaml_list([s.value for s in default_config.scenarios], indent=2)}

# Device Types
device_types:
{_yaml_list([d.value for d in default_config.device_types], indent=2)}

# Network Conditions
network_conditions:
{_yaml_list([n.value for n in default_config.network_conditions], indent=2)}

# Browser Configuration
browser_headless: {str(default_config.browser_headless).lower()}
capture_screenshots: {str(default_config.capture_screenshots).lower()}
record_videos: {str(default_config.record_videos).lower()}
enable_performance_profiling: {str(default_config.enable_performance_profiling).lower()}

# Output Configuration
output_directory: "{default_config.output_directory}"
report_formats:
{_yaml_list([f.value for f in default_config.report_formats], indent=2)}

# Timeouts (seconds)
page_timeout_seconds: {default_config.page_timeout_seconds}
scenario_timeout_seconds: {default_config.scenario_timeout_seconds}
max_concurrent_scans: {default_config.max_concurrent_scans}

# Quality Thresholds
performance_score_threshold: {default_config.performance_score_threshold}
memory_usage_threshold_mb: {default_config.memory_usage_threshold_mb}
load_time_threshold_seconds: {default_config.load_time_threshold_seconds}

# Reporting Options
include_recommendations: {str(default_config.include_recommendations).lower()}
include_comparisons: {str(default_config.include_comparisons).lower()}
generate_executive_summary: {str(default_config.generate_executive_summary).lower()}
"""

        # Write configuration file
        output_path.write_text(config_yaml)

        console.print(f"[green]✅ Configuration file created:[/green] {output_path}")
        console.print("[dim]Edit the file to customize your testing parameters[/dim]")

    except Exception as e:
        console.print(f"\n[bold red]💥 Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
def list_scenarios():
    """List all available test scenarios."""
    console.print("\n[bold blue]📋 Available Test Scenarios[/bold blue]")

    table = Table()
    table.add_column("Scenario", style="cyan")
    table.add_column("Description", style="green")

    for scenario in ScenarioType:
        table.add_row(scenario.value, scenario.description)

    console.print(table)


@cli.command()
def list_platforms():
    """List supported low-code platforms."""
    console.print("\n[bold blue]🏗️  Supported Low-Code Platforms[/bold blue]")

    table = Table()
    table.add_column("Platform", style="cyan")
    table.add_column("Status", style="green")

    platforms = {
        "Bubble.io": "✅ Fully Supported",
        "OutSystems": "✅ Fully Supported",
        "Airtable": "✅ Fully Supported",
        "Mendix": "🔄 In Development",
        "Microsoft PowerApps": "🔄 In Development",
        "Salesforce Lightning": "📋 Planned",
        "Appian": "📋 Planned",
    }

    for platform, status in platforms.items():
        table.add_row(platform, status)

    console.print(table)


def _build_scanner_config(
    scenarios,
    devices,
    network,
    output_dir,
    formats,
    headless=True,
    screenshots=True,
    video=True,
    timeout=30,
):
    """Build scanner configuration from CLI arguments."""
    config = ScannerConfig()

    if scenarios:
        config.scenarios = [ScenarioType(s) for s in scenarios]
    if devices:
        config.device_types = [DeviceType(d) for d in devices]
    if network:
        config.network_conditions = [NetworkCondition(n) for n in network]
    if formats:
        config.report_formats = [ReportFormat(f) for f in formats]

    config.output_directory = Path(output_dir)
    config.browser_headless = headless
    config.capture_screenshots = screenshots
    config.record_videos = video
    config.page_timeout_seconds = timeout

    return config


def _display_scan_results(result):
    """Display scan results using the unified CLI-based reporting resource."""
    console.print("\n[bold blue]📊 Performance Results[/bold blue]")

    try:
        # Import the unified CLI-based reporting module
        from .unified_reporting import get_console_display_data
        
        # Get console display data using CLI logic
        # Use full scan ID for session name
        session_name = getattr(result, 'scan_id', 'cli_scan') or 'cli_scan'
        url = getattr(result, 'url', 'Unknown URL')
        display_data = get_console_display_data(result, url, session_name)
        
        # Display Overview section
        overview = display_data["overview"]
        console.print("\n[bold cyan]📋 Overview[/bold cyan]")
        overview_table = Table(show_header=False, box=None)
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        
        overview_table.add_row("Overall Score", f"[bold green]{overview['overall_score']:.1f}/100[/bold green]")
        overview_table.add_row("Platform", overview['platform'])
        overview_table.add_row("Scenarios Tested", str(overview['scenarios_tested']))
        overview_table.add_row("Generated", overview['generated'])
        
        console.print(overview_table)
        console.print(f"\n[dim]{overview['executive_summary']}[/dim]")

        # Display Performance Matrix
        scenarios = display_data["scenarios"]
        if scenarios:
            console.print("\n[bold cyan]📊 Performance Matrix[/bold cyan]")
            
            matrix_table = Table()
            matrix_table.add_column("Scenario", style="cyan")
            matrix_table.add_column("Load Time (s)", justify="right")
            matrix_table.add_column("Memory (MB)", justify="right")
            matrix_table.add_column("Performance Traces", justify="left")
            matrix_table.add_column("Key Observations", justify="left")
            matrix_table.add_column("Score", justify="right")

            for scenario in scenarios:
                score_color = (
                    "green" if scenario['score'] >= 80
                    else "yellow" if scenario['score'] >= 60
                    else "red"
                )
                
                traces_text = scenario['traces'] if scenario['traces'] else 'No traces'
                obs_text = '\n'.join(scenario['observations']) if scenario['observations'] else 'No observations'

                matrix_table.add_row(
                    scenario['name'],
                    f"{scenario['load_time']:.2f}",
                    f"{scenario['memory']:.1f}",
                    traces_text,
                    obs_text,
                    f"[{score_color}]{scenario['score']:.1f}[/{score_color}]",
                )

            console.print(matrix_table)

        # Display Key Observations
        unique_obs = display_data["unique_observations"]
        if unique_obs:
            console.print("\n[bold yellow]🔍 Key Observations[/bold yellow]")
            for obs in unique_obs:
                console.print(f"  • {obs}")
        else:
            console.print("\n[dim]No key observations available[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error displaying results: {e}[/red]")
        # Fallback to basic display
        overall = getattr(result.performance_matrix, 'overall_score', 0)
        console.print(f"\nOverall Score: {overall:.1f}/100")


def _display_session_results(session):
    """Display session results summary."""
    console.print("\n[bold blue]📊 Batch Scan Results[/bold blue]")

    # Session summary
    summary = session.session_summary

    success_color = (
        "green"
        if summary["success_rate"] >= 90
        else "yellow"
        if summary["success_rate"] >= 70
        else "red"
    )

    console.print(
        Panel(
            f"Success Rate: [{success_color}]{summary['success_rate']:.1f}%[/{success_color}]\n"
            f"Total Scans: {summary['total_scans']}\n"
            f"Average Score: {summary.get('average_performance_score', 0):.1f}/100",
            title="Session Summary",
            title_align="center",
        )
    )

    # Platform distribution
    if summary.get("platform_distribution"):
        console.print("\n[bold yellow]🏗️  Platform Distribution[/bold yellow]")
        for platform, count in summary["platform_distribution"].items():
            console.print(f"  • {platform.title()}: {count} app(s)")


def _yaml_list(items, indent=0):
    """Format a list for YAML output."""
    return "\n".join(f"{' ' * indent}- {item}" for item in items)


async def _get_current_datetime():
    """Get current datetime string."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()
