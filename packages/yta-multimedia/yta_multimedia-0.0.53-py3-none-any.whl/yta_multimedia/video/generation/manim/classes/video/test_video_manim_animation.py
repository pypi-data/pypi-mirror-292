"""
Some tests I made with Manim (3D, as it is the most difficult):
- ImageMobject + Cairo works, but positioning gets crazy.
- ImageMobject + Opengl fails
- OpenGLImageMobject + Opengl works perfectly.
- VideoMobject (ImageMobject) + Cairo works, but positioning gets crazy.
- VideoMobject (ImageMobject) + Opengl fails
- VideoMobject (OpenGLImageMobject) + Opengl only shows the first frame, but positioning is perfect.
- Didn't test anything else
"""
from yta_multimedia.video.generation.manim.classes.base_manim_animation import BaseManimAnimation
from yta_multimedia.video.generation.manim.classes.base_three_d_manim_animation import BaseThreeDManimAnimation
from yta_multimedia.video.generation.manim.classes.video.mobjects.video_mobject import VideoMobject
from yta_multimedia.video.generation.manim.classes.video.mobjects.video_opengl_mobject import VideoOpenGLMobject
from manim import *

class TestVideoMobjectIn2DManimAnimation(BaseManimAnimation):
    def construct(self):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.animate()

    def generate(self, output_filename: str = 'output.mov'):
        """
        Checks and validates the provided parameters and generates
        the manim animation if those parameters are valid. The 
        'text' parameter is limited to 30 characters.
        """
        # Check and validate all parameters
        parameters = {}

        # Generate the animation when parameters are valid
        super().generate(parameters, renderer = 'cairo', output_filename = output_filename)

        return output_filename
    
    def animate(self):
        video1 = VideoMobject(
            filename = 'prueba.mp4',
        ).scale_to_fit_width(5)
        self.add(video1)
        self.wait(0.25)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.play(video1.animate.shift(2 * DOWN), run_time = 0.5)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.wait(0.25)

class TestVideoOpenGLMobjectIn2DManimAnimation(BaseManimAnimation):
    def construct(self):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.animate()

    def generate(self, output_filename: str = 'output.mov'):
        """
        Checks and validates the provided parameters and generates
        the manim animation if those parameters are valid. The 
        'text' parameter is limited to 30 characters.
        """
        # Check and validate all parameters
        parameters = {}

        # Generate the animation when parameters are valid
        super().generate(parameters, renderer = 'opengl', output_filename = output_filename)

        return output_filename
    
    def animate(self):
        video1 = VideoOpenGLMobject(
            filename = 'prueba.mp4',
        ).scale_to_fit_width(5)
        self.add(video1)
        self.wait(0.25)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.play(video1.animate.shift(2 * DOWN), run_time = 0.5)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.wait(0.25)

class TestVideoMobjectIn3DManimAnimation(BaseThreeDManimAnimation):
    def construct(self):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.animate()

    def generate(self, output_filename: str = 'output.mov'):
        """
        Checks and validates the provided parameters and generates
        the manim animation if those parameters are valid. The 
        'text' parameter is limited to 30 characters.
        """
        # Check and validate all parameters
        parameters = {}

        # Generate the animation when parameters are valid
        super().generate(parameters, renderer = 'cairo', output_filename = output_filename)

        return output_filename
    
    def animate(self):
        video1 = VideoMobject(
            filename = 'prueba.mp4',
        ).scale_to_fit_width(5)
        self.add(video1)
        self.wait(0.25)
        self.begin_ambient_camera_rotation(rate = 0.15)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.play(video1.animate.shift(2 * DOWN), run_time = 0.5)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES, zoom=1, run_time=1.5)
        self.wait(0.25)

class TestVideoOpenGLMobjectIn3DManimAnimation(BaseThreeDManimAnimation):
    def construct(self):
        """
        This method is called by manim when executed by shell and
        will call the scene animation render method to be processed
        and generated.
        """
        self.animate()

    def generate(self, output_filename: str = 'output.mov'):
        """
        Checks and validates the provided parameters and generates
        the manim animation if those parameters are valid. The 
        'text' parameter is limited to 30 characters.
        """
        # Check and validate all parameters
        parameters = {}

        # Generate the animation when parameters are valid
        super().generate(parameters, renderer = 'opengl', output_filename = output_filename)

        return output_filename
    
    def animate(self):
        video1 = VideoOpenGLMobject(
            filename = 'prueba.mp4',
        ).scale_to_fit_width(5)
        self.add(video1)
        self.wait(0.25)
        self.begin_ambient_camera_rotation(rate = 0.15)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.play(video1.animate.shift(2 * DOWN), run_time = 0.5)
        self.play(video1.animate.shift(1 * UP), run_time = 0.25)
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES, zoom=1, run_time=1.5)
        self.wait(0.25)