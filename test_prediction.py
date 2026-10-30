import sys
from pathlib import Path
import cv2

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.model.predict import predict_eye

dataset_path = PROJECT_ROOT / "dataset"
images = list(dataset_path.rglob("*.png"))[:20]

correct = 0
total = 0

for image_path in images:
    eye = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if eye is None:
        continue

    # Get actual label from the filename
    parts = image_path.stem.split("_")
    actual_label = int(parts[3])

    actual_state = "Open" if actual_label == 1 else "Closed"
    predicted_state = predict_eye(eye)

    total += 1

    if actual_state == predicted_state:
        correct += 1

    print(
        f"{image_path.name} | "
        f"Actual: {actual_state} | "
        f"Predicted: {predicted_state}"
    )

print("\n--- Summary ---")
print("Total images:", total)
print("Correct predictions:", correct)
print("Incorrect predictions:", total - correct)

if total > 0:
    print("Accuracy:", round(correct / total * 100, 2), "%")