import clsx from 'clsx'
import type { RequestType, Sentiment, Segment, Language } from '../../types/ticket'

type BadgeVariant = RequestType | Sentiment | Segment | Language | string

const VARIANT_CLASSES: Record<string, string> = {
  // Sentiment
  Positive: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  Neutral: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  Negative: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  // Segment
  VIP: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  Priority: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  Mass: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  // Language
  KZ: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  ENG: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  RU: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  // Request types
  Complaint: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  DataChange: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  Consultation: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
  Claim: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  AppMalfunction: 'bg-red-500/20 text-red-300 border-red-500/30',
  FraudulentActivity: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  Spam: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
}

interface BadgeProps {
  value: BadgeVariant
  className?: string
}

export function Badge({ value, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
        VARIANT_CLASSES[value] ?? 'bg-gray-500/20 text-gray-300 border-gray-500/30',
        className
      )}
    >
      {value}
    </span>
  )
}
