# exercises/deadlift.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class DeadliftAnalyzer:
    """Analyzes deadlift form in real-time."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        
    def analyze(self, landmarks, image):
        """Analyze deadlift form."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get coordinates (side view)
            shoulder = get_landmark_coords(landmarks, 12)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            ear = get_landmark_coords(landmarks, 8)
            
            # Calculate hip angle (shoulder-hip-knee)
            hip_angle = calculate_angle(shoulder, hip, knee)
            
            # Calculate back angle (ear-shoulder-hip)
            back_angle = calculate_angle(ear, shoulder, hip)
            
            # Calculate knee angle (hip-knee-ankle)
            knee_angle = calculate_angle(hip, knee, ankle)
            
            # Check form
            self._check_back_position(back_angle)
            self._check_hip_hinge(hip_angle, knee_angle)
            self._check_starting_position(hip, knee)
            
            # Count reps
            self._count_reps(hip_angle)
            
            # Draw angles
            self._draw_angle(image, hip, hip_angle, "Hip")
            self._draw_angle(image, shoulder, back_angle, "Back")
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_back_position(self, back_angle):
        """Check if back is straight (CRITICAL for safety)."""
        if 150 <= back_angle <= 200:
            self.feedback.append("✅ Back straight - SAFE!")
        elif back_angle < 150:
            self.feedback.append("❌ BACK ROUNDING - DANGER!")
            self.form_score -= 50  # Heavy penalty for back rounding
        else:
            self.feedback.append("⚠️ Leaning too far back")
            self.form_score -= 15
    
    def _check_hip_hinge(self, hip_angle, knee_angle):
        """Check proper hip hinge movement."""
        # Deadlift is hip-dominant (not squat)
        # Hip should bend more than knees
        if hip_angle < knee_angle - 20:
            self.feedback.append("✅ Good hip hinge!")
        else:
            self.feedback.append("⚠️ More hip hinge, less squat")
            self.form_score -= 15
    
    def _check_starting_position(self, hip, knee):
        """Check if starting low enough."""
        # Hip should be below shoulder level at start
        if hip[1] > knee[1]:
            self.feedback.append("✅ Good starting position!")
        else:
            self.feedback.append("⚠️ Start lower (bend more)")
            self.form_score -= 10
    
    def _count_reps(self, hip_angle):
        """Count deadlift reps."""
        # Down position (bent over)
        if hip_angle < 120 and not self.is_down:
            self.is_down = True
        # Up position (standing)
        elif hip_angle > 160 and self.is_down:
            self.is_down = False
            self.rep_count += 1
    
    def _draw_angle(self, image, point, angle, label):
        """Draw angle on image."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)
        
        cv2.putText(image, f"{label}: {int(angle)}°", 
                   (x + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
    
    def _draw_feedback(self, image):
        """Draw feedback on image."""
        # SAFETY WARNING if back rounding
        if self.form_score < 60:
            cv2.putText(image, "⚠️ UNSAFE FORM - STOP! ⚠️", 
                       (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, (0, 0, 255), 3)
            y_start = 80
        else:
            y_start = 30
        
        # Form score
        score_color = self._get_score_color(self.form_score)
        cv2.putText(image, f"Form Score: {self.form_score}/100", 
                   (10, y_start), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, score_color, 2)
        
        # Rep count
        cv2.putText(image, f"Reps: {self.rep_count}", 
                   (10, y_start + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        # Feedback messages
        y_offset = y_start + 80
        for msg in self.feedback:
            cv2.putText(image, msg, 
                       (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 255, 255), 2)
            y_offset += 30
    
    def _get_score_color(self, score):
        """Get color based on score."""
        if score >= 80:
            return (0, 255, 0)  # Green
        elif score >= 60:
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red