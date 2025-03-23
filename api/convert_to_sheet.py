import json

CLASS_NAMES = ['barline', 'bass_clef', 'decrescendo', 'dotted_half_note', 'dotted_quarter_note', 
               'eight_beam', 'eight_flag', 'eight_rest', 'flat', 'half_note', 'natural', 'quarter_note', 
               'quarter_rest', 'sharp', 'sixteenth_beam', 'sixteenth_flag', 'sixteenth_rest', 'thirty_second_beam', 
               'treble_clef', 'whole_half_rest', 'whole_note']

SCALE = {
    "0": "C major",
    "1b": "F major",
    "2b": "Bb major",
    "3b": "Eb major",
    "4b": "Ab major",
    "5b": "Db major",
    "6b": "Gb major",
    "7b": "Cb major",
    "1s": "G major",
    "2s": "D major",
    "3s": "A major",
    "4s": "E major",
    "5s": "B major",
    "6s": "F# major",
    "7s": "C# major"
}

NOTES_ON_SCALE = {
    "0": ["C", "D", "E", "F", "G", "A", "B"],
    "1b": ["C", "D", "E", "F", "G", "A", "As"],
    "2b": ["C", "D", "Ds", "F", "G", "A", "As"],
    "3b": ["C", "D", "Ds", "F", "G", "Gs", "As"],
    "4b": ["C", "Cs", "Ds", "F", "G", "Gs", "As"],
    "5b": ["C", "Cs", "Ds", "F", "Fs", "Gs", "As"],
    "6b": ["B", "Cs", "Ds", "F", "Fs", "Gs", "As"],
    "7b": ["B", "Cs", "Ds", "E", "Fs", "Gs", "As"],
    "1s": ["C", "D", "E", "Fs", "G", "A", "B"],
    "2s": ["Cs", "D", "E", "Fs", "G", "A", "B"],
    "3s": ["Cs", "D", "E", "Fs", "Gs", "A", "B"],
    "4s": ["Cs", "Ds", "E", "Fs", "Gs", "A", "B"],
    "5s": ["Cs", "Ds", "E", "Fs", "Gs", "As", "B"],
    "6s": ["Cs", "Ds", "F", "Fs", "Gs", "As", "B"],
    "7s": ["Cs", "Ds", "F", "Fs", "Gs", "As", "Bs"]
}

with open("json/data.json", "r") as f:
    full_data = json.load(f)

data = full_data[5]

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

# Extend 3 more staff lines for bass clef above
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
    "barline": [],
}
bass_zones = {
    "note": [],
    "flag": [],
    "beam": [],
    "rest": [],
    "sharp": [],
    "flat": [],
    "natural": [],
    "clef": [],
    "barline": [],
}
space_max_diff = line_space

# Iterate through the boxes and put them into the correct zones
for symbol_index in range(len(boxes)):
    for box_index in range(len(boxes[symbol_index])):
        box = boxes[symbol_index][box_index]
        symbol = CLASS_NAMES[symbol_index]

        # If the symbol is barline, put it into both treble and bass zones
        if (symbol == "barline"):
            treble_zones["barline"].append({"symbol": symbol, "box": box})
            bass_zones["barline"].append({"symbol": symbol, "box": box})
            continue
        
        # Check if the coordinates are within treble zone
        # if box[3] >= treble_staff_lines["C6"] and box[1] <= treble_staff_lines["A3"]:
        if (box[3] - treble_staff_lines["E6"] >= treble_staff_lines["E6"] - box[1]) and (treble_staff_lines["F3"] - box[1] >= box[3] - treble_staff_lines["F3"]):
            for key in treble_zones:
                if (symbol.count(key) > 0):
                    treble_zones[key].append({"symbol": symbol, "box": box})
                    break
                    
        # Check if the coordinates are within bass zone
        # if box[3] >= bass_staff_lines["E4"] and box[1] <= bass_staff_lines["C2"]:
        elif (box[3] - bass_staff_lines["G4"] >= bass_staff_lines["G4"] - box[1]) and (bass_staff_lines["A1"] - box[1] >= box[3] - bass_staff_lines["A1"]):
            for key in bass_zones:
                if (symbol.count(key) > 0):
                    bass_zones[key].append({"symbol": symbol, "box": box})
                    break

