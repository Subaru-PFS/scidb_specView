import SpectrumViewer.specController as C
import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
import SpectrumViewer.SDSSDriver as driver

def view(filename,filesource="PFS"):
    coaddObj, zObj = driver.loadFITS(filename, filesource)
    m = M.SpecModel(coaddObj, zObj)
    v = V.SpecView(filename)
    c = C.SpecController(m,v)
    c.run()
    #c.controlFunc('Other')

#Set the bool value to be true for those information you are interested:
#ae means absorption or emission line, other means undetermined line
def window_view(filename,filesource="PFS",skyline = False,flux = True,model = True,residual = False,emission=False,absorption=False,
                ae = False,other = False):
    coaddObj, zObj = driver.loadFITS(filename, filesource)
    m = M.SpecModel(coaddObj, zObj)
    v=V.windowView(filename)
    c = C.SpecController(m,v)
    c.windowRun(skyline ,flux ,model ,residual,emission,absorption,ae ,other)