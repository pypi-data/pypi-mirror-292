from moviepy.editor import ImageClip, vfx, AudioFileClip, CompositeVideoClip, ColorClip, clips_array
from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_multimedia.resources.video.effect.sound.drive_urls import SAD_MOMENT_GOOGLE_DRIVE_DOWNLOAD_URL
from enum import Enum

class MoviepyEffect(Enum):
    """
    Moviepy default effects made Enum to be used by this
    software easily. These are names that must be used
    as they are with the 'clip.fl(effect)' or similar.
    """
    BLACKWHITE = 'blackwhite'
    # TODO: See utils/video_utils.py in software project