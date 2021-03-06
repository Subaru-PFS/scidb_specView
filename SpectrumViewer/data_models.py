from collections import OrderedDict
from enum import Enum



class Spectrum:
    def __init__(self,x_coords=None, y_coords=None, name=None, color="black", linewidth=1, alpha=1):
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.name = name
        self.color = color
        self.linewidth = linewidth
        self.alpha = alpha


class SpectrumLine:
    def __init__(self, lambda1=None, lambda2=None, name=None, medium=None, color="lightblue", linewidth=1, alpha=0.3):
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.name = name
        if medium is None:
            medium = Medium.AIR
        self.medium = medium
        self.color = color
        self.linewidth = linewidth
        self.alpha = alpha




class Medium(Enum):
        AIR = 1
        VACUUM = 2

class RectangleBoundaries:
    def __init__(self,x1=None,y1=None,x2=None,y2=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return "RectangleBoundaries({x1: "+str(self.x1) +", y1: "+str(self.y1)+", x2: "+str(self.x2)+", y2: "+str(self.y2) +"})"
    def __repr__(self):
        return "SpectrumViewer.data_models.RectangleBoundaries("+str(self.x1) +", "+str(self.y1)+", "+str(self.x2)+", "+str(self.y2) +"}>"

class SpectrumLineGrid:
    def __init__(self, spectrum_line_grid=None):
        if spectrum_line_grid is None:
            self.grid = OrderedDict()
        else:
            self.grid = spectrum_line_grid

    def add_line(self, spectrum_line, spectrum_line_name):
        self.grid[spectrum_line_name] = spectrum_line

    def remove_line(self, spectrum_line_name):
        self.grid.pop(spectrum_line_name)


def getter_setter_gen(name, type_):
    def getter(self):
        return getattr(self, "__" + name)
    def setter(self, value):
        if not isinstance(value, type_):
            raise TypeError("%s attribute must be set to an instance of %s" % (name, type_))
        setattr(self, "__" + name, value)
    return property(getter, setter)

def auto_attr_check(cls):
    new_dct = {}
    for key, value in cls.__dict__.items():
        if isinstance(value, type):
            value = getter_setter_gen(key, value)
        new_dct[key] = value
    # Creates a new class, using the modified dictionary as the class dict:
    return type(cls)(cls.__name__, cls.__bases__, new_dct)