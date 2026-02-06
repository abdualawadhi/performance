# 📖 How to Use the Performance Scanner

## 🎯 What This Does

This is a **professional performance testing tool** for low-code applications like:
- Bubble.io
- OutSystems
- Airtable
- Any web application

It automatically tests your app and generates:
- 📊 Performance metrics (load time, memory usage, etc.)
- 📈 Performance traces (scripting, rendering, paint breakdowns)
- 🖼️ Screenshots and timeline visualizations
- 📑 Professional HTML/PDF reports with recommendations

---

## ⚡ Quick Start (Copy & Paste)

### 1️⃣ Scan a Website

```bash
# Single URL scan
python -m lowcode_scanner scan-url https://example.com

# Or from the backend directory
cd backend
python main.py
```

### 2️⃣ Generate Reports

```bash
# Generate HTML report
python -m lowcode_scanner scan-url https://example.com --formats html

# Generate multiple formats
python -m lowcode_scanner scan-url https://example.com --formats html json pdf
```

### 3️⃣ Use the Web Interface

```bash
# Start the web server
cd backend
python main.py

# Open browser to
http://localhost:8000
```

---

## 🔧 Usage Methods

### Method 1: Command Line (Recommended for quick tests)

```bash
# Basic scan
python -m lowcode_scanner scan-url https://myapp.com

# Specific scenarios
python -m lowcode_scanner scan-url https://myapp.com \
    --scenarios homepage_load upfront_scripting \
    --formats html

# Multiple URLs from file
python -m lowcode_scanner scan-multiple --file urls.txt

# Custom settings
python -m lowcode_scanner scan-url https://myapp.com \
    --device mobile \
    --network 4g \
    --output-dir ./reports
```

**Available Scenarios:**
- `homepage_load` - Initial page load
- `upfront_scripting` - JavaScript execution
- `regular_use` - Normal user interactions
- `heavy_list_load` - Large data processing

**Device Types:**
- `desktop` (default)
- `mobile`
- `tablet`

**Network Conditions:**
- `wifi` (default)
- `3g`
- `4g`
- `5g`

### Method 2: Web Interface (Best for ongoing use)

```bash
# Start server
cd backend
python main.py

# Open http://localhost:8000 in your browser
```

**Web Interface Features:**
- 📋 Drag-and-drop URL input
- ⚙️ Configure scenarios, device, network
- 🔄 Real-time progress updates
- 📊 View results immediately
- 💾 Download reports

### Method 3: Python API (For custom integration)

```python
from lowcode_scanner.core import LowCodePerformanceScanner, ScannerConfig
from lowcode_scanner.models import DeviceType, NetworkCondition

# Create config
config = ScannerConfig(
    url="https://myapp.com",
    device_type=DeviceType.DESKTOP,
    network_condition=NetworkCondition.WIFI,
)

# Run scan
scanner = LowCodePerformanceScanner(config)
results = scanner.scan()

# Access results
print(f"Load Time: {results.performance_metrics.load_time}s")
print(f"Memory Peak: {results.performance_metrics.memory_usage_peak}MB")

# Generate report
scanner.generate_report(results, format="html")
```

### Method 4: Docker (For deployment)

```bash
# Build image
docker build -t performance-scanner .

# Run scan in container
docker run -v $(pwd)/reports:/reports performance-scanner \
    scan-url https://myapp.com --output-dir /reports
```

---

## 📊 Understanding the Results

### Performance Metrics Explained

| Metric | What It Means | Good Value |
|--------|--------------|-----------|
| **Load Time** | Time for page to fully load | < 3 seconds |
| **Memory Peak** | Max memory used during load | < 100MB |
| **Scripting Time** | JavaScript execution | < 500ms |
| **Rendering Time** | DOM updates | < 200ms |
| **Paint Time** | Visual updates | < 100ms |
| **First Contentful Paint** | When content appears | < 2s |
| **Largest Contentful Paint** | When main content loads | < 3s |

### Sample Report Output

```
📊 PERFORMANCE SCAN REPORT
═══════════════════════════════════════════════════════════

URL: https://example.bubbleapps.io/
Timestamp: 2026-02-02 14:32:15
Device: Desktop
Network: WiFi

┌─────────────────────────────────────────────────────────┐
│ PERFORMANCE METRICS                                     │
├──────────────────────────────┬─────────────┬────────────┤
│ Metric                       │ Value       │ Status     │
├──────────────────────────────┼─────────────┼────────────┤
│ Load Time                    │ 2.34s       │ ✅ Good    │
│ Memory Peak                  │ 85.2 MB     │ ✅ Good    │
│ First Contentful Paint       │ 1.45s       │ ✅ Good    │
│ Largest Contentful Paint     │ 2.12s       │ ✅ Good    │
│ Total Blocking Time          │ 120ms       │ ✅ Good    │
└──────────────────────────────┴─────────────┴────────────┘

┌─────────────────────────────────────────────────────────┐
│ PERFORMANCE TRACES BREAKDOWN                            │
├──────────────────────────────┬─────────────┬────────────┤
│ Phase                        │ Duration    │ Percentage │
├──────────────────────────────┼─────────────┼────────────┤
│ Scripting (JavaScript)       │ 450ms       │ 19%        │
│ Rendering (DOM Updates)      │ 120ms       │ 5%         │
│ Painting (Visual Updates)    │ 80ms        │ 3%         │
│ Other (Network, etc)         │ 1.69s       │ 73%        │
└──────────────────────────────┴─────────────┴────────────┘

🔍 KEY FINDINGS
───────────────
✅ Load performance is excellent
✅ Memory usage is within acceptable limits
⚠️  Consider optimizing JavaScript bundles
📝 Recommendation: Implement code splitting
```

---

