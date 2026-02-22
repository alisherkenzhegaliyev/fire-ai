import { useQuery } from '@tanstack/react-query'
import { fetchManagers, fetchManagersFromDb } from '../api/managers.api'
import { useAppStore } from '../store/appStore'

export function useManagers() {
  const { phase, sessionId, dbMode } = useAppStore()

  return useQuery({
    queryKey: ['managers', dbMode ? '__db__' : sessionId],
    queryFn: () => (dbMode ? fetchManagersFromDb() : fetchManagers(sessionId!)),
    enabled: phase === 'dashboard' && (dbMode || sessionId != null),
    staleTime: Infinity,
  })
}
