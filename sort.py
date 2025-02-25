from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from datetime import datetime
from pathlib import Path
import shutil
import time
import mimetypes
from concurrent.futures import ThreadPoolExecutor

parent_dir = Path(r"C:\Users\herma\Desktop\Copy")

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
mutagen_supported_audio_formats = [
    "mp3",   # MP3 (MPEG Audio)
    "flac",  # FLAC (Free Lossless Audio Codec)
    "ogg",   # OGG Vorbis
    "opus",  # Opus (Next-generation OGG)
    "mp4",   # MP4 (AAC, ALAC, MPEG-4)
    "m4a",   # M4A (Apple AAC/ALAC)
    "m4b",   # M4B (Audiobooks, MPEG-4)
    "m4p",   # M4P (Protected AAC)
    "asf",   # Advanced Systems Format (ASF) (WMA, WMV)
    "wma",   # Windows Media Audio
    "wav",   # WAV (RIFF)
    "aiff",  # AIFF (Apple)
    "ape",   # APE (Monkey’s Audio)
    "wv",    # WavPack
    "dsf",   # DSF (DSD Stream File)
    "dff",   # DFF (DSD Interchange File)
    "spx",   # Speex
    "tta",   # True Audio
    "ac3",   # AC3 (Dolby Digital)
    "mpc",   # Musepack
    "au",    # AU (Sun Audio)
]

image_formats = list(map(str.lower, Image.registered_extensions().values()))
image_formats.append("jpg")
video_formats = [item.split("/")[1] for item in video_mime_types]
audio_mime_types = ["audio/" + item for item in mutagen_supported_audio_formats]

number_of_files_transferred: int = 0
number_of_unknown_files: int = 0


def image_metadata_extractor(source_file, image):
    """ Verify file is an image and extract the dates. Convert the str date object to an datetime object """
    
    image_exifdata = image.getexif()
    
    if image_exifdata:
        decoded_exif = {TAGS.get(tag, tag): value for tag, value in image_exifdata.items()}        
        date_taken = decoded_exif.get("DateTime", decoded_exif.get("DateTimeOriginal"))
        
        if date_taken:
            return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
    else:
        # For e.g screen shots that does not have exif data
        mod_time = source_file.stat().st_mtime
        date_taken = datetime.fromtimestamp(mod_time)
        
        if date_taken:
            return date_taken

def video_metadata_extractor(source_file):
    mod_time = source_file.stat().st_mtime
    date_taken = datetime.fromtimestamp(mod_time)
    
    return date_taken

def audio_metadata_extractor(source_file):
    mod_time = source_file.stat().st_mtime
    date_taken = datetime.fromtimestamp(mod_time)
    
    return date_taken

def handle_unknown_files(file, source_file):
    """ Handle files with unknown dates or formats """
    # Unknown file folder
    unknown_dir = parent_dir / "Unknown files"
    
    # Skip makedir if dir exist
    unknown_dir.mkdir(exist_ok=True)
    file_destination = unknown_dir / file.name
    
    if not file_destination.exists():
        shutil.copy2(source_file, unknown_dir)
        global number_of_unknown_files
        number_of_unknown_files += 1

def move_file_to_year_folder(file, source_file, file_date_obj):
    """ Create folders and move the file to suitable folder """
    if isinstance(file_date_obj, datetime):
        # Create a dir based on file ctime
        sorted_image_folders = parent_dir / str(file_date_obj.year)

        # Skip makedir if dir exist
        sorted_image_folders.mkdir(exist_ok=True)
        # Path to filed that is being moved
        file_destination = sorted_image_folders / file.name
        
        if not file_destination.exists():
            shutil.copy2(source_file, sorted_image_folders)
            global number_of_files_transferred
            number_of_files_transferred += 1

def process_files(file):
    """ Based on the MIME-type, call different sorting functions """
    
    source_file = Path(file)                        
    file_mime_type, _ = mimetypes.guess_type(source_file)
    
    try:
        # Check if file type is an image
        if file_mime_type and file_mime_type.startswith("image/"):
            with Image.open(source_file) as image:
                file_date_obj: datetime = image_metadata_extractor(source_file, image)
                move_file_to_year_folder(file, source_file, file_date_obj)
        # check for video files
        elif file_mime_type in video_mime_types:
            file_date_obj = video_metadata_extractor(source_file)
            move_file_to_year_folder(file, source_file, file_date_obj)
        elif file_mime_type in audio_mime_types:
            file_date_obj = audio_metadata_extractor(source_file)
            move_file_to_year_folder(file, source_file, file_date_obj)
        else:
            handle_unknown_files(file, source_file)
    except UnidentifiedImageError as e:
        handle_unknown_files(file, source_file)
    except Exception as e:
        handle_unknown_files(file, source_file)
    
def main():
    files = list(parent_dir.rglob("*"))
    number_of_files = len(files)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_files, files)
    
    print(f"Number of files identified: {number_of_files}")
    print(f"Number of unknown files: {number_of_unknown_files}")
    print(f"Number of files transferred: {number_of_files_transferred}")
        

if __name__ == "__main__":
    start_time = time.perf_counter()
    
    main()
    
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    
    print(f"Total execution time: {total_time:2f} seconds")