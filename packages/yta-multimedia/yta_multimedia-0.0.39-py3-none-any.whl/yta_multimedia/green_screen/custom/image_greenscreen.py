from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from yta_general_utils.type_checker import variable_is_type
from moviepy.editor import ImageClip
from typing import Union
from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from yta_general_utils.file_processor import file_is_video_file
from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from PIL import Image, ImageDraw, ImageFont

class ImageGreenscreen:
    greenscreen: GreenscreenDetails = None

    def __init__(self, greenscreen: Union[GreenscreenDetails, str]):
        # TODO: if 'greenscreen' is str (and is file), we should
        # automatically scan the file to detect by code the 
        # greenscreen details (color and pixels)
        if variable_is_type(greenscreen, str):
            # TODO: We first detect and generate a GreenscreenDetails object
            # that we set in self.greenscreen
            raise Exception('Function not implemented yet: auto-detecting greenscreen details.')

        self.greenscreen = greenscreen

    def __process_elements_and_save(self, output_filename):
        """
        Processes the greenscreen by writing the title, description
        and any other available element, and stores it locally as
        'output_filename' once processed.
        """
        base = Image.open(self.greenscreen.google_drive_url)
        draw = ImageDraw.Draw(base)

        # TODO: I preserve this code for the future
        # # We need to write title if existing
        # if self.__title:
        #     title_position = (self.__title_x, self.__title_y)
        #     draw.text(title_position, self.__title, font = self.__title_font, fill = self.__title_color)

        # if self.__description:
        #     description_position = (self.__description_x, self.__description_y)
        #     draw.text(description_position, self.__description, font = self.__description_font, fill = self.__description_color)

        # TODO: Handle anything else here

        # We save the image
        base.save(output_filename, quality = 100)

    def from_image_to_image(self, image_filename: str, output_filename: str):
        """
        Receives an 'image_filename', places it into the greenscreen and generates
        another image that is stored locally as 'output_filename'.
        """
        if not image_filename:
            return None
        
        if not output_filename:
            return None
        
        # Put the image into the greenscreen
        imageclip = ImageClip(image_filename, duration = 1 / 60)
        final_clip = self.from_video_to_video(imageclip)

        # Generate the result image
        final_clip.save_frame(output_filename, t = 0)

    def from_image_to_video(self, image_filename: str, duration: float = 3.0, output_filename: Union[str, None] = None):
        """
        Receives an 'image_filename', places it into the greenscreen and generates
        a video of 'duration' seconds of duration that is returned. This method
        will store locally the video if 'output_filename' is provided.
        """
        if not image_filename:
            return None
        
        if not duration:
            return None
        
        if not output_filename:
            return None
        
        imageclip = ImageClip(image_filename, duration = duration)
        final_clip = self.from_video_to_video(imageclip)

        if output_filename:
            final_clip.write_videofile(output_filename)

        return final_clip
    
    def from_video_to_image(self):
        # TODO: Does this make sense? By now it is not implemented
        pass

    def from_video_to_video(self, video: Union[str, VideoFileClip, CompositeVideoClip, ImageClip], output_filename: Union[str, None] = None):
        """
        Inserts the provided 'video' in the greenscreen and returns the
        CompositeVideoClip that has been created. If 'output_filename' 
        provided, it will be written locally with that file name.

        The provided 'video' can be a filename or a moviepy video clip.

        TODO: Careful when video is longer than greenscreen
        """
        if not video:
            return None
        
        if variable_is_type(video, str):
            if not file_is_video_file(video):
                return None
            
            video = VideoFileClip(video)

        # TODO: Change this 
        # We could have different areas in which append 1 or more 
        # videos, so it would be handled different. By now I'm
        # considering we only have one
        
        # We download the file to be able to use it
        TMP_FILENAME = download_file_from_google_drive(self.greenscreen.google_drive_url, create_tmp_filename('tmp.png'))

        # We process greenscreen elements if needed
        # TODO: This will be done in the future (writing titles)
        #tmp_filename = create_tmp_filename('tmp_gs.png')
        #self.__process_elements_and_save(tmp_filename)

        # We choose the first greenscreen area to work with
        greenscreen_area = self.greenscreen.greenscreen_areas[0]

        # We work to maintain the proportion
        ulx = greenscreen_area.upper_left_pixel[0]
        uly = greenscreen_area.upper_left_pixel[1]
        lrx = greenscreen_area.lower_right_pixel[0]
        lry = greenscreen_area.lower_right_pixel[1]
        
        # TODO: Please, review this below
        gs_width = lrx - ulx
        gs_height = lry - uly
        aspect_ratio = gs_width / gs_height
        if aspect_ratio > (1920 / 1080):
            # We keep the width, but we calculate the height to keep 16/9 aspect ratio
            gs_height_for_16_9 = gs_width * (1080 / 1920)
            # Now we know the new height, so we only have to center the video on 'y' axis
            difference = gs_height_for_16_9 - gs_height
            # My video (16/9) will not fit the whole width
            uly -= difference / 2
            lry += difference / 2
        elif aspect_ratio < (1920 / 1080):
            # We keep the height, but we calculate the width to keep 16/9 aspect ratio
            gs_width_for_16_9 = gs_height * (1920 / 1080)
            # Now we know the new width, so we only have to center the video on 'x' axis
            difference = gs_width_for_16_9 - gs_width
            ulx -= difference / 2
            lrx += difference / 2
        # TODO: Are we sure that those coords are int and make a real 16/9 with int numbers?
        
        # Create the clip
        green_screen_clip = ImageClip(TMP_FILENAME, duration = video.duration).fx(vfx.mask_color, color = greenscreen_area.rgb_color, thr = 100, s = 5)
        width = lrx - ulx
        video = video.resize(width = width).set_position((ulx, uly))

        final_clip = CompositeVideoClip([video, green_screen_clip], size = green_screen_clip.size)

        if output_filename:
            final_clip.write_videofile(output_filename, fps = video.fps)

        return final_clip