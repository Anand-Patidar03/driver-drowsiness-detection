import cv2
import sys
from pathlib import Path

# [ADDED BY ASSISTANT] Ensure project root and module directories are in sys.path
FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parents[1]
for p in [str(PROJECT_ROOT), str(FILE_DIR), str(FILE_DIR / "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# [ADDED BY ASSISTANT] Resilient imports for detectors
try:
    from src.opencv.src.face_detector import FaceDetector
    from src.opencv.src.eye_detector import EyeDetector
except ImportError:
    from face_detector import FaceDetector
    from eye_detector import EyeDetector

# [ADDED BY ASSISTANT] Connect with Model Member's prediction pipeline
try:
    from src.model.predict import predict_eye_with_confidence
    MODEL_AVAILABLE = True
except Exception as e:
    print(f"[Warning] Could not load CNN model: {e}. Running in detection-only mode.")
    MODEL_AVAILABLE = False


def main():
    print("Initializing Driver Drowsiness Monitor CV Subsystem...")
    
    try:
        detector = FaceDetector()
        eye_detector = EyeDetector()
    except Exception as e:
        print(f"Startup Failed: {e}")
        return
        
    print("Successfully loaded the Haar Cascade models!")
    if MODEL_AVAILABLE:
        print("Successfully loaded CNN Eye State Classifier!")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    print("Webcam successfully accessed. Press 'q' on your keyboard to quit.")
    
    #  THE VIDEO LOOP
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame. Exiting video loop.")
            break
            
        face_box = detector.detect_face(frame)
        
        if face_box is not None:
            x, y, w, h = face_box
            
            # [ADDED BY ASSISTANT] Use extract_eye_crops to communicate with Model Member
            eye_crops_data = eye_detector.extract_eye_crops(frame, face_box)
            status_summaries = []

            for eye_info in eye_crops_data:
                ex, ey, ew, eh = eye_info["bbox"]
                crop = eye_info["crop"]
                side = eye_info["side"]

                # [ADDED BY ASSISTANT] Model Member coordination: predict eye state
                if MODEL_AVAILABLE:
                    state, prob = predict_eye_with_confidence(crop)
                    color = (0, 255, 0) if state == "Open" else (0, 0, 255)
                    label = f"{side}: {state} ({prob:.2f})"
                    status_summaries.append(f"{side}:{state}")
                else:
                    color = (255, 0, 0)  # Default blue
                    label = f"{side} Eye"
                    status_summaries.append(f"{side}:Detected")

                # Draw bounding box and label above eye
                cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), color, 2)
                cv2.putText(frame, label, (ex, max(15, ey - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

            # Update terminal status smoothly replacing the same line
            eyes_status_str = " | ".join(status_summaries) if status_summaries else "Searching..."
            print(f"Status: Face Detected | Eyes: {eyes_status_str}       ", end='\r', flush=True)
        else:
            print(f"Status: No Face Detected                     ", end='\r', flush=True)

        cv2.imshow("Main Driving Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nShutting down program (q pressed)...")
            break
        try:
            if cv2.getWindowProperty("Main Driving Feed", cv2.WND_PROP_VISIBLE) < 1:
                print("\nShutting down program (window closed)...")
                break
        except cv2.error:
            # Window was already destroyed
            break

    #  CLEANUP
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
