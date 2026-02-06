# Professional Components Guide

This guide provides documentation for the professional enterprise-grade components in the Low-Code Performance Scanner frontend.

---

## Table of Contents
1. [ProfessionalDashboard](#professionaldashboard)
2. [ExecutiveSummary](#executivesummary)
3. [MetricDisplay](#metricdisplay)
4. [SeverityBlockPro](#severityblockpro)
5. [ProgressBarPro](#progressbarpro)
6. [ProfessionalCharts](#professionalcharts)

---

## ProfessionalDashboard

**Purpose**: Main dashboard component for running and managing performance scans.

### Features
- Live scan progress tracking with WebSocket updates
- Real-time log streaming
- Quick scan form with scenario selection
- Scan history with quick download actions
- Professional severity-based result display

### Usage

```tsx
import ProfessionalDashboard from '@/components/ProfessionalDashboard'

export default function DashboardPage() {
  return <ProfessionalDashboard />
}
```

### Props
All props are managed internally through Zustand store.

### Store Integration
Requires the following store state:
- `scanUrl`: URL to scan
- `setScanUrl`: Function to set URL
- `startScan`: Function to initiate scan
- `isScanning`: Boolean indicating scan status
- `currentScan`: Current scan data
- `liveProgress`: Live progress updates
- `scanHistory`: Array of past scans
- `fetchScanHistory`: Function to load history

---

## ExecutiveSummary

**Purpose**: Display comprehensive executive summary of scan results.

### Features
- Overall score with severity-based styling
- Platform detection display
- Confidence level indicator
- Key findings with numbered list
- Business impact assessment
- Priority recommendations with priority cards

### Usage

```tsx
import { ExecutiveSummary } from '@/components/ExecutiveSummary'

<ExecutiveSummary
  overallScore={85.5}
  keyFindings={[
    'Fast initial load time',
    'Efficient resource usage',
    'Optimized rendering'
  ]}
  businessImpact="Good performance with minor optimizations possible"
  priorityRecommendations={[
    'Address immediately: Critical issues',
    'Prioritize: Important improvements'
  ]}
  platform="bubble"
  confidenceLevel="certain"
/>
```

### Props

| Prop | Type | Required | Default | Description |
|------|------|-----------|----------|-------------|
| `overallScore` | `number` | Yes | - | Overall performance score (0-100) |
| `keyFindings` | `string[]` | Yes | - | Array of key finding strings |
| `businessImpact` | `string` | Yes | - | Business impact assessment text |
| `priorityRecommendations` | `string[]` | Yes | - | Array of priority recommendation strings |
| `platform` | `string` | No | `'Generic'` | Detected platform name |
| `confidenceLevel` | `'certain' \| 'firm' \| 'tentative'` | No | `'certain'` | Confidence level of results |
| `className` | `string` | No | `''` | Additional CSS classes |

---

## MetricDisplay

**Purpose**: Display individual metrics with optional trend indicators.

### Features
- Icon support
- Trend indicators (up/down/neutral)
- Multiple size options (sm, md, lg)
- Color coding options
- Hover animations
- Optional description text

### Usage

```tsx
import { MetricDisplay } from '@/components/MetricDisplay'
import { Activity, TrendingUp } from 'lucide-react'

<MetricDisplay
  label="Average Load Time"
  value={2.5}
  unit="seconds"
  icon={Activity}
  trend="down"
  trendValue="-12%"
  color="success"
  size="lg"
  description="Loading time decreased from last scan"
/>
```

### Props

| Prop | Type | Required | Default | Description |
|------|------|-----------|----------|-------------|
| `label` | `string` | Yes | - | Metric label |
| `value` | `string \| number` | Yes | - | Metric value |
| `unit` | `string` | No | - | Unit of measurement |
| `icon` | `LucideIcon` | No | - | Icon component from lucide-react |
| `trend` | `'up' \| 'down' \| 'neutral'` | No | - | Trend direction |
| `trendValue` | `string` | No | - | Trend value text |
| `color` | `'primary' \| 'success' \| 'warning' \| 'danger' \| 'info'` | No | `'primary'` | Color theme |
| `size` | `'sm' \| 'md' \| 'lg'` | No | `'md'` | Component size |
| `description` | `string` | No | - | Additional description text |
| `className` | `string` | No | `''` | Additional CSS classes |

---

## SeverityBlockPro

**Purpose**: Display severity-coded information blocks with recommendations.

### Features
- Five severity levels: excellent, good, warning, accent, critical
- Color-coded borders and backgrounds
- Icons for each severity
- Optional metric display
- Recommendation text support
- Hover effects with lift animation
- Click handlers for interactivity

### Usage

```tsx
import { SeverityBlock } from '@/components/SeverityBlockPro'

<SeverityBlock
  severity="critical"
  title="High Memory Usage"
  description="Memory consumption exceeds recommended threshold"
  count={5}
  metric={150}
  metricLabel="MB"
  recommendation="Optimize memory by reducing unnecessary data retention"
  onClick={() => handleClick()}
/>
```

### Props

| Prop | Type | Required | Default | Description |
|------|------|-----------|----------|-------------|
| `severity` | `'excellent' \| 'good' \| 'warning' \| 'accent' \| 'critical'` | Yes | - | Severity level |
| `title` | `string` | Yes | - | Block title |
| `description` | `string` | Yes | - | Block description |
| `count` | `number` | No | - | Number of issues/items |
| `metric` | `string \| number` | No | - | Metric value to display |
| `metricLabel` | `string` | No | - | Label for metric |
| `recommendation` | `string` | No | - | Recommendation text |
| `className` | `string` | No | `''` | Additional CSS classes |
| `onClick` | `() => void` | No | - | Click handler |

### Severity Levels

| Level | Color | Icon | Use Case |
|-------|--------|-------|----------|
| `excellent` | Green | 🟢 | Score 90+, optimal performance |
| `good` | Blue | 🔵 | Score 80-89, good performance |
| `warning` | Yellow | 🟡 | Score 70-79, needs improvement |
| `accent` | Orange | 🟠 | Needs attention |
| `critical` | Red | 🔴 | Score <70, critical issues |

---

## ProgressBarPro

**Purpose**: Enhanced progress bar with multiple styles and status indicators.

### Features
- Color options (primary, success, warning, accent, error, info)
- Multiple sizes (sm, md, lg)
- Animated transitions
- Status icons (complete/error/loading)
- Percentage and value display
- Label support
- Smooth animations using Framer Motion

### Usage

```tsx
import { ProgressBar } from '@/components/ProgressBarPro'

<ProgressBar
  value={75}
  max={100}
  label="Scan Progress"
  color="primary"
  showPercentage={true}
  animated={true}
  status="loading"
/>

<ProgressBar
  value={100}
  max={100}
  label="Task Complete"
  color="success"
  status="complete"
/>
```

### Props

| Prop | Type | Required | Default | Description |
|------|------|-----------|----------|-------------|
| `value` | `number` | Yes | - | Current progress value |
| `max` | `number` | No | `100` | Maximum value |
| `label` | `string` | No | - | Label text |
| `color` | `'primary' \| 'success' \| 'warning' \| 'accent' \| 'error' \| 'info'` | No | `'primary'` | Color theme |
| `size` | `'sm' \| 'md' \| 'lg'` | No | `'md'` | Bar height |
| `showValue` | `boolean` | No | `true` | Show raw value |
| `showPercentage` | `boolean` | No | `true` | Show percentage |
| `animated` | `boolean` | No | `true` | Animate progress |
| `status` | `'idle' \| 'loading' \| 'complete' \| 'error'` | No | `'idle'` | Status indicator |
| `className` | `string` | No | `''` | Additional CSS classes |

---

## ProfessionalCharts

**Purpose**: Enterprise-grade data visualizations using Recharts.

### Available Charts

#### PerformanceTrendChart
Area chart showing performance trends over time.

```tsx
import { PerformanceTrendChart } from '@/components/ProfessionalCharts'

<PerformanceTrendChart
  data={[
    { name: 'Scenario 1', value: 85 },
    { name: 'Scenario 2', value: 92 },
  ]}
  title="Performance Trend"
  subtitle="Score by scenario"
  height={300}
/>
```

#### ScenarioComparisonChart
Grouped bar chart comparing multiple metrics.

```tsx
import { ScenarioComparisonChart } from '@/components/ProfessionalCharts'

<ScenarioComparisonChart
  data={[
    { name: 'Scenario 1', loadTime: 2.5, memory: 150, score: 85 },
    { name: 'Scenario 2', loadTime: 1.8, memory: 120, score: 92 },
  ]}
  title="Scenario Comparison"
  height={300}
/>
```

#### PerformanceRadarChart
Radar chart for multi-dimensional analysis.

```tsx
import { PerformanceRadarChart } from '@/components/ProfessionalCharts'

<PerformanceRadarChart
  data={[
    { subject: 'Load Time', value: 85, target: 90 },
    { subject: 'Memory', value: 92, target: 85 },
  ]}
  title="Performance Radar"
  height={300}
/>
```

#### DistributionPieChart
Donut-style distribution chart.

```tsx
import { DistributionPieChart } from '@/components/ProfessionalCharts'

<DistributionPieChart
  data={[
    { name: 'Excellent', value: 5, percentage: 25 },
    { name: 'Good', value: 10, percentage: 50 },
    { name: 'Needs Work', value: 5, percentage: 25 },
  ]}
  title="Severity Distribution"
  height={300}
/>
```

### Common Props

| Prop | Type | Required | Default | Description |
|------|------|-----------|----------|-------------|
| `data` | `any[]` | Yes | - | Chart data array |
| `title` | `string` | Yes | - | Chart title |
| `subtitle` | `string` | No | - | Chart subtitle |
| `height` | `number` | No | `300` | Chart height in px |
| `className` | `string` | No | `''` | Additional CSS classes |

---

## Color System

### Primary Colors
- **Primary Blue**: `#2563eb` - Main actions and branding
- **Success Green**: `#16a34a` - Positive states
- **Warning Amber**: `#f59e0b` - Warning states
- **Danger Red**: `#dc2626` - Critical states
- **Accent Orange**: `#ea580c` - Needs improvement
- **Info Indigo**: `#4f46e5` - Informational

### Neutral Colors
- **Slate Scale**: #f8fafc to #020617
- Professional, modern neutral system

---

## Utilities

### Animations
- `animate-fade-in`: Smooth fade in
- `animate-fade-in-up`: Fade in with upward movement
- `animate-fade-in-down`: Fade in with downward movement
- `animate-shimmer`: Loading shimmer effect

### Shadows
- `shadow-soft`: Subtle shadow for depth
- `shadow-elevated`: Prominent shadow for elevation
- `shadow-card`: Standard card shadow
- `shadow-hover`: Enhanced hover shadow
- `shadow-glow`: Colored glow effect

### Responsive
All components are fully responsive:
- Mobile: Stacked layouts
- Tablet: 2-column grids
- Desktop: Full-width layouts

---

## Best Practices

1. **Use Semantic HTML**: Maintain proper HTML structure
2. **Accessibility First**: Include ARIA labels and keyboard navigation
3. **Consistent Styling**: Use Tailwind utility classes
4. **Performance**: Lazy load components when possible
5. **Error Handling**: Always provide error states
6. **Loading States**: Show loading indicators for async operations
7. **Validation**: Validate user inputs before submission

---

## Examples

### Complete Dashboard Example

```tsx
import ProfessionalDashboard from '@/components/ProfessionalDashboard'

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <ProfessionalDashboard />
    </div>
  )
}
```

### Executive Summary in Report

```tsx
import { ExecutiveSummary } from '@/components/ExecutiveSummary'

function ReportSummary({ scanResult }) {
  return (
    <ExecutiveSummary
      overallScore={scanResult.overallScore}
      keyFindings={scanResult.keyFindings}
      businessImpact={scanResult.businessImpact}
      priorityRecommendations={scanResult.recommendations}
      platform={scanResult.platform}
      confidenceLevel="certain"
    />
  )
}
```

### Metrics Grid

```tsx
import { MetricDisplay } from '@/components/MetricDisplay'
import { Activity, Clock, Database } from 'lucide-react'

function MetricsPanel() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <MetricDisplay
        label="Average Load Time"
        value={2.5}
        unit="s"
        icon={Activity}
        color="primary"
        trend="down"
        trendValue="-12%"
      />
      <MetricDisplay
        label="Memory Usage"
        value={150}
        unit="MB"
        icon={Database}
        color="success"
        trend="down"
        trendValue="-8%"
      />
      <MetricDisplay
        label="Response Time"
        value={180}
        unit="ms"
        icon={Clock}
        color="info"
        trend="neutral"
      />
    </div>
  )
}
```

---

## Support

For questions or issues:
1. Check this documentation
2. Review component source code
3. Refer to Tailwind CSS documentation
4. Check Recharts documentation for chart customization

---

## Changelog

### v1.0.0 (Current)
- Initial release of professional components
- Full TypeScript support
- Accessibility features
- Responsive design
- Enterprise-grade styling
