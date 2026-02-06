'use client'

import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle } from 'lucide-react'

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  color?: 'primary' | 'success' | 'warning' | 'accent' | 'error' | 'info'
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  showPercentage?: boolean
  animated?: boolean
  status?: 'idle' | 'loading' | 'complete' | 'error'
  className?: string
}

export function ProgressBar({
  value,
  max = 100,
  label,
  color = 'primary',
  size = 'md',
  showValue = true,
  showPercentage = true,
  animated = true,
  status = 'idle',
  className = ''
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)

  const colorClasses = {
    primary: 'bg-primary-600',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    accent: 'bg-accent-500',
    error: 'bg-danger-500',
    info: 'bg-info-600'
  }

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="w-4 h-4 text-success-600" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-danger-600" />
      case 'loading':
        return <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
      default:
        return null
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {(label || showValue || showPercentage || status !== 'idle') && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {label && (
              <span className="text-sm font-medium text-grey-700">{label}</span>
            )}
            {status !== 'idle' && getStatusIcon()}
          </div>
          <div className="flex items-center gap-3">
            {showPercentage && (
              <span className="text-sm font-semibold text-grey-600">
                {Math.round(percentage)}%
              </span>
            )}
            {showValue && !showPercentage && (
              <span className="text-sm text-grey-500">
                {value.toFixed(1)}/{max}
              </span>
            )}
          </div>
        </div>
      )}

      <div className={`w-full bg-grey-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: animated ? 1 : 0, ease: 'easeOut' }}
          className={`h-full ${colorClasses[color]} rounded-full shadow-soft`}
        />
      </div>
    </div>
  )
}
