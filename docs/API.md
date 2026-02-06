# Low-Code Performance Scanner - API Documentation

Complete reference for the REST API and WebSocket endpoints.

## Base URL

```
Development: http://localhost:8000
Production: https://api.lowcode-scanner.com
```

## Authentication

Currently, the API is open for local development. For production, API key authentication is recommended.

```bash
# Add API key to headers
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/scans
```

## Content Types

All endpoints accept and return JSON unless otherwise specified.

```
Content-Type: application/json
```

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/api/scans` | Start a new scan |
| GET | `/api/scans` | List all scans |
| GET | `/api/scans/{scan_id}` | Get scan status/result |
| DELETE | `/api/scans/{scan_id}` | Cancel/delete scan |
| GET | `/api/scans/{scan_id}/download` | Download report |
| WS | `/api/scans/{scan_id}/ws` | WebSocket for live updates |

---

## Detailed Endpoints

### Health Check

Check if the API is running.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.2",
  "timestamp": "2026-01-27T10:30:00Z"
}
```

---

### Start New Scan

Initiate a performance scan for a URL.

```http
POST /api/scans
```

**Request Body:**
```json
{
  "url": "https://example.bubbleapps.io",
  "scenarios": ["homepage_load", "regular_use_case", "heavy_list_load", "upfront_scripting"],
  "devices": ["desktop", "mobile"],
  "network": ["wifi", "3g_slow"],
  "formats": ["html", "json", "pdf"],
  "session_name": "My App Scan"
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to scan |
| `scenarios` | array | No | `["homepage_load", "regular_use_case", "heavy_list_load", "upfront_scripting"]` | Test scenarios |
| `devices` | array | No | `["desktop", "mobile"]` | Device types |
| `network` | array | No | `["wifi"]` | Network conditions |
| `formats` | array | No | `["html", "json"]` | Report formats |
| `session_name` | string | No | null | Optional session name |

**Available Scenarios:**
- `homepage_load` - Initial page load performance
- `regular_use_case` - Standard user interaction simulation
- `heavy_list_load` - Performance under data-heavy conditions
- `upfront_scripting` - JavaScript execution during boot
- `database_heavy` - Database-intensive operations
- `api_intensive` - API-heavy interactions
- `complex_navigation` - Multi-step navigation flow
- `form_interaction` - Form submission performance
- `search_operation` - Search functionality performance
- `media_loading` - Image/video loading performance

**Available Devices:**
- `desktop` - Desktop browser (1920x1080)
- `mobile` - Mobile phone (375x667)
- `tablet` - Tablet device (768x1024)

**Available Network Conditions:**
- `wifi` - Fast WiFi (30 Mbps)
- `4g` - 4G LTE (8 Mbps)
- `3g_fast` - Fast 3G (1.6 Mbps)
- `3g_slow` - Slow 3G (0.4 Mbps)
- `2g` - 2G connection (0.25 Mbps)

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "url": "https://example.bubbleapps.io",
  "websocket_url": "/api/scans/550e8400-e29b-41d4-a716-446655440000/ws",
  "message": "Scan queued successfully"
}
```

**Status Codes:**
- `202 Accepted` - Scan queued successfully
- `400 Bad Request` - Invalid request body
- `422 Unprocessable Entity` - Invalid URL or parameters
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

### List All Scans

Get a list of all scans with their status.