# Sort the symbols based on their x-coordinate
for key in treble_zones:
    treble_zones[key] = sorted(treble_zones[key], key=lambda coord: (coord["box"][0], coord["box"][1]))

for key in bass_zones:
    bass_zones[key] = sorted(bass_zones[key], key=lambda coord: (coord["box"][0], coord["box"][1]))

# Barlines are used for both treble and bass zones
bass_zones["barline"] = treble_zones["barline"]

print(len(treble_zones["note"]), len(treble_zones["flag"]), len(treble_zones["beam"]), len(treble_zones["rest"]), len(treble_zones["sharp"]), len(treble_zones["flat"]), len(treble_zones["natural"]), len(treble_zones["clef"]), len(treble_zones["barline"]))
print(len(bass_zones["note"]), len(bass_zones["flag"]), len(bass_zones["beam"]), len(bass_zones["rest"]), len(bass_zones["sharp"]), len(bass_zones["flat"]), len(bass_zones["natural"]), len(bass_zones["clef"]), len(bass_zones["barline"]))
# --------------------------------- Determine Scale ---------------------------------
# Determine the scale
scale = ""

sharp_idx = 1

if (len(treble_zones["sharp"]) > 0):
    # If there is a sharp symbol near the clef, determine the scale based on the sharp symbol
    if (treble_zones["sharp"][0]["box"][0] - treble_zones["clef"][0]["box"][2] < 20):
        prev_x = treble_zones["sharp"][0]["box"][2]

        while (sharp_idx < len(treble_zones["sharp"])):
            curr_x = treble_zones["sharp"][sharp_idx]["box"][0]

            # Compare the starting x-coordinate of the current box with the ending x-coordinate of the previous box
            if (abs(curr_x - prev_x) < 10):
                scale = f"{str(sharp_idx + 1)}s"
            else:
                break

            # Update the previous x-coordinate by the current ending x-coordinate
            prev_x = treble_zones["sharp"][sharp_idx]["box"][2]
            sharp_idx += 1

flat_idx = 1

if (len(treble_zones["flat"]) > 0):
    # If there is a flat symbol near the clef, determine the scale based on the sharp symbol
    if (treble_zones["flat"][0]["box"][0] - treble_zones["clef"][0]["box"][2] < 20):
        prev_x = treble_zones["flat"][0]["box"][2]

        while (flat_idx < len(treble_zones["flat"])):
            curr_x = treble_zones["flat"][flat_idx]["box"][0]

            # Compare the starting x-coordinate of the current box with the ending x-coordinate of the previous box
            if (abs(curr_x - prev_x) < 10):
                scale = f"{str(flat_idx + 1)}b"
            else:
                break
            
            # Update the previous x-coordinate by the current ending x-coordinate
            prev_x = treble_zones["flat"][flat_idx]["box"][2]
            flat_idx += 1

# --------------------------------- Determine Note's Pitch ---------------------------------
def shift_note(original_note, scale):
    note_idx = 0

    # Find the index of the orignal note in C major scale
    for i in range(len(NOTES_ON_SCALE["0"])):
        if (NOTES_ON_SCALE["0"][i] == original_note[0]):
            note_idx = i
            break
    
    # Shift the note based on the scale
    shifted_note = NOTES_ON_SCALE[scale][note_idx] + original_note[1]
    
    return shifted_note

# Determine note's pitch
def get_note_pitch(p1, p2):
    letters = ["C", "D", "E", "F", "G", "A", "B"]
    note = ""

    if (letters.index(p1[0]) == 6):
        note = f"{letters[0]}{int(p1[1]) + 1}"
    elif (letters.index(p2[0]) == 0):
        note = f"{letters[6]}{int(p2[1]) - 1}"
    else:
        note = f"{letters[letters.index(p1[0]) + 1]}{p1[1]}"
    
    return note

