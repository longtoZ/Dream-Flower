from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which
import os

AudioSegment.converter = "../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "../ffmpeg-build/bin/ffprobe.exe"

note_sounds = {
    "A1": AudioSegment.from_mp3("../sounds_modify/A1.mp3"),
}

def pitch_shift(sound, shift):
    return sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * (2 ** (shift / 12.0)))
    })

# Generate missing notes B1
b1 = pitch_shift(note_sounds["A1"], 2)
b1.export("../sounds_modify/B1.mp3", format="mp3")