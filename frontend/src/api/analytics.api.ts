import client from './client'
import type { AnalyticsData } from '../types/analytics'

export async function fetchAnalytics(sessionId: string): Promise<AnalyticsData> {
  const response = await client.get<AnalyticsData>('/api/analytics', {
    params: { session_id: sessionId },
  })
  return response.data
}
