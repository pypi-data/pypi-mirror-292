from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails
from yta_general_utils.type_checker import is_google_drive_url
from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_general_utils.file_processor import copy_file
from typing import List

class GreenscreenDetails:
    """
    This class represents a greenscreen image or video
    resource, its information and the greenscreen areas
    that it contains.

    @param
        **greenscreen_areas**
        An array of _GreenscreenAreaDetails_ objects that
        represent the different greenscreen that there are
        inside this greenscreen resource.

    @param
        **filename_or_google_drive_url**
        The resource file filename or Google Drive url.
    """
    greenscreen_areas = []
    filename_or_google_drive_url = None
    type = None

    def __init__(self, greenscreen_areas: List[GreenscreenAreaDetails] = [], filename_or_google_drive_url: str = None, type = 'image'):
        # TODO: Implement checkings please
        self.greenscreen_areas = greenscreen_areas
        self.filename_or_google_drive_url = filename_or_google_drive_url
        self.type = type

    def get_filename(self):
        """
        This method will download the file from Google Drive or 
        will return the filename if it is already downloaded.

        This method will generate always a new temporary file
        that will be returned, even if the file already exists
        in the system.
        """
        TMP_FILENAME = create_tmp_filename('tmp.mp4')
        if self.type == 'image':
            TMP_FILENAME = create_tmp_filename('tmp.png')

        if is_google_drive_url(self.filename_or_google_drive_url):
            TMP_FILENAME = download_file_from_google_drive(self.filename_or_google_drive_url, TMP_FILENAME)
        else:
            copy_file(self.filename_or_google_drive_url, TMP_FILENAME)

        return TMP_FILENAME