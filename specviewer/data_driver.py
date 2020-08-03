#load SDSS into workable object
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
#from spectrumviewer.data_models import Medium, Spectrum, SpectrumLineGrid
from .models import data_models as dm
from .models import enum_models as em
#from SpectrumViewer.data_models import *
import numpy as np
from .flux import fnu_to_flambda
from specviewer.models.data_models import Trace, Catalogs

object_types = {"PfsObject":"PfsObject", "ZObject":"ZObject","Lam1D":"Lam1D"}

hdu_names = {}
hdu_names["PfsObject"] = ["PRIMARY", "FLUX", "FLUXTBL", "COVAR", "COVAR2", "MASK", "SKY", "CONFIG"]
#hdu_names["ZObject"] = ["PRIMARY", "COADD", "SPECOBJ", "SPZLINE"]
hdu_names["ZObject"] = ["PRIMARY", "COADD", None, "SPZLINE"]
hdu_names["Lam1D"] = ["PRIMARY", "LAMBDA_SCALE", "ZCANDIDATES", "ZPDF", "ZLINES"]


def get_object_type(hdulist):

    for hdu_name in hdu_names:
            if len(hdulist) == len(hdu_names[hdu_name]):
                is_model = True
                for i in range(len(hdulist)):
                    if  hdu_names[hdu_name][i] is not None and hdulist[i].name.upper() != hdu_names[hdu_name][i].upper():
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

def get_mask_id(catalog_or_file_name, mask_name, bit):
    return str(catalog_or_file_name) + " " + str(mask_name) + " " + str(bit)

sdss_mask_bits = { get_mask_id("SDSS",mb[0],mb[1]): {'bit':mb[1], 'catalog':'SDSS', 'name':mb[0], 'description':mb[2]} for mb in sdss_mask_bits_array}



def create_mask(mask_array, wavelength_array):

    mask = {}
    mask_value =  mask_array[0]
    mask[mask_value] = [[0,0]]
    unique_mask_values = set()

    for i in range(1,len(wavelength_array),1):
        new_mask_value = mask_array[i]
        unique_mask_values.add(int(new_mask_value))

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

    return mask, unique_mask_values

