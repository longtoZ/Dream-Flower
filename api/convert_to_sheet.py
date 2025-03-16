import json

CLASS_NAMES = [
    "barline", "bass_clef", "decrescendo", "dotted_note", "eight_beam",
    "eight_flag", "eight_rest", "flat", "half_note", "natural",
    "quarter_note", "quarter_rest", "sharp", "sixteenth_beam", "sixteenth_flag",
    "sixteenth_rest", "thirty_second_beam", "treble_clef", "whole_half_rest", "whole_note"
]

SCALE = {
    "0": "C major",
    "1b": "F major",
    "2b": "Bb major",
    "3b": "Eb major",
    "4b": "Ab major",
    "5b": "Db major",
    "6b": "Gb major",
    "7b": "Cb major",
    "1#": "G major",
    "2#": "D major",
    "3#": "A major",
    "4#": "E major",
    "5#": "B major",
    "6#": "F# major",
    "7#": "C# major"
}

with open("json/data.json", "r") as f:
    full_data = json.load(f)

data = full_data[0]

# --------------------------------- Extracting Staff Lines ---------------------------------
staff_lines = data["staff_lines"]
treble_staff_lines = {}
bass_staff_lines = {}

line_space = staff_lines[1][1] - staff_lines[0][1]

# Extend 3 more staff lines for treble clef above
treble_staff_lines["E6"] = staff_lines[0][1] - line_space*3
treble_staff_lines["C6"] = staff_lines[0][1] - line_space*2
treble_staff_lines["A5"] = staff_lines[0][1] - line_space

# Add basic 5 staff lines for treble clef
treble_staff_lines["F5"] = staff_lines[0][1]
treble_staff_lines["D5"] = staff_lines[1][1]
treble_staff_lines["B4"] = staff_lines[2][1]
treble_staff_lines["G4"] = staff_lines[3][1]
treble_staff_lines["E4"] = staff_lines[4][1]

# Extend 3 more staff lines for treble clef below
treble_staff_lines["C4"] = staff_lines[4][1] + line_space
treble_staff_lines["A3"] = staff_lines[4][1] + line_space*2
treble_staff_lines["F3"] = staff_lines[4][1] + line_space*3

# Extend 3 more staff lines for bass clef below
bass_staff_lines["G4"] = staff_lines[5][1] - line_space*3
bass_staff_lines["E4"] = staff_lines[5][1] - line_space*2
bass_staff_lines["C4"] = staff_lines[5][1] - line_space

# Add basic 5 staff lines for bass clef
bass_staff_lines["A3"] = staff_lines[5][1]
bass_staff_lines["F3"] = staff_lines[6][1]
bass_staff_lines["D3"] = staff_lines[7][1]
bass_staff_lines["B2"] = staff_lines[8][1]
bass_staff_lines["G2"] = staff_lines[9][1]

# Extend 3 more staff lines for bass clef below
bass_staff_lines["E2"] = staff_lines[9][1] + line_space
bass_staff_lines["C2"] = staff_lines[9][1] + line_space*2
bass_staff_lines["A1"] = staff_lines[9][1] + line_space*3

# --------------------------------- Extracting Symbols ---------------------------------
# Extract boxes
boxes = data["boxes"]

# Put symbol's bounding box into the correct order (from left to right, top to bottom)
treble_zones = {
    "note": [],
    "flag": [],
    "beam": [],
    "rest": [],
    "sharp": [],
    "flat": [],
    "natural": [],
    "clef": [],
}
bass_zones = []
space_max_diff = line_space

for symbol_index in range(len(boxes)):
    for box_index in range(len(boxes[symbol_index])):
        box = boxes[symbol_index][box_index]
        symbol = CLASS_NAMES[symbol_index]
        
        # Check if the coordinates are within treble zone
        if box[1] > treble_staff_lines["C6"] - space_max_diff and box[1] < treble_staff_lines["A3"] + space_max_diff:
            for key in treble_zones:
                if (symbol.count(key) > 0):
                    treble_zones[key].append({"symbol": symbol, "box": box})
                    break
        
        # Check if the coordinates are within bass zone
        if box[1] > bass_staff_lines["E4"] - space_max_diff and box[1] < bass_staff_lines["C2"] + space_max_diff:
            for key in treble_zones:
                if (symbol.count(key) > 0):
                    bass_zones.append({"symbol": symbol, "box": box})
                    break

# Sort the symbols based on their x-coordinate
for key in treble_zones:
    treble_zones[key] = sorted(treble_zones[key], key=lambda coord: (coord["box"][0], coord["box"][1]))

# --------------------------------- Determine Scale ---------------------------------
# Determine the scale
scale = ""

sharp_idx = 0
flat_idx = 0

