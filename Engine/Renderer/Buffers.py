# buffers.py
from OpenGL.GL import *
import ctypes

class VertexBuffer:
    """
    Wraps an OpenGL VBO for float data.
    """
    def __init__(self, data: list[float], usage=GL_STATIC_DRAW):
        self.id = glGenBuffers(1)
        array_type = (GLfloat * len(data))
        buf = array_type(*data)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(buf), buf, usage)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def Bind(self): 
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        
    def Unbind(self): 
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
    # def __del__(self): 
    #     glDeleteBuffers(1, [self.id])

class VertexArray:
    """
    Wraps an OpenGL VAO for attribute state.
    """
    def __init__(self):
        self.id = glGenVertexArrays(1)

    def Bind(self):   
        glBindVertexArray(self.id)
        
    def Unbind(self): 
        glBindVertexArray(0)

    def AddAttribute(self, index, size, type, normalized, stride, pointer):
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, size, type, normalized, stride, pointer)

    # def __del__(self): 
    #     glDeleteVertexArrays(1, [self.id])