from Engine.Renderer.Buffers import *
from OpenGL.GL import *
import ctypes

import math
import glm

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
        
    def SetInstanceData(self,
                    points: list[glm.vec3],
                    colors: list[glm.vec3]):
        # 1) One instance per vec3 in points
        count = len(points)
        assert len(colors) == count

        # 2) Clean up old buffer if present
        if hasattr(self, '_inst_vbo'):
            glDeleteBuffers(1, [self._inst_vbo])
        self._inst_vbo = glGenBuffers(1)

        # 3) Prepare interleaved float data: 3 + 3 + 1 = 7 floats per instance
        floats_per = 6
        total = count * floats_per
        ArrayType = GLfloat * total

        inter = []
        for i in range(count):
            # expand each glm.vec3 into its x,y,z
            inter += [points[i].x, points[i].y, points[i].z]
            inter += [colors[i].x, colors[i].y, colors[i].z]

        buf = ArrayType(*inter)

        # 4) Upload to GPU
        glBindBuffer(GL_ARRAY_BUFFER, self._inst_vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     ctypes.sizeof(buf),
                     buf,
                     GL_DYNAMIC_DRAW)

        # 5) Configure per-instance vertex attributes
        self.vao.Bind()
        stride = floats_per * ctypes.sizeof(ctypes.c_float)

        # aInstancePoint → location=1, vec3 at offset 0
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)

        # aInstanceColor → location=2, vec3 at offset 3*sizeof(float)
        off = 3 * ctypes.sizeof(ctypes.c_float)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(off))
        glVertexAttribDivisor(2, 1)

        # aInstanceRadius → location=3, float at offset 6*sizeof(float)
        

        self.vao.Unbind()
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # 6) Store count for instanced draw
        self.instance_count = count

    @staticmethod
    def GenerateUVSphere(stacks: int, slices: int, radius: float = 1.0) -> list[float]:
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