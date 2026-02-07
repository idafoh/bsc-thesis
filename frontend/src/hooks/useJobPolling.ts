import { useQuery } from '@tanstack/react-query'
import { getJobStatus } from '../services/api'
import type { Job } from '../types'

export function useJobPolling(jobId: string | null, enabled: boolean = true) {
  return useQuery<Job>({
    queryKey: ['job', jobId],
    queryFn: () => getJobStatus(jobId!),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false
      }
      return 2000
    },
  })
}
