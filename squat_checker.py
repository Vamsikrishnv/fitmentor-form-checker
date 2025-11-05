# squat_checker.py
import cv2
import mediapipe as mp
from exercises.squat import SquatAnalyzer

print("🏋️ Squat Form Checker")
print("Press 'q' to quit")
print("\nInstructions:")
print("1. Stand sideways to camera")
print("2. Perform squats")
print("3. Watch for real-time feedback!")
print("-" * 50)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize squat analyzer
squat_analyzer = SquatAnalyzer()

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

print("✅ Starting squat analysis...\n")

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Convert to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process pose
        results = pose.process(image)
        
        # Convert back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Analyze squat form
            image = squat_analyzer.analyze(results.pose_landmarks, image)
        else:
            cv2.putText(image, 'No pose detected - Stand sideways to camera', 
                       (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 255), 2)
        
        # Display
        cv2.imshow('Squat Form Checker', image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print("✅ Analysis complete!")