if (len(treble_zones["sharp"]) > 0):
    # If there is a sharp symbol near the clef, determine the scale based on the sharp symbol
    if (treble_zones["sharp"][0]["box"][0] - treble_zones["clef"][0]["box"][0] < 10):
        prev_x = treble_zones["sharp"][0]["box"][0]

        while (sharp_idx < len(treble_zones["sharp"])):
            curr_x = treble_zones["sharp"][sharp_idx]["box"][0]

            if (curr_x - prev_x < 10):
                scale = SCALE[str(sharp_idx + 1) + "#"]
            else:
                break

            prev_x = curr_x
            sharp_idx += 1
    
    # If there is a sharp symbol near the clef, determine the scale based on the sharp symbol
    elif (treble_zones["flat"][0]["box"][0] - treble_zones["clef"][0]["box"][0] < 10):
        prev_x = treble_zones["flat"][0]["box"][0]

        while (flat_idx < len(treble_zones["flat"])):
            curr_x = treble_zones["flat"][flat_idx]["box"][0]

            if (curr_x - prev_x < 10):
                scale = SCALE[str(flat_idx + 1) + "b"]
            else:
                break

            prev_x = curr_x
            flat_idx += 1
    else:
        scale = SCALE["0"]

# --------------------------------- Determine Note's Pitch ---------------------------------
# Determine note's pitch
def get_note_pitch(p1, p2):
    letters = ["C", "D", "E", "F", "G", "A", "B"]

    if (letters.index(p1[0]) == 6):
        return f"{letters[0]}{p1[1] + 1}"
    elif (letters.index(p2[0]) == 0):
        return f"{letters[6]}{p2[1] - 1}"
    else:
        return f"{letters[letters.index(p1[0]) + 1]}{p1[1]}"

sheet = []
treble_staff_lines_list = list(treble_staff_lines.items())
bass_staff_lines_list = list(bass_staff_lines.items())

note_idx = 0

# Add dummy note at the end of the list to ensure the last note is processed
treble_zones["note"].append({"box": [10000, 10000, 1000, 1000]})

if (len(treble_zones["note"]) > 0):
    prev_x = treble_zones["note"][0]["box"][0]
    notes = []

    while (note_idx < len(treble_zones["note"])):
        curr_x = treble_zones["note"][note_idx]["box"][0]

        # Collect notes occurring in the same column
        if (curr_x - prev_x < 10):
            notes.append(treble_zones["note"][note_idx])
        else:
            # Sort notes based on their y-coordinate
            notes = sorted(notes, key=lambda x: x["box"][1])
            notes_data = {
                "notes": [],
                "head_type": "",
                "flag_type": "",
                "x": 0,
            }

            # Determine the pitch of each note
            for note in notes:
                # Update the farthermost x-coordinate
                notes_data["x"] = max(notes_data["x"], note["box"][2])

                # Update the head type
                notes_data["head_type"] = note["symbol"]

                y1 = note["box"][1]
                y2 = note["box"][3]
                note_pitch = ""

                # Iterate through the staff lines and find the correct line the note is laying on
                for line_idx in range(len(treble_staff_lines_list)):
                    curr_line_y = treble_staff_lines_list[line_idx][1]
                    next_line_y = treble_staff_lines_list[line_idx + 1][1] if line_idx < len(treble_staff_lines_list) - 1 else None

                    if (y1 <= curr_line_y):
                        # If the box covers two lines, the note is in staff space
                        if (next_line_y is not None and y2 >= next_line_y):
                            note_pitch = get_note_pitch(treble_staff_lines_list[line_idx + 1][0], treble_staff_lines_list[line_idx][0])
                            # print("Note in staff space:", note_pitch)
                        # If the box covers only one line, the note is on the staff line
                        else:
                            note_pitch = treble_staff_lines_list[line_idx][0]
                            # print("Note on staff line:", note_pitch)
                        
                        # print("y1:", y1, "y2:", y2, note_pitch, end="\n\n")

                        break
                
                notes_data["notes"].append(note_pitch)
            
            # Append the notes to the sheet
            sheet.append(notes_data)

            # Reset notes
            notes = [treble_zones["note"][note_idx]]

        prev_x = curr_x
        note_idx += 1

# Remove the dummy note
treble_zones["note"].pop()

# --------------------------------- Determine Note's Duration ---------------------------------
# Determine note's duration by checking the flag symbol
note_idx = 0
flag_idx = 0

if (len(treble_zones["flag"]) > 0):
    while (flag_idx < len(treble_zones["flag"])):
        curr_flag = treble_zones["flag"][flag_idx]

        # Iterate through the notes and find the note that is right in front of the flag
        while (note_idx < len(sheet)):
            curr_note = sheet[note_idx]

            if (curr_flag["box"][0] - curr_note["x"] < 10):
                # Only update the flag type if the note head type is a quarter note. Half note and whole note do not have flags
                if (curr_note["head_type"] == "quarter_note"):
                    curr_note["flag_type"] = curr_flag["symbol"].replace("_flag", "")
                break
            
            note_idx += 1
        
        flag_idx += 1

