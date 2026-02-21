import client from './client'
import type { Ticket } from '../types/ticket'

export async function fetchTickets(sessionId: string): Promise<Ticket[]> {
  const response = await client.get<Ticket[]>('/api/tickets', {
    params: { session_id: sessionId },
  })
  return response.data
}
