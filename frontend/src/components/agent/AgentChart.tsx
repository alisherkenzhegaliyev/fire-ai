import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { AgentChartPayload } from '../../types/agent'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#3b82f6', '#a855f7', '#14b8a6']

interface AgentChartProps {
  payload: AgentChartPayload
}

export function AgentChart({ payload }: AgentChartProps) {
  const { type, title, data, xKey, yKey } = payload

  const commonAxis = {
    tick: { fill: '#9ca3af', fontSize: 10 },
    axisLine: false,
    tickLine: false,
  }

  const tooltipStyle = {
    contentStyle: {
      background: '#1f2937',
      border: '1px solid #374151',
      borderRadius: '8px',
      color: '#f9fafb',
      fontSize: 11,
    },
  }

  return (
    <div className="mt-2 rounded-xl border border-gray-700/40 bg-gray-900/60 p-3">
      <p className="text-xs font-medium text-gray-300 mb-3">{title}</p>
      <ResponsiveContainer width="100%" height={180}>
        {type === 'pie' ? (
          <PieChart>
            <Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" outerRadius={65} paddingAngle={2}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip {...tooltipStyle} />
            <Legend iconSize={8} formatter={(v) => <span style={{ color: '#9ca3af', fontSize: 10 }}>{v}</span>} />
          </PieChart>
        ) : type === 'line' ? (
          <LineChart data={data} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey={xKey} {...commonAxis} />
            <YAxis {...commonAxis} />
            <Tooltip {...tooltipStyle} />
            <Line type="monotone" dataKey={yKey} stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        ) : type === 'scatter' ? (
          <ScatterChart margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey={xKey} {...commonAxis} />
            <YAxis dataKey={yKey} {...commonAxis} />
            <Tooltip {...tooltipStyle} />
            <Scatter data={data} fill="#6366f1" />
          </ScatterChart>
        ) : (
          <BarChart data={data} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
            <XAxis dataKey={xKey} {...commonAxis} />
            <YAxis {...commonAxis} />
            <Tooltip {...tooltipStyle} />
            <Bar dataKey={yKey} radius={[3, 3, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