sheet = {
    "treble_zone": [],
    "bass_zone": [],
}
treble_staff_lines_list = list(treble_staff_lines.items())
bass_staff_lines_list = list(bass_staff_lines.items())

def generate_symbol_data(zone_name, zones, staff_lines_list, spare_staff_lines_list, switch_staff_coords=[]):
    working_lines_list = staff_lines_list
    switch_index = 0

    note_idx = 0

    # Add dummy note at the end of the list to ensure the last note is processed
    zones["note"].append({"box": [10000, 10000, 1000, 1000]})

    if (len(zones["note"]) > 0):
        prev_coord = zones["note"][0]["box"]
        notes = []

        while (note_idx < len(zones["note"])):
            curr_coord = zones["note"][note_idx]["box"]

            # Check if the switch position is reached
            if (switch_index < len(switch_staff_coords) and curr_coord[0] >= switch_staff_coords[switch_index]):
                working_lines_list = spare_staff_lines_list if switch_index % 2 == 0 else staff_lines_list
                switch_index += 1

            # Collect notes occurring in the same column. The second condition is used to handle
            # the case where the note is in the same column but doesn't have enough space to stand. So, it must shift to the right 
            if (abs(curr_coord[0] - prev_coord[0]) < line_space or curr_coord[0] <= prev_coord[2]):
                notes.append(zones["note"][note_idx])
            else:
                # Sort notes based on their y-coordinate
                notes = sorted(notes, key=lambda x: x["box"][1])
                notes_data = {
                    "notes": [],
                    "head_type": "",
                    "flag_type": "",
                    "x1": 0,
                    "x2": 0,
                }

                # Determine the pitch of each note
                for note in notes:
                    # Update the nearest and farthest x-coordinate
                    notes_data["x1"] = min(notes_data["x1"], note["box"][0]) if notes_data["x1"] != 0 else note["box"][0]
                    notes_data["x2"] = max(notes_data["x2"], note["box"][2]) if notes_data["x2"] != 0 else note["box"][2]

                    # Update the head type
                    notes_data["head_type"] = note["symbol"]

                    # Find the y-coordinate of top and bottom of the note
                    y1 = note["box"][1]
                    y2 = note["box"][3]
                    note_pitch = ""

                    # Iterate through the staff lines and find the correct line the note is laying on
                    for line_idx in range(len(working_lines_list)):
                        curr_line_y = working_lines_list[line_idx][1]
                        next_line_y = working_lines_list[line_idx + 1][1] if line_idx < len(working_lines_list) - 1 else None

                        if (y1 <= curr_line_y):
                            # If the box covers two lines, the note is in staff space
                            if (next_line_y is not None and y2 >= next_line_y):
                                note_pitch = get_note_pitch(working_lines_list[line_idx + 1][0], working_lines_list[line_idx][0])
                                # print("Note in staff space:", note_pitch)
                            # If the box covers only one line, the note is on the staff line
                            else:
                                note_pitch = working_lines_list[line_idx][0]
                                # print("Note on staff line:", note_pitch)
                            
                            # print("y1:", y1, "y2:", y2, note_pitch, end="\n\n")
                            note_pitch = shift_note(note_pitch, scale)
                            break
                    
                    notes_data["notes"].append(note_pitch)
                
                # Append the notes to the sheet
                sheet[zone_name].append(notes_data)

                # Reset notes
                notes = [zones["note"][note_idx]]

            prev_coord = curr_coord
            note_idx += 1

    # Remove the dummy note
    zones["note"].pop()

