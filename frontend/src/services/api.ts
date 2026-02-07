import axios from 'axios'
import type { Job, AnalysisResult, UploadResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadVideo = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<UploadResponse>('/videos/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        onProgress(progress)
      }
    },
  })

  return response.data
}

export const getJobStatus = async (jobId: string): Promise<Job> => {
  const response = await api.get<Job>(`/jobs/${jobId}`)
  return response.data
}

export const getResults = async (jobId: string): Promise<AnalysisResult> => {
  const response = await api.get<AnalysisResult>(`/results/${jobId}`)
  return response.data
}

export const exportResults = async (
  jobId: string,
  format: 'csv' | 'json'
): Promise<Blob> => {
  const response = await api.get(`/results/${jobId}/export`, {
    params: { format },
    responseType: 'blob',
  })
  return response.data
}

export const deleteJob = async (jobId: string): Promise<void> => {
  await api.delete(`/jobs/${jobId}`)
}

export const getJobs = async (): Promise<Job[]> => {
  const response = await api.get<Job[]>('/jobs')
  return response.data
}

export const getVideoUrl = (jobId: string): string => {
  return `/api/videos/${jobId}`
}
