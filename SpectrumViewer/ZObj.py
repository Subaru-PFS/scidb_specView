class ZObj:
    def __init__(self,LINENAME=None,LINEWAVE=None,LINEZ =None,LINEZ_ERR= None,LINEEW=None,LINEEW_ERR=None):
        self.LINENAME = LINENAME

        self.LINEWAVE = LINEWAVE
        self.LINEZ = LINEZ
        self.LINEZ_ERR = LINEZ_ERR
        self.LINEEW = LINEEW
        self.LINEER_ERR = LINEEW_ERR
        #f = open('line dictionary', 'r')
        f = open('SpectrumViewer/line dictionary', 'r')#TODO chnage it back to full path
        lineList = f.readlines()
        self.lineDict = {}

        for item in lineList:
            listTemp = item.split()
            #print(listTemp)
            self.lineDict[listTemp[1]] = listTemp[0]
        self.LINEZ_type =[]
        for i in range(len(LINENAME)):
            if LINENAME[i] in self.lineDict.keys():
                #e or a
                if self.lineDict[LINENAME[i]]=='a':
                    self.LINEZ_type.append('a')
                elif self.lineDict[LINENAME[i]]=='e':
                    self.LINEZ_type.append('e')
                else:
                    self.LINEZ_type.append('ae')

            else:
                #other
                self.LINEZ_type.append('other')

