import { useQuery } from '@tanstack/react-query'
import { fetchManagers } from '../api/managers.api'
import { useAppStore } from '../store/appStore'

export function useManagers() {
  const { phase, sessionId, dbMode } = useAppStore()

  return useQuery({
    queryKey: ['managers', dbMode ? '__db__' : sessionId],
    // In DB mode there are no managers (CSV-only data) — return empty list
    queryFn: () => (dbMode ? Promise.resolve([]) : fetchManagers(sessionId!)),
    enabled: phase === 'dashboard' && (dbMode || sessionId != null),
    staleTime: Infinity,
  })
}
