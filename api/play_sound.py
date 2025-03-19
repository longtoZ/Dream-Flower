from pydub import AudioSegment
from pydub.playback import play
import json

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

note_sounds = {
    "A0": AudioSegment.from_mp3("./sounds/A0.mp3"),
    "As0": AudioSegment.from_mp3("./sounds/As0.mp3"),
    "B1": AudioSegment.from_mp3("./sounds/B1.mp3"),
    "C1": AudioSegment.from_mp3("./sounds/C1.mp3"),
    "Cs1": AudioSegment.from_mp3("./sounds/Cs1.mp3"),
    "D1": AudioSegment.from_mp3("./sounds/D1.mp3"),
    "Ds1": AudioSegment.from_mp3("./sounds/Ds1.mp3"),
    "E1": AudioSegment.from_mp3("./sounds/E1.mp3"),
    "F1": AudioSegment.from_mp3("./sounds/F1.mp3"),
    "Fs1": AudioSegment.from_mp3("./sounds/Fs1.mp3"),
    "G1": AudioSegment.from_mp3("./sounds/G1.mp3"),
    "Gs1": AudioSegment.from_mp3("./sounds/Gs1.mp3"),
    "A1": AudioSegment.from_mp3("./sounds/A1.mp3"),
    "As1": AudioSegment.from_mp3("./sounds/As1.mp3"),
    "B2": AudioSegment.from_mp3("./sounds/B2.mp3"),
    "C2": AudioSegment.from_mp3("./sounds/C2.mp3"),
    "Cs2": AudioSegment.from_mp3("./sounds/Cs2.mp3"),
    "D2": AudioSegment.from_mp3("./sounds/D2.mp3"),
    "Ds2": AudioSegment.from_mp3("./sounds/Ds2.mp3"),
    "E2": AudioSegment.from_mp3("./sounds/E2.mp3"),
    "F2": AudioSegment.from_mp3("./sounds/F2.mp3"),
    "Fs2": AudioSegment.from_mp3("./sounds/Fs2.mp3"),
    "G2": AudioSegment.from_mp3("./sounds/G2.mp3"),
    "Gs2": AudioSegment.from_mp3("./sounds/Gs2.mp3"),
    "A2": AudioSegment.from_mp3("./sounds/A2.mp3"),
    "As2": AudioSegment.from_mp3("./sounds/As2.mp3"),
    "B3": AudioSegment.from_mp3("./sounds/B3.mp3"),
    "C3": AudioSegment.from_mp3("./sounds/C3.mp3"),
    "Cs3": AudioSegment.from_mp3("./sounds/Cs3.mp3"),
    "D3": AudioSegment.from_mp3("./sounds/D3.mp3"),
    "Ds3": AudioSegment.from_mp3("./sounds/Ds3.mp3"),
    "E3": AudioSegment.from_mp3("./sounds/E3.mp3"),
    "F3": AudioSegment.from_mp3("./sounds/F3.mp3"),
    "Fs3": AudioSegment.from_mp3("./sounds/Fs3.mp3"),
    "G3": AudioSegment.from_mp3("./sounds/G3.mp3"),
    "Gs3": AudioSegment.from_mp3("./sounds/Gs3.mp3"),
    "A3": AudioSegment.from_mp3("./sounds/A3.mp3"),
    "As3": AudioSegment.from_mp3("./sounds/As3.mp3"),
    "B4": AudioSegment.from_mp3("./sounds/B4.mp3"),
    "C4": AudioSegment.from_mp3("./sounds/C4.mp3"),
    "Cs4": AudioSegment.from_mp3("./sounds/Cs4.mp3"),
    "D4": AudioSegment.from_mp3("./sounds/D4.mp3"),
    "Ds4": AudioSegment.from_mp3("./sounds/Ds4.mp3"),
    "E4": AudioSegment.from_mp3("./sounds/E4.mp3"),
    "F4": AudioSegment.from_mp3("./sounds/F4.mp3"),
    "Fs4": AudioSegment.from_mp3("./sounds/Fs4.mp3"),
    "G4": AudioSegment.from_mp3("./sounds/G4.mp3"),
    "Gs4": AudioSegment.from_mp3("./sounds/Gs4.mp3"),
    "A4": AudioSegment.from_mp3("./sounds/A4.mp3"),
    "As4": AudioSegment.from_mp3("./sounds/As4.mp3"),
    "B5": AudioSegment.from_mp3("./sounds/B5.mp3"),
    "C5": AudioSegment.from_mp3("./sounds/C5.mp3"),
    "Cs5": AudioSegment.from_mp3("./sounds/Cs5.mp3"),
    "D5": AudioSegment.from_mp3("./sounds/D5.mp3"),
    "Ds5": AudioSegment.from_mp3("./sounds/Ds5.mp3"),
    "E5": AudioSegment.from_mp3("./sounds/E5.mp3"),
    "F5": AudioSegment.from_mp3("./sounds/F5.mp3"),
    "Fs5": AudioSegment.from_mp3("./sounds/Fs5.mp3"),
    "G5": AudioSegment.from_mp3("./sounds/G5.mp3"),
    "Gs5": AudioSegment.from_mp3("./sounds/Gs5.mp3"),
    "A5": AudioSegment.from_mp3("./sounds/A5.mp3"),
    "As5": AudioSegment.from_mp3("./sounds/As5.mp3"),
    "B6": AudioSegment.from_mp3("./sounds/B6.mp3"),
    "C6": AudioSegment.from_mp3("./sounds/C6.mp3"),
    "Cs6": AudioSegment.from_mp3("./sounds/Cs6.mp3"),
    "D6": AudioSegment.from_mp3("./sounds/D6.mp3"),
    "Ds6": AudioSegment.from_mp3("./sounds/Ds6.mp3"),
    "E6": AudioSegment.from_mp3("./sounds/E6.mp3"),
    "F6": AudioSegment.from_mp3("./sounds/F6.mp3"),
    "Fs6": AudioSegment.from_mp3("./sounds/Fs6.mp3"),
    "G6": AudioSegment.from_mp3("./sounds/G6.mp3"),
    "Gs6": AudioSegment.from_mp3("./sounds/Gs6.mp3"),
    "A6": AudioSegment.from_mp3("./sounds/A6.mp3"),
    "As6": AudioSegment.from_mp3("./sounds/As6.mp3"),
    "B7": AudioSegment.from_mp3("./sounds/B7.mp3"),
    "C7": AudioSegment.from_mp3("./sounds/C7.mp3"),
    "Cs7": AudioSegment.from_mp3("./sounds/Cs7.mp3"),
    "D7": AudioSegment.from_mp3("./sounds/D7.mp3"),
    "Ds7": AudioSegment.from_mp3("./sounds/Ds7.mp3"),
    "E7": AudioSegment.from_mp3("./sounds/E7.mp3"),
    "F7": AudioSegment.from_mp3("./sounds/F7.mp3"),
    "Fs7": AudioSegment.from_mp3("./sounds/Fs7.mp3"),
    "G7": AudioSegment.from_mp3("./sounds/G7.mp3"),
    "Gs7": AudioSegment.from_mp3("./sounds/Gs7.mp3"),
    "A7": AudioSegment.from_mp3("./sounds/A7.mp3"),
    "As7": AudioSegment.from_mp3("./sounds/As7.mp3"),
    "B8": AudioSegment.from_mp3("./sounds/B8.mp3"),
    "C8": AudioSegment.from_mp3("./sounds/C8.mp3"),
}

