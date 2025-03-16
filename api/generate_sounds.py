from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which
import os

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

note_sounds = {
    "A0": AudioSegment.from_mp3("./sounds/A0.mp3"),
    "C1": AudioSegment.from_mp3("./sounds/C1.mp3"),
    "Ds1": AudioSegment.from_mp3("./sounds/Ds1.mp3"),
    "Fs1": AudioSegment.from_mp3("./sounds/Fs1.mp3"),
    "A1": AudioSegment.from_mp3("./sounds/A1.mp3"),
    "C2": AudioSegment.from_mp3("./sounds/C2.mp3"),
    "Ds2": AudioSegment.from_mp3("./sounds/Ds2.mp3"),
    "Fs2": AudioSegment.from_mp3("./sounds/Fs2.mp3"),
    "A2": AudioSegment.from_mp3("./sounds/A2.mp3"),
    "C3": AudioSegment.from_mp3("./sounds/C3.mp3"),
    "Ds3": AudioSegment.from_mp3("./sounds/Ds3.mp3"),
    "Fs3": AudioSegment.from_mp3("./sounds/Fs3.mp3"),
    "A3": AudioSegment.from_mp3("./sounds/A3.mp3"),
    "C4": AudioSegment.from_mp3("./sounds/C4.mp3"),
    "Ds4": AudioSegment.from_mp3("./sounds/Ds4.mp3"),
    "Fs4": AudioSegment.from_mp3("./sounds/Fs4.mp3"),
    "A4": AudioSegment.from_mp3("./sounds/A4.mp3"),
    "C5": AudioSegment.from_mp3("./sounds/C5.mp3"),
    "Ds5": AudioSegment.from_mp3("./sounds/Ds5.mp3"),
    "Fs5": AudioSegment.from_mp3("./sounds/Fs5.mp3"),
    "A5": AudioSegment.from_mp3("./sounds/A5.mp3"),
    "C6": AudioSegment.from_mp3("./sounds/C6.mp3"),
    "Ds6": AudioSegment.from_mp3("./sounds/Ds6.mp3"),
    "Fs6": AudioSegment.from_mp3("./sounds/Fs6.mp3"),
    "A6": AudioSegment.from_mp3("./sounds/A6.mp3"),
    "C7": AudioSegment.from_mp3("./sounds/C7.mp3"),
    "Ds7": AudioSegment.from_mp3("./sounds/Ds7.mp3"),
    "Fs7": AudioSegment.from_mp3("./sounds/Fs7.mp3"),
    "A7": AudioSegment.from_mp3("./sounds/A7.mp3"),
    "C8": AudioSegment.from_mp3("./sounds/C8.mp3"),
}

def pitch_shift(sound, shift):
    return sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * (2 ** (shift / 12.0)))
    })

# Generate missing notes
as0 = pitch_shift(note_sounds["A0"], 1)
b1 = pitch_shift(note_sounds["A0"], 2)
cs1 = pitch_shift(note_sounds["C1"], 1)
d1 = pitch_shift(note_sounds["C1"], 2)
e1 = pitch_shift(note_sounds["Ds1"], 1)
f1 = pitch_shift(note_sounds["Ds1"], 2)
g1 = pitch_shift(note_sounds["Fs1"], 1)
gs1 = pitch_shift(note_sounds["Fs1"], 2)

as1 = pitch_shift(note_sounds["A1"], 1)
b2 = pitch_shift(note_sounds["A1"], 2)
cs2 = pitch_shift(note_sounds["C2"], 1)
d2 = pitch_shift(note_sounds["C2"], 2)
e2 = pitch_shift(note_sounds["Ds2"], 1)
f2 = pitch_shift(note_sounds["Ds2"], 2)
g2 = pitch_shift(note_sounds["Fs2"], 1)
gs2 = pitch_shift(note_sounds["Fs2"], 2)

as2 = pitch_shift(note_sounds["A2"], 1)
b3 = pitch_shift(note_sounds["A2"], 2)
cs3 = pitch_shift(note_sounds["C3"], 1)
d3 = pitch_shift(note_sounds["C3"], 2)
e3 = pitch_shift(note_sounds["Ds3"], 1)
f3 = pitch_shift(note_sounds["Ds3"], 2)
g3 = pitch_shift(note_sounds["Fs3"], 1)
gs3 = pitch_shift(note_sounds["Fs3"], 2)

as3 = pitch_shift(note_sounds["A3"], 1)
b4 = pitch_shift(note_sounds["A3"], 2)
cs4 = pitch_shift(note_sounds["C4"], 1)
d4 = pitch_shift(note_sounds["C4"], 2)
e4 = pitch_shift(note_sounds["Ds4"], 1)
f4 = pitch_shift(note_sounds["Ds4"], 2)
g4 = pitch_shift(note_sounds["Fs4"], 1)
gs4 = pitch_shift(note_sounds["Fs4"], 2)

as4 = pitch_shift(note_sounds["A4"], 1)
b5 = pitch_shift(note_sounds["A4"], 2)
cs5 = pitch_shift(note_sounds["C5"], 1)
d5 = pitch_shift(note_sounds["C5"], 2)
e5 = pitch_shift(note_sounds["Ds5"], 1)
f5 = pitch_shift(note_sounds["Ds5"], 2)
g5 = pitch_shift(note_sounds["Fs5"], 1)
gs5 = pitch_shift(note_sounds["Fs5"], 2)

