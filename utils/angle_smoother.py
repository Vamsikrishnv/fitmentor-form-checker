# utils/angle_smoother.py
from collections import deque
import numpy as np


class AngleSmoother:
    """Smooth angle measurements using rolling average to reduce jitter."""
    
    def __init__(self, window_size=5):
        """
        Initialize angle smoother.
        
        Args:
            window_size: Number of frames to average (default 5)
        """
        self.window_size = window_size
        self.angle_history = {}
    
    def smooth(self, angle_name: str, angle_value: float) -> float:
        """
        Smooth an angle using rolling average.
        
        Args:
            angle_name: Name/ID of the angle (e.g., "knee", "elbow")
            angle_value: Current angle measurement
            
        Returns:
            Smoothed angle value
        """
        # Initialize history for this angle if needed
        if angle_name not in self.angle_history:
            self.angle_history[angle_name] = deque(maxlen=self.window_size)
        
        # Add current value
        self.angle_history[angle_name].append(angle_value)
        
        # Return average
        return np.mean(self.angle_history[angle_name])
    
    def reset(self):
        """Reset all angle histories."""
        self.angle_history = {}
    
    def reset_angle(self, angle_name: str):
        """Reset history for specific angle."""
        if angle_name in self.angle_history:
            del self.angle_history[angle_name]


class ConfidenceFilter:
    """Filter out low-confidence pose detections."""
    
    def __init__(self, min_confidence=0.7):
        """
        Initialize confidence filter.
        
        Args:
            min_confidence: Minimum confidence threshold (0-1)
        """
        self.min_confidence = min_confidence
    
    def is_valid(self, landmarks) -> bool:
        """
        Check if pose landmarks meet confidence threshold.
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            True if confidence is acceptable
        """
        if not landmarks:
            return False
        
        # Check average visibility of key landmarks
        key_landmarks = [11, 12, 23, 24, 25, 26]  # shoulders, hips, knees
        
        total_visibility = 0
        for idx in key_landmarks:
            if idx < len(landmarks.landmark):
                total_visibility += landmarks.landmark[idx].visibility
        
        avg_visibility = total_visibility / len(key_landmarks)
        
        return avg_visibility >= self.min_confidence


class RepCounter:
    """Improved rep counter with state machine."""
    
    def __init__(self, down_threshold=100, up_threshold=160):
        """
        Initialize rep counter.
        
        Args:
            down_threshold: Angle threshold for "down" position
            up_threshold: Angle threshold for "up" position
        """
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.state = "READY"  # READY, DOWN, UP
        self.rep_count = 0
        self.partial_rep = False
    
    def update(self, angle: float) -> dict:
        """
        Update state machine with new angle.
        
        Args:
            angle: Current angle measurement
            
        Returns:
            dict with rep_count, state, partial_rep
        """
        if self.state == "READY" and angle < self.down_threshold:
            self.state = "DOWN"
            self.partial_rep = True
        
        elif self.state == "DOWN" and angle > self.up_threshold:
            self.state = "READY"
            if self.partial_rep:
                self.rep_count += 1
                self.partial_rep = False
        
        return {
            "rep_count": self.rep_count,
            "state": self.state,
            "partial_rep": self.partial_rep
        }
    
    def reset(self):
        """Reset counter."""
        self.state = "READY"
        self.rep_count = 0
        self.partial_rep = False