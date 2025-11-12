# FitMentor AI - Deployment Guide

## Entry Points

### Production API (Recommended)
**File:** `backend/main.py`

This is the full-featured production API with:
- ✅ Environment-based configuration
- ✅ Secure CORS policy
- ✅ File size and duration limits
- ✅ Structured logging
- ✅ 10 exercise analyzers with angle smoothing
- ✅ Comprehensive error handling

**Start command:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Legacy/Simple API
**File:** `main.py` (root level)

Basic API with only squat analysis. Kept for backward compatibility.

**Start command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### CLI Webcam Demo
**File:** `main.py` (root level)

Interactive CLI for testing with webcam.

**Start command:**
```bash
python main.py
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Required variables:
- `EMAIL_OCTOPUS_API_KEY` - EmailOctopus API key
- `EMAIL_OCTOPUS_LIST_ID` - EmailOctopus list ID
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
- `MAX_FILE_SIZE_MB` - Maximum video file size (default: 50)
- `MAX_VIDEO_DURATION_SECONDS` - Maximum video duration (default: 300)
- `LOG_LEVEL` - Logging level (default: INFO)

## Deployment Platforms

### Render.com
Update `render.yaml` to use the production API:
```yaml
services:
  - type: web
    name: fitmentor-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
```

### Docker
```bash
docker build -t fitmentor-api .
docker run -p 8000:8000 --env-file .env fitmentor-api
```

### Local Development
```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Frontend
cd landing
npm install
npm run dev
```

## Health Check
```bash
curl http://localhost:8000/api/health
```

## API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
