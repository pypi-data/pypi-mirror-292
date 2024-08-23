from PIL import Image
from enum import Enum
from skimage.filters import gaussian

import numpy as np
import math

class CustomVFXEffect(Enum):
    """
    Handmade custom moviepy effects that must be applied
    by using 'clip.fl(effect)' or similar. These effects 
    are doing something on each frame.
    """
    def __zoom_in(get_frame, t, zoom_ratio = 0.01):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result
    
    def __zoom_out(get_frame, t, zoom_ratio = 0.01):
        # TODO: This is not a good effect because it doesn't 
        # work perfectly... Maybe removing it
        img = Image.fromarray(get_frame(t))
        base_size = tuple(1.4*x for x in img.size)

        new_size = [
            math.ceil(img.size[0] * (1 - (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 - (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)
        print(new_size)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result
    
    def __blur(get_frame, t, blur_radius = 4):
        """
        Applies the provided 'blur_radius' (in pixels) in
        the clip.
        """    
        # TODO: Is this working well (?)
        return gaussian(get_frame(t).astype(float), sigma = blur_radius)
    
    ZOOM_IN = __zoom_in
    ZOOM_OUT = __zoom_out
    BLUR = __blur

    # TODO: See utils/video_utils.py in software project