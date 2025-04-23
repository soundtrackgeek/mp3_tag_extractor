import os
import sys
from mutagen.easyid3 import EasyID3, EasyID3KeyError
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError

def update_track_numbers(album_path):
    """
    Updates track numbers for MP3 and FLAC files within a given album directory.

    Args:
        album_path (str): The path to the album directory.
    """
    print(f"Processing album: {album_path}")
    try:
        # List all files and filter for audio files
        files = [f for f in os.listdir(album_path) if os.path.isfile(os.path.join(album_path, f))]
        audio_files = sorted([f for f in files if f.lower().endswith(('.mp3', '.flac'))])

        if not audio_files:
            print("  No audio files found.")
            return

        total_tracks = len(audio_files)
        print(f"  Found {total_tracks} tracks.")

        for i, filename in enumerate(audio_files):
            track_number = i + 1
            new_track_tag = f"{track_number}/{total_tracks}"
            file_path = os.path.join(album_path, filename)

            try:
                if filename.lower().endswith('.mp3'):
                    try:
                        audio = EasyID3(file_path)
                    except ID3NoHeaderError:
                        print(f"  No ID3 header found for {filename}, creating one.")
                        audio = EasyID3() # Create tags if none exist
                    audio['tracknumber'] = new_track_tag
                    audio.save(file_path)
                elif filename.lower().endswith('.flac'):
                    audio = FLAC(file_path)
                    audio['tracknumber'] = new_track_tag # FLAC tags are often lists, but assignment handles it
                    audio.save()

                print(f"  Updated {filename} to track {new_track_tag}")

            except Exception as e:
                print(f"  Error updating {filename}: {e}")

    except Exception as e:
        print(f"Error processing directory {album_path}: {e}")

def main(root_directory):
    """
    Main function to walk through the root directory and process each album subdirectory.

    Args:
        root_directory (str): The root directory containing album folders.
    """
    if not os.path.isdir(root_directory):
        print(f"Error: Root directory '{root_directory}' not found.")
        sys.exit(1)

    print(f"Starting scan in: {root_directory}")
    for item in os.listdir(root_directory):
        item_path = os.path.join(root_directory, item)
        if os.path.isdir(item_path):
            update_track_numbers(item_path)

    print("Processing complete.")

if __name__ == "__main__":
    # Define the root directory containing album folders
    # IMPORTANT: Make sure this path is correct for your system
    target_directory = r'm:\_LPTOFIX'
    main(target_directory) 