as5 = pitch_shift(note_sounds["A5"], 1)
b6 = pitch_shift(note_sounds["A5"], 2)
cs6 = pitch_shift(note_sounds["C6"], 1)
d6 = pitch_shift(note_sounds["C6"], 2)
e6 = pitch_shift(note_sounds["Ds6"], 1)
f6 = pitch_shift(note_sounds["Ds6"], 2)
g6 = pitch_shift(note_sounds["Fs6"], 1)
gs6 = pitch_shift(note_sounds["Fs6"], 2)

as6 = pitch_shift(note_sounds["A6"], 1)
b7 = pitch_shift(note_sounds["A6"], 2)
cs7 = pitch_shift(note_sounds["C7"], 1)
d7 = pitch_shift(note_sounds["C7"], 2)
e7 = pitch_shift(note_sounds["Ds7"], 1)
f7 = pitch_shift(note_sounds["Ds7"], 2)
g7 = pitch_shift(note_sounds["Fs7"], 1)
gs7 = pitch_shift(note_sounds["Fs7"], 2)

as7 = pitch_shift(note_sounds["A7"], 1)
b8 = pitch_shift(note_sounds["A7"], 2)

# Export the audio files
as0.export("./missing_sounds/As0.mp3", format="mp3")
b1.export("./missing_sounds/B1.mp3", format="mp3")
cs1.export("./missing_sounds/Cs1.mp3", format="mp3")
d1.export("./missing_sounds/D1.mp3", format="mp3")
e1.export("./missing_sounds/E1.mp3", format="mp3")
f1.export("./missing_sounds/F1.mp3", format="mp3")
g1.export("./missing_sounds/G1.mp3", format="mp3")
gs1.export("./missing_sounds/Gs1.mp3", format="mp3")

as1.export("./missing_sounds/As1.mp3", format="mp3")
b2.export("./missing_sounds/B2.mp3", format="mp3")
cs2.export("./missing_sounds/Cs2.mp3", format="mp3")
d2.export("./missing_sounds/D2.mp3", format="mp3")
e2.export("./missing_sounds/E2.mp3", format="mp3")
f2.export("./missing_sounds/F2.mp3", format="mp3")
g2.export("./missing_sounds/G2.mp3", format="mp3")
gs2.export("./missing_sounds/Gs2.mp3", format="mp3")

as2.export("./missing_sounds/As2.mp3", format="mp3")
b3.export("./missing_sounds/B3.mp3", format="mp3")
cs3.export("./missing_sounds/Cs3.mp3", format="mp3")
d3.export("./missing_sounds/D3.mp3", format="mp3")
e3.export("./missing_sounds/E3.mp3", format="mp3")
f3.export("./missing_sounds/F3.mp3", format="mp3")
g3.export("./missing_sounds/G3.mp3", format="mp3")
gs3.export("./missing_sounds/Gs3.mp3", format="mp3")

as3.export("./missing_sounds/As3.mp3", format="mp3")
b4.export("./missing_sounds/B4.mp3", format="mp3")
cs4.export("./missing_sounds/Cs4.mp3", format="mp3")
d4.export("./missing_sounds/D4.mp3", format="mp3")
e4.export("./missing_sounds/E4.mp3", format="mp3")
f4.export("./missing_sounds/F4.mp3", format="mp3")
g4.export("./missing_sounds/G4.mp3", format="mp3")
gs4.export("./missing_sounds/Gs4.mp3", format="mp3")

as4.export("./missing_sounds/As4.mp3", format="mp3")
b5.export("./missing_sounds/B5.mp3", format="mp3")
cs5.export("./missing_sounds/Cs5.mp3", format="mp3")
d5.export("./missing_sounds/D5.mp3", format="mp3")
e5.export("./missing_sounds/E5.mp3", format="mp3")
f5.export("./missing_sounds/F5.mp3", format="mp3")
g5.export("./missing_sounds/G5.mp3", format="mp3")
gs5.export("./missing_sounds/Gs5.mp3", format="mp3")

as5.export("./missing_sounds/As5.mp3", format="mp3")
b6.export("./missing_sounds/B6.mp3", format="mp3")
cs6.export("./missing_sounds/Cs6.mp3", format="mp3")
d6.export("./missing_sounds/D6.mp3", format="mp3")
e6.export("./missing_sounds/E6.mp3", format="mp3")
f6.export("./missing_sounds/F6.mp3", format="mp3")
g6.export("./missing_sounds/G6.mp3", format="mp3")
gs6.export("./missing_sounds/Gs6.mp3", format="mp3")

as6.export("./missing_sounds/As6.mp3", format="mp3")
b7.export("./missing_sounds/B7.mp3", format="mp3")
cs7.export("./missing_sounds/Cs7.mp3", format="mp3")
d7.export("./missing_sounds/D7.mp3", format="mp3")
e7.export("./missing_sounds/E7.mp3", format="mp3")
f7.export("./missing_sounds/F7.mp3", format="mp3")
g7.export("./missing_sounds/G7.mp3", format="mp3")
gs7.export("./missing_sounds/Gs7.mp3", format="mp3")

as7.export("./missing_sounds/As7.mp3", format="mp3")
b8.export("./missing_sounds/B8.mp3", format="mp3")