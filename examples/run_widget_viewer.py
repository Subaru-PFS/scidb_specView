import SpectrumViewer.mvcViewer as mvc
from SpectrumViewer.data_models import Stream2D
import numpy as np
from astropy.io import fits

viewer = mvc.MvcViewer();

fits_file = './fits/example_lite.fits'
hdulist = fits.open(fits_file)
wavelength = np.power(10, hdulist[1].data['loglam'])
flux = hdulist[1].data['flux']
redshift = hdulist[2].data['z']

new_stream = Stream2D(wavelength, flux, name="spectrum", color="black", linewidth=1, alpha=1)
viewer.add_stream2d(new_stream)
viewer.add_spectral_lines_grid(spectral_lines_grid_name="specLines", redshift = redshift, color="red", linewidth=1, alpha=0.1)

viewer.plot()
a =1