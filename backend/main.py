# backend/main.py
# ==============================================================================
# PRODUCTION API ENTRY POINT
# ==============================================================================
# This is the main production API with:
# - Security: Environment-based configuration, CORS restrictions, file limits
# - Logging: Structured logging throughout
# - Features: 10 exercise analyzers with angle smoothing and rep counting
# - Error Handling: Comprehensive error handling and validation
#
# To run:
#   uvicorn backend.main:app --host 0.0.0.0 --port 8000
#
# For CLI demos: Use `python main.py` (root level) instead
# ==============================================================================

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sys
import os
import logging
from backend.email_signup import router as signup_router
from backend.logging_config import setup_logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import AnalysisResponse, ExerciseInfo, HealthResponse
from backend.video_processor import VideoProcessor

# Setup logging
logger = setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FitMentor AI API",
    description="AI-powered fitness form checker API",
    version="0.2.0"
)

# Configure CORS with environment variable or secure defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # Secure defaults - restrict to known origins only
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://fitmentor-form-checker.onrender.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Include email signup router
app.include_router(signup_router)

# Initialize video processor
video_processor = VideoProcessor()

# Exercise database
EXERCISES = [
    {
        "id": 1,
        "name": "Squat",
        "description": "Lower body compound exercise targeting quads, glutes, and hamstrings",
        "difficulty": "Beginner",
        "muscle_groups": ["Quadriceps", "Glutes", "Hamstrings", "Core"]
    },
    {
        "id": 2,
        "name": "Push-up",
        "description": "Upper body compound exercise targeting chest, shoulders, and triceps",
        "difficulty": "Beginner",
        "muscle_groups": ["Chest", "Shoulders", "Triceps", "Core"]
    },
    {
        "id": 3,
        "name": "Plank",
        "description": "Isometric core exercise for stability and strength",
        "difficulty": "Beginner",
        "muscle_groups": ["Core", "Shoulders", "Back"]
    },
    {
        "id": 4,
        "name": "Lunge",
        "description": "Lower body unilateral exercise for balance and strength",
        "difficulty": "Beginner",
        "muscle_groups": ["Quadriceps", "Glutes", "Hamstrings"]
    },
    {
        "id": 5,
        "name": "Deadlift",
        "description": "Full body compound exercise - hip hinge pattern",
        "difficulty": "Intermediate",
        "muscle_groups": ["Hamstrings", "Glutes", "Back", "Core"]
    },
    {
        "id": 6,
        "name": "Overhead Press",
        "description": "Shoulder compound exercise for overhead strength",
        "difficulty": "Intermediate",
        "muscle_groups": ["Shoulders", "Triceps", "Core"]
    },
    {
        "id": 7,
        "name": "Bent-Over Row",
        "description": "Back compound exercise for pulling strength",
        "difficulty": "Intermediate",
        "muscle_groups": ["Back", "Biceps", "Rear Delts"]
    },
    {
        "id": 8,
        "name": "Shoulder Raise",
        "description": "Shoulder isolation exercise",
        "difficulty": "Beginner",
        "muscle_groups": ["Shoulders"]
    },
    {
        "id": 9,
        "name": "Bicep Curl",
        "description": "Arm isolation exercise for biceps",
        "difficulty": "Beginner",
        "muscle_groups": ["Biceps"]
    },
    {
        "id": 10,
        "name": "Tricep Extension",
        "description": "Arm isolation exercise for triceps",
        "difficulty": "Beginner",
        "muscle_groups": ["Triceps"]
    }
]


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": "FitMentor AI API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "exercises_available": len(EXERCISES)
    }


@app.get("/api/exercises", response_model=List[ExerciseInfo], tags=["Exercises"])
async def list_exercises():
    """Get list of all available exercises."""
    return EXERCISES


@app.get("/api/exercises/{exercise_id}", response_model=ExerciseInfo, tags=["Exercises"])
async def get_exercise(exercise_id: int):
    """Get details of a specific exercise."""
    for exercise in EXERCISES:
        if exercise["id"] == exercise_id:
            return exercise
    
    raise HTTPException(status_code=404, detail="Exercise not found")


