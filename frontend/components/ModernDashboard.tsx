"use client"

import React, { useState, useEffect, useRef } from 'react'
import toast from 'react-hot-toast'
import { useDashboardStore } from '../app/store'

interface Scan {
  scan_id: string
  url: string
  status: string
  progress: number
  current_step?: string
  overall_score?: number
  platform?: string
  scenarios_count?: number
  completed_at?: string
  error?: string
}

// Convert store interfaces to dashboard interface
const convertStoreScanToDashboardScan = (storeScan: any): Scan | null => {
  if (!storeScan) return null;
  
  return {
    scan_id: storeScan.id || storeScan.scan_id,
    url: storeScan.url,
    status: storeScan.status || 'completed',
    progress: storeScan.status === 'completed' ? 100 : 0,
    current_step: storeScan.currentStep,
    overall_score: storeScan.overallScore,
    platform: storeScan.platform,
    scenarios_count: storeScan.scenarios?.length || 0,
    completed_at: storeScan.timestamp?.toISOString(),
    error: storeScan.error
  };
};

const convertStoreHistoryToDashboardScans = (storeHistory: any[]): Scan[] => {
  return storeHistory.map(convertStoreScanToDashboardScan).filter(Boolean) as Scan[];
};

// Parse log messages from the scanner into a clean format
const parseLogMessage = (log: string): string => {
  // Extract timestamp and message from scanner logs
  const timestampMatch = log.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})/);
  const messageMatch = log.match(/- (.+)$/);
  
  if (timestampMatch && messageMatch) {
    const timestamp = timestampMatch[1];
    const message = messageMatch[1];
    
    // Clean up the message
    let cleanMessage = message
      .replace(/lowcode_scanner\.core\.scanner\.LowCodePerformanceScanner - INFO - /g, '')
      .replace(/INFO - /g, '')
      .trim();
    
    // Add icons for common actions
    if (cleanMessage.includes('Starting performance scan')) {
      return `🚀 ${cleanMessage}`;
    } else if (cleanMessage.includes('Detected platform')) {
      return `🌐 ${cleanMessage}`;
    } else if (cleanMessage.includes('Running scenario')) {
      return `⚡ ${cleanMessage}`;
    } else if (cleanMessage.includes('Run')) {
      return `🔄 ${cleanMessage}`;
    } else if (cleanMessage.includes('Completed scenario')) {
      return `✅ ${cleanMessage}`;
    } else if (cleanMessage.includes('Generated') || cleanMessage.includes('Scan completed successfully')) {
      return `🎉 ${cleanMessage}`;
    } else if (cleanMessage.includes('Scanning...')) {
      return `⏳ ${cleanMessage}`;
    }
    
    return cleanMessage;
  }
  
  // Fallback for other log formats
  if (log.includes('Starting performance scan')) {
    return `🚀 ${log}`;
  } else if (log.includes('Detected platform')) {
    return `🌐 ${log}`;
  } else if (log.includes('Running scenario')) {
    return `⚡ ${log}`;
  } else if (log.includes('Run')) {
    return `🔄 ${log}`;
  } else if (log.includes('Completed scenario')) {
    return `✅ ${log}`;
  } else if (log.includes('Generated') || log.includes('Scan completed successfully')) {
    return `🎉 ${log}`;
  }
  
  return log;
};

