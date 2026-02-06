"""
FastAPI Backend Server for Low-Code Performance Scanner
========================================================

This module provides a REST API and WebSocket interface for the performance scanner,
allowing web-based interaction and real-time progress updates.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl

sys.path.append(str(Path(__file__).parent.parent))

from lowcode_scanner.core import LowCodePerformanceScanner, ScannerConfig
from lowcode_scanner.models import (
    DeviceType,
    LowCodePlatform,
    NetworkCondition,
    ReportFormat,
    ScenarioType,
)

# ============================================================================
# Pydantic Models for API
# ============================================================================


class ScanRequest(BaseModel):
    """Request model for starting a scan."""

    url: HttpUrl = Field(..., description="URL to scan")
    scenarios: List[str] = Field(
        default=[
            "homepage_load",
            "regular_use_case",
            "heavy_list_load",
            "upfront_scripting",
        ],
        description="Test scenarios to run",
    )
    devices: List[str] = Field(
        default=["desktop", "mobile"], description="Device types to test"
    )
    network: List[str] = Field(
        default=["wifi"], description="Network conditions to simulate"
    )
    formats: List[str] = Field(
        default=["html", "json"], description="Report formats to generate"
    )
    session_name: Optional[str] = Field(
        default=None, description="Optional session name"
    )


class ScanStatus(BaseModel):
    """Status model for scan progress."""

    scan_id: str
    status: str  # queued, running, completed, failed
    progress: float  # 0-100
    current_step: Optional[str] = None
    url: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ScanResult(BaseModel):
    """Result model for completed scan."""

    scan_id: str
    url: str
    overall_score: float
    platform: str
    scenarios_count: int
    reports: List[Dict[str, str]]
    performance_summary: Dict
    completed_at: datetime


# ============================================================================
# FastAPI Application
# ============================================================================

# API version
API_VERSION = "1.1.0"

app = FastAPI(
    title="Low-Code Performance Scanner API",
    description="Professional performance testing API for low-code web applications",
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
# Read allowed origins from environment variable, default to localhost for development
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State Management
# ============================================================================


class ScanManager:
    """Manages scan jobs and their status."""

    def __init__(self):
        self.scans: Dict[str, Dict] = {}
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def create_scan(self, url: str, config: Dict) -> str:
        """Create a new scan job."""
        scan_id = str(uuid.uuid4())
        self.scans[scan_id] = {
            "scan_id": scan_id,
            "url": url,
            "status": "queued",
            "progress": 0,
            "current_step": None,
            "logs": [],
            "config": config,
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": None,
        }
        return scan_id

    def update_scan(self, scan_id: str, **kwargs):
        """Update scan status."""
        if scan_id in self.scans:
            # support appending a log entry via 'append_log'
            if "append_log" in kwargs:
                log_entry = kwargs.pop("append_log")
                self.scans[scan_id].setdefault("logs", []).append(log_entry)
                print(f"Updated scan {scan_id} with log: {log_entry}")

            self.scans[scan_id].update(kwargs)
            print(f"Updated scan {scan_id} with progress: {kwargs.get('progress', 'unchanged')}")
            # Notify connected clients
            asyncio.create_task(self.broadcast_update(scan_id))

    async def broadcast_update(self, scan_id: str):
        """Broadcast scan update to all connected clients."""
        if scan_id in self.active_connections:
            scan_data = self.scans.get(scan_id)
            if scan_data:
                message = json.dumps(
                    {
                        "type": "progress",
                        "data": {
                            "scan_id": scan_id,
                            "status": scan_data["status"],
                            "progress": scan_data["progress"],
                            "current_step": scan_data["current_step"],
                            "logs": scan_data.get("logs", [])[-200:],
                            "result": scan_data.get("result"),
                        },
                    }
                )
                print(f"Broadcasting to {len(self.active_connections[scan_id])} WebSocket clients for scan {scan_id}")
                # Send to all connected websockets
                disconnected = []
                for ws in self.active_connections[scan_id]:
                    try:
                        await ws.send_text(message)
                        print(f"Sent WebSocket message: progress={scan_data['progress']}, logs_count={len(scan_data.get('logs', []))}")
                    except:
                        disconnected.append(ws)

                # Clean up disconnected clients
                for ws in disconnected:
                    self.active_connections[scan_id].remove(ws)

    def get_scan(self, scan_id: str) -> Optional[Dict]:
        """Get scan by ID."""
        return self.scans.get(scan_id)

    def get_all_scans(self) -> List[Dict]:
        """Get all scans."""
        return list(self.scans.values())

    def add_connection(self, scan_id: str, websocket: WebSocket):
        """Add WebSocket connection for scan."""
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)

    def remove_connection(self, scan_id: str, websocket: WebSocket):
        """Remove WebSocket connection."""
        if scan_id in self.active_connections:
            try:
                self.active_connections[scan_id].remove(websocket)
            except ValueError:
                pass


scan_manager = ScanManager()


# ============================================================================
# Helper Functions
# ============================================================================


async def run_scan_job(scan_id: str, url: str, config: Dict):
    """Run the actual scan job."""
    try:
        scan_manager.update_scan(
            scan_id,
            status="running",
            started_at=datetime.now(),
            progress=5,
            current_step="Initializing scanner...",
        )

        # Parse scenarios
        scenarios = []
        for scenario_str in config.get("scenarios", ["homepage_load"]):
            try:
                scenarios.append(ScenarioType[scenario_str.upper()])
            except KeyError:
                pass

        # Parse devices
        devices = []
        for device_str in config.get("devices", ["desktop"]):
            try:
                devices.append(DeviceType[device_str.upper()])
            except KeyError:
                pass

        # Parse network conditions
        networks = []
        for network_str in config.get("network", ["wifi"]):
            try:
                networks.append(NetworkCondition[network_str.upper()])
            except KeyError:
                pass

        # Parse report formats
        formats = []
        for format_str in config.get("formats", ["html", "json"]):
            try:
                formats.append(ReportFormat[format_str.upper()])
            except KeyError:
                pass

        scan_manager.update_scan(
            scan_id, progress=10, current_step="Configuring scanner..."
        )

        # Create scanner configuration
        print(f"Configuring scanner with scenarios: {scenarios}")
        print(f"Devices: {devices}")
        print(f"Network conditions: {networks}")
        print(f"Report formats: {formats}")
        
        # Build scanner configuration using the same logic as CLI
        from lowcode_scanner.__main__ import _build_scanner_config
        scanner_config = _build_scanner_config(
            scenarios=scenarios,
            devices=devices,
            network=networks,
            output_dir="performance_reports",
            formats=formats,
            headless=True,
            screenshots=True,
            video=False,
            timeout=30
        )

        scan_manager.update_scan(
            scan_id, progress=15, current_step="Starting performance scan..."
        )

        # Create scanner instance
        scanner = LowCodePerformanceScanner(scanner_config)

        # Attach a logging handler to stream scanner logs to the scan manager
        try:
            import logging

            # calculate total observable runs to estimate progress
            total_runs = (
                max(1, scanner_config.num_runs)
                * max(1, len(scanner_config.scenarios))
                * max(1, len(scanner_config.device_types))
                * max(1, len(scanner_config.network_conditions))
            )

            class ScanLogHandler(logging.Handler):
                def __init__(self):
                    super().__init__()
                    self._run_counter = 0
                    self._total_runs = total_runs

                def emit(self, record):
                    try:
                        msg = self.format(record)
                        # Append the log
                        scan_manager.update_scan(scan_id, append_log=msg, current_step=msg)

                        # Update progress heuristically based on observed "Run X/Y" messages
                        try:
                            text = msg
                            run_match = None
                            # look for patterns like 'Run 1/3' or 'Run 2/3'
                            import re

                            run_match = re.search(r"Run\s+(\d+)\/(\d+)", text)
                            if run_match:
                                # increment global counter
                                self._run_counter += 1
                                progress_pct = min(95, int(15 + (self._run_counter / max(1, self._total_runs)) * 80))
                                scan_manager.update_scan(scan_id, progress=progress_pct)
                            elif "Completed scenario" in text:
                                # nudge progress forward on scenario completion
                                self._run_counter = min(self._total_runs, self._run_counter + 1)
                                progress_pct = min(95, int(15 + (self._run_counter / max(1, self._total_runs)) * 80))
                                scan_manager.update_scan(scan_id, progress=progress_pct)
                        except Exception:
                            pass
                    except Exception:
                        pass

            handler = ScanLogHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            # Attach to scanner logger (if it exists)
            try:
                scanner.logger.addHandler(handler)
            except Exception:
                pass
        except Exception:
            pass

        # Run the scan - use full UUID as session name
        session_name = config.get("session_name") or scan_id

        # Update progress during scan (simplified - would need callback integration)
        scan_manager.update_scan(
            scan_id, progress=25, current_step="Running test scenarios..."
        )

        try:
            print(f"Attempting to run scanner for URL: {url}")
            print(f"Scanner config: {scanner_config}")
            
            # For now, use the same scanner execution as CLI
            # This ensures identical behavior between CLI and web
            import subprocess
            import sys
            import os
            
            # Build CLI command
            cli_cmd = [
                sys.executable, "-m", "lowcode_scanner", "scan-url", url
            ]
            
            # Add scenarios
            for scenario in scenarios:
                cli_cmd.extend(["--scenarios", scenario.value])
            
            # Add devices
            for device in devices:
                cli_cmd.extend(["--devices", device.value])
            
            # Add network conditions
            for network in networks:
                cli_cmd.extend(["--network", network.value])
            
            # Add formats
            for format in formats:
                cli_cmd.extend(["--formats", format.value])
            
            # Add other options
            cli_cmd.extend([
                "--output-dir", "performance_reports",
                "--session-name", session_name,
                "--timeout", "30",
                "--no-headless"
            ])
            
            print(f"Running CLI command: {' '.join(cli_cmd)}")
            
            # Change to the parent directory to run CLI
            original_cwd = os.getcwd()
            os.chdir("..")
            
            try:
                # Set environment to avoid banner display issues
                import os
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                # Run subprocess with real-time output streaming
                process = subprocess.Popen(
                    cli_cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    bufsize=1,  # Line buffered
                    universal_newlines=True,
                    env=env
                )
                
                # Stream output in real-time
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Clean and forward log message to WebSocket clients
                        log_line = output.strip()
                        if log_line:
                            # Parse progress from CLI output
                            current_scan = scan_manager.scans.get(scan_id, {})
                            progress = current_scan.get('progress', 0)
                            current_step = log_line
                            
                            # Extract progress indicators from CLI output
                            if "Run" in log_line and "/" in log_line:
                                # Parse "Run 1/3" patterns
                                import re
                                run_match = re.search(r"Run\s+(\d+)/(\d+)", log_line)
                                if run_match:
                                    run_num = int(run_match.group(1))
                                    total_runs = int(run_match.group(2))
                                    # Calculate progress based on runs
                                    base_progress = 25 + (run_num / total_runs) * 60
                                    progress = min(95, int(base_progress))
                            
                            # Clean up scanner log messages
                            if "lowcode_scanner.core.scanner" in log_line:
                                current_step = log_line.split("-")[-1].strip() if "-" in log_line else log_line
                                current_step = current_step.replace("INFO", "").strip()
                            
                            # Update scan with live progress
                            scan_manager.update_scan(
                                scan_id, 
                                append_log=log_line,
                                progress=progress,
                                current_step=current_step
                            )
                
                # Get final result
                return_code = process.poll()
                print(f"CLI exit code: {return_code}")
                
                if return_code != 0:
                    raise Exception(f"CLI failed with exit code {return_code}")
                
                result_stdout = process.stdout.read() or ""
                print(f"CLI stdout: {result_stdout[-1000:] if result_stdout else 'None'}")
                
                # Load the generated JSON report
                import json
                import glob
                
                # Find the most recent JSON report (CLI generates its own scan ID)
                json_files = glob.glob("performance_reports/*.json")
                if not json_files:
                    raise Exception("No CLI JSON reports found")
                
                # Get the most recent file
                json_file = max(json_files, key=os.path.getctime)
                print(f"Found latest CLI report: {json_file}")
                
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                print(f"Successfully loaded CLI result with {len(json_data.get('scenarios', []))} scenarios")
                
                # Create a simple result object that works with unified reporting
                class CLIScanResult:
                    def __init__(self, json_data):
                        self.scan_id = json_data.get('scan_id', session_name)
                        self.url = json_data.get('url', url)
                        self.platform = json_data.get('platform', 'generic')
                        self.performance_matrix = type('PerformanceMatrix', (), {
                            'rows': [],
                            'overall_score': json_data.get('overall_score', 0)
                        })()
                        self.scenarios_data = json_data.get('scenarios', [])
                
                result = CLIScanResult(json_data)
                    
            except subprocess.TimeoutExpired:
                print("CLI execution timed out")
                raise Exception("Scan timed out after 300 seconds")
            except Exception as e:
                print(f"Error during CLI execution: {e}")
                raise e
            finally:
                os.chdir(original_cwd)
            
            print(f"Scanner completed successfully. Scenarios tested: {len(result.performance_matrix.rows)}")
            
            # Use real scanner result - no fallback to mock data
            if len(result.performance_matrix.rows) == 0:
                print("Warning: Scanner returned 0 scenarios - using empty result")
                print(f"Scanner result details: {result}")
                # Create empty result instead of mock
                from lowcode_scanner.models import ScanResult, PerformanceMatrix, LowCodePlatform, LowCodePerformanceMetrics, CoreWebVitals, MemoryUsageMetrics, NetworkMetrics, PlatformSpecificMetrics
                result = ScanResult(
                    scan_id=scan_id,
                    url=url,
                    platform=LowCodePlatform.GENERIC,
                    performance_metrics=LowCodePerformanceMetrics(
                        url=url,
                        platform=LowCodePlatform.GENERIC,
                        test_session_id=scan_id,
                        core_web_vitals=CoreWebVitals(
                            largest_contentful_paint_ms=0.0,
                            first_input_delay_ms=0.0,
                            time_to_interactive_ms=0.0,
                            total_blocking_time_ms=0.0
                        ),
                        memory_metrics=MemoryUsageMetrics(
                            peak_heap_size_mb=0.0,
                            initial_heap_size_mb=0.0,
                            final_heap_size_mb=0.0,
                            major_gc_count=0,
                            minor_gc_count=0,
                            memory_samples=[],
                            memory_efficiency_score=0.0,
                            memory_growth_rate=0.0
                        ),
                        network_metrics=NetworkMetrics(
                            total_requests=0,
                            failed_requests=0,
                            total_transfer_size_kb=0.0,
                            average_response_time_ms=0.0,
                            cache_hit_rate=0.0,
                            compression_ratio=0.0,
                            network_efficiency_score=0.0
                        ),
                        platform_specific_metrics=PlatformSpecificMetrics(
                            platform="generic",
                            custom_metrics={},
                            platform_optimizations=[],
                            platform_specific_issues=[]
                        )
                    ),
                    performance_matrix=PerformanceMatrix(
                        url=url,
                        platform=LowCodePlatform.GENERIC,
                        rows=[],
                        overall_score=0.0,
                        critical_scenarios=[],
                        executive_summary="No scenarios were executed",
                        key_recommendations=[]
                    ),
                    test_configuration={
                        "scenarios": list(scenarios),
                        "devices": list(devices),
                        "network": list(networks),
                        "formats": list(formats)
                    }
                )
            else:
                print(f"Scanner returned {len(result.performance_matrix.rows)} scenarios, using real result")
                
        except Exception as scan_error:
            print(f"Scanner error: {scan_error}")
            print(f"Error type: {type(scan_error)}")
            import traceback
            traceback.print_exc()
            # Return error instead of mock data
            scan_manager.update_scan(
                scan_id,
                status="failed",
                progress=0,
                current_step=f"Scan failed: {str(scan_error)}",
                completed_at=datetime.now(),
                error=str(scan_error),
            )
            return

        scan_manager.update_scan(
            scan_id, progress=90, current_step="Generating reports..."
        )

        # Generate reports using the unified CLI-based reporting resource
        try:
            from lowcode_scanner.unified_reporting import save_reports, generate_json_report, get_aggregated_scenarios, get_executive_summary

            # For CLI-based results, use the JSON data directly
            if hasattr(result, 'scenarios_data'):
                # Use CLI-generated reports directly - they're already in the right format
                saved_reports = {
                    'html': f"performance_reports/{session_name}.html",
                    'json': f"performance_reports/{session_name}.json"
                }

                # Get JSON content for API response using CLI data
                json_content = result.scenarios_data if isinstance(result.scenarios_data, dict) else {
                    "scan_id": scan_id,  # Use full UUID for consistency
                    "url": url,
                    "platform": result.platform,
                    "overall_score": result.performance_matrix.overall_score,
                    "generated_at": datetime.now().isoformat(),
                    "scenarios": result.scenarios_data,
                    "executive_summary": get_executive_summary(result.performance_matrix.overall_score),
                    "scenarios_count": len(result.scenarios_data),
                    "platform_detected": result.platform,
                    "performance_summary": {
                        "overall_score": result.performance_matrix.overall_score,
                        "total_scenarios": len(result.scenarios_data),
                        "platform": result.platform,
                        "average_load_time": sum(s.get('load_time', 0) for s in result.scenarios_data) / len(result.scenarios_data) if result.scenarios_data else 0,
                        "average_memory_mb": sum(s.get('memory', 0) for s in result.scenarios_data) / len(result.scenarios_data) if result.scenarios_data else 0,
                        "scenarios": result.scenarios_data
                    }
                }
            else:
                # Use regular unified reporting for ScanResult objects
                saved_reports = save_reports(result, url, session_name, "performance_reports")
                json_content = generate_json_report(result, url, session_name)

            print(f"Generated unified CLI-based reports: {saved_reports}")

            # Update in-memory scan result with CLI-based data for WS consumers
            try:
                scan_manager.update_scan(
                    scan_id,
                    result={
                        **(scan_manager.scans.get(scan_id, {}).get('result', {}) or {}),
                        'aggregated_scenarios': result.scenarios_data if hasattr(result, 'scenarios_data') else get_aggregated_scenarios(result),
                        'executive_summary': get_executive_summary(result.performance_matrix.overall_score),
                        'performance_summary': json_content['performance_summary'],
                    },
                )
            except Exception:
                pass
            
            # Prepare result data
            reports = []
            if Path("performance_reports").exists():
                for report_file in Path("performance_reports").glob(f"*{session_name}*"):
                    reports.append(
                        {
                            "name": report_file.name,
                            "path": str(report_file),
                            "type": report_file.suffix[1:],
                            "size": report_file.stat().st_size,
                        }
                    )

            # Attach a full, consistent result payload for Web and API consumers
            try:
                aggregated = result.scenarios_data if hasattr(result, 'scenarios_data') else get_aggregated_scenarios(result)
            except Exception:
                aggregated = []

            scan_manager.update_scan(
                scan_id,
                status="completed",
                progress=100,
                current_step="Scan completed successfully!",
                completed_at=datetime.now(),
                result={
                    "scan_id": scan_id,  # Use full UUID for consistency
                    "url": url,
                    "overall_score": result.performance_matrix.overall_score,
                    "platform": result.platform.value,
                    "scenarios_count": len(result.performance_matrix.rows),
                    "aggregated_scenarios": aggregated,
                    "executive_summary": get_executive_summary(result.performance_matrix.overall_score),
                    "reports": reports,
                    "performance_summary": json_content['performance_summary'],
                },
            )
            
        except Exception as e:
            print(f"Error using unified CLI-based reporting: {e}")
            # Fallback to basic completion
            scan_manager.update_scan(
                scan_id,
                status="completed",
                progress=100,
                current_step="Scan completed successfully!",
                completed_at=datetime.now(),
                result={
                    "overall_score": result.performance_matrix.overall_score,
                    "platform": result.platform.value,
                    "scenarios_count": len(result.performance_matrix.rows),
                    "reports": [],
                    "performance_summary": {},
                },
            )

    except Exception as e:
        scan_manager.update_scan(
            scan_id,
            status="failed",
            progress=0,
            current_step=f"Scan failed",
            completed_at=datetime.now(),
            error=str(e),
        )


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns basic API information and links to documentation.
    """
    return {
        "name": "Low-Code Performance Scanner API",
        "version": API_VERSION,
        "status": "operational",
        "docs": "/api/docs",
        "endpoints": {
            "scans": "/api/scans",
            "health": "/api/health",
            "docs": "/api/docs",
        }
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Health status with timestamp and version information.
    """
    import psutil
    
    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat(),
        "system": {
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "cpu_percent": psutil.cpu_percent(interval=0.1),
        },
        "scans": {
            "total": len(scan_manager.scans),
            "running": len([s for s in scan_manager.scans.values() if s["status"] == "running"]),
            "queued": len([s for s in scan_manager.scans.values() if s["status"] == "queued"]),
        }
    }


@app.post("/api/scans", response_model=Dict)
async def create_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Create a new scan job."""
    try:
        # Create scan
        scan_id = scan_manager.create_scan(
            url=str(request.url),
            config={
                "scenarios": request.scenarios,
                "devices": request.devices,
                "network": request.network,
                "formats": request.formats,
                "session_name": request.session_name,
            },
        )

        # Start scan in background
        background_tasks.add_task(
            run_scan_job,
            scan_id,
            str(request.url),
            scan_manager.scans[scan_id]["config"],
        )

        return {
            "scan_id": scan_id,
            "status": "queued",
            "message": "Scan job created and queued for execution",
            "websocket_url": f"/api/scans/{scan_id}/ws",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scans/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status by ID."""
    scan = scan_manager.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": scan["scan_id"],
        "url": scan["url"],
        "status": scan["status"],
        "progress": scan["progress"],
        "current_step": scan["current_step"],
        "started_at": scan["started_at"],
        "completed_at": scan["completed_at"],
        "error": scan["error"],
        "result": scan["result"],
    }


@app.get("/api/scans")
async def list_scans(limit: int = 50, status: Optional[str] = None):
    """List all scans."""
    scans = scan_manager.get_all_scans()

    # Filter by status if provided
    if status:
        scans = [s for s in scans if s["status"] == status]

    # Sort by created date (most recent first)
    scans.sort(key=lambda x: x.get("started_at") or datetime.min, reverse=True)

    # Limit results
    scans = scans[:limit]

    return {
        "total": len(scans),
        "scans": [
            {
                "scan_id": s["scan_id"],
                "url": s["url"],
                "status": s["status"],
                "progress": s["progress"],
                "platform": s.get('result', {}).get('platform') if s.get('result') else None,
                "overall_score": s.get('result', {}).get('overall_score') if s.get('result') else None,
                "started_at": s["started_at"],
                "completed_at": s["completed_at"],
            }
            for s in scans
        ],
    }


@app.get("/api/scans/{scan_id}/result")
async def get_scan_result(scan_id: str):
    """Get detailed scan result."""
    scan = scan_manager.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["status"] != "completed":
        raise HTTPException(
            status_code=400, detail=f"Scan is {scan['status']}, not completed"
        )

    if not scan["result"]:
        raise HTTPException(status_code=404, detail="Scan result not available")

    return scan["result"]


@app.get("/api/scans/{scan_id}/reports/{report_name}")
async def download_report(scan_id: str, report_name: str):
    """Download a specific report file."""
    scan = scan_manager.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["status"] != "completed":
        raise HTTPException(status_code=400, detail="Scan not completed yet")

    # Find the report file
    reports_dir = Path("performance_reports")
    
    # Try to find the report file by pattern - use unified session name
    session_name = f"scan_{scan_id[:8]}"
    
    if report_name == "html":
        report_pattern = f"{session_name}.html"
    elif report_name == "json":
        report_pattern = f"{session_name}.json"
    else:
        report_pattern = report_name
    
    report_path = reports_dir / report_pattern

    if not report_path.exists():
        # Try to find any file with the session name and requested extension
        matching_files = list(reports_dir.glob(f"{session_name}*.{report_name}"))
        if matching_files:
            report_path = matching_files[0]
        else:
            raise HTTPException(status_code=404, detail=f"Report file not found: {report_pattern}")

    return FileResponse(
        report_path, media_type="application/octet-stream", filename=report_path.name
    )


@app.delete("/api/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan and its results."""
    scan = scan_manager.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Remove from manager
    del scan_manager.scans[scan_id]

    return {"message": "Scan deleted successfully"}


@app.websocket("/api/scans/{scan_id}/ws")
async def scan_websocket(websocket: WebSocket, scan_id: str):
    """WebSocket endpoint for real-time scan updates."""
    await websocket.accept()

    # Check if scan exists
    scan = scan_manager.get_scan(scan_id)
    if not scan:
        await websocket.close(code=4004, reason="Scan not found")
        return

    # Add connection
    scan_manager.add_connection(scan_id, websocket)

    try:
        # Send initial status including current logs and any result so clients
        # receive a complete snapshot on connect.
        await websocket.send_json(
            {
                "type": "connected",
                "data": {
                    "scan_id": scan_id,
                    "status": scan["status"],
                    "progress": scan["progress"],
                    "logs": scan.get("logs", [])[-200:],
                    "result": scan.get("result"),
                },
            }
        )

        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed (e.g., cancel request)
            except WebSocketDisconnect:
                break

    finally:
        # Remove connection
        scan_manager.remove_connection(scan_id, websocket)


@app.get("/api/platforms")
async def get_supported_platforms():
    """Get list of supported platforms."""
    return {
        "platforms": [
            {"id": "bubble", "name": "Bubble.io", "status": "fully_supported"},
            {"id": "outsystems", "name": "OutSystems", "status": "fully_supported"},
            {"id": "airtable", "name": "Airtable", "status": "fully_supported"},
            {"id": "mendix", "name": "Mendix", "status": "in_development"},
            {"id": "powerapps", "name": "Microsoft PowerApps", "status": "planned"},
        ]
    }


@app.get("/api/scenarios")
async def get_available_scenarios():
    """Get list of available test scenarios."""
    return {
        "scenarios": [
            {
                "id": "homepage_load",
                "name": "Homepage Load",
                "description": "Tests initial page load performance",
            },
            {
                "id": "regular_use_case",
                "name": "Regular Use Case",
                "description": "Tests typical user interactions",
            },
            {
                "id": "heavy_list_load",
                "name": "Heavy List Load",
                "description": "Tests performance with large data sets",
            },
            {
                "id": "upfront_scripting",
                "name": "Upfront Scripting",
                "description": "Tests JavaScript bundle loading and execution",
            },
        ]
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Low-Code Performance Scanner API starting...")
    print("📊 API Documentation: http://localhost:8000/api/docs")
    print("🌐 Frontend: http://localhost:3000 (if running)")

    # Ensure reports directory exists
    Path("performance_reports").mkdir(exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Low-Code Performance Scanner API shutting down...")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
