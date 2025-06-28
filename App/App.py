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

import imgui

# App imports
from App.Simulation.Simulation import *

class ParticleFlowLayer(Layer):
    def __init__(self, window: Window, name="ParticleFlowLayer", ):
        super().__init__(name)
        
        self._camera = Camera(aspect=window.GetWidth()/window.GetHeight())
        self._window = window
                      
        self.shader: Shader = Shader("App/Shaders/Particle.vert", "App/Shaders/Particle.frag")

        # Look at this hunk of garbage
        self.mesh   = Mesh(Mesh.GenerateUVSphere(6, 12, 1))
        self._renderer = Renderer(self.shader, self.mesh)
        
        self._camera = Camera()

        self._particle_size = 0.05
        self._domain_size = glm.vec3(3)
        self._domain_list = [self._domain_size.x, self._domain_size.y, self._domain_size.z]
        self._friction_coefficient = 0.7
        self._particle_number = 100
        self._particle_spacing = self._particle_size/2
        self._gravity = False
        self._sim = Simulation(self._particle_number, self._particle_size, self._domain_size, self._friction_coefficient, self._particle_spacing, glm.vec3(0, 0, 0))
        
    def OnAttach(self):
        print("Attached Particle Flow Layer")

    def OnUpdate(self, dt: DeltaTime):
        #Actual application code here
        dt = dt.GetSeconds()
        
        # To stop the program from going unpredictable under low framerates we limit highest dt to ensure smooth sim        
        minDt = 1/60
        if dt > minDt:
            dt = minDt
         
        if not UI.IsHovered():
            self._camera.OnUpdate(self._window.GetWindow())
            # Yo i think this is a pretty cool fix for dt being too big after creating particles
            if not self._sim.isFirst:
                self._sim.OnUpdate(dt)
            else:
                self._sim.isFirst = False
        self.shader.Use()
        self.shader.UploadMat4("uView", self._camera.GetViewMatrix())
        self.shader.UploadMat4("uProj", self._camera.GetProjectionMatrix())
        self.shader.UploadFloat("uParticleRadii", self._particle_size)
        
        # 2nd largest inefficiency
        self.mesh.SetInstanceData(self._sim.GetPoints(), self._sim.GetColors())
        self._renderer.DrawInstanced()
        # largest inefficiency
        
        # self._renderer.Draw()
    
    def OnUI(self, dt: DeltaTime = None):
        UI.Begin("Settings")
        
        if self._gravity:
            gravity = glm.vec3(0, -9.8, 0)
        else:
            gravity = glm.vec3()
        
        reset = UI.Button("Reset Simulation")
        if reset:
            self._sim = Simulation(
                    self._particle_number,
                    self._particle_size,
                    self._domain_size,
                    self._friction_coefficient,
                    self._particle_spacing,
                    gravity
                )
        reset = UI.Button("Reset Camera")
        if reset:
                self._camera = Camera()
        
        # Show debug info if true
        if imgui.collapsing_header("Stats", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            time = dt.GetSeconds()
            timems = dt.GetMilliseconds()
            UI.Text(f"Last frame time(ms): {round(timems, 4)}")
            UI.Text(f"Last frame time(s): {round(time, 4)}")

            UI.Text(f"FPS: {round(1/time, 2)}")
        
        if imgui.collapsing_header("Simulation Params", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            self._particle_number, changed = UI.SliderInt("Particle Amount", self._particle_number, 1, 10000)
            if changed:#imgui.is_item_deactivated_after_edit():
                self._sim = Simulation(
                    self._particle_number,
                    self._particle_size,
                    self._domain_size,
                    self._friction_coefficient,
                    self._particle_spacing,
                    gravity
                )
                
            self._gravity, changed = UI.Checkbox("Gravity", self._gravity)
            if changed:
                if self._gravity:
                    self._sim.SetGravity(glm.vec3(0, -9.8, 0))
                else:
                    self._sim.SetGravity(glm.vec3(0, 0, 0))
            
            self._particle_size, changed = UI.SliderFloat("Particle Size", self._particle_size, 0.0005, 1.0)
            if changed:
                self._sim.SetParticleSize(self._particle_size)
                self._sim.SetOptimalSmoothingRadius()
                
            self._particle_spacing, changed = UI.SliderFloat("Particle Spacing", self._particle_spacing, self._particle_size/2, 1.0)
            if imgui.is_item_deactivated_after_edit():
                self._sim = Simulation(
                    self._particle_number,
                    self._particle_size,
                    self._domain_size,
                    self._friction_coefficient,
                    self._particle_spacing,
                    gravity
                )
            
            self._friction_coefficient, changed = UI.SliderFloat("Friction Coefficient", self._friction_coefficient, 0.005, 1.0)
            if changed:
                self._sim.SetFrictionCoefficient(self._friction_coefficient)
            
            self._domain_size, changed = UI.SliderFloat3("Domain Size", self._domain_size, 0.1, 20.0)
            if changed:
                self._sim.SetBoundSize(self._domain_size)
                self._sim.SetOptimalSmoothingRadius()
        
            #self._domain_size, changed = UI.SliderFloat3("Bound Size", self._domain_size, 0, 20.0)
            #if changed:
            #    self._sim.SetBoundSize(self._domain_size)
            # changed, x, y, z = imgui.slider_float3("Bound Size", self._domain_size.x, self._domain_size.y, self._domain_size.z, change_speed=0.1)
            # if imgui.is_item_deactivated_after_edit():
            #     self._domain_size = glm.vec3(x, y, z)
            #     self._sim.SetBoundSize(self._domain_size)
        

                    
        UI.End()
        

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)
               
        self._layer_stack.PushLayer(ParticleFlowLayer(self._window))
