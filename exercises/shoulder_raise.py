# exercises/shoulder_raise.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class ShoulderRaiseAnalyzer:
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_raised = False
        
    def analyze(self, landmarks, image):
        self.form_score = 100
        self.feedback = []
        
        try:
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            hip = get_landmark_coords(landmarks, 24)
            
            # Arm angle from body
            arm_angle = calculate_angle(hip, shoulder, elbow)
            
            if 70 <= arm_angle <= 110:
                self.feedback.append("✅ Perfect height!")
            elif arm_angle < 70:
                self.feedback.append("⚠️ Raise higher!")
                self.form_score -= 20
            else:
                self.feedback.append("⚠️ Don't go too high!")
                self.form_score -= 10
            
            self._count_reps(arm_angle)
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _count_reps(self, arm_angle):
        if 70 <= arm_angle <= 110 and not self.is_raised:
            self.is_raised = True
            self.rep_count += 1
        elif arm_angle < 30 and self.is_raised:
            self.is_raised = False
    
    def _draw_feedback(self, image):
        score_color = (0, 255, 0) if self.form_score >= 80 else (0, 0, 255)
        cv2.putText(image, f"Form: {self.form_score}/100", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2)
        cv2.putText(image, f"Reps: {self.rep_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        y_offset = 110
        for msg in self.feedback:
            cv2.putText(image, msg, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30