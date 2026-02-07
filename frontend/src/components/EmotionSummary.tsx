import type { AnalysisResult, EmotionType } from '../types'

interface EmotionSummaryProps {
  data: AnalysisResult
}

const EMOTION_LABELS: Record<EmotionType, string> = {
  happiness: 'Happiness',
  sadness: 'Sadness',
  anger: 'Anger',
  fear: 'Fear',
  disgust: 'Disgust',
  surprise: 'Surprise',
  neutral: 'Neutral',
}

const EMOTION_COLORS: Record<EmotionType, string> = {
  happiness: '#FFD700',
  sadness: '#4169E1',
  anger: '#DC143C',
  fear: '#8B008B',
  disgust: '#228B22',
  surprise: '#FF8C00',
  neutral: '#808080',
}

export default function EmotionSummary({ data }: EmotionSummaryProps) {
  const { summary } = data
  const sortedEmotions = (Object.entries(summary.average_scores) as [EmotionType, number][])
    .sort(([, a], [, b]) => b - a)

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Analysis Summary
      </h3>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-500">Video Duration</p>
          <p className="text-2xl font-semibold text-gray-900">
            {data.duration.toFixed(1)}s
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Dominant Emotion</p>
          <span
            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-1"
            style={{
              backgroundColor: `${EMOTION_COLORS[summary.dominant_emotion]}20`,
              color: EMOTION_COLORS[summary.dominant_emotion],
            }}
          >
            {EMOTION_LABELS[summary.dominant_emotion]}
          </span>
        </div>

        <div>
          <p className="text-sm text-gray-500 mb-2">Average Emotion Scores</p>
          <div className="space-y-2">
            {sortedEmotions.map(([emotion, score]) => (
              <div key={emotion}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">
                    {EMOTION_LABELS[emotion]}
                  </span>
                  <span className="font-medium text-gray-900">
                    {(score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${score * 100}%`,
                      backgroundColor: EMOTION_COLORS[emotion],
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t text-sm text-gray-500">
          <p>Total Frames: {data.total_frames}</p>
          <p>FPS: {data.fps.toFixed(1)}</p>
        </div>
      </div>
    </div>
  )
}
