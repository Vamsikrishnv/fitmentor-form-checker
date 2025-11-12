# backend/video_processor.py
import cv2
import mediapipe as mp
import tempfile
import os
import sys
import logging
import time

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

        # Performance settings from environment variables
        self.frame_skip_rate = int(os.getenv("FRAME_SKIP_RATE", "6"))
        self.max_frames_to_analyze = int(os.getenv("MAX_FRAMES_TO_ANALYZE", "300"))
        self.video_resize_width = int(os.getenv("VIDEO_RESIZE_WIDTH", "640"))
        self.min_frames_for_analysis = int(os.getenv("MIN_FRAMES_FOR_ANALYSIS", "30"))

        logger.info(f"VideoProcessor initialized with: skip_rate={self.frame_skip_rate}, "
                   f"max_frames={self.max_frames_to_analyze}, resize_width={self.video_resize_width}")

    def _resize_frame(self, frame):
        """
        Resize frame to target width while maintaining aspect ratio.

        Args:
            frame: Input video frame

        Returns:
            Resized frame (or original if resize disabled)
        """
        if self.video_resize_width <= 0:
            return frame

        height, width = frame.shape[:2]

        # Only resize if frame is wider than target
        if width > self.video_resize_width:
            aspect_ratio = height / width
            new_width = self.video_resize_width
            new_height = int(new_width * aspect_ratio)
            return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        return frame

    async def analyze_video_stream(self, video_file, exercise_type: str, max_duration: int = 300):
        """
        Analyze video using streaming to avoid memory exhaustion.

        This method streams the uploaded file directly to disk in chunks
        instead of loading it entirely into memory, making it suitable
        for low-memory environments like Render's free tier (512MB).

        Args:
            video_file: FastAPI UploadFile object
            exercise_type: Type of exercise (squat, pushup, etc.)
            max_duration: Maximum video duration in seconds (default: 300)

        Returns:
            dict: Analysis results
        """

        start_time = time.time()

        if exercise_type not in self.ANALYZERS:
            return {
                "success": False,
                "message": f"Unknown exercise type: {exercise_type}",
                "exercise": exercise_type,
                "form_score": 0,
                "rep_count": 0,
                "feedback": []
            }

        # Create temp file and stream upload in chunks (memory-efficient)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

        try:
            # Stream file in 8KB chunks instead of loading all at once
            chunk_size = 8192
            while chunk := await video_file.read(chunk_size):
                temp_file.write(chunk)
            temp_file.close()

            logger.info(f"Video streamed to temp file: {temp_file.name}")

            # Now process the video from disk (not from memory)
            return await self._process_video_file(temp_file.name, exercise_type, max_duration, start_time)

        except Exception as e:
            logger.error(f"Error streaming video: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error streaming video: {str(e)}",
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
                logger.warning(f"Failed to clean up temp file {temp_file.name}: {str(e)}")

    async def _process_video_file(self, video_path: str, exercise_type: str, max_duration: int, start_time: float):
        """
        Internal method to process video from file path.

        Args:
            video_path: Path to video file on disk
            exercise_type: Type of exercise
            max_duration: Max duration in seconds
            start_time: Time when processing started

        Returns:
            dict: Analysis results
        """

        try:
            # Initialize analyzer
            analyzer = self.ANALYZERS[exercise_type]()

            # Process video
            cap = cv2.VideoCapture(video_path)

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

            # Use faster MediaPipe model for speed
            with self.mp_pose.Pose(
                model_complexity=0,  # 0 = fastest, 2 = most accurate
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                smooth_landmarks=True) as pose:

                while cap.isOpened():
                    ret, frame = cap.read()

                    if not ret:
                        break

                    frame_count += 1

                    # Skip frames based on configured rate
                    if frame_count % self.frame_skip_rate != 0:
                        continue

                    # Early termination if max frames reached
                    if frames_analyzed >= self.max_frames_to_analyze:
                        logger.info(f"Reached max frames limit ({self.max_frames_to_analyze}), stopping analysis")
                        break

                    # Resize frame for faster processing
                    frame = self._resize_frame(frame)

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

                        # Explicitly delete image to free memory
                        del image

                    # Early termination for rep-based exercises if enough data collected
                    if (frames_analyzed >= self.min_frames_for_analysis and
                        hasattr(analyzer, 'rep_count') and
                        analyzer.rep_count >= 5):  # If 5+ reps detected, we have enough data
                        logger.info(f"Detected {analyzer.rep_count} reps with {frames_analyzed} frames, early termination")
                        break
            
            cap.release()

            processing_time = time.time() - start_time
            logger.info(f"Video processing complete: {frames_analyzed}/{frame_count} frames analyzed in {processing_time:.2f}s")

            # Return results
            response = {
                "success": True,
                "message": f"Analyzed {frames_analyzed} frames in {processing_time:.1f}s",
                "exercise": exercise_type,
                "form_score": analyzer.form_score,
                "rep_count": getattr(analyzer, 'rep_count', 0),
                "feedback": analyzer.feedback,
                "frames_processed": frame_count,
                "frames_analyzed": frames_analyzed,
                "processing_time_seconds": round(processing_time, 2)
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

    async def analyze_video(self, video_content: bytes, exercise_type: str, max_duration: int = 300):
        """
        Legacy method - loads entire video into memory (not recommended for production).
        Use analyze_video_stream() instead for memory efficiency.

        Args:
            video_content: Video file content as bytes
            exercise_type: Type of exercise (squat, pushup, etc.)
            max_duration: Maximum video duration in seconds (default: 300)

        Returns:
            dict: Analysis results
        """

        start_time = time.time()

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
            return await self._process_video_file(temp_file.name, exercise_type, max_duration, start_time)
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}", exc_info=True)
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