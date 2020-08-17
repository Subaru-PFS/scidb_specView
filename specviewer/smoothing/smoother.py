from specviewer.models.base_model import Base
from astropy.convolution import convolve, Gaussian1DKernel, Box1DKernel, CustomKernel
from astropy.convolution.kernels import Model1DKernel
from astropy.modeling import Fittable1DModel
import numpy as np

class SmoothingKernels(Base):
    GAUSSIAN1D = "Gaussian"
    Box1D = "Box"
    CUSTOM = "Custom"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_list():
        methods = {func for func in dir(SmoothingKernels) if callable(getattr(SmoothingKernels, func))}
        return [v for k,v in SmoothingKernels.__dict__.items() if k not in methods and not k.startswith('__')]

smoothing_kernels_list = SmoothingKernels.get_list()
default_smoothing_kernels = [SmoothingKernels.GAUSSIAN1D, SmoothingKernels.Box1D]



class Smoother():
    def __init__(self):
        self.kernel_func=Gaussian1DKernel(int(5))
        self.kernel_func_type=SmoothingKernels.GAUSSIAN1D

    def set_smoothing_kernel(self, kernel=None, kernel_width=None, custom_array_kernel=None, custom_kernel_function=None, function_array_size=21):
        #if custom_kernel_array is None and custom_kernel_function is None:

        if custom_array_kernel is not None:
            custom_kernel_array = np.array([i for i in custom_array_kernel])
            self.kernel_func = CustomKernel(custom_kernel_array)
            self.kernel_func_type = SmoothingKernels.CUSTOM

        elif custom_kernel_function is not None:
            if not isinstance(custom_kernel_function, Fittable1DModel):
                raise Exception("custom_kernel_function must be an instance of astropy.modeling.Fittable1DModel")
            self.kernel_func = Model1DKernel(custom_kernel_function, x_size=function_array_size)
            self.kernel_func_type = SmoothingKernels.CUSTOM

        elif kernel in default_smoothing_kernels:
            if kernel == SmoothingKernels.GAUSSIAN1D:
                self.kernel_func = Gaussian1DKernel(int(kernel_width))
                self.kernel_func_type = SmoothingKernels.GAUSSIAN1D
            elif kernel == SmoothingKernels.Box1D:
                self.kernel_func = Box1DKernel(int(kernel_width))
                self.kernel_func_type = SmoothingKernels.Box1D
            else:
                raise Exception("Unsupported smoothing kernel " + str(kernel))

        else:
            raise Exception("Problem while setting the smoothing kernel")


    def get_smoothed_flux(self, flux):
        smoothed_flux = convolve(flux, self.kernel_func)
        return smoothed_flux