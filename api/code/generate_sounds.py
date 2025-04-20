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

# Generate missing notes from B0 to Gs1

b0 = pitch_shift(note_sounds["A1"], -10)  # B0 is 10 semitones below A1
c1 = pitch_shift(note_sounds["A1"], -9)   # C1 is 9 semitones below A1
cs1 = pitch_shift(note_sounds["A1"], -8)  # C#1 is 8 semitones below A1
d1 = pitch_shift(note_sounds["A1"], -7)   # D1 is 7 semitones below A1
ds1 = pitch_shift(note_sounds["A1"], -6)  # D#1 is 6 semitones below A1
e1 = pitch_shift(note_sounds["A1"], -5)   # E1 is 5 semitones below A1
f1 = pitch_shift(note_sounds["A1"], -4)   # F1 is 4 semitones below A1
fs1 = pitch_shift(note_sounds["A1"], -3)  # F#1 is 3 semitones below A1
g1 = pitch_shift(note_sounds["A1"], -2)   # G1 is 2 semitones below A1
gs1 = pitch_shift(note_sounds["A1"], -1)  # G#1 is 1 semitone below A1

b0.export("../sounds_modify/B0.mp3", format="mp3")
c1.export("../sounds_modify/C1.mp3", format="mp3")
cs1.export("../sounds_modify/Cs1.mp3", format="mp3")
d1.export("../sounds_modify/D1.mp3", format="mp3")
ds1.export("../sounds_modify/Ds1.mp3", format="mp3")
e1.export("../sounds_modify/E1.mp3", format="mp3")
f1.export("../sounds_modify/F1.mp3", format="mp3")
fs1.export("../sounds_modify/Fs1.mp3", format="mp3")
g1.export("../sounds_modify/G1.mp3", format="mp3")
gs1.export("../sounds_modify/Gs1.mp3", format="mp3")
