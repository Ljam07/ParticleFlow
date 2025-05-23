from Engine.Core.Window import *
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import *
from Engine.Core.DeltaTime import DeltaTime
import glfw
    
class Application:
    def __init__(self, width = 800, height = 600, title = "ParticleFlow"):
        self._window = Window(width, height, title)

        self._layer_stack = LayerStack()
        self._renderer = Renderer()
        self._Running = True
        self._last_frame_time = 0.0

    def EndApplication(self):
        self._Running = False

    def Run(self):
        print("Created Application")
        while self._window.WindowOpen():
            time = glfw.get_time()
            deltaTime = DeltaTime(time - self._last_frame_time)
            self._last_frame_time = time

            # clear + buffer swap
            self._window.Clear()
            # update layers if any
            self._layer_stack.OnUpdate(deltaTime)

            # draw triangle
            self._renderer.draw()
            self._window.OnUpdate()

        self._window.CloseWindow()


