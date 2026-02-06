"use client"

import React from 'react'

export default function EnhancedDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-7xl p-6">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg brand flex items-center justify-center font-bold">LS</div>
            <div>
              <h1 className="text-xl font-semibold">Enhanced Dashboard</h1>
              <p className="text-sm text-gray-500">Legacy dashboard placeholder — simplified to avoid build errors.</p>
            </div>
          </div>
        </header>

        <main>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">Controls</div>
            <div className="card md:col-span-2">Results</div>
          </div>
        </main>
      </div>
    </div>
  )
}
