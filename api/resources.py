# resources.py
import os
import io
import uuid
import base64
import json
import time # For waiting

from flask import request, Response, jsonify, current_app, send_file
from flask_restful import Resource
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
             # Maybe wait a fraction of a second in case of race condition
             time.sleep(0.5) 
             if not os.path.exists(uploaded_filepath):
                return Response(f"data: {json.dumps({'error': 'Uploaded file not found on server'})}\n\n", mimetype="text/event-stream")

        def generate():
            try:
                # Check PDF validity before conversion
                try:
                   pdfinfo_from_path(uploaded_filepath, poppler_path=POPPLER_PATH)
                except Exception as pdf_err:
                    yield f"data: {json.dumps({'error': f'Invalid PDF file: {pdf_err}'})}\n\n"
                    return

                # Convert PDF to images
                print(f"Converting PDF: {original_filename} using poppler: {POPPLER_PATH}")
                images = convert_from_path(uploaded_filepath, dpi=300, poppler_path=POPPLER_PATH)
                print(f"PDF conversion complete. Found {len(images)} pages.")

                total_zones_processed = 0
                # Process each page
                for i, pil_img in enumerate(images):
                    # Convert PIL Image to BytesIO for processing functions
                    img_io = io.BytesIO()
                    pil_img.save(img_io, "PNG")
                    img_io.seek(0) # Reset stream position

                    # Separate staff zones
                    staff_zones = separate_staff_zones(img_io)
                    print(f"Page {i+1}: Found {len(staff_zones)} potential staff zones.")

                    if not staff_zones:
                         yield f"data: {json.dumps({'page': i+1, 'status': 'No zones found'})}\n\n"
                         continue

                    # Process each zone
                    for j, zone_bgr in enumerate(staff_zones):
                        if zone_bgr is None or zone_bgr.size == 0:
                            print(f"Skipping invalid zone {j+1} on page {i+1}")
                            continue
                        
                        # 1. Original Zone Image (for display)
                        original_zone_pil = Image.fromarray(cv2.cvtColor(zone_bgr, cv2.COLOR_BGR2RGB))
                        original_zone_io = io.BytesIO()
                        original_zone_pil.save(original_zone_io, "PNG")
                        original_zone_base64 = base64.b64encode(original_zone_io.getvalue()).decode("utf-8")
                        
                        # 2. Remove staff lines (for detection)
                        # Ensure remove_staff_lines returns an image suitable for extract_boxes
                        zone_no_lines = remove_staff_lines(zone_bgr) 
                        if zone_no_lines is None or zone_no_lines.size == 0:
                            print(f"Skipping zone {j+1} on page {i+1} after line removal failed.")
                            continue

                        # Convert processed zone (e.g., grayscale/binary) back to PIL Image -> BytesIO
                        # Assuming extract_boxes needs BGR, convert back if needed. 
                        # If extract_boxes takes grayscale, adjust accordingly.
                        # If zone_no_lines is Grayscale:
                        # processed_zone_pil = Image.fromarray(zone_no_lines) 
                        # If it's BGR (after potential conversion in remove_staff_lines):
                        processed_zone_pil = Image.fromarray(cv2.cvtColor(zone_no_lines, cv2.COLOR_BGR2RGB)) # Example if needed

                        processed_zone_io = io.BytesIO()
                        processed_zone_pil.save(processed_zone_io, "PNG")
                        processed_zone_io.seek(0)

                        # 3. Extract bounding boxes using the processed zone
                        boxes = extract_boxes(processed_zone_io)

                        # 4. Extract staff line positions from the original zone
                        staff_line_y_coords = extract_staff_lines(zone_bgr)

                        # Construct response for this zone
                        response = {
                            "session_id": session_id,
                            "page": i + 1,
                            "zone": j + 1,
                            "image_original": original_zone_base64, # Base64 encoded original zone
                            "boxes": boxes, # Dictionary of detected boxes per class
                            "staff_lines_y": staff_line_y_coords # List of y-coordinates
                        }
                        
                        # Yield the JSON response for the current zone
                        yield f"data: {json.dumps(response)}\n\n"
                        print(f"Sent: Page {i + 1}, Zone {j + 1}")
                        total_zones_processed += 1

                print(f"Finished processing. Total zones sent: {total_zones_processed}")
                yield f"data: {json.dumps({'status': 'done', 'total_pages': len(images), 'total_zones': total_zones_processed})}\n\n"

            except Exception as e:
                current_app.logger.error(f"Error during streaming for session {session_id}: {e}", exc_info=True)
                # Send an error message through the stream
                yield f"data: {json.dumps({'error': f'An error occurred during processing: {e}'})}\n\n"
            finally:
                # Clean up: remove the uploaded file and session state
                if session_id in uploaded_files_state:
                    file_to_remove = uploaded_files_state[session_id]["path"]
                    if os.path.exists(file_to_remove):
                        try:
                            os.remove(file_to_remove)
                            print(f"Cleaned up file: {file_to_remove}")
                        except OSError as rm_err:
                            current_app.logger.error(f"Error removing file {file_to_remove}: {rm_err}")
                    del uploaded_files_state[session_id]
                    print(f"Removed session state for: {session_id}")

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

        if not isinstance(music_sheet, list):
            return {"error": "Request body must be a JSON list"}, 400

        filename = combine_audio(music_sheet, measure_playtime)

        return send_file(
            filename,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=os.path.basename(filename),
        )