def get_trace_list_from_fits(hdulist, name):

    trace_list = []

    object_type = get_object_type(hdulist)

    if object_type == object_types["ZObject"]:
        coaddData =1 # the index of Coadd data in the HDU list
        zData =3 # index of absorption and emission line data in HDU list
        c=hdulist[coaddData].data
        z=hdulist[zData].data
        # the name of the data unit can be found on the official SDSS DR webpage

        #note: alwasys convert data types to native python types, not numpy types. The reason is that everything has
        # to be serialized as json, and numpy objects cannot be automatically serialized as such.

        # object spectrum
        trace = Trace()
        trace.name = name
        wavelength = [float(10**lam) for lam in c['loglam']]
        trace.wavelength = wavelength
        trace.wavelength_unit = dm.WavelenghUnit.ANGSTROM
        trace.flux = [1.0*10**-17*float(x) for x in c['flux']]
        trace.flux_error = [1.0*10**-17*np.sqrt(float(1.0/x)) for x in c['ivar']]
        trace.flux_unit = dm.FluxUnit.F_lambda
        trace.flambda = [x for x in trace.flux]
        trace.flambda_error = [x for x in trace.flux_error]

        trace.ancestors = []
        trace.catalog = Catalogs.SDSS
        trace.spectrum_type = em.SpectrumType.OBJECT
        trace.is_visible = True

        # masks:
        and_mask, and_mask_values = create_mask([int(m) for m in c['and_mask']], wavelength)
        or_mask, or_mask_values = create_mask([int(m) for m in c['or_mask']], wavelength)

        and_mask_bits = { bit for (a,bit,c) in sdss_mask_bits_array for mv in and_mask_values if  (mv & 2**bit) != 0 }
        and_mask_values = {get_mask_id(name, mb[0], mb[1]): {'bit': mb[1], 'catalog': 'SDSS', 'name': mb[0], 'description': mb[2]} for mb in sdss_mask_bits_array if mb[1] in and_mask_bits}
        or_mask_bits = { bit for (a,bit,c) in sdss_mask_bits_array for mv in or_mask_values if  (mv & 2**bit) != 0 }
        or_mask_values = {get_mask_id(name, mb[0], mb[1]): {'bit': mb[1], 'catalog': 'SDSS', 'name': mb[0], 'description': mb[2]} for mb in sdss_mask_bits_array if int(mb[1]) in or_mask_bits}

        trace.masks = {'and_mask': and_mask, 'or_mask': or_mask, 'and_mask_values':and_mask_values, 'or_mask_values':or_mask_values}
        trace.mask_bits = sdss_mask_bits

        trace_list.append(trace)

        # sky spectrum
        sky_trace = Trace()
        sky_trace.catalog = Catalogs.SDSS
        sky_trace.name = name + "_sky"
        sky_trace.wavelength = wavelength
        sky_trace.flux = [1.0*10**-17*float(x) for x in c['sky']]
        sky_trace.wavelength_unit = dm.WavelenghUnit.ANGSTROM
        sky_trace.flux_unit = dm.FluxUnit.F_lambda
        sky_trace.ancestors = [name]
        sky_trace.flambda = [f for f in sky_trace.flux]
        sky_trace.is_visible = False
        sky_trace.spectrum_type=em.SpectrumType.SKY

        trace_list.append(sky_trace)

        # flux error
        error_trace = Trace()
        error_trace.catalog = Catalogs.SDSS
        error_trace.name = name + "_error"
        error_trace.wavelength = wavelength
        error_trace.flux = [1.0*10**-17*np.sqrt(float(1.0/x)) for x in c['ivar']]
        error_trace.wavelength_unit = dm.WavelenghUnit.ANGSTROM
        error_trace.flux_unit = dm.FluxUnit.F_lambda
        error_trace.ancestors = [name]
        error_trace.flambda = [f for f in error_trace.flux]
        error_trace.is_visible = False
        error_trace.spectrum_type = em.SpectrumType.ERROR

        trace_list.append(error_trace)

        # model trace

        model_trace = Trace()
        model_trace.catalog = Catalogs.SDSS
        model_trace.name = name + "_model"
        model_trace.wavelength = wavelength
        model_trace.flux = [1.0*10**-17*float(x) for x in c['model']]
        model_trace.wavelength_unit = dm.WavelenghUnit.ANGSTROM
        model_trace.flux_unit = dm.FluxUnit.F_lambda
        model_trace.ancestors = [name]
        model_trace.flambda = [f for f in model_trace.flux]
        model_trace.is_visible = False
        model_trace.spectrum_type=em.SpectrumType.MODEL

        trace_list.append(model_trace)


        return trace_list

    elif object_type == object_types["PfsObject"]:
        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data

        # add object spectrum
        trace = Trace()
        trace.name = name
        trace.catalog = Catalogs.PFS
        trace.wavelength = [10.0*float(x) for x  in c['lambda']]
        # converted from Jy to Flambda
        trace.flux = [fnu_to_flambda(fnu*10**-23, trace.wavelength[i], dm.WavelenghUnit.ANGSTROM) for (i, fnu) in
                             enumerate(c['flux'])]

        trace.wavelength_unit = dm.WavelenghUnit.ANGSTROM
        trace.flux_unit = dm.FluxUnit.F_lambda
        trace.flambda = [f for f in trace.flux]
        trace.is_visible= True
        trace.spectrum_type = em.SpectrumType.OBJECT

        trace_list.append(trace)
        return trace_list

    elif object_type == object_types["Lam1D"]:

        coaddData =2 # the index of Coadd data in the HDU list
        c=hdulist[coaddData].data
        coaddData =1 # the index of the HDU that contains the wavelength
        l=hdulist[coaddData].data

        for ind in range(len(c['MODELFLUX'])):
            trace = Trace()
            trace.name = name + "_" + str(ind)
            trace.wavelength = [10.0*float(x) for x in l['WAVELENGTH']]
            # adding flux
            trace.flux = [0.0 for s in range(len(l['WAVELENGTH']))]
            trace.flambda = [0.0 for s in range(len(l['WAVELENGTH']))]
            trace.spectrum_type = em.SpectrumType.OBJECT
            trace_list.append(trace)


        return trace_list

    else:
        raise Exception("Unknown data model for input file.")

