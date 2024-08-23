from PIL import Image

def get_greenscreen_area_details(image_filename: str):
    """
    This methods detects the greenscreen area in the provided
    'image_filename' image that contains one and valid 
    greenscreen.

    This method returns a dictionary containing 'rgb_color', 
    that is the green rgb color of the greenscreen area, and
    'upper_left_pixel' and 'lower_right_pixel', that are the
    greenscreen area corners we need to know. Each of those
    are (x, y) tuples containing the pixel coordinates. The
    'rgb_color' will be a (r, g, b) tuple containing the 
    values from 0 to 255 for each color.

    This method will return None in 'rgb_color' if no green
    color detected. This method will fail if more than one
    separated greenscreens in the provided 'image_filename'.
    """
    if not image_filename:
        return None
    
    green_rgb_color = get_most_common_rgb_color(image_filename)

    image = Image.open(image_filename).convert('RGB')

    upper_left = {
        'x': 99999,
        'y': 99999,
    }
    lower_right = {
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
                
                if x > lower_right['x']:
                    lower_right['x'] = x
                if y > lower_right['y']:
                    lower_right['y'] = y

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

    if (lower_right['x'] + MARGIN) < 1920:
        lower_right['x'] += MARGIN
    else:
        lower_right['x'] = 1920

    if (lower_right['y'] + MARGIN) < 1080:
        lower_right['y'] += MARGIN
    else:
        lower_right['y'] = 1080

    return {
        'rgb_color': green_rgb_color,
        'upper_left_pixel': (upper_left['x'], upper_left['y']),
        'lower_right_pixel': (lower_right['x'], lower_right['y'])
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