# exercises/romanian_deadlift.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class RomanianDeadliftAnalyzer:
    """Romanian deadlift analyzer for hamstring and glute development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_position = False

    def analyze(self, landmarks, image):
        """Analyze Romanian deadlift form with focus on hip hinge and back angle."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            wrist = get_landmark_coords(landmarks, 16)

            # Calculate angles
            back_angle = calculate_angle(shoulder, hip, knee)
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, ankle)

            # Check if in proper standing position
            self._check_position(shoulder, hip, ankle)

            if self.in_position:
                # Check back angle (should stay relatively straight)
                self._check_back_straightness(back_angle)

                # Check knee bend (slight bend, not full squat)
                self._check_knee_bend(knee_angle)

                # Check hip hinge depth
                self._check_hip_hinge(hip_angle)

                # Check bar path (hands should move straight down)
                self._check_bar_path(wrist, ankle)

                # Rep counting
                self._count_reps(hip_angle)

                # Draw visuals
                self._draw_angle(image, hip, hip_angle, "Hip")
                self._draw_angle(image, knee, knee_angle, "Knee")
            else:
                self.feedback.append("⚠️ Stand upright to start")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, hip, ankle):
        """Check if in proper starting position (standing upright)."""
        vertical_alignment = abs(shoulder[0] - ankle[0])
        hip_height = hip[1] < shoulder[1]

        if vertical_alignment < 0.15 and hip_height:
            self.in_position = True
        else:
            self.in_position = False
            self.is_down = False

    def _check_back_straightness(self, back_angle):
        """Check if back stays straight (neutral spine)."""
        if 155 <= back_angle <= 185:
            self.feedback.append("✓✓ Back straight - perfect!")
        elif 145 <= back_angle < 155:
            self.feedback.append("⚠️ Back rounding slightly")
            self.form_score -= 20
        elif back_angle < 145:
            self.feedback.append("❌ BACK ROUNDING - dangerous!")
            self.form_score -= 40
        elif back_angle > 185:
            self.feedback.append("⚠️ Maintain neutral spine")
            self.form_score -= 15

    def _check_knee_bend(self, knee_angle):
        """Check for slight knee bend (not locked, not deep squat)."""
        if 150 <= knee_angle <= 170:
            self.feedback.append("✓ Perfect knee bend")
        elif knee_angle > 175:
            self.feedback.append("⚠️ Bend knees slightly")
            self.form_score -= 15
        elif knee_angle < 140:
            self.feedback.append("⚠️ Too much knee bend - hinge at hips")
            self.form_score -= 20
        else:
            self.feedback.append("✓ Good knee position")

    def _check_hip_hinge(self, hip_angle):
        """Check hip hinge depth."""
        if hip_angle < 70:
            self.feedback.append("❌ Too deep - keep tension")
            self.form_score -= 15
        elif 70 <= hip_angle <= 100:
            self.feedback.append("✓✓ Perfect hip hinge depth")
        elif hip_angle < 120:
            self.feedback.append("✓ Good depth")
        elif hip_angle < 140:
            self.feedback.append("⚠️ Go deeper for full hamstring stretch")
            self.form_score -= 15
        else:
            self.feedback.append("❌ Lower the weight more")
            self.form_score -= 25

    def _check_bar_path(self, wrist, ankle):
        """Check if bar stays close to legs."""
        bar_distance = abs(wrist[0] - ankle[0])

        if bar_distance < 0.1:
            self.feedback.append("✓ Bar close to legs")
        else:
            self.feedback.append("⚠️ Keep bar close to body")
            self.form_score -= 15

    def _count_reps(self, hip_angle):
        """Count reps."""
        if hip_angle < 110 and not self.is_down:
            self.is_down = True
        elif hip_angle > 145 and self.is_down:
            self.is_down = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if label == "Hip":
            if 70 <= angle <= 100:
                color = (0, 255, 0)
            else:
                color = (0, 255, 255)
        else:  # Knee
            if 150 <= angle <= 170:
                color = (0, 255, 0)
            else:
                color = (0, 255, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_position else (0, 0, 255)
        pos_text = "ROMANIAN DEADLIFT" if self.in_position else "STAND UPRIGHT"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, pos_color, 2)

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
