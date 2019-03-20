import SpectrumViewer.mvcViewer as mvc

fileName = './fits/example_lite.fits'
fileName = './fits/example_pfsObject.fits'
fileSource = 'PFS'
mvc.window_view(fileName,fileSource, residual = True, other =True)
#mvc.window_view(fileName,fileSource)