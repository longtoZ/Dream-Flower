# resources.py
import os
import io
import uuid
import base64
import json
import time # For waiting

from flask import request, Response, jsonify, current_app, send_file
from flask_restful import Resource
from flask_socketio import emit
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
import cv2
import numpy as np

# Import utilities and config
from config import UPLOAD_FOLDER, POPPLER_PATH
from image_utils import separate_staff_zones, remove_staff_lines, extract_staff_lines
from model_utils import extract_boxes # Use the function from model_utils
from sheet_converter import convert_to_sheet
from audio_generator import combine_audio

from extensions import socketio

# --- API Resources ---

# Temporary storage for filename (Consider a more robust solution for production)
# This is still not ideal for concurrent requests or multiple server workers.
# A better approach might involve a database, cache (Redis), or passing state via URLs/requests.
uploaded_files_state = {} 

class UploadPdf(Resource):
    def post(self):
        """Handles PDF file upload."""
        if "file" not in request.files:
            return {"error": "No file part in the request"}, 400
        
        file = request.files["file"]

        if file.filename == "":
            return {"error": "No selected file"}, 400
        
        if not file.filename.lower().endswith(".pdf"):
            return {"error": "Invalid file type, please upload a PDF"}, 400
        
        # Generate a unique identifier for this upload session/request
        session_id = str(uuid.uuid4())
        original_filename = file.filename
        # Store filename using session_id to avoid conflicts
        saved_filename = f"{session_id}_{original_filename}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], saved_filename)

        try:
            file.save(save_path)
            # Store info needed for the stream endpoint
            uploaded_files_state[session_id] = {
                "filename": saved_filename,
                "path": save_path,
                "status": "uploaded" 
            }
            # Return the session_id to the client
            return {"message": "File uploaded successfully", "session_id": session_id}, 200
        except Exception as e:
            current_app.logger.error(f"Error saving file: {e}")
            return {"error": "Failed to save uploaded file"}, 500

class StreamImageResults(Resource):
    def get(self, session_id):
        """Streams processed image zones and detection results for a given session_id."""
        
        if session_id not in uploaded_files_state:
             return Response(f"data: {json.dumps({'error': 'Invalid or expired session ID'})}\n\n", mimetype="text/event-stream")
        
        file_info = uploaded_files_state[session_id]
        uploaded_filepath = file_info["path"]
        original_filename = file_info["filename"] # Keep original for reference if needed

        if not os.path.exists(uploaded_filepath):
            return Response(f"data: {json.dumps({'error': 'Uploaded file not found on server'})}\n\n", mimetype="text/event-stream")

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

                    # Encode original zone image to base64
                    original_zone_io = io.BytesIO()
                    original_zone_image = Image.fromarray(cv2.cvtColor(zone, cv2.COLOR_BGR2RGB))
                    original_zone_image.save(original_zone_io, "PNG")
                    original_zone_base64 = base64.b64encode(original_zone_io.getvalue()).decode("utf-8")

                    # Extract bounding boxes from image
                    response = {
                        "filename": original_filename,
                        "page": i + 1,
                        "zone": j + 1,
                        "image": original_zone_base64,
                        "boxes": extract_boxes(zone_io),
                        "staff_lines": staff_lines
                    }

                    print(f"Image {i + 1}, Zone {j + 1} sent")
                    yield f"data:{json.dumps(response)}\n\n"
            
            print("All images sent")
            # Clean up the uploaded file after processing
            os.remove(uploaded_filepath)

            # Clear the state for this session ID
            del uploaded_files_state[session_id]

            yield "data:done\n\n"

        # Return the streaming response
        return Response(generate(), mimetype="text/event-stream")
    
class ConvertToSheetResource(Resource):
    def post(self):
        """
        Receives a list of processed zone data via POST, converts each item 
        into a music sheet structure, and returns a list of results.
        """
        # Parse the JSON input data from the request body
        input_data_list = request.get_json()

        if not isinstance(input_data_list, list):
            return {"error": "Request body must be a JSON list"}, 400

        results_list = []
        TIME_COEFF = [1]

        for index, item in enumerate(input_data_list):
            try:
                # Call the conversion function for each item in the list
                music_sheet_result = convert_to_sheet(item, TIME_COEFF)
                if music_sheet_result: # Append only if conversion was successful
                   results_list.append(music_sheet_result)
                else:
                   current_app.logger.warning(f"Conversion returned None for item at index {index}")
                   # Optionally append an error marker: results_list.append({"error": "Conversion failed", "index": index})
            except Exception as e:
                current_app.logger.error(f"Error processing item at index {index}: {e}", exc_info=True)
                # Optionally append an error marker: results_list.append({"error": str(e), "index": index})

        # Return the list of generated music_sheet dictionaries
        return jsonify(results_list) 

class GenerateAudioResource(Resource):
    def post(self):
        """
        Receives a list of music sheet data via POST, generates audio for each item,
        and returns a list of audio results.
        """

        # Parse the JSON input data from the request body
        input_data = request.get_json()
        music_sheet = input_data.get("music_sheet")
        measure_playtime = input_data.get("measure_playtime")
        audio_theme = input_data.get("audio_theme")

        # Get the socket ID from the request context
        socket_id = input_data.get("socket_id")
        print(f"Socket ID: {socket_id}")

        if not isinstance(music_sheet, list):
            return {"error": "Request body must be a JSON list"}, 400
        
        filename, checkpoints = combine_audio({"socket_io": socketio, "socket_id": socket_id}, music_sheet, measure_playtime, audio_theme)

        # Create multipart response with audio file and checkpoints
        socketio.emit("status_update", {"message": "Audio file is being sent..."}, namespace="/audio", to=socket_id)

        with open(filename, "rb") as audio_file:
            audio_data = audio_file.read()

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

        response_body = (
            f"--{boundary}\r\n"
            "Content-Type: application/json\r\n\r\n"
            f"{json.dumps(checkpoints)}\r\n"
            f"--{boundary}\r\n"
            "Content-Type: audio/mp3\r\n"
            f"Content-Disposition: attachment; filename={filename}\r\n\r\n"
        ).encode("utf-8") + audio_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        # Delete the audio file after sending it
        os.remove(filename)

        return Response(
            response_body,
            mimetype=f"multipart/mixed; boundary={boundary}",
            headers={"Content-Length": str(len(response_body))},
        )

