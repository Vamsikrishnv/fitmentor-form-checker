# exercises/pushup.py
import cv2
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords
from utils.base_analyzer import BaseExerciseAnalyzer
from utils.angle_smoother import RepCounter

logger = logging.getLogger(__name__)


class PushupAnalyzer(BaseExerciseAnalyzer):
    """Analyzes push-up form with intelligent rep counting and angle smoothing."""

    def __init__(self):
        super().__init__(use_smoothing=True)
        # Rep counter: Down = elbow angle < 100, Up = elbow angle > 150
        self.rep_counter = RepCounter(down_threshold=100, up_threshold=150)
        self.in_pushup_position = False
        
    def analyze(self, landmarks, image):
        """Analyze push-up form with improved rep counting."""
        self.reset_frame()

        try:
            # Check pose confidence
            if not self.is_pose_valid(landmarks):
                self.add_feedback("⚠️ Can't detect pose clearly")
                self.draw_feedback(image)
                return image

            # Get coordinates (right side)
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)

            # Calculate angles
            elbow_angle_raw = calculate_angle(shoulder, elbow, wrist)
            body_angle_raw = calculate_angle(shoulder, hip, knee)

            elbow_angle = self.smooth_angle("elbow", elbow_angle_raw)
            body_angle = self.smooth_angle("body", body_angle_raw)

            # Check if in push-up position (body relatively horizontal)
            self._check_position(shoulder, hip, ankle)

            if self.in_pushup_position:
                # Check form
                self._check_elbow_depth(elbow_angle)
                self._check_body_alignment(body_angle)

                # Count reps using state machine
                rep_state = self.rep_counter.update(elbow_angle)
                self.rep_count = rep_state["rep_count"]

                # Draw angle
                self.draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.add_feedback("⚠️ Get in push-up position!")
                self.add_feedback("(Body should be horizontal)")
                # Reset rep counter if not in position
                if self.rep_counter:
                    self.rep_counter.state = "READY"

            # Draw feedback
            self.draw_feedback(image)

        except Exception as e:
            logger.error(f"Error analyzing pushup form: {str(e)}", exc_info=True)
            self.add_feedback("Analysis error occurred")

        return image
    
    def _check_position(self, shoulder, hip, ankle):
        """Check if user is in push-up position (horizontal body)."""
        vertical_diff = abs(shoulder[1] - hip[1])
        avg_y = (shoulder[1] + hip[1]) / 2

        # In push-up position if body is relatively horizontal and low
        if vertical_diff < 0.15 and avg_y > 0.3:
            self.in_pushup_position = True
        else:
            self.in_pushup_position = False

    def _check_elbow_depth(self, elbow_angle):
        """Check if going low enough."""
        if elbow_angle > 150:
            self.add_feedback("⚠️ Not going low enough", 20)
        elif 70 <= elbow_angle <= 110:
            self.add_feedback("✅ Good depth!")
        elif elbow_angle < 70:
            self.add_feedback("⚠️ Going too low", 10)

    def _check_body_alignment(self, body_angle):
        """Check if body is straight (plank position)."""
        if body_angle < 160:
            self.add_feedback("❌ Hips sagging!", 30)
        elif body_angle > 200:
            self.add_feedback("❌ Hips too high!", 30)
        else:
            self.add_feedback("✅ Good alignment!")

    def draw_feedback(self, image):
        """Override to show position status."""
        # Position status
        position_color = (0, 255, 0) if self.in_pushup_position else (0, 0, 255)
        status = "IN POSITION" if self.in_pushup_position else "NOT IN POSITION"
        cv2.putText(image, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, position_color, 2)

        if self.in_pushup_position:
            # Form score
            score_color = self.get_score_color(self.form_score)
            cv2.putText(image, f"Form: {self.form_score}/100", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2)

        # Rep count
        cv2.putText(image, f"Reps: {self.rep_count}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Feedback messages
        y_offset = 150
        for msg in self.feedback:
            cv2.putText(image, msg, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30