from .base_model import Base


class ObjectType(Base):
    GALAXY='GALAXY'
    STAR='STAR'
    QSO='QSO'
    DEFAULT="DEFAULT"
    UNKNOWN="UNKNOWN"
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(ObjectType) if callable(getattr(ObjectType, func))}
        return [v for k,v in ObjectType.__dict__.items() if k not in methods and not k.startswith('__')]

class SpectrumType(Base):
    OBJECT="OBJECT"
    OBJECT_PRECURSOR="OBJECT_PRECURSOR"
    SKY="SKY"
    MODEL="MODEL"
    ERROR="ERROR"
    FIT = "FIT"
    DEFAULT="DEFAULT"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(SpectrumType) if callable(getattr(SpectrumType, func))}
        return [v for k,v in SpectrumType.__dict__.items() if k not in methods and not k.startswith('__')]


class FittingModels(Base):
    GAUSSIAN_PLUS_LINEAR = "gaussian + linear"
    LORENTZIAN_PLUS_LINEAR = "lorentzian + linear"
    VOIGT_PLUS_LINEAR = "voigt + linear"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(FittingModels) if callable(getattr(FittingModels, func))}
        return [v for k,v in FittingModels.__dict__.items() if k not in methods and not k.startswith('__')]

fitting_models_list = FittingModels.get_list()

class SmoothingKernels(Base):
    GAUSSIAN1D = "Gaussian1DKernel"
    Box1D = "Box1DKernel"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(SmoothingKernels) if callable(getattr(SmoothingKernels, func))}
        return [v for k,v in SmoothingKernels.__dict__.items() if k not in methods and not k.startswith('__')]

smoothing_kernels_list = SmoothingKernels.get_list()

class Catalogs(Base):
    SDSS = "SDSS"
    PFS = "PFS"
    DEFAULT_CAT = "DEFAULT_CAT"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(Catalogs) if callable(getattr(Catalogs, func))}
        return [v for k,v in Catalogs.__dict__.items() if k not in methods and not k.startswith('__')]

catalogs_list = Catalogs.get_list()


class WavelenghUnit(Base):
    ANGSTROM = "angstrom"
    NANOMETER = "nanometer"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(WavelenghUnit) if callable(getattr(WavelenghUnit, func))}
        return [v for k,v in WavelenghUnit.__dict__.items() if k not in methods and not k.startswith('__')]

wavelength_units_list = WavelenghUnit.get_list()

class FluxUnit(Base):
    F_nu = "F_nu"
    F_lambda = "F_lambda"
    AB_magnitude = "AB_magnitude"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(FluxUnit) if callable(getattr(FluxUnit, func))}
        return [v for k,v in FluxUnit.__dict__.items() if k not in methods and not k.startswith('__')]

flux_units_list = FluxUnit.get_list()