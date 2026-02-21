interface UploadSuccessProps {
  ticketCount: number
  managerCount: number
}

export function UploadSuccess({ ticketCount, managerCount }: UploadSuccessProps) {
  return (
    <div className="flex flex-col items-center gap-5 animate-fade-in text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/20">
        <svg className="h-8 w-8 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <div>
        <p className="text-lg font-semibold text-emerald-300">Processing Complete!</p>
        <p className="mt-1 text-sm text-gray-400">
          {ticketCount} tickets and {managerCount} managers loaded
        </p>
      </div>

      <p className="text-xs text-gray-500">Loading dashboard…</p>
    </div>
  )
}
