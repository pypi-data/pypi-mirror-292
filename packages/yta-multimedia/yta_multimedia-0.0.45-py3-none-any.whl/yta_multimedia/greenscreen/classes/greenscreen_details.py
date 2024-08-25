from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails
from yta_general_utils.type_checker import is_google_drive_url
from yta_general_utils.file_downloader import download_file_from_google_drive, get_id_from_google_drive_url
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_general_utils.file_processor import copy_file, file_exists
from yta_multimedia.resources import get_resource
from yta_multimedia.greenscreen.enum.greenscreen_type import GreenscreenType
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

    def __init__(self, greenscreen_areas: List[GreenscreenAreaDetails] = [], filename_or_google_drive_url: str = None, type: GreenscreenType = GreenscreenType.IMAGE):
        # TODO: Implement checkings please
        self.greenscreen_areas = greenscreen_areas
        self.filename_or_google_drive_url = filename_or_google_drive_url
        self.type = type

    def get_filename(self):
        """
        This method will generate always a new temporary file
        that will be returned, even if the file already exists
        in the system, that will be the resource you need to
        generate the greenscreen.
        """
        folder = 'resources/greenscreens/moving/' + google_drive_id + '/'
        TMP_FILENAME = create_tmp_filename('tmp.mp4')
        if self.type == GreenscreenType.IMAGE:
            TMP_FILENAME = create_tmp_filename('tmp.png')

        if is_google_drive_url(self.filename_or_google_drive_url):
            # Check if it's been downloaded previously
            google_drive_id = get_id_from_google_drive_url(self.filename_or_google_drive_url)
            folder = 'resources/greenscreens/moving/' + google_drive_id + '/'
            if file_exists(folder + 'greenscreen.mp4'):
                TMP_FILENAME = folder + 'greenscreen.mp4'
            else:
                TMP_FILENAME = get_resource(self.filename_or_google_drive_url, TMP_FILENAME)
        else:
            copy_file(self.filename_or_google_drive_url, TMP_FILENAME)

        return TMP_FILENAME