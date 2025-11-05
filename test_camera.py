# test_camera.py
import cv2

print("🎥 Testing webcam capture...")
print("Press 'q' to quit")

# Initialize webcam (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

print("✅ Webcam opened successfully!")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("❌ Error: Can't receive frame")
        break
    
    # Display the frame
    cv2.imshow('FitMentor - Camera Test', frame)
    
    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything
cap.release()
cv2.destroyAllWindows()

print("✅ Camera test complete!")