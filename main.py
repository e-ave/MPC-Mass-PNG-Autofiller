import io
import re
import sys
import os
import shutil
from PIL import Image
import zlib
from typing import Tuple
import hashlib

# Borrowed from https://github.com/marshvin/Image_hash_spoofing
def modify_png_get_hash(image_bytes, current_attempt):
    """Modify PNG metadata and return new bytes and hash"""
    # Create a copy of the image bytes
    new_bytes = bytearray(image_bytes)

    # Find the IEND chunk (last chunk in PNG)
    iend_index = new_bytes.rfind(b'IEND')
    if iend_index == -1:
        raise ValueError("Invalid PNG: No IEND chunk found")

    # Insert custom metadata chunk before IEND
    # Using 'prVt' as custom chunk type (private ancillary chunk)
    chunk_type = b'prVt'
    chunk_data = str(current_attempt).encode('utf-8')
    chunk_length = len(chunk_data)

    # Calculate CRC for the chunk
    crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF

    # Construct the complete chunk
    new_chunk = (
            chunk_length.to_bytes(4, 'big') +
            chunk_type +
            chunk_data +
            crc.to_bytes(4, 'big')
    )

    # Insert the new chunk before IEND
    new_bytes[iend_index:iend_index] = new_chunk

    # Calculate SHA-512 hash of modified image
    return bytes(new_bytes), hashlib.sha512(new_bytes).hexdigest()

def format_id(number, side):
    return f"{number:04d}_{side}.png"


def dupe_cards(source_dir, side, start_id, end_id, increment, max_id):
    # Loop over source files
    for base_index in range(start_id, end_id + 1):
        base_filename = format_id(base_index, side)
        base_path = os.path.join(source_dir, base_filename)

        if not os.path.isfile(base_path):
            print(f"Skipping missing file: {base_path} - {base_filename}")
            continue

        # Generate and copy to new files
        multiplier = 1
        while True:
            new_index = base_index + multiplier * increment
            if new_index > max_id:
                break

            new_filename = format_id(new_index, side)
            new_path = os.path.join(source_dir, new_filename)

            # shutil.copy(base_path, new_path)
            # Copying doesnt work because MGC does not upload images with the same hash

            # Read original image and convert to PNG in memory
            with Image.open(base_path) as img:
                # Convert to PNG format in memory
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                original_bytes = img_byte_arr.getvalue()

            # Insert a custom metadata block into the PNG containing the card index
            modified_bytes, hash_result = modify_png_get_hash(original_bytes, new_index)

            # Output the new file
            with open(new_path, 'wb') as f:
                f.write(modified_bytes)
            print(f"Copied {base_filename} -> {new_filename}")

            multiplier += 1


def find_min_max_ids(directory, side="front"):
    ids = []

    pattern1 = re.compile(rf"(\d+)_front\.png")
    pattern2 = re.compile(rf"(\d+)_back\.png")
    for path in os.listdir(directory):
        filename = os.path.basename(path)
        match1 = pattern1.match(filename)
        match2 = pattern2.match(filename)
        if match1:
            ids.append(int(match1.group(1)))
        if match2:
            ids.append(int(match2.group(1)))
    if not ids:
        raise ValueError("No matching files found")

    return min(ids), max(ids)

def duplicate_all(directory, max_card_id):
    start_id, end_id = find_min_max_ids(directory)
    duplicate_range(directory, start_id, end_id, max_card_id)

def duplicate_range(directory, start_id, end_id, max_card_id):
    number_of_cards = end_id - start_id + 1
    dupe_cards(directory, "front", start_id, end_id, number_of_cards, max_card_id)
    dupe_cards(directory, "back", start_id, end_id, number_of_cards, max_card_id)

def main():
    directory = "./cards/"
    max_card_id = 234
    dupe_all_cards = True
    if dupe_all_cards:
        duplicate_all(directory, max_card_id)
    else:
        # Define your own range of cards
        # This will duplicate cards 0000_front/0000_back through 0011_front/0011_back
        duplicate_range(directory=directory, start_id=0, end_id=11, max_card_id=max_card_id)

if __name__ == "__main__":
    main()

