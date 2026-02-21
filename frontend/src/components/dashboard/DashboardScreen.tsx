import { useState } from 'react'
import { StatsPanel } from './StatsPanel'
import { AssignmentChain } from './AssignmentChain'
import { TicketsTable } from './TicketsTable'
import { TicketModal } from './TicketModal'
import { ManagersTable } from './ManagersTable'
import { ChartsPanel } from '../charts/ChartsPanel'
import { GeoMapPanel } from '../map/GeoMapPanel'
import { Spinner } from '../shared/Spinner'
import { ErrorBanner } from '../shared/ErrorBanner'
import { useTickets } from '../../hooks/useTickets'
import { useManagers } from '../../hooks/useManagers'
import { useAnalytics } from '../../hooks/useAnalytics'
import { useAppStore } from '../../store/appStore'
import type { Ticket } from '../../types/ticket'

export function DashboardScreen() {
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)
  const [modalTicket, setModalTicket] = useState<Ticket | null>(null)
  const nlpTiming = useAppStore((s) => s.nlpTiming)

  const ticketsQuery = useTickets()
  const managersQuery = useManagers()
  const analyticsQuery = useAnalytics()

  const isLoading = ticketsQuery.isLoading || managersQuery.isLoading || analyticsQuery.isLoading
  const isError = ticketsQuery.isError || managersQuery.isError || analyticsQuery.isError
  const errorMsg =
    (ticketsQuery.error as Error | null)?.message ??
    (managersQuery.error as Error | null)?.message ??
    (analyticsQuery.error as Error | null)?.message

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="lg" />
          <p className="text-sm text-gray-400">Loading dashboard data…</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="w-full max-w-md">
          <ErrorBanner message={errorMsg ?? 'Failed to load dashboard data'} />
        </div>
      </div>
    )
  }

  const tickets = ticketsQuery.data ?? []
  const managers = managersQuery.data ?? []
  const analytics = analyticsQuery.data!

  return (
    <>
      <div className="h-full overflow-y-auto">
        <div className="max-w-screen-2xl mx-auto px-4 py-5 space-y-5">
          {/* Stats */}
          <StatsPanel data={analytics} nlpTiming={nlpTiming} />

          {/* Charts */}
          <ChartsPanel data={analytics} />

          {/* AI Summary — full width */}
          <AssignmentChain ticket={selectedTicket} />

          {/* Managers + Tickets side by side */}
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-5">
            <div className="xl:col-span-2">
              <ManagersTable managers={managers} />
            </div>
            <div className="xl:col-span-3">
              <TicketsTable
                tickets={tickets}
                selectedId={selectedTicket?.id ?? null}
                onSelect={setSelectedTicket}
                onViewDetails={setModalTicket}
              />
            </div>
          </div>

          {/* Map at the bottom */}
          <GeoMapPanel tickets={tickets} />
        </div>
      </div>

      {modalTicket && (
        <TicketModal ticket={modalTicket} onClose={() => setModalTicket(null)} />
      )}
    </>
  )
}
