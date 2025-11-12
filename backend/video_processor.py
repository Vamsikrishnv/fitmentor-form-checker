# backend/video_processor.py
import cv2
import mediapipe as mp
import tempfile
import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

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


class VideoProcessor:
    """Process uploaded videos and analyze exercise form."""
    
    ANALYZERS = {
        "squat": SquatAnalyzer,
        "pushup": PushupAnalyzer,
        "plank": PlankAnalyzer,
        "lunge": LungeAnalyzer,
        "deadlift": DeadliftAnalyzer,
        "overhead_press": OverheadPressAnalyzer,
        "row": RowAnalyzer,
        "shoulder_raise": ShoulderRaiseAnalyzer,
        "bicep_curl": BicepCurlAnalyzer,
        "tricep_extension": TricepExtensionAnalyzer
    }
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
    
    async def analyze_video(self, video_content: bytes, exercise_type: str, max_duration: int = 300):
        """
        Analyze a video file for exercise form.

        Args:
            video_content: Video file content as bytes
            exercise_type: Type of exercise (squat, pushup, etc.)
            max_duration: Maximum video duration in seconds (default: 300)

        Returns:
            dict: Analysis results
        """

        if exercise_type not in self.ANALYZERS:
            return {
                "success": False,
                "message": f"Unknown exercise type: {exercise_type}",
                "exercise": exercise_type,
                "form_score": 0,
                "rep_count": 0,
                "feedback": []
            }

        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(video_content)
        temp_file.close()
        
        try:
            # Initialize analyzer
            analyzer = self.ANALYZERS[exercise_type]()
            
            # Process video
            cap = cv2.VideoCapture(temp_file.name)

            if not cap.isOpened():
                return {
                    "success": False,
                    "message": "Could not open video file",
                    "exercise": exercise_type,
                    "form_score": 0,
                    "rep_count": 0,
                    "feedback": []
                }

            # Check video duration
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            logger.info(f"Video stats: duration={duration:.1f}s, fps={fps}, frames={total_frames}")

            if duration > max_duration:
                cap.release()
                logger.warning(f"Video duration {duration:.1f}s exceeds max {max_duration}s")
                return {
                    "success": False,
                    "message": f"Video duration ({duration:.1f}s) exceeds maximum allowed ({max_duration}s)",
                    "exercise": exercise_type,
                    "form_score": 0,
                    "rep_count": 0,
                    "feedback": []
                }

            frame_count = 0
            frames_analyzed = 0
            
            with self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # Process every 3rd frame (optimization)
                    if frame_count % 3 != 0:
                        continue
                    
                    # Convert to RGB
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    
                    # Process pose
                    results = pose.process(image)
                    
                    if results.pose_landmarks:
                        # Analyze form
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        image.flags.writeable = True
                        analyzer.analyze(results.pose_landmarks, image)
                        frames_analyzed += 1
            
            cap.release()

            logger.info(f"Video processing complete: {frames_analyzed}/{frame_count} frames analyzed")

            # Return results
            response = {
                "success": True,
                "message": f"Analyzed {frames_analyzed} frames",
                "exercise": exercise_type,
                "form_score": analyzer.form_score,
                "rep_count": getattr(analyzer, 'rep_count', 0),
                "feedback": analyzer.feedback,
                "frames_processed": frame_count,
                "frames_analyzed": frames_analyzed
            }

            # Add hold time for plank
            if hasattr(analyzer, 'hold_time'):
                response['hold_time'] = analyzer.hold_time

            return response

        except Exception as e:
            logger.error(f"Error processing video for {exercise_type}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error processing video: {str(e)}",
                "exercise": exercise_type,
                "form_score": 0,
                "rep_count": 0,
                "feedback": []
            }
        
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                    logger.debug(f"Cleaned up temp file: {temp_file.name}")
            except Exception as e:
                # Log but don't raise - cleanup failure shouldn't break the response
                logger.warning(f"Failed to clean up temp file {temp_file.name}: {str(e)}")