## 🚀 Common Tasks

### Task 1: Compare Two Apps

```bash
# Scan App A
python -m lowcode_scanner scan-url https://app-a.com --output-dir ./reports/app-a

# Scan App B
python -m lowcode_scanner scan-url https://app-b.com --output-dir ./reports/app-b

# Compare results (check generated JSON)
python -c "
import json
a = json.load(open('./reports/app-a/scan_results.json'))
b = json.load(open('./reports/app-b/scan_results.json'))

print(f'App A Load Time: {a[\"load_time\"]}s')
print(f'App B Load Time: {b[\"load_time\"]}s')
print(f'Difference: {abs(a[\"load_time\"] - b[\"load_time\"])}s')
"
```

### Task 2: Monitor Performance Over Time

```bash
# Run daily scans
for day in {1..7}; do
    python -m lowcode_scanner scan-url https://myapp.com \
        --output-dir ./reports/day-$day
done

# Compare results
python verify_tests_3x.py  # Already includes multi-run analysis
```

### Task 3: Test Multiple Scenarios

```bash
# Test all scenarios
python -m lowcode_scanner scan-url https://myapp.com \
    --scenarios homepage_load upfront_scripting regular_use heavy_list_load \
    --formats html json

# Results include comprehensive matrix
```

### Task 4: Export Data for Analysis

```bash
# Get JSON for Excel/Python processing
python -m lowcode_scanner scan-url https://myapp.com \
    --formats json \
    --output-dir ./data

# Use in Excel, Python, etc.
```

---

## 📁 Where Results Go

```
📦 Current Directory
└── performance_reports/
    ├── scan_results.json      ← Raw data
    ├── scan_report.html       ← Visual report
    ├── scan_report.pdf        ← Printable report
    ├── screenshots/
    │   ├── homepage_load.png
    │   ├── upfront_scripting.png
    │   └── ...
    └── timeline/
        └── performance_trace.json
```

---

## 🐛 Troubleshooting

### "Browser not found"
```bash
# Install Playwright browsers
playwright install chromium
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "Port already in use" (running web interface)
```bash
# Use different port
python main.py --port 8001
```

### "Timeout during scan"
```bash
# Increase timeout
python -m lowcode_scanner scan-url https://myapp.com --timeout 30
```

---

## 🎯 Best Practices

### ✅ DO
- **Scan during off-peak hours** for consistent results
- **Run 3+ times** for average performance (already built in!)
- **Use same network** for consistent comparisons
- **Test both desktop and mobile** versions
- **Include all critical scenarios**
- **Set baseline metrics** and track over time

### ❌ DON'T
- Run immediately after deployment (give it 5 min to stabilize)
- Scan production during peak hours
- Compare results from different networks (WiFi vs 4G)
- Ignore warnings—they indicate optimization opportunities
- Use old browsers (keep updated for accurate metrics)

---

## 📈 Real-World Example Workflow

### Week 1: Establish Baseline
```bash
# Run baseline scan 3 times
for i in {1..3}; do
    python -m lowcode_scanner scan-url https://myapp.com \
        --output-dir ./baseline/run-$i
done

# Record average metrics
# Load Time: 2.34s
# Memory Peak: 85.2 MB
```

### Week 2-3: Optimization
```bash
# Make performance improvements
# ... (update your app)

# Test improvements
python -m lowcode_scanner scan-url https://myapp.com \
    --output-dir ./optimized/run-1
```

### Week 4: Comparison
```bash
# Compare with baseline
# Baseline: 2.34s load time
# Optimized: 1.89s load time
# Improvement: 19% faster!
```

### Ongoing: Continuous Monitoring
```bash
# Daily scans
(crontab -l; echo "0 2 * * * cd /path/to/scanner && python -m lowcode_scanner scan-url https://myapp.com --output-dir ./daily/\$(date +\%Y-\%m-\%d)") | crontab -
```

---

## 🔗 Integration Examples

### With CI/CD Pipeline (GitHub Actions)
```yaml
name: Performance Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: playwright install chromium
      - run: python -m lowcode_scanner scan-url https://myapp.com --formats html json
      - uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: performance_reports/
```

### With Slack Notifications
```python
import json
import subprocess
from slack_sdk import WebClient

# Run scan
subprocess.run(['python', '-m', 'lowcode_scanner', 'scan-url', 'https://myapp.com'])

# Read results
results = json.load(open('performance_reports/scan_results.json'))

# Send to Slack
client = WebClient(token="YOUR_SLACK_TOKEN")
client.chat_postMessage(
    channel="#performance",
    text=f"📊 Scan Complete\nLoad Time: {results['load_time']}s\nMemory: {results['memory_peak']}MB"
)
```

---

## 📚 Additional Resources

- **QUICK_START.md** - Technology overview
- **PROFESSIONAL_ENHANCEMENTS_COMPLETE.md** - Feature details
- **FILE_STRUCTURE_REFERENCE.md** - Component reference
- **README.md** - Project overview

---

## 💡 Tips & Tricks

### Fastest Results
```bash
# Quick scan (homepage only)
python -m lowcode_scanner scan-url https://myapp.com \
    --scenarios homepage_load \
    --output-dir ./quick-scan
```

### Most Comprehensive
```bash
# Full analysis
python -m lowcode_scanner scan-url https://myapp.com \
    --scenarios homepage_load upfront_scripting regular_use heavy_list_load \
    --device desktop mobile \
    --network wifi 4g \
    --formats html json pdf
```

### Automated Batch Testing
```bash
# Create urls.txt with:
# https://app1.com
# https://app2.com
# https://app3.com

python -m lowcode_scanner scan-multiple --file urls.txt --formats html json
```

---

**Need help?** Check the documentation files or run: `python -m lowcode_scanner --help`
