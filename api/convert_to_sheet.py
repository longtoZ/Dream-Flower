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

print(json.dumps(treble_staff_lines, indent=4))
print(json.dumps(bass_staff_lines, indent=4))

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
    print("p1:", p1, "p2:", p2)
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
            }

            # Determine the pitch of each note
            for note in notes:
                y1 = note["box"][1]
                y2 = note["box"][3]
                note_pitch = ""

                for line_idx in range(len(treble_staff_lines_list)):
                    curr_line_y = treble_staff_lines_list[line_idx][1]
                    next_line_y = treble_staff_lines_list[line_idx + 1][1] if line_idx < len(treble_staff_lines_list) - 1 else None

                    if (y1 < curr_line_y):
                        # If the box covers two lines, the note is in staff space
                        if (next_line_y is not None and y2 > next_line_y):
                            note_pitch = get_note_pitch(treble_staff_lines_list[line_idx + 1][0], treble_staff_lines_list[line_idx][0])
                            print("Note in staff space:", note_pitch)
                        # If the box covers only one line, the note is on the staff line
                        else:
                            note_pitch = treble_staff_lines_list[line_idx][0]
                            print("Note on staff line:", note_pitch)
                        
                        print("y1:", y1, "y2:", y2, note_pitch, end="\n\n")

                        break
                
                notes_data["notes"].append(note_pitch)
            
            # Append the notes to the sheet
            sheet.append(notes_data)

            # Reset notes
            notes = [treble_zones["note"][note_idx]]

        prev_x = curr_x
        note_idx += 1

print("Sheet:", sheet)