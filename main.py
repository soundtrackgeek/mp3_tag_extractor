import os
import csv
import time
import datetime
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.flac import FLAC

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

# Traverse the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.mp3') or file.endswith('.flac'):
            file_path = os.path.join(root, file)
            tags = {}
            try:
                if file.endswith('.mp3'):
                    audio = EasyID3(file_path)
                elif file.endswith('.flac'):
                    audio = FLAC(file_path)
                for tag in audio.keys():
                    tags[tag] = audio[tag]
                tags['file_path'] = file_path
                tag_data.append(tags)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Get all unique tag keys
all_keys = set()
for tags in tag_data:
    all_keys.update(tags.keys())

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