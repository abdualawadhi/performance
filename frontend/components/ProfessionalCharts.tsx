'use client'

import { motion } from 'framer-motion'
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts'

interface ChartProps {
  data: any[]
  title: string
  subtitle?: string
  height?: number
  className?: string
}

export function PerformanceTrendChart({ data, title, subtitle, height = 300, className = '' }: ChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-bold text-grey-900">{title}</h3>
        {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '12px' }} />
          <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#f1f5f9' }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#2563eb"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorScore)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function ScenarioComparisonChart({ data, title, subtitle, height = 300, className = '' }: ChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-bold text-grey-900">{title}</h3>
        {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '12px' }} />
          <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#f1f5f9' }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Bar dataKey="loadTime" fill="#2563eb" radius={[8, 8, 0, 0]} />
          <Bar dataKey="memory" fill="#16a34a" radius={[8, 8, 0, 0]} />
          <Bar dataKey="score" fill="#f59e0b" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function PerformanceRadarChart({ data, title, subtitle, height = 300, className = '' }: ChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-bold text-grey-900">{title}</h3>
        {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={data} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
          <PolarGrid stroke="#cbd5e1" />
          <PolarAngleAxis dataKey="subject" stroke="#64748b" style={{ fontSize: '12px' }} />
          <PolarRadiusAxis stroke="#cbd5e1" style={{ fontSize: '12px' }} />
          <Radar name="Current" dataKey="value" stroke="#2563eb" fill="#2563eb" fillOpacity={0.5} />
          <Radar name="Target" dataKey="target" stroke="#16a34a" fill="#16a34a" fillOpacity={0.3} />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#f1f5f9' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function DistributionPieChart({ data, title, subtitle, height = 250, className = '' }: ChartProps) {
  const colors = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#64748b', '#9333ea'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-bold text-grey-900">{title}</h3>
        {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4 items-center">
        <ResponsiveContainer width="100%" height={height}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#f1f5f9' }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="space-y-3">
          {data.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: colors[idx % colors.length] }}
                />
                <span className="text-sm text-grey-700">{item.name}</span>
              </div>
              <div className="text-sm font-semibold text-grey-900">{item.value} ({item.percentage}%)</div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

export function MemoryUsageTimelineChart({ data, title, subtitle, height = 300, className = '' }: ChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-bold text-grey-900">{title}</h3>
        {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="time" type="number" unit="s" stroke="#64748b" style={{ fontSize: '12px' }} />
          <YAxis unit="MB" stroke="#64748b" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#f1f5f9' }}
            formatter={(value: any, name: any) => [`${value} MB`, name]}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line type="monotone" dataKey="used_memory" stroke="#dc2626" strokeWidth={2} name="Used Memory" />
          <Line type="monotone" dataKey="total_memory" stroke="#16a34a" strokeWidth={2} name="Total Memory" />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  )
}
