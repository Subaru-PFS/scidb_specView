#load SDSS into workable object
from astropy.io import fits
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
from urllib.parse import urlparse
import SpectrumViewer.CoaddObj as Coadd
import SpectrumViewer.ZObj as Z
import SpectrumViewer.data_models as data_models
#from spectrumviewer.data_models import Medium, Spectrum, SpectrumLineGrid
import SpectrumViewer
from specviewer.data_models import Spectrum, WavelenghUnit, FluxUnit
#from SpectrumViewer.data_models import *
import math
from collections.abc import Iterable
from collections import OrderedDict
import numpy as np
import os
from .flux import fnu_to_flambda
import json
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

#http://www.sdss3.org/dr8/algorithms/bitmask_sppixmask.php

sdss_mask_bits_array = [
['NOPLUG', 	0, 'Fiber not listed in plugmap file'],
['BADTRACE', 	1, 'Bad trace from routine TRACE320CRUDE'],
['BADFLAT', 	2, 'Low counts in fiberflat'],
['BADARC', 	3, 'Bad arc solution'],
['MANYBADCOLUMNS', 	4, 'More than 10% of pixels are bad columns'],
['MANYREJECTED',	5, 'More than 10% of pixels are rejected in extraction'],
['LARGESHIFT', 	6, 'Large spatial shift between flat and object position'],
['BADSKYFIBER', 	7, 'Sky fiber shows extreme residuals'],
['NEARWHOPPER', 	8, 'Within 2 fibers of a whopping fiber (exclusive)'],
['WHOPPER', 	9, 'Whopping fiber, with a very bright source.'],
['SMEARIMAGE', 	10, 'Smear available for red and blue cameras'],
['SMEARHIGHSN', 	11, 'S/N sufficient for full smear fit'],
['SMEARMEDSN', 	12, 'S/N only sufficient for scaled median fit'],
['NEARBADPIXEL', 	16, 'Bad pixel within 3 pixels of trace.'],
['LOWFLAT', 	17, 'Flat field less than 0.5'],
['FULLREJECT', 	18, 'Pixel fully rejected in extraction (INVVAR=0)'],
['PARTIALREJECT', 	19, 'Some pixels rejected in extraction'],
['SCATTEREDLIGHT', 	20, 'Scattered light significant'],
['CROSSTALK', 	21, 'Cross-talk significant'],
['NOSKY', 	22, 'Sky level unknown at this wavelength (INVVAR=0)'],
['BRIGHTSKY', 	23, 'Sky level > flux + 10*(flux_err) AND sky > 1.25 * median(sky,99 pixels)'],
['NODATA', 	24, 'No data available in combine B-spline (INVVAR=0)'],
['COMBINEREJ', 	25, 'Rejected in combine B-spline'],
['BADFLUXFACTOR', 	26, 'Low flux-calibration or flux-correction factor'],
['BADSKYCHI', 	27, 'Relative χ2 > 3 in sky residuals at this wavelength'],
['REDMONSTER', 	28, 'Contiguous region of bad χ2 in sky residuals (with threshhold of relative χ2 > 3).']
]

def get_mask_id(catalog, name, bit):
    return catalog + " " + name + " " + str(bit)

sdss_mask_bits = { get_mask_id("SDSS",mb[0],mb[1]): {'bit':mb[1], 'catalog':'SDSS', 'name':mb[0], 'description':mb[2]} for mb in sdss_mask_bits_array}



def create_mask(mask_array, wavelength_array):

    mask = {}
    mask_value =  mask_array[0]
    mask[mask_value] = [[0,0]]

    for i in range(1,len(wavelength_array),1):
        new_mask_value = mask_array[i]

        if new_mask_value == mask_value:
            mask[mask_value][-1][1] = i
        else:
            if new_mask_value not in mask:
                mask[new_mask_value] = [[i,i]]
            else:
                arr = mask[new_mask_value]
                arr.append([i, i])
                mask[new_mask_value] = arr

            mask_value = new_mask_value

    return mask

def get_spectrum_list_from_fits(hdulist, name, add_sky=False, add_model=False, add_error=False, add_masks=False):

    spectrum_list = []

    object_type = get_object_type(hdulist)

    if object_type == object_types["ZObject"]:
        coaddData =1 # the index of Coadd data in the HDU list
        zData =3 # index of absorption and emission line data in HDU list
        c=hdulist[coaddData].data
        z=hdulist[zData].data
        # the name of the data unit can be found on the official SDSS DR webpage

        #note: alwasys convert data types to native python types, not numpy types. The reason is that everything has
        # to be serialized as json, and numpy objects cannot be automatically serialized as such.

        spectrum = Spectrum()
        spectrum.catalog = "SDSS"
        spectrum.name = name
        wavelength = [float(10**lam) for lam in c['loglam']]
        spectrum.wavelength = wavelength
        spectrum.flux = [1.0*10**-17*float(x) for x in c['flux']]
        spectrum.model = [1.0*10**-17*float(x) for x in c['model']]
        spectrum.wavelength_unit = WavelenghUnit.ANGSTROM
        spectrum.flux_unit = FluxUnit.F_lambda
        if np.sum(np.asarray(spectrum.flux) <= 0, axis=0):
            spectrum.flambda = [f for f in spectrum.flux]

        if add_masks:
            and_mask = create_mask([int(m) for m in c['and_mask']], wavelength)
            or_mask = create_mask([int(m) for m in c['or_mask']], wavelength)
            #spectrum.masks = json.dumps({'and_mask': and_mask, 'or_mask': or_mask})
            spectrum.masks = {'and_mask': and_mask, 'or_mask': or_mask}
            spectrum.mask_bits = sdss_mask_bits
        else:
            spectrum.masks = None

        spectrum_list.append(spectrum)


        if add_sky:
            spectrum_sky = Spectrum()
            spectrum.catalog = "SDSS"
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
            spectrum_error.catalog = "SDSS"
            spectrum_error.name = name + "_error"
            spectrum_error.wavelength = wavelength
            spectrum_error.flux = [1.0*10**-17*np.sqrt(float(1.0/x)) for x in c['ivar']]
            spectrum_error.wavelength_unit = WavelenghUnit.ANGSTROM
            spectrum_error.flux_unit = FluxUnit.F_lambda
            if np.sum(np.asarray(spectrum_sky.flux) <= 0, axis=0):
                spectrum_sky.flambda = [f for f in spectrum_sky.flux]

            spectrum_list.append(spectrum_error)
        if add_model:
            spectrum_model = Spectrum()
            spectrum_model.catalog = "SDSS"
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
        spectrum.catalog = "PFS"
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

