# Engine imports
from Engine.Core.Application import Application
from Engine.Core.Layer import *
from Engine.Renderer.Renderer import Renderer
from Engine.Renderer.Camera import Camera
from Engine.Core.DeltaTime import DeltaTime
from Engine.Core.UI import UI
from Engine.Core.Window import Window
from Engine.Renderer.Shader import Shader
from Engine.Renderer.Mesh import Mesh
from Engine.Renderer.Camera import Camera

import glm
import glfw

class ParticleFlowLayer(Layer):
    def __init__(self, window: Window, name="ParticleFlowLayer",):
        super().__init__(name)
        
        self._camera = Camera(aspect=window.GetWidth()/window.GetHeight())
        self._window = window
        
        sphere_vertices = Mesh.generate_uv_sphere(6, 12, 1)
                
        self.shader: Shader = Shader("App/Shaders/default.vert", "App/Shaders/default.frag")
        mesh   = Mesh(sphere_vertices)
        self._renderer = Renderer(self.shader, mesh)
        
        self._camera = Camera()
        self._show_debug = True
        self._colors = glm.vec3(0.2, 0.3, 0.5)
        
    def OnAttach(self):
        print("Attached Particle Flow Layer")

    def OnUpdate(self, dt: DeltaTime):
        #Actual application code here
        if not UI.IsHovered():
            self._camera.OnUpdate(self._window.GetWindow())
        self.shader.Use()
        self.shader.UploadMat4("uView", self._camera.GetViewMatrix())
        self.shader.UploadMat4("uProj", self._camera.GetProjectionMatrix())
        
        self._renderer.draw()
    
    def OnUI(self, dt: DeltaTime = None):
        UI.Begin("Debug")
        self._show_debug, _ = UI.Checkbox("Show Debug Stats", self._show_debug)
        
        # Show debug info if true
        if not (dt == None) and self._show_debug:
            time = dt.GetSeconds()
            timems = dt.GetMilliseconds()
            UI.Text(f"Last frame time(ms): {round(timems, 4)}")
            UI.Text(f"FPS: {round(1/time, 2)}")
                    
        UI.End()
        
        

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)
               
        self._layer_stack.PushLayer(ParticleFlowLayer(self._window))
