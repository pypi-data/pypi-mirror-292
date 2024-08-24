from yta_multimedia.video.generation.manim.constants import SCENE_HEIGHT
from yta_multimedia.video.generation.manim.utils.dimensions import manim_height_to_height, manim_width_to_width, width_to_manim_width, height_to_manim_height
from yta_multimedia.video.generation.manim.utils.config import write_manim_config_file
from yta_general_utils.file_processor import get_project_abspath, get_filename, rename_file

from manim import *
from subprocess import run

"""
Docummentation here: 
    https://docs.manim.community/en/stable/

Useful links:
- https://www.youtube.com/watch?v=KHGoFDB-raE (+1h of using SVGs and drawing and animating)
- https://www.youtube.com/watch?v=bCsk6hnMO5w   (Mobjects and animations)
            -> https://github.com/mphammer/Manim-Mobjects-and-Animations/blob/main/animations.py
- https://www.youtube.com/watch?v=5qj3b7DY5oA   (Mobjects and animations)
            -> https://github.com/mphammer/Manim-Mobjects-and-Animations/blob/main/mobjects.py

Command to throw:
    manim PYTHON_FILE.py CLASS_NAME -pqm
"""

"""
Interesting:
    - https://docs.manim.community/en/stable/examples.html (some examples)
    - https://medium.com/@andresberejnoi/data-visualization-bar-chart-animations-with-manim-andres-berejnoi-75ece91a2da4 (bar graphs)
"""

# TODO: Maybe this one needs to be moved to a text handler
def fitting_text(text, width_to_fit: float = 1920, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor = None, font_size: float = DEFAULT_FONT_SIZE, line_spacing: float = -1, font: str = '', slant: str = NORMAL, weight: str = NORMAL, t2c: dict[str, str] = None, t2f: dict[str, str] = None, t2g: dict[str, tuple] = None, t2s: dict[str, str] = None, t2w: dict[str, str] = None, gradient: tuple = None, tab_width: int = 4, warn_missing_font: bool = True, height: float = None, width: float = None, should_center: bool = True, disable_ligatures: bool = False, **kwargs):
    width_to_fit = width_to_manim_width(width_to_fit)

    txt_width_fitted = Text(text, fill_opacity, stroke_width, color, font_size, line_spacing, font, slant, weight, t2c, t2f, t2g, t2s, t2w, gradient, tab_width, warn_missing_font, height, width, should_center, disable_ligatures, **kwargs).scale_to_fit_width(width_to_fit)
    # I use a margin of 100 pixels so avoid being just in the borders
    txt_height_fitted = Text(text, fill_opacity, stroke_width, color, font_size, line_spacing, font, slant, weight, t2c, t2f, t2g, t2s, t2w, gradient, tab_width, warn_missing_font, height, width, should_center, disable_ligatures, **kwargs).scale_to_fit_height(SCENE_HEIGHT - height_to_manim_height(100))

    # As it is a 16:9 proportion, the height is the measure that limits the most
    if txt_height_fitted.font_size < txt_width_fitted.font_size:
        return txt_height_fitted
    return txt_width_fitted

def fullscreen_image(filename, scale_to_resolution: int = QUALITIES[DEFAULT_QUALITY]["pixel_height"], invert: bool = False, image_mode: str = 'RGBA', **kwargs):
    """
    Returns an ImageMobject that fits the provided 'width_to_fit' ignoring height. This is useful
    if you want an Image that fills the whole screen width.
    """
    image_width_fitted = ImageMobject(filename, scale_to_resolution, invert, image_mode, **kwargs).scale_to_fit_width(width_to_manim_width(1920))
    image_height_fitted = ImageMobject(filename, scale_to_resolution, invert, image_mode, **kwargs).scale_to_fit_height(height_to_manim_height(1080))

    # We want the image that occupies the whole screen
    if manim_height_to_height(image_width_fitted.height) >= 1080:
        return image_width_fitted
    
    return image_height_fitted

