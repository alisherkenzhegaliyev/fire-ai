import { useState, useCallback } from "react";
import { DropZone } from "./DropZone";
import { UploadProgress } from "./UploadProgress";
import { UploadSuccess } from "./UploadSuccess";
import { ErrorBanner } from "../shared/ErrorBanner";
import { uploadCSV } from "../../api/upload.api";
import { useAppStore } from "../../store/appStore";

export function UploadScreen() {
  const {
    uploadStatus,
    uploadProgress,
    uploadError,
    setUploadStatus,
    setUploadProgress,
    setUploadError,
    setSessionId,
    setPhase,
    resetUpload,
    setNlpTiming,
    enterDbMode,
  } = useAppStore();

  const [fileName, setFileName] = useState("");
  const [successData, setSuccessData] = useState<{
    ticketCount: number;
    managerCount: number;
  } | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setFileName(file.name);
      setUploadStatus("uploading");
      setUploadError(null);
      setUploadProgress(0);

      try {
        const result = await uploadCSV(file, setUploadProgress);
        setSessionId(result.sessionId);
        setNlpTiming({
          totalTime: result.nlpTotalTime,
          avgTime: result.nlpAvgTime,
        });
        setSuccessData({
          ticketCount: result.ticketCount,
          managerCount: result.managerCount,
        });
        setUploadStatus("success");

        setTimeout(() => {
          setPhase("dashboard");
        }, 1800);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setUploadError(message);
        setUploadStatus("error");
      }
    },
    [
      setUploadStatus,
      setUploadProgress,
      setUploadError,
      setSessionId,
      setPhase,
      setNlpTiming,
    ]
  );

  const isIdle = uploadStatus === "idle" || uploadStatus === "error";

  return (
    <div className="flex h-full flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg space-y-8">
        {/* Title */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-white">Upload Ticket Data</h1>
          <p className="text-sm text-gray-400">
            Upload your CSV file containing tickets, managers, and business
            units. The system will analyze and assign each request
            automatically.
          </p>
        </div>

        {/* Main content area */}
        <div className="rounded-2xl border border-gray-700/50 bg-gray-800/40 p-8">
          {isIdle ? (
            <div className="space-y-4">
              <DropZone onFile={handleFile} disabled={false} />
              {uploadStatus === "error" && uploadError && (
                <ErrorBanner message={uploadError} onDismiss={resetUpload} />
              )}
            </div>
          ) : uploadStatus === "uploading" ? (
            <div className="flex items-center justify-center py-4">
              <UploadProgress percentage={uploadProgress} fileName={fileName} />
            </div>
          ) : uploadStatus === "success" && successData ? (
            <div className="flex items-center justify-center py-4">
              <UploadSuccess
                ticketCount={successData.ticketCount}
                managerCount={successData.managerCount}
              />
            </div>
          ) : null}
        </div>

        {/* Database analysis shortcut */}
        {isIdle && (
          <div className="flex flex-col items-center gap-2">
            <div className="flex items-center gap-3 w-full">
              <div className="flex-1 h-px bg-gray-700/60" />
              <span className="text-xs text-gray-600">or</span>
              <div className="flex-1 h-px bg-gray-700/60" />
            </div>
            <button
              onClick={enterDbMode}
              className="flex items-center gap-2.5 rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-5 py-3 text-sm font-medium text-indigo-300 hover:bg-indigo-500/20 hover:border-indigo-400/50 hover:text-indigo-200 transition-all"
            >
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.8}
              >
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path
                  strokeLinecap="round"
                  d="M3 5v14c0 1.657 4.03 3 9 3s9-1.343 9-3V5"
                />
                <path
                  strokeLinecap="round"
                  d="M3 12c0 1.657 4.03 3 9 3s9-1.343 9-3"
                />
              </svg>
              Analyze Existing Database
            </button>
            <p className="text-xs text-gray-600 text-center">
              View analytics from previously processed tickets in the database
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
