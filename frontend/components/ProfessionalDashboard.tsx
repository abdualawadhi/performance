"use client"

import React, { useState, useEffect, useRef } from 'react'
import toast from 'react-hot-toast'
import { useDashboardStore } from '../app/store'
import { API_BASE_URL } from '@/lib/config'
import { motion } from 'framer-motion'
import { SeverityBlock } from './SeverityBlockPro'
import { ProgressBar } from './ProgressBarPro'
import { PerformanceTrendChart, ScenarioComparisonChart, PerformanceRadarChart, DistributionPieChart } from './ProfessionalCharts'
import {
  Activity,
  Clock,
  Database,
  Globe,
  TrendingUp,
  Shield,
  Zap,
  FileText,
  Download,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Info
} from 'lucide-react'

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle2 className="w-5 h-5 text-success-600" />
    case 'running':
      return <Activity className="w-5 h-5 text-primary-600 animate-pulse" />
    case 'failed':
      return <XCircle className="w-5 h-5 text-danger-600" />
    default:
      return <Info className="w-5 h-5 text-grey-600" />
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-success-100 text-success-800 border-success-200'
    case 'running':
      return 'bg-primary-100 text-primary-800 border-primary-200'
    case 'failed':
      return 'bg-danger-100 text-danger-800 border-danger-200'
    default:
      return 'bg-grey-100 text-grey-800 border-grey-200'
  }
}

