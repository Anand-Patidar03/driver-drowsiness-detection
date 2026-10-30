import cv2
import numpy as np
import os

class FaceDetector:
    """
     handles grabbing the Haar Cascade model and finding a face in an image.
    """
    def __init__(self):
        

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_default.xml')
        
        # cv2.CascadeClassifier is an OpenCV function that reads the XML model file 
        # and prepares it so we can use it to detect faces later.
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # [ADDED BY ASSISTANT] Fallback to OpenCV's built-in cascade path if local XML is missing or empty
        if self.face_cascade.empty():
            default_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
            self.face_cascade = cv2.CascadeClassifier(default_path)

        if self.face_cascade.empty():
            raise RuntimeError(f"Error loading Haar cascade XML file from {cascade_path} or OpenCV default path. Make sure it exists!")

    def detect_face(self, frame: np.ndarray):
        """
        Takes an image frame (like from a webcam) and returns the bounding box 
        (x, y, width, height) of the largest detected face.
        """
        if frame is None or not isinstance(frame, np.ndarray) or len(frame.shape) < 2:
            return None


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #  RUN THE ACTUAL FACE DETECTION
        # detectMultiScale scans the image at different scales (to find big faces and small faces).
        # - scaleFactor=1.3: It shrinks the image by 30% each scan to find faces at different distances.
        # - minNeighbors=5: It tells the algorithm how many "neighbor" rectangles need to agree it's a face before drawing one box. Higher = stricter (less false positives).
        # - minSize=(100, 100): We ignore any faces smaller than 100x100 pixels, because a driver's face will be close to the webcam.
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) == 0:
            return None
            
        #  PICK THE CORRECT FACE
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        # [ADDED BY ASSISTANT] Return as a standard python tuple of integers (x, y, w, h)
        x, y, w, h = faces[0]
        return (int(x), int(y), int(w), int(h))
