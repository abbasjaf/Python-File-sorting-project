from PIL import Image, UnidentifiedImageError, ExifTags
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import time
import mimetypes
import magic

parent_dir = Path(r"C:\Users\herma\Desktop\Copy")
video_mime = magic.Magic(mime=True, keep_going=True)
video_mime_types = [
    "video/mp4",         # MP4 (MPEG-4 Part 14)
    "video/x-msvideo",   # AVI (Microsoft Audio Video Interleave)
    "video/x-matroska",  # MKV (Matroska Video)
    "video/quicktime",   # MOV (Apple QuickTime)
    "video/x-ms-wmv",    # WMV (Windows Media Video)
    "video/webm",        # WebM (Web Media)
    "video/ogg",         # OGV (Ogg Video)
    "video/mpeg",        # MPEG (MPEG-1, MPEG-2)
    "video/3gpp",        # 3GP (3rd Generation Partnership Project)
    "video/3gpp2",       # 3G2 (3rd Generation Partnership Project 2)
    "video/x-flv",       # FLV (Flash Video)
    "video/x-f4v",       # F4V (Flash MP4)
    "video/x-ms-asf",    # ASF (Advanced Systems Format)
    "video/h264",        # H.264 Video
    "video/h265",        # H.265 (HEVC)
    "video/x-theora",    # Theora Video
    "video/x-divx",      # DivX Video
    "video/x-xvid",      # Xvid Video
    "application/vnd.rn-realmedia", # RM (RealMedia)
]
image_formats = list(map(str.lower, Image.registered_extensions().values()))
number_of_files_transferred: int = 0
print(image_formats)

def image_metadata_extractor(file_source, image):
    """ Verify file is an image and extract the dates. Convert the str date object to an datetime object """
    
    image_exifdata = image.getexif()
    
    if image_exifdata:
        decoded_exif = {TAGS.get(tag, tag): value for tag, value in image_exifdata.items()}        
        date_taken = decoded_exif.get("DateTime", decoded_exif.get("DateTimeOriginal"))
        
        return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
    else:
        # For e.g screen shots that does not have exif data
        mod_time = file_source.stat().st_mtime
        date_taken = datetime.fromtimestamp(mod_time)
        
        if date_taken:
            return date_taken


def video_metadata_extractor(file_source):
    mod_time = file_source.stat().st_mtime
    date_taken = datetime.fromtimestamp(mod_time)
    
    return date_taken

def handle_unknown_files(file, file_source):
    """ Handle files with unknown dates or formats """
    # Unknown file folder
    unknown_dir = parent_dir / "Unknown files"
    
    # Skip makedir if dir exist
    unknown_dir.mkdir(exist_ok=True)
    file_destination = unknown_dir / file.name
    
    if file_destination.exists():
        global number_of_files_transferred
        number_of_files_transferred += 1
    
    if not file_destination.exists():
        shutil.copy2(file_source, unknown_dir)

def move_file_to_year_folder(file_date_obj, file, file_source):
    """ Create folders and move the file to suitable folder """
    if isinstance(file_date_obj, datetime):
        # Create a dir based on file ctime
        sorted_image_folders = parent_dir / str(file_date_obj.year)

        # Skip makedir if dir exist
        sorted_image_folders.mkdir(exist_ok=True)
        # Path to filed that is being moved
        file_destination = sorted_image_folders / file.name
        
        if file_destination.exists():
            global number_of_files_transferred
            number_of_files_transferred += 1
        
        if not file_destination.exists():
            shutil.copy2(file_source, sorted_image_folders)

def main():
    """ Walk through all the dirs and subdirs and sort the files """
    number_of_files: int = 0
    
    for file in parent_dir.rglob("*"):
        if file.is_file():
            file_source = Path(file)
            number_of_files += 1
            
            # try:
            #     # Check if file type is an image
            #     if mimetypes.guess_file_type(file_source)[0].split("/")[1] in image_formats:
            #         with Image.open(file_source) as image:
            #             file_date_obj: datetime = image_metadata_extractor(file_source, image)
            #             move_file_to_year_folder(file_date_obj, file_source, file)
            #     # check for video files
            #     elif mimetypes.guess_file_type(file_source)[0] in video_mime_types:
            #         file_date_obj = video_metadata_extractor(file_source)
            #         move_file_to_year_folder(file_date_obj, file, file_source)
            #     else:
            #         handle_unknown_files(file_source, file)
            # except Exception:
            #     handle_unknown_files(file, file_source)
    
    print(f"Number of files identified: {number_of_files}")
    print(f"Number of files transferred: {number_of_files_transferred}")

if __name__ == "__main__":
    start_time = time.perf_counter()
    
    main()
    
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    
    print(f"Total execution time: {total_time:2f} seconds")