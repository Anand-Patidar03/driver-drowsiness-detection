"""
[ADDED BY ASSISTANT]
OpenCV module for Face and Eye Detection in Driver Drowsiness System.
Provides easy imports for FaceDetector and EyeDetector.
"""
from src.opencv.src.face_detector import FaceDetector
from src.opencv.src.eye_detector import EyeDetector

__all__ = ["FaceDetector", "EyeDetector"]
