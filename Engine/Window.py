import glfw

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
        
        # Create a windowed mode window and its OpenGL context
        self._window = glfw.create_window(self._width, self._height, self._title, None, None)
        if not self._window:
            glfw.terminate()
            return
        
        glfw.make_context_current(self._window)

    def OnUpdate(self, deltaTime = 0):
        glfw.swap_buffers(self._window)

        # Poll for and process events
        glfw.poll_events()

    def WindowOpen(self):
        return glfw.window_should_close(self._window)
    
    def CloseWindow(self):
        glfw.terminate()
        print("Closed Window")