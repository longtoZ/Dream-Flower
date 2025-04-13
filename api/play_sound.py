from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
from pydub.effects import compress_dynamic_range
import json

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

measure_playtime = 3000
note_playtime = {
    "whole": 1 * measure_playtime,
    "half": 0.5 * measure_playtime,
    "quarter": 0.25 * measure_playtime,
    "eight": 0.125 * measure_playtime,
    "sixteenth": 0.0625 * measure_playtime,
    "thirty_second": 0.03125 * measure_playtime,
}

# zone_index = 6

TARGET_TREBLE_DBFS = -20
TARGET_BASS_DBFS = -20

def generate_audio(zone, zone_name):
    final_audio = AudioSegment.silent(duration=int(len(zone) * measure_playtime + measure_playtime * 0.25))
    measure_idx = 0

    for measure in zone:
        measure_audio = AudioSegment.silent(duration=int(measure_playtime*1.25))
        symbol_idx = 0

        for symbol in measure:
            if (symbol.get("notes")):
                # Adjust the volume of the notes before overlaying them
                num_notes = len(symbol["notes"])
                notes = [AudioSegment.from_mp3(f"sounds_modify/{note}.mp3").apply_gain(-3 * (num_notes - 1)) for note in symbol["notes"]]
                
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
                
                # Trim the chord to the correct duration. Add 100% to the duration to make it sound better
                chord = chord[:int(duration * 2)]

                # Add fade in and fade out to the chord
                chord = chord.fade_in(100)
                chord = chord.fade_out(100)

                # Add the chord to the measure audio
                measure_audio = measure_audio.overlay(chord, position=symbol_idx)
                symbol_idx += int(duration)
                
            elif (symbol.get("rest")):
                # measure_audio += AudioSegment.silent(duration=int(note_playtime[symbol["rest"]]))
                symbol_idx += int(note_playtime[symbol["rest"]])
        
        # If the measure audio is longer than the measure playtime, trim it
        if (len(measure_audio) > int(measure_playtime*1.25)):
            measure_audio = measure_audio[:int(measure_playtime*1.25)]
        
        # Add fade out to the measure audio so that it doesn't cut off abruptly and cause a pop sound
        measure_audio = measure_audio.fade_in(10).fade_out(int(measure_playtime * 0.25))

        # Add the measure audio to the final audio
        final_audio = final_audio.overlay(measure_audio, position=measure_idx * measure_playtime)
        measure_idx += 1

    return final_audio

final_audio = AudioSegment.silent(duration=0)

def process_zone(zone_index):
    with open(f"json/your-lie-in-april/z{zone_index}.json") as f:
        data = json.load(f)

    original_length = int(len(data["treble_zone"]) * measure_playtime)
    treble_audio = generate_audio(data["treble_zone"], "treble")
    bass_audio = generate_audio(data["bass_zone"], "bass")

    # Adjust the volume of the treble and bass audio
    treble_audio = treble_audio.apply_gain(TARGET_TREBLE_DBFS - treble_audio.dBFS)
    bass_audio = bass_audio.apply_gain(TARGET_BASS_DBFS - bass_audio.dBFS)

    mix_audio = treble_audio.overlay(bass_audio)

    if (mix_audio.dBFS > 0):
        mix_audio = mix_audio.apply_gain(-mix_audio.dBFS - 0.1)

    print(f"Zone {zone_index} done")
    return {
        "audio": mix_audio,
        "length": original_length,
    }

# Use ThreadPoolExecutor to process zones in parallel
with ThreadPoolExecutor() as executor:
    results = list(executor.map(process_zone, range(0, 2)))

# Combine all processed zones into the final audio
last_idx = 0

for mix_audio in results:
    final_audio += AudioSegment.silent(duration=len(mix_audio["audio"]))
    final_audio = final_audio.overlay(mix_audio["audio"], position=last_idx)

    if (final_audio.dBFS > 0):
        final_audio = final_audio.apply_gain(-final_audio.dBFS - 0.1)
        
    last_idx += mix_audio["length"]

final_audio.export(f"output/your-lie-in-april/full_mp3.mp3", format="mp3", bitrate="192k")