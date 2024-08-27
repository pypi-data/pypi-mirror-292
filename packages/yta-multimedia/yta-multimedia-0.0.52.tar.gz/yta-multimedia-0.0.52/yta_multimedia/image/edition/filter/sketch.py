from PIL import Image
from typing import Union

import cv2

def image_to_sketch(image: str, output_filename: Union[str, None] = None):
    """
    Turns the provided 'image' into an sketch that is made 
    by white and black colors.
    """
    # Thank you: https://github.com/code-kudos/Convert-any-image-to-sketch-with-python/blob/main/Sketch.py
    if not image:
        return None

    img = cv2.imread(image)
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    invert_img = cv2.bitwise_not(grey_img)
    blur_img = cv2.GaussianBlur(invert_img, (277, 277), 0)
    invblur_img = cv2.bitwise_not(blur_img)
    sketch_img = cv2.divide(grey_img, invblur_img, scale = 256.0)
    rgb_sketch = cv2.cvtColor(sketch_img, cv2.COLOR_BGR2RGB)

    sketch_image = Image.fromarray(rgb_sketch)

    if output_filename:
        sketch_image.save(output_filename)

    return sketch_image