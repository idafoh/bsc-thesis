#!/usr/bin/env python3
"""CLI script to test the emotion detection pipeline on sample videos."""

import argparse
import json
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.pipeline.emotion_detector import EmotionDetector


def main():
    parser = argparse.ArgumentParser(
        description="Analyze emotions in a video file"
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to the video file to analyze",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "-r", "--sample-rate",
        type=int,
        default=5,
        help="Process every Nth frame (default: 5)",
    )
    parser.add_argument(
        "-w", "--smoothing-window",
        type=int,
        default=5,
        help="Smoothing window size (default: 5)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print progress updates",
    )

    args = parser.parse_args()

    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    def progress_callback(progress: int):
        if args.verbose:
            print(f"Progress: {progress}%", end="\r")

    print(f"Analyzing video: {video_path}", file=sys.stderr)

    detector = EmotionDetector(
        frame_sample_rate=args.sample_rate,
        smoothing_window=args.smoothing_window,
    )

    try:
        results = detector.process_video(video_path, progress_callback=progress_callback)
    except Exception as e:
        print(f"Error processing video: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print()  # New line after progress

    # Output results
    output_json = json.dumps(results, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_json)
        print(f"Results written to: {output_path}", file=sys.stderr)
    else:
        print(output_json)

    # Print summary to stderr
    summary = results.get("summary", {})
    print(f"\n--- Summary ---", file=sys.stderr)
    print(f"Duration: {results.get('duration', 0):.2f}s", file=sys.stderr)
    print(f"Total frames: {results.get('total_frames', 0)}", file=sys.stderr)
    print(f"FPS: {results.get('fps', 0):.2f}", file=sys.stderr)
    print(f"Dominant emotion: {summary.get('dominant_emotion', 'N/A')}", file=sys.stderr)
    print(f"Average scores:", file=sys.stderr)
    for emotion, score in sorted(
        summary.get("average_scores", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"  {emotion}: {score * 100:.1f}%", file=sys.stderr)


if __name__ == "__main__":
    main()
