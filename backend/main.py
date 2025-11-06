# backend/main.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import AnalysisResponse, ExerciseInfo, HealthResponse
from backend.video_processor import VideoProcessor

app = FastAPI(
    title="FitMentor AI API",
    description="AI-powered fitness form checker API",
    version="0.2.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    exercise: str = Form(..., description="Exercise type (squat, pushup, plank, etc.)")
):
    """
    Analyze exercise form from uploaded video.
    
    - **video**: Video file (mp4, avi, mov)
    - **exercise**: Exercise type (squat, pushup, plank, lunge, deadlift, overhead_press, row, shoulder_raise, bicep_curl, tricep_extension)
    
    Returns form score, rep count, and feedback.
    """
    
    # Validate file type
    if not video.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="File must be a video (mp4, avi, mov, etc.)"
        )
    
    # Validate exercise type
    valid_exercises = [
        "squat", "pushup", "plank", "lunge", "deadlift",
        "overhead_press", "row", "shoulder_raise", "bicep_curl", "tricep_extension"
    ]
    
    if exercise.lower() not in valid_exercises:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid exercise type. Valid types: {', '.join(valid_exercises)}"
        )
    
    # Process video
    result = await video_processor.analyze_video(video, exercise.lower())
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)