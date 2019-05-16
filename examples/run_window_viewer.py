import SpectrumViewer.mvcViewer as mvc

fileName1 = './fits/example_lite.fits'
fileName2 = './fits/example_pfsObject.fits'
fileName3 = './fits/example_lam1d.fits'
#mvc.window_view([fileName1,fileName2],fileSource, skyline = True,flux = True,model = True,residual = True,emission=True,absorption=True, ae = True,other = True)
#mvc.window_view(fileName1,fileSource, skyline = False,flux = True,model = True,residual = True,emission=True,absorption=True, ae = True,other = True)
#mvc.window_view([fileName1],fileSource)
#mvc.view([fileName1,fileName1,fileName1])
#mvc.view([fileName1,fileName2,fileName3])
mvc.window_view([fileName1,fileName2], skyline = True, flux = True, model = True, residual = True, emission=True, absorption=True, ae = True, other = True)
