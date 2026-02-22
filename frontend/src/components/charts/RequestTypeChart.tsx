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

// Maps both English and Russian request type labels to colors
const TYPE_COLORS: Record<string, string> = {
  Complaint: '#f43f5e',
  DataChange: '#3b82f6',
  Consultation: '#14b8a6',
  Claim: '#f97316',
  AppMalfunction: '#a855f7',
  FraudulentActivity: '#ec4899',
  Spam: '#6b7280',
  // Russian equivalents
  'Жалоба': '#f43f5e',
  'ИзменениеДанных': '#3b82f6',
  'Консультация': '#14b8a6',
  'Претензия': '#f97316',
  'СбойПриложения': '#a855f7',
  'МошенническаяДеятельность': '#ec4899',
  'Спам': '#6b7280',
}

const TOOLTIP_STYLE = {
  background: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  fontSize: 12,
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
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval={0}
            angle={-30}
            textAnchor="end"
            height={50}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            itemStyle={{ color: '#f1f5f9' }}
            labelStyle={{ color: '#94a3b8', marginBottom: 2 }}
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
