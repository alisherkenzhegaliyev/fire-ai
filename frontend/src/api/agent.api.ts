import client from './client'
import type { AgentQueryRequest, AgentQueryResponse } from '../types/agent'

export async function sendAgentQuery(
  payload: AgentQueryRequest
): Promise<AgentQueryResponse> {
  const response = await client.post<AgentQueryResponse>('/api/agent/query', payload)
  return response.data
}
