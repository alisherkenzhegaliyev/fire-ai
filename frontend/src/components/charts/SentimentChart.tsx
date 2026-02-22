import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { DistributionBucket } from '../../types/analytics'

// Maps both English (session) and Russian (DB) sentiment labels to colors
const SENTIMENT_COLORS: Record<string, string> = {
  Positive: '#10b981',
  Neutral: '#f59e0b',
  Negative: '#f43f5e',
  // Russian values stored in DB
  'Позитивный': '#10b981',
  'Нейтральный': '#f59e0b',
  'Негативный': '#f43f5e',
}

const TOOLTIP_STYLE = {
  background: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  fontSize: 12,
}

interface SentimentChartProps {
  data: DistributionBucket[]
}

export function SentimentChart({ data }: SentimentChartProps) {
  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 p-4">
      <p className="text-sm font-semibold text-white mb-4">Sentiment Distribution</p>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={55}
            outerRadius={85}
            dataKey="count"
            nameKey="label"
            paddingAngle={3}
          >
            {data.map((entry) => (
              <Cell
                key={entry.label}
                fill={SENTIMENT_COLORS[entry.label] ?? '#6366f1'}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            itemStyle={{ color: '#f1f5f9' }}
            labelStyle={{ color: '#94a3b8', marginBottom: 2 }}
            formatter={(value: number, name: string) => [
              `${value} tickets`,
              name,
            ]}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: '#cbd5e1', fontSize: 11 }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
