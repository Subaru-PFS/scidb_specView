import numpy as np

class ObjType:
    pfs_object = "PfsObject"
    z_object   = "ZObj";

class FitsFileObject:

    def __init__(self,file_name):
        self.LINENAME = 0


    def get_object_type(self):
