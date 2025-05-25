from Engine.Core.Window import *
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import *
from Engine.Core.DeltaTime import DeltaTime
from Engine.Core.UI import UI

import glfw

    
class Application:
    def __init__(self, width = 800, height = 600, title = "ParticleFlow"):
        self._window = Window(width, height, title)
        self._ui = UI()
        
        self._layer_stack = LayerStack()
        self._Running = True
        self._last_frame_time = 0.0

    def EndApplication(self):
        self._Running = False
        
    def GetWindow(self):
        return self._window

    def Run(self):
        print("Created Application") 
        self._ui.InitUI(self._window.GetWindow())
        while self._window.WindowOpen():
            time = glfw.get_time()
            deltaTime = DeltaTime(time - self._last_frame_time)
            self._last_frame_time = time


            # clear + buffer swap
            self._window.Clear()
            # update layers if any
            self._ui.BeginFrame()
            self._layer_stack.OnUpdate(deltaTime)
            self._layer_stack.OnUI(deltaTime)

            # draw triangle
            self._ui.EndFrame()
            self._window.OnUpdate()

        self._window.CloseWindow()


