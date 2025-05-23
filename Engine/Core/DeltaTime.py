class DeltaTime:
    def __init__(self, time):
        self._time = time

    def GetSeconds(self):
        return self._time
    
    def GetMiliseconds(self):
        return self._time * 1000