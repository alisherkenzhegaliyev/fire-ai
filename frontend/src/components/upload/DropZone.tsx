import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import clsx from 'clsx'

interface DropZoneProps {
  onFile: (file: File) => void
  disabled?: boolean
}

export function DropZone({ onFile, disabled }: DropZoneProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFile(accepted[0])
    },
    [onFile]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
    disabled,
  })

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-12 py-16 cursor-pointer transition-all duration-200',
        isDragReject
          ? 'border-rose-500 bg-rose-500/5'
          : isDragActive
          ? 'border-indigo-400 bg-indigo-500/10 scale-[1.02]'
          : 'border-gray-600 bg-gray-800/50 hover:border-indigo-500 hover:bg-gray-800',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />

      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-700 mb-5">
        {isDragReject ? (
          <svg className="h-8 w-8 text-rose-400" viewBox="0 0 24 24" fill="currentColor">
            <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className={clsx('h-8 w-8', isDragActive ? 'text-indigo-400' : 'text-gray-400')} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        )}
      </div>

      {isDragReject ? (
        <p className="text-rose-400 font-medium text-center">Only CSV files are accepted</p>
      ) : isDragActive ? (
        <p className="text-indigo-300 font-medium text-center">Drop your CSV file here</p>
      ) : (
        <>
          <p className="text-base font-medium text-gray-200 text-center">
            Drag & drop your CSV file here
          </p>
          <p className="mt-1.5 text-sm text-gray-400 text-center">
            or{' '}
            <span className="text-indigo-400 hover:text-indigo-300 font-medium underline-offset-2 hover:underline">
              browse to choose a file
            </span>
          </p>
          <p className="mt-4 text-xs text-gray-500">Accepts .csv files only</p>
        </>
      )}
    </div>
  )
}
