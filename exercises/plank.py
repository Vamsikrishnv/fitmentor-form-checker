# exercises/plank.py
import cv2
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class PlankAnalyzer:
    """Analyzes plank form in real-time."""
    
    def __init__(self):
        self.form_score = 100
        self.frame_scores = []
        self.feedback_counts = {}
        self.feedback = []
        self.start_time = None
        self.hold_time = 0
        self.in_plank_position = False
        
    def analyze(self, landmarks, image):
        """Analyze plank form."""
        frame_score = 100
        frame_feedback = []
        
        try:
            # Get coordinates
            shoulder = get_landmark_coords(landmarks, 12)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            elbow = get_landmark_coords(landmarks, 14)
            
            # Calculate body angle (shoulder-hip-ankle)
            body_angle = calculate_angle(shoulder, hip, ankle)
            
            # Check if in plank position
            self._check_position(shoulder, hip, elbow)
            
            if self.in_plank_position:
                # Start timer
                if self.start_time is None:
                    self.start_time = time.time()
                
                # Calculate hold time
                self.hold_time = int(time.time() - self.start_time)
                
                # Check form
                self._check_body_alignment(body_angle)
                self._check_hip_position(hip, shoulder, ankle)
                
            else:
                frame_feedback.append("⚠️ Get in plank position!")
                self.start_time = None
                self.hold_time = 0
            
            # Draw feedback
            self._draw_feedback(image)

            # Store frame score
            self.frame_scores.append(max(0, frame_score))

            # Accumulate feedback
            for msg in frame_feedback:
                self.feedback_counts[msg] = self.feedback_counts.get(msg, 0) + 1

            # Calculate average score
            if self.frame_scores:
                self.form_score = int(sum(self.frame_scores) / len(self.frame_scores))

            # Get most common feedback
            if self.feedback_counts:
                sorted_feedback = sorted(self.feedback_counts.items(), key=lambda x: x[1], reverse=True)
                self.feedback = [msg for msg, count in sorted_feedback[:4]]

        except Exception as e:
            frame_feedback.append(f"Error: {str(e)}")

        return image
    
    def _check_position(self, shoulder, hip, elbow):
        """Check if in plank position."""
        # Body should be horizontal
        vertical_diff = abs(shoulder[1] - hip[1])
        
        # Should be on forearms (elbow below shoulder)
        on_forearms = elbow[1] > shoulder[1]
        
        # In lower portion of screen
        avg_y = (shoulder[1] + hip[1]) / 2
        
        if vertical_diff < 0.2 and avg_y > 0.3 and on_forearms:
            self.in_plank_position = True
        else:
            self.in_plank_position = False
    
    def _check_body_alignment(self, body_angle):
        """Check if body forms straight line."""
        if 160 <= body_angle <= 200:
            frame_feedback.append("✅ Perfect alignment!")
        elif body_angle < 160:
            frame_feedback.append("❌ Hips sagging - Engage core!")
            frame_score -= 30
        else:
            frame_feedback.append("❌ Hips too high - Lower them!")
            frame_score -= 25
    
    def _check_hip_position(self, hip, shoulder, ankle):
        """Check hip height relative to body."""
        # Hip should be roughly in line with shoulder and ankle
        hip_deviation = abs(hip[1] - ((shoulder[1] + ankle[1]) / 2))
        
        if hip_deviation > 0.1:
            frame_feedback.append("⚠️ Keep hips level!")
            frame_score -= 15
    
    def _draw_feedback(self, image):
        """Draw feedback on image."""
        # Position status
        position_color = (0, 255, 0) if self.in_plank_position else (0, 0, 255)
        status = "HOLDING PLANK" if self.in_plank_position else "NOT IN POSITION"
        cv2.putText(image, status, 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, position_color, 3)
        
        # Hold time (big and prominent!)
        if self.in_plank_position:
            cv2.putText(image, f"Time: {self.hold_time}s", 
                       (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1.5, (0, 255, 255), 3)
            
            # Form score
            score_color = self._get_score_color(self.form_score)
            cv2.putText(image, f"Form: {self.form_score}/100", 
                       (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1, score_color, 2)
        
        # Feedback messages
        y_offset = 170
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