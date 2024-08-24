from objects.customgreenscreenimage import CustomGreenScreenImage
from yta_image_edition_module.green_screen import get_green_screen_position
from os import getenv as os_getenv

class TVScreenOne:
    __TOUSE_ABSOLUTE_PATH = os_getenv('TOUSE_ABSOLUTE_PATH')
    __GREEN_SCREENS_FOLDER = __TOUSE_ABSOLUTE_PATH + 'green_screens/'

    def __init__(self):
        filename = self.__GREEN_SCREENS_FOLDER + '001_screen.png'
        #rgb_color = (0, 249, 12)
        #self.ulx = 388
        #self.uly = 44
        #self.drx = 1538
        #self.dry = 698

        green_screen_info = get_green_screen_position(filename)
        rgb_color = green_screen_info['rgb_color']
        self.ulx = green_screen_info['ulx']
        self.uly = green_screen_info['uly']
        self.drx = green_screen_info['drx']
        self.dry = green_screen_info['dry']

        gs_width = self.drx - self.ulx
        gs_height = self.dry - self.uly
        aspect_ratio = gs_width / gs_height
        if aspect_ratio > (1920 / 1080):
            # We keep the width, but we calculate the height to keep 16/9 aspect ratio
            gs_height_for_16_9 = gs_width * (1080 / 1920)
            # Now we know the new height, so we only have to center the video on 'y' axis
            difference = gs_height_for_16_9 - gs_height
            # My video (16/9) will not fit the whole width
            self.uly -= difference / 2
            self.dry += difference / 2
        elif aspect_ratio < (1920 / 1080):
            # We keep the height, but we calculate the width to keep 16/9 aspect ratio
            gs_width_for_16_9 = gs_height * (1920 / 1080)
            # Now we know the new width, so we only have to center the video on 'x' axis
            difference = gs_width_for_16_9 - gs_width
            self.ulx -= difference / 2
            self.drx += difference / 2
        # TODO: Are we sure that those coords are int and make a real 16/9 with int numbers?

        self.cgsi = CustomGreenScreenImage(filename, rgb_color, self.ulx, self.uly, self.drx, self.dry, None, None, None, None, None, None, None, None, None, None)

    def save(self, output_filename):
        self.cgsi.save(output_filename)

    def insert_video(self, video_filename, output_filename):
        self.cgsi.insert_video(video_filename, output_filename)

    def from_clip(self, clip):
        """
        Receives a 'clip' and generates a new one that is the provided one inside of the
        green screen.
        """
        return self.cgsi.from_clip(clip)

    def insert_image(self, image_filename, output_filename):
        self.cgsi.insert_image(image_filename, output_filename)