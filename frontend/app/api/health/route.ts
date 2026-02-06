import { NextResponse } from 'next/server'

/**
 * Health check endpoint for the frontend
 * Used by Docker health checks and monitoring
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'frontend',
      timestamp: new Date().toISOString(),
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.2',
    },
    { status: 200 }
  )
}
