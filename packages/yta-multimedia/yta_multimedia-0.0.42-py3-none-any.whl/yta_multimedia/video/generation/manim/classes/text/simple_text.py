from yta_multimedia.video.generation.manim.classes.base_manim_animation import MyAnimation
from yta_multimedia.video.generation.manim.constants import MANDATORY_CONFIG_PARAMETER
from manim import Text, DOWN, Write

class SimpleText(MyAnimation):
    required_parameters = {
        'text': MANDATORY_CONFIG_PARAMETER,
        'duration': MANDATORY_CONFIG_PARAMETER,
    }

    def construct(self):
        self.animate()

    def animate(self):
        text = Text(self.parameters['text'], font_size = 100, stroke_width = 2.0, font = 'Arial').shift(DOWN * 0)
        simple_play_animation(self, Write, text)

def simple_play_animation(self, animation, object):
    # TODO: Move this to a general animator util
    END_WAITING = 0.1
    REAL_DURATION = self.parameters['duration'] - END_WAITING

    self.play(animation(object), run_time = REAL_DURATION)
    self.wait(END_WAITING)