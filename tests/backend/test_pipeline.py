import pytest
import numpy as np

from app.pipeline.emotion_detector import EmotionDetector


class TestEmotionDetector:
    def test_init(self):
        detector = EmotionDetector()
        assert detector.frame_sample_rate == 5
        assert detector.smoothing_window == 5
        assert len(detector.EMOTION_LABELS) == 7

    def test_init_custom_params(self):
        detector = EmotionDetector(frame_sample_rate=10, smoothing_window=3)
        assert detector.frame_sample_rate == 10
        assert detector.smoothing_window == 3

    def test_emotion_labels(self):
        expected = [
            "happiness",
            "sadness",
            "anger",
            "fear",
            "disgust",
            "surprise",
            "neutral",
        ]
        assert EmotionDetector.EMOTION_LABELS == expected

    def test_emotion_map(self):
        expected_mappings = {
            "happy": "happiness",
            "sad": "sadness",
            "angry": "anger",
            "fear": "fear",
            "disgust": "disgust",
            "surprise": "surprise",
            "neutral": "neutral",
        }
        assert EmotionDetector.EMOTION_MAP == expected_mappings

    def test_get_dominant_emotion(self):
        detector = EmotionDetector()

        emotions = {
            "happiness": 0.8,
            "sadness": 0.1,
            "anger": 0.05,
            "fear": 0.02,
            "disgust": 0.01,
            "surprise": 0.01,
            "neutral": 0.01,
        }

        dominant, confidence = detector._get_dominant_emotion(emotions)
        assert dominant == "happiness"
        assert confidence == 0.8

    def test_get_dominant_emotion_empty(self):
        detector = EmotionDetector()
        dominant, confidence = detector._get_dominant_emotion({})
        assert dominant == "neutral"
        assert confidence == 0.0

    def test_smooth_emotions(self):
        detector = EmotionDetector(smoothing_window=3)

        # First sample
        emotions1 = {e: 0.0 for e in detector.EMOTION_LABELS}
        emotions1["happiness"] = 0.9
        smoothed1 = detector._smooth_emotions(emotions1)
        assert smoothed1["happiness"] == 0.9  # Only one sample

        # Second sample
        emotions2 = {e: 0.0 for e in detector.EMOTION_LABELS}
        emotions2["happiness"] = 0.6
        smoothed2 = detector._smooth_emotions(emotions2)
        assert smoothed2["happiness"] == 0.75  # Average of 0.9 and 0.6

        # Third sample
        emotions3 = {e: 0.0 for e in detector.EMOTION_LABELS}
        emotions3["happiness"] = 0.3
        smoothed3 = detector._smooth_emotions(emotions3)
        assert smoothed3["happiness"] == 0.6  # Average of 0.9, 0.6, 0.3

    def test_reset_buffers(self):
        detector = EmotionDetector(smoothing_window=3)

        # Add some samples
        emotions = {e: 0.5 for e in detector.EMOTION_LABELS}
        detector._smooth_emotions(emotions)
        detector._smooth_emotions(emotions)

        # Verify buffers have data
        assert len(detector.emotion_buffers["happiness"]) == 2

        # Reset
        detector._reset_buffers()

        # Verify buffers are empty
        assert len(detector.emotion_buffers["happiness"]) == 0

    def test_calculate_summary_empty(self):
        detector = EmotionDetector()
        summary = detector._calculate_summary([], 0)

        assert summary["dominant_emotion"] == "neutral"
        assert all(v == 0.0 for v in summary["average_scores"].values())
        assert summary["emotion_timeline"] == []

    def test_calculate_summary(self):
        detector = EmotionDetector()

        frame_results = [
            {
                "frame_number": 0,
                "timestamp": 0.0,
                "face_detected": True,
                "emotions": {
                    "happiness": 0.8,
                    "sadness": 0.1,
                    "anger": 0.05,
                    "fear": 0.02,
                    "disgust": 0.01,
                    "surprise": 0.01,
                    "neutral": 0.01,
                },
                "dominant_emotion": "happiness",
                "confidence": 0.8,
            },
            {
                "frame_number": 5,
                "timestamp": 0.2,
                "face_detected": True,
                "emotions": {
                    "happiness": 0.6,
                    "sadness": 0.2,
                    "anger": 0.1,
                    "fear": 0.05,
                    "disgust": 0.02,
                    "surprise": 0.02,
                    "neutral": 0.01,
                },
                "dominant_emotion": "happiness",
                "confidence": 0.6,
            },
        ]

        summary = detector._calculate_summary(frame_results, 1.0)

        assert summary["dominant_emotion"] == "happiness"
        assert summary["average_scores"]["happiness"] == 0.7
        assert len(summary["emotion_timeline"]) == 2

    def test_process_video_file_not_found(self):
        detector = EmotionDetector()

        with pytest.raises(FileNotFoundError):
            detector.process_video("/nonexistent/path/video.mp4")
