# config.py
import os
import torch

# --- Constants ---
UPLOAD_FOLDER = "uploads"
NUMBER_OF_CLASSES = 21
CLASS_NAMES = [
    'barline', 'bass_clef', 'decrescendo', 'dotted_half_note', 
    'dotted_quarter_note', 'eight_beam', 'eight_flag', 'eight_rest', 
    'flat', 'half_note', 'natural', 'quarter_note', 'quarter_rest', 
    'sharp', 'sixteenth_beam', 'sixteenth_flag', 'sixteenth_rest', 
    'thirty_second_beam', 'treble_clef', 'whole_half_rest', 'whole_note'
]

# --- Model Configuration ---
# IMPORTANT: Ensure this path is correct relative to where app.py will be run,
# or use an absolute path or environment variable.
MODEL_PATH = r"C:\Users\VICTUS\Documents\OMR project\model_training\runs\detect\train7\weights\best.pt" 

# --- Device Configuration ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Poppler Path (if needed system-wide) ---
# If poppler is not in PATH, specify its bin directory
# Example: POPPLER_PATH = "/path/to/poppler-xx.yy.z/Library/bin" 
# Set to None if poppler is in the system PATH
POPPLER_PATH = "./poppler-24.08.0/Library/bin" # Or adjust as needed