import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
from SpectrumViewer import spectral_lines_info
import SpectrumViewer.dataDriver as driver
from SpectrumViewer.data_models import Medium, Spectrum, SpectrumLineGrid, SpectrumLine
import SpectrumViewer
from collections import OrderedDict
import matplotlib.text
import numpy as np
import matplotlib.transforms as transforms
import copy
from . import controller as c
import json
import datetime

from . import data_models



class ApplicationData:

    def __init__(self):
        self.traces = OrderedDict()
        self.spectral_lines = OrderedDict()
        self.trace_dependencies = OrderedDict()
        self.rectangle_data = None

    def get_traces(self):
        return self.traces

    def get_trace(self,name):
        return self.traces[name]

    def get_spectral_lines(self,name):
        return self.spectral_lines[name]

    def add_trace(self, name, trace):
        if name in self.traces:
            raise Exception("Trace " + name + " already exists")
        self.traces[name] = trace

    def add_spectral_lines(self):
        pass

    def add_rectangle_data(self):
        pass

    def add_trace_dependency(self):
        pass
