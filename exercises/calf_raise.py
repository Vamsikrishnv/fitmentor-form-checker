# exercises/calf_raise.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class CalfRaiseAnalyzer:
    """Calf raise analyzer for calf muscle development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_raised = False
        self.in_position = False

    def analyze(self, landmarks, image):
        """Analyze calf raise form with focus on ankle movement and balance."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            heel = get_landmark_coords(landmarks, 29)
            toe = get_landmark_coords(landmarks, 32)
            shoulder = get_landmark_coords(landmarks, 12)

            # Calculate angles
            knee_angle = calculate_angle(hip, knee, ankle)
            ankle_angle = calculate_angle(knee, ankle, toe)

            # Check if standing upright
            self._check_position(shoulder, hip, ankle)

            if self.in_position:
                # Check knee straightness
                self._check_knee_straightness(knee_angle)

                # Check ankle extension (heel raise)
                self._check_ankle_extension(ankle_angle, heel, toe)

                # Check balance
                self._check_balance(shoulder, ankle)

                # Check range of motion
                self._check_range_of_motion(heel, toe)

                # Rep counting
                self._count_reps(heel, toe)

                # Draw visuals
                self._draw_angle(image, ankle, ankle_angle, "Ankle")
            else:
                self.feedback.append("⚠️ Stand upright")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, hip, ankle):
        """Check if standing in proper upright position."""
        vertical_alignment = abs(shoulder[0] - ankle[0])

        if vertical_alignment < 0.15:
            self.in_position = True
        else:
            self.in_position = False
            self.is_raised = False

    def _check_knee_straightness(self, knee_angle):
        """Check if knees are straight (not locked, but extended)."""
        if knee_angle > 160:
            self.feedback.append("✓ Knees straight")
        elif knee_angle > 140:
            self.feedback.append("⚠️ Straighten knees slightly")
            self.form_score -= 10
        else:
            self.feedback.append("❌ Keep knees straight")
            self.form_score -= 20

    def _check_ankle_extension(self, ankle_angle, heel, toe):
        """Check ankle extension (plantar flexion)."""
        heel_raised = toe[1] - heel[1]

        if heel_raised > 0.05:
            self.feedback.append("✓✓ Full ankle extension")
        elif heel_raised > 0.02:
            self.feedback.append("✓ Good ankle extension")
        else:
            self.feedback.append("⚠️ Rise higher on toes")
            self.form_score -= 20

    def _check_balance(self, shoulder, ankle):
        """Check if maintaining balance."""
        lateral_sway = abs(shoulder[0] - ankle[0])

        if lateral_sway > 0.15:
            self.feedback.append("⚠️ Keep balance - don't sway")
            self.form_score -= 15

    def _check_range_of_motion(self, heel, toe):
        """Check if using full range of motion."""
        rom = toe[1] - heel[1]

        if rom > 0.08:
            self.feedback.append("✓ Excellent range of motion")
        elif rom > 0.05:
            self.feedback.append("✓ Good range")
        else:
            self.feedback.append("⚠️ Increase range of motion")
            self.form_score -= 15

    def _count_reps(self, heel, toe):
        """Count reps based on heel raise."""
        heel_raised = toe[1] - heel[1] > 0.04

        if heel_raised and not self.is_raised:
            self.is_raised = True
        elif not heel_raised and self.is_raised:
            self.is_raised = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        color = (0, 255, 0) if angle > 140 else (0, 255, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_position else (0, 0, 255)
        pos_text = "CALF RAISE" if self.in_position else "STAND UPRIGHT"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_position:
            if self.form_score >= 85:
                score_color = (0, 255, 0)
            elif self.form_score >= 70:
                score_color = (0, 255, 255)
            else:
                score_color = (0, 0, 255)

            cv2.putText(image, f"FORM: {self.form_score}/100",
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 3)

        cv2.putText(image, f"REPS: {self.rep_count}",
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        y_offset = 180
        for msg in self.feedback[:4]:
            cv2.putText(image, msg, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 35
