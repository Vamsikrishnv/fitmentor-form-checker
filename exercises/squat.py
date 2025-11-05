# exercises/squat.py
import cv2
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class SquatAnalyzer:
    """Analyzes squat form in real-time."""
    
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        
    def analyze(self, landmarks, image):
        """
        Analyze squat form from pose landmarks.
        
        Args:
            landmarks: MediaPipe pose landmarks
            image: Current video frame
            
        Returns:
            Annotated image with feedback
        """
        self.form_score = 100
        self.feedback = []
        
        try:
            # Get coordinates for left side
            hip = get_landmark_coords(landmarks, 23)
            knee = get_landmark_coords(landmarks, 25)
            ankle = get_landmark_coords(landmarks, 27)
            shoulder = get_landmark_coords(landmarks, 11)
            
            # Calculate knee angle (hip-knee-ankle)
            knee_angle = calculate_angle(hip, knee, ankle)
            
            # Calculate hip angle (shoulder-hip-knee)
            hip_angle = calculate_angle(shoulder, hip, knee)
            
            # Analyze form
            self._check_depth(knee_angle)
            self._check_back_position(hip_angle)
            
            # Draw angles on image
            self._draw_angle(image, knee, knee_angle, "Knee")
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _check_depth(self, knee_angle):
        """Check if squat depth is adequate."""
        if knee_angle > 160:
            self.feedback.append("❌ Too shallow - Go deeper!")
            self.form_score -= 30
        elif knee_angle > 140:
            self.feedback.append("⚠️ Quarter squat - Try to go lower")
            self.form_score -= 15
        elif knee_angle >= 90:
            self.feedback.append("✅ Good depth!")
        else:
            self.feedback.append("✅ Excellent depth!")
    
    def _check_back_position(self, hip_angle):
        """Check if back position is safe."""
        if hip_angle < 45:
            self.feedback.append("❌ Back too bent - Stand more upright")
            self.form_score -= 25
        elif hip_angle < 60:
            self.feedback.append("⚠️ Watch your back angle")
            self.form_score -= 10
    
    def _draw_angle(self, image, point, angle, label):
        """Draw angle value on image."""
        h, w, _ = image.shape
        x, y = int(point[0] * w), int(point[1] * h)
        
        cv2.putText(image, f"{label}: {int(angle)}°", 
                   (x + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
    
    def _draw_feedback(self, image):
        """Draw feedback and score on image."""
        h, w, _ = image.shape
        
        # Draw form score
        score_color = self._get_score_color(self.form_score)
        cv2.putText(image, f"Form Score: {self.form_score}/100", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, score_color, 2)
        
        # Draw feedback messages
        y_offset = 70
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