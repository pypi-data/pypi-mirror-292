from yta_general_utils.tmp_processor import create_custom_tmp_filename
from yta_multimedia.video.frames import extract_all_frames_from_video
from yta_general_utils.file_processor import read_json_from_file, write_json_to_file, get_filename, create_file_abspath, list, file_exists, get_project_abspath, file_is_video_file
from yta_general_utils.type_checker import variable_is_type
from yta_multimedia.resources import get_resource
from yta_multimedia.greenscreen.classes.greenscreen_details import GreenscreenDetails
from yta_multimedia.greenscreen.classes.greenscreen_area_details import GreenscreenAreaDetails
from yta_multimedia.greenscreen.enum.greenscreen_type import GreenscreenType
from moviepy.editor import ImageSequenceClip
from yta_general_utils.file_downloader import get_id_from_google_drive_url
from yta_multimedia.green_screen.custom.image_greenscreen import ImageGreenscreen
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
from typing import Union

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

    # TODO: Maybe improve this code below with this:
    # https://www.projectpro.io/recipes/find-most-frequent-value-array
    #
    # This finds the most common value in numpy array
    # counts = np.bincount(a)
    # most_frequent_value = np.argmax(counts)

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


# TODO: I'm placing this below here by now, but maybe we should
# build a 'MovingVideoGreenscreen' object for this
def insert_video_into_moving_greescreen(greenscreen_google_drive_url: str, video: Union[VideoFileClip, CompositeVideoClip, ImageClip, str], output_filename: str):
    """
    This method inserts the provided 'video' into the moving greenscreen
    that is contained in the provided 'greenscreen_google_drive_url'. It
    will extract all greenscreen frames, analyze each of them and extract
    the greenscreen areas information and put the provided 'video' 
    combined with the greenscreen.

    This method will identify the Google Drive ID to store (or load if
    previously downloaded) the moving greenscreen video to be able to
    handle it. It will use one specific folder to work with the data:
    'resources/greenscreens/moving/frames/GOOGLE_DRIVE_ID', extracting
    the frames, generating a 'config.json' file and also downloading
    the resource from Google Drive.

    @param
        **greenscreen_google_drive_url**
        The Google Drive url of the moving greenscreen video resource.

    @param
        **video**
        The filename of the video we want to put into the greenscreen.

    @param
        **output_filename**
        The filename in which we want to write the final video that is
        our 'video' inside of the greenscreen.
    """
    if not video:
        raise Exception('No valid "video" provided.')
    
    if variable_is_type(video, str):
        if not file_is_video_file(video):
            raise Exception('Parameter "video" provided is not a valid video file.')
        
        video = VideoFileClip(video)
    
    preprocess_moving_greenscreen(greenscreen_google_drive_url)
    google_drive_id = get_id_from_google_drive_url(greenscreen_google_drive_url)
    moving_gs_folder = 'resources/greenscreens/moving/frames/' + google_drive_id + '/'
    moving_gs_filename = moving_gs_folder + 'greenscreen.mp4'

    moving_gs = VideoFileClip(get_resource(greenscreen_google_drive_url, moving_gs_filename))

    if moving_gs.duration < video.duration:
        video = video.set_duration(moving_gs.duration)
    elif video.duration < moving_gs.duration:
        moving_gs = moving_gs.set_duration(video.duration)

    # We extract the main video frames
    frames_main_folder = create_custom_tmp_filename('frames_main')
    final_frames_folder = create_custom_tmp_filename('frames_final')
    extract_all_frames_from_video(video, frames_main_folder)

    greenscreen_id = get_id_from_google_drive_url(greenscreen_google_drive_url)

    moving_greenscreen_frames_folder_relpath = 'resources/greenscreens/moving/frames/' + greenscreen_id + '/'
    config_filename = moving_greenscreen_frames_folder_relpath + 'config.json'

    greenscreen_details = read_json_from_file(config_filename)

    # Iterate over frames
    frames = list(frames_main_folder + '/')
    for index, frame in enumerate(frames):
        details = greenscreen_details[str(index)]

        image_greenscreen = ImageGreenscreen(GreenscreenDetails(
            greenscreen_areas = [
                GreenscreenAreaDetails(
                    rgb_color = details['rgb_color'],
                    upper_left_pixel = details['upper_left_pixel'],
                    lower_right_pixel = details['lower_right_pixel'],
                    frames = None
                )
            ],
            filename_or_google_drive_url = moving_gs_folder + get_filename(frame),
            type = GreenscreenType.IMAGE
        ))
        print(frame)
        print(final_frames_folder + '/' + get_filename(frame))
        # Write final combined frame
        image_greenscreen.from_image_to_image(frame, final_frames_folder + '/' + get_filename(frame))
        
    ImageSequenceClip(final_frames_folder, fps = video.fps).set_audio(video.audio).write_videofile(output_filename)

