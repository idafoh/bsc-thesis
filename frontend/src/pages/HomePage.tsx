import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import VideoUpload from '../components/VideoUpload'
import JobStatus from '../components/JobStatus'
import RecentJobs from '../components/RecentJobs'
import { useJobPolling } from '../hooks/useJobPolling'

export default function HomePage() {
  const navigate = useNavigate()
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)

  const { data: job } = useJobPolling(currentJobId)

  const handleUploadComplete = (jobId: string) => {
    setCurrentJobId(jobId)
  }

  if (job?.status === 'completed') {
    navigate(`/results/${job.id}`)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Emotion Detection in Video
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Upload a video to analyze facial expressions and detect emotions over
          time
        </p>
      </div>

      <div className="space-y-6">
        <VideoUpload onUploadComplete={handleUploadComplete} />

        {job && <JobStatus job={job} />}

        <div className="bg-gray-50 rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            How it works
          </h2>
          <ol className="space-y-3 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                1
              </span>
              <span>Upload a video file (MP4, AVI, MOV, or WebM)</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                2
              </span>
              <span>
                Our system extracts frames and detects faces in the video
              </span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                3
              </span>
              <span>
                Each face is analyzed for 7 emotions: happiness, sadness, anger,
                fear, disgust, surprise, and neutral
              </span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                4
              </span>
              <span>
                View the emotion timeline and export results as CSV or JSON
              </span>
            </li>
          </ol>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>Supported video duration: up to 10 minutes</p>
          <p>Maximum file size: 500MB</p>
        </div>

        <RecentJobs />
      </div>
    </div>
  )
}
