import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { DistributionBucket } from '../../types/analytics'

const SENTIMENT_COLORS: Record<string, string> = {
  Positive: '#10b981',
  Neutral: '#f59e0b',
  Negative: '#f43f5e',
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
            contentStyle={{
              background: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb',
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => [
              `${value} tickets`,
              name,
            ]}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: '#9ca3af', fontSize: 11 }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
