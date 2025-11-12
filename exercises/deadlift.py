# exercises/deadlift.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.angle_calculator import calculate_angle, get_landmark_coords


class DeadliftAnalyzer:
    """Advanced deadlift analyzer - SAFETY FIRST with strict back checks."""
    
    def __init__(self):
        self.form_score = 100
        self.frame_scores = []
        self.feedback_counts = {}
        self.feedback = []
        self.rep_count = 0
        self.is_down = False
        self.back_warnings = 0
        self.critical_warning = False
        
    def analyze(self, landmarks, image):
        """Analyze deadlift with strict safety checks."""
        frame_score = 100
        frame_feedback = []
        self.critical_warning = False
        
        try:
            # Get all key landmarks
            shoulder = get_landmark_coords(landmarks, 12)
            hip = get_landmark_coords(landmarks, 24)
            knee = get_landmark_coords(landmarks, 26)
            ankle = get_landmark_coords(landmarks, 28)
            ear = get_landmark_coords(landmarks, 8)
            nose = get_landmark_coords(landmarks, 0)
            
            # Calculate angles
            hip_angle = calculate_angle(shoulder, hip, knee)
            back_angle = calculate_angle(ear, shoulder, hip)
            knee_angle = calculate_angle(hip, knee, ankle)
            spine_angle = calculate_angle(nose, shoulder, hip)
            
            # CRITICAL SAFETY CHECKS FIRST
            self._check_back_safety(back_angle, spine_angle)
            
            if not self.critical_warning:
                # Additional form checks
                self._check_hip_hinge(hip_angle, knee_angle)
                self._check_bar_path(shoulder, hip, knee)
                self._check_lockout(hip_angle, knee_angle)
                
                # Rep counting
                self._count_reps(hip_angle)
            
            # Visual feedback
            self._draw_angles(image, hip, hip_angle, back_angle)
            self._draw_safety_warning(image)
            

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
    
    def _check_back_safety(self, back_angle, spine_angle):
        """CRITICAL: Check for dangerous back rounding."""
        # Back should be straight (neutral spine)
        # Angle should be 150-200° (straight line)
        
        if back_angle < 135:
            frame_feedback.append("❌ STOP! BACK ROUNDING - INJURY RISK!")
            self.form_score = 0  # Zero score for safety violation
            self.back_warnings += 1
            self.critical_warning = True
            return
        
        if back_angle < 145:
            frame_feedback.append("❌ Dangerous back position!")
            frame_score -= 50
            self.back_warnings += 1
        elif back_angle < 155:
            frame_feedback.append("⚠️ WARNING: Back rounding detected")
            frame_score -= 30
        elif 155 <= back_angle <= 200:
            frame_feedback.append("✓✓ SAFE - Back neutral")
        else:
            frame_feedback.append("⚠️ Over-extending back")
            frame_score -= 15
    
    def _check_hip_hinge(self, hip_angle, knee_angle):
        """Check proper hip-dominant movement."""
        # Deadlift is hip hinge, not squat
        # Hip should bend MORE than knees
        
        hip_bend = 180 - hip_angle
        knee_bend = 180 - knee_angle
        
        if hip_bend > knee_bend + 15:
            frame_feedback.append("✓ Good hip hinge pattern")
        elif hip_bend > knee_bend:
            frame_feedback.append("⚠️ More hip hinge needed")
            frame_score -= 10
        else:
            frame_feedback.append("❌ Too much knee bend - not a squat!")
            frame_score -= 25
    
    def _check_bar_path(self, shoulder, hip, knee):
        """Check if 'bar' stays close to body."""
        # Bar should travel vertically, close to legs
        shoulder_knee_distance = abs(shoulder[0] - knee[0])
        
        if shoulder_knee_distance > 0.2:
            frame_feedback.append("⚠️ Bar too far - stay closer")
            frame_score -= 20
        else:
            frame_feedback.append("✓ Good bar path")
    
    def _check_lockout(self, hip_angle, knee_angle):
        """Check full lockout at top."""
        # At standing position, both hips and knees should be extended
        if hip_angle > 165 and knee_angle > 165:
            # Check if truly standing (not just extended)
            if hip_angle > 170:
                frame_feedback.append("✓ Full lockout achieved")
        elif hip_angle > 140:
            frame_feedback.append("⚠️ Lock out hips at top")
            frame_score -= 10
    
    def _count_reps(self, hip_angle):
        """Count reps only with safe form."""
        # Down: bent over (hip angle < 120°)
        if hip_angle < 120 and not self.is_down:
            self.is_down = True
        # Up: standing tall (hip angle > 170°)
        elif hip_angle > 170 and self.is_down:
            self.is_down = False
            # Only count if no critical warnings
            if not self.critical_warning:
                self.rep_count += 1
    
    def _draw_angles(self, image, hip, hip_angle, back_angle):
        """Draw angles with safety color coding."""
        h, w, _ = image.shape
        x, y = int(hip[0] * w), int(hip[1] * h)
        
        # Back angle color (most important)
        if back_angle >= 155:
            back_color = (0, 255, 0)  # Safe
        elif back_angle >= 145:
            back_color = (0, 165, 255)  # Warning
        else:
            back_color = (0, 0, 255)  # Danger
        
        cv2.putText(image, f"Back: {int(back_angle)}°", 
                   (x + 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, back_color, 2)
        
        cv2.putText(image, f"Hip: {int(hip_angle)}°", 
                   (x + 20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (255, 255, 255), 2)
    
    def _draw_safety_warning(self, image):
        """Draw safety warnings prominently."""
        if self.critical_warning:
            # CRITICAL WARNING - flashing red
            cv2.rectangle(image, (0, 0), (image.shape[1], 120), (0, 0, 255), -1)
            cv2.putText(image, "⚠️ STOP IMMEDIATELY ⚠️", 
                       (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.5, (255, 255, 255), 4)
            cv2.putText(image, "BACK ROUNDING - INJURY RISK", 
                       (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, (255, 255, 255), 3)
            y_start = 140
        else:
            # Normal score display
            if self.form_score >= 85:
                score_color = (0, 255, 0)
                status = "SAFE FORM"
            elif self.form_score >= 70:
                score_color = (0, 255, 255)
                status = "ACCEPTABLE"
            else:
                score_color = (0, 165, 255)
                status = "NEEDS WORK"
            
            cv2.putText(image, f"{status}: {self.form_score}/100", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, score_color, 3)
            y_start = 90
        
        # Rep count
        cv2.putText(image, f"REPS: {self.rep_count}", 
                   (10, y_start), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        # Feedback
        y_offset = y_start + 50
        for msg in self.feedback[:4]:
            cv2.putText(image, msg, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            y_offset += 40
