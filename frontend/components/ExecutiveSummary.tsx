'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, AlertTriangle, XCircle, Target, TrendingUp, Zap, Shield } from 'lucide-react'

interface ExecutiveSummaryProps {
  overallScore: number
  keyFindings: string[]
  businessImpact: string
  priorityRecommendations: string[]
  platform?: string
  confidenceLevel?: 'certain' | 'firm' | 'tentative'
  className?: string
}

const getScoreSeverity = (score: number) => {
  if (score >= 90) return { level: 'Excellent', color: 'success', icon: CheckCircle2 }
  if (score >= 80) return { level: 'Good', color: 'primary', icon: CheckCircle2 }
  if (score >= 70) return { level: 'Needs Improvement', color: 'warning', icon: AlertTriangle }
  return { level: 'Critical', color: 'danger', icon: XCircle }
}

const colorConfig: Record<string, { bg: string; text: string; border: string; icon: string; gradient: string }> = {
  success: {
    bg: 'bg-success-50',
    text: 'text-success-700',
    border: 'border-success-200',
    icon: 'text-success-600',
    gradient: 'from-success-500 to-success-600'
  },
  primary: {
    bg: 'bg-primary-50',
    text: 'text-primary-700',
    border: 'border-primary-200',
    icon: 'text-primary-600',
    gradient: 'from-primary-500 to-primary-600'
  },
  warning: {
    bg: 'bg-warning-50',
    text: 'text-warning-700',
    border: 'border-warning-200',
    icon: 'text-warning-600',
    gradient: 'from-warning-500 to-warning-600'
  },
  danger: {
    bg: 'bg-danger-50',
    text: 'text-danger-700',
    border: 'border-danger-200',
    icon: 'text-danger-600',
    gradient: 'from-danger-500 to-danger-600'
  },
}

export function ExecutiveSummary({
  overallScore,
  keyFindings,
  businessImpact,
  priorityRecommendations,
  platform,
  confidenceLevel = 'certain',
  className = '',
}: ExecutiveSummaryProps) {
  const severity = getScoreSeverity(overallScore)
  const colors = colorConfig[severity.color] || colorConfig.primary
  const ScoreIcon = severity.icon

  const confidenceConfig = {
    certain: {
      label: 'High',
      icon: Shield,
      color: 'success',
      description: 'Results verified with ±5% tolerance'
    },
    firm: {
      label: 'Medium',
      icon: Shield,
      color: 'warning',
      description: 'Results with ±10% tolerance'
    },
    tentative: {
      label: 'Low',
      icon: AlertTriangle,
      color: 'danger',
      description: 'Results require additional verification'
    }
  }

  const confidence = confidenceConfig[confidenceLevel]
  const ConfidenceIcon = confidence.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`space-y-6 ${className}`}
    >
      {/* Overall Score Section */}
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden">
        <div className={`bg-gradient-to-r from-${severity.color}-500 to-${severity.color}-600 px-6 py-4`}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Executive Summary</h3>
            <ScoreIcon className="w-6 h-6 text-white" />
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Overall Score Card */}
            <div className={`rounded-xl p-6 border-2 ${colors.bg} ${colors.border}`}>
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-slate-700">Overall Performance Score</h4>
                <ScoreIcon className={`w-6 h-6 ${colors.icon}`} />
              </div>
              <div className="flex items-baseline gap-2 mb-3">
                <span className={`text-5xl font-bold ${colors.text}`}>{overallScore.toFixed(1)}</span>
                <span className="text-xl text-slate-400">/100</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2.5 mb-3">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${overallScore}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-2.5 rounded-full bg-gradient-to-r from-${severity.color}-400 to-${severity.color}-600}`}
                />
              </div>
              <span className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-semibold ${colors.bg} ${colors.text}`}>
                {severity.level}
              </span>
            </div>

            {/* Platform Card */}
            <div className="bg-slate-50 rounded-xl p-6 border-2 border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-slate-700">Platform Detected</h4>
                <Target className="w-6 h-6 text-primary-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2 capitalize">
                {platform || 'Generic'}
              </div>
              <p className="text-sm text-slate-600">
                Low-code platform automatically identified during scanning
              </p>
            </div>

            {/* Confidence Level Card */}
            <div className="bg-slate-50 rounded-xl p-6 border-2 border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-slate-700">Confidence Level</h4>
                <ConfidenceIcon className={`w-6 h-6 ${confidence.color === 'success' ? 'text-success-600' : confidence.color === 'warning' ? 'text-warning-600' : 'text-danger-600'}`} />
              </div>
              <div className="flex items-baseline gap-2 mb-3">
                <span className={`text-4xl font-bold ${confidence.color === 'success' ? 'text-success-600' : confidence.color === 'warning' ? 'text-warning-600' : 'text-danger-600'}`}>
                  {confidence.label}
                </span>
              </div>
              <p className="text-sm text-slate-600">
                {confidence.description}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Findings Section */}
      <div className="bg-white rounded-xl shadow-soft border border-slate-200 p-6">
        <h4 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          Key Findings
        </h4>
        <ul className="space-y-3">
          {keyFindings.map((finding, index) => (
            <motion.li
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg"
            >
              <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-primary-600 font-bold text-sm">{index + 1}</span>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">{finding}</p>
            </motion.li>
          ))}
        </ul>
      </div>

      {/* Business Impact Section */}
      <div className="bg-white rounded-xl shadow-soft border border-slate-200 p-6">
        <h4 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-primary-600" />
          Business Impact Assessment
        </h4>
        <p className="text-slate-700 leading-relaxed">{businessImpact}</p>
      </div>

      {/* Priority Recommendations Section */}
      <div className="bg-white rounded-xl shadow-soft border border-slate-200 p-6">
        <h4 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-warning-600" />
          Priority Recommendations
        </h4>
        <div className="space-y-3">
          {priorityRecommendations.map((recommendation, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-warning-400 to-warning-600 flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">{index + 1}</span>
              </div>
              <div className="flex-1">
                <p className="text-sm text-slate-700 leading-relaxed">{recommendation}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
