from yta_general_utils.tmp_processor import create_tmp_filename
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from PIL import Image, ImageDraw, ImageFont
from typing import Union
from yta_general_utils.type_checker import variable_is_type
from yta_general_utils.file_processor import file_is_video_file

class CustomGreenScreenImage:
    """
    This class is used to build custom green screen that has specific green screen positions and
    title and description font sizes.
    """
    def __init__(self, filename: str, rgb_color: tuple, ulx: int, uly: int, drx: int, dry: int, title: str, title_font: ImageFont.FreeTypeFont, title_color: str, title_x: int, title_y: int, description: str, description_font: ImageFont.FreeTypeFont, description_color: str, description_x: int, description_y: int):
        # TODO: What about custom values ?
        self.__filename = filename
        self.ulx = ulx
        self.uly = uly
        self.drx = drx
        self.dry = dry
        self.rgb_color = rgb_color
        self.__title = title
        self.__title_font = title_font
        self.__title_color = title_color
        self.__title_x = title_x
        self.__title_y = title_y
        self.__description = description
        self.__description_font = description_font
        self.__description_color = description_color
        self.__description_x = description_x
        self.__description_y = description_y

    def __process_elements_and_save(self, output_filename):
        """
        Processes the greenscreen by writing the title, description
        and any other available element, and stores it locally as
        'output_filename' once processed.
        """
        base = Image.open(self.__filename)
        draw = ImageDraw.Draw(base)

        # We need to write title if existing
        if self.__title:
            title_position = (self.__title_x, self.__title_y)
            draw.text(title_position, self.__title, font = self.__title_font, fill = self.__title_color)

        if self.__description:
            description_position = (self.__description_x, self.__description_y)
            draw.text(description_position, self.__description, font = self.__description_font, fill = self.__description_color)

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
        """
        if not video:
            return None
        
        if variable_is_type(video, str):
            if not file_is_video_file(video):
                return None
            
            video = VideoFileClip(video)

        # We process greenscreen elements if needed
        tmp_filename = create_tmp_filename('tmp_gs.png')
        self.__process_elements_and_save(tmp_filename)

        # Create the clip
        green_screen_clip = ImageClip(tmp_filename, duration = video.duration).fx(vfx.mask_color, color = self.rgb_color, thr = 100, s = 5)
        width = self.drx - self.ulx
        clip = video.resize(width = width).set_position((self.ulx, self.uly))

        final_clip = CompositeVideoClip([clip, green_screen_clip], size = green_screen_clip.size)

        if output_filename:
            final_clip.write_videofile(output_filename, fps = clip.fps)

        return final_clip
    
    def __generate_green_screen(self):
        # This method exists to be overwritten by the titled 
        # greenscreen but could dissapear in the future
        pass