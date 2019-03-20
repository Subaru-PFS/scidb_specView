#load SDSS into workable object
from astropy.io import fits
#from py3.SciServer import Authentication, Config
#from py3.SciServer import CasJobs
from urllib.parse import urlparse
import SpectrumViewer.CoaddObj as Coadd
import SpectrumViewer.ZObj as Z
import math

object_types = {"PfsObject":"PfsObject", "ZObject":"ZObject"}


def get_object_type(file_name, hdulist):
    if hdulist is None:
        hdulist = fits.open(file_name)  # fits file store the data in form of HDU list

    pfsObj_hdu_names = ["PRIMARY","FLUX","FLUXTBL","COVAR","COVAR2","MASK","SKY","CONFIG"]
    zObj_hdu_names = ["PRIMARY", "COADD", "SPECOBJ", "SPZLINE"]

    if len(hdulist) == 8: # is_pfs_object  has 8 HDUs
        is_pfsObject = True
        for i in range(len(hdulist)):
            if hdulist[i].name != pfsObj_hdu_names[i]:
                is_pfsObject = False

        if is_pfsObject is False:
            raise Exception("Incorrect data model for input PfsObject " + file_name)

        return object_types["PfsObject"]

    elif len(hdulist) == 4:
        is_zObj = True
        for i in range(len(hdulist)):
            if hdulist[i].name != zObj_hdu_names[i]:
                is_zObj = False

        if is_zObj is False:
            raise Exception("Incorrect data model for input ZObject " + file_name)

        return object_types["ZObject"]

    else:
        raise Exception("Unknown data model for input object " + file_name)


def loadFITS(file_name,file_source):
    # this function was used to load critical information from fits file to standardised data object

    hdulist = fits.open(file_name)  # fits file store the data in form of HDU list
    object_type = get_object_type(file_name, hdulist)

    if file_source=='PFS':
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
            return coaddObj,zObj

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
            return coaddObj,zObj
        else:
            raise Exception("Unknown data model for input object " + file_name)


    else:
        print('Only PFS file sources supported for now.')