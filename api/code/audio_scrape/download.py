import requests
import os

notes_list = ['A0', 'C1', 'Ds1', 'Fs1', 'A1', 'C2', 'Ds2', 'Fs2', 
              'A2', 'C3', 'Ds3', 'Fs3', 'A3', 'C4', 'Ds4', 'Fs4', 
              'A4', 'C5', 'Ds5', 'Fs5', 'A5', 'C6', 'Ds6', 'Fs6', 
              'A6', 'C7']
domain = "https://virtualpiano.net/wp-content/themes/generatepress_child/js-dev/samples/auditorium-piano/"
output_dir = "original_audio/"

for note in notes_list:
    # Construct the URL for the audio file
    url = os.path.join(domain, f"{note}.mp3")
    
    # Send a GET request to download the audio file
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the audio file to the specified directory
        base_note = note[:-1]
        octave = int(note[-1])
        new_octave = octave + 1
        new_filename = f"{base_note}{new_octave}"

        with open(os.path.join(output_dir, f"{new_filename}.mp3"), 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {new_filename}.mp3")
    else:
        print(f"Failed to download: {note}.mp3 - Status code: {response.status_code}")
