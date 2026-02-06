import { motion } from 'framer-motion'

interface SeverityBlockProps {
  severity: 'excellent' | 'good' | 'needs_improvement' | 'poor' | 'critical'
  title: string
  description: string
  count?: number
  className?: string
}

export function SeverityBlock({
  severity,
  title,
  description,
  count,
  className = ''
}: SeverityBlockProps) {
  const getSeverityConfig = () => {
    switch (severity) {
      case 'excellent':
        return {
          bg: 'bg-success-50',
          border: 'border-success-200',
          text: 'text-success-800',
          icon: '🟢'
        }
      case 'good':
        return {
          bg: 'bg-primary-50',
          border: 'border-primary-200',
          text: 'text-primary-800',
          icon: '🔵'
        }
      case 'needs_improvement':
        return {
          bg: 'bg-warning-50',
          border: 'border-warning-200',
          text: 'text-warning-800',
          icon: '🟡'
        }
      case 'poor':
        return {
          bg: 'bg-warning-50',
          border: 'border-warning-200',
          text: 'text-warning-800',
          icon: '🟠'
        }
      case 'critical':
        return {
          bg: 'bg-danger-50',
          border: 'border-danger-200',
          text: 'text-danger-800',
          icon: '🔴'
        }
    }
  }

  const config = getSeverityConfig()

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`rounded-lg p-4 border-2 ${config.bg} ${config.border} ${className}`}
    >
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{config.icon}</span>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h4 className={`font-semibold ${config.text}`}>{title}</h4>
            {count !== undefined && (
              <span className={`text-sm ${config.text} opacity-75`}>
                ({count})
              </span>
            )}
          </div>
          <p className={`text-sm ${config.text} opacity-90 mt-1`}>
            {description}
          </p>
        </div>
      </div>
    </motion.div>
  )
}