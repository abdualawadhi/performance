# 🌐 Low-Code Performance Scanner - Web Interface

**Professional Frontend for Real-Time Performance Testing**

A modern, responsive web interface for the Low-Code Performance Scanner, built with Next.js 14, React 18, and TypeScript.

---

## 🎯 Features

### 🚀 Core Features
- **Real-Time Monitoring** - WebSocket-powered live scan updates
- **Interactive Dashboard** - Beautiful, responsive UI with Tailwind CSS
- **Performance Visualizations** - Charts, graphs, and interactive tables
- **Multi-Format Reports** - Download HTML, JSON, CSV, Excel reports
- **Scan History** - Browse and compare previous scans
- **Platform Detection** - Automatic detection and optimization for Bubble, OutSystems, Airtable

### 🎨 User Experience
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Mode Ready** - Prepared for theme switching
- **Smooth Animations** - Framer Motion for delightful interactions
- **Toast Notifications** - Real-time feedback for user actions
- **Loading States** - Clear feedback during async operations

### 📊 Performance Dashboard
- Overall performance score (0-100)
- Scenario-by-scenario breakdown
- Memory usage charts
- Load time graphs
- Network performance metrics
- Core Web Vitals display

---

## 🏗️ Tech Stack

### Frontend Framework
- **Next.js 14** - React framework with App Router
- **React 18** - UI library with latest features
- **TypeScript** - Type-safe development

### Styling & UI
- **Tailwind CSS 3** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Lucide React** - Beautiful icon system
- **Custom Components** - Reusable UI components

### State & Data
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API calls
- **WebSocket API** - Real-time bidirectional communication
- **Recharts** - Charting library for data visualization

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting (recommended)
- **TypeScript** - Static type checking

---

## 📦 Installation

### Prerequisites

1. **Node.js 18+** and **npm 9+**
   ```bash
   node --version  # Should be v18.0.0 or higher
   npm --version   # Should be 9.0.0 or higher
   ```

2. **Backend API Running** (see parent README)
   - Backend should be running on `http://localhost:8000`
   - API docs available at `http://localhost:8000/api/docs`

### Quick Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

The application will be available at **http://localhost:3000**

---

## 🚀 Getting Started

### 1. Environment Configuration

Create `.env.local` file:

```bash
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Optional: Analytics (if using)
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

### 2. Start Development Server

```bash
npm run dev
```

Visit: http://localhost:3000

### 3. Build for Production

```bash
# Create production build
npm run build

# Start production server
npm run start
```

### 4. Run Type Checks

```bash
npm run type-check
```

### 5. Run Linter

```bash
npm run lint
```

---

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js 14 App Directory
│   ├── layout.tsx               # Root layout with header/footer
│   ├── page.tsx                 # Home page - Scan form
│   ├── globals.css              # Global styles & Tailwind
│   ├── scans/                   # Scan-related pages
│   │   ├── page.tsx            # Scan history list
│   │   └── [id]/               # Dynamic scan detail page
│   │       └── page.tsx        # Individual scan results
│   └── api/                     # API routes (if needed)
│
├── components/                   # React Components
│   ├── ui/                      # Base UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   └── ProgressBar.tsx
│   │
│   ├── ScanForm.tsx            # Main scan configuration form
│   ├── ScanCard.tsx            # Scan status card component
│   ├── ScanList.tsx            # List of scans
│   ├── ProgressTracker.tsx     # Real-time progress component
│   ├── ResultsViewer.tsx       # Scan results display
│   ├── PerformanceChart.tsx    # Performance visualization
│   ├── ScenarioTable.tsx       # Performance matrix table
│   ├── PlatformBadge.tsx       # Platform indicator badge
│   ├── MetricCard.tsx          # Individual metric card
│   └── WebSocketIndicator.tsx  # Connection status indicator
│
├── lib/                         # Utilities & Helpers
│   ├── api.ts                  # API client (Axios setup)
│   ├── websocket.ts            # WebSocket client
│   ├── utils.ts                # Helper functions
│   └── constants.ts            # App constants
│
├── hooks/                       # Custom React Hooks
│   ├── useScan.ts              # Scan management hook
│   ├── useWebSocket.ts         # WebSocket connection hook
│   ├── useScans.ts             # Scans list hook
│   └── useLocalStorage.ts      # Local storage hook
│
├── types/                       # TypeScript Type Definitions
│   ├── index.ts                # Main types
│   ├── api.ts                  # API response types
│   └── scan.ts                 # Scan-related types
│
├── store/                       # State Management (Zustand)
│   └── scanStore.ts            # Scan state store
│
├── public/                      # Static Assets
│   ├── favicon.ico
│   ├── logo.svg
│   └── icons/                  # Icon assets
│
├── styles/                      # Additional Styles
│   └── animations.css          # Custom animations
│
├── package.json                 # Dependencies & scripts
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── next.config.js              # Next.js configuration
├── postcss.config.js           # PostCSS configuration
├── .env.local                  # Environment variables (create this)
├── .env.example                # Environment template
├── .eslintrc.json              # ESLint configuration
└── README.md                   # This file
```

