from os import path
import pkg_resources

def read_spectrum_lines():

    #TEST_FILENAME = path.join(path.dirname(__file__), 'line_dictionary.txt')

    package_name = __name__  # Could be any module/package name
    resource_path = 'line_dictionary.txt'  # Do not use os.path.join()
    spectrum_lines_file = pkg_resources.resource_stream(package_name, resource_path)

    #f = open(spectrum_lines_file, 'r')
    lineList = spectrum_lines_file.readlines()
    spectrum_lines_file.close()
    return lineList

