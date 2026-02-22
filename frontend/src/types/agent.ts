export type ChartType = 'bar' | 'pie' | 'line' | 'scatter'

export interface AgentChartPayload {
  type: ChartType
  title: string
  data: Record<string, unknown>[]
  xKey: string
  yKey: string
  colorKey?: string
}

export interface AgentQueryRequest {
  question: string
  sessionId: string
}

export interface AgentQueryResponse {
  answer: string
  chartData?: AgentChartPayload
  htmlArtifact?: string
}
