# exercises/pullup.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class PullupAnalyzer:
    """Pull-up analyzer for back and bicep development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_up = False
        self.in_hang_position = False

    def analyze(self, landmarks, image):
        """Analyze pull-up form with focus on chin height and body control."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            nose = get_landmark_coords(landmarks, 0)

            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            body_angle = calculate_angle(shoulder, hip, knee)

            # Check if in hanging position
            self._check_position(wrist, shoulder)

            if self.in_hang_position:
                # Check pull-up height (chin over bar)
                self._check_pull_height(nose, wrist)

                # Check elbow angle
                self._check_elbow_angle(elbow_angle)

                # Check body control (no excessive swing)
                self._check_body_control(body_angle)

                # Check leg position
                self._check_leg_position(hip, knee)

                # Rep counting
                self._count_reps(elbow_angle, nose, wrist)

                # Draw visuals
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Hang from bar to start")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, wrist, shoulder):
        """Check if in proper hanging position."""
        # Wrists should be above shoulders (hanging from bar)
        wrist_above = wrist[1] < shoulder[1]

        if wrist_above:
            self.in_hang_position = True
        else:
            self.in_hang_position = False
            self.is_up = False

    def _check_pull_height(self, nose, wrist):
        """Check if chin goes above bar level."""
        chin_above_bar = nose[1] < wrist[1]

        if chin_above_bar:
            self.feedback.append("✓✓ Chin above bar!")
        else:
            # Check how close they are
            diff = wrist[1] - nose[1]
            if diff > 0.1:
                self.feedback.append("❌ Pull higher - chin must clear bar")
                self.form_score -= 30
            elif diff > 0.05:
                self.feedback.append("⚠️ Almost there - pull a bit higher")
                self.form_score -= 15

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow angle during pull-up."""
        if elbow_angle > 160:
            self.feedback.append("✓ Full hang - good starting position")
        elif 60 <= elbow_angle <= 90:
            self.feedback.append("✓ Strong pull position")
        elif elbow_angle < 60:
            self.feedback.append("✓✓ Full pull!")

    def _check_body_control(self, body_angle):
        """Check for excessive swinging/kipping."""
        # Body should be relatively straight
        if body_angle < 150:
            self.feedback.append("⚠️ Too much swing - control your body")
            self.form_score -= 15
        elif body_angle > 200:
            self.feedback.append("⚠️ Excessive kipping - use strict form")
            self.form_score -= 15
        else:
            self.feedback.append("✓ Good body control")

    def _check_leg_position(self, hip, knee):
        """Check leg position during pull-up."""
        # Legs can be straight or slightly bent, but should be stable
        vertical_check = knee[1] > hip[1]

        if not vertical_check:
            self.feedback.append("⚠️ Legs swinging too much")
            self.form_score -= 10

    def _count_reps(self, elbow_angle, nose, wrist):
        """Count reps - must have chin above bar and return to full hang."""
        chin_above = nose[1] < wrist[1]

        if chin_above and elbow_angle < 100 and not self.is_up:
            self.is_up = True
        elif elbow_angle > 155 and self.is_up:
            self.is_up = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if angle < 90:
            color = (0, 255, 0)
        elif angle < 140:
            color = (0, 255, 255)
        else:
            color = (255, 255, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_hang_position else (0, 0, 255)
        pos_text = "PULL-UP" if self.in_hang_position else "HANG FROM BAR"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_hang_position:
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
