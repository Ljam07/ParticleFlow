from OpenGL.GL import *
import ctypes

class Renderer:
    def __init__(self):
        print("Created Renderer")
        self._setup_vertices()
        self._setup_shaders()
        self._setup_buffers()

    def _setup_vertices(self):
        # Triangle vertices
        self.vertices = [
            -0.5, -0.5, 0.0,  # Bottom left
             0.5, -0.5, 0.0,  # Bottom right
             0.0,  0.5, 0.0   # Top
        ]

    def _setup_shaders(self):
        # Vertex shader
        vertex_src = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        void main() {
            gl_Position = vec4(aPos, 1.0);
        }
        """

        # Fragment shader
        fragment_src = """
        #version 330 core
        out vec4 FragColor;
        void main() {
            FragColor = vec4(1.0, 0.4, 0.2, 1.0);
        }
        """

        # Compile shaders
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, vertex_src)
        glCompileShader(self.vertex_shader)
        self._check_compile_errors(self.vertex_shader, "VERTEX")

        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, fragment_src)
        glCompileShader(self.fragment_shader)
        self._check_compile_errors(self.fragment_shader, "FRAGMENT")

        # Link program
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)
        glLinkProgram(self.shader_program)
        self._check_link_errors(self.shader_program)

        # Clean up shaders (no longer needed after linking)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

    def _setup_buffers(self):
        # Convert vertices to ctypes array
        array_type = GLfloat * len(self.vertices)
        vertex_data = array_type(*self.vertices)

        # VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # VBO
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertex_data), vertex_data, GL_STATIC_DRAW)

        # Vertex attribute pointer
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * ctypes.sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Unbind VAO
        glBindVertexArray(0)

    def draw(self):
        glUseProgram(self.shader_program)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)

    def _check_compile_errors(self, shader, shader_type):
        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            info_log = glGetShaderInfoLog(shader)
            print(f"ERROR::{shader_type}::SHADER_COMPILATION_ERROR\n{info_log.decode()}")

    def _check_link_errors(self, program):
        success = glGetProgramiv(program, GL_LINK_STATUS)
        if not success:
            info_log = glGetProgramInfoLog(program)
            print(f"ERROR::PROGRAM::LINKING_ERROR\n{info_log.decode()}")
        else:
            print("Successful linking")
