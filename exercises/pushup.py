# exercises/pushup.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class PushupAnalyzer:
    """Analyzes push-up form in real-time."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.in_pushup_position = False
        
    def analyze(self, landmarks, image):
        """Analyze push-up form."""
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get coordinates (right side)
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            
            # Calculate elbow angle (shoulder-elbow-wrist)
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            
            # Calculate body angle (shoulder-hip-knee) - for plank position
            body_angle = calculate_angle(shoulder, hip, knee)
            
            # Check if in push-up position (body relatively horizontal)
            self._check_position(shoulder, hip, ankle)
            
            if self.in_pushup_position:
                # Check form
                self._check_elbow_depth(elbow_angle)
                self._check_body_alignment(body_angle)
                
                # Count reps only if in proper position
                self._count_reps(elbow_angle)
                
                # Draw angle
                self._draw_angle(image, elbow, elbow_angle, "Elbow")
            else:
                self.feedback.append("⚠️ Get in push-up position!")
                self.feedback.append("(Body should be horizontal)")
            
            # Draw feedback
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_position(self, shoulder, hip, ankle):
        """Check if user is in push-up position (horizontal body)."""
        # If shoulder and hip are roughly same height (y-coordinate), 
        # person is likely horizontal
        vertical_diff = abs(shoulder[1] - hip[1])
        
        # Also check that person is low enough (not standing)
        avg_y = (shoulder[1] + hip[1]) / 2
        
        # In push-up position if:
        # 1. Body is relatively horizontal (small vertical difference)
        # 2. Person is in lower half of frame (not standing)
        if vertical_diff < 0.15 and avg_y > 0.3:
            self.in_pushup_position = True
        else:
            self.in_pushup_position = False
            # Reset rep counter if not in position
            self.is_down = False
    
    def _check_elbow_depth(self, elbow_angle):
        """Check if going low enough."""
        if elbow_angle > 150:
            self.feedback.append("⚠️ Not going low enough")
            self.form_score -= 20
        elif 70 <= elbow_angle <= 110:
            self.feedback.append("✅ Good depth!")
        elif elbow_angle < 70:
            self.feedback.append("⚠️ Going too low")
            self.form_score -= 10
    
    def _check_body_alignment(self, body_angle):
        """Check if body is straight (plank position)."""
        if body_angle < 160:
            self.feedback.append("❌ Hips sagging!")
            self.form_score -= 30
        elif body_angle > 200:
            self.feedback.append("❌ Hips too high!")
            self.form_score -= 30
        else:
            self.feedback.append("✅ Good alignment!")
    
    def _count_reps(self, elbow_angle):
        """Count push-up reps - only when in proper position."""
        # Down position: elbows bent significantly
        if elbow_angle < 100 and not self.is_down:
            self.is_down = True
        # Up position: arms extended
        elif elbow_angle > 150 and self.is_down:
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
        # Position status
        position_color = (0, 255, 0) if self.in_pushup_position else (0, 0, 255)
        status = "IN POSITION" if self.in_pushup_position else "NOT IN POSITION"
        cv2.putText(image, status, 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, position_color, 2)
        
        # Form score (only show if in position)
        if self.in_pushup_position:
            score_color = self._get_score_color(self.form_score)
            cv2.putText(image, f"Form: {self.form_score}/100", 
                       (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1, score_color, 2)
        
        # Rep count
        cv2.putText(image, f"Reps: {self.rep_count}", 
                   (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        # Feedback messages
        y_offset = 150
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