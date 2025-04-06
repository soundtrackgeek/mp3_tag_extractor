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
    r'z:\\_LPTOFIX'
]

# Define CSV file settings
output_dir = 'tag_exports'
csv_base_name = 'audio_tags'
max_files_per_csv = 100000  # Number of files per CSV chunk

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Generate timestamp for this run
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# Function to write data to a CSV file
def write_csv_file(data, keys, file_index, base_name, ts, out_dir):
    output_filename = f"{base_name}_{ts}_{file_index}.csv"
    output_path = os.path.join(out_dir, output_filename)
    sorted_keys = sorted(list(keys)) # Ensure consistent column order
    if 'file_path' in sorted_keys: # Move file_path to the end
        sorted_keys.remove('file_path')
        sorted_keys.append('file_path')

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"Data written to {output_path}")
    return output_path

# Initialize statistics and tracking variables
tag_data = []
all_keys = set(['file_path']) # Start with file_path as a mandatory key
processed_files = 0
errors = 0
current_csv_count = 1
csv_files_created = []
start_time = time.time()

print(f"Starting scan at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

# Traverse the directories
for directory in directories:
    print(f"Scanning directory: {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.flac')):
                processed_files += 1
                file_path = os.path.join(root, file)
                tags = {'file_path': file_path} # Initialize with file_path
                try:
                    if file.endswith('.mp3'):
                        audio = EasyID3(file_path)
                        # EasyID3 keys are standard, add them directly
                        for key, value in audio.items():
                            tags[key] = value[0] # EasyID3 returns lists
                            all_keys.add(key)
                    elif file.endswith('.flac'):
                        audio = FLAC(file_path)
                        # FLAC keys might be standard or custom, add them
                        for key, value in audio.items():
                            # Handle potential list values from FLAC tags
                            tags[key] = value[0] if isinstance(value, list) else value
                            all_keys.add(key)

                    tag_data.append(tags)

                    # Write to CSV in chunks
                    if len(tag_data) >= max_files_per_csv:
                        output_path = write_csv_file(tag_data, all_keys, current_csv_count, csv_base_name, timestamp, output_dir)
                        csv_files_created.append(output_path)
                        tag_data = [] # Reset data list for the next chunk
                        current_csv_count += 1
                        # Re-evaluate all keys for the next chunk if needed, though less efficient
                        # all_keys = set(['file_path'])
                        # for tags_dict in tag_data: all_keys.update(tags_dict.keys())

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    errors += 1

# Write any remaining data to a final CSV file
if tag_data:
    # Ensure all keys from the final batch are included before writing
    # final_keys = set(['file_path'])
    # for tags_dict in tag_data: final_keys.update(tags_dict.keys())
    # all_keys.update(final_keys) # Combine keys from all chunks
    output_path = write_csv_file(tag_data, all_keys, current_csv_count, csv_base_name, timestamp, output_dir)
    csv_files_created.append(output_path)

end_time = time.time()
duration = end_time - start_time

# Summary report
print(f"\n✅ Task completed in {duration:.2f} seconds!")
print(f"  - Processed files: {processed_files}")
print(f"  - Errors encountered: {errors}")
print(f"  - CSV files created: {len(csv_files_created)}")
for csv_file in csv_files_created:
    print(f"    - {csv_file}")
print(f"\nCSV files are saved in the '{output_dir}' directory.")