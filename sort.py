import os
from PIL import Image, UnidentifiedImageError, ExifTags
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import threading
import time

"""
Things to consider:

1. Screen shots are not dealt with properly. They are sent to the unknown filder.
2. Videos are not sorted yet.

"""

image_src_dir = Path(r"C:\Users\herma\Desktop\Copy")
parent_dir = Path(image_src_dir)

image_formats = list(Image.registered_extensions().values())

def image_metadata_extractor(image: str):
    """ Verify file is an image and extract the dates. Convert the str date object to an datetime object """
    
    # Convert TAGS to human readable names        
    image_exifdata = image.getexif()
    
    if image_exifdata:
        decoded_exif = {TAGS.get(tag, tag): value for tag, value in image_exifdata.items()}        
        date_taken = decoded_exif.get("DateTime", decoded_exif.get("DateTimeOriginal"))

    if date_taken:
        return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")

def video_metadata_extractor():
    pass

def handle_unknown_files(file_path, file):
    """ Handle files with unknown dates or formats """
    unknown_dir = os.path.join(parent_dir, "Unknown files")
    
    # Skip makedir if dir exist
    os.makedirs(unknown_dir, exist_ok=True)
    file_to_be_moved_path = os.path.join(unknown_dir, file)
    
    if not os.path.exists(file_to_be_moved_path):
        shutil.copy(file_path, unknown_dir)

def move_file_to_year_folder(image_date_obj, file_path, file):
    """ Create folders and move the file to suitable folder """
    if isinstance(image_date_obj, datetime):
        sorted_image_folders = os.path.join(parent_dir, str(image_date_obj.year))

        # Skip makedir if dir exist
        os.makedirs(sorted_image_folders, exist_ok=True)
        file_to_be_moved_path = os.path.join(sorted_image_folders, file)
        
        if not os.path.exists(file_to_be_moved_path):
            # shutil.copy(file_path, sorted_image_folders)
            pass

def main():
    """ Walk through all the dirs and subdirs and sort the files """
    number_of_files: int = 0
    number_of_files_transferred: int = 0
    
    for dirpath, _, filenames in os.walk(image_src_dir, topdown=True):
        for file in filenames:
            try:
                file_path: str = os.path.join(dirpath, file)
                number_of_files += 1
                
                with Image.open(file_path) as image:
                    if image.format in image_formats:
                        image_date_obj: str = image_metadata_extractor(image)
                        move_file_to_year_folder(image_date_obj, file_path, file)
                
                number_of_files_transferred += 1
            except UnidentifiedImageError:
                handle_unknown_files(file_path, file)
            except Exception:
                handle_unknown_files(file_path, file)
            except Exception as e:
                return str(e)
    
    print(f"Number of files identified: {number_of_files}")
    print(f"Number of files transferred: {number_of_files_transferred}")

if __name__ == "__main__":
    start_time = time.perf_counter()
    # t1 = threading.Thread(target=main)
    # t2 = threading.Thread(target=main)
    # t3 = threading.Thread(target=main)
    # t4 = threading.Thread(target=main)
    
    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    
    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
    
    for i in range(16):
        ti = threading.Thread(target=main)
    
    end_time = time.perf_counter()
    
    print(f"Total execution time: {end_time - start_time} seconds")