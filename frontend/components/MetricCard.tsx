'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: number
  confidence?: 'certain' | 'firm' | 'tentative'
  icon?: React.ReactNode
  tooltip?: string
  status?: 'excellent' | 'good' | 'warning' | 'critical'
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function MetricCard({
  title,
  value,
  unit,
  trend,
  trendValue,
  confidence,
  icon,
  tooltip,
  status = 'good',
  className = '',
  size = 'md'
}: MetricCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-success-600" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-danger-600" />
      default:
        return <Minus className="w-4 h-4 text-grey-500" />
    }
  }

  const getConfidenceIcon = () => {
    const icons = {
      certain: '🔒',
      firm: '⚠️',
      tentative: '❓'
    }
    return icons[confidence || 'firm']
  }

  const getStatusColor = () => {
    const colors = {
      excellent: 'border-success-300 bg-success-50',
      good: 'border-primary-300 bg-primary-50',
      warning: 'border-warning-300 bg-warning-50',
      critical: 'border-danger-300 bg-danger-50'
    }
    return colors[status]
  }

  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, boxShadow: '0 12px 24px rgba(0, 0, 0, 0.12)' }}
      className={`card ${sizeClasses[size]} border-l-4 ${getStatusColor()} transition-all duration-200 ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="p-2 rounded-lg bg-white bg-opacity-60">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-sm font-medium text-grey-600 uppercase tracking-wide">
              {title}
            </h3>
            {tooltip && (
              <p className="text-xs text-grey-500 mt-0.5">{tooltip}</p>
            )}
          </div>
        </div>
        {confidence && (
          <span
            className="text-lg transition-transform hover:scale-110"
            title={`Confidence: ${confidence}`}
          >
            {getConfidenceIcon()}
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-3 mb-2">
        <span className="text-3xl font-bold text-grey-900 font-display">
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
        {unit && <span className="text-lg text-grey-500 font-medium">{unit}</span>}
      </div>

      {trend && (
        <div className="flex items-center gap-1">
          {getTrendIcon()}
          <span className={`text-sm font-medium ${
            trend === 'up' ? 'text-success-600' : trend === 'down' ? 'text-danger-600' : 'text-grey-600'
          }`}>
            {trend === 'up' ? 'Improving' : trend === 'down' ? 'Declining' : 'Stable'}
            {trendValue && ` ${trendValue > 0 ? '+' : ''}${trendValue.toFixed(1)}%`}
          </span>
        </div>
      )}
    </motion.div>
  )
}
