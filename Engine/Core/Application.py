from Engine.Core.Window import *
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import *
    
class Application:
    def __init__(self, width = 800, height = 600, title = "ParticleFlow"):
        self._window = Window(width, height, title)

        self._layer_stack = LayerStack()
        self._renderer = Renderer()
        self._Running = True

    def EndApplication(self):
        self._Running = False

    def Run(self):
        print("Created Application")
        while self._window.WindowOpen():
            # clear + buffer swap
            self._window.Clear()
            # update layers if any
            self._layer_stack.OnUpdate(0.1)

            # draw triangle
            self._renderer.draw()
            self._window.OnUpdate()

        self._window.CloseWindow()


