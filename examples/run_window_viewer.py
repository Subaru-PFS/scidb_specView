import SpectrumViewer.mvcViewer as mvc

fileName = './fits/example_lite.fits'
fileName = './fits/example_pfsObject.fits'
fileName = './fits/example_lam1d.fits'
fileSource = 'PFS'
mvc.window_view(fileName,fileSource, skyline = True,flux = True,model = True,residual = True,emission=True,absorption=True, ae = True,other = True)
#mvc.window_view(fileName,fileSource)