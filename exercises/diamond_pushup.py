# exercises/diamond_pushup.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class DiamondPushupAnalyzer:
    """Diamond push-up analyzer focusing on triceps with close hand placement."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_pushup_position = False

    def analyze(self, landmarks, image):
        """Analyze diamond push-up form with hand placement emphasis."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get all key landmarks
            left_shoulder = get_landmark_coords(landmarks, 11)
            right_shoulder = get_landmark_coords(landmarks, 12)
            left_elbow = get_landmark_coords(landmarks, 13)
            right_elbow = get_landmark_coords(landmarks, 14)
            left_wrist = get_landmark_coords(landmarks, 15)
            right_wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            ankle = get_landmark_coords(landmarks, 28)
            nose = get_landmark_coords(landmarks, 0)

            # Calculate angles (using right side as primary)
            elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            body_angle = calculate_angle(right_shoulder, hip, ankle)

            # Check position
            self._check_position(right_shoulder, hip, ankle)

            if self.in_pushup_position:
                # Check hand placement (diamond position)
                self._check_hand_placement(left_wrist, right_wrist, left_shoulder, right_shoulder)

                # Check elbow angle
                self._check_elbow_angle(elbow_angle)

                # Check body alignment
                self._check_body_alignment(body_angle)

                # Check elbow tuck (should be close to body for diamond)
                self._check_elbow_tuck(right_elbow, right_shoulder)

                # Rep counting
                self._count_reps(elbow_angle)

                # Draw visuals
                self._draw_angle(image, right_elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Get in push-up position")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, hip, ankle):
        """Check if in proper push-up starting position."""
        vertical_diff = abs(shoulder[1] - hip[1])
        avg_y = (shoulder[1] + hip[1]) / 2

        if vertical_diff < 0.15 and avg_y > 0.35:
            self.in_pushup_position = True
        else:
            self.in_pushup_position = False
            self.is_down = False

    def _check_hand_placement(self, left_wrist, right_wrist, left_shoulder, right_shoulder):
        """Check if hands are close together (diamond position)."""
        hand_distance = abs(left_wrist[0] - right_wrist[0])
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])

        # Hands should be much closer than shoulders for diamond
        if hand_distance > shoulder_width * 0.5:
            self.feedback.append("❌ Hands too far apart - bring them together!")
            self.form_score -= 30
        elif hand_distance > shoulder_width * 0.3:
            self.feedback.append("⚠️ Hands not close enough")
            self.form_score -= 15
        else:
            self.feedback.append("✓✓ Perfect diamond hand position")

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow depth."""
        if elbow_angle > 160:
            self.feedback.append("❌ Not low enough - go deeper")
            self.form_score -= 25
        elif elbow_angle > 140:
            self.feedback.append("⚠️ Shallow push-up")
            self.form_score -= 15
        elif 75 <= elbow_angle <= 95:
            self.feedback.append("✓✓ Perfect depth (90°)")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Too low")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good depth")

    def _check_body_alignment(self, body_angle):
        """Check if body is straight line."""
        if body_angle < 155:
            self.feedback.append("❌ HIPS SAGGING - engage core!")
            self.form_score -= 30
        elif body_angle < 165:
            self.feedback.append("⚠️ Slight hip sag")
            self.form_score -= 15
        elif body_angle > 195:
            self.feedback.append("❌ HIPS TOO HIGH")
            self.form_score -= 25
        elif body_angle > 185:
            self.feedback.append("⚠️ Hips slightly high")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good body alignment")

    def _check_elbow_tuck(self, elbow, shoulder):
        """Check if elbows are tucked close to body (key for diamond pushups)."""
        elbow_shoulder_diff = abs(elbow[0] - shoulder[0])

        if elbow_shoulder_diff > 0.20:
            self.feedback.append("⚠️ Keep elbows tucked close to body")
            self.form_score -= 15
        else:
            self.feedback.append("✓ Good elbow tuck")

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
        pos_color = (0, 255, 0) if self.in_pushup_position else (0, 0, 255)
        pos_text = "DIAMOND PUSH-UP" if self.in_pushup_position else "GET IN POSITION"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_pushup_position:
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
