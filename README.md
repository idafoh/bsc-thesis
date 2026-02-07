# Emotion Detection in Video

A web application for detecting and visualizing emotion dynamics in user-uploaded videos. Built as a BSc thesis project.

## Features

- **Video Upload**: Support for MP4, AVI, MOV, and WebM formats (up to 500MB)
- **Face Detection**: MediaPipe-based face detection with automatic largest face tracking
- **Emotion Classification**: 7-class emotion recognition (happiness, sadness, anger, fear, disgust, surprise, neutral)
- **Temporal Smoothing**: Sliding window averaging for stable emotion readings
- **Interactive Visualization**: Real-time emotion timeline with Recharts
- **Data Export**: Download results as CSV or JSON

## Technology Stack

### Frontend
- React 18 with TypeScript
- Vite build tool
- TailwindCSS for styling
- Recharts for visualization
- React Query for API state management

### Backend
- FastAPI (Python)
- Celery + Redis for async processing
- SQLite for job storage
- MediaPipe for face detection
- FER library for emotion recognition

## Project Structure

```
thesis/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Config, settings
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── pipeline/         # Emotion detection pipeline
│   ├── requirements.txt
│   ├── cli.py                # CLI for testing pipeline
│   └── main.py
├── tests/                    # Test suites
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (for Celery task queue)

## Setup

### Backend

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Start Redis (required for async processing):
```bash
# On macOS with Homebrew
brew install redis
brew services start redis

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

5. Start the Celery worker:
```bash
celery -A app.core.celery_app worker --loglevel=info
```

6. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/videos/upload` | Upload video for analysis |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{job_id}` | Get job status |
| DELETE | `/api/jobs/{job_id}` | Cancel/delete job |
| GET | `/api/results/{job_id}` | Get analysis results |
| GET | `/api/results/{job_id}/export?format=csv\|json` | Export results |

Full API documentation available at http://localhost:8000/docs

## CLI Usage

Test the emotion detection pipeline directly:

```bash
cd backend
python cli.py path/to/video.mp4 -v -o results.json
```

Options:
- `-o, --output`: Output JSON file path (default: stdout)
- `-r, --sample-rate`: Process every Nth frame (default: 5)
- `-w, --smoothing-window`: Smoothing window size (default: 5)
- `-v, --verbose`: Print progress updates

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Configuration

Environment variables (set in `backend/.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `DATABASE_URL` | Database connection URL | `sqlite+aiosqlite:///./emotion_detection.db` |
| `MAX_VIDEO_SIZE_MB` | Maximum upload size | `500` |
| `MAX_VIDEO_DURATION_SECONDS` | Maximum video duration | `600` |
| `FRAME_SAMPLE_RATE` | Process every Nth frame | `5` |
| `SMOOTHING_WINDOW_SIZE` | Temporal smoothing window | `5` |

## Emotion Classes

The system detects 7 emotion classes:

| Emotion | Color Code |
|---------|------------|
| Happiness | #FFD700 |
| Sadness | #4169E1 |
| Anger | #DC143C |
| Fear | #8B008B |
| Disgust | #228B22 |
| Surprise | #FF8C00 |
| Neutral | #808080 |

## License

This project is part of a BSc thesis and is intended for educational purposes.
