import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation } from '@tanstack/react-query'
import { uploadVideo } from '../services/api'

interface VideoUploadProps {
  onUploadComplete: (jobId: string) => void
}

const ACCEPTED_FORMATS = {
  'video/mp4': ['.mp4'],
  'video/avi': ['.avi'],
  'video/quicktime': ['.mov'],
  'video/webm': ['.webm'],
}

const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB

export default function VideoUpload({ onUploadComplete }: VideoUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0)

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadVideo(file, setUploadProgress),
    onSuccess: (data) => {
      onUploadComplete(data.job_id)
      setUploadProgress(0)
    },
  })

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (file) {
        uploadMutation.mutate(file)
      }
    },
    [uploadMutation]
  )

  const { getRootProps, getInputProps, isDragActive, fileRejections } =
    useDropzone({
      onDrop,
      accept: ACCEPTED_FORMATS,
      maxSize: MAX_FILE_SIZE,
      maxFiles: 1,
      disabled: uploadMutation.isPending,
    })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploadMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        {uploadMutation.isPending ? (
          <div className="space-y-4">
            <div className="flex justify-center">
              <svg
                className="animate-spin h-10 w-10 text-indigo-600"
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
            </div>
            <div>
              <p className="text-sm text-gray-600">Uploading video...</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive
                  ? 'Drop your video here'
                  : 'Drag and drop your video here'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse your files
              </p>
            </div>
            <p className="text-xs text-gray-400">
              Supported formats: MP4, AVI, MOV, WebM (max 500MB)
            </p>
          </div>
        )}
      </div>

      {fileRejections.length > 0 && (
        <div className="mt-2 text-sm text-red-600">
          {fileRejections[0].errors.map((error) => (
            <p key={error.code}>{error.message}</p>
          ))}
        </div>
      )}

      {uploadMutation.isError && (
        <div className="mt-2 text-sm text-red-600">
          Upload failed. Please try again.
        </div>
      )}
    </div>
  )
}
