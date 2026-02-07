# Low-Code Performance Scanner - User Guide

A comprehensive guide for using the Low-Code Performance Scanner to analyze and optimize web application performance.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Using the CLI](#using-the-cli)
- [Using the Web Interface](#using-the-web-interface)
- [Using the API](#using-the-api)
- [Understanding Results](#understanding-results)
- [Interpreting Reports](#interpreting-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Introduction

The Low-Code Performance Scanner is a professional-grade tool designed specifically for analyzing the performance of web applications built on low-code platforms like **Bubble.io**, **OutSystems**, and **Airtable**.

### What It Measures

- **Core Web Vitals**: LCP, FID, CLS, FCP, TTFB, TBT
- **Memory Usage**: JavaScript heap, DOM nodes, event listeners
- **Network Performance**: Request timing, transfer sizes, compression
- **Rendering Performance**: Scripting, rendering, painting times
- **Platform-Specific Metrics**: Tailored for each low-code platform

### Who Should Use This Tool

- **Developers** building on low-code platforms
- **QA Engineers** performing performance testing
- **Product Managers** evaluating platform performance
- **Consultants** providing optimization recommendations
- **Researchers** studying low-code platform performance

---

## Installation

### System Requirements

- **OS**: Linux, macOS, or Windows 10/11
- **Python**: 3.8 or higher
- **Node.js**: 18 or higher (for frontend)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space

### Python Package Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install lowcode-performance-scanner

# Or install from source
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Docker Installation

```bash
# Clone repository
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Start all services
docker-compose up -d

# Or start development environment
docker-compose --profile dev up -d
```

---

## Quick Start

### 1. CLI Quick Scan

```bash
# Basic scan
lowcode-scanner scan-url https://myapp.bubbleapps.io

# With custom options
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --scenarios homepage_load regular_use_case \
  --devices desktop mobile \
  --formats html pdf json \
  --output-dir ./my-reports
```

### 2. Web Interface Quick Start

```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Start frontend
cd frontend && npm run dev

# Open browser
open http://localhost:3000
```

### 3. API Quick Start

```bash
# Start scan
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"url": "https://myapp.bubbleapps.io"}'

# Check status (use scan_id from previous response)
curl http://localhost:8000/api/scans/{scan_id}
```

---

## Using the CLI

### Basic Commands

```bash
# Show help
lowcode-scanner --help

# List available scenarios
lowcode-scanner list-scenarios

# List supported platforms
lowcode-scanner list-platforms

# Scan single URL
lowcode-scanner scan-url <URL>

# Scan multiple URLs
lowcode-scanner scan-multiple --file urls.txt

# Compare scans
lowcode-scanner compare <scan1> <scan2>

# Launch dashboard
lowcode-scanner dashboard --session-id <id>
```

### Scan URL Options

```bash
lowcode-scanner scan-url <URL> [OPTIONS]

Options:
  -s, --scenarios         Scenarios to run (multiple allowed)
  -d, --devices           Device types (multiple allowed)
  -n, --network           Network conditions (multiple allowed)
  -o, --output-dir        Output directory for reports
  -f, --formats           Report formats (multiple allowed)
  --headless / --no-headless    Run browser headless
  --screenshots / --no-screenshots  Capture screenshots
  --video / --no-video    Record video
  --timeout INTEGER       Page load timeout (seconds)
  --session-name TEXT     Session name
  --executive            Generate executive dashboard
  --academic             Generate academic report
  --baseline PATH        Compare against baseline
  --export [excel|csv|markdown|all]  Export formats
```

### Examples

#### Basic Scan

```bash
lowcode-scanner scan-url https://myapp.bubbleapps.io
```

#### Comprehensive Scan

```bash
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --scenarios homepage_load regular_use_case heavy_list_load upfront_scripting \
  --devices desktop mobile tablet \
  --network wifi 4g 3g_slow \
  --formats html pdf excel json \
  --output-dir ./reports \
  --executive --academic \
  --export excel --export csv
```

#### Mobile-Only Scan

```bash
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --devices mobile \
  --network 3g_slow \
  --scenarios homepage_load heavy_list_load
```

#### Batch Scanning

Create a `urls.txt` file:
```
https://app1.bubbleapps.io
https://app2.bubbleapps.io
https://app3.bubbleapps.io
```

Run batch scan:
```bash
lowcode-scanner scan-multiple --file urls.txt --output-dir ./batch-reports
```

#### Compare Scans

```bash
# Scan with baseline
lowcode-scanner scan-url https://myapp.bubbleapps.io --output-dir ./baseline

# Make changes to app, then scan again
lowcode-scanner scan-url https://myapp.bubbleapps.io --output-dir ./current

# Compare
lowcode-scanner compare ./baseline ./current
```

---

## Using the Web Interface

### Accessing the Interface

1. Start the backend server
2. Start the frontend development server
3. Navigate to `http://localhost:3000`

### Dashboard Overview

The dashboard consists of:

1. **Scan Input**: Enter URL and configure options
2. **Live Progress**: Real-time scan status and logs
3. **Results Panel**: Performance scores and metrics
4. **History**: Previous scans for comparison

### Performing a Scan

1. **Enter URL**: Type the URL of your application
2. **Configure Options**:
   - Select scenarios to test
   - Choose device types
   - Pick network conditions
   - Select report formats
3. **Click "Start Scan"**
4. **Watch Progress**: Monitor real-time updates
5. **View Results**: Analyze performance scores

### Understanding the Results View

- **Overall Score**: 0-100 performance rating
- **Platform Detection**: Identified low-code platform
- **Scenario Breakdown**: Performance per scenario
- **Core Web Vitals**: Key metrics visualization
- **Download Reports**: Access generated reports

---

## Using the API

See the [API Documentation](./API.md) for detailed endpoint reference.

### Python Client Example

```python
import asyncio
import requests
import websockets
import json

class ScannerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_scan(self, url, **kwargs):
        """Start a new scan."""
        payload = {
            "url": url,
            "scenarios": kwargs.get("scenarios", ["homepage_load"]),
            "devices": kwargs.get("devices", ["desktop"]),
            "network": kwargs.get("network", ["wifi"]),
            "formats": kwargs.get("formats", ["html", "json"])
        }
        response = requests.post(f"{self.base_url}/api/scans", json=payload)
        return response.json()
    
    def get_status(self, scan_id):
        """Get scan status."""
        response = requests.get(f"{self.base_url}/api/scans/{scan_id}")
        return response.json()
    
    async def watch_progress(self, scan_id, callback):
        """Watch scan progress via WebSocket."""
        uri = f"ws://localhost:8000/api/scans/{scan_id}/ws"
        async with websockets.connect(uri) as ws:
            async for message in ws:
                data = json.loads(message)
                callback(data)
                if data["data"]["status"] == "completed":
                    break

# Usage
client = ScannerClient()
scan = client.start_scan("https://myapp.bubbleapps.io")
print(f"Scan started: {scan['scan_id']}")

# Watch progress
def on_progress(data):
    print(f"Progress: {data['data']['progress']}%")

asyncio.run(client.watch_progress(scan['scan_id'], on_progress))
```

---

## Understanding Results

### Performance Score (0-100)

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Excellent | Outstanding performance |
| 80-89 | Good | Above average performance |
| 70-79 | Fair | Acceptable performance |
| 60-69 | Poor | Needs optimization |
| 0-59 | Critical | Significant issues |

### Core Web Vitals

#### Largest Contentful Paint (LCP)
- **Target**: < 2.5s
- **Measures**: Loading performance
- **What it tracks**: Time to render largest visible element

#### First Input Delay (FID)
- **Target**: < 100ms
- **Measures**: Interactivity
- **What it tracks**: Delay before responding to user input

#### Cumulative Layout Shift (CLS)
- **Target**: < 0.1
- **Measures**: Visual stability
- **What it tracks**: Unexpected layout shifts

#### First Contentful Paint (FCP)
- **Target**: < 1.8s
- **Measures**: Initial render speed
- **What it tracks**: Time to first visible content

#### Time to First Byte (TTFB)
- **Target**: < 0.8s
- **Measures**: Server response time
- **What it tracks**: Time until first byte received

#### Total Blocking Time (TBT)
- **Target**: < 200ms
- **Measures**: JavaScript execution impact
- **What it tracks**: Time blocked by long tasks

### Memory Metrics

- **JS Heap Size**: JavaScript memory usage
- **DOM Nodes**: Number of DOM elements
- **Event Listeners**: Number of active listeners
- **Peak Memory**: Maximum memory usage during scan

### Network Metrics

- **Request Count**: Total HTTP requests
- **Transfer Size**: Total data transferred
- **Resource Types**: Breakdown by type (JS, CSS, images, etc.)
- **Third-party Requests**: External dependencies

---

## Interpreting Reports

### HTML Report

Interactive dashboard with:
- Performance score gauges
- Core Web Vitals visualization
- Scenario comparison charts
- Detailed recommendations
- Waterfall timeline

### PDF Report

Executive summary including:
- High-level performance overview
- Key findings and recommendations
- Performance trends
- Platform-specific insights

### Excel Report

Detailed spreadsheets with:
- Raw metric data
- Statistical analysis
- Multiple worksheets per scenario
- Exportable for further analysis

### JSON Report

Machine-readable format for:
- CI/CD integration
- Custom dashboards
- Automated processing
- API consumption

---

## Best Practices

### 1. Establish Baselines

```bash
# Create baseline scan
lowcode-scanner scan-url https://myapp.com --session-name "Baseline v1.0"
```

### 2. Test Multiple Scenarios

Always test multiple scenarios to get a complete picture:
- Homepage load
- Regular use case
- Heavy list operations
- Upfront scripting

### 3. Test Across Devices

Test on multiple devices:
- Desktop (primary)
- Mobile (critical for user experience)
- Tablet (if applicable)

### 4. Simulate Real Network Conditions

Test with various network speeds:
- WiFi (best case)
- 4G (typical mobile)
- 3G (slow mobile)

### 5. Run Multiple Times

The scanner runs 3 times by default for statistical reliability. Don't rely on single measurements.

### 6. Monitor Trends

Regular scans help identify performance degradation:
```bash
# Weekly scan script
#!/bin/bash
DATE=$(date +%Y-%m-%d)
lowcode-scanner scan-url https://myapp.com \
  --output-dir ./trends/$DATE \
  --session-name "Weekly Scan $DATE"
```

### 7. Compare Before/After

Always compare scans before and after optimizations:
```bash
# Before optimization
lowcode-scanner scan-url https://myapp.com --output-dir ./before

# After optimization
lowcode-scanner scan-url https://myapp.com --output-dir ./after

# Compare
lowcode-scanner compare ./before ./after
```

---

## Troubleshooting

### Common Issues

#### Browser Won't Launch

**Error**: `BrowserType.launch: Executable doesn't exist`

**Solution**:
```bash
playwright install chromium
```

#### Scan Times Out

**Error**: `TimeoutError: Page load timeout`

**Solutions**:
- Increase timeout: `--timeout 60`
- Check URL accessibility
- Verify network connectivity

#### Out of Memory

**Error**: `MemoryError` or system freeze

**Solutions**:
- Reduce concurrent scans
- Close other applications
- Increase system RAM
- Use headless mode: `--headless`

#### Reports Not Generated

**Error**: Report files missing

**Solutions**:
- Check output directory permissions
- Verify disk space
- Check for error messages in logs

### Getting Help

1. **Check logs**: Look for error messages in console output
2. **Enable debug mode**: Use `--debug` flag for verbose output
3. **Review documentation**: Check [API.md](./API.md) and this guide
4. **Open an issue**: Report bugs on GitHub with:
   - Error message
   - Command used
   - Environment details
   - Expected vs actual behavior

---

## FAQ

### Q: How long does a scan take?

A typical scan takes 2-5 minutes depending on:
- Number of scenarios
- Number of devices
- Number of network conditions
- Website complexity

### Q: Can I scan any website?

Yes, but the scanner is optimized for low-code platforms. Generic websites may not get platform-specific recommendations.

### Q: Is the scanner free?

Yes, this is an open-source project under MIT license.

### Q: Do I need authentication?

For public websites, no. For private/protected applications, you may need to configure authentication (feature in development).

### Q: Can I integrate with CI/CD?

Yes! Use the API or CLI in your CI pipeline. See [API.md](./API.md) for examples.

### Q: What browsers are supported?

Currently Chromium via Playwright. Firefox and WebKit support coming in future versions.

### Q: How accurate are the measurements?

The scanner uses Chrome DevTools Protocol for high accuracy. Results are real measurements from a browser instance and highly reliable for performance analysis.

### Q: Can I export data?

Yes! Reports are available in HTML, PDF, Excel, JSON, CSV, and Markdown formats.

---

## Additional Resources

- [API Documentation](./API.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

## Support

- GitHub Issues: [github.com/your-org/lowcode-performance-scanner/issues](https://github.com/your-org/lowcode-performance-scanner/issues)
- Documentation: [docs.lowcode-scanner.com](https://docs.lowcode-scanner.com)
- Email: support@lowcode-scanner.com
