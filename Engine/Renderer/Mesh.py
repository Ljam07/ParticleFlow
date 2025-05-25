from Engine.Renderer.Buffers import *
from OpenGL.GL import *
import ctypes

import math

class Mesh:
    """
    Simple mesh with a position-only VBO and VAO.
    """
    def __init__(self, vertices: list[float]):
        self.vbo = VertexBuffer(vertices)
        self.vao = VertexArray()
        stride = 3 * ctypes.sizeof(ctypes.c_float)
        self.vao.Bind()
        self.vbo.Bind()
        self.vao.AddAttribute(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        self.vbo.Unbind()
        self.vao.Unbind()
        self.vertex_count = len(vertices) // 3

    def Bind(self):   
        self.vao.Bind()
    
    def Unbind(self): 
        self.vao.Unbind()
    
    def __del__(self): 
        del self.vbo; del self.vao
        
    @staticmethod
    def generate_uv_sphere(stacks: int, slices: int, radius: float = 1.0) -> list[float]:
        """
        Generate a UV sphere as a flat list of triangle vertices (x, y, z).

        stacks: number of horizontal rings (latitude)
        slices: number of vertical segments (longitude)
        radius: sphere radius
        """
        vertices = []
        # Precompute sin/cos of the angles
        for i in range(stacks):
            phi0 = math.pi * (i    ) / stacks     - math.pi/2  # from -π/2 to +π/2
            phi1 = math.pi * (i + 1) / stacks     - math.pi/2
            y0 = math.sin(phi0) * radius
            y1 = math.sin(phi1) * radius
            r0 = math.cos(phi0) * radius
            r1 = math.cos(phi1) * radius

            for j in range(slices):
                theta0 = 2 * math.pi * (j    ) / slices
                theta1 = 2 * math.pi * (j + 1) / slices
                x00 = math.cos(theta0) * r0; z00 = math.sin(theta0) * r0
                x01 = math.cos(theta1) * r0; z01 = math.sin(theta1) * r0
                x10 = math.cos(theta0) * r1; z10 = math.sin(theta0) * r1
                x11 = math.cos(theta1) * r1; z11 = math.sin(theta1) * r1

                # Two triangles per quad (skip degenerate at poles)
                # Triangle 1
                vertices += [x00, y0, z00]
                vertices += [x10, y1, z10]
                vertices += [x11, y1, z11]
                # Triangle 2
                vertices += [x00, y0, z00]
                vertices += [x11, y1, z11]
                vertices += [x01, y0, z01]

        return vertices