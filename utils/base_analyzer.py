# utils/base_analyzer.py
"""
Base class for all exercise analyzers.
Provides common functionality to reduce code duplication.
"""
import cv2
import logging
from abc import ABC, abstractmethod
from typing import Tuple, List
from utils.angle_smoother import AngleSmoother, ConfidenceFilter, RepCounter

logger = logging.getLogger(__name__)


class BaseExerciseAnalyzer(ABC):
    """Abstract base class for exercise form analyzers."""

    def __init__(self, use_smoothing: bool = True):
        """
        Initialize base analyzer.

        Args:
            use_smoothing: Whether to use angle smoothing (default: True)
        """
        self.form_score = 100
        self.feedback: List[str] = []
        self.rep_count = 0

        # Advanced utilities
        self.use_smoothing = use_smoothing
        if use_smoothing:
            self.angle_smoother = AngleSmoother(window_size=5)
        self.confidence_filter = ConfidenceFilter(min_confidence=0.7)

        # Optional rep counter (subclasses can override)
        self.rep_counter = None

    @abstractmethod
    def analyze(self, landmarks, image):
        """
        Analyze exercise form. Must be implemented by subclasses.

        Args:
            landmarks: MediaPipe pose landmarks
            image: Video frame (numpy array)

        Returns:
            Processed image with annotations
        """
        pass

    def smooth_angle(self, angle_name: str, angle_value: float) -> float:
        """
        Smooth angle using rolling average.

        Args:
            angle_name: Identifier for the angle (e.g., "knee", "elbow")
            angle_value: Current angle measurement

        Returns:
            Smoothed angle value
        """
        if self.use_smoothing:
            return self.angle_smoother.smooth(angle_name, angle_value)
        return angle_value

    def is_pose_valid(self, landmarks) -> bool:
        """
        Check if pose detection has sufficient confidence.

        Args:
            landmarks: MediaPipe pose landmarks

        Returns:
            True if pose is valid and confident enough
        """
        return self.confidence_filter.is_valid(landmarks)

    def draw_angle(self, image, point: Tuple[float, float], angle: float, label: str):
        """
        Draw angle measurement on image.

        Args:
            image: Video frame
            point: Normalized coordinates (x, y) in range [0, 1]
            angle: Angle value in degrees
            label: Label to display
        """
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        cv2.putText(
            image,
            f"{label}: {int(angle)}°",
            (x + 20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    def draw_feedback(self, image):
        """
        Draw form score, rep count, and feedback messages on image.

        Args:
            image: Video frame
        """
        score_color = self.get_score_color(self.form_score)

        # Form score
        cv2.putText(
            image,
            f"Form: {self.form_score}/100",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            score_color,
            2
        )

        # Rep count
        cv2.putText(
            image,
            f"Reps: {self.rep_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        # Feedback messages
        y_offset = 110
        for msg in self.feedback:
            cv2.putText(
                image,
                msg,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y_offset += 30

    def get_score_color(self, score: int) -> Tuple[int, int, int]:
        """
        Get BGR color based on form score.

        Args:
            score: Form score (0-100)

        Returns:
            BGR color tuple
        """
        if score >= 80:
            return (0, 255, 0)  # Green - Good form
        elif score >= 60:
            return (0, 255, 255)  # Yellow - Acceptable
        else:
            return (0, 0, 255)  # Red - Poor form

    def add_feedback(self, message: str, score_penalty: int = 0):
        """
        Add feedback message and apply score penalty.

        Args:
            message: Feedback message to display
            score_penalty: Points to deduct from form score (default: 0)
        """
        self.feedback.append(message)
        if score_penalty > 0:
            self.form_score = max(0, self.form_score - score_penalty)

    def reset_frame(self):
        """Reset per-frame state (form_score and feedback)."""
        self.form_score = 100
        self.feedback = []

    def reset_exercise(self):
        """Reset entire exercise state including rep count."""
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        if self.use_smoothing:
            self.angle_smoother.reset()
        if self.rep_counter:
            self.rep_counter.reset()
