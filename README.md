# 🚀 Low-Code Performance Scanner

[![CI/CD](https://github.com/your-org/lowcode-performance-scanner/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-org/lowcode-performance-scanner/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/codecov/c/github/your-org/lowcode-performance-scanner)](https://codecov.io/gh/your-org/lowcode-performance-scanner)

**Professional Performance Testing for Low-Code Web Applications**

A comprehensive, enterprise-grade performance testing solution specifically designed for low-code platforms including **Bubble.io**, **OutSystems**, and **Airtable**. This scanner provides detailed performance analysis with comprehensive reporting, memory profiling, and actionable recommendations.

[📖 Documentation](docs/USER_GUIDE.md) • [🚀 Quick Start](#quick-start) • [📊 Examples](#examples) • [🔧 API Reference](docs/API.md)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Capabilities

- **🏗️ Low-Code Platform Optimization**: Specialized testing for Bubble, OutSystems, Airtable with platform-specific metrics
- **📊 Comprehensive Performance Matrix**: Multi-dimensional testing across scenarios, devices, and network conditions
- **🧠 Memory Profiling**: Peak usage tracking, leak detection, and garbage collection monitoring
- **📈 Performance Traces**: Detailed scripting, rendering, and paint analysis breakdown
- **🌐 Core Web Vitals**: Full LCP, FID, CLS, FCP, TTFB, and TBT measurement
- **🎭 Multi-Scenario Testing**: 10 comprehensive test scenarios covering real-world use cases

### 📱 Testing Coverage

| Dimension | Options |
|-----------|---------|
| **Devices** | Desktop (1920x1080), Mobile (375x667), Tablet (768x1024) |
| **Networks** | WiFi, 4G, 3G Fast, 3G Slow, 2G |
| **Scenarios** | Homepage Load, Regular Use, Heavy List, Upfront Scripting, Database Heavy, API Intensive, Complex Navigation, Form Interaction, Search Operation, Media Loading |
| **Platforms** | Bubble.io, OutSystems, Airtable, Generic Web |

### 📑 Report Formats

- **HTML**: Interactive dashboards with charts and visualizations
- **PDF**: Executive summaries for stakeholders
- **Excel**: Detailed data analysis with multiple worksheets
- **JSON**: Machine-readable for CI/CD integration
- **CSV**: Import into spreadsheet tools
- **Markdown**: Documentation-friendly reports

### 💻 Interfaces

- **CLI**: Rich terminal interface with progress bars and tables
- **Web UI**: Modern Next.js dashboard with real-time updates
- **REST API**: Full-featured API with WebSocket support
- **Python SDK**: Programmatic access for custom integrations

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Start all services
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Using pip

```bash
# Install package
pip install lowcode-performance-scanner

# Install Playwright browsers
playwright install chromium

# Run your first scan
lowcode-scanner scan-url https://myapp.bubbleapps.io
```

### Using Python

```python
import asyncio
from lowcode_scanner import LowCodePerformanceScanner, ScannerConfig

async def main():
    config = ScannerConfig(
        scenarios=["homepage_load", "regular_use_case"],
        devices=["desktop", "mobile"],
        network_conditions=["wifi", "3g_slow"]
    )
    
    scanner = LowCodePerformanceScanner(config)
    result = await scanner.scan_url("https://myapp.bubbleapps.io")
    
    print(f"Overall Score: {result.performance_matrix.overall_score}/100")
    print(f"Platform: {result.platform}")

asyncio.run(main())
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for web UI)
- 4GB RAM minimum (8GB recommended)
- Chrome/Chromium browser

### Detailed Installation

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

#### 3. Set Up Frontend

```bash
cd frontend
npm install
```

#### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

#### 5. Start Services

```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Start frontend
cd frontend && npm run dev
```

Visit `http://localhost:3000` to access the dashboard.

---

## 📖 Usage

### CLI Usage

```bash
# Basic scan
lowcode-scanner scan-url https://example.com

# Comprehensive scan with all options
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --scenarios homepage_load regular_use_case heavy_list_load upfront_scripting \
  --devices desktop mobile \
  --network wifi 4g 3g_slow \
  --formats html pdf excel json \
  --output-dir ./reports \
  --executive --academic \
  --export excel

# List available scenarios
lowcode-scanner list-scenarios

# Scan multiple URLs
lowcode-scanner scan-multiple --file urls.txt --output-dir ./batch-reports
```

### Web Interface

1. Open `http://localhost:3000`
2. Enter the URL to scan
3. Select scenarios, devices, and network conditions
4. Click "Start Scan"
5. Watch real-time progress
6. View and download results

### API Usage

```bash
# Start a scan
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://myapp.bubbleapps.io",
    "scenarios": ["homepage_load", "regular_use_case"],
    "devices": ["desktop", "mobile"],
    "formats": ["html", "json"]
  }'

# Check status
curl http://localhost:8000/api/scans/{scan_id}

# Download report
curl -O -J "http://localhost:8000/api/scans/{scan_id}/download?format=pdf"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Next.js    │  │    CLI       │  │   Python     │      │
│  │   Frontend   │  │   (Rich)     │  │    SDK       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────┼─────────────────────────────────┐
│                           ▼                                 │
│                   APPLICATION LAYER                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                        │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │  REST API    │  │  WebSocket   │                │   │
│  │  └──────┬───────┘  └──────┬───────┘                │   │
│  │         └─────────────────┼────────────────────────┘   │
│  │                           │                            │
│  │              LowCodePerformanceScanner                 │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  │ Platform │ │Scenario  │ │Performance│ │ Report  │  │
│  │  │ Detector │ │ Runner   │ │Orchestrator│ │ Engine │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                           ▼                                 │
│                   INFRASTRUCTURE LAYER                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Playwright Browser Automation            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │   │
│  │  │ Memory   │ │ Network  │ │Performance│ │Screenshot│ │
│  │  │ Monitor  │ │ Monitor  │ │  Tracer   │ │ Handler │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 📊 Examples

### Example 1: Quick Health Check

```bash
# Simple scan to check overall health
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --scenarios homepage_load \
  --devices desktop \
  --formats json
```

### Example 2: Mobile Performance Analysis

```bash
# Focus on mobile performance with slow network
lowcode-scanner scan-url https://myapp.bubbleapps.io \
  --scenarios homepage_load heavy_list_load \
  --devices mobile \
  --network 3g_slow \
  --formats html pdf \
  --output-dir ./mobile-analysis
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/performance.yml
name: Performance Test

on: [push]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Performance Scan
        run: |
          pip install lowcode-performance-scanner
          playwright install chromium
          lowcode-scanner scan-url https://staging.myapp.com \
            --formats json \
            --output-dir ./results
      
      - name: Check Performance Score
        run: |
          SCORE=$(cat ./results/*.json | jq '.performance_matrix.overall_score')
          if [ $SCORE -lt 70 ]; then
            echo "Performance score $SCORE is below threshold"
            exit 1
          fi
```

### Example 4: Batch Testing

```python
import asyncio
from lowcode_scanner import LowCodePerformanceScanner, ScannerConfig

urls = [
    "https://app1.bubbleapps.io",
    "https://app2.bubbleapps.io",
    "https://app3.bubbleapps.io"
]

async def scan_all():
    config = ScannerConfig(
        scenarios=["homepage_load"],
        devices=["desktop"]
    )
    scanner = LowCodePerformanceScanner(config)
    
    results = []
    for url in urls:
        result = await scanner.scan_url(url)
        results.append({
            "url": url,
            "score": result.performance_matrix.overall_score
        })
    
    # Sort by performance score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print("Performance Ranking:")
    for r in results:
        print(f"  {r['score']:>3}/100 - {r['url']}")

asyncio.run(scan_all())
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Complete usage guide |
| [API Reference](docs/API.md) | REST API and WebSocket documentation |
| [Architecture](docs/ARCHITECTURE.md) | System design and components |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment guide |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |
| [Changelog](docs/CHANGELOG.md) | Version history |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
playwright install chromium

# Run tests
pytest

# Format code
black .
isort .

# Submit pull request
git checkout -b feature/my-feature
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

---

## 🗺️ Roadmap

### v1.1.0 (In Progress)
- [ ] Mendix platform support
- [ ] Microsoft PowerApps support
- [ ] Historical trend analysis
- [ ] CI/CD integration helpers

### v1.2.0 (Planned)
- [ ] Salesforce Lightning support
- [ ] GraphQL API monitoring
- [ ] Database query profiling
- [ ] Slack/Email notifications

### v2.0.0 (Future)
- [ ] Machine learning performance predictions
- [ ] Automated optimization recommendations
- [ ] Multi-region testing
- [ ] Load testing integration

See [CHANGELOG.md](docs/CHANGELOG.md) for completed features.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Rich](https://github.com/Textualize/rich) for beautiful CLI output

---

## 📞 Support

- **GitHub Issues**: [github.com/your-org/lowcode-performance-scanner/issues](https://github.com/your-org/lowcode-performance-scanner/issues)
- **Documentation**: [docs.lowcode-scanner.com](https://docs.lowcode-scanner.com)
- **Email**: support@lowcode-scanner.com

---

**Built with ❤️ for the low-code development community.**

[⬆ Back to Top](#-low-code-performance-scanner)
