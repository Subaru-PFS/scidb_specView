#load SDSS into workable object
from astropy.io import fits
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
from urllib.parse import urlparse
import SpectrumViewer.CoaddObj as Coadd
import SpectrumViewer.ZObj as Z
import SpectrumViewer.data_models as data_models
from SpectrumViewer.data_models import Medium, Stream2D, SpectrumLineGrid
import SpectrumViewer

#from SpectrumViewer.data_models import *
import math
from collections.abc import Iterable
from collections import OrderedDict
import numpy as np
import os
from . import spectral_lines_info

object_types = {"PfsObject":"PfsObject", "ZObject":"ZObject","Lam1D":"Lam1D"}

hdu_names = {}
hdu_names["PfsObject"] = ["PRIMARY", "FLUX", "FLUXTBL", "COVAR", "COVAR2", "MASK", "SKY", "CONFIG"]
hdu_names["ZObject"] = ["PRIMARY", "COADD", "SPECOBJ", "SPZLINE"]
hdu_names["Lam1D"] = ["PRIMARY", "LAMBDA_SCALE", "ZCANDIDATES", "ZPDF", "ZLINES"]


def get_object_type(file_path, hdulist):
    if hdulist is None:
        hdulist = fits.open(file_path)  # fits file store the data in form of HDU list


    for hdu_name in hdu_names:
            if len(hdulist) == len(hdu_names[hdu_name]):
                is_model = True
                for i in range(len(hdulist)):
                    if hdulist[i].name.upper() != hdu_names[hdu_name][i].upper():
                        is_model = False

                if is_model:
                    return hdu_name

    raise Exception("Unknown data model for input file " + file_path)


def loadFITS(file_names):
    # this function was used to load critical information from fits file to standardised data object
    if len(file_names[0]) ==1:  # it is a letter
        file_names = [file_names]

    data_array = []

    for file_name in file_names:

        hdulist = fits.open(file_name)  # fits file store the data in form of HDU list
        object_type = get_object_type(file_name, hdulist)


        if object_type == object_types["ZObject"]:
            coaddData =1 # the index of Coadd data in the HDU list
            zData =3 # index of absorption and emission line data in HDU list
            hdulist = fits.open(file_name)# fits file store the data in form of HDU list
            c=hdulist[coaddData].data
            z=hdulist[zData].data
            # the name of the data unit can be found on the official SDSS DR webpage
            coaddObj = Coadd.CoaddObj(
                flux=c['flux'],
                loglam=c['loglam'],
                ivar=c['ivar'],
                andMask=c['and_Mask'],
                orMask=c['or_Mask'],
                wdisp=c['wdisp'],
                sky = c['sky'],
                model=c['model'])
            zObj = Z.ZObj(
                LINENAME=z['LINENAME'],
                LINEWAVE=z['LINEWAVE'],
                LINEZ=z['LINEZ'],
                LINEEW=z['LINEEW'],
                LINEZ_ERR=z['LINEZ_ERR'],
                LINEEW_ERR=z['LINEEW_ERR'])

            data_array.append((coaddObj,zObj))

        elif object_type == object_types["PfsObject"]:
            coaddData =2 # the index of Coadd data in the HDU list
            c=hdulist[coaddData].data
            # the name of the data unit can be found on the official SDSS DR webpage
            coaddObj = Coadd.CoaddObj(
                flux=c['flux'],
                loglam=[math.log10(lam) for lam in c['lambda']],
                ivar=c['fluxvariance'],
                andMask=c['Mask'],
                orMask=[0.0 for s in range(len(c['flux']))],
                wdisp=[0.0 for s in range(len(c['flux']))],
                sky = [0.0 for s in range(len(c['flux']))],
                model=[0.0 for s in range(len(c['flux']))])
            zObj = Z.ZObj(
                LINENAME=[],
                LINEWAVE=None,
                LINEZ=None,
                LINEEW=None,
                LINEZ_ERR=None,
                LINEEW_ERR=None)

            data_array.append((coaddObj, zObj))

        elif object_type == object_types["Lam1D"]:

            coaddData =2 # the index of Coadd data in the HDU list
            c=hdulist[coaddData].data
            coaddData =1 # the index of the HDU that contains the wavelength
            l=hdulist[coaddData].data

            for ind in range(len(c['MODELFLUX'])):

                # the name of the data unit can be found on the official SDSS DR webpage
                coaddObj = Coadd.CoaddObj(
                    flux=[0.0 for s in range(len(l['WAVELENGTH']))],
                    loglam=[math.log10(lam) for lam in l['WAVELENGTH']],
                    ivar=[0.0 for s in range(len(l['WAVELENGTH']))],
                    andMask=None,
                    orMask=[0.0 for s in range(len(l['WAVELENGTH']))],
                    wdisp=[0.0 for s in range(len(l['WAVELENGTH']))],
                    sky = [0.0 for s in range(len(l['WAVELENGTH']))],
                    model=c['MODELFLUX'][ind])
                zObj = Z.ZObj(
                    LINENAME=[],
                    LINEWAVE=None,
                    LINEZ=None,
                    LINEEW=None,
                    LINEZ_ERR=None,
                    LINEEW_ERR=None)

                data_array.append((coaddObj, zObj))

        else:
            raise Exception("Unknown data model for input object " + file_name)

    return data_array


