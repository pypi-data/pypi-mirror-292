from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx, concatenate_videoclips
from PIL import ImageFont
from typing import Union
from yta_general_utils.type_checker import variable_is_type
from yta_general_utils.file_processor import file_is_video_file

class CustomGreenScreenVideo:
    """
    This class is used to build green screen videos by inserting videos in this green screen video.
    """
    def __init__(self, greenscreen: GreenscreenDetails):
        self.greenscreen = greenscreen

    # def __init__(self, filename: str, rgb_color: tuple, ulx: int, uly: int, drx: int, dry: int, title: str, title_font: ImageFont.FreeTypeFont, title_color: str, title_x: int, title_y: int, description: str, description_font: ImageFont.FreeTypeFont, description_color: str, description_x: int, description_y: int):
    #     # TODO: What about custom values ?
    #     self.__filename = filename
    #     self.ulx = ulx
    #     self.uly = uly
    #     self.drx = drx
    #     self.dry = dry
    #     self.rgb_color = rgb_color
    #     # By now these elements are not used
    #     self.__title = title
    #     self.__title_font = title_font
    #     self.__title_color = title_color
    #     self.__title_x = title_x
    #     self.__title_y = title_y
    #     self.__description = description
    #     self.__description_font = description_font
    #     self.__description_color = description_color
    #     self.__description_x = description_x
    #     self.__description_y = description_y

    def from_image_to_image(self):
        # TODO: Does this make sense? We are working with a video, so
        # trying to generate just a frame, an image, does make sense?
        # TODO: By the way, this is not working yet
        pass

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

        # TODO: We process greenscreen elements if needed

        # Create the clip
        green_screen_clip = VideoFileClip(self.__filename).fx(vfx.mask_color, color = self.rgb_color, thr = 100, s = 5)

        width = self.drx - self.ulx
        # If the provided clip is shorter than our green screen: easy, crop the green screen
        # If the provided clip is longer than our green screen: I use the green screen duration
        # and let the clip be original the rest of the time
        if green_screen_clip.duration > video.duration:
            green_screen_clip = green_screen_clip.set_duration(video.duration)
            # Clip will be displayed inside the green screen area
            video = video.resize(width = width).set_position((self.ulx, self.uly))
            video = CompositeVideoClip([video, green_screen_clip], size = green_screen_clip.size)
        elif video.duration > green_screen_clip.duration:
            # First subclip will be displayed inside the green screen area
            first_clip = video.subclip(0, green_screen_clip.duration).resize(width = width).set_position((self.ulx, self.uly))
            # Second clip will be as the original one
            second_clip = video.subclip(green_screen_clip.duration, video.duration)
            video = concatenate_videoclips([
                CompositeVideoClip([first_clip, green_screen_clip], size = green_screen_clip.size),
                second_clip
            ])
        else:
            video = CompositeVideoClip([video, green_screen_clip], size = green_screen_clip.size)

        if output_filename:
            video.write_videofile(output_filename, fps = video.fps)

        return video

    def __generate_green_screen(self):
        # This method exists to be overwritten by the titled 
        # greenscreen but could dissapear in the future
        pass