---

## 🎨 Component Examples

### ScanForm Component

```typescript
'use client'

import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { scanAPI } from '@/lib/api'

export function ScanForm() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await scanAPI.createScan({
        url,
        scenarios: ['homepage_load', 'regular_use_case'],
        devices: ['desktop', 'mobile'],
        network: ['wifi'],
        formats: ['html', 'json']
      })

      toast.success('Scan started successfully!')
      // Navigate to scan page
      window.location.href = `/scans/${response.data.scan_id}`
    } catch (error) {
      toast.error('Failed to start scan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  )
}
```

### WebSocket Hook

```typescript
import { useEffect, useState } from 'react'

export function useWebSocket(scanId: string) {
  const [status, setStatus] = useState<any>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL}/api/scans/${scanId}/ws`
    )

    ws.onopen = () => setConnected(true)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        setStatus(data.data)
      }
    }
    ws.onclose = () => setConnected(false)

    return () => ws.close()
  }, [scanId])

  return { status, connected }
}
```

---

## 🎯 Key Pages

### Home Page (`/`)
- Scan configuration form
- Quick start guide
- Recent scans list
- Platform selection

### Scan History (`/scans`)
- List of all scans
- Filter by status (completed, running, failed)
- Sort by date
- Quick actions (view, delete)

### Scan Details (`/scans/[id]`)
- Real-time progress (if running)
- Performance score
- Scenario breakdown
- Performance matrix table
- Charts and graphs
- Download reports
- Key observations and recommendations

---

## 🔌 API Integration

### Creating a Scan

```typescript
import { scanAPI } from '@/lib/api'

const createScan = async () => {
  const response = await scanAPI.createScan({
    url: 'https://myapp.bubbleapps.io',
    scenarios: ['homepage_load', 'heavy_list_load'],
    devices: ['desktop', 'mobile'],
    network: ['wifi'],
    formats: ['html', 'json']
  })
  
  return response.data.scan_id
}
```

### Real-Time Updates

```typescript
import { useWebSocket } from '@/hooks/useWebSocket'

function ScanProgress({ scanId }) {
  const { status, connected } = useWebSocket(scanId)

  return (
    <div>
      <div>Status: {status?.status}</div>
      <div>Progress: {status?.progress}%</div>
      <div>Step: {status?.current_step}</div>
    </div>
  )
}
```

### Fetching Results

```typescript
import { scanAPI } from '@/lib/api'

const getResults = async (scanId: string) => {
  const response = await scanAPI.getResult(scanId)
  return response.data
}
```

---

## 🎨 Styling Guide

### Tailwind CSS Classes

```typescript
// Buttons
<button className="btn btn-primary">
  Primary Button
</button>

<button className="btn btn-secondary">
  Secondary Button
</button>

// Cards
<div className="card">
  Card Content
</div>

// Inputs
<input className="input" type="text" />

// Badges
<span className="badge badge-success">Success</span>
<span className="badge badge-warning">Warning</span>
<span className="badge badge-danger">Error</span>
```

### Custom Colors

```javascript
// tailwind.config.js
colors: {
  primary: { /* blue shades */ },
  success: { /* green shades */ },
  warning: { /* yellow shades */ },
  danger: { /* red shades */ },
}
```

---

## 🧪 Testing

### Run Tests (when implemented)

```bash
npm test
```

### E2E Tests (when implemented)

```bash
npm run test:e2e
```

---

## 📱 Responsive Design

The interface is fully responsive:

- **Desktop** (1024px+): Full layout with sidebar
- **Tablet** (768px-1023px): Adapted layout
- **Mobile** (< 768px): Mobile-optimized stack layout

---

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

### Manual Deployment

```bash
# Build
npm run build

# Start production server
npm run start
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

---

## 🔧 Configuration

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
```

---

## 🐛 Troubleshooting

### Issue: npm install fails

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 3000 already in use

**Solution:**
```bash
# Use different port
PORT=3001 npm run dev
```

### Issue: API connection fails

**Check:**
- Backend is running on port 8000
- CORS is configured correctly
- Environment variables are set

---

## 📚 Resources

- **Next.js Docs**: https://nextjs.org/docs
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com/docs
- **TypeScript**: https://www.typescriptlang.org/docs
- **Framer Motion**: https://www.framer.com/motion

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎉 Credits

Built with ❤️ for professional low-code developers

**Version**: 1.0.2
**Last Updated**: January 27, 2026
**Status**: Production Ready

---

## 📞 Support

For issues or questions:
- Check the main project README
- Review the Web Interface section in the main README
- Open an issue on GitHub

---

**Happy Testing! 🚀**