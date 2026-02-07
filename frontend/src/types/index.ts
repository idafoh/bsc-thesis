export type EmotionType =
  | 'happiness'
  | 'sadness'
  | 'anger'
  | 'fear'
  | 'disgust'
  | 'surprise'
  | 'neutral'

export interface EmotionScores {
  happiness: number
  sadness: number
  anger: number
  fear: number
  disgust: number
  surprise: number
  neutral: number
}

export interface FrameResult {
  frame_number: number
  timestamp: number
  face_detected: boolean
  emotions: EmotionScores
  dominant_emotion: EmotionType
  confidence: number
}

export interface AnalysisResult {
  job_id: string
  video_filename: string
  total_frames: number
  fps: number
  duration: number
  frames: FrameResult[]
  summary: {
    dominant_emotion: EmotionType
    average_scores: EmotionScores
    emotion_timeline: Array<{
      timestamp: number
      emotions: EmotionScores
    }>
  }
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface Job {
  id: string
  filename: string
  status: JobStatus
  progress: number
  created_at: string
  completed_at?: string
  error?: string
}

export interface UploadResponse {
  job_id: string
  message: string
}

export interface ApiError {
  detail: string
}
