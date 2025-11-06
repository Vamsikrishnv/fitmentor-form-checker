# backend/models.py
from pydantic import BaseModel
from typing import List, Optional

class AnalysisResponse(BaseModel):
    """Response model for form analysis."""
    exercise: str
    form_score: int
    rep_count: int
    feedback: List[str]
    angles: Optional[dict] = None
    success: bool
    message: str

class ExerciseInfo(BaseModel):
    """Information about an exercise."""
    id: int
    name: str
    description: str
    difficulty: str
    muscle_groups: List[str]

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    exercises_available: int