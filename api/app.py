import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import logging
from extensions import socketio

# Import configuration and resources
from config import UPLOAD_FOLDER
from resources import UploadPdf, StreamImageResults, ConvertToSheetResource, GenerateAudioResource

# --- Flask App Initialization ---
app = Flask(__name__)
api = Api(app)

# --- SocketIO Initialization ---
socketio.init_app(app, cors_allowed_origins="*") # Allow all origins for development

# --- Configuration ---
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- CORS ---
CORS(app) 

# --- Logging ---
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
app.logger.setLevel(logging.INFO) # Use Flask's logger

# --- Ensure Upload Folder Exists ---
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.logger.info(f"Upload folder '{UPLOAD_FOLDER}' ensured.")
except OSError as e:
    app.logger.error(f"Could not create upload folder '{UPLOAD_FOLDER}': {e}")

@socketio.on('connect', namespace='/audio')
def handle_connect():
    print('Client connected to /audio')

@socketio.on('disconnect', namespace='/audio')
def handle_disconnect():
    print('Client disconnected from /audio')

# --- API Resource Routing ---
api.add_resource(UploadPdf, "/api/upload") 
api.add_resource(ConvertToSheetResource, "/api/convert-to-sheet")
api.add_resource(GenerateAudioResource, "/api/generate-audio")
api.add_resource(StreamImageResults, "/api/stream/<string:session_id>")

# --- Run Application ---
if __name__ == "__main__":
    app.logger.info("Starting Flask development server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)