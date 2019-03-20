
import bisect
class SpecModel:
    def locateLmb(self,numbers,lmb):
        if lmb>numbers[0] and lmb<numbers[-1]:
            return bisect.bisect_left(numbers, lmb)#not sure if -1 or not
        else:
            return False



    def __init__(self,coaddObj,zObj):
        self.coaddObj = coaddObj
        self.zObj = zObj
        # when initializing take coaddObj and zObj
        self.lam = self.coaddObj.lam
        # lam is true lambda(freq) which is a list of number whose length equal to, for example,
        # the length of flux list(flux is also a list of number)

        # self.col_labels = ['redshift', 'error']
        # self.row_labels = [name for name in self.zObj.LINENAME]
        # self.table_vals = [[self.zObj.LINEZ[i], self.zObj.LINEZ_ERR[i]] for i in range(len(self.zObj.LINENAME))]
        # this section is useless, unless showing all the a/e line in a table
        self.eline={}
        self.aline={}
        self.aeline={}
        self.otherline={}

        # without vertical position
        # for lineIndex in range(0, len(self.zObj.LINENAME)):
        #     if self.zObj.LINEZ_type[lineIndex] == 'a':
        #         self.aline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
        #     elif self.zObj.LINEZ_type[lineIndex] == 'e':
        #         self.eline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
        #     elif self.zObj.LINEZ_type[lineIndex] == 'a':
        #         self.otherline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
        #with vertical postition

        if self.zObj.LINENAME is not None:
            for lineIndex in range(0, len(self.zObj.LINENAME)):
                # for each a/e line in the data
                type = self.zObj.LINEZ_type[lineIndex]
                # check with the a/e line directory to get the type either absorption or emission
                name = self.zObj.LINENAME[lineIndex]
                # get the name of the line
                #position = self.zObj.LINEWAVE[lineIndex]
                position = self.zObj.OBLINEWAVE[lineIndex]
                # the horizontal position of the red-shifted a/e line on the chart
                indexFlux=self.locateLmb(self.coaddObj.lam,position)
                # get the corresponding index of such line on the flux list e.g the 100 th number in the list of flux
                # has same horizontal position of this particular a/e line.
                if indexFlux:
                    height = self.coaddObj.flux[indexFlux]
                    # according to the index of a number in the flux list, find the value of that number
                    # finally, get the height of flux
                else:
                    height =0
                    #if found nothing just set the height to be 0
                if type == 'a':
                    self.aline[name]=[position,height]
                elif type == 'e':
                    self.eline[name]=[position,height]
                elif type=='ae':
                    self.aeline[name] = [position, height]
                elif type == 'other':
                    self.otherline[name]=[position,height]
                #construct the line dictionary that including the position of annotation



    def getSkyline(self):
        return self.coaddObj.sky
        # return the skyline
    def getFluxline(self):
        return self.coaddObj.flux
        # return the flux line
    def getModelline(self):
        return self.coaddObj.model
        # return the best fitted model
    def getResidualline(self):
        return self.getFluxline() - self.getModelline()
        # return the residual
    def getEline(self):
        return self.eline
        # return the emission line
    def getAline(self):
        return self.aline
        #return the absorption line
    def getOtherline(self):
        return self.otherline
        # return the lines that couldn't be classified as any type
    # def __init__(self):
    #     self.t = np.arange(0.0, 2.0, 0.01)
    #     self.s0 = np.sin(2 * np.pi * self.t)
    #     self.s1 = np.sin(4 * np.pi * self.t)
    #     self.s2 = np.sin(6 * np.pi * self.t)
    #     self.position = 1