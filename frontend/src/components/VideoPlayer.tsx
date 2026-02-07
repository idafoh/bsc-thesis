import { useRef, useEffect } from 'react'

interface VideoPlayerProps {
  src: string
  currentTime?: number
  onTimeUpdate?: (time: number) => void
}

export default function VideoPlayer({
  src,
  currentTime,
  onTimeUpdate,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current && currentTime !== undefined) {
      const diff = Math.abs(videoRef.current.currentTime - currentTime)
      if (diff > 0.5) {
        videoRef.current.currentTime = currentTime
      }
    }
  }, [currentTime])

  const handleTimeUpdate = () => {
    if (videoRef.current && onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime)
    }
  }

  return (
    <div className="bg-black rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        src={src}
        controls
        onTimeUpdate={handleTimeUpdate}
        className="w-full h-auto max-h-96 object-contain"
      >
        Your browser does not support the video tag.
      </video>
    </div>
  )
}
