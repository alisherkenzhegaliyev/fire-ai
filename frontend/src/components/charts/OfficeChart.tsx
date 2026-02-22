import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { DistributionBucket } from '../../types/analytics'

// Cycle through a palette for offices/cities
const PALETTE = ['#6366f1', '#10b981', '#f59e0b', '#3b82f6', '#a855f7', '#14b8a6', '#f43f5e']

const TOOLTIP_STYLE = {
  background: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  fontSize: 12,
}

interface OfficeChartProps {
  data: DistributionBucket[]
}

export function OfficeChart({ data }: OfficeChartProps) {
  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 p-4">
      <p className="text-sm font-semibold text-white mb-4">Tickets by Office</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 20, left: 8, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: '#cbd5e1', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={80}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            itemStyle={{ color: '#f1f5f9' }}
            labelStyle={{ color: '#94a3b8', marginBottom: 2 }}
            formatter={(value: number, _name: string, props) => [
              `${value} (${props.payload.percentage}%)`,
              'Tickets',
            ]}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={entry.label} fill={PALETTE[i % PALETTE.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
