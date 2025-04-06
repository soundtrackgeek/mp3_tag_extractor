import os
import csv
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, POPM  # Import ID3 and POPM for rating extraction

# Define the directory to scan
directory = r'c:\_MP3TODO'

# Define the output CSV file
output_csv = 'current_tags.csv'

# List to hold the tag data
tag_data = []

# Traverse the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.mp3') or file.endswith('.flac'):
            file_path = os.path.join(root, file)
            tags = {}
            try:
                if file.endswith('.mp3'):
                    audio = EasyID3(file_path)
                    # Load raw ID3 tags for POPM
                    raw_id3 = ID3(file_path)
                    for tag in audio.keys():
                        tags[tag] = audio[tag]
                    # Get POPM rating if it exists
                    if 'POPM:' in raw_id3:
                        popm_frame = raw_id3['POPM:']
                        tags['rating'] = popm_frame.rating
                elif file.endswith('.flac'):
                    audio = FLAC(file_path)
                    for tag in audio.tags:
                        key = tag[0].lower()
                        tags[key] = tag[1]
                    # Get RATING if it exists
                    if 'rating' in tags:
                        tags['rating'] = tags['rating']
                
                tags['file_path'] = file_path
                tag_data.append(tags)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Get all unique tag keys
all_keys = set()
for tags in tag_data:
    all_keys.update(tags.keys())

# Write the tags to the CSV file
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=list(all_keys))
    writer.writeheader()
    for tags in tag_data:
        writer.writerow(tags)

print(f"Tags have been extracted and saved to {output_csv}")