measure_playtime = 2000
note_playtime = {
    "whole": 1 * measure_playtime,
    "half": 0.5 * measure_playtime,
    "quarter": 0.25 * measure_playtime,
    "eight": 0.125 * measure_playtime,
    "sixteenth": 0.0625 * measure_playtime,
    "thirty_second": 0.03125 * measure_playtime,
}

with open("json/result_mix.json") as f:
    data = json.load(f)

def generate_audio(zone):
    final_audio = AudioSegment.silent(duration=0)

    for symbol in zone:
        if (symbol.get("notes")):
            notes = [AudioSegment.from_mp3(f"sounds/{note}.mp3") for note in symbol["notes"]]
            # Create a chord by overlaying all notes
            chord = notes[0].apply_gain(-10)
            for note in notes[1:]:
                chord = chord.overlay(note)
            
            # Trim the chord to the correct duration
            chord = chord[:int(note_playtime[symbol["flag_type"]])]

            # Add fade in and fade out to the chord
            chord = chord.fade_in(100)
            chord = chord.fade_out(100)

            # Add the chord to the final audio
            final_audio += chord
        elif (symbol.get("rest")):
            final_audio += AudioSegment.silent(duration=int(note_playtime[symbol["rest"]]))

    # final_audio.export("output/output_bass.wav", format="wav")

    return final_audio

treble_audio = generate_audio(data["treble_zone"])
bass_audio = generate_audio(data["bass_zone"])

# Adjust the volume of the treble and bass audio
treble_audio = treble_audio.apply_gain(-10)
bass_audio = bass_audio.apply_gain(-10)

final_audio = treble_audio.overlay(bass_audio)

final_audio.export("output/output_full_mix.wav", format="wav")