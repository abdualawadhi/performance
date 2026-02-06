import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  title: 'Low-Code Performance Scanner | Professional Edition',
  description: 'Enterprise-grade performance testing and optimization for Bubble, OutSystems, and Airtable applications',
  keywords: [
    'performance',
    'testing',
    'low-code',
    'bubble',
    'outsystems',
    'airtable',
    'enterprise',
    'professional',
    'automation'
  ],
  authors: [{ name: 'Professional Performance Scanner Team' }],
  openGraph: {
    title: 'Low-Code Performance Scanner',
    description: 'Enterprise-grade performance testing for low-code platforms',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className={`${inter.className} h-full bg-gradient-to-br from-slate-50 to-slate-100 antialiased`}>
        <div className="min-h-full flex flex-col">
          {/* Enhanced Header */}
          <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-slate-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg shadow-primary-200">
                    <svg
                      width="28"
                      height="28"
                      className="w-7 h-7 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                      Low-Code Performance Scanner
                    </h1>
                    <p className="text-sm text-slate-600 font-medium">
                      Enterprise Testing Suite
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="hidden sm:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-success-50 to-success-100 rounded-full border border-success-200">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-semibold text-success-700">v1.0.2 Professional</span>
                  </div>
                  <a
                    href="/api/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors font-medium text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    API Docs
                  </a>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Enhanced Footer */}
          <footer className="bg-white border-t border-slate-200 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                      <svg
                        width="20"
                        height="20"
                        className="w-5 h-5 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                    </div>
                    <h3 className="font-bold text-slate-900">Performance Scanner</h3>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Professional-grade performance testing and optimization insights for low-code platforms.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-4">Supported Platforms</h4>
                  <ul className="space-y-2 text-sm text-slate-600">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                      Bubble.io
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                      OutSystems
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                      Airtable
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                      And More
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-4">Features</h4>
                  <ul className="space-y-2 text-sm text-slate-600">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-success-500 rounded-full"></span>
                      Multi-scenario testing
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-success-500 rounded-full"></span>
                      Core Web Vitals analysis
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-success-500 rounded-full"></span>
                      Memory profiling
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-success-500 rounded-full"></span>
                      Professional reports
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-slate-200 pt-6">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-600">
                  <p>
                    © {new Date().getFullYear()} Low-Code Performance Scanner. All rights reserved.
                  </p>
                  <p className="flex items-center gap-2">
                    Built with
                    <span className="text-red-500">❤️</span>
                    for professional developers
                  </p>
                </div>
              </div>
            </div>
          </footer>
        </div>

        {/* Enhanced Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#1e293b',
              boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.15)',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '16px',
              fontSize: '14px',
            },
            success: {
              iconTheme: {
                primary: '#16a34a',
                secondary: '#fff',
              },
              style: {
                borderLeft: '4px solid #16a34a',
              },
            },
            error: {
              iconTheme: {
                primary: '#dc2626',
                secondary: '#fff',
              },
              style: {
                borderLeft: '4px solid #dc2626',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
