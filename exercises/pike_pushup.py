# exercises/pike_pushup.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class PikePushupAnalyzer:
    """Pike push-up analyzer for shoulder development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_pike_position = False

    def analyze(self, landmarks, image):
        """Analyze pike push-up form with focus on hip angle and shoulder movement."""
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
            nose = get_landmark_coords(landmarks, 0)

            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            hip_angle = calculate_angle(shoulder, hip, ankle)
            knee_angle = calculate_angle(hip, knee, ankle)

            # Check if in pike position (inverted V)
            self._check_position(hip, shoulder, ankle)

            if self.in_pike_position:
                # Check hip angle (should be acute, ~60-90°)
                self._check_hip_angle(hip_angle)

                # Check elbow depth
                self._check_elbow_angle(elbow_angle)

                # Check leg straightness
                self._check_leg_straightness(knee_angle)

                # Check head position
                self._check_head_position(nose, wrist)

                # Rep counting
                self._count_reps(elbow_angle)

                # Draw visuals
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
                self._draw_angle(image, hip, hip_angle, "Hip")
            else:
                self.feedback.append("⚠️ Get in pike position (inverted V)")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, hip, shoulder, ankle):
        """Check if in proper pike position (hips high, inverted V)."""
        # Hip should be significantly higher than both shoulder and ankle
        hip_elevation = hip[1] < shoulder[1] - 0.15 and hip[1] < ankle[1] - 0.15

        if hip_elevation:
            self.in_pike_position = True
        else:
            self.in_pike_position = False
            self.is_down = False

    def _check_hip_angle(self, hip_angle):
        """Check if hips are at proper pike angle."""
        if 60 <= hip_angle <= 90:
            self.feedback.append("✓✓ Perfect pike angle")
        elif hip_angle < 60:
            self.feedback.append("⚠️ Hips too low - lift them higher")
            self.form_score -= 20
        elif hip_angle < 100:
            self.feedback.append("✓ Good pike angle")
        else:
            self.feedback.append("❌ Hips not high enough")
            self.form_score -= 30

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow depth during pike push-up."""
        if elbow_angle > 160:
            self.feedback.append("❌ Not low enough - lower head")
            self.form_score -= 25
        elif elbow_angle > 140:
            self.feedback.append("⚠️ Go deeper")
            self.form_score -= 15
        elif 75 <= elbow_angle <= 95:
            self.feedback.append("✓✓ Perfect depth (90°)")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Too low")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good depth")

    def _check_leg_straightness(self, knee_angle):
        """Check if legs are straight."""
        if knee_angle > 160:
            self.feedback.append("✓ Legs straight")
        elif knee_angle > 140:
            self.feedback.append("⚠️ Straighten legs more")
            self.form_score -= 10
        else:
            self.feedback.append("❌ Legs bent - keep them straight")
            self.form_score -= 20

    def _check_head_position(self, nose, wrist):
        """Check if head is moving toward hands."""
        # Head should move toward floor/hands, not forward
        head_wrist_diff = abs(nose[0] - wrist[0])

        if head_wrist_diff > 0.25:
            self.feedback.append("⚠️ Lower head toward hands")
            self.form_score -= 10

    def _count_reps(self, elbow_angle):
        """Count reps."""
        if elbow_angle < 100 and not self.is_down:
            self.is_down = True
        elif elbow_angle > 155 and self.is_down:
            self.is_down = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if label == "Hip":
            if 60 <= angle <= 90:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
        else:  # Elbow
            if 75 <= angle <= 95:
                color = (0, 255, 0)
            elif 100 <= angle <= 140:
                color = (0, 255, 255)
            else:
                color = (0, 0, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_pike_position else (0, 0, 255)
        pos_text = "PIKE POSITION" if self.in_pike_position else "GET IN PIKE"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_pike_position:
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
