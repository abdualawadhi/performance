# Low-Code Performance Scanner - Architecture Documentation

This document describes the system architecture, component interactions, and design decisions of the Low-Code Performance Scanner.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Security Considerations](#security-considerations)
- [Scalability](#scalability)
- [Deployment Architecture](#deployment-architecture)

---

## System Overview

The Low-Code Performance Scanner is a distributed system designed for comprehensive performance testing of low-code web applications. It consists of three main layers:

1. **Presentation Layer**: Web UI and CLI interfaces
2. **Application Layer**: API server and core scanner engine
3. **Infrastructure Layer**: Browser automation and data storage

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │   Next.js    │  │    CLI       │  │   Python     │                       │
│  │   Frontend   │  │   (Rich)     │  │    SDK       │                       │
│  │  (Port 3000) │  │              │  │              │                       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                       │
│         │                 │                 │                               │
│         └─────────────────┼─────────────────┘                               │
│                           │                                                 │
└───────────────────────────┼─────────────────────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────┼─────────────────────────────────────────────────┐
│                           ▼                                                 │
│                      APPLICATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend (Port 8000)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  REST API    │  │  WebSocket   │  │    Scan      │              │   │
│  │  │  Endpoints   │  │    Server    │  │   Manager    │              │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  │         └─────────────────┼─────────────────┘                      │   │
│  │                           │                                        │   │
│  └───────────────────────────┼────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  LowCodePerformanceScanner                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Platform    │  │ Performance  │  │   Scenario   │              │   │
│  │  │  Detector    │  │ Orchestrator │  │    Runner    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────────────┐
│                           ▼                                                 │
│                      INFRASTRUCTURE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                Browser Automation (Playwright)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Automation  │  │   Memory     │  │   Network    │              │   │
│  │  │   Engine     │  │   Monitor    │  │   Monitor    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐                                │   │
│  │  │ Performance  │  │ Screenshot   │                                │   │
│  │  │    Tracer    │  │   Handler    │                                │   │
│  │  └──────────────┘  └──────────────┘                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Chrome DevTools Protocol                         │   │
│  │                    (Performance Metrics Collection)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────────────┐
│                           ▼                                                 │
│                         STORAGE LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │   Report     │  │    Scan      │  │   Session    │                      │
│  │    Files     │  │    Data      │  │    Store     │                      │
│  │ (HTML/PDF/   │  │   (JSON)     │  │   (Redis)    │                      │
│  │  Excel/CSV)  │  │              │  │              │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Frontend (Next.js)

**Purpose**: User interface for scan configuration and results visualization

**Key Features**:
- Real-time progress via WebSocket
- Interactive results dashboard
- Historical scan comparison
- Report download interface

**Technology Stack**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Recharts (visualizations)

**Architecture**:
```
app/
├── page.tsx              # Main dashboard
├── layout.tsx            # Root layout with navigation
├── store.ts              # Zustand store for state management
├── globals.css           # Tailwind configuration
└── api/                  # API route handlers (optional)
```

### 2. Backend (FastAPI)

**Purpose**: REST API and WebSocket server for scan orchestration

**Key Features**:
- Async request handling
- Real-time WebSocket updates
- Background task processing
- Report file serving

**Technology Stack**:
- FastAPI
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Python asyncio

**Architecture**:
```
backend/main.py
├── FastAPI App
│   ├── REST Endpoints
│   │   ├── POST /api/scans
│   │   ├── GET /api/scans
│   │   ├── GET /api/scans/{id}
│   │   └── DELETE /api/scans/{id}
│   └── WebSocket
│       └── /api/scans/{id}/ws
└── ScanManager
    ├── Scan state management
    ├── WebSocket broadcasting
    └── Background task coordination
```

### 3. Core Scanner Engine

**Purpose**: Main scanning logic and orchestration

**Key Components**:

#### PlatformDetector
- Identifies low-code platforms via DOM analysis
- Pattern matching for Bubble, OutSystems, Airtable
- Platform-specific metric collection

#### PerformanceOrchestrator
- Manages scan execution workflow
- Coordinates multiple scenario runs
- Aggregates results with statistical analysis
- Handles concurrent scan limits

#### ScenarioRunner
- Executes individual test scenarios
- Manages browser lifecycle
- Collects metrics per scenario
- Handles retry logic

#### ScannerConfig
- Configuration validation
- Scenario/device/network selection
- Report format specification
- Timeout and threshold settings

### 4. Browser Automation Layer

**Purpose**: Browser control and metric collection

**Key Components**:

#### BrowserAutomation (automation.py)
- Playwright browser management
- Page lifecycle control
- Device and network emulation
- Screenshot and video recording

#### MemoryMonitor (memory_monitor.py)
- JavaScript heap monitoring
- DOM node counting
- Event listener tracking
- Garbage collection detection

#### NetworkMonitor (network_monitor.py)
- Request/response interception
- Resource classification
- Transfer size calculation
- Third-party detection

#### PerformanceTracer (performance_tracer.py)
- Chrome DevTools Protocol integration
- Performance timeline recording
- Core Web Vitals extraction
- Long task detection

#### ScreenshotHandler (screenshot_handler.py)
- Timeline screenshot capture
- Video recording
- Image optimization
- File management

### 5. Reporting Engine

**Purpose**: Multi-format report generation

**Key Components**:

#### ComprehensiveReportGenerator
- HTML interactive reports
- PDF executive summaries
- Excel data exports
- JSON machine-readable output
- CSV for analysis
- Markdown documentation

#### VisualizationEngine
- Chart generation
- Waterfall diagrams
- Performance gauges
- Comparison visualizations

### 6. Platform Analyzers

**Purpose**: Platform-specific analysis and recommendations

**Structure**:
```
platforms/
├── base.py               # Base analyzer class
├── registry.py           # Analyzer registration
└── implementations/
    ├── bubble.py         # Bubble.io specific
    ├── outsystems.py     # OutSystems specific
    └── airtable.py       # Airtable specific
```

---

## Data Flow

### Scan Execution Flow

```
1. Client Request
   │
   ▼
2. API Validation (Pydantic models)
   │
   ▼
3. Scan Job Creation (ScanManager)
   │
   ▼
4. Background Task Launch
   │
   ▼
5. Platform Detection
   │
   ▼
6. For each scenario:
   │  ├── Browser Launch
   │  ├── Device/Network Setup
   │  ├── Page Navigation
   │  ├── Metric Collection
   │  └── Browser Close
   │
   ▼
7. Result Aggregation
   │
   ▼
8. Report Generation
   │
   ▼
9. Client Notification (WebSocket)
```

### Data Model

```
ScanResult
├── metadata
│   ├── scan_id
│   ├── url
│   ├── platform
│   ├── timestamp
│   └── duration
├── performance_matrix
│   ├── overall_score
│   └── rows[]
│       ├── scenario
│       ├── device
│       ├── network
│       ├── runs[]
│       └── aggregates
├── core_web_vitals
│   ├── lcp, fid, cls
│   ├── fcp, ttfb, tbt
│   └── scores
├── memory_profile
│   ├── heap_size
│   ├── dom_nodes
│   └── peak_usage
├── network_metrics
│   ├── request_count
│   ├── transfer_size
│   └── timing
└── recommendations[]
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.8+ | Backend logic |
| Framework | FastAPI | API server |
| Browser | Playwright | Automation |
| Frontend | Next.js 14 | Web UI |
| Styling | Tailwind CSS | UI styling |
| State | Zustand | Frontend state |
| Charts | Recharts | Visualizations |

### Key Dependencies

```
# Core
pydantic>=2.0.0          # Data validation
playwright>=1.40.0       # Browser automation
asyncio-throttle>=1.0.2  # Rate limiting

# Data Processing
pandas>=2.0.0            # Data analysis
numpy>=1.24.0            # Numerical computing

# Reports
jinja2>=3.1.0            # HTML templating
openpyxl>=3.1.0          # Excel generation
reportlab>=4.0.0         # PDF generation
plotly>=5.17.0           # Interactive charts
matplotlib>=3.7.0        # Static charts

# CLI/UI
click>=8.1.0             # CLI framework
rich>=13.0.0             # Terminal UI
typer>=0.9.0             # Modern CLI

# Logging
structlog>=23.0.0        # Structured logging
```

---

## Design Patterns

### 1. Strategy Pattern

Used for platform analyzers and scenario types:

```python
class PlatformAnalyzer(ABC):
    @abstractmethod
    def detect(self, page) -> bool:
        pass
    
    @abstractmethod
    def analyze(self, metrics) -> AnalysisResult:
        pass

class BubbleAnalyzer(PlatformAnalyzer):
    def detect(self, page) -> bool:
        return "bubble" in page.content()
```

### 2. Observer Pattern

Used for scan progress updates:

```python
class ScanManager:
    def __init__(self):
        self._observers: List[Callable] = []
    
    def subscribe(self, callback: Callable):
        self._observers.append(callback)
    
    def notify(self, event: ScanEvent):
        for observer in self._observers:
            observer(event)
```

### 3. Factory Pattern

Used for creating browser instances:

```python
class BrowserFactory:
    @staticmethod
    def create(device_type: DeviceType):
        if device_type == DeviceType.MOBILE:
            return MobileBrowser()
        return DesktopBrowser()
```

### 4. Builder Pattern

Used for report generation:

```python
class ReportBuilder:
    def __init__(self):
        self.report = Report()
    
    def add_summary(self, data):
        self.report.summary = Summary(data)
        return self
    
    def add_charts(self, data):
        self.report.charts = Charts(data)
        return self
    
    def build(self) -> Report:
        return self.report
```

---

## Security Considerations

### 1. Input Validation

- All inputs validated with Pydantic models
- URL validation with HttpUrl type
- Enum validation for constrained values

### 2. Sandboxing

- Browser runs in isolated process
- No persistent browser storage
- Clean browser profile per scan

### 3. Resource Limits

- Concurrent scan limits
- Timeout enforcement
- Memory usage monitoring

### 4. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Future Enhancements

- API key authentication
- Rate limiting
- Request signing
- Audit logging

---

## Scalability

### Horizontal Scaling

The scanner can be scaled horizontally by:

1. **Multiple Worker Instances**
   - Run multiple backend instances
   - Load balancer distribution
   - Shared Redis for state

2. **Queue-Based Architecture**
   - Celery for task queuing
   - Redis as message broker
   - Worker pool for parallel processing

### Vertical Scaling

1. **Resource Optimization**
   - Browser pooling
   - Connection reuse
   - Memory-efficient data structures

2. **Caching**
   - Platform detection caching
   - Report template caching
   - Static asset caching

### Current Limitations

- Single-node deployment
- In-memory scan storage
- No distributed locking

### Future Architecture

```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌──▼────┐
│API-1  │  │ API-2 │
└───┬───┘  └──┬────┘
    │         │
    └────┬────┘
         │
    ┌────┴────┐
    │  Redis  │
    │ (Queue) │
    └────┬────┘
         │
    ┌────┴────┐
    │ Celery  │
    │ Workers │
    └─────────┘
```

---

## Deployment Architecture

### Local Development

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │◄───►│   Backend   │
│  :3000      │     │   :8000     │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Browser   │
                    │  (Chromium) │
                    └─────────────┘
```

### Docker Compose (Production)

```
┌─────────────────────────────────────────┐
│              Nginx (80/443)             │
│         (Reverse Proxy + SSL)           │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌────────▼───────┐
│    Frontend    │     │    Backend     │
│     :3000      │     │     :8000      │
└────────────────┘     └────────┬───────┘
                                │
                       ┌────────┴───────┐
                       │     Redis      │
                       │     :6379      │
                       └────────────────┘
```

### Kubernetes (Future)

```
┌─────────────────────────────────────────┐
│              Ingress Controller         │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌────────▼───────┐
│  Frontend Pod  │     │  Backend Pod   │
│  (ReplicaSet)  │     │  (ReplicaSet)  │
└────────────────┘     └────────┬───────┘
                                │
                       ┌────────┴───────┐
                       │  Redis Cluster │
                       └────────────────┘
```

---

## Monitoring and Observability

### Logging

- Structured logging with structlog
- Different log levels per environment
- Correlation IDs for request tracing

### Metrics

Future implementation:
- Prometheus metrics endpoint
- Custom business metrics
- Performance counters

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": __version__,
        "checks": {
            "browser": browser_pool.status(),
            "disk": disk_usage(),
            "memory": memory_usage()
        }
    }
```

---

## Conclusion

This architecture provides:
- **Modularity**: Clear component separation
- **Extensibility**: Easy to add new platforms and scenarios
- **Testability**: Component isolation enables unit testing
- **Maintainability**: Well-defined interfaces and patterns
- **Scalability**: Foundation for horizontal scaling

For questions or suggestions, please refer to the [Contributing Guidelines](../CONTRIBUTING.md).
