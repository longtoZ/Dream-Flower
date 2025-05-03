import io
import cv2
import numpy as np
from ultralytics import YOLO

from config import MODEL_PATH, DEVICE, NUMBER_OF_CLASSES, CLASS_NAMES

# --- Model Initialization ---
try:
    print(f"Loading model from: {MODEL_PATH}")
    print(f"Using device: {DEVICE}")
    model = YOLO(MODEL_PATH)
    model.to(DEVICE)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None # Set model to None if loading fails

# --- Utility Functions ---

def extract_boxes(image_io: io.BytesIO) -> list:
    """Performs object detection on the image and returns bounding boxes."""
    if model is None:
        print("Error: Model not loaded, cannot extract boxes.")
        return [[] for _ in range(NUMBER_OF_CLASSES)]
        
    try:
        # Decode image ensuring it's in the format the model expects (usually BGR)
        image = cv2.imdecode(np.frombuffer(image_io.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            print("Error: Could not decode image in extract_boxes")
            return [[] for _ in range(NUMBER_OF_CLASSES)]

        # Perform inference
        results = model(image, device=DEVICE) # Pass device explicitly if needed

        # Initialize a list to hold bounding boxes for each class
        box_coordinates = [[] for _ in range(NUMBER_OF_CLASSES)]

        # Iterate through detections and store bounding box coordinates
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())  # Get class ID
                x1, y1, x2, y2 = box.xyxy[0].tolist()  # Get bounding box coordinates
                box_coordinates[class_id].append((x1, y1, x2, y2))

        return box_coordinates

        return box_coordinates # Return dictionary keyed by class name

    except Exception as e:
        print(f"Error during model inference: {e}")
        return [[] for _ in range(NUMBER_OF_CLASSES)] # Return empty boxes for each class