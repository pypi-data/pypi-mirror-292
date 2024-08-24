from PIL import Image

import numpy as np
import skimage.exposure
import cv2

def get_green_screen_position(image_filename):
    """
    Detects the green screen color of the provided 'image_filename' and then looks for
    the upper left corner and the bottom right corner.

    This method return an object containing 'ulx', 'uly', 'drx', 'dry' coords. It also
    returns the 'rgb_color' most common green color as an (r, g, b).

    This will return None in ['rgb_color'] field if no green color detected.

    # TODO: Maybe rename to 'get_green_screen_properties' (?)
    """
    green_rgb_color = get_most_common_rgb_color(image_filename)

    image = Image.open(image_filename).convert('RGB')

    upper_left = {
        'x': 99999,
        'y': 99999,
    }
    down_right = {
        'x': -1,
        'y': -1,
    }

    for x in range(image.width):
        for y in range(image.height):
            rgb_color = (r, g, b) = image.getpixel((x, y))

            if rgb_color == green_rgb_color:
                if x < upper_left['x']:
                    upper_left['x'] = x
                if y < upper_left['y']:
                    upper_left['y'] = y
                
                """
                if x <= upper_left['x'] and y <= upper_left['y']:
                    upper_left = {
                        'x': x,
                        'y': y,
                    }
                """

                if x > down_right['x']:
                    down_right['x'] = x
                if y > down_right['y']:
                    down_right['y'] = y

                """
                if x >= down_right['x'] and y >= down_right['y']:
                    down_right = {
                        'x': x,
                        'y': y,
                    }
                """

    # We apply some margin to make sure we fit the green screen
    MARGIN = 2

    if (upper_left['x'] - MARGIN) > 0:
        upper_left['x'] -= MARGIN
    else:
        upper_left['x'] = 0

    if (upper_left['y'] - MARGIN) > 0:
        upper_left['y'] -= MARGIN
    else:
        upper_left['y'] = 0

    if (down_right['x'] + MARGIN) < 1920:
        down_right['x'] += MARGIN
    else:
        down_right['x'] = 1920

    if (down_right['y'] + MARGIN) < 1080:
        down_right['y'] += MARGIN
    else:
        down_right['y'] = 1080

    return {
        'rgb_color': green_rgb_color,
        'ulx': upper_left['x'],
        'uly': upper_left['y'],
        'drx': down_right['x'],
        'dry': down_right['y'],
    }

def get_most_common_rgb_color(image_filename, force_green = True):
    """
    Returns the most common green rgb color that exist in the provided
    'image_filename'. There could be no green color so it will return
    None, or the green color as (r, g, b) if existing.

    # TODO: This method could be made more generic by using a range
    # and then specializing this one by using that with green range
    """
    colors = {}
    image = Image.open(image_filename).convert('RGB')

    # We will check the most common rgb color (should be the green of mask)
    for x in range(image.width):
        for y in range(image.height):
            rgb_color = (r, g, b) = image.getpixel((x, y))

            if not rgb_color in colors:
                colors[rgb_color] = 1
            else:
                colors[rgb_color] += 1

    # Check which one is the most common
    most_used_rgb_color = {
        'color': None,
        'times': 0,
    }
    for key, value in colors.items():
        if force_green:
            # We only care about green colors
            r, g, b = key
            is_green = (r >= 0 and r <= 100) and (g >= 100 and g <= 255) and (b >= 0 and b <= 100)
            if is_green:
                if value > most_used_rgb_color['times']:
                    most_used_rgb_color = {
                        'color': key,
                        'times': value
                    }
        else:
            if value > most_used_rgb_color['times']:
                most_used_rgb_color = {
                    'color': key,
                    'times': value
                }

    return most_used_rgb_color['color']

def remove_green_screen_from_image_file(image_filename: str, output_filename: str):
    """
    Removes the green screen in the provided 'image_filename' (if
    existing) and creates a new image as 'output_filename' with a
    transparent mask instead of the green screen.
    """
    # From https://stackoverflow.com/a/72280828
    if not image_filename:
        return None
    
    if not output_filename:
        return None

    # load image
    img = cv2.imread(image_filename)

    # convert to LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # extract A channel
    A = lab[:,:,1]

    # threshold A channel
    thresh = cv2.threshold(A, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # blur threshold image
    blur = cv2.GaussianBlur(thresh, (0,0), sigmaX = 5, sigmaY = 5, borderType = cv2.BORDER_DEFAULT)

    # stretch so that 255 -> 255 and 127.5 -> 0
    mask = skimage.exposure.rescale_intensity(blur, in_range = (127.5, 255), out_range = (0, 255)).astype(np.uint8)

    # add mask to image as alpha channel
    result = img.copy()
    result = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
    result[:,:,3] = mask

    # save output
    cv2.imwrite(output_filename, result)