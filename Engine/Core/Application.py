from Engine.Core.Window import *
    
class Application:
    def __init__(self, width = 800, height = 600, title = "ParticleFlow"):
        self._window = Window(width, height, title)

        self._Running = True

    def EndApplication(self):
        self._Running = False

    def Run(self):
        print("Created Application")
        while self._Running and (not self._window.WindowOpen()):
            self._window.OnUpdate()
    
        self._window.CloseWindow()


