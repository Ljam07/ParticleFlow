# renderer.py
from Engine.Renderer.Shader import Shader
from Engine.Renderer.Mesh import Mesh
from OpenGL.GL import *

class Renderer:
    """
    Issues draw calls for a given shader and mesh.
    """
    def __init__(self, shader: Shader, mesh: Mesh):
        self.shader = shader
        self.mesh = mesh

    def Draw(self):
        self.shader.Use()
        self.mesh.Bind()
        glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count)
        self.mesh.Unbind()

    def DrawInstanced(self):
        count = getattr(self.mesh, 'instance_count', 0)
        if count <= 0:
            return
        
        self.shader.Use()
        self.mesh.Bind()
        glDrawArraysInstanced(GL_TRIANGLES, 0, self.mesh.vertex_count, count)
        self.mesh.Unbind()