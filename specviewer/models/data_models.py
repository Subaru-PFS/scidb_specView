from collections import OrderedDict
from enum import Enum
import json
from .base_model import Base
from specviewer import flux as fl
from .enum_models import WavelenghUnit, FluxUnit, Catalogs, SpectrumType, ObjectType




class Spectrum(Base):
    def __init__(self,name="", wavelength=[], flux=[], flux_error=[], masks=[],
                 mask_bits={}, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda,
                 catalog=None, spectrum_type=SpectrumType.OBJECT, color="black", linewidth=1, alpha=1):

        def __init__(self):
            super().__init__()

        if wavelength_unit not in WavelenghUnit.get_list():
            raise Exception("Parameter wavelength_unit must take a value from WavelenghUnit class: " + str(WavelenghUnit.get_list()))

        if flux_unit not in FluxUnit.get_list():
            raise Exception("Parameter flux_unit must take a value from FluxUnit class: " + str(FluxUnit.get_list()))

        self.name = name
        self.wavelength = wavelength
        self.flux = flux
        self.flux_error = flux_error
        self.masks = masks
        self.mask_bits = mask_bits
        self.wavelength_unit = wavelength_unit
        self.flux_unit = flux_unit
        self.catalog = catalog
        self.spectrum_type = spectrum_type
        self.color = color,
        self.linewidth = linewidth,
        self.alpha = alpha



class Trace(Spectrum):
    def __init__(self,name="", wavelength=[], flux=[], flux_error=[], masks={},
                 mask_bits={}, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda,
                 catalog=Catalogs.DEFAULT_CAT, spectrum_type=SpectrumType.OBJECT, color="black", linewidth=1, alpha=1,
                 flambda=[],
                 flambda_error=[],
                 is_visible=True,
                 show_error=False,
                 ancestors=[],
                 ):

        super().__init__(name, wavelength, flux, flux_error, masks,mask_bits, wavelength_unit, flux_unit,
                 catalog, spectrum_type, color, linewidth, alpha)

        self.flambda = flambda
        self.flambda_error = flambda_error
        self.is_visible = is_visible
        self.show_error = show_error
        self.ancestors = ancestors
        self.curveNumber = None

        def from_spectrum(spectrum, visible = True, ancestors = ancestors):
            for key,value in spectrum.to_dict().items():
                self.__dict__[key] = value

            self.flambda = fl.convert_flux(spectrum.flux, spectrum.wavelength, spectrum.flux_unit, FluxUnit.F_lambda, WavelenghUnit.ANGSTROM)
            self.visible = visible
            self.ancestors = ancestors

        def to_spectrum(self):
            return Spectrum().from_dict(self.__dict__)



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