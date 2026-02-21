import { useQuery } from '@tanstack/react-query'
import { fetchManagers } from '../api/managers.api'
import { useAppStore } from '../store/appStore'

export function useManagers() {
  const { phase, sessionId } = useAppStore()

  return useQuery({
    queryKey: ['managers', sessionId],
    queryFn: () => fetchManagers(sessionId!),
    enabled: phase === 'dashboard' && sessionId != null,
    staleTime: Infinity,
  })
}
