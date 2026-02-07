import { useQuery } from '@tanstack/react-query'
import { getResults } from '../services/api'
import type { AnalysisResult } from '../types'

export function useAnalysisResults(jobId: string | null, enabled: boolean = true) {
  return useQuery<AnalysisResult>({
    queryKey: ['results', jobId],
    queryFn: () => getResults(jobId!),
    enabled: enabled && !!jobId,
    staleTime: Infinity,
  })
}
