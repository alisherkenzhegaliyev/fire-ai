export const SENTIMENT_COLORS = {
  Positive: '#10b981',
  Neutral: '#f59e0b',
  Negative: '#f43f5e',
} as const

export const SEGMENT_COLORS = {
  VIP: '#a855f7',
  Priority: '#f97316',
  Mass: '#3b82f6',
} as const

export const REQUEST_TYPE_COLORS = {
  Complaint: '#f43f5e',
  DataChange: '#3b82f6',
  Consultation: '#14b8a6',
  Claim: '#f97316',
  AppMalfunction: '#ef4444',
  FraudulentActivity: '#ec4899',
  Spam: '#6b7280',
} as const

export const LANGUAGE_LABELS = {
  KZ: 'Kazakh',
  ENG: 'English',
  RU: 'Russian',
} as const

export const OFFICE_COORDINATES = {
  Astana: [51.1801, 71.446] as [number, number],
  Almaty: [43.238, 76.889] as [number, number],
}

export const DEFAULT_MAP_CENTER: [number, number] = [47.0, 65.0]
