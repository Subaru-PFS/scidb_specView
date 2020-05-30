from os import path
import pkg_resources
import numpy as np
import json
from collections import OrderedDict
from io import TextIOWrapper

#http://classic.sdss.org/dr6/algorithms/linestable.html
#https://classic.sdss.org/dr7/algorithms/speclinefits.html

def get_spectral_lines_from_json():
    package_name = __name__  # Could be any module/package name
    resource_path = 'assets/spectral_lines.json'  # Do not use os.path.join()
    spectrum_lines_file = pkg_resources.resource_stream(package_name, resource_path)
    content_dict = json.loads(spectrum_lines_file.read())
    spectrum_lines_file.close()
    return content_dict

def get_spectral_lines():

    #TEST_FILENAME = path.join(path.dirname(__file__), 'line_dictionary.txt')

    package_name = __name__  # Could be any module/package name
    resource_path = 'assets/spectral_lines.txt'  # Do not use os.path.join()
    spectrum_lines_file = pkg_resources.resource_stream(package_name, resource_path)
    lineList = spectrum_lines_file.readlines()
    spectrum_lines_file.close()
    spectral_lines = {}
    for item in lineList:
        listTemp = item.split()
        listTemp = [ item.decode('ascii') for item in listTemp]
        # print(listTemp)
        spectral_line = {}
        id = listTemp[1] + " " + listTemp[0]
        spectral_line["fullname"] = id
        spectral_line["lambda"] = float(listTemp[0])
        spectral_line["name"] = listTemp[1]
        spectral_line["label"] = listTemp[2]
        spectral_lines[id] = spectral_line

    return spectral_lines

spectral_lines = get_spectral_lines()
