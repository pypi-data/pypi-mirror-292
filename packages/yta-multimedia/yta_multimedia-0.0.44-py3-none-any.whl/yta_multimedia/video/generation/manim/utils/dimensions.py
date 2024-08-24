from yta_multimedia.video.generation.manim.constants import SCENE_HEIGHT, SCENE_WIDTH

def width_to_manim_width(width):
    """
    You provide a real width in pixels (maybe 1920) and it is returned in the
    manim equivalent width. We consider a 16:9 proportion and 1920 as the
    maximum valid width.

    This method is built by myself to work better with a 16:9 proportion of 
    1920x1080 pixels. The manim system is different, so I made this to
    simplify the process.
    """
    return (width * SCENE_WIDTH) / 1920

def manim_width_to_width(width):
    """
    TODO: Write help
    """
    return (width * 1920) / SCENE_WIDTH

def height_to_manim_height(height):
    """
    You provide a real height in pixels (maybe 1080) and it is returned in the
    manim equivalent pixels. We consider 16:9 proportion and 1080 as the 
    maximum valid height.

    This method is built by myself to work better with a 16:9 proportion of 
    1920x1080 pixels. The manim system is different, so I made this to
    simplify the process.
    """
    return (height * SCENE_HEIGHT) / 1080

def manim_height_to_height(height):
    """
    TODO: Write help
    """
    return (height * 1080) / SCENE_HEIGHT