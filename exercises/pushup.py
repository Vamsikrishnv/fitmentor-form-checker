# exercises/pushup.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class PushupAnalyzer:
    """Advanced push-up analyzer with precise alignment checks."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_pushup_position = False
        self.alignment_warnings = 0
        
    def analyze(self, landmarks, image):
        """Analyze push-up form with strict alignment checks."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get all key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            nose = get_landmark_coords(landmarks, 0)
            
            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            body_angle = calculate_angle(shoulder, hip, ankle)  # Full body line
            shoulder_hip_knee = calculate_angle(shoulder, hip, knee)
            
            # Check position
            self._check_position(shoulder, hip, ankle, nose)
            
            if self.in_pushup_position:
                # STRICT CHECKS
                self._check_elbow_angle(elbow_angle, elbow, shoulder)
                self._check_body_alignment(body_angle, shoulder_hip_knee)
                self._check_head_position(nose, shoulder)
                self._check_hand_placement(wrist, shoulder)
                
                # Rep counting
                self._count_reps(elbow_angle)
                
                # Draw visuals
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Get in push-up position")
            
            self._draw_form_score(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_position(self, shoulder, hip, ankle, nose):
        """Check if in proper push-up starting position."""
        vertical_diff = abs(shoulder[1] - hip[1])
        avg_y = (shoulder[1] + hip[1]) / 2
        
        # Must be horizontal and low
        if vertical_diff < 0.15 and avg_y > 0.35:
            self.in_pushup_position = True
        else:
            self.in_pushup_position = False
            self.is_down = False
    
    def _check_elbow_angle(self, elbow_angle, elbow, shoulder):
        """Strict elbow depth and flare check."""
        # Check depth
        if elbow_angle > 160:
            self.feedback.append("❌ Not low enough - go deeper")
            self.form_score -= 30
        elif elbow_angle > 140:
            self.feedback.append("⚠️ Shallow push-up")
            self.form_score -= 20
        elif 75 <= elbow_angle <= 95:
            self.feedback.append("✓✓ Perfect depth (90°)")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Too low - chest hitting ground")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good depth")
        
        # Check elbow flare (should be ~45° from body, not 90°)
        elbow_shoulder_diff = abs(elbow[0] - shoulder[0])
        if elbow_shoulder_diff > 0.25:
            self.feedback.append("⚠️ Elbows flaring out too much")
            self.form_score -= 15
    
    def _check_body_alignment(self, body_angle, shoulder_hip_knee):
        """Check if body is straight line (no sagging or piking)."""
        # Body should be straight (angle ~160-180°)
        if body_angle < 155:
            self.feedback.append("❌ HIPS SAGGING - engage core!")
            self.form_score -= 35
            self.alignment_warnings += 1
        elif body_angle < 165:
            self.feedback.append("⚠️ Slight hip sag")
            self.form_score -= 15
        elif body_angle > 195:
            self.feedback.append("❌ HIPS TOO HIGH - lower them")
            self.form_score -= 30
            self.alignment_warnings += 1
        elif body_angle > 185:
            self.feedback.append("⚠️ Hips slightly high")
            self.form_score -= 10
        else:
            self.feedback.append("✓✓ Perfect plank position")
    
    def _check_head_position(self, nose, shoulder):
        """Check head/neck alignment."""
        # Head should be roughly in line with spine
        head_drop = nose[1] - shoulder[1]
        
        if head_drop > 0.15:
            self.feedback.append("⚠️ Head too low - look ahead")
            self.form_score -= 10
        elif head_drop < -0.05:
            self.feedback.append("⚠️ Chin up - neutral neck")
            self.form_score -= 5
    
    def _check_hand_placement(self, wrist, shoulder):
        """Check if hands are shoulder-width."""
        hand_width = abs(wrist[0] - shoulder[0])
        
        if hand_width < 0.05:
            self.feedback.append("⚠️ Hands too narrow")
            self.form_score -= 10
        elif hand_width > 0.25:
            self.feedback.append("⚠️ Hands too wide")
            self.form_score -= 10
    
    def _count_reps(self, elbow_angle):
        """Count reps with strict standards."""
        # Down: must go below 100° (strict)
        if elbow_angle < 100 and not self.is_down:
            self.is_down = True
        # Up: arms must be mostly extended
        elif elbow_angle > 155 and self.is_down:
            self.is_down = False
            self.rep_count += 1
    
    def _draw_angle(self, image, point, angle, label):
        """Draw angle with color coding."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)
        
        # Color based on angle
        if 75 <= angle <= 95:
            color = (0, 255, 0)  # Perfect
        elif 100 <= angle <= 140:
            color = (0, 255, 255)  # Okay
        else:
            color = (0, 0, 255)  # Bad
        
        cv2.putText(image, f"{label}: {int(angle)}°", 
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, color, 2)
    
    def _draw_form_score(self, image):
        """Draw score and feedback."""
        # Position indicator
        pos_color = (0, 255, 0) if self.in_pushup_position else (0, 0, 255)
        pos_text = "PUSH-UP POSITION" if self.in_pushup_position else "GET IN POSITION"
        cv2.putText(image, pos_text, (10, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, pos_color, 2)
        
        if self.in_pushup_position:
            # Form score
            if self.form_score >= 85:
                score_color = (0, 255, 0)
            elif self.form_score >= 70:
                score_color = (0, 255, 255)
            else:
                score_color = (0, 0, 255)
            
            cv2.putText(image, f"FORM: {self.form_score}/100", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 3)
        
        # Reps
        cv2.putText(image, f"REPS: {self.rep_count}", 
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Feedback
        y_offset = 180
        for msg in self.feedback[:4]:
            cv2.putText(image, msg, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 35
