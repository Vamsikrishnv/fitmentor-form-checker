# pushup_checker.py
import cv2
import mediapipe as mp
from exercises.pushup import PushupAnalyzer

print("💪 Push-up Form Checker")
print("Press 'q' to quit")
print("\nInstructions:")
print("1. Position camera to see your side profile")
print("2. Get in push-up position")
print("3. Perform push-ups!")
print("-" * 50)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

pushup_analyzer = PushupAnalyzer()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

print("✅ Starting push-up analysis...\n")

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            image = pushup_analyzer.analyze(results.pose_landmarks, image)
        else:
            cv2.putText(image, 'No pose detected', 
                       (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 255), 2)
        
        cv2.imshow('Push-up Form Checker', image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print(f"✅ Analysis complete! Total reps: {pushup_analyzer.rep_count}")