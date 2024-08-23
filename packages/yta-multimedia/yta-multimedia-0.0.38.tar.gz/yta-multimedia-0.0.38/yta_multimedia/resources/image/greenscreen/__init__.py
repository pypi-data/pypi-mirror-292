"""
    In this file we register all video greenscreens we have
    available in our system. These greenscreens have their
    own resource uploaded to Google Drive and we have also
    detected the greenscreen color and the pixels in which
    the area is and we define those parameters below.

    This file is for letting these greenscreens to be used
    by the VideoGreenscreen class to inject some pictures
    or videos on it and enhance the video experience.

    This should be replaced by a database in which we store
    this information and keep it updated, not directly in
    code, but for now it is our system.
"""
from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails

YOUTUBE_VIDEO_IMAGE_GREENSCREEN = GreenscreenDetails(
    greenscreen_areas = [
        GreenscreenAreaDetails(
            rgb_color = (0, 249, 12),
            upper_left_pixel = (28, 110),
            lower_right_pixel = (1282, 817),
            frames = None
        )
    ],
    filename_or_google_drive_url = 'https://drive.google.com/file/d/1WQVnXY1mrw-quVXOqTBJm8x9scEO_JNz/view?usp=sharing',
    type = 'image'
)