def validate_squat_position(self, landmarks) -> dict:
    """
    Check if user is positioned correctly for squat analysis.
    Lenient thresholds for real-world use.
    """
    
    # Check 1: Are feet visible? (Most important)
    left_ankle = landmarks.landmark[27]
    right_ankle = landmarks.landmark[28]
    
    if left_ankle.visibility < 0.3 and right_ankle.visibility < 0.3:
        return {
            "valid": False,
            "instruction": "Step back - Cannot see your feet"
        }
    
    # Check 2: Is full body in frame? (Very lenient)
    left_shoulder = landmarks.landmark[11]
    right_shoulder = landmarks.landmark[12]
    
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    ankle_y = max(left_ankle.y, right_ankle.y)
    
    body_height = abs(ankle_y - shoulder_y)
    
    # Much more lenient body height check
    if body_height < 0.25:
        return {
            "valid": False,
            "instruction": "Step BACK - too close"
        }
    
    # That's it! Just 2 simple checks
    # If feet are visible and body isn't too close, we're good!
    return {"valid": True, "instruction": None}