from pathlib import Path
from typing import Callable
import cv2
import numpy as np
import mediapipe as mp
from fer import FER
from collections import deque


class EmotionDetector:
    EMOTION_LABELS = [
        "happiness",
        "sadness",
        "anger",
        "fear",
        "disgust",
        "surprise",
        "neutral",
    ]

    # Map FER emotion names to our standardized names
    EMOTION_MAP = {
        "happy": "happiness",
        "sad": "sadness",
        "angry": "anger",
        "fear": "fear",
        "disgust": "disgust",
        "surprise": "surprise",
        "neutral": "neutral",
    }

    def __init__(
        self,
        frame_sample_rate: int = 5,
        smoothing_window: int = 5,
    ):
        self.frame_sample_rate = frame_sample_rate
        self.smoothing_window = smoothing_window

        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1,  # Full range model for better detection
            min_detection_confidence=0.5,
        )

        # Initialize FER emotion detector
        self.emotion_detector = FER(mtcnn=False)

        # Smoothing buffers for each emotion
        self.emotion_buffers: dict[str, deque] = {
            emotion: deque(maxlen=smoothing_window)
            for emotion in self.EMOTION_LABELS
        }

    def _detect_largest_face(self, frame: np.ndarray) -> tuple[bool, tuple | None]:
        """Detect faces and return the largest one."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(rgb_frame)

        if not results.detections:
            return False, None

        # Find the largest face by bounding box area
        h, w = frame.shape[:2]
        largest_face = None
        largest_area = 0

        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            face_w = int(bbox.width * w)
            face_h = int(bbox.height * h)

            area = face_w * face_h
            if area > largest_area:
                largest_area = area
                largest_face = (x, y, face_w, face_h)

        return True, largest_face

    def _analyze_emotions(self, frame: np.ndarray) -> dict[str, float]:
        """Analyze emotions in frame using FER."""
        try:
            emotions = self.emotion_detector.detect_emotions(frame)

            if emotions and len(emotions) > 0:
                # Get the first (largest) face's emotions
                raw_emotions = emotions[0].get("emotions", {})

                # Map to standardized emotion names
                standardized = {}
                for fer_name, our_name in self.EMOTION_MAP.items():
                    standardized[our_name] = raw_emotions.get(fer_name, 0.0)

                return standardized

        except Exception:
            pass

        # Return zero scores if detection fails
        return {emotion: 0.0 for emotion in self.EMOTION_LABELS}

    def _smooth_emotions(self, emotions: dict[str, float]) -> dict[str, float]:
        """Apply temporal smoothing using sliding window average."""
        smoothed = {}

        for emotion, score in emotions.items():
            self.emotion_buffers[emotion].append(score)
            buffer = self.emotion_buffers[emotion]
            smoothed[emotion] = sum(buffer) / len(buffer)

        return smoothed

    def _get_dominant_emotion(
        self, emotions: dict[str, float]
    ) -> tuple[str, float]:
        """Get the emotion with highest confidence."""
        if not emotions:
            return "neutral", 0.0

        dominant = max(emotions.items(), key=lambda x: x[1])
        return dominant[0], dominant[1]

    def _reset_buffers(self):
        """Clear smoothing buffers."""
        for buffer in self.emotion_buffers.values():
            buffer.clear()

    def process_video(
        self,
        video_path: str | Path,
        progress_callback: Callable[[int], None] | None = None,
    ) -> dict:
        """Process video and return emotion analysis results."""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            self._reset_buffers()

            frame_results = []
            processed_count = 0
            frame_number = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Sample frames
                if frame_number % self.frame_sample_rate == 0:
                    timestamp = frame_number / fps if fps > 0 else 0

                    # Detect face
                    face_detected, face_bbox = self._detect_largest_face(frame)

                    if face_detected and face_bbox:
                        # Crop face region for emotion analysis
                        x, y, w, h = face_bbox
                        # Add padding
                        pad = int(min(w, h) * 0.2)
                        x1 = max(0, x - pad)
                        y1 = max(0, y - pad)
                        x2 = min(frame.shape[1], x + w + pad)
                        y2 = min(frame.shape[0], y + h + pad)

                        face_roi = frame[y1:y2, x1:x2]
                        raw_emotions = self._analyze_emotions(face_roi)
                    else:
                        raw_emotions = {e: 0.0 for e in self.EMOTION_LABELS}

                    # Apply smoothing
                    smoothed_emotions = self._smooth_emotions(raw_emotions)
                    dominant_emotion, confidence = self._get_dominant_emotion(
                        smoothed_emotions
                    )

                    frame_results.append(
                        {
                            "frame_number": frame_number,
                            "timestamp": round(timestamp, 3),
                            "face_detected": face_detected,
                            "emotions": {
                                k: round(v, 4) for k, v in smoothed_emotions.items()
                            },
                            "dominant_emotion": dominant_emotion,
                            "confidence": round(confidence, 4),
                        }
                    )

                    processed_count += 1

                    # Update progress
                    if progress_callback and total_frames > 0:
                        progress = int((frame_number / total_frames) * 100)
                        progress_callback(min(progress, 99))

                frame_number += 1

        finally:
            cap.release()

        # Calculate summary statistics
        summary = self._calculate_summary(frame_results, duration)

        return {
            "job_id": video_path.stem,
            "video_filename": video_path.name,
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration": round(duration, 2),
            "frames": frame_results,
            "summary": summary,
        }

    def _calculate_summary(
        self, frame_results: list[dict], duration: float
    ) -> dict:
        """Calculate summary statistics from frame results."""
        if not frame_results:
            return {
                "dominant_emotion": "neutral",
                "average_scores": {e: 0.0 for e in self.EMOTION_LABELS},
                "emotion_timeline": [],
            }

        # Calculate average scores
        emotion_sums = {e: 0.0 for e in self.EMOTION_LABELS}
        face_detected_count = 0

        for frame in frame_results:
            if frame["face_detected"]:
                face_detected_count += 1
                for emotion, score in frame["emotions"].items():
                    emotion_sums[emotion] += score

        if face_detected_count > 0:
            average_scores = {
                e: round(s / face_detected_count, 4)
                for e, s in emotion_sums.items()
            }
        else:
            average_scores = {e: 0.0 for e in self.EMOTION_LABELS}

        # Find overall dominant emotion
        dominant_emotion = max(average_scores.items(), key=lambda x: x[1])[0]

        # Create downsampled timeline for visualization (max 100 points)
        timeline = []
        step = max(1, len(frame_results) // 100)
        for i in range(0, len(frame_results), step):
            frame = frame_results[i]
            timeline.append(
                {
                    "timestamp": frame["timestamp"],
                    "emotions": frame["emotions"],
                }
            )

        return {
            "dominant_emotion": dominant_emotion,
            "average_scores": average_scores,
            "emotion_timeline": timeline,
        }
