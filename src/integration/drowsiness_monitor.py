"""
[ADDED BY ASSISTANT]
Integration Module for Driver Drowsiness Detection System.
Coordinates the OpenCV Face & Eye Detector with the CNN Eye State Predictor.
"""

import sys
import time
import threading
from pathlib import Path
import cv2
import numpy as np

# [ADDED BY ASSISTANT] Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# [ADDED BY ASSISTANT] Coordinated imports from both members' modules
from src.opencv import FaceDetector, EyeDetector
from src.model import predict_eye_with_confidence

# [ADDED BY ASSISTANT] Optional Windows sound alert
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class DrowsinessMonitor:
    """
    [ADDED BY ASSISTANT]
    Coordinates FaceDetector, EyeDetector, and CNN Model prediction.
    Tracks consecutive closed-eye frames and raises warnings/alerts.
    """

    def __init__(
        self,
        camera_index: int = 0,
        drowsy_frames_threshold: int = 15,
        enable_audio: bool = True
    ):
        self.camera_index = camera_index
        self.drowsy_frames_threshold = drowsy_frames_threshold
        self.enable_audio = enable_audio

        # Initialize detectors from OpenCV member
        self.face_detector = FaceDetector()
        self.eye_detector = EyeDetector()

        # State tracking
        self.closed_frame_count = 0
        self.is_alarm_playing = False
        self.fps = 0.0

    def trigger_beep(self):
        """
        [ADDED BY ASSISTANT] Plays an audio alert in a background thread so the video feed doesn't freeze.
        """
        if not self.enable_audio or not HAS_WINSOUND:
            return

        if not self.is_alarm_playing:
            def _play():
                self.is_alarm_playing = True
                try:
                    winsound.Beep(2500, 400)  # 2500 Hz for 400 ms
                except Exception:
                    pass
                finally:
                    self.is_alarm_playing = False

            threading.Thread(target=_play, daemon=True).start()

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        [ADDED BY ASSISTANT]
        Coordinates detection and prediction for a single video frame.
        Draws visual feedback and HUD directly on the frame.
        """
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]

        # 1. OpenCV Member: Detect Face
        face_box = self.face_detector.detect_face(frame)

        if face_box is not None:
            fx, fy, fw, fh = face_box
            # Subtle face outline
            cv2.rectangle(display_frame, (fx, fy), (fx + fw, fy + fh), (200, 200, 200), 1)

            # 2. OpenCV Member: Extract safe eye crops
            eye_data = self.eye_detector.extract_eye_crops(frame, face_box)

            eye_states = []
            for item in eye_data:
                ex, ey, ew, eh = item["bbox"]
                crop = item["crop"]
                side = item["side"]

                # 3. Model Member: Predict state and probability
                state, prob = predict_eye_with_confidence(crop)
                eye_states.append(state)

                # Visual bounding box & label
                color = (0, 255, 0) if state == "Open" else (0, 0, 255)
                label = f"{side}: {state} ({prob:.2f})"

                cv2.rectangle(display_frame, (ex, ey), (ex + ew, ey + eh), color, 2)
                cv2.putText(
                    display_frame,
                    label,
                    (ex, max(18, ey - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    color,
                    1,
                    cv2.LINE_AA
                )

            # 4. Coordination Logic: Check for Drowsiness
            # If all visible eyes are closed
            if eye_states and all(s == "Closed" for s in eye_states):
                self.closed_frame_count += 1
            else:
                self.closed_frame_count = max(0, self.closed_frame_count - 1)

            # Determine drowsiness alert condition
            if self.closed_frame_count >= self.drowsy_frames_threshold:
                # Trigger sound alert
                self.trigger_beep()

                # High-visibility flashing banner
                alert_box_h = 70
                overlay = display_frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, alert_box_h), (0, 0, 220), -1)
                display_frame = cv2.addWeighted(overlay, 0.75, display_frame, 0.25, 0)

                cv2.putText(
                    display_frame,
                    "*** DROWSINESS ALERT! WAKE UP! ***",
                    (30, 45),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.85,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )
            else:
                # Draw status progress bar for closed eye duration
                progress = min(1.0, self.closed_frame_count / self.drowsy_frames_threshold)
                bar_w = int(200 * progress)
                bar_color = (0, 200, 255) if progress < 0.7 else (0, 0, 255)
                cv2.rectangle(display_frame, (20, 20), (220, 35), (80, 80, 80), 1)
                if bar_w > 0:
                    cv2.rectangle(display_frame, (20, 20), (20 + bar_w, 35), bar_color, -1)
                cv2.putText(
                    display_frame,
                    f"Drowsiness Meter: {self.closed_frame_count}/{self.drowsy_frames_threshold}",
                    (20, 52),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )
        else:
            # No face detected
            self.closed_frame_count = max(0, self.closed_frame_count - 1)
            cv2.putText(
                display_frame,
                "No Face Detected",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),
                2,
                cv2.LINE_AA
            )

        # Draw FPS indicator
        cv2.putText(
            display_frame,
            f"FPS: {self.fps:.1f}",
            (w - 110, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            1,
            cv2.LINE_AA
        )

        return display_frame

    def start(self):
        """
        [ADDED BY ASSISTANT] Starts the live webcam video monitoring loop.
        """
        print(f"Starting Driver Drowsiness Monitor on camera {self.camera_index}...")
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print(f"Error: Could not open video device at index {self.camera_index}.")
            return

        print("Monitor active. Press 'q' to quit.")

        prev_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of stream or failed to read frame.")
                break

            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
            prev_time = curr_time

            processed_frame = self.process_frame(frame)
            cv2.imshow("Driver Drowsiness Monitor - Integrated System", processed_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            try:
                if cv2.getWindowProperty("Driver Drowsiness Monitor - Integrated System", cv2.WND_PROP_VISIBLE) < 1:
                    break
            except cv2.error:
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Driver Drowsiness Monitor closed successfully.")


def run_monitor(camera_index: int = 0, threshold: int = 15):
    """
    [ADDED BY ASSISTANT] Helper entry point to easily launch the monitor.
    """
    monitor = DrowsinessMonitor(camera_index=camera_index, drowsy_frames_threshold=threshold)
    monitor.start()


if __name__ == "__main__":
    run_monitor()