def load_fits_files(new_data_streams, new_display_names, current_data_streams):

    number_of_current_streams = len(current_data_streams)

    if len(new_data_streams[0]) == 1:  # it is a letter
        file_paths = [new_data_streams]
    else:
        file_paths = new_data_streams
    file_names = [".".join((os.path.basename(file_path).split(".")[:-1])) for file_path in file_paths]

    _current_streams_names = [name for name in current_data_streams]
    _new_data_stream_names = []
    if new_display_names is None:
        for file_name in file_names:
            if file_name in _current_streams_names:
                new_name = file_name + "_new"
            else:
                new_name = file_name
            _new_data_stream_names.append(new_name)
            _current_streams_names.append(new_name)

    else:
        if ( type(new_display_names) == str and len(file_paths) != 1 ) or \
           ( type(new_display_names) != str and len(new_display_names) != len(file_paths) ):
            raise Exception("Number of new display names not equal to number of new files")

        for new_display_name in new_display_names:
            if type(new_display_name) != str:
                raise TypeError("Stream name " + str(new_display_name) + " is not of type string")
            if new_display_name in _current_streams_names:
                raise NameError("Stream named " + new_display_name + " already exists")
            _new_data_stream_names.append(new_display_name)
            _current_streams_names.append(new_display_name)


    _new_data_streams = []
    _new_stream_display_names = []

    for i in range(len(file_paths)):
        file_path = file_paths[i]

        try:
            hdulist = fits.open(file_path)  # fits file store the data in form of HDU list
        except:
            raise FileNotFoundError("File " + str(file_path) + " not found")

        object_type = get_object_type(file_path, hdulist)


        if object_type == object_types["ZObject"]:
            coaddData =1 # the index of Coadd data in the HDU list
            zData =3 # index of absorption and emission line data in HDU list
            c=hdulist[coaddData].data
            z=hdulist[zData].data
            # the name of the data unit can be found on the official SDSS DR webpage

            lam = [10**lam for lam in c['loglam']]

            # adding flux
            flux = c['flux']
            _new_data_stream_names.append(_new_data_stream_names[i] + "_flux")
            _new_data_streams.append([lam,flux])

            # adding sky
            flux = c['sky']
            _new_stream_display_names.append(_new_data_stream_names[i] + "_sky")
            _new_data_streams.append([lam,flux])

            # adding model
            flux = c['model']
            _new_stream_display_names.append(_new_data_stream_names[i] + "_model")
            _new_data_streams.append([lam,flux])

        elif object_type == object_types["PfsObject"]:
            coaddData =2 # the index of Coadd data in the HDU list
            c=hdulist[coaddData].data

            lam = c['lambda']

            # adding flux
            flux = c['flux']
            _new_stream_display_names.append(_new_data_stream_names[i] + "_flux")
            _new_data_streams.append([lam,flux])

            # adding flux variance
            flux = c['fluxvariance']
            _new_stream_display_names.append(_new_data_stream_names[i] + "_fluxvariance")
            _new_data_streams.append([lam,flux])

        elif object_type == object_types["Lam1D"]:

            coaddData =2 # the index of Coadd data in the HDU list
            c=hdulist[coaddData].data
            coaddData =1 # the index of the HDU that contains the wavelength
            l=hdulist[coaddData].data

            for ind in range(len(c['MODELFLUX'])):

                lam = l['WAVELENGTH']

                # adding flux
                flux = [0.0 for s in range(len(l['WAVELENGTH']))]
                _new_stream_display_names.append(new_display_names[i] + "_flux" + str(ind))
                _new_data_streams.append([lam, flux])

        else:
            raise Exception("Unknown data model for input file " + file_path)

    return (_new_data_streams, _new_data_stream_names)


def get_new_stream_name(current_names, base_name = "stream"):

    last_name_indexes = [ int(current_name.split("_")[1]) for current_name in current_names if ( current_name.startswith("stream_") or current_name.startswith("lineGrid_")  ) ]
    if len(last_name_indexes) == 0:
        last_name_index_max = 0
    else:
        last_name_index_max = np.max(last_name_indexes)

    new_data_stream_name = base_name + "_" + str(last_name_index_max+1)
    return new_data_stream_name