# Sometimes, the treble or bass zone is not actually themself. Therefore, we need to check their clef symbol to determine the correct zone
# Create modified treble staff lines list by changing the key to bass staff while keeping the lines coordinates
treble_staff_lines_list_modified = [(bass_staff_lines_list[i][0], treble_staff_lines_list[i][1]) for i in range(len(treble_staff_lines_list))]
bass_staff_lines_list_modified = [(treble_staff_lines_list[i][0], bass_staff_lines_list[i][1]) for i in range(len(bass_staff_lines_list))]

treble_cleves_coords = [treble_zones["clef"][i]["box"][0] for i in range(1, len(treble_zones["clef"]))]
bass_cleves_coords = [bass_zones["clef"][i]["box"][0] for i in range(1, len(bass_zones["clef"]))]

if (treble_zones["clef"][0]["symbol"] == "bass_clef"):
    generate_symbol_data("treble_zone", treble_zones, treble_staff_lines_list_modified, treble_staff_lines_list, treble_cleves_coords)
else:
    generate_symbol_data("treble_zone", treble_zones, treble_staff_lines_list, treble_staff_lines_list_modified, treble_cleves_coords)

# Similar to bass zone
if (bass_zones["clef"][0]["symbol"] == "treble_clef"):
    generate_symbol_data("bass_zone", bass_zones, bass_staff_lines_list_modified, bass_staff_lines_list, bass_cleves_coords)
else:
    generate_symbol_data("bass_zone", bass_zones, bass_staff_lines_list, bass_staff_lines_list_modified, bass_cleves_coords)

# --------------------------------- Determine Note's Duration ---------------------------------
# Determine note's duration by checking the flag symbol
def generate_note_duration(zone_name, zone):
    note_idx = 0
    flag_idx = 0

    # Combine the flag and beam symbols into one list
    flag_beam_list = zone["flag"] + zone["beam"]
    flag_beam_list = sorted(flag_beam_list, key=lambda x: x["box"][0])
    
    if (len(flag_beam_list) > 0):
        while (flag_idx < len(flag_beam_list)):
            curr_flag = flag_beam_list[flag_idx]

            # Iterate through the notes and find the note that is right in front of the flag
            while (note_idx < len(sheet[zone_name])):
                curr_note = sheet[zone_name][note_idx]

                # Do not update if the flag type is already set
                if (len(curr_note["flag_type"]) != 0):
                    # print("Skip", curr_note)
                    note_idx += 1
                    continue
                
                # If the current symbol is flag, update one note
                if (curr_flag["symbol"].count("flag") > 0):
                    
                    # Check if the flag's box is in acceptable range of the note's x-coordinate
                    if (abs(curr_flag["box"][0] - curr_note["x1"]) <= line_space or abs(curr_flag["box"][0] - curr_note["x2"]) <= line_space):
                        # Only update the flag type if the note head type is a quarter note. Half note and whole note do not have flags
                        if (curr_note["head_type"] == "quarter_note"):
                            curr_note["flag_type"] = curr_flag["symbol"].replace("_flag", "")
                            # print("Set flags for", curr_note["notes"])
                        break
                
                # If the current symbol is beam, update two notes
                elif (curr_flag["symbol"].count("beam") > 0):

                    # Add two variables for each beam to check for availablity of the beginning and the end of the beam
                    curr_flag["start_available"] = True
                    curr_flag["end_available"] = True
                
                    if (flag_idx - 1 >= 0):
                        prev_flag = flag_beam_list[flag_idx - 1]
                        if (prev_flag["symbol"].count("beam") > 0 and curr_flag["box"][0] <= prev_flag["box"][2]):
                            curr_flag["start_available"] = prev_flag["end_available"]
                            
                    # Variables to handle 3 cases of the note's position in the beam
                    curr_beam = curr_flag
                    next_note = sheet[zone_name][note_idx + 1] if note_idx < len(sheet[zone_name]) - 1 else None
                    start_note_set = False
                    end_note_set = False

                    # If there is a note presenting at the beginning of the beam
                    if (abs(curr_beam["box"][0] - curr_note["x1"]) <= line_space or abs(curr_beam["box"][0] - curr_note["x2"]) <= line_space):
                        if (curr_flag["start_available"]):
                            start_note_set = True
                            curr_flag["start_available"] = False

                            if (curr_note["head_type"] == "quarter_note"):
                                curr_note["flag_type"] = curr_beam["symbol"].replace("_beam", "")
                                # print("Current note at the beginning")
                                # print("Set beam for", curr_note)
                    
                    # If there is a note presenting at the end of the beam
                    # If there is no note at the beginning, the note at the end must be current note
                    if (not start_note_set and (abs(curr_beam["box"][2] - curr_note["x1"]) <= line_space or abs(curr_beam["box"][2] - curr_note["x2"]) <= line_space)):
                        if (curr_flag["end_available"]):
                            end_note_set = True
                            curr_flag["end_available"] = False

                            if (curr_note["head_type"] == "quarter_note"):
                                curr_note["flag_type"] = curr_beam["symbol"].replace("_beam", "")
                                # print("Current note at the end")
                                # print("Set beam for", curr_note)
                    
                    # If there is a note presenting at the beginning of the beam, the note at the end must be the next note
                    if (start_note_set and not end_note_set and next_note is not None and (abs(curr_beam["box"][2] - next_note["x1"]) <= line_space or abs(curr_beam["box"][2] - next_note["x2"]) <= line_space)):
                        if (curr_flag["end_available"]):
                            end_note_set = True
                            curr_flag["end_available"] = False

                            if (next_note["head_type"] == "quarter_note"):
                                next_note["flag_type"] = curr_beam["symbol"].replace("_beam", "")
                    #             print("Next note at the end")
                    #             print("Set beam for", next_note)
                    
                    # print("\n")
                    if (start_note_set or end_note_set):
                        break

                note_idx += 1
            
            flag_idx += 1
        

