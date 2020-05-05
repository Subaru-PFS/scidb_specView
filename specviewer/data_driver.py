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


def get_spectrum_from_fits(hdulist, name):

    object_type = get_object_type(hdulist)
    spectrum = Spectrum()
    spectrum.name = name

    if object_type == object_types["ZObject"]:
        coaddData =1 # the index of Coadd data in the HDU list
        zData =3 # index of absorption and emission line data in HDU list
        c=hdulist[coaddData].data
        z=hdulist[zData].data
        # the name of the data unit can be found on the official SDSS DR webpage

        spectrum.wavelength = [float(10**lam) for lam in c['loglam']]
        spectrum.flux = [float(x) for x in c['flux']]
        spectrum.sky = [float(x) for x in c['sky']]
        spectrum.model = [float(x) for x in c['model']]

    elif object_type == object_types["PfsObject"]:
        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data

        spectrum.wavelength = [float(x) for x  in c['lambda']]
        spectrum.flux = [float(x) for x  in c['flux']]
        # adding flux variance
        #flux = c['fluxvariance']


    elif object_type == object_types["Lam1D"]:

        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data
        coaddData =1 # the index of the HDU that contains the wavelength
        l=hdulist[coaddData].data

        for ind in range(len(c['MODELFLUX'])):

            lam = [float(x) for x in l['WAVELENGTH']]
            # adding flux
            flux = [0.0 for s in range(len(l['WAVELENGTH']))]

    else:
        raise Exception("Unknown data model for input file.")

    return spectrum
