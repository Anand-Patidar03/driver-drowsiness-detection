"""
[ADDED BY ASSISTANT]
Main entry point to run the integrated Driver Drowsiness Detection System.
Coordinates the OpenCV computer vision module and the CNN model.
"""

from src.integration.drowsiness_monitor import run_monitor

if __name__ == "__main__":
    # Launch with default webcam (index 0) and threshold of 15 consecutive frames
    run_monitor(camera_index=0, threshold=15)