@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_form(
    video: UploadFile = File(..., description="Video file to analyze"),
    exercise: str = Form(default="squat", description="Exercise type")
):
    """
    Analyze exercise form from uploaded video.

    - **video**: Video file (mp4, avi, mov)
    - **exercise**: Exercise type (default: squat)

    Valid exercises: squat, pushup, plank, lunge, deadlift, overhead_press,
                    row, shoulder_raise, bicep_curl, tricep_extension

    Returns form score, rep count, and feedback.
    """

    logger.info(f"Received video upload: {video.filename}, exercise: {exercise}, content_type: {video.content_type}")

    # Get file size limits from environment
    max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    max_duration_seconds = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "300"))

    # Check file size (read first to get size)
    video_content = await video.read()
    file_size_mb = len(video_content) / (1024 * 1024)

    if file_size_mb > max_file_size_mb:
        logger.warning(f"File too large: {file_size_mb:.2f}MB (max: {max_file_size_mb}MB) from file: {video.filename}")
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_file_size_mb}MB)"
        )

    # Validate file type - strict validation
    valid_video_types = [
        'video/mp4', 'video/avi', 'video/quicktime',
        'video/x-msvideo', 'video/x-matroska', 'video/webm'
    ]

    # Allow application/octet-stream only if filename has video extension
    if video.content_type == 'application/octet-stream':
        if video.filename and not any(video.filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            logger.warning(f"Invalid file extension for octet-stream: {video.filename}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Please upload a video file (mp4, avi, mov, mkv, webm)"
            )
    elif video.content_type not in valid_video_types and not video.content_type.startswith('video/'):
        logger.warning(f"Invalid content type: {video.content_type} for file: {video.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {video.content_type}. Please upload a video file (mp4, avi, mov, etc.)"
        )
    
    # Validate exercise type
    valid_exercises = [
        "squat", "pushup", "plank", "lunge", "deadlift",
        "overhead_press", "row", "shoulder_raise", "bicep_curl", "tricep_extension"
    ]
    
    exercise_lower = exercise.lower()

    if exercise_lower not in valid_exercises:
        logger.warning(f"Invalid exercise type requested: {exercise_lower}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid exercise type: {exercise}. Valid types: {', '.join(valid_exercises)}"
        )

    logger.info(f"Starting analysis for {exercise_lower} on file: {video.filename}")

    # Process video with duration limit
    try:
        result = await video_processor.analyze_video(
            video_content,
            exercise_lower,
            max_duration_seconds
        )
        logger.info(f"Analysis complete for {exercise_lower}: success={result['success']}, score={result.get('form_score', 'N/A')}, reps={result.get('rep_count', 'N/A')}")
        return result
    except Exception as e:
        logger.error(f"Error during video analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )

@app.get("/api/exercises/random", response_model=ExerciseInfo, tags=["Exercises"])
async def get_random_exercise():
    """Get a random exercise suggestion."""
    import random
    return random.choice(EXERCISES)


@app.get("/api/exercises/difficulty/{difficulty}", response_model=List[ExerciseInfo], tags=["Exercises"])
async def get_exercises_by_difficulty(difficulty: str):
    """Get exercises by difficulty level (beginner, intermediate, advanced)."""
    results = [ex for ex in EXERCISES if ex["difficulty"].lower() == difficulty.lower()]
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No exercises found for difficulty: {difficulty}")
    
    return results


@app.get("/api/exercises/muscle/{muscle}", response_model=List[ExerciseInfo], tags=["Exercises"])
async def get_exercises_by_muscle(muscle: str):
    """Get exercises targeting a specific muscle group."""
    results = [
        ex for ex in EXERCISES 
        if any(muscle.lower() in mg.lower() for mg in ex["muscle_groups"])
    ]
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No exercises found for muscle: {muscle}")
    
    return results


@app.post("/api/batch-analyze", tags=["Analysis"])
async def batch_analyze(
    videos: List[UploadFile] = File(...),
    exercise: str = Form(default="squat")
):
    """Analyze multiple videos at once."""
    results = []
    
    for video in videos:
        result = await video_processor.analyze_video(video, exercise.lower())
        results.append({
            "filename": video.filename,
            "result": result
        })
    
    return {
        "total_videos": len(videos),
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)