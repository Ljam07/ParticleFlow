from Engine.Core.Application import Application

class App(Application):
    def __init__(self, width=800, height=600, title="ParticleFlow"):
        super().__init__(width, height, title)