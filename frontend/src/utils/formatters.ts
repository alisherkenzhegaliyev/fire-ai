export function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString([], {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value)
}