# Determine note's duration based on the beam symbol
note_idx = 0
beam_idx = 0

if (len(treble_zones["beam"]) > 0):
    while (beam_idx < len(treble_zones["beam"])):
        curr_beam = treble_zones["beam"][beam_idx]

        # Iterate through the notes and find the note that is right in front of the beam
        while (note_idx < len(sheet)):
            curr_note = sheet[note_idx]
            next_note = sheet[note_idx + 1] if note_idx < len(sheet) - 1 else None

            if (next_note is not None and curr_beam["box"][0] - curr_note["x"] < 10 and next_note["x"] - curr_beam["box"][2] < 10):
                # Only update the flag type if the note head type is a quarter note. Half note and whole note do not have beams
                if (curr_note["head_type"] == "quarter_note"):
                    curr_note["flag_type"] = curr_beam["symbol"].replace("_beam", "")
                    next_note["flag_type"] = curr_beam["symbol"].replace("_beam", "")
                break
            
            note_idx += 1
        
        beam_idx += 1

# --------------------------------- Determine Rest's Duration ---------------------------------
note_idx = 0
rest_idx = 0

# Iterate through the rests and push them into the correct order in the sheet
if (len(treble_zones["rest"]) > 0):
    while (note_idx < len(sheet)):
        curr_note = sheet[note_idx]
        rests_to_push = []

        while (rest_idx < len(treble_zones["rest"])):
            curr_rest = treble_zones["rest"][rest_idx]

            # In case the rests are in front of the note
            if (curr_rest["box"][0] < curr_note["x"]):
                rests_to_push.append({
                    "rest": curr_rest["symbol"].replace("_rest", ""),
                    "x": curr_rest["box"][2],
                })
                rest_idx += 1
            else:
                break
        
        # Push rests into the sheet
        sheet[note_idx:note_idx] = rests_to_push

        # Update the note index
        note_idx += len(rests_to_push) if len(rests_to_push) > 0 else 1
    
    # Push the remaining rests into the sheet
    sheet.extend(treble_zones["rest"][rest_idx:])

# Assume the time signature is 4/4 and time for each measure is 1 second
measure_playtime = 1
note_playtime = {
    "whole_note": 1,
    "half_note": 0.5,
    "quarter_note": 0.25,
    "eighth_note": 0.125,
    "sixteenth_note": 0.0625,
    "thirty_second_note": 0.03125,
}

from pydub import AudioSegment
from pydub.playback import play

note_sounds = {
    "A0": AudioSegment.from_file("sounds/A0.mp3"),
    "C1": AudioSegment.from_file("sounds/C1.mp3"),
    "Ds1": AudioSegment.from_file("sounds/Ds1.mp3"),
    "Fs1": AudioSegment.from_file("sounds/Fs1.mp3"),
    "A1": AudioSegment.from_file("sounds/A1.mp3"),
    "C2": AudioSegment.from_file("sounds/C2.mp3"),
    "Ds2": AudioSegment.from_file("sounds/Ds2.mp3"),
    "Fs2": AudioSegment.from_file("sounds/Fs2.mp3"),
    "A2": AudioSegment.from_file("sounds/A2.mp3"),
    "C3": AudioSegment.from_file("sounds/C3.mp3"),
    "Ds3": AudioSegment.from_file("sounds/Ds3.mp3"),
    "Fs3": AudioSegment.from_file("sounds/Fs3.mp3"),
    "A3": AudioSegment.from_file("sounds/A3.mp3"),
    "C4": AudioSegment.from_file("sounds/C4.mp3"),
    "Ds4": AudioSegment.from_file("sounds/Ds4.mp3"),
    "Fs4": AudioSegment.from_file("sounds/Fs4.mp3"),
    "A4": AudioSegment.from_file("sounds/A4.mp3"),
    "C5": AudioSegment.from_file("sounds/C5.mp3"),
    "Ds5": AudioSegment.from_file("sounds/Ds5.mp3"),
    "Fs5": AudioSegment.from_file("sounds/Fs5.mp3"),
    "A5": AudioSegment.from_file("sounds/A5.mp3"),
    "C6": AudioSegment.from_file("sounds/C6.mp3"),
    "Ds6": AudioSegment.from_file("sounds/Ds6.mp3"),
    "Fs6": AudioSegment.from_file("sounds/Fs6.mp3"),
    "A6": AudioSegment.from_file("sounds/A6.mp3"),
    "C7": AudioSegment.from_file("sounds/C7.mp3"),
    "Ds7": AudioSegment.from_file("sounds/Ds7.mp3"),
    "Fs7": AudioSegment.from_file("sounds/Fs7.mp3"),
    "A7": AudioSegment.from_file("sounds/A7.mp3"),
    "C8": AudioSegment.from_file("sounds/C8.mp3"),
}

def pitch_shift(sound, shift):
    return sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * (2 ** (shift / 12.0)))
    })