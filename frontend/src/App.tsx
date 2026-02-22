import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PageShell } from './components/layout/PageShell'
import { UploadScreen } from './components/upload/UploadScreen'
import { DashboardScreen } from './components/dashboard/DashboardScreen'
import { AgentPanel } from './components/agent/AgentPanel'
import { useAppStore } from './store/appStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function AppContent() {
  const { phase, agentPanelOpen } = useAppStore()

  return (
    <PageShell>
      {phase === 'upload' && <UploadScreen />}
      {phase === 'dashboard' && <DashboardScreen />}
      {agentPanelOpen && <AgentPanel />}
    </PageShell>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}
