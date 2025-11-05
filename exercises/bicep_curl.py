# exercises/bicep_curl.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class BicepCurlAnalyzer:
    def __init__(self):
        self.form_score = 100
        self.feedback = []
        self.rep_count = 0
        self.is_curled = False
        
    def analyze(self, landmarks, image):
        self.form_score = 100
        self.feedback = []
        
        try:
            shoulder = get_landmark_coords(landmarks, 12)
            elbow = get_landmark_coords(landmarks, 14)
            wrist = get_landmark_coords(landmarks, 16)
            
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            
            if elbow_angle < 60:
                self.feedback.append("✅ Full curl!")
            elif elbow_angle < 80:
                self.feedback.append("✅ Good curl!")
            else:
                self.feedback.append("⚠️ Curl higher!")
                self.form_score -= 15
            
            self._count_reps(elbow_angle)
            self._draw_feedback(image)
            
        except Exception as e:
            self.feedback.append(f"Error: {str(e)}")
            
        return image
    
    def _count_reps(self, elbow_angle):
        if elbow_angle < 70 and not self.is_curled:
            self.is_curled = True
            self.rep_count += 1
        elif elbow_angle > 140 and self.is_curled:
            self.is_curled = False
    
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