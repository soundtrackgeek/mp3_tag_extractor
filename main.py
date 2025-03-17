import os
import csv
import time
import datetime
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from tqdm import tqdm

# Define the directories to scan
directories = [
    r'H:\AdditionalMusic',
    r'H:\SinglesCompilations',
    r'H:\SonicMusic',
    r'H:\SonicScoresNewest',
    r'H:\Synthwave',
    r'I:\ModernMusic',
    r'I:\ModernSoundtracks',
    r'D:\_Backup\SonicPlexamp',
    r'D:\_Backup\SonicScoresPlexamp',
    r'G:\_BACKUP\PlexAMP',
    r'J:\SonicScores',
    r'D:\SonicScoresPlexampNew'
]

# Define CSV file settings
output_dir = 'tag_exports'
csv_base_name = 'audio_tags'
max_files_per_csv = 100000  # Number of files per CSV chunk

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Generate timestamp for this run
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# List to hold the tag data
tag_data = []
current_csv_count = 1
files_in_current_csv = 0

# Helper function to clean tag values
def clean_tag_value(value):
    # If the value is a list, join its elements with a comma
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    return str(value)

# Helper function to write CSV file
def write_csv_file(data, file_number):
    if not data:
        return
    
    # Get all unique tag keys
    all_keys = set()
    for tags in data:
        all_keys.update(tags.keys())

    # Ensure file_path is the first column
    all_keys_list = ['file_path'] + [key for key in all_keys if key != 'file_path']
    
    # Create filename with timestamp and chunk number
    output_csv = f"{csv_base_name}_{timestamp}_{file_number}.csv"
    output_path = os.path.join(output_dir, output_csv)
    
    # Write the tags to the CSV file
    print(f"\nWriting extracted tags to {output_path}...")
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys_list)
        writer.writeheader()
        for tags in data:
            writer.writerow(tags)
    
    print(f"✅ CSV file {output_path} created with {len(data)} entries and {len(all_keys)} unique tags")
    return output_path

# Count the total number of audio files first
print("Counting audio files across all directories...")
total_files = 0
audio_extensions = ('.mp3', '.flac')

for directory in directories:
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} does not exist. Skipping.")
        continue
        
    print(f"Scanning directory: {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(audio_extensions):
                total_files += 1
    
print(f"Found {total_files} audio files to process across all directories.")
time.sleep(1)  # Brief pause for better user experience

# Traverse the directories with progress bar
print("\nExtracting tags from audio files...")
processed_files = 0
errors = 0
csv_files_created = []

# Create overall progress bar
with tqdm(total=total_files, desc="Total Progress", unit="file") as progress_bar:
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        print(f"\nProcessing directory: {directory}")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(audio_extensions):
                    file_path = os.path.join(root, file)
                    tags = {}
                    try:
                        if file.lower().endswith('.mp3'):
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
                        
                        elif file.lower().endswith('.flac'):
                            audio = FLAC(file_path)
                            for tag in audio.keys():
                                tags[tag] = clean_tag_value(audio[tag])
                        
                        tags['file_path'] = file_path
                        tag_data.append(tags)
                        files_in_current_csv += 1
                        processed_files += 1
                        
                        # Check if we need to write a CSV file (reached max files or last file)
                        if files_in_current_csv >= max_files_per_csv:
                            output_path = write_csv_file(tag_data, current_csv_count)
                            csv_files_created.append(output_path)
                            # Reset for next batch
                            tag_data = []
                            current_csv_count += 1
                            files_in_current_csv = 0
                            
                    except Exception as e:
                        errors += 1
                        print(f"\nError processing {file_path}: {e}")
                    
                    progress_bar.update(1)

# Write any remaining data to a final CSV file
if tag_data:
    output_path = write_csv_file(tag_data, current_csv_count)
    csv_files_created.append(output_path)

# Summary report
print(f"\n✅ Task completed!")
print(f"  - Processed files: {processed_files}")
print(f"  - Errors encountered: {errors}")
print(f"  - CSV files created: {len(csv_files_created)}")
for csv_file in csv_files_created:
    print(f"    - {csv_file}")
print(f"\nCSV files are saved in the '{output_dir}' directory.")