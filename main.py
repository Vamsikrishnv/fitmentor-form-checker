# main.py
import os
import cv2
import math
import time
import tempfile
import numpy as np
import mediapipe as mp
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mp_pose = mp.solutions.pose

def angle_3pts(a, b, c):
    """Return angle ABC in degrees given 3 points (x, y)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) or 1e-6
    cosang = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def lm_xy(landmarks, image_w, image_h, idx):
    lm = landmarks[idx]
    return (lm.x * image_w, lm.y * image_h)

class SquatCounter:
    def __init__(self):
        self.rep_count = 0
        self.state = "up"
        self.min_knee_angle = 180.0
        self.reached_depth = False

    def update(self, left_knee_angle, right_knee_angle):
        knee = min(left_knee_angle, right_knee_angle)
        self.min_knee_angle = min(self.min_knee_angle, knee)
        
        # Track if reached deep depth (below parallel)
        if knee < 70:
            self.reached_depth = True

        if self.state == "up":
            # Must go to parallel or below (100° or less)
            if knee < 100:
                self.state = "down"
        else:  # down
            # Standing back up
            if knee > 160:
                # Only count rep if reached at least parallel depth
                if self.min_knee_angle < 110:
                    self.rep_count += 1
                # Reset for next rep
                self.state = "up"
                self.min_knee_angle = 180.0
                self.reached_depth = False

        return knee

def squat_metrics_from_landmarks(landmarks, img_w, img_h):
    L_HIP, L_KNEE, L_ANKLE = 24, 26, 28
    R_HIP, R_KNEE, R_ANKLE = 23, 25, 27

    lh = lm_xy(landmarks, img_w, img_h, L_HIP)
    lk = lm_xy(landmarks, img_w, img_h, L_KNEE)
    la = lm_xy(landmarks, img_w, img_h, L_ANKLE)

    rh = lm_xy(landmarks, img_w, img_h, R_HIP)
    rk = lm_xy(landmarks, img_w, img_h, R_KNEE)
    ra = lm_xy(landmarks, img_w, img_h, R_ANKLE)

    left_knee = angle_3pts(lh, lk, la)
    right_knee = angle_3pts(rh, rk, ra)
    return left_knee, right_knee

def score_squat(depth_hit, rep_count):
    score = 0
    if rep_count > 0:
        score = 60
        if depth_hit:
            score += 20
        score += min(20, rep_count * 2)
    return int(np.clip(score, 0, 100))

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/analyze")
async def analyze_endpoint(
    video: UploadFile = File(...),
    exercise: str = Form("squat")
):
    suffix = os.path.splitext(video.filename or "")[-1] or ".mp4"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    try:
        content = await video.read()
        tmp.write(content)
        tmp.flush()
        tmp.close()
        video_path = tmp.name

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not read video")

        frames_analyzed = 0
        feedback = []

        if exercise.lower() == "squat":
            counter = SquatCounter()
            session_depth_hits = False
            frames_analyzed = 0

            MAX_SIDE = 960
            STILL_SKIP = 3
            MOTION_SKIP = 1
            MOTION_THRESH = 8.0

            def downscale_keep_aspect(img, max_side=MAX_SIDE):
                h, w = img.shape[:2]
                side = max(h, w)
                if side <= max_side:
                    return img
                scale = max_side / side
                new_w, new_h = int(w * scale), int(h * scale)
                return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

            def keypoints_xy(landmarks, w, h):
                L_HIP, R_HIP, L_KNEE, R_KNEE = 24, 23, 26, 25
                pts = []
                for idx in (L_HIP, R_HIP, L_KNEE, R_KNEE):
                    lm = landmarks[idx]
                    pts.append((lm.x * w, lm.y * h))
                return np.array(pts, dtype=np.float32)

            cv2.ocl.setUseOpenCL(False)

            with mp_pose.Pose(
                model_complexity=2,
                enable_segmentation=False,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            ) as pose:

                i = 0
                skip_every = MOTION_SKIP
                last_pts = None

                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    i += 1

                    if skip_every > 1 and (i % skip_every) != 0:
                        continue

                    frame_ds = downscale_keep_aspect(frame, MAX_SIDE)
                    h, w = frame_ds.shape[:2]

                    rgb = cv2.cvtColor(frame_ds, cv2.COLOR_BGR2RGB)
                    rgb.flags.writeable = False
                    res = pose.process(rgb)

                    if res.pose_landmarks:
                        pts = keypoints_xy(res.pose_landmarks.landmark, w, h)
                        if last_pts is not None:
                            disp = np.linalg.norm(pts - last_pts, axis=1).mean()
                        else:
                            disp = MOTION_THRESH + 1.0
                        last_pts = pts

                        skip_every = MOTION_SKIP if disp >= MOTION_THRESH else STILL_SKIP

                        lka, rka = squat_metrics_from_landmarks(res.pose_landmarks.landmark, w, h)
                        knee = counter.update(lka, rka)
                        if knee < 70:
                            session_depth_hits = True

                        frames_analyzed += 1
                    else:
                        skip_every = MOTION_SKIP

            form_score = score_squat(session_depth_hits, counter.rep_count)

            feedback = []
            if counter.rep_count == 0:
                feedback.append("Try a full squat: descend until knee angle < 70°.")
            elif not session_depth_hits:
                feedback.append("Great effort. Aim for deeper range to improve form score.")
            if form_score >= 80:
                feedback.append("Nice control and range. Keep your chest up and core tight.")

            cap.release()
            return {
                "form_score": int(form_score),
                "rep_count": int(counter.rep_count),
                "frames_analyzed": int(frames_analyzed),
                "feedback": feedback or ["Analysis complete."],
            }
        else:
            cap.release()
            return {
                "form_score": 70,
                "rep_count": 0,
                "frames_analyzed": 0,
                "feedback": [f"'{exercise}' analyzer not implemented yet."],
            }

    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


if __name__ == "__main__":
    import mediapipe as mp
    import cv2

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
        "10": ("Tricep Extension", TricepExtensionAnalyzer()),
    }

    if choice not in analyzers:
        print("❌ Invalid choice!")
        raise SystemExit(1)

    exercise_name, analyzer = analyzers[choice]

    print(f"\n✅ Starting {exercise_name} analysis...")
    print("Press 'q' to quit\n")

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        raise SystemExit(1)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
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