# exercises/squat.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class SquatAnalyzer:
    """Analyzes squat form - SIMPLE AND FAST VERSION."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        
    def analyze(self, landmarks, image):
        """Analyze squat form."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get coordinates
            hip = get_landmark_coords(landmarks, 23)
            knee = get_landmark_coords(landmarks, 25)
            ankle = get_landmark_coords(landmarks, 27)
            shoulder = get_landmark_coords(landmarks, 11)
            
            # Calculate angles
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)
            
            # Check form
            self._check_depth(knee_angle)
            self._check_back_position(hip_angle)
            
            # Count reps (simple logic)
            self._count_reps(knee_angle)
            
            # Draw
            self._draw_angle(image, knee, knee_angle, "Knee")
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_depth(self, knee_angle):
        """Check squat depth."""
        if knee_angle > 160:
            self.feedback.append("Too shallow - Go deeper!")
            self.form_score -= 30
        elif knee_angle > 140:
            self.feedback.append("Quarter squat")
            self.form_score -= 15
        elif knee_angle >= 90:
            self.feedback.append("Good depth!")
        else:
            self.feedback.append("Excellent depth!")
    
    def _check_back_position(self, hip_angle):
        """Check back position."""
        if hip_angle < 45:
            self.feedback.append("Back too bent")
            self.form_score -= 25
        elif hip_angle < 60:
            self.feedback.append("Watch back angle")
            self.form_score -= 10
    
    def _count_reps(self, knee_angle):
        """Simple rep counting."""
        if knee_angle < 120 and not self.is_down:
            self.is_down = True
        elif knee_angle > 160 and self.is_down:
            self.is_down = False
            self.rep_count += 1
    
    def _draw_angle(self, image, point, angle, label):
        """Draw angle."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)
        cv2.putText(image, f"{label}: {int(angle)}°", 
                   (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
    
    def _draw_feedback(self, image):
        """Draw feedback."""
        score_color = (0, 255, 0) if self.form_score >= 80 else (0, 255, 255) if self.form_score >= 60 else (0, 0, 255)
        
        cv2.putText(image, f"Form: {self.form_score}/100", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2)
        cv2.putText(image, f"Reps: {self.rep_count}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        y_offset = 110
        for msg in self.feedback:
            cv2.putText(image, msg, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30