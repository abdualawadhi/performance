'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricDisplayProps {
  label: string
  value: string | number
  unit?: string
  icon?: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  description?: string
  className?: string
}

const colorClasses = {
  primary: 'text-primary-600 bg-primary-50 border-primary-200',
  success: 'text-success-600 bg-success-50 border-success-200',
  warning: 'text-warning-600 bg-warning-50 border-warning-200',
  danger: 'text-danger-600 bg-danger-50 border-danger-200',
  info: 'text-info-600 bg-info-50 border-info-200',
}

const sizeClasses = {
  sm: {
    value: 'text-2xl',
    label: 'text-xs',
    icon: 'w-4 h-4',
  },
  md: {
    value: 'text-3xl',
    label: 'text-sm',
    icon: 'w-5 h-5',
  },
  lg: {
    value: 'text-4xl',
    label: 'text-base',
    icon: 'w-6 h-6',
  },
}

export function MetricDisplay({
  label,
  value,
  unit,
  icon: Icon,
  trend,
  trendValue,
  color = 'primary',
  size = 'md',
  description,
  className = '',
}: MetricDisplayProps) {
  const colorClass = colorClasses[color]
  const sizeClass = sizeClasses[size]

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-success-600" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-danger-600" />
      default:
        return <Minus className="w-4 h-4 text-grey-600" />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-success-600'
      case 'down':
        return 'text-danger-600'
      default:
        return 'text-grey-600'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      className={`bg-white rounded-xl shadow-soft border border-slate-200 p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className={`p-2.5 rounded-lg ${colorClass}`}>
              <Icon className={sizeClass.icon} />
            </div>
          )}
          <div>
            <p className={`font-medium text-slate-600 ${sizeClass.label}`}>{label}</p>
            {description && (
              <p className="text-xs text-slate-500 mt-0.5">{description}</p>
            )}
          </div>
        </div>
        {trend && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${getTrendColor()} bg-slate-50`}>
            {getTrendIcon()}
            {trendValue && (
              <span className="text-xs font-semibold">{trendValue}</span>
            )}
          </div>
        )}
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-2">
        <span className={`font-bold ${colorClass.split(' ')[0]} ${sizeClass.value}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {unit && (
          <span className={`text-slate-500 ${sizeClass.label}`}>{unit}</span>
        )}
      </div>
    </motion.div>
  )
}
