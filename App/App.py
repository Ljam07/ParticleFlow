from Engine.Core.Application import Application
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import Renderer
from Engine.Renderer.Camera import Camera
from Engine.Core.DeltaTime import DeltaTime

import imgui

class ParticleFlowLayer(Layer):
    def __init__(self, name="ParticleFlowLayer"):
        super().__init__(name)
        
        self._camera = Camera()
        
    def OnAttach(self):
        print("Attached Particle Flow Layer")

    def OnUpdate(self, dt: DeltaTime):
        # time = dt.GetSeconds()
        # print(f"Last Frame Time: {time}")
        # print(f"FPS: {1/time}")
        pass
        
class UILayer(Layer):
    
    def __init__(self, name="Layer"):
        super().__init__(name)
        # initilize imgui context (see documentation)
        
        
    def OnAttach(self):
        print("Attached UI Layer")
        imgui.create_context()
        imgui.get_io().display_size = 100, 100
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        
    def OnUpdate(self, dt):
        # start new frame context
        imgui.new_frame()

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

        # close current window context
        imgui.end()

        # pass all drawing comands to the rendering pipeline
        # and close frame context
        imgui.render()
        imgui.end_frame()

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)
        
        self._layer_stack.PushLayer(ParticleFlowLayer())
        self._layer_stack.PushLayer(UILayer())