def preprocess_moving_greenscreen(greenscreen_google_drive_url: str):
    """
    This method analyzes, frame by frame, a video greenscreen and stores
    each frame information about greenscreen area in a config file to
    be lately used for video injection.
    """
    if not greenscreen_google_drive_url:
        raise Exception('No valid "greenscreen_google_drive_url" provided.')

    google_drive_id = get_id_from_google_drive_url(greenscreen_google_drive_url)
    moving_gs_filename = get_resource(greenscreen_google_drive_url, 'resources/greenscreens/moving/frames/' + google_drive_id + '/greenscreen.mp4')

    # Read the video and extract frames
    gs_clip = VideoFileClip(moving_gs_filename)

    for i in range((int) (gs_clip.fps * gs_clip.duration)):
        process_moving_greenscreen_frame(greenscreen_google_drive_url, i)

    return

# TODO: I think this method could be private
def process_moving_greenscreen_frame(greenscreen_google_drive_url: str, frame_number: int, do_force: bool = False):
    """
    This method processes the 'frame_number' frame of the existing
    greenscreen in 'greenscreen_google_drive_url' source. It will
    detect the greenscreen area of that frame and store it in the
    specific configuration file.

    This method will store the information in an specific folder
    'resources/greenscreens/moving/frames/GOOGLE_DRIVE_ID/'. All
    the information is the greenscreen video, the frames and the
    'config.json' file that contains the detailed greenscreen
    areas of each frame. As you can see, the 'GOOGLE_DRIVE_ID' is
    used as identifier.

    If that 'frame_number' has been previously analyzed, the 
    system will do it again only if the 'do_force' parameter
    is True. If not, it will stop and return.

    @param
        **greenscreen_google_drive_url**
        The Google Drive url that contains the greenscreen video
        from which we will analyze the frame.
    
    @param
        **frame_number**
        The frame number that will be analyzed. The first frame of
        the greenscreen is the number 0.

    @param
        **do_force**
        The information of that 'frame_number' could be stored 
        previously so it would be ignored. You can set this
        parameter to True to force recalculating the frame.
    """
    if not greenscreen_google_drive_url:
        return None
    
    if frame_number < 0:
        return None
    
    # We obtain greenscreen id from google_drive_url
    # url: https://drive.google.com/file/d/1My5V8gKcXDQGGKB9ARAsuP9MIJm0DQOK/view?usp=sharing
    greenscreen_id = get_id_from_google_drive_url(greenscreen_google_drive_url)

    moving_greenscreen_frames_folder_relpath = 'resources/greenscreens/moving/frames/' + greenscreen_id + '/'
    config_filename = moving_greenscreen_frames_folder_relpath + 'config.json'
    greenscreen_filename = moving_greenscreen_frames_folder_relpath + 'greenscreen.mp4'

    # Check that frames folder and config file exist or create them
    if not file_exists(config_filename):
        create_file_abspath(get_project_abspath() + config_filename)
        write_json_to_file({}, config_filename)

    json_data = read_json_from_file(config_filename)

    if str(frame_number) in json_data and not do_force:
        # TODO: Maybe rewrite it (?)
        return

    # We make sure we have the clip (and resource)
    gs_clip = VideoFileClip(get_resource(greenscreen_google_drive_url, greenscreen_filename))

    greenscreen_frames_number = (int) (gs_clip.fps * gs_clip.duration)
    if frame_number > (greenscreen_frames_number):
        raise Exception('The requested "frame_number" is not valid. The greenscreen only has "' + str(greenscreen_frames_number) + '" frames.')
    
    frames = list(moving_greenscreen_frames_folder_relpath, pattern = '*.png')

    # Requesting a valid frame that we don't have: extract
    if len(frames) <= frame_number:
        extract_all_frames_from_video(gs_clip, moving_greenscreen_frames_folder_relpath)
        frames = list(moving_greenscreen_frames_folder_relpath, pattern = '*.png')

    gs_frame = frames[frame_number]
    
    details = get_greenscreen_area_details(gs_frame)

    # By now we are only getting one single greenscreen area data
    json_data[frame_number]= {
        'index': frame_number,
        'frame_filename': gs_frame,
        'rgb_color': details['rgb_color'],
        'upper_left_pixel': details['upper_left_pixel'],
        'lower_right_pixel': details['lower_right_pixel'],
        'frames': None
    }

    return write_json_to_file(json_data, config_filename)