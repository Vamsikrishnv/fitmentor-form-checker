# exercises/bulgarian_split_squat.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class BulgarianSplitSquatAnalyzer:
    """Bulgarian split squat analyzer for unilateral leg development."""

    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_position = False

    def analyze(self, landmarks, image):
        """Analyze Bulgarian split squat form with focus on front leg mechanics."""
        self.form_score = 100
        self.feedback = []

        try:
            # Get key landmarks
            left_hip = get_landmark_coords(landmarks, 23)
            right_hip = get_landmark_coords(landmarks, 24)
            left_knee = get_landmark_coords(landmarks, 25)
            right_knee = get_landmark_coords(landmarks, 26)
            left_ankle = get_landmark_coords(landmarks, 27)
            right_ankle = get_landmark_coords(landmarks, 28)
            shoulder = get_landmark_coords(landmarks, 12)

            # Determine which leg is forward (lower ankle)
            if left_ankle[1] > right_ankle[1]:
                # Left leg is forward
                front_hip, front_knee, front_ankle = left_hip, left_knee, left_ankle
                back_hip, back_knee, back_ankle = right_hip, right_knee, right_ankle
            else:
                # Right leg is forward
                front_hip, front_knee, front_ankle = right_hip, right_knee, right_ankle
                back_hip, back_knee, back_ankle = left_hip, left_knee, left_ankle

            # Calculate angles
            front_knee_angle = calculate_angle(front_hip, front_knee, front_ankle)
            back_knee_angle = calculate_angle(back_hip, back_knee, back_ankle)
            torso_angle = calculate_angle(shoulder, front_hip, front_knee)

            # Check if in split stance
            self._check_position(front_ankle, back_ankle)

            if self.in_position:
                # Check front knee angle (depth)
                self._check_front_knee_angle(front_knee_angle)

                # Check front knee tracking
                self._check_knee_tracking(front_knee, front_ankle)

                # Check torso position
                self._check_torso_position(torso_angle)

                # Check balance
                self._check_balance(shoulder, front_ankle)

                # Rep counting
                self._count_reps(front_knee_angle)

                # Draw visuals
                self._draw_angle(image, front_knee, front_knee_angle, "Front Knee")
            else:
                self.feedback.append("⚠️ Get in split stance position")

            self._draw_form_score(image)

        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")

        return image

    def _check_position(self, front_ankle, back_ankle):
        """Check if in proper split stance."""
        # Front and back foot should be separated
        foot_separation = abs(front_ankle[1] - back_ankle[1])

        if foot_separation > 0.15:
            self.in_position = True
        else:
            self.in_position = False
            self.is_down = False

    def _check_front_knee_angle(self, knee_angle):
        """Check front knee depth."""
        if knee_angle > 140:
            self.feedback.append("❌ Not deep enough - lower down")
            self.form_score -= 25
        elif knee_angle > 120:
            self.feedback.append("⚠️ Go deeper for better results")
            self.form_score -= 15
        elif 75 <= knee_angle <= 95:
            self.feedback.append("✓✓ Perfect depth (90°)")
        elif knee_angle < 70:
            self.feedback.append("⚠️ Too deep")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good depth")

    def _check_knee_tracking(self, knee, ankle):
        """Check if knee stays over ankle."""
        knee_forward = knee[0] - ankle[0]

        if abs(knee_forward) < 0.05:
            self.feedback.append("✓ Good knee tracking")
        elif abs(knee_forward) > 0.15:
            self.feedback.append("⚠️ Knee too far forward")
            self.form_score -= 20
        else:
            self.feedback.append("⚠️ Watch knee position")
            self.form_score -= 10

    def _check_torso_position(self, torso_angle):
        """Check torso upright position."""
        if 160 <= torso_angle <= 190:
            self.feedback.append("✓ Torso upright")
        elif torso_angle < 150:
            self.feedback.append("⚠️ Leaning too far forward")
            self.form_score -= 15
        else:
            self.feedback.append("⚠️ Leaning back too much")
            self.form_score -= 10

    def _check_balance(self, shoulder, front_ankle):
        """Check if maintaining balance over front foot."""
        lateral_offset = abs(shoulder[0] - front_ankle[0])

        if lateral_offset > 0.15:
            self.feedback.append("⚠️ Balance over front foot")
            self.form_score -= 10

    def _count_reps(self, knee_angle):
        """Count reps."""
        if knee_angle < 100 and not self.is_down:
            self.is_down = True
        elif knee_angle > 130 and self.is_down:
            self.is_down = False
            self.rep_count += 1

    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)

        if 75 <= angle <= 95:
            color = (0, 255, 0)
        elif 95 < angle <= 120:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.putText(image, f"{label}: {int(angle)}°",
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, color, 2)

    def _draw_form_score(self, image):
        """Draw score and feedback."""
        pos_color = (0, 255, 0) if self.in_position else (0, 0, 255)
        pos_text = "BULGARIAN SPLIT SQUAT" if self.in_position else "GET IN SPLIT STANCE"
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
