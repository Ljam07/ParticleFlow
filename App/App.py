from Engine.Core.Application import Application
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import Renderer
from Engine.Renderer.Camera import Camera
from Engine.Core.DeltaTime import DeltaTime

from Engine.Core.UI import UI

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
    
    def OnUI(self):
        UI.Begin("New Window")
        UI.Text("Hello, world!")
        UI.End()
        
        

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)
        
        self._layer_stack.PushLayer(ParticleFlowLayer())