```http
GET /api/scans
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (queued, running, completed, failed) |
| `limit` | integer | Maximum number of results (default: 50) |
| `offset` | integer | Pagination offset (default: 0) |

**Response:**
```json
{
  "scans": [
    {
      "scan_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "url": "https://example.bubbleapps.io",
      "platform": "bubble",
      "overall_score": 78.5,
      "scenarios_count": 4,
      "started_at": "2026-01-27T10:30:00Z",
      "completed_at": "2026-01-27T10:35:00Z",
      "progress": 100
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

### Get Scan Status

Get detailed status and results of a specific scan.

```http
GET /api/scans/{scan_id}
```

**Response (Running):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 45,
  "current_step": "Running scenario: heavy_list_load (Device: mobile, Network: wifi)",
  "url": "https://example.bubbleapps.io",
  "started_at": "2026-01-27T10:30:00Z",
  "logs": [
    "🚀 Starting performance scan",
    "🌐 Detected platform: bubble",
    "⚡ Running scenario: homepage_load"
  ]
}
```

**Response (Completed):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "url": "https://example.bubbleapps.io",
  "platform": "bubble",
  "overall_score": 78.5,
  "confidence": "certain",
  "scenarios_count": 4,
  "started_at": "2026-01-27T10:30:00Z",
  "completed_at": "2026-01-27T10:35:00Z",
  "progress": 100,
  "result": {
    "url": "https://example.bubbleapps.io",
    "platform": "bubble",
    "overall_score": 78.5,
    "performance_matrix": {
      "overall_score": 78.5,
      "rows": [
        {
          "scenario": "homepage_load",
          "device": "desktop",
          "network": "wifi",
          "avg_load_time": 2.3,
          "avg_score": 82.0,
          "memory_peak": 145.2,
          "confidence": "certain"
        }
      ]
    },
    "core_web_vitals": {
      "lcp": 2.5,
      "fid": 50,
      "cls": 0.1,
      "fcp": 1.2,
      "ttfb": 0.8,
      "tbt": 150
    },
    "reports": [
      {
        "format": "html",
        "path": "/reports/scan_550e8400/report.html",
        "url": "/api/scans/550e8400-e29b-41d4-a716-446655440000/download?format=html"
      }
    ]
  }
}
```

---

### Cancel/Delete Scan

Cancel a running scan or delete a completed one.

```http
DELETE /api/scans/{scan_id}
```

**Response:**
```json
{
  "message": "Scan deleted successfully",
  "scan_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Download Report

Download the generated report for a completed scan.

```http
GET /api/scans/{scan_id}/download?format={format}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | string | Yes | Report format (html, json, pdf, csv, excel, markdown) |

**Response:**
- Content-Type varies by format
- File download with appropriate filename

**Example:**
```bash
curl -O -J "http://localhost:8000/api/scans/550e8400-e29b-41d4-a716-446655440000/download?format=pdf"
```

---

## WebSocket API

Connect to receive real-time scan updates.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/scans/{scan_id}/ws');
```

### Message Format

**Client to Server:**
- No messages required from client

**Server to Client:**
```json
{
  "type": "progress",
  "data": {
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress": 45,
    "current_step": "Running scenario: heavy_list_load",
    "logs": [
      "🚀 Starting performance scan",
      "🌐 Detected platform: bubble"
    ]
  }
}
```

**Completion Message:**
```json
{
  "type": "progress",
  "data": {
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "current_step": "Scan completed",
    "result": {
      "overall_score": 78.5,
      "platform": "bubble"
    }
  }
}
```

### Example Usage

```javascript
const scanId = '550e8400-e29b-41d4-a716-446655440000';
const ws = new WebSocket(`ws://localhost:8000/api/scans/${scanId}/ws`);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Progress:', message.data.progress);
  console.log('Step:', message.data.current_step);
  
  if (message.data.status === 'completed') {
    console.log('Scan complete!', message.data.result);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "type": "validation_error"
}
```

**Common Error Types:**

| Status Code | Type | Description |
|-------------|------|-------------|
| 400 | `validation_error` | Invalid request parameters |
| 404 | `not_found` | Scan not found |
| 422 | `unprocessable_entity` | URL validation failed |
| 429 | `rate_limit` | Too many requests |
| 500 | `internal_error` | Server error |

---

## Rate Limiting

API requests are limited to prevent abuse:

- **Scan creation**: 10 requests per minute
- **Status checks**: 60 requests per minute
- **Downloads**: 30 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1706352000
```

---

## SDK Examples

### Python

```python
import requests
import websockets
import asyncio
import json

API_BASE = "http://localhost:8000"

# Start a scan
response = requests.post(f"{API_BASE}/api/scans", json={
    "url": "https://example.com",
    "scenarios": ["homepage_load"],
    "devices": ["desktop"]
})
scan_id = response.json()["scan_id"]

# Connect to WebSocket for updates
async def watch_scan(scan_id):
    uri = f"ws://localhost:8000/api/scans/{scan_id}/ws"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            print(f"Progress: {data['data']['progress']}%")
            if data['data']['status'] == 'completed':
                break

asyncio.run(watch_scan(scan_id))

# Download report
response = requests.get(f"{API_BASE}/api/scans/{scan_id}/download?format=pdf")
with open('report.pdf', 'wb') as f:
    f.write(response.content)
```

### JavaScript/TypeScript

```typescript
class LowCodeScannerClient {
  private baseUrl: string;
  
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async startScan(config: ScanConfig): Promise<ScanResponse> {
    const response = await fetch(`${this.baseUrl}/api/scans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return response.json();
  }
  
  watchScan(scanId: string, onProgress: (data: any) => void): WebSocket {
    const ws = new WebSocket(`ws://localhost:8000/api/scans/${scanId}/ws`);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onProgress(message.data);
    };
    return ws;
  }
  
  async downloadReport(scanId: string, format: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/scans/${scanId}/download?format=${format}`
    );
    return response.blob();
  }
}
```

---

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for API version history.

## Support

For API support:
- GitHub Issues: [github.com/your-org/lowcode-performance-scanner/issues](https://github.com/your-org/lowcode-performance-scanner/issues)
- Documentation: [docs.lowcode-scanner.com](https://docs.lowcode-scanner.com)
- Email: support@lowcode-scanner.com
