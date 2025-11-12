# exercises/dips.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class DipsAnalyzer:
    """Dips analyzer for chest and tricep development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_dip_position = False

    def analyze(self, landmarks, image):
        """Analyze dip form with focus on depth and shoulder position."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)

            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            torso_angle = calculate_angle(shoulder, hip, knee)

            # Check if in dip position (upright, arms supporting)
            self._check_position(shoulder, wrist, hip)

            if self.in_dip_position:
                # Check elbow depth
                self._check_elbow_angle(elbow_angle)

                # Check body posture
                self._check_torso_angle(torso_angle)

                # Check shoulder safety
                self._check_shoulder_position(shoulder, elbow)

                # Check leg position
                self._check_leg_position(hip, knee, ankle)

                # Rep counting
                self._count_reps(elbow_angle)

                # Draw visuals
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Get in dip starting position")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, wrist, hip):
        """Check if in proper dip position (upright, arms extended)."""
        # Wrists should be roughly level with or above shoulders
        # Body should be relatively upright
        wrist_shoulder_diff = wrist[1] - shoulder[1]

        if wrist_shoulder_diff < 0.1 and shoulder[1] < 0.7:
            self.in_dip_position = True
        else:
            self.in_dip_position = False
            self.is_down = False

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow depth for proper dip."""
        if elbow_angle > 170:
            self.feedback.append("✓ Arms fully extended")
        elif elbow_angle > 140:
            self.feedback.append("⚠️ Go lower for full range")
            self.form_score -= 15
        elif 70 <= elbow_angle <= 95:
            self.feedback.append("✓✓ Perfect dip depth (90°)")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Too low - risk to shoulders")
            self.form_score -= 20
        else:
            self.feedback.append("✓ Good depth")

    def _check_torso_angle(self, torso_angle):
        """Check body lean (slight forward lean is normal)."""
        if torso_angle < 140:
            self.feedback.append("⚠️ Leaning too far forward")
            self.form_score -= 10
        elif torso_angle > 200:
            self.feedback.append("⚠️ Too upright - lean slightly forward")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good torso angle")

    def _check_shoulder_position(self, shoulder, elbow):
        """Check shoulder safety (shoulders shouldn't drop too low)."""
        shoulder_elbow_diff = shoulder[1] - elbow[1]

        if shoulder_elbow_diff > 0.15:
            self.feedback.append("❌ Shoulders dropping too low - DANGER!")
            self.form_score -= 40
        elif shoulder_elbow_diff > 0.1:
            self.feedback.append("⚠️ Watch shoulder position")
            self.form_score -= 15

    def _check_leg_position(self, hip, knee, ankle):
        """Check if legs are in proper position."""
        # Legs can be straight or bent, but should be controlled
        leg_angle = calculate_angle(hip, knee, ankle)

        if leg_angle < 120:
            self.feedback.append("⚠️ Legs bent too much - keep controlled")
            self.form_score -= 5

    def _count_reps(self, elbow_angle):
        """Count reps with proper depth."""
        if elbow_angle < 100 and not self.is_down:
            self.is_down = True
        elif elbow_angle > 160 and self.is_down:
            self.is_down = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if 70 <= angle <= 95:
            color = (0, 255, 0)
        elif angle > 160:
            color = (0, 255, 255)
        else:
            color = (255, 255, 0)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_dip_position else (0, 0, 255)
        pos_text = "DIP POSITION" if self.in_dip_position else "GET IN POSITION"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_dip_position:
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
