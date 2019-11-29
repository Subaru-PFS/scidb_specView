
import bisect
from collections import OrderedDict

class SpecModel:

    def locateLmb(self,numbers,lmb):
        if lmb>numbers[0] and lmb<numbers[-1]:
            return bisect.bisect_left(numbers, lmb)#not sure if -1 or not
        else:
            return False

    def __init__(self,streams,spectral_lines):

        self.streams = streams
        self.spectral_lines = spectral_lines

    def getStream(self,name):
        return self.streams[name]

    def get_spectral_lines(self,name):
        return self.spectral_lines[name]
