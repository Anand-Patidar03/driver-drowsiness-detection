import cv2
import numpy as np
import os

class EyeDetector:
    """
    Handles loading the Haar Cascade model for eyes and finding eyes within a given face region.
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cascade_path = os.path.join(base_dir, 'models', 'haarcascade_eye.xml')

        self.eye_cascade = cv2.CascadeClassifier(cascade_path)
        # [ADDED BY ASSISTANT] Fallback to OpenCV default data path if local XML is missing or empty
        if self.eye_cascade.empty():
            default_path = os.path.join(cv2.data.haarcascades, 'haarcascade_eye.xml')
            self.eye_cascade = cv2.CascadeClassifier(default_path)

        if self.eye_cascade.empty():
            raise RuntimeError(f"Error loading Haar cascade XML file from {cascade_path} or OpenCV default path. Make sure it exists!")

    def detect_eyes(self, frame: np.ndarray, face_box: tuple):
        """
        Takes an image frame and a face bounding box (x, y, w, h).
        Returns a list of eye bounding boxes (ex, ey, ew, eh) relative to the original frame.
        """
        if frame is None or face_box is None:
            return []

        x, y, w, h = face_box
        
        # Isolate the upper half of the face to reduce false positives (like nostrils/mouth).
        # We use the top 60% of the face bounding box for better accuracy.
        roi_top_h = int(h * 0.6)
        roi_frame = frame[y:y+roi_top_h, x:x+w]
        
        if roi_frame.size == 0:
            return []

        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Map Haar Cascade bounds specifically targeting eyes
        # minNeighbors is set to 10 to require more consensus and reduce false detections
        eyes = self.eye_cascade.detectMultiScale(
            gray_roi, 
            scaleFactor=1.1, 
            minNeighbors=10, 
            minSize=(20, 20)
        )
        
        # Convert the localized eye coordinates back to the global frame coordinates
        detected_eyes = []
        for (ex, ey, ew, eh) in eyes:
            global_ex = x + ex
            global_ey = y + ey
            detected_eyes.append((global_ex, global_ey, ew, eh))
            
        # Optional: Sort isolated eyes by area to prioritize the two most prominent "eyes"
        detected_eyes = sorted(detected_eyes, key=lambda e: e[2]*e[3], reverse=True)[:2]

        # [ADDED BY ASSISTANT] Sort top 2 eyes from left to right (by X-coordinate)
        # This guarantees eyes[0] is screen-left and eyes[1] is screen-right consistently
        detected_eyes = sorted(detected_eyes, key=lambda e: e[0])
        return detected_eyes

    # [ADDED BY ASSISTANT] Communication bridge method:
    # Safely extracts cropped NumPy eye image arrays with boundary checks ready for CNN model prediction.
    def extract_eye_crops(self, frame: np.ndarray, face_box: tuple) -> list:
        """
        [ADDED BY ASSISTANT]
        Detects eyes and returns a list of dictionaries containing:
        - 'bbox': (ex, ey, ew, eh)
        - 'crop': cropped NumPy array from frame (safe boundary slicing)
        - 'side': 'Left' (screen-left) or 'Right' (screen-right)
        Directly consumed by the model's predict_eye() function.
        """
        if frame is None or face_box is None:
            return []

        eye_boxes = self.detect_eyes(frame, face_box)
        h_frame, w_frame = frame.shape[:2]
        eye_data = []

        for idx, (ex, ey, ew, eh) in enumerate(eye_boxes):
            # [ADDED BY ASSISTANT] Boundary-safe cropping to avoid out-of-bounds slicing crashes
            y1, y2 = max(0, ey), min(h_frame, ey + eh)
            x1, x2 = max(0, ex), min(w_frame, ex + ew)

            if y2 > y1 and x2 > x1:
                crop = frame[y1:y2, x1:x2].copy()
                side = "Left" if idx == 0 else "Right"
                eye_data.append({
                    "bbox": (ex, ey, ew, eh),
                    "crop": crop,
                    "side": side
                })

        return eye_data
