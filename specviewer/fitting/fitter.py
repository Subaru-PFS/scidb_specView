#from astropy.io import fits
#from astropy.convolution import convolve, Gaussian1DKernel, Box1DKernel, CustomKernel
#from astropy.convolution.kernels import Model1DKernel
#from ..models.enum_models import WavelenghUnit, FluxUnit, SmoothingKernels, SpectrumType
#from ..models.data_models import Trace
from astropy.modeling import Fittable1DModel

from astropy.modeling import models, fitting
from specviewer.models.base_model import Base
import numpy as np

class FittingModels(Base):
    GAUSSIAN_PLUS_LINEAR = "gaussian + linear"
    LORENTZIAN_PLUS_LINEAR = "lorentzian + linear"
    VOIGT_PLUS_LINEAR = "voigt + linear"
    CUSTOM = "custom"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(FittingModels) if callable(getattr(FittingModels, func))}
        return [v for k,v in FittingModels.__dict__.items() if k not in methods and not k.startswith('__')]

fitting_models_list = FittingModels.get_list()
default_fitting_models = [FittingModels.GAUSSIAN_PLUS_LINEAR, FittingModels.LORENTZIAN_PLUS_LINEAR, FittingModels.VOIGT_PLUS_LINEAR]


class ModelFitter(Base):
    def __init__(self, model=None, fitter=None, model_type=FittingModels.CUSTOM):
        self.model = model
        self.fitter = fitter
        self.model_type = model_type
        self.fitted_model = None

    def set_model_fitter(self, model, fitter):
        self.model = model
        self.fitter = fitter
        self.fitted_model = None


    def get_fit(self, x, y, weights=None):
        self.fitted_model = self.fitter(self.model, x, y, weights=weights)
        fitting_parameters = {x: y for (x, y) in zip(self.fitted_model.param_names, self.fitted_model.parameters)}
        parameter_errors = np.sqrt(np.diag(self.fitter.fit_info['param_cov'])) if self.fitter.fit_info['param_cov'] is not None else None
        return {'fitted_parameters':fitting_parameters,'parameter_errors':parameter_errors}

    def get_fitted_model(self):
        return self.fitted_model
