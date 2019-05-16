#load SDSS into workable object
from astropy.io import fits
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
from urllib.parse import urlparse
import SpectrumViewer.CoaddObj as Coadd
import SpectrumViewer.ZObj as Z
import math
from collections.abc import Iterable

object_types = {"PfsObject":"PfsObject", "ZObject":"ZObject","Lam1D":"Lam1D"}

hdu_names = {}
hdu_names["PfsObject"] = ["PRIMARY", "FLUX", "FLUXTBL", "COVAR", "COVAR2", "MASK", "SKY", "CONFIG"]
hdu_names["ZObject"] = ["PRIMARY", "COADD", "SPECOBJ", "SPZLINE"]
hdu_names["Lam1D"] = ["PRIMARY", "LAMBDA_SCALE", "ZCANDIDATES", "ZPDF", "ZLINES"]


def get_object_type(file_name, hdulist):
    if hdulist is None:
        hdulist = fits.open(file_name)  # fits file store the data in form of HDU list


    for hdu_name in hdu_names:
            if len(hdulist) == len(hdu_names[hdu_name]):
                is_model = True
                for i in range(len(hdulist)):
                    if hdulist[i].name.upper() != hdu_names[hdu_name][i].upper():
                        is_model = False

                if is_model:
                    return hdu_name

    raise Exception("Unknown data model for input object " + file_name)


def loadFITS(file_names):
    # this function was used to load critical information from fits file to standardised data object
    if len(file_names[0]) ==1:  # it is a letter
        file_names = [file_names]

    data_array=[]

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