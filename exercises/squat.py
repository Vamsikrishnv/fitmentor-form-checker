# exercises/squat.py
import cv2
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords
from utils.base_analyzer import BaseExerciseAnalyzer
from utils.angle_smoother import RepCounter

logger = logging.getLogger(__name__)


class SquatAnalyzer(BaseExerciseAnalyzer):
    """Analyzes squat form with intelligent rep counting and angle smoothing."""

    def __init__(self):
        super().__init__(use_smoothing=True)
        # Rep counter with squat-specific thresholds
        # Down: knee angle < 120, Up: knee angle > 160
        self.rep_counter = RepCounter(down_threshold=120, up_threshold=160)
        
    def analyze(self, landmarks, image):
        """Analyze squat form with improved rep counting."""
        self.reset_frame()

        try:
            # Check pose confidence
            if not self.is_pose_valid(landmarks):
                self.add_feedback("⚠️ Can't detect pose clearly")
                self.draw_feedback(image)
                return image

            # Get coordinates
            hip = get_landmark_coords(landmarks, 23)
            knee = get_landmark_coords(landmarks, 25)
            ankle = get_landmark_coords(landmarks, 27)
            shoulder = get_landmark_coords(landmarks, 11)

            # Calculate and smooth angles
            knee_angle_raw = calculate_angle(hip, knee, ankle)
            hip_angle_raw = calculate_angle(shoulder, hip, knee)

            knee_angle = self.smooth_angle("knee", knee_angle_raw)
            hip_angle = self.smooth_angle("hip", hip_angle_raw)

            # Check form
            self._check_depth(knee_angle)
            self._check_back_position(hip_angle)

            # Count reps using state machine
            rep_state = self.rep_counter.update(knee_angle)
            self.rep_count = rep_state["rep_count"]

            # Draw
            self.draw_angle(image, knee, knee_angle, "Knee")
            self.draw_feedback(image)

        except Exception as e:
            logger.error(f"Error analyzing squat form: {str(e)}", exc_info=True)
            self.add_feedback(f"Analysis error occurred")

        return image
    
    def _check_depth(self, knee_angle):
        """Check squat depth."""
        if knee_angle > 160:
            self.add_feedback("Too shallow - Go deeper!", 30)
        elif knee_angle > 140:
            self.add_feedback("Quarter squat", 15)
        elif knee_angle >= 90:
            self.add_feedback("Good depth!")
        else:
            self.add_feedback("Excellent depth!")

    def _check_back_position(self, hip_angle):
        """Check back position."""
        if hip_angle < 45:
            self.add_feedback("Back too bent", 25)
        elif hip_angle < 60:
            self.add_feedback("Watch back angle", 10)