from scamp import Session, playback_settings, Envelope, wait
from random import random, choice

def play_instrumental():
    """
    This method is so experimental. It uses a library that allows
    creating instrumental part of a song by using instruments and
    telling the songs you want to listen.

    TODO: This need a lot of work, investigation and refactor
    """
    # Thanks to:
    # https://www.youtube.com/watch?v=vpv686Rasds

    # This is for saving the generated audio, that is based on:
    # https://scampsters.marcevanstein.com/t/can-we-send-scamp-output-to-a-wav-file/314
    playback_settings.recording_file_path = "chello.wav"

    session = Session()
    session.tempo = 60 

    cello = session.new_part('cello')

    #session.start_transcribing()

    forte_piano = Envelope.from_levels_and_durations(
        [0.8, 0.4, 1.0], [0.2, 0.8], curve_shapes = [0, 3]
    )

    diminuendo = Envelope.from_levels([0.8, 0.3])

    def wrap_in_range(value, low, high):
        return (value - low) % (high - low) + low
    
    for pitch in (48, 53, 64, 75, 80):
        cello.play_note(pitch, 1.0, 1.0)

    interval = 1
    cello_pitch = 48

    do_continue = True
    while do_continue:
        if random() < 0.7:
            cello.play_note(cello_pitch, forte_piano, choice([1.0, 1.5]))
        else:
            cello.play_note(cello_pitch, diminuendo, choice([2.0, 2.5, 3.0]))
            wait(choice([1.0, 1.5]))
        cello_pitch = wrap_in_range(cello_pitch + interval, 36, 60)
        interval += 1

        if interval == 20:
            do_continue = False

    # ImportError: abjad was not found; LilyPond output is not available.
    #session.stop_transcribing().to_score(time_signature = '3/8').show()
    #session.stop_transcribing()

    return