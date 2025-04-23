# mp3_tag_extractor

This repository contains Python scripts for managing audio file metadata.

## `lptocd.py`

This script scans a specified root directory for subdirectories (presumably albums). For each album directory, it finds all `.mp3` and `.flac` files, sorts them alphabetically, and updates their `tracknumber` metadata tag to reflect their position in the sequence (e.g., "1/12", "2/12").

### Usage

1.  **Install dependencies:** `pip install -r requirements.txt`
2.  **Modify the `target_directory`:** Change the `target_directory` variable within the script (`lptocd.py`) to point to the root folder containing your album subdirectories.
3.  **Run the script:** `python lptocd.py`

**Note:** The script modifies files in place. Ensure you have backups if needed.
