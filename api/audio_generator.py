from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

AudioSegment.converter = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "ffmpeg-build/bin/ffprobe.exe"

TARGET_DBFS = {
    "treble": -25,  # Lowered for more headroom
    "bass": -25
}

CHEKPOINTS = {
    "page": 1,
    "zone": 1,
    "measure": 1,
    "time": 0,
    "checkpoints": []
}

USED_NOTES = {}

FOLDER_PATH = ["sounds_modify/", ""]

SOCKET = {
    "socket_io": None,
    "socket_id": None
}

def generate_audio(zone, zone_name, measure_playtime, note_playtime):
    original_length = sum([measure_playtime * measure["measure_duration"] for measure in zone])
    chord_delay = 50 if zone_name == "treble" else 100  # Reduced for crisper sound
    final_audio = AudioSegment.silent(duration=int(original_length * 1.25))
    next_position = 0

    for measure_idx, measure in enumerate(zone):
        actual_measure_playtime = measure_playtime * measure["measure_duration"]
        measure_audio = AudioSegment.silent(duration=int(actual_measure_playtime * 1.25))
        symbol_idx = 0

        for symbol in measure["symbols"]:
            if symbol.get("notes"):
                num_notes = len(symbol["notes"])
                notes = []
                for i, note in enumerate(symbol["notes"]):
                    if note not in USED_NOTES:
                        USED_NOTES[note] = AudioSegment.from_mp3(f"{''.join(FOLDER_PATH)}{note}.mp3")
                    # Lower gain more aggressively and pan notes slightly
                    note_audio = USED_NOTES[note].apply_gain(-4 * (num_notes - 1))
                    pan_value = 0.2 * (i % 2 * 2 - 1)  # Alternate left (-0.2) and right (0.2)
                    note_audio = note_audio.pan(pan_value)
                    notes.append(note_audio)

                # Create chord with slight time offsets to reduce phase interference
                chord = notes[0]
                for i, note in enumerate(notes[1:], 1):
                    chord = chord.overlay(note, position=5 * i)  # 5ms offset per note

                # Set duration
                duration = 0
                if len(symbol["flag_type"]) == 0:
                    duration = note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")]
                else:
                    duration = note_playtime[symbol["flag_type"]]

                if symbol["head_type"].count("dotted") > 0:
                    if len(symbol["flag_type"]) == 0:
                        duration += note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")] / 2
                    else:
                        duration += note_playtime[symbol["flag_type"]] / 2

                # Trim chord to 1.5x duration for less overlap
                chord = chord[:int(duration * 1.5)]

                # Apply lighter fade for crisper attacks
                chord = chord.fade_in(50).fade_out(chord_delay)

                measure_audio = measure_audio.overlay(chord, position=symbol_idx)
                symbol_idx += int(duration)

            elif symbol.get("rest"):
                symbol_idx += int(note_playtime[symbol["rest"]])

        if len(measure_audio) > int(actual_measure_playtime * 1.25):
            measure_audio = measure_audio[:int(actual_measure_playtime * 1.25)]

        measure_audio = measure_audio.fade_in(10).fade_out(int(actual_measure_playtime * 0.25))
        final_audio = final_audio.overlay(measure_audio, position=next_position)
        next_position += actual_measure_playtime

        SOCKET["socket_io"].emit("status_update", {"message": f"{zone_name.capitalize()} - Measure {measure['measure']} done"}, namespace="/audio", to=SOCKET["socket_id"])

    return final_audio, original_length

def process_zone(data, measure_playtime, note_playtime):
    treble_audio, original_length = generate_audio(data["treble_zone"], "treble", measure_playtime, note_playtime)
    bass_audio, _ = generate_audio(data["bass_zone"], "bass", measure_playtime, note_playtime)

    # Adjust volume with headroom
    treble_audio = treble_audio.apply_gain(TARGET_DBFS["treble"] - treble_audio.dBFS)
    bass_audio = bass_audio.apply_gain(TARGET_DBFS["bass"] - bass_audio.dBFS)

    mix_audio = treble_audio.overlay(bass_audio)

    # Prevent clipping
    if mix_audio.max_dBFS > -0.1:
        mix_audio = mix_audio.apply_gain(-mix_audio.max_dBFS - 0.5)

    print(f"Page: {data['page']} - Zone {data['zone']} done")
    SOCKET["socket_io"].emit("status_update", {"message": f"Page: {data['page']} - Zone {data['zone']} done"}, namespace="/audio", to=SOCKET["socket_id"])

    return {
        "audio": mix_audio,
        "length": original_length,
    }

