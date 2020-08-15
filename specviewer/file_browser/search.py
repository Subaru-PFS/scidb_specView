import os
from specviewer import data_base_directory
def get_spectrum_path(specid):
    #raise Exception(os.getcwd())
    #return ("example_lite", "../examples/fits/example_lite.fits")
    return ("example_lite", data_base_directory + "example_lite.fits")
