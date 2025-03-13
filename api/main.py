import os
import io
import uuid
import base64
import json
from pdf2image import convert_from_path
import numpy as np
from PIL import Image
import cv2
import torch
from flask import Flask, request, Response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from ultralytics import YOLO

# -------------------- Configuration --------------------

# Constants
UPLOAD_FOLDER = "uploads"
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

def separate_staff_zones(images_io: io.BytesIO) -> list:
    original_image = cv2.imdecode(np.frombuffer(images_io.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    modified_image = original_image.copy()
    height, width, channels = modified_image.shape

    # Apply grayscale, Gaussian blur, thresholding and morphological operations to group staff zones
    gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours and filter for staff zones
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x : cv2.boundingRect(x)[1]) # Sort based on vertical order

    # Extract staff zones by filtering contours whose width is greater than 80% of the image width
    staff_zones = []

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        
        if w > width*0.8:
            roi = original_image[y:y+h, x:x+w]
            staff_zones.append(roi)
        
    return staff_zones

def remove_staff_lines(zone: np.ndarray) -> np.ndarray:
    # Convert image to grayscale and apply thresholding
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    vertical = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4))
    
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    # Reconstruct noteheads and beams
    notehead_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    reconstructed = cv2.dilate(vertical, notehead_kernel, iterations=1)

    # Invert the image to origin
    inverted = cv2.bitwise_not(reconstructed)

    return inverted

def extract_staff_lines(zone: np.ndarray) -> list:
    # Convert image to grayscale and apply thresholding
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    horizontal = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    height, width, = horizontal.shape

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (round(width*0.8), 1))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    # Filter based on thickness
    contours, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x : cv2.boundingRect(x)[1])

    # List to hold staff lines
    staff_lines = []

    for contour in contours:
        # Get bounding box of each contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter based on height (thickness)
        if w < width*0.8 and h > 4:  # Adjust this value to filter out thicker beams
            cv2.drawContours(horizontal, [contour], -1, 0, -1)
        else:
            staff_lines.append((x, y, w, h))

    # Optional: Preserve edges
    # horizontal = cv2.dilate(horizontal, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    return staff_lines

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
        
        # Generate a unique filename and save the file
        uploaded_filename = f"{str(uuid.uuid4())}_{file.filename}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename))

        return {"message": "File uploaded successfully", "filename": uploaded_filename}, 200

class StreamImages(Resource):
    def get(self):
        global uploaded_filename
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

                # Separate staff zones and detect symbols
                staff_zones = separate_staff_zones(img_io)

                for j, zone in enumerate(staff_zones):
                    # Remove staff lines from the zone
                    zone_no_lines = remove_staff_lines(zone)

                    # Extract staff lines from the zone
                    staff_lines = extract_staff_lines(zone)

                    # Convert Numpy array to image
                    zone_image = Image.fromarray(cv2.cvtColor(zone_no_lines, cv2.COLOR_BGR2RGB))

                    # Save image to BytesIO object
                    zone_io = io.BytesIO()
                    zone_image.save(zone_io, "PNG")

                    # Encode image to base64
                    zone_base64 = base64.b64encode(zone_io.getvalue()).decode("utf-8")

                    # Extract bounding boxes from image
                    response = {
                        "filename": uploaded_filename,
                        "page": i + 1,
                        "zone": j + 1,
                        "image": zone_base64,
                        "boxes": extract_boxes(zone_io),
                        "staff_lines": staff_lines
                    }

                    print(f"Image {i + 1}, Zone {j + 1} sent")
                    yield f"data:{json.dumps(response)}\n\n"
            
            print("All images sent")
            yield "data:done\n\n"
    
        return Response(generate(), mimetype="text/event-stream")

# Add resource to API
api.add_resource(ExtractSymbol, "/extract")
api.add_resource(StreamImages, "/stream")

# -------------------- Run Application --------------------

if __name__ == "__main__":
    app.run(debug=True)
