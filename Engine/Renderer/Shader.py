from OpenGL.GL import *
from glm import value_ptr
import ctypes
import os

class Shader:
    """
    Loads, compiles, and links a GLSL vertex+fragment shader from files.
    Provides uniform-setting helpers.
    """
    def __init__(self, vertex_path: str, fragment_path: str):
        # Read source
        vertex_src   = self._LoadSource(vertex_path)
        fragment_src = self._LoadSource(fragment_path)

        # Create program handle
        self.handle = glCreateProgram()

        # Compile and attach
        vert = self._CompileShader(vertex_src, GL_VERTEX_SHADER, vertex_path)
        frag = self._CompileShader(fragment_src, GL_FRAGMENT_SHADER, fragment_path)
        glAttachShader(self.handle, vert)
        glAttachShader(self.handle, frag)

        # Link and check
        glLinkProgram(self.handle)
        link_status = glGetProgramiv(self.handle, GL_LINK_STATUS)
        if link_status != GL_TRUE:
            error = glGetProgramInfoLog(self.handle).decode()
            raise RuntimeError(f"Failed to link shader program:\n{error}")

        # We can delete individual shaders once linked
        glDeleteShader(vert)
        glDeleteShader(frag)

    def _LoadSource(self, path: str) -> str:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Shader file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _CompileShader(self, src: str, shader_type: int, path: str) -> int:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, src)
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if status != GL_TRUE:
            error = glGetShaderInfoLog(shader).decode()
            type_name = 'VERTEX' if shader_type == GL_VERTEX_SHADER else 'FRAGMENT'
            raise RuntimeError(f"Error compiling {type_name} shader ({path}):\n{error}")
        return shader

    def Use(self):
        """Bind this shader program for rendering."""
        glUseProgram(self.handle)

    def UploadInt(self, name: str, value: int):
        loc = glGetUniformLocation(self.handle, name)
        if loc != -1:
            glUniform1i(loc, value)

    def UploadFloat(self, name: str, value: float):
        loc = glGetUniformLocation(self.handle, name)
        if loc != -1:
            glUniform1f(loc, value)

    def UploadVec3(self, name: str, vec3):
        loc = glGetUniformLocation(self.handle, name)
        if loc != -1:
            glUniform3f(loc, vec3[0], vec3[1], vec3[2])

    def UploadMat4(self, name: str, mat, transpose=False):
        loc = glGetUniformLocation(self.handle, name)
        if loc == -1:
            return
        # convert glm.mat4 to float* via value_ptr
        ptr = value_ptr(mat)
        glUniformMatrix4fv(loc, 1, GL_TRUE if transpose else GL_FALSE, ptr)

    def __del__(self):
        try:
            glDeleteProgram(self.handle)
        except Exception:
            pass