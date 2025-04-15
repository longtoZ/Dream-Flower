import os
import shutil
import re

# Define source and destination folders
source_folder = "sounds"
destination_folder = "sounds_modify"

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Regular expression to match note filenames (e.g., A0.mp3, As1.mp3)
note_pattern = re.compile(r"([A-Ga-g]s?\d)\.mp3")

# Process all files in the source folder
for filename in os.listdir(source_folder):
    match = note_pattern.match(filename)
    if match:
        note = match.group(1)  # Extract note (e.g., "A0", "As1")
        base_note = note[:-1]  # Extract note without octave (e.g., "A", "As")
        octave = int(note[-1])  # Extract octave number
        
        new_octave = octave + 1  # Increase the octave by 1
        new_filename = f"{base_note}{new_octave}.mp3"  # Create new filename

        # Copy and rename the file to the destination folder
        shutil.copy(
            os.path.join(source_folder, filename),
            os.path.join(destination_folder, new_filename)
        )
        print(f"Copied {filename} → {new_filename}")

print("✅ All note files have been copied with increased octaves.")
