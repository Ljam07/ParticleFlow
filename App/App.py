from Engine.Core.Application import Application
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import Renderer
from Engine.Renderer.Camera import Camera

class ParticleFlowLayer(Layer):
    def __init__(self, name="ParticleFlowLayer"):
        super().__init__(name)
        
        self._camera = Camera()
        
    def OnAttach(self):
        print("Attached Particle Flow Layer")
        
class UILayer(Layer):
    
    def __init__(self, name="Layer"):
        super().__init__(name)
        
    def OnAttach(self):
        print("Attached UI Layer")

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)
        
        self._layer_stack.PushLayer(ParticleFlowLayer())
        self._layer_stack.PushLayer(UILayer())
