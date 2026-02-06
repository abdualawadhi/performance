'use client'

import { motion } from 'framer-motion'
import { Lock, AlertCircle, HelpCircle } from 'lucide-react'

type ConfidenceType = 'certain' | 'firm' | 'tentative'

interface ConfidenceLevelProps {
  level: ConfidenceType
  percentage?: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function ConfidenceLevel({
  level,
  percentage,
  showLabel = true,
  size = 'md',
  className = ''
}: ConfidenceLevelProps) {
  const confidenceConfig = {
    certain: {
      icon: Lock,
      label: 'Certain',
      color: 'success',
      bgColor: 'bg-success-50',
      textColor: 'text-success-700',
      borderColor: 'border-success-200',
      description: 'High confidence in findings'
    },
    firm: {
      icon: AlertCircle,
      label: 'Firm',
      color: 'warning',
      bgColor: 'bg-warning-50',
      textColor: 'text-warning-700',
      borderColor: 'border-warning-200',
      description: 'Good confidence in findings'
    },
    tentative: {
      icon: HelpCircle,
      label: 'Tentative',
      color: 'info',
      bgColor: 'bg-info-50',
      textColor: 'text-info-700',
      borderColor: 'border-info-200',
      description: 'Findings need verification'
    }
  }

  const config = confidenceConfig[level]
  const IconComponent = config.icon

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}
    >
      <IconComponent className={`${sizeClasses[size]} ${config.textColor}`} />
      {showLabel && (
        <div className="flex flex-col">
          <span className={`text-xs font-semibold ${config.textColor}`}>
            {config.label}
          </span>
          {percentage !== undefined && (
            <span className={`text-xs ${config.textColor} opacity-75`}>
              {percentage}% confidence
            </span>
          )}
        </div>
      )}
    </motion.div>
  )
}
