import json

CLASS_NAMES = [
    "barline", "bass_clef", "decrescendo", "dotted_note", "eight_beam",
    "eight_flag", "eight_rest", "flat", "half_note", "natural",
    "quarter_note", "quarter_rest", "sharp", "sixteenth_beam", "sixteenth_flag",
    "sixteenth_rest", "thirty_second_beam", "treble_clef", "whole_half_rest", "whole_note"
]

SCALE = {
    "Empty": "C major",
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

staff_lines = data["staff_lines"]
treble_staff_lines = {}
bass_staff_lines = {}

line_space = staff_lines[1][1] - staff_lines[0][1]

# Add basic 5 staff lines for treble clef
treble_staff_lines["F5"] = staff_lines[0]
treble_staff_lines["D5"] = staff_lines[1]
treble_staff_lines["B4"] = staff_lines[2]
treble_staff_lines["G4"] = staff_lines[3]
treble_staff_lines["E4"] = staff_lines[4]

# Extend 2 more staff lines for treble clef above and below
treble_staff_lines["A5"] = [staff_lines[0][0], staff_lines[0][1] - line_space, staff_lines[0][2], staff_lines[0][3]]
treble_staff_lines["C6"] = [staff_lines[0][0], staff_lines[0][1] - line_space*2, staff_lines[0][2], staff_lines[0][3]]
treble_staff_lines["C4"] = [staff_lines[4][0], staff_lines[4][1] + line_space, staff_lines[4][2], staff_lines[4][3]]
treble_staff_lines["A3"] = [staff_lines[4][0], staff_lines[4][1] + line_space*2, staff_lines[4][2], staff_lines[4][3]]

# Add basic 5 staff lines for bass clef
bass_staff_lines["A3"] = staff_lines[5]
bass_staff_lines["F3"] = staff_lines[6]
bass_staff_lines["D3"] = staff_lines[7]
bass_staff_lines["B2"] = staff_lines[8]
bass_staff_lines["G2"] = staff_lines[9]

# Extend 2 more staff lines for bass clef above and below
bass_staff_lines["C4"] = [staff_lines[5][0], staff_lines[5][1] - line_space, staff_lines[5][2], staff_lines[5][3]]
bass_staff_lines["E4"] = [staff_lines[5][0], staff_lines[5][1] - line_space*2, staff_lines[5][2], staff_lines[5][3]]
bass_staff_lines["E2"] = [staff_lines[9][0], staff_lines[9][1] + line_space, staff_lines[9][2], staff_lines[9][3]]
bass_staff_lines["C2"] = [staff_lines[9][0], staff_lines[9][1] + line_space*2, staff_lines[9][2], staff_lines[9][3]]

# Extract boxes
boxes = data["boxes"]

# Put symbol's bounding box into the correct order (from left to right, top to bottom)
treble_zones = []
bass_zones = []
space_max_diff = line_space

for symbol_index in range(len(boxes)):
    for box_index in range(len(boxes[symbol_index])):
        box = boxes[symbol_index][box_index]
        
        # Check if the coordinates are within treble zone
        if box[1] > treble_staff_lines["C6"][1] - space_max_diff and box[1] < treble_staff_lines["A3"][1] + space_max_diff:
            treble_zones.append({"symbol": CLASS_NAMES[symbol_index], "box": box})
        
        # Check if the coordinates are within bass zone
        if box[1] > bass_staff_lines["E4"][1] - space_max_diff and box[1] < bass_staff_lines["C2"][1] + space_max_diff:
            bass_zones.append({"symbol": CLASS_NAMES[symbol_index], "box": box})

# Sort treble and bass zones based on x-coordinate (compare y-coordinate if x-coordinate is the same)
treble_zones = sorted(treble_zones, lambda coord : (coord["box"][0], coord["box"][1]))
bass_zones = sorted(bass_zones, lambda coord : (coord["box"][0], coord["box"][1]))

# Start converting to sheet
sheet = []

# Start with treble zone
prev_symbol = ""
curr_symbol = ""

scale = ""
is_treble_zone = False
measure = []

# Variables for determining scale
start_determine_scale = False
current_scale = ""

# Variables for determining note
start_determining_note = False
current_note = []

for i in range(len(treble_zones)):
    curr_symbol = treble_zones[i]["symbol"]

    # Set the beginning of a measure
    if (curr_symbol == "barline"):
        if (len(measure) > 0):
            sheet.append(measure)
            measure = []
    
    # Check if the current zone is treble zone
    elif (curr_symbol == "treble_clef"):
        is_treble_zone = True
    
    # Determine the scale
    elif (prev_symbol == "treble_clef" and (curr_symbol == "sharp" or curr_symbol == "flat")):
        start_determine_scale = True
    
    # Determine the note
    elif (curr_symbol.endswith("note")):
        start_determining_note = True
        
    if (start_determine_scale):
        if (curr_symbol == "sharp" or curr_symbol == "flat"):
            current_scale += curr_symbol + " "
        else:
            scale = SCALE[f"{current_scale.count('flat')}b" if current_scale.count('flat') > 0 else f"{current_scale.count('sharp')}#"]
            start_determine_scale = False
            current_scale = ""
    
    
    prev_symbol = curr_symbol
