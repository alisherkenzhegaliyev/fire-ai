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

const TYPE_COLORS: Record<string, string> = {
  Complaint: '#f43f5e',
  DataChange: '#3b82f6',
  Consultation: '#14b8a6',
  Claim: '#f97316',
  AppMalfunction: '#ef4444',
  FraudulentActivity: '#ec4899',
  Spam: '#6b7280',
}

interface RequestTypeChartProps {
  data: DistributionBucket[]
}

export function RequestTypeChart({ data }: RequestTypeChartProps) {
  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 p-4">
      <p className="text-sm font-semibold text-white mb-4">Request Types</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval={0}
            angle={-30}
            textAnchor="end"
            height={50}
          />
          <YAxis
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              background: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb',
              fontSize: 12,
            }}
            formatter={(value: number, _name: string, props) => [
              `${value} (${props.payload.percentage}%)`,
              'Count',
            ]}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.label}
                fill={TYPE_COLORS[entry.label] ?? '#6366f1'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