def preprocess_image(image: ImageMobject):
    """
    This method processes images bigger than our 1920x1080 dimensions and returns it
    scaled down to fit those dimensions. You should use this method as the first one
    when working with ImageMobjects, and then scaling it down as much as you need.
    """
    if manim_width_to_width(image.width) > 1920:
        image.scale_to_fit_width(width_to_manim_width(1920))
    if manim_height_to_height(image.height) > 1080:
        image.scale_to_fit_height(height_to_manim_height(1080))

    return image

def generate_manim_animation(animation_name, parameters, output_filename):
    """
    Generates a manim animation video file using one of our premade animations
    (attending to 'animation_name' provided), using the 'parameters', that is
    stored as the 'output_filename' video file.

    The 'animation_name' must be the exact name of any of our custom manim
    animation classes created. For example: 'TextAnimated'

    The 'parameters' option must be a dictionary. Manim animation building
    process will use those parameter to customize the animation.

    If a '.mp4' extension in output given, it won't use the '-t' manim parameter
    that allows transparency, because it is not supported in .mp4 files.

    Be careful, because when using sounds the video time could become longer
    than the expected one.
    """
    write_manim_config_file(parameters)

    FPS = str(60)
    MANIM_CLASSES_CONTAINER_ABSPATH = 'utils/animation_classes'

    # TODO: Please, try to execute it from here as Python code and not through the
    # command line (see here: https://stackoverflow.com/questions/66642657/is-it-possible-to-run-manim-programmatically-and-not-from-the-command-line)
    # TODO: Check if 'animation_name' is accepted
    # -qh is high quality (1080p)
    # '-t' parameter creates a .mov file (that accepts transparency) instead of .mp4
    command_parameters = ['manim', '-qh', '-t', '--fps', FPS, MANIM_CLASSES_CONTAINER_ABSPATH, animation_name]
    manim_output_file_extension = '.mov'

    # TODO: Do more Exception checkings (such as '.smtg')
    if output_filename.endswith('.mp4'):
        #output_filename.replace('.mp4', '.mov')
        # We now delete '-t' parameter instead of forcing .mov
        manim_output_file_extension = '.mp4'
        del command_parameters[2]

    run(command_parameters)
        
    MANIM_CREATIONS_ABSPATH = get_project_abspath() + 'media/videos/' + get_filename(MANIM_CLASSES_CONTAINER_ABSPATH) + '/1080p' + FPS + '/' + animation_name + manim_output_file_extension

    rename_file(MANIM_CREATIONS_ABSPATH, output_filename)

    return output_filename

# TODO: Remove this below as it is useless
# def add_manim_animation_to_video(original_video_filename, original_video_duration, manim_animation_name, manim_animation_parameters, output_filename):
#     """
#     Generates a manim animation video file with the provided 'manim_animation_name' and
#     'manim_animation_parameters', and puts it in the foreground of the original video
#     provided.

#     'original_video_duration' parameter is passed to crop the original video to that
#     duration in seconds if it is interesting for the final animation.

#     This is a method that must be used to add any manim animation to any app-generated
#     video.
#     """
#     from utils.video_utils import add_manin_animation_to_video as add_manim_animation_to_videoclip
#     TMP_MANIM_ANIMATION_FILENAME = PROJECT_ABSOLUTE_PATH + 'tmp_manim_animation.mov'

#     # TODO: Check that 'manim_animation_name' exist (is valid)

#     # We generate the animation video file
#     generate_manim_animation(manim_animation_name, manim_animation_parameters, TMP_MANIM_ANIMATION_FILENAME)

#     # We put the animation video file in the foreground of the original video
#     add_manim_animation_to_videoclip(original_video_filename, original_video_duration, TMP_MANIM_ANIMATION_FILENAME, output_filename)
    
# TODO: Is this below useful?
# export with transparent background: https://manimclass.com/manim-export-transparent-background/
# command to export:   manim --format=mp4 -qm -t Formula
