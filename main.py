# main.py
import cv2
import mediapipe as mp
from exercises.squat import SquatAnalyzer
from exercises.pushup import PushupAnalyzer
from exercises.plank import PlankAnalyzer
from exercises.lunge import LungeAnalyzer
from exercises.deadlift import DeadliftAnalyzer
from exercises.overhead_press import OverheadPressAnalyzer
from exercises.row import RowAnalyzer
from exercises.shoulder_raise import ShoulderRaiseAnalyzer
from exercises.bicep_curl import BicepCurlAnalyzer
from exercises.tricep_extension import TricepExtensionAnalyzer

print("🏋️ FitMentor AI - Form Checker v0.2")
print("-" * 50)
print("\nSelect Exercise:")
print("1. Squat")
print("2. Push-up")
print("3. Plank")
print("4. Lunge")
print("5. Deadlift")
print("6. Overhead Press")
print("7. Bent-Over Row")
print("8. Shoulder Raise")
print("9. Bicep Curl")
print("10. Tricep Extension")
print("-" * 50)

choice = input("\nEnter number (1-10): ")

analyzers = {
    "1": ("Squat", SquatAnalyzer()),
    "2": ("Push-up", PushupAnalyzer()),
    "3": ("Plank", PlankAnalyzer()),
    "4": ("Lunge", LungeAnalyzer()),
    "5": ("Deadlift", DeadliftAnalyzer()),
    "6": ("Overhead Press", OverheadPressAnalyzer()),
    "7": ("Bent-Over Row", RowAnalyzer()),
    "8": ("Shoulder Raise", ShoulderRaiseAnalyzer()),
    "9": ("Bicep Curl", BicepCurlAnalyzer()),
    "10": ("Tricep Extension", TricepExtensionAnalyzer())
}

if choice not in analyzers:
    print("❌ Invalid choice!")
    exit()

exercise_name, analyzer = analyzers[choice]

print(f"\n✅ Starting {exercise_name} analysis...")
print("Press 'q' to quit\n")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

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
            
            image = analyzer.analyze(results.pose_landmarks, image)
        else:
            cv2.putText(image, 'No pose detected', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 255), 2)
        
        cv2.imshow(f'FitMentor - {exercise_name}', image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ {exercise_name} analysis complete!")
if hasattr(analyzer, 'rep_count'):
    print(f"Total reps: {analyzer.rep_count}")
if hasattr(analyzer, 'hold_time'):
    print(f"Hold time: {analyzer.hold_time} seconds")