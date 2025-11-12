# tests/test_utils.py
"""
Tests for utility modules.

To run: pytest tests/test_utils.py
"""
import pytest
import numpy as np
from utils.angle_calculator import calculate_angle
from utils.angle_smoother import AngleSmoother, ConfidenceFilter, RepCounter


def test_calculate_angle():
    """Test angle calculation."""
    # Test 90 degree angle
    p1 = (0, 1)
    p2 = (0, 0)
    p3 = (1, 0)
    angle = calculate_angle(p1, p2, p3)
    assert abs(angle - 90) < 1  # Allow small floating point error

    # Test 180 degree angle (straight line)
    p1 = (0, 0)
    p2 = (1, 0)
    p3 = (2, 0)
    angle = calculate_angle(p1, p2, p3)
    assert abs(angle - 180) < 1


def test_angle_smoother():
    """Test angle smoothing functionality."""
    smoother = AngleSmoother(window_size=3)

    # Test with noisy data
    angles = [90, 92, 88, 91, 89]
    smoothed = []

    for angle in angles:
        smoothed_angle = smoother.smooth("knee", angle)
        smoothed.append(smoothed_angle)

    # Smoothed values should be less noisy
    assert len(smoothed) == len(angles)
    # After window fills, smoothed values should be averages
    assert abs(smoothed[2] - 90) < 2  # Should be close to 90


def test_angle_smoother_reset():
    """Test angle smoother reset functionality."""
    smoother = AngleSmoother(window_size=3)

    smoother.smooth("knee", 90)
    smoother.smooth("knee", 100)

    smoother.reset()

    # After reset, should start fresh
    result = smoother.smooth("knee", 80)
    assert result == 80  # First value after reset


def test_rep_counter():
    """Test rep counting state machine."""
    counter = RepCounter(down_threshold=100, up_threshold=160)

    # Simulate a rep: start high, go low, return high
    angles = [170, 165, 120, 90, 85, 90, 120, 160, 170]

    for angle in angles:
        state = counter.update(angle)

    # Should have counted 1 rep
    assert state["rep_count"] == 1
    assert state["state"] == "READY"


def test_rep_counter_partial_rep():
    """Test that incomplete reps are not counted."""
    counter = RepCounter(down_threshold=100, up_threshold=160)

    # Go down but don't return up
    angles = [170, 120, 90, 85]

    for angle in angles:
        state = counter.update(angle)

    # Should not have counted a rep yet
    assert state["rep_count"] == 0
    assert state["partial_rep"] is True


def test_rep_counter_multiple_reps():
    """Test counting multiple reps."""
    counter = RepCounter(down_threshold=100, up_threshold=160)

    # Simulate 3 reps
    for _ in range(3):
        # Go down
        counter.update(90)
        # Go up
        result = counter.update(170)

    assert result["rep_count"] == 3


def test_confidence_filter():
    """Test confidence filter (basic structure test)."""
    filter = ConfidenceFilter(min_confidence=0.7)

    # Test with None
    assert filter.is_valid(None) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