export default function ProfessionalDashboard() {
  const [selectedDevice, setSelectedDevice] = useState('desktop')
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])

  const scanUrl = useDashboardStore((s) => s.scanUrl)
  const setScanUrl = useDashboardStore((s) => s.setScanUrl)
  const startScan = useDashboardStore((s) => s.startScan)
  const isScanning = useDashboardStore((s) => s.isScanning)
  const currentScan = useDashboardStore((s) => s.currentScan)
  const liveProgress = useDashboardStore((s) => s.liveProgress)
  const scanHistory = useDashboardStore((s) => s.scanHistory)
  const fetchScanHistory = useDashboardStore((s) => s.fetchScanHistory)

  const logsRef = useRef<HTMLDivElement | null>(null)
  const showLiveSection = isScanning || !!liveProgress || !!currentScan
  const status = isScanning ? 'running' : currentScan ? 'completed' : 'idle'
  const statusLabel = status === 'running' ? 'Running' : status === 'completed' ? 'Completed' : 'Idle'
  const activeUrl = currentScan?.url || scanUrl || '—'
  const activeScanId = currentScan?.id || '—'

  useEffect(() => {
    fetchScanHistory()
  }, [])

  const scenarios = [
    { id: 'homepage_load', name: 'Homepage Load', description: 'Initial page load performance', icon: '🏠' },
    { id: 'regular_use_case', name: 'Regular Use Case', description: 'Typical user interactions', icon: '👆' },
    { id: 'heavy_list_load', name: 'List Load', description: 'Large dataset loading', icon: '📋' },
    { id: 'upfront_scripting', name: 'Scripting', description: 'JavaScript execution test', icon: '⚡' },
  ]

  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight
    }
  }, [liveProgress?.logs, currentScan])

  const toggleScenario = (scenarioId: string) => {
    setSelectedScenarios(prev =>
      prev.includes(scenarioId)
        ? prev.filter(id => id !== scenarioId)
        : [...prev, scenarioId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!scanUrl) {
      toast.error('Please enter a URL to scan')
      return
    }

    if (selectedScenarios.length === 0) {
      toast.error('Please select at least one test scenario')
      return
    }

    try {
      await startScan({
        scenarios: selectedScenarios,
        devices: [selectedDevice],
        network: ['wifi'],
        formats: ['html', 'json'],
      })

      toast.success('Scan started — tracking live progress')
      setSelectedScenarios([])
    } catch (error) {
      toast.error('Failed to connect to backend. Make sure the API server is running.')
      console.error('Scan error:', error)
    }
  }

  const downloadReport = async (scanId: string, reportName: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/scans/${scanId}/reports/${reportName}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${scanId}.${reportName}` 
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success(`Downloaded ${reportName} report`)
      } else {
        toast.error(`Failed to download ${reportName} report`)
      }
    } catch (error) {
      toast.error('Failed to download report')
      console.error('Download error:', error)
    }
  }

  const getSeverityFromScore = (score: number) => {
    if (score >= 90) return 'excellent'
    if (score >= 80) return 'good'
    if (score >= 70) return 'warning'
    return 'critical'
  }

  return (
    <div className="space-y-8">
      {/* Live Scan Progress Section */}
      {showLiveSection && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-soft border border-grey-200 overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-50 to-primary-100 px-6 py-4 border-b border-primary-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity className="w-6 h-6 text-primary-600" />
                <h3 className="text-lg font-bold text-primary-900">Live Scan Progress</h3>
              </div>
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${getStatusBadge(status)}`}>
                {getStatusIcon(status)}
                <span className="text-sm font-semibold capitalize">
                  {statusLabel}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Scan Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-grey-50 rounded-xl p-4 border border-grey-200">
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="w-5 h-5 text-primary-600" />
                  <span className="text-sm font-medium text-grey-600">Target URL</span>
                </div>
                <p className="text-sm font-mono text-grey-900 break-all">{activeUrl}</p>
              </div>
              <div className="bg-grey-50 rounded-xl p-4 border border-grey-200">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="w-5 h-5 text-primary-600" />
                  <span className="text-sm font-medium text-grey-600">Scan ID</span>
                </div>
                <p className="text-sm font-mono text-grey-900">{activeScanId}</p>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <ProgressBar
                value={liveProgress?.progress || 0}
                label="Overall Progress"
                color="primary"
                showPercentage={true}
                animated={true}
                status={status === 'completed' ? 'complete' : status === 'running' ? 'loading' : 'idle'}
              />
            </div>

            {/* Current Step */}
            {liveProgress?.currentStep && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4"
              >
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide">Current Step</p>
                    <p className="text-sm text-blue-900 font-medium">{liveProgress.currentStep}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Live Logs */}
            {liveProgress && liveProgress.logs.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-grey-900 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-primary-600" />
                    Live Activity Log
                  </h4>
                  <span className="text-xs text-grey-500 bg-grey-100 px-2 py-1 rounded-full">Auto-scrolling</span>
                </div>
                <div
                  ref={logsRef}
                  className="bg-grey-900 text-green-400 rounded-xl p-4 h-64 overflow-y-auto font-mono text-xs leading-relaxed shadow-inner"
                >
                  {liveProgress.logs.map((log, index) => (
                    <div key={index} className="mb-1">
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results Summary */}
            {!isScanning && currentScan && currentScan.overallScore > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="pt-4 border-t border-grey-200"
              >
                <h4 className="text-sm font-semibold text-grey-900 mb-4 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-success-600" />
                  Scan Results
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <SeverityBlock
                    severity={getSeverityFromScore(currentScan.overallScore)}
                    title="Overall Score"
                    description="Performance score based on all test scenarios"
                    metric={currentScan.overallScore}
                    metricLabel="/100"
                  />
                  {currentScan.platform && (
                    <SeverityBlock
                      severity="good"
                      title="Platform Detected"
                      description={`Low-code platform identified during scan`}
                      metric={currentScan.platform}
                      metricLabel=""
                    />
                  )}
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => downloadReport(currentScan.id, 'html')}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium shadow-lg shadow-primary-200"
                  >
                    <FileText className="w-5 h-5" />
                    Download HTML Report
                  </button>
                  <button
                    onClick={() => downloadReport(currentScan.id, 'json')}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-grey-300 text-grey-700 rounded-lg hover:bg-grey-50 transition-colors font-medium"
                  >
                    <Download className="w-5 h-5" />
                    Download JSON
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      )}

      {/* Quick Scan Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-2xl shadow-soft border border-grey-200 overflow-hidden"
      >
        <div className="bg-gradient-to-r from-grey-50 to-grey-100 px-6 py-4 border-b border-grey-200">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-grey-900">Quick Scan</h2>
          </div>
          <p className="text-grey-600 mt-1">Run a focused performance test in seconds</p>
        </div>

        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* URL Input */}
            <div>
              <label htmlFor="url" className="block text-sm font-semibold text-grey-700 mb-3">
                Application URL
              </label>
              <div className="flex gap-3">
                <input
                  id="url"
                  type="url"
                  value={scanUrl}
                  onChange={(e) => setScanUrl(e.target.value)}
                  placeholder="https://example.app"
                  className="flex-1 px-4 py-3 border-2 border-grey-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all text-grey-900"
                  disabled={isScanning}
                />
                <select
                  value={selectedDevice}
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  className="px-4 py-3 border-2 border-grey-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none bg-white text-grey-700"
                  disabled={isScanning}
                >
                  <option value="desktop">Desktop - Chrome</option>
                  <option value="mobile">Mobile - Chrome</option>
                </select>
              </div>
            </div>

            {/* Scenarios */}
            <div>
              <label className="block text-sm font-semibold text-grey-700 mb-4">
                Test Scenarios
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {scenarios.map((scenario) => (
                  <button
                    key={scenario.id}
                    type="button"
                    onClick={() => toggleScenario(scenario.id)}
                    disabled={isScanning}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedScenarios.includes(scenario.id)
                        ? 'bg-primary-50 border-primary-500 text-primary-900'
                        : 'bg-white border-grey-300 text-grey-700 hover:border-primary-300 hover:bg-grey-50'
                    } ${isScanning ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title={scenario.description}
                  >
                    <div className="text-2xl mb-1">{scenario.icon}</div>
                    <div className="text-sm font-medium">{scenario.name}</div>
                    <div className="text-xs mt-1 opacity-75">{scenario.description}</div>
                  </button>
                ))}
              </div>
              {selectedScenarios.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 text-sm text-primary-700 bg-primary-50 px-4 py-2 rounded-lg inline-flex items-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Selected: {selectedScenarios.length} scenario{selectedScenarios.length > 1 ? 's' : ''}
                </motion.div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-6 border-t border-grey-200">
              <p className="text-sm text-grey-500">
                {isScanning ? 'Starting scan...' : 'Advanced options are available in the sidebar'}
              </p>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setScanUrl('')
                    setSelectedScenarios([])
                  }}
                  disabled={isScanning}
                  className="px-6 py-3 border-2 border-grey-300 text-grey-700 rounded-xl hover:bg-grey-50 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Clear Form
                </button>
                <button
                  type="submit"
                  disabled={isScanning || !scanUrl || selectedScenarios.length === 0}
                  className="px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all font-medium shadow-lg shadow-primary-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-grey-400 disabled:to-grey-500 disabled:shadow-none"
                >
                  {isScanning ? (
                    <span className="flex items-center gap-2">
                      <Activity className="w-5 h-5 animate-spin" />
                      Starting...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      Run Scan
                    </span>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </motion.div>

      {/* Scan History Section */}
      {scanHistory.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-soft border border-grey-200 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-grey-50 to-grey-100 px-6 py-4 border-b border-grey-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Clock className="w-6 h-6 text-primary-600" />
                <h3 className="text-lg font-bold text-grey-900">Recent Scans</h3>
              </div>
              <span className="text-sm text-grey-600 bg-grey-200 px-3 py-1 rounded-full">
                {scanHistory.length} scan{scanHistory.length > 1 ? 's' : ''}
              </span>
            </div>
          </div>
          <div className="divide-y divide-grey-200">
            {scanHistory.slice(0, 5).map((scan: any) => (
              <div key={scan.id} className="p-4 hover:bg-grey-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      {getStatusIcon(scan.status)}
                      <span className="text-sm font-medium text-grey-900 truncate">
                        {scan.url}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-grey-500">
                      <span className="font-mono">{scan.id}</span>
                      {scan.timestamp && (
                        <span>• {new Date(scan.timestamp).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {scan.overallScore && (
                      <div className="text-right">
                        <div className="text-2xl font-bold text-grey-900">
                          {scan.overallScore}
                        </div>
                        <div className="text-xs text-grey-500">Score</div>
                      </div>
                    )}
                    {scan.status === 'completed' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => downloadReport(scan.id, 'html')}
                          className="p-2 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors"
                          title="Download HTML"
                        >
                          <FileText className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => downloadReport(scan.id, 'json')}
                          className="p-2 bg-grey-100 text-grey-700 rounded-lg hover:bg-grey-200 transition-colors"
                          title="Download JSON"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
