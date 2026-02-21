import { useQuery } from '@tanstack/react-query'
import { fetchAnalytics } from '../api/analytics.api'
import { useAppStore } from '../store/appStore'

export function useAnalytics() {
  const { phase, sessionId } = useAppStore()

  return useQuery({
    queryKey: ['analytics', sessionId],
    queryFn: () => fetchAnalytics(sessionId!),
    enabled: phase === 'dashboard' && sessionId != null,
    staleTime: Infinity,
  })
}
