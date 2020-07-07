from collections import OrderedDict
from enum import Enum
import json


class FittingModels():
    GAUSSIAN_PLUS_LINEAR = "gaussian + linear"
    LORENTZIAN_PLUS_LINEAR = "lorentzian + linear"
    VOIGT_PLUS_LINEAR = "voigt + linear"

fitting_model_types = [FittingModels.GAUSSIAN_PLUS_LINEAR, FittingModels.LORENTZIAN_PLUS_LINEAR, FittingModels.VOIGT_PLUS_LINEAR]


class WavelenghUnit:
    ANGSTROM = "angstrom"
    NANOMETER = "nanometer"

class FluxUnit:
    F_nu = "F_nu"
    F_lambda = "F_lambda"
    AB_magnitude = "AB_magnitude"


class Trace:
    def __init__(self,name=None, x_coords=None, y_coords=None, color="black", linewidth=1, alpha=1):
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.name = name
        self.color = color
        self.linewidth = linewidth
        self.alpha = alpha

    def to_dict(self):
        return vars(self)

    def to_string(self):
        return str(self.to_dict())

class Spectrum:
    def __init__(self,name=None, wavelength=None, flux=None, sky=None, model=None, masks=None, mask_bits=None, wavelength_unit=None, flux_unit=None, flambda=None, catalog=None, ancestors=[]):
        self.name = name
        self.wavelength = wavelength
        self.sky = sky
        self.model=model
        self.masks = masks
        self.mask_bits = mask_bits
        self.wavelength_unit = wavelength_unit
        self.flux_unit = flux_unit
        self.flambda = flambda
        self.catalog = catalog
        self.ancestors = ancestors


    def to_dict(self):
        return vars(self)

    def to_string(self):
        return str(self.to_dict())

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