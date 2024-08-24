from moviepy.editor import ImageClip, vfx, AudioFileClip, CompositeVideoClip, ColorClip
from yta_general_utils.file_downloader import download_file_from_google_drive
from yta_general_utils.tmp_processor import create_tmp_filename
from yta_multimedia.resources.video.effect.sound.drive_urls import SAD_MOMENT_GOOGLE_DRIVE_DOWNLOAD_URL
from enum import Enum

class CustomEffect(Enum):
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

    SAD_MOMENT = __sad_moment

    # TODO: See utils/video_utils.py in software project