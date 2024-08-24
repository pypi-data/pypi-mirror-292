from moviepy.editor import ImageClip, vfx, AudioFileClip, CompositeVideoClip, ColorClip, clips_array
from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_multimedia.resources.video.effect.sound.drive_urls import SAD_MOMENT_GOOGLE_DRIVE_DOWNLOAD_URL
from enum import Enum
from math import log as math_log, pow as math_pow

class MoviepyCustomEffect(Enum):
    """
    Handmade custom moviepy effects that are applied by
    composing moviepy video clips. These effects are
    manually made and tested.
    """
    def __sad_moment(clip, duration = 4.8):
        """
        This method gets the first frame of the provided 'clip' and returns a
        new clip that is an incredible 'sad_moment' effect with black and white
        filter, zoom in and rotating effect and also sad violin music.

        The 'duration' parameter is to set the returned clip duration, but the
        default value is a perfect one.
        """
        if not clip:
            return None
        
        # We freeze the first frame
        aux = ImageClip(clip.get_frame(0), duration = duration)
        aux.fps = clip.fps
        clip = aux
        # We then build the whole effect
        clip = clip.fx(vfx.blackwhite).resize(lambda t: 1 + 0.30 * (t / clip.duration)).set_position(lambda t: (-(0.15 * clip.w * (t / clip.duration)), -(0.15 * clip.h * (t / clip.duration)))).rotate(lambda t: 5 * (t / clip.duration), expand = False)
        # We set the effect audio
        TMP_FILENAME = download_file_from_google_drive(SAD_MOMENT_GOOGLE_DRIVE_DOWNLOAD_URL, create_tmp_filename('tmp.mp3'))
        clip.audio = AudioFileClip(TMP_FILENAME).set_duration(clip.duration)

        return CompositeVideoClip([
            ColorClip(color = [0, 0, 0], size = clip.size, duration = clip.duration),
            clip,
        ])
    
    def __multiply_x(clip, times = 4):
        """
        Generates a clips array with the provided 'clip' being shown
        'times' times (this parameter must be a pow of 4). This
        method has been created to be used internally with our own
        default methods.
        """
        if not clip:
            return None
        
        if times <= 1 or not math_log(times, 4).is_integer():
            return None
        
        audio = clip.audio
        size = (clip.w, clip.h)

        # We will dynamically build the matrix
        row = []
        group = []
        # 4^3 = 64 => 8x8 = 2^3x2^3  and  4^2 = 16 => 4x4 = 2^2x2^2
        range_limit_value = math_pow(2, math_log(times, 4))
        for i in range(int(times / range_limit_value)):
            row = []
            for j in range(int(times / range_limit_value)):
                row.append(clip.resize((clip.w / times, clip.h / times)))
            group.append(row)

        # When building 'clips_array' you sum the resolutions, so if you add four videos
        # of 1920x1080, you'll get one video of 4x(1920x1080) that will be impossible to
        # exported and unexpected. We resize it.
        return clips_array(group).resize(size).set_audio(audio)
    
        # TODO: Remove this if above is working
        return clips_array([
            [clip, clip],
            [clip, clip]
        ]).resize(size).set_audio(audio)

    SAD_MOMENT = __sad_moment
    MULTIPLY_X = __multiply_x

    # TODO: See utils/video_utils.py in software project