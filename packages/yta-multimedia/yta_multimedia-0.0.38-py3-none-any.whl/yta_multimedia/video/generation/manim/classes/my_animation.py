from yta_multimedia.video.generation.manim.constants import MANDATORY_CONFIG_PARAMETER
from yta_multimedia.video.generation.manim.utils.config import read_manim_config_file
from manim import Scene, AddTextLetterByLetter, Write, DrawBorderThenFill, ApplyWave, FadeIn
from random import randrange

class MyAnimation(Scene):
    """
    General class so that our own classes can inherit it 
    and work correctly.
    """
    def __set_mandatory_config(self):
        """
        This method set some configuration parameters we need to build perfect
        animation videos.
        """
        # This makes the video background transparent to fit well over the main video
        self.camera.background_opacity = 0.0

    def __read_manim_config_file(self, required_parameters):
        """
        Reads the configuration file we have to share parameters between moviepy
        software and manim software.

        It checks if the mandatory parameters exist in the information provided
        in the config file. If not, it raises an exception.
        """
        json_object = read_manim_config_file()
        object = {}

        # We check if required parameters exist or not
        for key, value in required_parameters.items():
            if key in json_object:
                object[key] = json_object[key]
            elif value == MANDATORY_CONFIG_PARAMETER:
                raise Exception('Parameter "' + key + '" is mandatory. Aborting...')

        return object
    
    def check_parameters(self, parameters, required_parameters):
        for key, value in required_parameters.items():
            if not key in parameters and value == MANDATORY_CONFIG_PARAMETER:
                raise Exception('Parameter "' + key + '" is mandatory. Aborting...')
        
        return True
    
    # TODO: I think this method below doesn't fit here
    def RandomTextAnimation(self):
        """
        Returns a random text animation to be applied with text.
        """
        random_animations = [AddTextLetterByLetter, Write, DrawBorderThenFill, ApplyWave, FadeIn]

        return random_animations[randrange(len(random_animations))]
    
    required_parameters = {}
    parameters = {}

    def setup(self):
        self.__set_mandatory_config()
        self.parameters = self.__read_manim_config_file(self.required_parameters)

        return self.parameters
    
    def construct(self):
        self.setup()