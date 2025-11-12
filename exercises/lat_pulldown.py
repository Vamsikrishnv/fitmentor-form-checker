# exercises/lat_pulldown.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class LatPulldownAnalyzer:
    """Lat pulldown analyzer for lat and back development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_pulled = False
        self.in_position = False

    def analyze(self, landmarks, image):
        """Analyze lat pulldown form with focus on pulling pattern."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)

            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            torso_angle = calculate_angle(shoulder, hip, get_landmark_coords(landmarks, 26))

            # Check if in seated position
            self._check_position(shoulder, hip)

            if self.in_position:
                # Check elbow angle
                self._check_elbow_angle(elbow_angle)

                # Check pull depth (elbows should go behind torso)
                self._check_pull_depth(elbow, shoulder)

                # Check torso position (slight lean back is OK)
                self._check_torso_angle(torso_angle)

                # Check wrist position
                self._check_wrist_position(wrist, shoulder)

                # Rep counting
                self._count_reps(elbow_angle)

                # Draw visuals
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Get in seated position")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, shoulder, hip):
        """Check if in proper seated position."""
        # Person should be roughly upright/seated
        vertical_alignment = abs(shoulder[0] - hip[0])

        if vertical_alignment < 0.2:
            self.in_position = True
        else:
            self.in_position = False
            self.is_pulled = False

    def _check_elbow_angle(self, elbow_angle):
        """Check elbow angle during pulldown."""
        if elbow_angle > 160:
            self.feedback.append("⚠️ Pull the bar down")
            self.form_score -= 20
        elif 60 <= elbow_angle <= 100:
            self.feedback.append("✓✓ Perfect pull depth")
        elif elbow_angle < 60:
            self.feedback.append("⚠️ Don't over-pull")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good pull")

    def _check_pull_depth(self, elbow, shoulder):
        """Check if pulling deep enough (elbows behind shoulders)."""
        # Elbows should move behind the shoulder line
        elbow_behind = elbow[0] > shoulder[0] if shoulder[0] < 0.5 else elbow[0] < shoulder[0]

        if elbow_behind:
            self.feedback.append("✓ Full range of motion")
        else:
            self.feedback.append("⚠️ Pull elbows back more")
            self.form_score -= 15

    def _check_torso_angle(self, torso_angle):
        """Check torso position (slight lean back OK, but not excessive)."""
        if 150 <= torso_angle <= 180:
            self.feedback.append("✓ Good torso position")
        elif torso_angle < 140:
            self.feedback.append("⚠️ Don't lean back too much")
            self.form_score -= 15
        elif torso_angle > 190:
            self.feedback.append("⚠️ Lean back slightly")
            self.form_score -= 10

    def _check_wrist_position(self, wrist, shoulder):
        """Check if bar is pulled to proper height (chest level)."""
        wrist_shoulder_diff = wrist[1] - shoulder[1]

        if -0.05 <= wrist_shoulder_diff <= 0.15:
            self.feedback.append("✓ Bar at chest level")
        elif wrist_shoulder_diff < -0.05:
            self.feedback.append("⚠️ Don't pull bar too high")
            self.form_score -= 10
        else:
            self.feedback.append("⚠️ Pull bar lower to chest")
            self.form_score -= 15

    def _count_reps(self, elbow_angle):
        """Count reps."""
        if elbow_angle < 100 and not self.is_pulled:
            self.is_pulled = True
        elif elbow_angle > 150 and self.is_pulled:
            self.is_pulled = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if 60 <= angle <= 100:
            color = (0, 255, 0)
        elif 100 < angle <= 140:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_position else (0, 0, 255)
        pos_text = "LAT PULLDOWN" if self.in_position else "GET IN POSITION"
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
