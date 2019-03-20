import os
from . import lineList
import numpy as np
class ZObj:
    def __init__(self,LINENAME=[],LINEWAVE=None,LINEZ =None,LINEZ_ERR= None,LINEEW=None,LINEEW_ERR=None):
        self.LINENAME = LINENAME

        self.LINEWAVE = LINEWAVE
        self.LINEZ = LINEZ
        self.LINEZ_ERR = LINEZ_ERR
        self.LINEEW = LINEEW
        self.LINEER_ERR = LINEEW_ERR
        if self.LINEZ is not None:
            self.ZAVG =np.sum(self.LINEZ)/np.sum(self.LINEZ!=0)
        else:
            self.ZAVG = None

        if self.LINEWAVE is not None and self.LINEZ is not None:
            self.OBLINEWAVE = (self.LINEZ+1)*self.LINEWAVE
        else:
            self.OBLINEWAVE = None
            # the observed wavelength of lines calculated by rest frame wave length
        # (z +1)* lambda_rest frame

        #f = open('./SpectrumViewer/line_dictionary.txt', 'r')
        #TEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test.txt')
        #f = open('SpectrumViewer/line dictionary', 'r')#TODO chnage it back to full path
        #lineList = f.readlines()

        self.lineDict = {}

        for item in lineList:
            listTemp = item.split()
            #print(listTemp)
            self.lineDict[listTemp[1]] = listTemp[0]
        self.LINEZ_type =[]
        for i in range(len(LINENAME)):
            shorthand = LINENAME[i].split(" ")[0].replace("_","")
            if shorthand in self.lineDict.keys():
                #e or a
                if self.lineDict[shorthand]=='a':
                    self.LINEZ_type.append('a')
                elif self.lineDict[shorthand]=='e':
                    self.LINEZ_type.append('e')
                else:
                    self.LINEZ_type.append('ae')

            else:
                #other
                self.LINEZ_type.append('other')

