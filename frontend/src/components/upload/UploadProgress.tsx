interface UploadProgressProps {
  percentage: number
  fileName: string
}

export function UploadProgress({ percentage, fileName }: UploadProgressProps) {
  return (
    <div className="w-full max-w-md space-y-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/20 mx-auto animate-pulse-slow">
        <svg className="h-8 w-8 text-indigo-400 animate-bounce" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
      </div>

      <div>
        <p className="text-base font-medium text-gray-200">Uploading & Processing</p>
        <p className="mt-1 text-sm text-gray-400 truncate max-w-xs mx-auto">{fileName}</p>
      </div>

      <div className="w-full rounded-full bg-gray-700 h-2 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="text-sm text-gray-400">
        {percentage < 100 ? `Uploading… ${percentage}%` : 'Processing with AI…'}
      </p>
    </div>
  )
}
