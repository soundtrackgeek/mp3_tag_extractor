import os
import csv
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from tqdm import tqdm
import time

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

# Count the total number of audio files first
print(f"Scanning directory: {directory}")
print("Counting files to process...")

total_files = 0
audio_extensions = ('.mp3', '.flac')
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(audio_extensions):
            total_files += 1

print(f"Found {total_files} audio files to process.")
time.sleep(0.5)  # Brief pause for better user experience

# Traverse the directory with progress bar
print("\nExtracting tags from audio files...")
processed_files = 0
errors = 0

with tqdm(total=total_files, desc="Processing", unit="file") as progress_bar:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(audio_extensions):
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
                    processed_files += 1
                except Exception as e:
                    errors += 1
                    print(f"\nError processing {file_path}: {e}")
                
                progress_bar.update(1)

# Get all unique tag keys
all_keys = set()
for tags in tag_data:
    all_keys.update(tags.keys())

# Ensure file_path is the first column
all_keys_list = ['file_path'] + [key for key in all_keys if key != 'file_path']

# Write the tags to the CSV file
print(f"\nWriting extracted tags to {output_csv}...")
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=all_keys_list)
    writer.writeheader()
    for tags in tag_data:
        writer.writerow(tags)

print(f"\n✅ Task completed!")
print(f"  - Processed files: {processed_files}")
print(f"  - Errors encountered: {errors}")
print(f"  - Unique tags found: {len(all_keys)}")
print(f"  - Results saved to: {output_csv}")