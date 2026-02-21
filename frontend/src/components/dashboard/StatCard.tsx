import clsx from 'clsx'

interface StatCardProps {
  label: string
  value: string | number
  subtext?: string
  icon: React.ReactNode
  accent?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'purple'
}

const ACCENT_CLASSES = {
  indigo: 'bg-indigo-500/15 text-indigo-400',
  emerald: 'bg-emerald-500/15 text-emerald-400',
  amber: 'bg-amber-500/15 text-amber-400',
  rose: 'bg-rose-500/15 text-rose-400',
  purple: 'bg-purple-500/15 text-purple-400',
}

export function StatCard({ label, value, subtext, icon, accent = 'indigo' }: StatCardProps) {
  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/60 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</p>
          <p className="mt-1.5 text-2xl font-bold text-white truncate">{value}</p>
          {subtext && <p className="mt-1 text-xs text-gray-500">{subtext}</p>}
        </div>
        <div className={clsx('flex h-10 w-10 shrink-0 items-center justify-center rounded-lg', ACCENT_CLASSES[accent])}>
          {icon}
        </div>
      </div>
    </div>
  )
}
