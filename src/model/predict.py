import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path

# Get project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load the trained CNN
MODEL_PATH = PROJECT_ROOT / "models" / "drowsiness_cnn_model.keras"

# [ADDED BY ASSISTANT] Fallback path check if loaded from different working directories
if not MODEL_PATH.exists():
    fallback_path = Path.cwd() / "models" / "drowsiness_cnn_model.keras"
    if fallback_path.exists():
        MODEL_PATH = fallback_path

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

model = tf.keras.models.load_model(MODEL_PATH)


# [ADDED BY ASSISTANT] Detailed prediction function returning both classification and confidence score
def predict_eye_with_confidence(eye):
    """
    [ADDED BY ASSISTANT]
    Takes a cropped eye NumPy array (BGR or Grayscale) and returns (state, probability).
    - state: "Open", "Closed", or "Unknown"
    - probability: float (0.0 to 1.0) indicating likelihood of being Open
    """
    # Safe validation: check if crop is empty or invalid
    if eye is None or not isinstance(eye, np.ndarray) or eye.size == 0:
        return "Unknown", 0.0

    if eye.shape[0] < 5 or eye.shape[1] < 5:
        return "Unknown", 0.0

    # Convert BGR image to grayscale
    if len(eye.shape) == 3:
        eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)

    # Resize image to match model input (80x80)
    eye = cv2.resize(eye, (80, 80))

    # Normalize pixel values
    eye = eye.astype(np.float32) / 255.0

    # Add channel and batch dimensions: (1, 80, 80, 1)
    eye = np.expand_dims(eye, axis=-1)
    eye = np.expand_dims(eye, axis=0)

    # Predict open-eye probability
    probability = float(model.predict(eye, verbose=0)[0][0])

    # Classify eye state
    state = "Open" if probability >= 0.5 else "Closed"
    return state, probability


def predict_eye(eye):
    """
    Predicts eye state ("Open" or "Closed").
    Preserved for 100% backward compatibility with test_prediction.py.
    """
    # [ADDED BY ASSISTANT] Uses safe predict_eye_with_confidence under the hood
    state, _ = predict_eye_with_confidence(eye)
    return state