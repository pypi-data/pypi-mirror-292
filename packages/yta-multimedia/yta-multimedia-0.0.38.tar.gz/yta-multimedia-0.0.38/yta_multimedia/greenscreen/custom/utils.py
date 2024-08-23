from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_multimedia.greenscreen.utils import get_greenscreen_area_details
from yta_general_utils.type_checker import is_google_drive_url
from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails
from yta_multimedia.video.frames import extract_frame_from_video
from yta_multimedia.greenscreen.enum.greenscreen_type import GreenscreenType

def get_greenscreen_details(greenscreen_filename_or_google_drive_url: str, type: GreenscreenType):
    """
    Method to obtain greenscreen area and details that must be
    used by ImageGreenscreen and VideoGreenscreen to automatically
    detect greenscreens in their resources.
    """
    if not greenscreen_filename_or_google_drive_url:
        return None
    
    # TODO: Check that 'type' is GreenscreenType type
    
    if is_google_drive_url(greenscreen):
        TMP_FILENAME = create_tmp_filename('tmp_gs_autodetect.png')

        if type == GreenscreenType.IMAGE:
            TMP_FILENAME = download_file_from_google_drive(greenscreen, TMP_FILENAME)
        else:  # GreenscreenType.VIDEO
            TMP_VIDEO_FILENAME = download_file_from_google_drive(greenscreen, TMP_VIDEO_FILENAME)
            # Video so we will apply the method to the first frame
            extract_frame_from_video(TMP_VIDEO_FILENAME, 0, TMP_FILENAME)

    # TODO: Autodetect and instantiate a Greenscreen
    details = get_greenscreen_area_details(TMP_FILENAME)

    if not details['rgb_color']:
        raise Exception('No automatic greenscreen detected in "' + greenscreen + '". Aborting.')

    greenscreen = GreenscreenDetails(
        greenscreen_areas = [
            GreenscreenAreaDetails(
                rgb_color = details['rgb_color'],
                upper_left_pixel = details['upper_left_pixel'],
                lower_right_pixel = details['lower_right_pixel'],
                frames = None # TODO: Implement a way of handling frames
            )
        ],
        filename_or_google_drive_url = TMP_FILENAME,
        type = type
    )

    return greenscreen