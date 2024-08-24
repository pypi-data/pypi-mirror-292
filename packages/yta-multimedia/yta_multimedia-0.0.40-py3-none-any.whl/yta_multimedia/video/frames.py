from moviepy.editor import VideoFileClip
from yta_general_utils.type_checker import variable_is_type
from yta_general_utils.file_processor import file_is_video_file
from typing import Union

def extract_all_frames_from_video(video_input: Union[VideoFileClip, str], output_folder: str):
    """
    This method will extract all the 'video_input' frames in the
    provided 'output_folder' with the 'frameXXXXX.png' name, starting
    from 0 to the last frame.
    """
    if not video_input:
        return None
    
    if not output_folder:
        return None
    
    if not output_folder.endswith('/'):
        output_folder += '/'
    
    if variable_is_type(video_input, str):
        if not file_is_video_file(video_input):
            return None
        
        video_input = VideoFileClip(video_input)

    video_input.write_images_sequence(output_folder + 'frame%05d.png')

    return output_folder

def extract_frames_from_video(video_input: Union[VideoFileClip, str], frames_number: int, output_folder: str):
    """
    This method will extract only 'frames_number' frames of the 
    provided 'video_input' video and will be stored in also
    provided 'output_folder' with the 'frameXXXXX.png' name, 
    starting from 0 to the last frame.

    This method will split the video in 'frames_number' segments
    of the same duration and will extract the frame in the middle
    of each of those segments.

    To clarify, if a video lasts 20 seconds and the 'frames_number'
    parameter is 4, this method will extract the 4 frames that are
    in '2.5s', '7.5s', '12.5s' and '17.5s' time moments.
    """
    if not video_input:
        return None
    
    if not output_folder:
        return None
    
    if frames_number < 1:
        return None
    
    if not output_folder.endswith('/'):
        output_folder += '/'
    
    if variable_is_type(video_input, str):
        if not file_is_video_file(video_input):
            return None
        
        video_input = VideoFileClip(video_input)

    total_video_frames = video_input.fps * video_input.duration
    if frames_number > total_video_frames:
        return None

    # We will split the video in half 'frames_number' + 1 times
    # 20s video -> 4 frames => 20/4 = 5s*i + (5s/2) => 
    # i = 0,    i = 1,  i = 2,  i = 3
    # 2.5s,     7.5s,   12.5s,  17.5s
    time_fraction = video_input.duration / frames_number # 5s
    time_fraction_half = time_fraction / 2 # 2.5s
    moments = []

    for i in range(frames_number):
        moments.append(time_fraction * i + time_fraction_half)

    for index, moment in enumerate(moments):
        output_filename = output_folder + 'frame' + (str(index) + '').zfill(5) + '.png'
        video_input.save_frame(t = moment, filename = output_filename)

    return output_folder

def extract_frame_from_video(video_input: Union[VideoFileClip, str], time: float, output_filename: str):
    """
    Extracts a frame from the provided 'video_input' that is exactly at the
    also provided 'time' moment. The frame will be stored as 
    'output_filename'.
    """
    if not video_input:
        return None
    
    if not output_filename:
        return None
    
    if time < 0:
        return None
    
    if variable_is_type(video_input, str):
        if not file_is_video_file(video_input):
            return None
        
        video_input = VideoFileClip(video_input)

    if time > video_input.duration:
        return None

    video_input.save_frame(t = time, filename = output_filename)

    return output_filename