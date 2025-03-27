from pydub import AudioSegment
from pydub.playback import play
import json

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

DOWN1 = 2
DOWN2 = 1
UP1 = -4
UP2 = -6

notes_volume_adjustment = {
    "A0": DOWN1,
    "As0": DOWN1,
    "B1": DOWN1,
    "C1": DOWN1,
    "Cs1": DOWN2,
    "D1": DOWN2,
    "Ds1": DOWN2,
    "E1": DOWN2,
    "F1": DOWN2,
    "Fs1": DOWN2,
    "G1": DOWN2,
    "Gs1": DOWN2,
    "A1": DOWN2,
    "As1": DOWN2,
    "B2": DOWN2,
    "C2": DOWN2,
    "Cs2": DOWN1,
    "D2": DOWN1,
    "Ds2": DOWN1,
    "E2": DOWN1,
    "F2": DOWN1,
    "Fs2": DOWN1,
    "G2": DOWN1,
    "Gs2": DOWN1,
    "A2": DOWN1,
    "As2": DOWN1,
    "B3": DOWN1,
    "C3": 0,
    "Cs3": 0,
    "D3": 0,
    "Ds3": 0,
    "E3": 0,
    "F3": 0,
    "Fs3": 0,
    "G3": 0,
    "Gs3": 0,
    "A3": 0,
    "As3": 0,
    "B4": 0,
    "C4": 0,
    "Cs4": 0,
    "D4": 0,
    "Ds4": 0,
    "E4": 0,
    "F4": 0,
    "Fs4": 0,
    "G4": 0,
    "Gs4": 0,
    "A4": 0,
    "As4": 0,
    "B5": 0,
    "C5": 0,
    "Cs5": UP1,
    "D5": UP1,
    "Ds5": UP1,
    "E5": UP1,
    "F5": UP1,
    "Fs5": UP1,
    "G5": UP1,
    "Gs5": UP1,
    "A5": UP1,
    "As5": UP1,
    "B6": UP1,
    "C6": UP2,
    "Cs6": UP2,
    "D6": UP2,
    "Ds6": UP2,
    "E6": UP2,
    "F6": UP2,
    "Fs6": UP2,
    "G6": UP2,
    "Gs6": UP2,
    "A6": UP2,
    "As6": UP2,
    "B7": UP2,
    "C7": UP2,
    "Cs7": UP2,
    "D7": UP2,
    "Ds7": UP2,
    "E7": UP2,
    "F7": UP2,
    "Fs7": UP2,
    "G7": UP2,
    "Gs7": UP2,
    "A7": UP2,
    "As7": UP2,
    "B8": UP2,
    "C8": UP2,
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

# zone_index = 6

final_audio = AudioSegment.silent(duration=0)

for zone_index in range(0, 23):
    with open(f"json/rewrite-the-stars/z{zone_index}.json") as f:
        data = json.load(f)

    def generate_audio(zone):
        final_audio = AudioSegment.silent(duration=0)

        for measure in zone:
            measure_audio = AudioSegment.silent(duration=0)

            for symbol in measure:
                if (symbol.get("notes")):
                    notes = [AudioSegment.from_mp3(f"sounds/{note}.mp3").apply_gain(notes_volume_adjustment[note]) for note in symbol["notes"]]
                    # Create a chord by overlaying all notes
                    chord = notes[0]
                    for note in notes[1:]:
                        chord = chord.overlay(note)

                    # Set the duration
                    # If the note doesn't have a flag, the duration is the same as the head type
                    duration = 0
                    if (len(symbol["flag_type"]) == 0):
                        duration = note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")]
                    else:
                        duration = note_playtime[symbol["flag_type"]]
                    
                    # Check if the note is dotted
                    if (symbol["head_type"].count("dotted") > 0):
                        if (len(symbol["flag_type"]) == 0):
                            duration += note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")] / 2
                        else:
                            duration += note_playtime[symbol["flag_type"]] / 2
                    
                    # Trim the chord to the correct duration
                    chord = chord[:int(duration)]

                    # Add fade in and fade out to the chord
                    chord = chord.fade_in(100)
                    chord = chord.fade_out(100)

                    # Add the chord to the measure audio
                    measure_audio += chord
                elif (symbol.get("rest")):
                    measure_audio += AudioSegment.silent(duration=int(note_playtime[symbol["rest"]]))
            
            # If the measure audio is shorter than the measure playtime, add silence
            if (len(measure_audio) < measure_playtime):
                measure_audio += AudioSegment.silent(duration=measure_playtime - len(measure_audio))
            # If the measure audio is longer than the measure playtime, trim it
            else:
                measure_audio = measure_audio[:measure_playtime]

            # Add the measure audio to the final audio
            final_audio += measure_audio

        # final_audio.export("output/output_bass.wav", format="wav")

        return final_audio

    treble_audio = generate_audio(data["treble_zone"])
    bass_audio = generate_audio(data["bass_zone"])

    # Adjust the volume of the treble and bass audio
    treble_audio = treble_audio.apply_gain(-10)
    bass_audio = bass_audio.apply_gain(-10)

    mix_audio = treble_audio.overlay(bass_audio)
    final_audio += mix_audio

    print("Zone", zone_index, "done")

final_audio.export(f"output/rewrite-the-stars/full.wav", format="wav")