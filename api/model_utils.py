# model_utils.py
import io
import cv2
import numpy as np
from ultralytics import YOLO

# Import config variables
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
        image_np = np.frombuffer(image_io.getvalue(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR) 
        
        if image is None:
            print("Error: Could not decode image in extract_boxes")
            return [[] for _ in range(NUMBER_OF_CLASSES)]

        # Perform inference
        results = model(image, device=DEVICE) # Pass device explicitly if needed

        # Initialize list to hold bounding boxes for each class
        box_coordinates = {name: [] for name in CLASS_NAMES} # Use names as keys

        # Iterate through detections
        for result in results:
            if result.boxes is None: continue
            
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                if 0 <= class_id < len(CLASS_NAMES):
                    class_name = CLASS_NAMES[class_id]
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item() # Get confidence score
                    
                    # Store dictionary with coords and confidence
                    box_info = {
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                        "confidence": confidence 
                    }
                    box_coordinates[class_name].append(box_info)
                else:
                    print(f"Warning: Detected unknown class ID: {class_id}")

        return box_coordinates # Return dictionary keyed by class name

    except Exception as e:
        print(f"Error during model inference: {e}")
        return {name: [] for name in CLASS_NAMES} # Return empty dict on error