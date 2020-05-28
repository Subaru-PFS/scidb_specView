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
from specviewer.data_models import WavelenghUnit, FluxUnit
#from SpectrumViewer.data_models import *
import math
from collections.abc import Iterable
from collections import OrderedDict
import numpy as np
import os
from .flux import fnu_to_flambda

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
        spectrum.flux = [1.0*10**-17*float(x) for x in c['flux']]
        spectrum.model = [1.0*10**-17*float(x) for x in c['model']]
        spectrum.wavelength_unit = WavelenghUnit.ANGSTROM
        spectrum.flux_unit = FluxUnit.F_lambda
        if np.sum(np.asarray(spectrum.flux) <= 0, axis=0):
            spectrum.flambda = [f for f in spectrum.flux]

        spectrum_list.append(spectrum)


        if add_sky:
            spectrum_sky = Spectrum()
            spectrum_sky.name = name + "_sky"
            spectrum_sky.wavelength = wavelength
            spectrum_sky.flux = [1.0*10**-17*float(x) for x in c['sky']]
            spectrum_sky.wavelength_unit = WavelenghUnit.ANGSTROM
            spectrum_sky.flux_unit = FluxUnit.F_lambda
            if np.sum(np.asarray(spectrum_sky.flux) <= 0, axis=0):
                spectrum_sky.flambda = [f for f in spectrum_sky.flux]

            spectrum_list.append(spectrum_sky)
        if add_error:
            spectrum_error = Spectrum()
            spectrum_error.name = name + "_error"
            spectrum_error.wavelength = wavelength
            spectrum_error.flux = [1.0*10**-17*np.sqrt(float(x)) for x in c['ivar']]
            spectrum_error.wavelength_unit = WavelenghUnit.ANGSTROM
            spectrum_error.flux_unit = FluxUnit.F_lambda
            if np.sum(np.asarray(spectrum_sky.flux) <= 0, axis=0):
                spectrum_sky.flambda = [f for f in spectrum_sky.flux]

            spectrum_list.append(spectrum_error)
        if add_model:
            spectrum_model = Spectrum()
            spectrum_model.name = name + "_model"
            spectrum_model.wavelength = wavelength
            spectrum_model.flux = [1.0*10**-17*float(x) for x in c['model']]
            spectrum_model.wavelength_unit = WavelenghUnit.ANGSTROM
            spectrum_model.flux_unit = FluxUnit.F_lambda
            if np.sum(np.asarray(spectrum_model.flux) <= 0, axis=0):
                spectrum_model.flambda = [f for f in spectrum_model.flux]

            spectrum_list.append(spectrum_model)

        return spectrum_list

    elif object_type == object_types["PfsObject"]:
        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data
        spectrum = Spectrum()
        spectrum.name = name
        spectrum.wavelength = [10.0*float(x) for x  in c['lambda']]
        # converted from Jy to Flambda
        spectrum.flux = [fnu_to_flambda(fnu*10**-23, spectrum.wavelength[i], WavelenghUnit.ANGSTROM) for (i, fnu) in
                             enumerate(c['flux'])]

        spectrum.wavelength_unit = WavelenghUnit.ANGSTROM
        spectrum.flux_unit = FluxUnit.F_lambda
        if np.sum(np.asarray(spectrum.flux) <= 0, axis=0):
            spectrum.flambda = [f for f in spectrum.flux]

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
            spectrum.wavelength = [10.0*float(x) for x in l['WAVELENGTH']]
            # adding flux
            spectrum.flux = [0.0 for s in range(len(l['WAVELENGTH']))]
            spectrum_list.append(spectrum)

        return spectrum_list

    else:
        raise Exception("Unknown data model for input file.")

