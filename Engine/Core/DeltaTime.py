class DeltaTime:
    def __init__(self, time):
        self._time = time

    def GetSeconds(self):
        return self._time
    
    def GetMilliseconds(self):
        return self._time * 1000