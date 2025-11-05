# utils/angle_calculator.py
import numpy as np

def calculate_angle(a, b, c):
    """
    Calculate angle between three points.
    
    Args:
        a: First point [x, y]
        b: Mid point [x, y] (vertex of angle)
        c: End point [x, y]
    
    Returns:
        Angle in degrees (0-180)
    """
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point (vertex)
    c = np.array(c)  # End point
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle using dot product
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)


def get_landmark_coords(landmarks, landmark_id):
    """
    Extract x, y coordinates from a landmark.
    
    Args:
        landmarks: MediaPipe pose landmarks
        landmark_id: ID of the landmark (0-32)
    
    Returns:
        [x, y] coordinates
    """
    landmark = landmarks.landmark[landmark_id]
    return [landmark.x, landmark.y]