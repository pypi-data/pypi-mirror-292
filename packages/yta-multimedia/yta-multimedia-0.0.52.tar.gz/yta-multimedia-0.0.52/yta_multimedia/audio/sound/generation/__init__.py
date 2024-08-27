from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from yta_multimedia.resources.audio.drive_urls import TYPING_KEYBOARD_3_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL, SILENCE_10_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL
from yta_multimedia.video.edition.effect.constants import EFFECTS_RESOURCES_FOLDER
from yta_multimedia.resources import get_resource
from yta_general_utils.tmp_processor import create_tmp_filename

# TODO: This should be moved to classes, I think, as I did with
# GoogleSearch video premade generator

def create_silence_audio_file(duration, output_filename):
    """
    Creates a silence audio file that lasts the 'duration' provided in 
    seconds.
    """
    create_silence_audio_clip(duration).write_audiofile(output_filename)

def create_silence_audio_clip(duration) -> AudioFileClip:
    """
    This method creates a silence AudioFileClip of the provided 'duration' in
    seconds and returns it.
    """
    TMP_FILENAME = get_resource(SILENCE_10_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL, EFFECTS_RESOURCES_FOLDER + 'sounds/silence_10s.mp3')

    # TODO: Here we need to apply a new logic that we need to create
    # in which we adjust a clip duration by lengthening or trimming 
    # the video
    return AudioFileClip(TMP_FILENAME).subclip(0, duration)

def create_typing_audio_file(output_filename: str):
    """
    This method creates a typing audio of 3.5 seconds (3s of typing, 0.5 of silence).
    """
    if not output_filename:
        return None
    
    create_typing_audio_clip().write_audiofile(output_filename)

def create_typing_audio_clip() -> CompositeAudioClip:
    """
    This method creates a typing audio of 3.5 seconds (3s of typing, 0.5 of silence)
    and returns it as a clip.
    """
    TMP_FILENAME = get_resource(TYPING_KEYBOARD_3_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL, EFFECTS_RESOURCES_FOLDER + 'sounds/typing_keyboard_3s.mp3')
    typing_audio_clip = AudioFileClip(TMP_FILENAME)
    silence_audio_clip = create_silence_audio_clip(0.5)

    return concatenate_audioclips([typing_audio_clip, silence_audio_clip])
