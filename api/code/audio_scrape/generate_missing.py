from pydub import AudioSegment

import os

AudioSegment.converter = "../../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "../../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "../../ffmpeg-build/bin/ffprobe.exe"

notes_list = ['A1', 'C2', 'Ds2', 'Fs2', 'A2', 'C3', 'Ds3', 'Fs3',
              'A3', 'C4', 'Ds4', 'Fs4', 'A4', 'C5', 'Ds5', 'Fs5',
              'A5', 'C6', 'Ds6', 'Fs6', 'A6', 'C7', 'Ds7', 'Fs7',
              'A7', 'C8']

note_sounds = {}
for note in notes_list:
    file_path = f"original_audio/{note}.mp3"
    if os.path.exists(file_path):
        note_sounds[note] = AudioSegment.from_mp3(file_path)
    else:
        print(f"Warning: File {file_path} not found. Skipping.")

def pitch_shift(sound, shift):
    return sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * (2 ** (shift / 12.0)))
    })

# Generate missing notes
a0 = pitch_shift(note_sounds["A1"], -12)
as0 = pitch_shift(note_sounds["A1"], -11)
b0 = pitch_shift(note_sounds["A1"], -10)
c1 = pitch_shift(note_sounds["A1"], -9)
cs1 = pitch_shift(note_sounds["A1"], -8)
d1 = pitch_shift(note_sounds["A1"], -7)
ds1 = pitch_shift(note_sounds["A1"], -6)
e1 = pitch_shift(note_sounds["A1"], -5)
f1 = pitch_shift(note_sounds["A1"], -4)
fs1 = pitch_shift(note_sounds["A1"], -3)
g1 = pitch_shift(note_sounds["A1"], -2)
gs1 = pitch_shift(note_sounds["A1"], -1)

a1 = pitch_shift(note_sounds["A1"], 0)
as1 = pitch_shift(note_sounds["A1"], 1)
b1 = pitch_shift(note_sounds["A1"], 2)
c2 = pitch_shift(note_sounds["C2"], 0)
cs2 = pitch_shift(note_sounds["C2"], 1)
d2 = pitch_shift(note_sounds["C2"], 2)
ds2 = pitch_shift(note_sounds["Ds2"], 0)
e2 = pitch_shift(note_sounds["Ds2"], 1)
f2 = pitch_shift(note_sounds["Ds2"], 2)
fs2 = pitch_shift(note_sounds["Fs2"], 0)
g2 = pitch_shift(note_sounds["Fs2"], 1)
gs2 = pitch_shift(note_sounds["Fs2"], 2)

a2 = pitch_shift(note_sounds["A2"], 0)
as2 = pitch_shift(note_sounds["A2"], 1)
b2 = pitch_shift(note_sounds["A2"], 2)
c3 = pitch_shift(note_sounds["C3"], 0)
cs3 = pitch_shift(note_sounds["C3"], 1)
d3 = pitch_shift(note_sounds["C3"], 2)
ds3 = pitch_shift(note_sounds["Ds3"], 0)
e3 = pitch_shift(note_sounds["Ds3"], 1)
f3 = pitch_shift(note_sounds["Ds3"], 2)
fs3 = pitch_shift(note_sounds["Fs3"], 0)
g3 = pitch_shift(note_sounds["Fs3"], 1)
gs3 = pitch_shift(note_sounds["Fs3"], 2)

a3 = pitch_shift(note_sounds["A3"], 0)
as3 = pitch_shift(note_sounds["A3"], 1)
b3 = pitch_shift(note_sounds["A3"], 2)
c4 = pitch_shift(note_sounds["C4"], 0)
cs4 = pitch_shift(note_sounds["C4"], 1)
d4 = pitch_shift(note_sounds["C4"], 2)
ds4 = pitch_shift(note_sounds["Ds4"], 0)
e4 = pitch_shift(note_sounds["Ds4"], 1)
f4 = pitch_shift(note_sounds["Ds4"], 2)
fs4 = pitch_shift(note_sounds["Fs4"], 0)
g4 = pitch_shift(note_sounds["Fs4"], 1)
gs4 = pitch_shift(note_sounds["Fs4"], 2)

