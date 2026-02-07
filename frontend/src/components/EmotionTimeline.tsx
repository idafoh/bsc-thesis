import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { AnalysisResult, EmotionType } from '../types'

interface EmotionTimelineProps {
  data: AnalysisResult
  currentTime?: number
  onTimeClick?: (time: number) => void
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

export default function EmotionTimeline({
  data,
  currentTime,
  onTimeClick,
}: EmotionTimelineProps) {
  const chartData = data.summary.emotion_timeline.map((point) => ({
    timestamp: point.timestamp,
    ...point.emotions,
  }))

  const handleClick = (e: { activePayload?: Array<{ payload: { timestamp: number } }> }) => {
    if (onTimeClick && e.activePayload?.[0]) {
      onTimeClick(e.activePayload[0].payload.timestamp)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Emotion Timeline
      </h3>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            onClick={handleClick}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="timestamp"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(value) => value.toFixed(1)}
              tick={{ fontSize: 12 }}
              label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              tick={{ fontSize: 12 }}
              label={{ value: 'Confidence', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
              labelFormatter={(label) => `Time: ${Number(label).toFixed(1)}s`}
            />
            <Legend verticalAlign="top" height={36} />

            {(Object.keys(EMOTION_COLORS) as EmotionType[]).map((emotion) => (
              <Line
                key={emotion}
                type="monotone"
                dataKey={emotion}
                stroke={EMOTION_COLORS[emotion]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}

            {currentTime !== undefined && (
              <ReferenceLine
                x={currentTime}
                stroke="#000"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
