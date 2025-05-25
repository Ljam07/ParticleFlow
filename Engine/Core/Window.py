import glfw
from OpenGL.GL import *

class Window:
    def __init__(self, width, height, title):
        self._width = width
        self._height = height
        self._title = title

        self.__CreateWindow()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
    
    @property
    def title(self):
        return self._title
    
    def __CreateWindow(self):
        if not glfw.init():
            return
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        # Create a windowed mode window and its OpenGL context
        self._window = glfw.create_window(self._width, self._height, self._title, None, None)
        if not self._window:
            glfw.terminate()
            return
               
        
        glfw.make_context_current(self._window)
        
        glViewport(0, 0, self._width, self._height)
        glfw.set_framebuffer_size_callback(self._window, self.__FramebufferSizeCallback)
        
        #glClearColor(0.2, 0.3, 0.3, 1.0)
        glClearColor(0.125, 0.125, 0.2, 1.0)

    def __FramebufferSizeCallback(self, window, width, height):
        glViewport(0, 0, width, height)

    def OnUpdate(self, deltaTime = 0):
        # Poll for and process events
        glfw.swap_buffers(self._window)
        glfw.poll_events()
        
    def Clear(self):
        glClear(GL_COLOR_BUFFER_BIT)        


    def WindowOpen(self):
        return not glfw.window_should_close(self._window)
    
    def CloseWindow(self):
        glfw.terminate()
        print("Closed Window")
        
    def GetWindow(self):
        return self._window