def load_arrays(new_data_streams, new_display_names, current_data_streams):

    _new_data_stream_names = []
    _new_data_streams = None

    if len(np.shape(new_data_streams)) == 2:  # one array data stream, like  [  [1,2,3,4], [1,2,3,4] ]
        _new_data_streams = [new_data_streams]
    elif len(np.shape(new_data_streams)) == 3:  # array of multiple data stream, like  [  [[1,2,3,4], [1,2,3,4]], [[1,2,3,4], [1,2,3,4]]  ]
        _new_data_streams = new_data_streams


    _current_streams_names = [name for name in current_data_streams]
    if new_display_names is None:
        for i in range(len(_new_data_streams)):
            _new_stream_name = get_new_stream_name(_current_streams_names, base_name = "stream")
            _new_data_stream_names.append(_new_stream_name)
            _current_streams_names.append(_new_stream_name)
    else:

        if len(_new_data_streams) != len(new_display_names):
            raise Exception("Number of new display names not equal to number of new streams")

        for new_display_name in new_display_names:
            if type(new_display_name) != str:
                raise TypeError("Stream name " + str(new_display_name) + " is not of type string")
            if new_display_name in _current_streams_names:
                raise NameError("Stream named " + new_display_name + " already exists")
            _new_data_stream_names.append(new_display_name)
            _current_streams_names.append(new_display_name)

    return (_new_data_streams, _new_data_stream_names)

def load_new_streams(current_data_streams, new_data_streams, new_display_names, new_data_stream_styles):
    """
        for i in len(data_stream_array):
            if data_stream_name is None:
                data_stream_name = "stream_" + str(number_of_stored_streams+1)

            new_stream = Stream2D(data_stream, data_stream_name)
            mvc_viewer.data_dict[data_stream_name] = new_stream
    """
    updated_streams = OrderedDict()
    #number_of_current_streams = len(current_data_streams)

    if type(new_data_streams) == str: # it is a single file or array of files
        (_new_data_streams, _new_data_stream_names) = load_fits_files(new_data_streams, new_display_names, current_data_streams)
    elif type(new_data_streams[0]) == str: # an array of strings
        (_new_data_streams, _new_data_stream_names) = load_fits_files(new_data_streams, new_display_names, current_data_streams)
    else: # arrays of floats or stream objects
        (_new_data_streams, _new_data_stream_names) = load_arrays(new_data_streams, new_display_names, current_data_streams)

    for i in range(len(_new_data_stream_names)):

        new_stream_name = _new_data_stream_names[i]
        x_coords = np.asarray(_new_data_streams[0][0])
        y_coords = np.asarray(_new_data_streams[0][1])

        new_stream = data_models.Stream2D(x_coords,y_coords,new_stream_name)
        updated_streams[new_stream_name] = new_stream

    return updated_streams


def load_new_stream2d(current_data_streams, new_data_stream, replace=False):

    if type(new_data_stream) == SpectrumViewer.data_models.Stream2D:
        _new_data_stream = [new_data_stream]
    elif type(new_data_stream) == list and len(new_data_stream) > 0 and type(new_data_stream[0]):
        _new_data_stream = new_data_stream
    else:
        raise Exception("Unsupported input object")

    if not replace:
        for new_data_stream in _new_data_stream:
            if str(new_data_stream.name) in current_data_streams.keys():
                raise Exception("Stream named " + str(new_data_stream.name) + " already exists")

    return _new_data_stream





def load_new_spectral_lines_grid(current_data_streams, new_spectral_lines_grid, spectral_lines_grid_name, redshift=0.0, medium= Medium.AIR, color="lightblue", alpha=0.3, linewidth=1):

    if new_spectral_lines_grid is None:
        new_spectral_lines_grid = [item for item in spectral_lines_info.keys()]
    else:
        if type(new_spectral_lines_grid) ==  str:
            new_spectral_lines_grid = [new_spectral_lines_grid]
        for line in new_spectral_lines_grid:
            if line not in spectral_lines_info:
                raise Exception("Line named " + line + " not in list of known lines: " + str([item for item in spectral_lines_info.keys()]))

    _new_spectral_line_grid = OrderedDict()

    _current_streams_names = [name for name in current_data_streams]

    if spectral_lines_grid_name is None:
        spectral_lines_grid_name = get_new_stream_name(_current_streams_names, base_name="lineGrid")
    else:
        if type(spectral_lines_grid_name) != str:
            raise TypeError("Spectral lines grid name " + str(spectral_lines_grid_name) + " is not of type string")
        if spectral_lines_grid_name in _current_streams_names:
            raise NameError("Stream named " + spectral_lines_grid_name + " already exists")

    _new_spectral_line_grid = OrderedDict()
    for i in range(len(new_spectral_lines_grid)):

        new_line_name = new_spectral_lines_grid[i]
        if medium == Medium.VACUUM:
            lambda1 = (1.0+redshift)*spectral_lines_info[new_line_name]['lambda_vacuum']
            lambda2 = lambda1
        elif medium == Medium.AIR:
            lambda1 = (1.0+redshift)*spectral_lines_info[new_line_name]['lambda_air']
            lambda2 = lambda1

        new_spec_line = data_models.SpectrumLine(lambda1, lambda2, new_line_name, medium, color, linewidth, alpha)
        _new_spectral_line_grid[new_line_name] = new_spec_line

    return (data_models.SpectrumLineGrid(_new_spectral_line_grid), spectral_lines_grid_name)


