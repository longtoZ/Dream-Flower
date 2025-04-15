import os
from pydub import AudioSegment

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

source_folder = "sounds_modify"
destination_folder = "sounds_normalize"

for filename in os.listdir(source_folder):
    if filename.endswith(".mp3"):
        # Load the audio file
        audio = AudioSegment.from_file(os.path.join(source_folder, filename))

        # Normalize the volume to -20 dBFS
        normalized_audio = audio.apply_gain(-20 - audio.dBFS)

        # Export the normalized audio to the destination folder
        normalized_audio.export(os.path.join(destination_folder, filename), format="mp3")
        print(f"Normalized {filename} and saved to {destination_folder}.")