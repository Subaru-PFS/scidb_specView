import numpy as np
from .data_models import WavelenghUnit

#https://en.wikipedia.org/wiki/AB_magnitude

def fnu_to_abmag(fnu):
    if fnu <= 0:
        return None
    else:
        return -2.5 * np.log10(fnu) - 48.60

def fnu_to_flambda(fnu, lam, wavelength_unit):
    if wavelength_unit == WavelenghUnit.NANOMETER:
        lam = lam * 10.0
    return 1.0 / (10 ** -23 * 3.33564095 * 10 ** 4 * (lam) ** 2) * fnu

def flambda_to_fnu(flam, lam, wavelength_unit):
    if wavelength_unit == WavelenghUnit.NANOMETER:
        lam = lam * 10.0
    return 10 ** -23 * 3.33564095 * 10 ** 4 * (lam) ** 2 * flam

def flambda_to_abmag(flam,lam, wavelength_unit):
    return fnu_to_abmag(flambda_to_fnu(flam,lam,wavelength_unit))

def abmag_to_fnu(abmag):
    return 10.0 ** ((abmag + 48.60) / -2.5)

def abmag_to_flambda(abmag,lam, wavelength_unit):
    return fnu_to_flambda(abmag_to_fnu(abmag),lam,wavelength_unit)