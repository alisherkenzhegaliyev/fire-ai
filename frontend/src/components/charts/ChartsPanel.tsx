import { RequestTypeChart } from './RequestTypeChart'
import { SentimentChart } from './SentimentChart'
import { OfficeChart } from './OfficeChart'
import type { AnalyticsData } from '../../types/analytics'

interface ChartsPanelProps {
  data: AnalyticsData
}

export function ChartsPanel({ data }: ChartsPanelProps) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <RequestTypeChart data={data.byRequestType} />
      <SentimentChart data={data.bySentiment} />
      <OfficeChart data={data.byOffice} />
    </div>
  )
}