export default function ModernDashboard() {
  const [selectedDevice, setSelectedDevice] = useState('desktop')
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([])

  const scanUrl = useDashboardStore((s) => s.scanUrl)
  const setScanUrl = useDashboardStore((s) => s.setScanUrl)
  const startScan = useDashboardStore((s) => s.startScan)
  const isScanning = useDashboardStore((s) => s.isScanning)
  const currentScan = useDashboardStore((s) => s.currentScan)
  const liveProgress = useDashboardStore((s) => s.liveProgress)
  const scanHistory = useDashboardStore((s) => s.scanHistory)

  const logsRef = useRef<HTMLDivElement | null>(null)

  // Convert store data to dashboard format
  const dashboardCurrentScan = convertStoreScanToDashboardScan(currentScan);
  const dashboardScanHistory = convertStoreHistoryToDashboardScans(scanHistory);

  const fetchScanHistory = useDashboardStore((s) => s.fetchScanHistory);

  // Fetch scan history on component mount
  useEffect(() => {
    fetchScanHistory()
  }, [])

  const scenarios = [
    { id: 'homepage_load', name: 'Homepage Load', description: 'Initial page load performance' },
    { id: 'regular_use_case', name: 'Regular Use Case', description: 'Typical user interactions' },
    { id: 'heavy_list_load', name: 'List Load', description: 'Large dataset loading' },
    { id: 'upfront_scripting', name: 'Scripting', description: 'JavaScript execution test' },
  ]

  // Auto-scroll logs when liveProgress updates
  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight
    }
  }, [liveProgress?.logs, dashboardCurrentScan])

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

    // setScanUrl is handled by the input binding
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
      const response = await fetch(`http://localhost:8000/api/scans/${scanId}/reports/${reportName}`)
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'running': return 'text-blue-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completed'
      case 'running': return 'Running'
      case 'failed': return 'Failed'
      default: return 'Unknown'
    }
  }

  return (
    <div className="space-y-6">
      {/* Current Scan Progress */}
      {dashboardCurrentScan && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Live Scan Progress</h3>
            <span className={`text-sm font-medium ${getStatusColor(dashboardCurrentScan.status)}`}>
              {getStatusText(dashboardCurrentScan.status)}
            </span>
          </div>
          
          <div className="space-y-4">
            {/* Scan Header */}
            <div className="flex justify-between items-center pb-3 border-b border-gray-200">
              <div>
                <p className="text-sm font-medium text-gray-900">Target URL</p>
                <p className="text-sm text-gray-600 font-mono">{dashboardCurrentScan.url}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Scan ID</p>
                <p className="text-sm text-gray-600 font-mono">{dashboardCurrentScan.scan_id}</p>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Overall Progress</span>
                <span className="font-medium text-gray-900">{dashboardCurrentScan.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${dashboardCurrentScan.progress}%` }}
                ></div>
              </div>
            </div>

            {/* Current Step */}
            {dashboardCurrentScan.current_step && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center">
                  <div className="animate-pulse">
                    <svg className="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-sm text-blue-800 font-medium">Current Step</p>
                </div>
                <p className="text-sm text-blue-700 mt-1">{dashboardCurrentScan.current_step}</p>
              </div>
            )}

            {/* Live Logs */}
            {liveProgress && liveProgress.logs.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-900">Live Activity Log</h4>
                  <span className="text-xs text-gray-500">Auto-scrolling</span>
                </div>
                <div 
                  ref={logsRef}
                  className="bg-gray-900 text-green-400 rounded-lg p-3 h-48 overflow-y-auto font-mono text-xs"
                >
                  {liveProgress.logs.map((log, index) => (
                    <div key={index} className="mb-1 leading-relaxed">
                      {parseLogMessage(log)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results Summary */}
            {dashboardCurrentScan.status === 'completed' && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Scan Results</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 rounded-lg p-3">
                    <p className="text-xs text-green-600 font-medium">Overall Score</p>
                    <p className="text-lg font-bold text-green-900">{dashboardCurrentScan.overall_score || 0}/100</p>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-xs text-blue-600 font-medium">Platform</p>
                    <p className="text-lg font-bold text-blue-900 capitalize">{dashboardCurrentScan.platform || 'Generic'}</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => downloadReport(dashboardCurrentScan.scan_id, 'html')}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    📊 Download HTML Report
                  </button>
                  <button
                    onClick={() => downloadReport(dashboardCurrentScan.scan_id, 'json')}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                  >
                    📄 Download JSON
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Scan Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Quick Scan</h2>
            <p className="text-gray-600 mt-1">Run a focused performance test in seconds</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* URL Input */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Application URL
            </label>
            <div className="flex gap-3">
              <input
                id="url"
                type="url"
                value={scanUrl}
                onChange={(e) => setScanUrl(e.target.value)}
                placeholder="https://example.app"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                disabled={isScanning}
              />
              <select
                value={selectedDevice}
                onChange={(e) => setSelectedDevice(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                disabled={isScanning}
              >
                <option value="desktop">Desktop - Chrome</option>
                <option value="mobile">Mobile - Chrome</option>
              </select>
            </div>
          </div>

          {/* Scenarios */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Test Scenarios
            </label>
            <div className="flex flex-wrap gap-2">
              {scenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  type="button"
                  onClick={() => toggleScenario(scenario.id)}
                  disabled={isScanning}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    selectedScenarios.includes(scenario.id)
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-700'
                  } ${isScanning ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={scenario.description}
                >
                  {scenario.name}
                </button>
              ))}
            </div>
            {selectedScenarios.length > 0 && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {selectedScenarios.length} scenario{selectedScenarios.length > 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-500">
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
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Clear Form
              </button>
              <button
                type="submit"
                disabled={isScanning || !scanUrl || selectedScenarios.length === 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-400"
              >
                {isScanning ? 'Starting...' : 'Run Scan'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Scan History */}
      {dashboardScanHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Scans</h3>
          <div className="space-y-3">
            {dashboardScanHistory.slice(0, 5).map((scan) => (
              <div key={scan.scan_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`text-sm font-medium ${getStatusColor(scan.status)}`}>
                        {getStatusText(scan.status)}
                      </span>
                      <span className="text-sm text-gray-600 truncate max-w-xs">
                        {scan.url}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      ID: {scan.scan_id}
                      {scan.completed_at && ` • Completed: ${new Date(scan.completed_at).toLocaleString()}`}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {scan.overall_score && (
                      <span className="text-sm font-semibold text-gray-900">
                        {scan.overall_score}/100
                      </span>
                    )}
                    {scan.status === 'completed' && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => downloadReport(scan.scan_id, 'html')}
                          className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                        >
                          HTML
                        </button>
                        <button
                          onClick={() => downloadReport(scan.scan_id, 'json')}
                          className="px-3 py-1 text-xs border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
                        >
                          JSON
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Overview</h3>
          <p className="text-gray-600 text-sm">
            A single place to run scans, save profiles, and view generated reports.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Latest Report</h3>
          <p className="text-gray-600 text-sm">
            {(() => {
              const latestScan = dashboardCurrentScan || (dashboardScanHistory.length > 0 ? dashboardScanHistory[0] : null);
              if (latestScan && latestScan.status === 'completed') {
                return (
                  <>
                    <div>
                      <strong>Score:</strong> {latestScan.overall_score || 'N/A'}/100
                      {latestScan.platform && (
                        <>
                          <br />
                          <strong>Platform:</strong> {latestScan.platform}
                        </>
                      )}
                      {latestScan.url && (
                        <>
                          <br />
                          <strong>URL:</strong> {latestScan.url}
                        </>
                      )}
                    </div>
                    <div className="mt-2">
                      <span className="text-green-600">✅ Ready for download</span>
                      {!dashboardCurrentScan && (
                        <div className="text-xs text-gray-500 mt-1">
                          From scan history
                        </div>
                      )}
                    </div>
                  </>
                );
              }
              return 'No recent reports. Run a scan to generate summary and full artifacts.';
            })()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Export</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => {
                const latestScan = dashboardCurrentScan || (dashboardScanHistory.length > 0 ? dashboardScanHistory[0] : null);
                if (latestScan && latestScan.status === 'completed') {
                  downloadReport(latestScan.scan_id, 'html');
                }
              }}
              disabled={!(dashboardCurrentScan && dashboardCurrentScan.status === 'completed') && !(dashboardScanHistory.length > 0 && dashboardScanHistory[0].status === 'completed')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Download HTML
            </button>
            <button 
              onClick={() => {
                const latestScan = dashboardCurrentScan || (dashboardScanHistory.length > 0 ? dashboardScanHistory[0] : null);
                if (latestScan && latestScan.status === 'completed') {
                  downloadReport(latestScan.scan_id, 'json');
                }
              }}
              disabled={!(dashboardCurrentScan && dashboardCurrentScan.status === 'completed') && !(dashboardScanHistory.length > 0 && dashboardScanHistory[0].status === 'completed')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Download JSON
            </button>
          </div>
          {!(dashboardCurrentScan && dashboardCurrentScan.status === 'completed') && dashboardScanHistory.length > 0 && dashboardScanHistory[0].status === 'completed' && (
            <p className="text-xs text-gray-500 mt-2">
              Using latest scan from history
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