a4 = pitch_shift(note_sounds["A4"], 0)
as4 = pitch_shift(note_sounds["A4"], 1)
b4 = pitch_shift(note_sounds["A4"], 2)
c5 = pitch_shift(note_sounds["C5"], 0)
cs5 = pitch_shift(note_sounds["C5"], 1)
d5 = pitch_shift(note_sounds["C5"], 2)
ds5 = pitch_shift(note_sounds["Ds5"], 0)
e5 = pitch_shift(note_sounds["Ds5"], 1)
f5 = pitch_shift(note_sounds["Ds5"], 2)
fs5 = pitch_shift(note_sounds["Fs5"], 0)
g5 = pitch_shift(note_sounds["Fs5"], 1)
gs5 = pitch_shift(note_sounds["Fs5"], 2)

a5 = pitch_shift(note_sounds["A5"], 0)
as5 = pitch_shift(note_sounds["A5"], 1)
b5 = pitch_shift(note_sounds["A5"], 2)
c6 = pitch_shift(note_sounds["C6"], 0)
cs6 = pitch_shift(note_sounds["C6"], 1)
d6 = pitch_shift(note_sounds["C6"], 2)
ds6 = pitch_shift(note_sounds["Ds6"], 0)
e6 = pitch_shift(note_sounds["Ds6"], 1)
f6 = pitch_shift(note_sounds["Ds6"], 2)
fs6 = pitch_shift(note_sounds["Fs6"], 0)
g6 = pitch_shift(note_sounds["Fs6"], 1)
gs6 = pitch_shift(note_sounds["Fs6"], 2)

a6 = pitch_shift(note_sounds["A6"], 0)
as6 = pitch_shift(note_sounds["A6"], 1)
b6 = pitch_shift(note_sounds["A6"], 2)
c7 = pitch_shift(note_sounds["C7"], 0)
cs7 = pitch_shift(note_sounds["C7"], 1)
d7 = pitch_shift(note_sounds["C7"], 2)
ds7 = pitch_shift(note_sounds["Ds7"], 0)
e7 = pitch_shift(note_sounds["Ds7"], 1)
f7 = pitch_shift(note_sounds["Ds7"], 2)
fs7 = pitch_shift(note_sounds["Fs7"], 0)
g7 = pitch_shift(note_sounds["Fs7"], 1)
gs7 = pitch_shift(note_sounds["Fs7"], 2)

a7 = pitch_shift(note_sounds["A7"], 0)
as7 = pitch_shift(note_sounds["A7"], 1)
b7 = pitch_shift(note_sounds["A7"], 2)
c8 = pitch_shift(note_sounds["C7"], 0)


# Export the audio files
output_dir = "generated_audio"
os.makedirs(output_dir, exist_ok=True)

notes = {
    "A0": a0, "As0": as0, "B0": b0, "C1": c1, "Cs1": cs1, "D1": d1, "Ds1": ds1, "E1": e1, "F1": f1, "Fs1": fs1, "G1": g1, "Gs1": gs1,
    "A1": a1, "As1": as1, "B1": b1, "C2": c2, "Cs2": cs2, "D2": d2, "Ds2": ds2, "E2": e2, "F2": f2, "Fs2": fs2, "G2": g2, "Gs2": gs2,
    "A2": a2, "As2": as2, "B2": b2, "C3": c3, "Cs3": cs3, "D3": d3, "Ds3": ds3, "E3": e3, "F3": f3, "Fs3": fs3, "G3": g3, "Gs3": gs3,
    "A3": a3, "As3": as3, "B3": b3, "C4": c4, "Cs4": cs4, "D4": d4, "Ds4": ds4, "E4": e4, "F4": f4, "Fs4": fs4, "G4": g4, "Gs4": gs4,
    "A4": a4, "As4": as4, "B4": b4, "C5": c5, "Cs5": cs5, "D5": d5, "Ds5": ds5, "E5": e5, "F5": f5, "Fs5": fs5, "G5": g5, "Gs5": gs5,
    "A5": a5, "As5": as5, "B5": b5, "C6": c6, "Cs6": cs6, "D6": d6, "Ds6": ds6, "E6": e6, "F6": f6, "Fs6": fs6, "G6": g6, "Gs6": gs6,
    "A6": a6, "As6": as6, "B6": b6, "C7": c7, "Cs7": cs7, "D7": d7, "Ds7": ds7, "E7": e7, "F7": f7, "Fs7": fs7, "G7": g7, "Gs7": gs7,
    "A7": a7, "As7": as7, "B7": b7, "C8": c8
}

for note, sound in notes.items():
    print(f"Exporting {note}.mp3")
    sound.export(os.path.join(output_dir, f"{note}.mp3"), format="mp3")