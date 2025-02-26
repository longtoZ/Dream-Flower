import os
import io
import uuid
import base64
from pdf2image import convert_from_path
import numpy as np
import cv2
import torch
from flask import Flask, request, Response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
# from ultralytics import YOLO

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

# Enable CORS
CORS(app)

# Configure app
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- Model Initialization --------------------

# # Load the pretrained YOLO model
# MODEL_PATH = r"C:\Users\VICTUS\Documents\OMR project\model_training\runs\detect\train4\weights\best.pt"
# model = YOLO(MODEL_PATH)

# # Set device (GPU if available, otherwise CPU)
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model.to(device)

# -------------------- Utility Functions --------------------

def allowed_file(filename: str) -> bool:
    """
    Check if a file has an allowed extension.
    :param filename: The name of the file.
    :return: True if allowed, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_boxes(image_io: io.BytesIO) -> list:
    image = cv2.imdecode(np.frombuffer(image_io.getvalue(), np.uint8), cv2.IMREAD_COLOR)
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

uploaded_filename = ""

class ExtractSymbol(Resource):
    def post(self):
        global uploaded_filename
        if "file" not in request.files:
            return {"error": "No file part"}, 400
        
        file = request.files["file"]

        if file.filename == "" or not file.filename.endswith(".pdf"):
            return {"error": "No selected file or invalid file type"}, 400
        
        uploaded_filename = f"{str(uuid.uuid4())}_{file.filename}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename))

        return {"message": "File uploaded successfully", "filename": uploaded_filename}, 200

class StreamImages(Resource):
    def get(self):
        uploaded_filepath = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename)

        # Wait for the file to be uploaded
        while not os.path.exists(uploaded_filepath):
            pass

        def generate():
            # Convert PDF to images
            images = convert_from_path(uploaded_filepath, dpi=300, poppler_path="./poppler-24.08.0/Library/bin")

            # Stream each image as a response
            for i, img in enumerate(images):
                img_io = io.BytesIO()
                img.save(img_io, "PNG")
                img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
                print(f"Image {i + 1} sent")

                yield f"data:{img_base64}\n\n"
            
            print("All images sent")

            yield "data:done\n\n"
    
        return Response(generate(), mimetype="text/event-stream")

# Add resource to API
api.add_resource(ExtractSymbol, "/extract")
api.add_resource(StreamImages, "/stream")

# -------------------- Run Application --------------------

if __name__ == "__main__":
    app.run(debug=True)
