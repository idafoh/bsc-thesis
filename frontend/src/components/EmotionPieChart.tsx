import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import type { AnalysisResult, EmotionType } from '../types'

interface EmotionPieChartProps {
  data: AnalysisResult
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

const EMOTION_LABELS: Record<EmotionType, string> = {
  happiness: 'Happiness',
  sadness: 'Sadness',
  anger: 'Anger',
  fear: 'Fear',
  disgust: 'Disgust',
  surprise: 'Surprise',
  neutral: 'Neutral',
}

export default function EmotionPieChart({ data }: EmotionPieChartProps) {
  const chartData = (Object.entries(data.summary.average_scores) as [EmotionType, number][])
    .map(([emotion, value]) => ({
      name: EMOTION_LABELS[emotion],
      value: value,
      emotion: emotion,
    }))
    .filter((item) => item.value > 0.01)
    .sort((a, b) => b.value - a.value)

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Emotion Distribution
      </h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) =>
                percent > 0.05 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
              }
              labelLine={false}
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.emotion}
                  fill={EMOTION_COLORS[entry.emotion]}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value) => <span className="text-sm">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
