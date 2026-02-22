import client from './client'
import type { AnalyticsData } from '../types/analytics'
import type { Ticket } from '../types/ticket'

export async function fetchDbAnalytics(): Promise<AnalyticsData> {
  const { data } = await client.get<AnalyticsData>('/api/db/analytics')
  return data
}

export async function fetchDbTickets(): Promise<Ticket[]> {
  const { data } = await client.get<Ticket[]>('/api/db/tickets')
  return data
}
