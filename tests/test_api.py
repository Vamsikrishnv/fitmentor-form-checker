# tests/test_api.py
"""
Basic API endpoint tests for FitMentor AI.

To run: pytest tests/test_api.py
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "exercises_available" in data


def test_list_exercises():
    """Test getting list of exercises."""
    response = client.get("/api/exercises")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check structure of first exercise
    exercise = data[0]
    assert "id" in exercise
    assert "name" in exercise
    assert "description" in exercise
    assert "difficulty" in exercise
    assert "muscle_groups" in exercise


def test_get_exercise_by_id():
    """Test getting a specific exercise."""
    response = client.get("/api/exercises/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Squat"


def test_get_nonexistent_exercise():
    """Test getting a non-existent exercise returns 404."""
    response = client.get("/api/exercises/9999")
    assert response.status_code == 404


def test_get_exercises_by_difficulty():
    """Test filtering exercises by difficulty."""
    response = client.get("/api/exercises/difficulty/Beginner")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(ex["difficulty"] == "Beginner" for ex in data)


def test_get_exercises_by_muscle():
    """Test filtering exercises by muscle group."""
    response = client.get("/api/exercises/muscle/core")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All exercises should target core
    assert all(
        any("core" in mg.lower() for mg in ex["muscle_groups"])
        for ex in data
    )


def test_invalid_exercise_type():
    """Test analyze endpoint rejects invalid exercise types."""
    # Create a dummy file
    files = {"video": ("test.mp4", b"fake video content", "video/mp4")}
    data = {"exercise": "invalid_exercise"}

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid exercise type" in response.json()["detail"]


def test_file_size_limit():
    """Test that oversized files are rejected."""
    # Create a file larger than 50MB (default limit)
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    files = {"video": ("large.mp4", large_content, "video/mp4")}
    data = {"exercise": "squat"}

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]


@pytest.mark.skip(reason="Requires EmailOctopus API key")
def test_signup_endpoint():
    """Test waitlist signup endpoint (requires API key)."""
    response = client.post(
        "/api/signup",
        json={"email": "test@example.com", "name": "Test User"}
    )
    # Response depends on whether API key is configured
    assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
