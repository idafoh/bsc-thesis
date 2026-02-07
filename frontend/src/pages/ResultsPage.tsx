import { useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAnalysisResults } from '../hooks/useAnalysisResults'
import EmotionTimeline from '../components/EmotionTimeline'
import EmotionSummary from '../components/EmotionSummary'
import EmotionPieChart from '../components/EmotionPieChart'
import ExportButtons from '../components/ExportButtons'
import { getVideoUrl } from '../services/api'

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { data, isLoading, error } = useAnalysisResults(jobId ?? null)
  const [currentTime, setCurrentTime] = useState<number>(0)
  const [isPortrait, setIsPortrait] = useState<boolean>(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      const { videoWidth, videoHeight } = videoRef.current
      setIsPortrait(videoHeight > videoWidth)
    }
  }

  const handleTimelineClick = (time: number) => {
    setCurrentTime(time)
    if (videoRef.current) {
      videoRef.current.currentTime = time
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <svg
            className="animate-spin h-12 w-12 text-indigo-600 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h2 className="mt-4 text-lg font-medium text-gray-900">
          Results not found
        </h2>
        <p className="mt-2 text-gray-600">
          The analysis results could not be loaded.
        </p>
        <Link
          to="/"
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          Upload a new video
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Link
            to="/"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to upload
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">
            Analysis Results
          </h1>
          <p className="text-gray-600">{data.video_filename}</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <ExportButtons jobId={jobId!} />
        </div>
      </div>

      {isPortrait ? (
        <>
          {/* Portrait Layout: Video + Timeline side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border p-6 h-full">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Video</h3>
                <video
                  ref={videoRef}
                  src={getVideoUrl(jobId!)}
                  controls
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  className="w-full rounded-lg"
                >
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
            <div className="lg:col-span-2">
              <EmotionTimeline
                data={data}
                currentTime={currentTime}
                onTimeClick={handleTimelineClick}
              />
            </div>
          </div>

          {/* Summary and Pie Chart below */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <EmotionSummary data={data} />
            <EmotionPieChart data={data} />
          </div>
        </>
      ) : (
        <>
          {/* Landscape Layout: Video on top */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Video</h3>
            <video
              ref={videoRef}
              src={getVideoUrl(jobId!)}
              controls
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              className="w-full max-h-96 rounded-lg"
            >
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Timeline Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EmotionTimeline
                data={data}
                currentTime={currentTime}
                onTimeClick={handleTimelineClick}
              />
            </div>
            <div className="space-y-6">
              <EmotionSummary data={data} />
              <EmotionPieChart data={data} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
