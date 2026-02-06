import { motion } from 'framer-motion'

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  color?: 'primary' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  className?: string
}

export function ProgressBar({
  value,
  max = 100,
  label,
  color = 'primary',
  size = 'md',
  showValue = true,
  className = ''
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)

  const getColorClasses = () => {
    switch (color) {
      case 'success':
        return 'bg-success-500'
      case 'warning':
        return 'bg-warning-500'
      case 'danger':
        return 'bg-danger-500'
      default:
        return 'bg-primary-600'
    }
  }

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-2'
      case 'lg':
        return 'h-4'
      default:
        return 'h-3'
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {(label || showValue) && (
        <div className="flex justify-between items-center">
          {label && <span className="text-sm font-medium text-grey-700">{label}</span>}
          {showValue && (
            <span className="text-sm text-grey-500">
              {value.toFixed(1)}/{max}
            </span>
          )}
        </div>
      )}

      <div className={`w-full bg-grey-200 rounded-full overflow-hidden ${getSizeClasses()}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`h-full ${getColorClasses()} rounded-full`}
        />
      </div>
    </div>
  )
}