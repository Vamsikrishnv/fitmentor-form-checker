# exercises/side_plank.py
import cv2
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class SidePlankAnalyzer:
    """Side plank analyzer for core stability and oblique development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.hold_time = 0
        self.start_time = None
        self.in_side_plank = False

    def analyze(self, landmarks, image):
        """Analyze side plank form with focus on hip alignment and body straightness."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            left_shoulder = get_landmark_coords(landmarks, 11)
            right_shoulder = get_landmark_coords(landmarks, 12)
            left_elbow = get_landmark_coords(landmarks, 13)
            right_elbow = get_landmark_coords(landmarks, 14)
            left_hip = get_landmark_coords(landmarks, 23)
            right_hip = get_landmark_coords(landmarks, 24)
            left_ankle = get_landmark_coords(landmarks, 27)
            right_ankle = get_landmark_coords(landmarks, 28)

            # Determine which side is down (lower shoulder/elbow)
            if left_shoulder[1] > right_shoulder[1]:
                # Left side down
                lower_shoulder = left_shoulder
                lower_elbow = left_elbow
                lower_hip = left_hip
                lower_ankle = left_ankle
                upper_shoulder = right_shoulder
                upper_hip = right_hip
            else:
                # Right side down
                lower_shoulder = right_shoulder
                lower_elbow = right_elbow
                lower_hip = right_hip
                lower_ankle = right_ankle
                upper_shoulder = left_shoulder
                upper_hip = left_hip

            # Calculate body alignment angle
            body_angle = calculate_angle(lower_shoulder, lower_hip, lower_ankle)

            # Check if in side plank position
            self._check_position(lower_shoulder, lower_elbow, lower_hip)

            if self.in_side_plank:
                # Start timer if just entered position
                if self.start_time is None:
                    self.start_time = time.time()

                # Check body alignment
                self._check_body_alignment(body_angle)

                # Check hip height (should be elevated, not sagging)
                self._check_hip_position(lower_hip, lower_shoulder, lower_ankle)

                # Check hip stacking
                self._check_hip_stacking(upper_hip, lower_hip)

                # Update hold time
                self.hold_time = int(time.time() - self.start_time)

                # Draw visuals
                self._draw_angle(image, lower_hip, body_angle, "Body")
            else:
                self.feedback.append("⚠️ Get in side plank position")
                self.start_time = None

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, elbow, hip):
        """Check if in proper side plank position."""
        # Shoulder and hip should be roughly aligned horizontally
        horizontal_alignment = abs(shoulder[1] - hip[1])

        # Elbow should be roughly under shoulder (on forearm)
        elbow_under_shoulder = abs(elbow[0] - shoulder[0]) < 0.1

        if horizontal_alignment < 0.2 and elbow_under_shoulder:
            self.in_side_plank = True
        else:
            self.in_side_plank = False

    def _check_body_alignment(self, body_angle):
        """Check if body forms a straight line."""
        if 165 <= body_angle <= 185:
            self.feedback.append("✓✓ Perfect straight line")
        elif 155 <= body_angle < 165:
            self.feedback.append("⚠️ Slight hip sag")
            self.form_score -= 15
        elif body_angle < 155:
            self.feedback.append("❌ HIPS SAGGING - lift them up!")
            self.form_score -= 35
        elif 185 < body_angle <= 195:
            self.feedback.append("⚠️ Hips slightly high")
            self.form_score -= 10
        else:
            self.feedback.append("⚠️ Hips too high")
            self.form_score -= 20

    def _check_hip_position(self, hip, shoulder, ankle):
        """Check if hips are elevated properly."""
        # Hip should be roughly level with or above the line from shoulder to ankle
        hip_elevation = (shoulder[1] + ankle[1]) / 2 - hip[1]

        if hip_elevation > 0.1:
            self.feedback.append("⚠️ Hips too high")
            self.form_score -= 10
        elif hip_elevation < -0.1:
            self.feedback.append("❌ Lift hips up!")
            self.form_score -= 25
        else:
            self.feedback.append("✓ Good hip height")

    def _check_hip_stacking(self, upper_hip, lower_hip):
        """Check if hips are stacked (one on top of other)."""
        hip_stacking = abs(upper_hip[0] - lower_hip[0])

        if hip_stacking < 0.1:
            self.feedback.append("✓ Hips stacked well")
        else:
            self.feedback.append("⚠️ Stack hips better")
            self.form_score -= 10

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if 165 <= angle <= 185:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_side_plank else (0, 0, 255)
        pos_text = "SIDE PLANK" if self.in_side_plank else "GET IN POSITION"
        cv2.putText(image, pos_text, (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)

        if self.in_side_plank:
            if self.form_score >= 85:
                score_color = (0, 255, 0)
            elif self.form_score >= 70:
                score_color = (0, 255, 255)
            else:
                score_color = (0, 0, 255)

            cv2.putText(image, f"FORM: {self.form_score}/100",
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 3)

        # Hold time
        cv2.putText(image, f"TIME: {self.hold_time}s",
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Feedback
        y_offset = 180
        for msg in self.feedback[:4]:
            cv2.putText(image, msg, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 35
