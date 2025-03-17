import os
import csv
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.flac import FLAC

# Define the directory to scan
directory = r'c:\_MP3TODO'

# Define the output CSV file
output_csv = 'current_tags.csv'

# List to hold the tag data
tag_data = []

# Helper function to clean tag values
def clean_tag_value(value):
    # If the value is a list, join its elements with a comma
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    return str(value)

# Traverse the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.mp3') or file.endswith('.flac'):
            file_path = os.path.join(root, file)
            tags = {}
            try:
                if file.endswith('.mp3'):
                    # Use both EasyID3 (for common tags) and ID3 (for all tags)
                    audio_easy = EasyID3(file_path)
                    audio_full = ID3(file_path)
                    
                    # Get common tags from EasyID3
                    for tag in audio_easy.keys():
                        tags[tag] = clean_tag_value(audio_easy[tag])
                    
                    # Get all tags from ID3 (includes ID3v2.3 and ID3v2.4 tags)
                    for frame_id, frame in audio_full.items():
                        # Frame IDs like "TXXX:customtag" are split into "TXXX" and "customtag"
                        if ":" in frame_id:
                            main_id, sub_id = frame_id.split(":", 1)
                            tag_name = f"{main_id}:{sub_id}"
                        else:
                            tag_name = frame_id
                        
                        # Convert the frame value to string
                        if hasattr(frame, 'text'):
                            tags[tag_name] = clean_tag_value(frame.text)
                        else:
                            tags[tag_name] = clean_tag_value(frame)
                
                elif file.endswith('.flac'):
                    audio = FLAC(file_path)
                    for tag in audio.keys():
                        tags[tag] = clean_tag_value(audio[tag])
                
                tags['file_path'] = file_path
                tag_data.append(tags)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Get all unique tag keys
all_keys = set()
for tags in tag_data:
    all_keys.update(tags.keys())

# Ensure file_path is the first column
all_keys_list = ['file_path'] + [key for key in all_keys if key != 'file_path']

# Write the tags to the CSV file
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=all_keys_list)
    writer.writeheader()
    for tags in tag_data:
        writer.writerow(tags)

print(f"Tags have been extracted and saved to {output_csv}")
print(f"Total number of unique tags found: {len(all_keys)}")