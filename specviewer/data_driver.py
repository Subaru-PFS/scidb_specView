#load SDSS into workable object
from astropy.io import fits
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
from urllib.parse import urlparse
import SpectrumViewer.CoaddObj as Coadd
import SpectrumViewer.ZObj as Z
import SpectrumViewer.data_models as data_models
from SpectrumViewer.data_models import Medium, Spectrum, SpectrumLineGrid
import SpectrumViewer

#from SpectrumViewer.data_models import *
import math
from collections.abc import Iterable
from collections import OrderedDict
import numpy as np
import os

from .data_models import Trace, Spectrum

object_types = {"PfsObject":"PfsObject", "ZObject":"ZObject","Lam1D":"Lam1D"}

hdu_names = {}
hdu_names["PfsObject"] = ["PRIMARY", "FLUX", "FLUXTBL", "COVAR", "COVAR2", "MASK", "SKY", "CONFIG"]
hdu_names["ZObject"] = ["PRIMARY", "COADD", "SPECOBJ", "SPZLINE"]
hdu_names["Lam1D"] = ["PRIMARY", "LAMBDA_SCALE", "ZCANDIDATES", "ZPDF", "ZLINES"]


def get_object_type(hdulist):

    for hdu_name in hdu_names:
            if len(hdulist) == len(hdu_names[hdu_name]):
                is_model = True
                for i in range(len(hdulist)):
                    if hdulist[i].name.upper() != hdu_names[hdu_name][i].upper():
                        is_model = False

                if is_model:
                    return hdu_name

    raise Exception("Unknown data model for input file.")


def get_spectrum_list_from_fits(hdulist, name, add_sky=False, add_model=False, add_error=False):

    spectrum_list = []

    object_type = get_object_type(hdulist)

    if object_type == object_types["ZObject"]:
        coaddData =1 # the index of Coadd data in the HDU list
        zData =3 # index of absorption and emission line data in HDU list
        c=hdulist[coaddData].data
        z=hdulist[zData].data
        # the name of the data unit can be found on the official SDSS DR webpage

        spectrum = Spectrum()
        spectrum.name = name
        wavelength = [float(10**lam) for lam in c['loglam']]
        spectrum.wavelength = wavelength
        spectrum.flux = [float(x) for x in c['flux']]
        spectrum.model = [float(x) for x in c['model']]
        spectrum_list.append(spectrum)

        if add_sky:
            spectrum_sky = Spectrum()
            spectrum_sky.name = name + "_sky"
            spectrum_sky.wavelength = wavelength
            spectrum_sky.flux = [float(x) for x in c['sky']]
            spectrum_list.append(spectrum_sky)
        if add_error:
            spectrum_error = Spectrum()
            spectrum_error.name = name + "_error"
            spectrum_error.wavelength = wavelength
            spectrum_error.flux = [np.sqrt(float(x)) for x in c['ivar']]
            spectrum_list.append(spectrum_error)
        if add_model:
            spectrum_model = Spectrum()
            spectrum_model.name = name + "_model"
            spectrum_model.wavelength = wavelength
            spectrum_model.flux = [float(x) for x in c['model']]
            spectrum_list.append(spectrum_model)

        return spectrum_list

    elif object_type == object_types["PfsObject"]:
        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data
        spectrum = Spectrum()
        spectrum.name = name
        spectrum.wavelength = [float(x) for x  in c['lambda']]
        spectrum.flux = [float(x) for x  in c['flux']]
        # adding flux variance
        #flux = c['fluxvariance']
        spectrum_list.append(spectrum)
        return spectrum_list

    elif object_type == object_types["Lam1D"]:

        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data
        coaddData =1 # the index of the HDU that contains the wavelength
        l=hdulist[coaddData].data

        for ind in range(len(c['MODELFLUX'])):
            spectrum = Spectrum()
            spectrum.name = name + "_" + str(ind)
            spectrum.wavelength = [float(x) for x in l['WAVELENGTH']]
            # adding flux
            spectrum.flux = [0.0 for s in range(len(l['WAVELENGTH']))]
            spectrum_list.append(spectrum)

        return spectrum_list

    else:
        raise Exception("Unknown data model for input file.")

