import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { url } = await request.json()

    if (!url) {
      return NextResponse.json({ error: 'URL is required' }, { status: 400 })
    }

    // For now, return mock data
    // In production, this would call the backend API
    const mockResult = {
      scan_id: `scan_${Date.now()}`,
      url,
      platform: 'bubble', // This would be detected
      performance_metrics: {
        average_score: 85.5,
        scenarios: {
          'homepage_load_desktop': {
            overall_score: 88.2,
            standard_deviation: 2.1,
            confidence_level: 'certain'
          }
        }
      },
      performance_matrix: {
        rows: [
          {
            scenario: 'homepage_load',
            load_time_s: 2.3,
            memory_usage_max_mb: 45.6,
            performance_score: 88.2,
            confidence_level: 'certain'
          },
          {
            scenario: 'regular_use_case',
            load_time_s: 1.8,
            memory_usage_max_mb: 42.1,
            performance_score: 91.5,
            confidence_level: 'firm'
          }
        ]
      }
    }

    return NextResponse.json(mockResult)
  } catch (error) {
    console.error('Scan API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}