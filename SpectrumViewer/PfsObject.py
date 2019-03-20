from . import lineList
import numpy as np
class PfsObject:
    def __init__(self,LINENAME=None,LINEWAVE=None,LINEZ =None,LINEZ_ERR= None,LINEEW=None,LINEEW_ERR=None):
        self.LINENAME = LINENAME

        self.LINEWAVE = LINEWAVE
        self.LINEZ = LINEZ
        self.LINEZ_ERR = LINEZ_ERR
        self.LINEEW = LINEEW
        self.LINEER_ERR = LINEEW_ERR
        self.ZAVG =np.sum(self.LINEZ)/np.sum(self.LINEZ!=0)
        self.OBLINEWAVE = (self.LINEZ+1)*self.LINEWAVE
        # the observed wavelength of lines calculated by rest frame wave length
        # (z +1)* lambda_rest frame

        #f = open('line dictionary', 'r')
        #f = open('SpectrumViewer/line dictionary', 'r')#TODO chnage it back to full path
        #lineList = f.readlines()
        #lineList = uitils.read_spectrum_lines()
        #self.lineDict = {}

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
