from collections import OrderedDict


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
