# exercises/lunge.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class LungeAnalyzer:
    """Analyzes lunge form in real-time."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        
    def analyze(self, landmarks, image):
        """Analyze lunge form."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get coordinates for both legs
            left_hip = get_landmark_coords(landmarks, 23)
            left_knee = get_landmark_coords(landmarks, 25)
            left_ankle = get_landmark_coords(landmarks, 27)
            
            right_hip = get_landmark_coords(landmarks, 24)
            right_knee = get_landmark_coords(landmarks, 26)
            right_ankle = get_landmark_coords(landmarks, 28)
            
            # Calculate knee angles for both legs
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
            
            # Determine which leg is front (more bent = front leg)
            if left_knee_angle < right_knee_angle:
                # Left leg is front
                front_knee_angle = left_knee_angle
                back_knee_angle = right_knee_angle
                front_knee = left_knee
            else:
                # Right leg is front
                front_knee_angle = right_knee_angle
                back_knee_angle = left_knee_angle
                front_knee = right_knee
            
            # Check form
            self._check_front_knee(front_knee_angle)
            self._check_back_knee(back_knee_angle)
            self._check_depth(front_knee_angle)
            
            # Count reps
            self._count_reps(front_knee_angle)
            
            # Draw angles
            self._draw_angle(image, front_knee, front_knee_angle, "Front")
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_front_knee(self, front_knee_angle):
        """Check front knee position."""
        if 70 <= front_knee_angle <= 110:
            self.feedback.append("✅ Good front knee angle!")
        elif front_knee_angle < 70:
            self.feedback.append("❌ Front knee too bent")
            self.form_score -= 20
        else:
            self.feedback.append("⚠️ Go deeper!")
            self.form_score -= 15
    
    def _check_back_knee(self, back_knee_angle):
        """Check back knee position."""
        if 140 <= back_knee_angle <= 180:
            self.feedback.append("✅ Good back leg extension!")
        else:
            self.feedback.append("⚠️ Extend back leg more")
            self.form_score -= 10
    
    def _check_depth(self, front_knee_angle):
        """Check lunge depth."""
        if front_knee_angle < 90:
            self.feedback.append("✅ Excellent depth!")
        elif front_knee_angle < 120:
            self.feedback.append("✅ Good depth!")
        else:
            self.feedback.append("❌ Too shallow - Go lower!")
            self.form_score -= 25
    
    def _count_reps(self, front_knee_angle):
        """Count lunge reps."""
        # Down position
        if front_knee_angle < 100 and not self.is_down:
            self.is_down = True
        # Up position
        elif front_knee_angle > 150 and self.is_down:
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
        # Form score
        score_color = self._get_score_color(self.form_score)
        cv2.putText(image, f"Form Score: {self.form_score}/100", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, score_color, 2)
        
        # Rep count
        cv2.putText(image, f"Reps: {self.rep_count}", 
                   (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        # Feedback messages
        y_offset = 110
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