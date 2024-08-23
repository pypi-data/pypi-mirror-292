from pedalboard import Pedalboard, Reverb
from math import trunc
from yta_general_utils.file_processor import get_file_extension, file_is_audio_file
from yta_general_utils.audio_processor import mp3_to_wav
from yta_general_utils.tmp_processor import create_tmp_filename

import numpy as np
import soundfile as sf

def slow_and_reverb_audio_file(audio_filename: str, output_filename: str, room_size: float = 0.75, damping: float = 0.5, wet_level: float = 0.08, dry_level: float = 0.2, delay: float = 2, slow_factor: float = 0.08):
    # Extracted from here: https://github.com/samarthshrivas/LoFi-Converter-GUI
    # But there is no only one: https://github.com/topics/slowedandreverbed
    if not audio_filename:
        return None
    
    if not file_is_audio_file(audio_filename):
        return None

    if not output_filename:
        return None
    
    if get_file_extension(audio_filename) != '.wav':
        # TODO: Handle other formats, by now I think it is .mp3 only
        tmp_filename = create_tmp_filename('transformed_audio.wav')
        mp3_to_wav(audio_filename, tmp_filename)
        audio_filename = tmp_filename

    audio, sample_rate = sf.read(audio_filename)
    sample_rate -= trunc(sample_rate * slow_factor)

    # Adding reverb effect
    reverved_board = Pedalboard([
        Reverb(
            # TODO: I need to learn more about these parameters
            room_size = room_size,
            damping = damping,
            wet_level = wet_level,
            dry_level = dry_level
        )
    ])

    # Adding other surrounding effects
    audio_with_effects = reverved_board(audio, sample_rate)
    channel_1 = audio_with_effects[:, 0]
    channel_2 = audio_with_effects[:, 1]
    shift_length = delay * 1000
    shifted_channel_1 = np.concatenate((np.zeros(shift_length), channel_1[:-shift_length]))
    combined_signal = np.hstack((shifted_channel_1.reshape(-1, 1), channel_2.reshape(-1, 1)))

    # Write the slowed and reverved output file
    sf.write(output_filename, combined_signal, sample_rate)


# TODO: Remove this below when tested
original_filename = 'C:/Users/dania/Downloads/rosalia_conaltura.mp3'
original_filename = 'C:/Users/dania/Desktop/PROYECTOS/yta-multimedia/output/rosalia_conaltura/accompaniment.wav'
output_filename = 'test_lofi.wav'

def test(input_filename, output_filename):
    print('Converting to lofi')
    slow_and_reverb_audio_file(input_filename, output_filename)
    print('Converted')

test(original_filename, output_filename)