generate_note_duration("treble_zone", treble_zones)
print("---------------------------------")
generate_note_duration("bass_zone", bass_zones)

# --------------------------------- Determine Rest's Duration ---------------------------------
def generate_rest_duration(zone_name, zone):
    note_idx = 0
    rest_idx = 0

    # Iterate through the rests and push them into the correct order in the sheet
    if (len(zone["rest"]) > 0):
        while (note_idx < len(sheet[zone_name])):
            curr_note = sheet[zone_name][note_idx]
            rests_to_push = []

            while (rest_idx < len(zone["rest"])):
                curr_rest = zone["rest"][rest_idx]

                # In case the rests are in front of the note
                if (curr_rest["box"][0] < curr_note["x1"]):
                    rests_to_push.append({
                        "rest": curr_rest["symbol"].replace("_rest", ""),
                        "x1": curr_rest["box"][0],
                        "x2": curr_rest["box"][2],
                    })
                    rest_idx += 1
                else:
                    break
            
            # Push rests into the sheet
            sheet[zone_name][note_idx:note_idx] = rests_to_push

            # Update the note index
            note_idx += len(rests_to_push) if len(rests_to_push) > 0 else 1
        
        # Push the remaining rests into the sheet
        sheet[zone_name].extend(list(map(lambda symbol: {"rest": symbol["symbol"].replace("_rest", ""), "x1": symbol["box"][0], "x2": symbol["box"][2]}, zone["rest"][rest_idx:])))

generate_rest_duration("treble_zone", treble_zones)
generate_rest_duration("bass_zone", bass_zones)

# --------------------------------- Determine barline position ---------------------------------
def generate_barline_position(zone_name, zone):
    note_idx = 0
    barline_idx = 0

    if (len(zone["barline"]) > 0):
        while (note_idx < len(sheet[zone_name])):
            curr_symbol = sheet[zone_name][note_idx]
            barlines_to_push = []

            while (barline_idx < len(zone["barline"])):
                curr_barline = zone["barline"][barline_idx]

                if (curr_barline["box"][0] < curr_symbol["x1"]):
                    barlines_to_push.append({
                        "barline": curr_barline["symbol"],
                        "x1": curr_barline["box"][0],
                        "x2": curr_barline["box"][2],
                    })
                    barline_idx += 1
                else:
                    break
            
            sheet[zone_name][note_idx:note_idx] = barlines_to_push

            note_idx += len(barlines_to_push) if len(barlines_to_push) > 0 else 1
        
        sheet[zone_name].extend(list(map(lambda symbol: {"barline": symbol["symbol"], "x1": symbol["box"][0], "x2": symbol["box"][2]}, zone["barline"][barline_idx:])))