def set_checkpoints(music_sheet, measure_playtime):
    for data in music_sheet:
        CHEKPOINTS["page"] = data["page"]
        CHEKPOINTS["zone"] = data["zone"]

        for measure in data["treble_zone"]:
            CHEKPOINTS["measure"] = measure["measure"]
            CHEKPOINTS["checkpoints"].append({
                "page": CHEKPOINTS["page"],
                "zone": CHEKPOINTS["zone"],
                "measure": CHEKPOINTS["measure"],
                "time": CHEKPOINTS["time"],
            })
            actual_measure_playtime = measure_playtime * measure["measure_duration"]
            CHEKPOINTS["time"] += actual_measure_playtime

def combine_audio(socket, music_sheet, measure_playtime, audio_theme):
    SOCKET["socket_io"] = socket["socket_io"]
    SOCKET["socket_id"] = socket["socket_id"]

    print(f"Socket IO: {SOCKET['socket_io']}")
    print(f"Socket ID: {SOCKET['socket_id']}")

    note_playtime = {
        "whole": 1 * measure_playtime,
        "half": 0.5 * measure_playtime,
        "quarter": 0.25 * measure_playtime,
        "eight": 0.125 * measure_playtime,
        "sixteenth": 0.0625 * measure_playtime,
        "thirty_second": 0.03125 * measure_playtime,
    }

    if audio_theme == "organ":
        FOLDER_PATH[1] = "organ/"
        TARGET_DBFS["bass"] = -28  # Slightly lower for organ's rich harmonics
    elif audio_theme == "violin":
        FOLDER_PATH[1] = "violin/"
        TARGET_DBFS["bass"] = -30
    elif audio_theme == "upright_piano":
        FOLDER_PATH[1] = "upright_piano/"
    elif audio_theme == "classical_piano":
        FOLDER_PATH[1] = "classical_piano/"
    elif audio_theme == "auditorium_piano":
        FOLDER_PATH[1] = "auditorium_piano/"

    SOCKET["socket_io"].emit("status_update", {"message": f"Select audio theme: {audio_theme}"}, namespace="/audio", to=SOCKET["socket_id"])

    final_audio = AudioSegment.silent(duration=0)

    SOCKET["socket_io"].emit("status_update", {"message": "Start generating audio concurently..."}, namespace="/audio", to=SOCKET["socket_id"])

    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_zone, music_sheet, [measure_playtime] * len(music_sheet), [note_playtime] * len(music_sheet)))

    last_idx = 0
    for i, mix_audio in enumerate(results):
        adding_length = len(mix_audio["audio"]) if i == 0 else mix_audio["length"]
        final_audio += AudioSegment.silent(duration=adding_length)
        final_audio = final_audio.overlay(mix_audio["audio"], position=last_idx)

        if final_audio.max_dBFS > -0.1:
            final_audio = final_audio.apply_gain(-final_audio.max_dBFS - 0.5)

        last_idx += mix_audio["length"]

    if audio_theme == "violin":
        final_audio = final_audio.low_pass_filter(3000).high_pass_filter(200)

    SOCKET["socket_io"].emit("status_update", {"message": "Setting checkpoints for measures..."}, namespace="/audio", to=SOCKET["socket_id"])
    set_checkpoints(music_sheet, measure_playtime)
    SOCKET["socket_io"].emit("status_update", {"message": "Audio generation is completed! Exporting to file..."}, namespace="/audio", to=SOCKET["socket_id"])

    filename = str(uuid4())
    final_audio.export(f"output/{filename}.mp3", format="mp3", bitrate="192k")
    SOCKET["socket_io"].emit("status_update", {"message": "Audio file is ready!"}, namespace="/audio", to=SOCKET["socket_id"])

    return f"output/{filename}.mp3", CHEKPOINTS["checkpoints"]