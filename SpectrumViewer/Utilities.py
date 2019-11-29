from os import path
import pkg_resources
import numpy as np
from collections import OrderedDict

def read_spectrum_lines():

    #TEST_FILENAME = path.join(path.dirname(__file__), 'line_dictionary.txt')

    package_name = __name__  # Could be any module/package name
    resource_path = 'line_dictionary.txt'  # Do not use os.path.join()
    spectrum_lines_file = pkg_resources.resource_stream(package_name, resource_path)

    #f = open(spectrum_lines_file, 'r')
    lineList = spectrum_lines_file.readlines()
    spectrum_lines_file.close()
    return lineList

def read_spectral_lines_info():

    #TEST_FILENAME = path.join(path.dirname(__file__), 'line_dictionary.txt')

    package_name = __name__  # Could be any module/package name
    resource_path = 'line_dictionary.txt'  # Do not use os.path.join()
    spectrum_lines_file = pkg_resources.resource_stream(package_name, resource_path)

    #f = open(spectrum_lines_file, 'r')
    lineList = spectrum_lines_file.readlines()
    spectrum_lines_file.close()
    spectral_lines_info = OrderedDict()
    for item in lineList:
        listTemp = item.split()
        listTemp = [ item.decode('ascii') for item in listTemp]
        # print(listTemp)
        spectral_lines_info[listTemp[1]] = OrderedDict()
        spectral_lines_info[listTemp[1]]['name'] = listTemp[1]
        spectral_lines_info[listTemp[1]]['type'] = listTemp[0]
        spectral_lines_info[listTemp[1]]['lambda_air'] = float(listTemp[3])
        spectral_lines_info[listTemp[1]]['lambda_vacuum'] = float(listTemp[2])


    return spectral_lines_info