generate_barline_position("treble_zone", treble_zones)
generate_barline_position("bass_zone", bass_zones)

# ---------------------------- Verify the duration of each measure ---------------------------------

# Assume the time signature is 4/4 and time for each measure is 2 second
measure_playtime = 2000
note_playtime = {
    "whole": 1 * measure_playtime,
    "half": 0.5 * measure_playtime,
    "quarter": 0.25 * measure_playtime,
    "eight": 0.125 * measure_playtime,
    "sixteenth": 0.0625 * measure_playtime,
    "thirty_second": 0.03125 * measure_playtime,
}

music_sheet = {
    "treble_zone": [],
    "bass_zone": [],
}

def verify_measure_duration(zone_name, zone):
    measure_duration = 0
    measure_idx = 0
    first_barline = True
    current_measure = []
    
    # Segments to handle whole_half_rest
    segment_before = 0

    for i in range(len(zone)):
        symbol = zone[i]
        should_append = False

        if (symbol.get("notes")):
            # If the note doesn't have a flag, the duration is the same as the head type
            if (len(symbol["flag_type"]) == 0):
                measure_duration += note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")]
            else:
                measure_duration += note_playtime[symbol["flag_type"]]

            # Check if the note is dotted
            if (symbol["head_type"].count("dotted") > 0):
                if (len(symbol["flag_type"]) == 0):
                    measure_duration += note_playtime[symbol["head_type"].replace("dotted_", "").replace("_note", "")] / 2
                else:
                    measure_duration += note_playtime[symbol["flag_type"]] / 2

        elif (symbol.get("rest")):
            # If the rest is whole_half_rest, save the segment before the rest and calculate the duration later on
            if (symbol["rest"] == "whole_half"):
                segment_before = measure_duration
                measure_duration = 0
            else:
                measure_duration += note_playtime[symbol["rest"]]

        elif (symbol.get("barline")):
            # Skip the first barline
            if (first_barline):
                first_barline = False
                continue

            # Determine the duration for whole_half_rest
            if (segment_before + measure_duration < measure_playtime):
                whole_half_rest_duration = measure_playtime - (segment_before + measure_duration)

                # Find the index of the whole_half_rest symbol in current measure
                whole_half_rest_index = next((j for j, d in enumerate(current_measure) if d.get("rest") == "whole_half"), -1)

                if (whole_half_rest_duration == note_playtime["whole"]):
                    current_measure[whole_half_rest_index]["rest"] = "whole"
                elif (whole_half_rest_duration == note_playtime["half"]):
                    current_measure[whole_half_rest_index]["rest"] = "half"
                
                # Update the measure duration
                measure_duration = segment_before + whole_half_rest_duration

            if (measure_duration != measure_playtime):
                print("Measure", measure_idx + 1, "duration is not correct")
                print("Expected:", measure_playtime, "Actual:", measure_duration)
            else:
                print("Measure", measure_idx + 1, "duration is correct")

            measure_duration = 0
            measure_idx += 1
            should_append = True
        
        # Append the symbol without x1 and x2 to the current measure
        current_measure.append({key: value for key, value in symbol.items() if key not in ("x1", "x2")})

        # Append the current measure to the music sheet
        if (should_append):
            music_sheet[zone_name].append(current_measure)
            current_measure = []

verify_measure_duration("treble_zone", sheet["treble_zone"])
verify_measure_duration("bass_zone", sheet["bass_zone"])

print(json.dumps(music_sheet, indent=4))