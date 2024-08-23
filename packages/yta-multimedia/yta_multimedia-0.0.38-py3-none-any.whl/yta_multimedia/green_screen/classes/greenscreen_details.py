from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails
from typing import List

class GreenscreenDetails:
    """
    This class represents a greenscreen image or video
    resource, its information and the greenscreen areas
    that it contains.
    """
    greenscreen_areas = []
    google_drive_url = None

    def __init__(self, greenscreen_areas: List[GreenscreenAreaDetails] = [], google_drive_url: str = None):
        # TODO: Implement checkings please
        self.greenscreen_areas = greenscreen_areas
        self.google_drive_url = google_drive_url