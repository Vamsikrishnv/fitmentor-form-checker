# exercises/squat.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class SquatAnalyzer:
    """Advanced squat form analyzer with strict biomechanics checks."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.depth_warning = 0
        self.knee_warning = 0
        
    def analyze(self, landmarks, image):
        """Analyze squat form with detailed checks."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get all key landmarks
            left_hip = get_landmark_coords(landmarks, 23)
            left_knee = get_landmark_coords(landmarks, 25)
            left_ankle = get_landmark_coords(landmarks, 27)
            left_shoulder = get_landmark_coords(landmarks, 11)
            right_hip = get_landmark_coords(landmarks, 24)
            right_knee = get_landmark_coords(landmarks, 26)
            
            # Calculate angles
            knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)
            
            # STRICT CHECKS
            self._check_depth(knee_angle, left_hip, left_knee)
            self._check_knee_tracking(left_knee, left_ankle, left_hip)
            self._check_back_angle(hip_angle)
            self._check_balance(left_knee, right_knee)
            
            # Rep counting
            self._count_reps(knee_angle)
            
            # Visual feedback
            self._draw_angles(image, left_knee, knee_angle)
            self._draw_form_score(image)
            
        except Exception as e:
            self.feedback.append(f"Analysis error: {str(e)}")
            
        return image
    
    def _check_depth(self, knee_angle, hip, knee):
        """Strict depth check - hip must go below knee."""
        # Check if hip is below knee (proper depth)
        hip_below_knee = hip[1] > knee[1]
        
        if knee_angle > 160:
            self.feedback.append("❌ Too shallow - barely squatting")
            self.form_score -= 40
            self.depth_warning += 1
        elif knee_angle > 140:
            self.feedback.append("⚠️ Quarter squat - go deeper")
            self.form_score -= 25
        elif knee_angle > 100:
            self.feedback.append("✓ Parallel depth - good!")
            if not hip_below_knee:
                self.form_score -= 5
        elif knee_angle >= 70:
            self.feedback.append("✓✓ Below parallel - excellent!")
        else:
            self.feedback.append("⚠️ Too deep - risk of injury")
            self.form_score -= 15
    
    def _check_knee_tracking(self, knee, ankle, hip):
        """Check if knees track over toes (not caving in)."""
        # Knee should be roughly above ankle
        knee_forward = abs(knee[0] - ankle[0])
        
        if knee_forward > 0.15:  # Knees too far forward
            self.feedback.append("⚠️ Knees too far forward")
            self.form_score -= 20
            self.knee_warning += 1
        
        # Check for knee valgus (knees caving in)
        knee_ankle_distance = abs(knee[0] - ankle[0])
        if knee_ankle_distance > 0.2:
            self.feedback.append("❌ Knees caving in - push out!")
            self.form_score -= 30
    
    def _check_back_angle(self, hip_angle):
        """Check back position - should stay relatively upright."""
        if hip_angle < 40:
            self.feedback.append("❌ Back too bent - injury risk!")
            self.form_score -= 35
        elif hip_angle < 55:
            self.feedback.append("⚠️ Back angle needs work")
            self.form_score -= 15
        elif hip_angle > 85:
            self.feedback.append("⚠️ Too upright - might fall back")
            self.form_score -= 10
        else:
            self.feedback.append("✓ Good back position")
    
    def _check_balance(self, left_knee, right_knee):
        """Check if knees are level (balanced squat)."""
        knee_diff = abs(left_knee[1] - right_knee[1])
        
        if knee_diff > 0.05:
            self.feedback.append("⚠️ Uneven - check balance")
            self.form_score -= 10
    
    def _count_reps(self, knee_angle):
        """Count reps only if depth is good."""
        if knee_angle < 110 and not self.is_down:  # Stricter depth requirement
            self.is_down = True
        elif knee_angle > 160 and self.is_down:
            self.is_down = False
            self.rep_count += 1
    
    def _draw_angles(self, image, knee, angle):
        """Draw angle visualization."""
        h, w, _ = image.shape
        x, y = int(knee[0] * w), int(knee[1] * h)
        
        # Color based on angle
        if angle < 100:
            color = (0, 255, 0)  # Green - good depth
        elif angle < 140:
            color = (0, 255, 255)  # Yellow - okay
        else:
            color = (0, 0, 255)  # Red - too shallow
        
        cv2.putText(image, f"Knee: {int(angle)}°", 
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, color, 2)
    
    def _draw_form_score(self, image):
        """Draw score and feedback."""
        # Score color
        if self.form_score >= 85:
            score_color = (0, 255, 0)  # Green
        elif self.form_score >= 70:
            score_color = (0, 255, 255)  # Yellow
        else:
            score_color = (0, 0, 255)  # Red
        
        # Draw score
        cv2.putText(image, f"FORM: {self.form_score}/100", 
                   (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 3)
        
        # Draw rep count
        cv2.putText(image, f"REPS: {self.rep_count}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw feedback
        y_offset = 140
        for msg in self.feedback[:4]:  # Limit to 4 messages
            cv2.putText(image, msg, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 35
