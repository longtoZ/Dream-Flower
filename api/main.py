import os
import cv2
import torch
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from ultralytics import YOLO

# -------------------- Configuration --------------------

# Constants
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
NUMBER_OF_CLASSES = 20
CLASS_NAMES = [
    "barline", "bass_clef", "decrescendo", "dotted_note", "eight_beam",
    "eight_flag", "eight_rest", "flat", "half_note", "natural",
    "quarter_note", "quarter_rest", "sharp", "sixteenth_beam", "sixteenth_flag",
    "sixteenth_rest", "thirty_second_beam", "treble_clef", "whole_half_rest", "whole_note"
]

# Initialize Flask app and API
app = Flask(__name__)
api = Api(app)

# Configure app
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- Model Initialization --------------------

# Load the pretrained YOLO model
MODEL_PATH = r"C:\Users\VICTUS\Documents\OMR project\model_training\runs\detect\train4\weights\best.pt"
model = YOLO(MODEL_PATH)

# Set device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# -------------------- Utility Functions --------------------

def allowed_file(filename: str) -> bool:
    """
    Check if a file has an allowed extension.
    :param filename: The name of the file.
    :return: True if allowed, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_boxes(image_path: str) -> list:
    """
    Extract bounding boxes from an image using the pretrained YOLO model.
    :param image_path: Path to the input image.
    :return: A list of bounding boxes categorized by class.
    """
    image = cv2.imread(image_path)
    results = model(image)

    # Initialize a list to hold bounding boxes for each class
    box_coordinates = [[] for _ in range(NUMBER_OF_CLASSES)]

    # Iterate through detections and store bounding box coordinates
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())  # Get class ID
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Get bounding box coordinates
            box_coordinates[class_id].append((x1, y1, x2, y2))

    return box_coordinates

# -------------------- API Endpoints --------------------

class ExtractSymbol(Resource):
    def post(self):
        """
        API endpoint to receive an image, process it, and return detected bounding boxes.
        """
        if "image" not in request.files:
            return {"error": "No image provided"}, 400

        file = request.files["image"]

        if not file.filename:
            return {"error": "No selected file"}, 400

        if not allowed_file(file.filename):
            return {"error": "Invalid file type"}, 400

        # Save the uploaded file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Extract symbols from the image
        boxes = extract_boxes(filepath)

        # Delete the image after processing
        os.remove(filepath)

        return jsonify({"boxes": boxes, "filename": file.filename})

# Add resource to API
api.add_resource(ExtractSymbol, "/extract")

# -------------------- Run Application --------------------

if __name__ == "__main__":
    app.run(debug=True)
