# app.py
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import logging

# Import configuration and resources
from config import UPLOAD_FOLDER
from resources import UploadPdf, StreamImageResults, ConvertToSheetResource

# --- Flask App Initialization ---
app = Flask(__name__)
api = Api(app)

# --- Configuration ---
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Optional: Add other Flask config like SECRET_KEY if needed later
# app.config['SECRET_KEY'] = os.urandom(24) 

# --- CORS ---
# Allow requests from any origin. For production, restrict this.
CORS(app) 
# Example for restricting origins:
# CORS(app, resources={r"/api/*": {"origins": "http://yourfrontenddomain.com"}})

# --- Logging ---
# Basic logging setup
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
app.logger.setLevel(logging.INFO) # Use Flask's logger

# --- Ensure Upload Folder Exists ---
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.logger.info(f"Upload folder '{UPLOAD_FOLDER}' ensured.")
except OSError as e:
    app.logger.error(f"Could not create upload folder '{UPLOAD_FOLDER}': {e}")
    # Depending on severity, you might want to exit or handle this differently

# --- API Resource Routing ---
# POST endpoint to upload PDF, returns a session ID
api.add_resource(UploadPdf, "/api/upload") 
api.add_resource(ConvertToSheetResource, "/api/convert-to-sheet")

# GET endpoint to stream results, takes session ID in the URL path
api.add_resource(StreamImageResults, "/api/stream/<string:session_id>")

# --- Run Application ---
if __name__ == "__main__":
    # Set debug=False for production
    # Consider using a production-ready server like Gunicorn or Waitress
    app.logger.info("Starting Flask development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)