# exercises/face_pull.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class FacePullAnalyzer:
    """Face pull analyzer for rear delts and upper back."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_pulled = False
        self.in_position = False

    def analyze(self, landmarks, image):
        """Analyze face pull form with focus on rear delt activation."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            left_shoulder = get_landmark_coords(landmarks, 11)
            right_shoulder = get_landmark_coords(landmarks, 12)
            left_elbow = get_landmark_coords(landmarks, 13)
            right_elbow = get_landmark_coords(landmarks, 14)
            left_wrist = get_landmark_coords(landmarks, 15)
            right_wrist = get_landmark_coords(landmarks, 16)
            nose = get_landmark_coords(landmarks, 0)
            hip = get_landmark_coords(landmarks, 24)

            # Calculate angles (using right side as primary)
            elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            shoulder_angle = calculate_angle(right_elbow, right_shoulder, hip)

            # Check if in proper standing position
            self._check_position(right_shoulder, hip)

            if self.in_position:
                # Check hand position relative to face
                self._check_hand_height(right_wrist, nose, right_shoulder)

                # Check elbow position (should be high and back)
                self._check_elbow_position(right_elbow, right_shoulder)

                # Check elbow angle
                self._check_elbow_angle(elbow_angle)

                # Check shoulder retraction
                self._check_shoulder_retraction(left_shoulder, right_shoulder)

                # Rep counting
                self._count_reps(elbow_angle, right_wrist, nose)

                # Draw visuals
                self._draw_angle(image, right_elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Stand upright to start")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, hip):
        """Check if standing upright."""
        vertical_diff = abs(shoulder[0] - hip[0])

        if vertical_diff < 0.15:
            self.in_position = True
        else:
            self.in_position = False
            self.is_pulled = False

    def _check_hand_height(self, wrist, nose, shoulder):
        """Check if hands are pulled to face level."""
        # Wrists should be near face height when pulled
        wrist_nose_diff = abs(wrist[1] - nose[1])

        if wrist_nose_diff < 0.1:
            self.feedback.append("✓✓ Perfect - hands at face level")
        elif wrist_nose_diff < 0.15:
            self.feedback.append("✓ Good hand position")
        else:
            self.feedback.append("⚠️ Pull hands toward face")
            self.form_score -= 20

    def _check_elbow_position(self, elbow, shoulder):
        """Check if elbows are high and back."""
        # Elbows should be at or above shoulder height
        elbow_height = shoulder[1] - elbow[1]

        if elbow_height > 0.05:
            self.feedback.append("✓ Elbows high - good!")
        elif elbow_height > -0.05:
            self.feedback.append("⚠️ Raise elbows higher")
            self.form_score -= 15
        else:
            self.feedback.append("❌ Elbows too low")
            self.form_score -= 25

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow angle during pull."""
        if 70 <= elbow_angle <= 110:
            self.feedback.append("✓ Good elbow angle")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Don't over-pull")
            self.form_score -= 10
        elif elbow_angle > 140:
            self.feedback.append("⚠️ Pull closer to face")
            self.form_score -= 15

    def _check_shoulder_retraction(self, left_shoulder, right_shoulder):
        """Check shoulder blade retraction."""
        # Shoulders should be pulled back (hard to detect perfectly)
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])

        if shoulder_width > 0.35:
            self.feedback.append("✓ Good shoulder retraction")
        else:
            self.feedback.append("⚠️ Squeeze shoulder blades")
            self.form_score -= 10

    def _count_reps(self, elbow_angle, wrist, nose):
        """Count reps."""
        hands_at_face = abs(wrist[1] - nose[1]) < 0.15

        if elbow_angle < 110 and hands_at_face and not self.is_pulled:
            self.is_pulled = True
        elif elbow_angle > 150 and self.is_pulled:
            self.is_pulled = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if 70 <= angle <= 110:
            color = (0, 255, 0)
        else:
            color = (0, 255, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_position else (0, 0, 255)
        pos_text = "FACE PULL" if self.in_position else "STAND UPRIGHT"
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
