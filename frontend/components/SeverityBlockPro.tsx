'use client'

import { motion } from 'framer-motion'

type SeverityType = 'excellent' | 'good' | 'warning' | 'accent' | 'critical'

interface SeverityBlockProps {
  severity: SeverityType
  title: string
  description: string
  count?: number
  metric?: string | number
  metricLabel?: string
  recommendation?: string
  className?: string
  onClick?: () => void
}

export function SeverityBlock({
  severity,
  title,
  description,
  count,
  metric,
  metricLabel,
  recommendation,
  className = '',
  onClick
}: SeverityBlockProps) {
  const severityConfig = {
    excellent: {
      bg: 'bg-success-50',
      border: 'border-success-200',
      borderLeft: 'border-l-success-500',
      text: 'text-success-900',
      icon: '🟢',
      label: 'Excellent'
    },
    good: {
      bg: 'bg-primary-50',
      border: 'border-primary-200',
      borderLeft: 'border-l-primary-500',
      text: 'text-primary-900',
      icon: '🔵',
      label: 'Good'
    },
    warning: {
      bg: 'bg-warning-50',
      border: 'border-warning-200',
      borderLeft: 'border-l-warning-500',
      text: 'text-warning-900',
      icon: '🟡',
      label: 'Warning'
    },
    accent: {
      bg: 'bg-accent-50',
      border: 'border-accent-200',
      borderLeft: 'border-l-accent-500',
      text: 'text-accent-900',
      icon: '🟠',
      label: 'Needs Improvement'
    },
    critical: {
      bg: 'bg-danger-50',
      border: 'border-danger-200',
      borderLeft: 'border-l-danger-500',
      text: 'text-danger-900',
      icon: '🔴',
      label: 'Critical'
    }
  }

  const config = severityConfig[severity]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`rounded-xl p-5 border-2 border-l-4 ${config.bg} ${config.border} ${config.borderLeft} transition-all duration-200 ${onClick ? 'cursor-pointer hover:shadow-card' : ''} ${className}`}
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl mt-1">{config.icon}</span>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className={`font-bold text-lg ${config.text}`}>{title}</h4>
            {count !== undefined && (
              <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${config.bg} ${config.text}`}>
                {count} {count === 1 ? 'issue' : 'issues'}
              </span>
            )}
          </div>
          
          <p className={`text-sm ${config.text} opacity-90 mb-3`}>
            {description}
          </p>

          {metric !== undefined && (
            <div className="mb-3">
              <div className="flex items-baseline gap-2">
                <span className={`text-2xl font-bold ${config.text}`}>
                  {typeof metric === 'number' ? metric.toFixed(2) : metric}
                </span>
                {metricLabel && (
                  <span className={`text-sm ${config.text} opacity-75`}>{metricLabel}</span>
                )}
              </div>
            </div>
          )}

          {recommendation && (
            <div className={`p-3 rounded-lg bg-white bg-opacity-40 border-l-2 ${config.borderLeft}`}>
              <p className={`text-xs font-medium ${config.text}`}>
                💡 {recommendation}
              </p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
