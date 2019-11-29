
import bisect
from collections import OrderedDict

class SpecModel:

    def locateLmb(self,numbers,lmb):
        if lmb>numbers[0] and lmb<numbers[-1]:
            return bisect.bisect_left(numbers, lmb)#not sure if -1 or not
        else:
            return False



    def __init__(self,data_array):

        self.number_of_objects = len(data_array)
        self.coaddObj  = [None for i in range(len(data_array))]
        self.zObj      = [None for i in range(len(data_array))]
        self.lam       = [None for i in range(len(data_array))]
        self.eline     = [None for i in range(len(data_array))]
        self.aline     = [None for i in range(len(data_array))]
        self.aeline    = [None for i in range(len(data_array))]
        self.otherline = [None for i in range(len(data_array))]


        for ind in range(len(data_array)):

            self.coaddObj[ind] = data_array[ind][0]
            self.zObj[ind] = data_array[ind][1]
            # when initializing take coaddObj and zObj
            self.lam[ind] = self.coaddObj[ind].lam
            # lam is true lambda(freq) which is a list of number whose length equal to, for example,
            # the length of flux list(flux is also a list of number)

            # self.col_labels = ['redshift', 'error']
            # self.row_labels = [name for name in self.zObj.LINENAME]
            # self.table_vals = [[self.zObj.LINEZ[i], self.zObj.LINEZ_ERR[i]] for i in range(len(self.zObj.LINENAME))]
            # this section is useless, unless showing all the a/e line in a table
            self.eline[ind]={}
            self.aline[ind]={}
            self.aeline[ind]={}
            self.otherline[ind]={}

            # without vertical position
            # for lineIndex in range(0, len(self.zObj.LINENAME)):
            #     if self.zObj.LINEZ_type[lineIndex] == 'a':
            #         self.aline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
            #     elif self.zObj.LINEZ_type[lineIndex] == 'e':
            #         self.eline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
            #     elif self.zObj.LINEZ_type[lineIndex] == 'a':
            #         self.otherline[self.zObj.LINENAME[lineIndex]]=self.zObj.LINEWAVE[lineIndex]
            #with vertical postition

            if self.zObj[ind].LINENAME is not None:
                for lineIndex in range(0, len(self.zObj[ind].LINENAME)):
                    # for each a/e line in the data
                    type = self.zObj[ind].LINEZ_type[lineIndex]
                    # check with the a/e line directory to get the type either absorption or emission
                    name = self.zObj[ind].LINENAME[lineIndex]
                    # get the name of the line
                    #position = self.zObj.LINEWAVE[lineIndex]
                    position = self.zObj[ind].OBLINEWAVE[lineIndex]
                    # the horizontal position of the red-shifted a/e line on the chart
                    indexFlux=self.locateLmb(self.coaddObj[ind].lam,position)
                    # get the corresponding index of such line on the flux list e.g the 100 th number in the list of flux
                    # has same horizontal position of this particular a/e line.
                    if indexFlux:
                        height = self.coaddObj[ind].flux[indexFlux]
                        # according to the index of a number in the flux list, find the value of that number
                        # finally, get the height of flux
                    else:
                        height =0
                        #if found nothing just set the height to be 0
                    if type == 'a':
                        self.aline[ind][name]=[position,height]
                    elif type == 'e':
                        self.eline[ind][name]=[position,height]
                    elif type=='ae':
                        self.aeline[ind][name] = [position, height]
                    elif type == 'other':
                        self.otherline[ind][name]=[position,height]
                    #construct the line dictionary that including the position of annotation



    def getSkyline(self,ind):
        return self.coaddObj[ind].sky
        # return the skyline
    def getFluxline(self,ind):
        return self.coaddObj[ind].flux
        # return the flux line
    def getModelline(self,ind):
        return self.coaddObj[ind].model
        # return the best fitted model
    def getResidualline(self,ind):
        if self.getFluxline(ind) is not None and self.getModelline(ind) is not None:
            return self.getFluxline(ind) - self.getModelline(ind)
        else:
            return None
        # return the residual
    def getEline(self,ind):
        return self.eline[ind]
        # return the emission line
    def getAline(self,ind):
        return self.aline[ind]
        #return the absorption line
    def getOtherline(self,ind):
        return self.otherline[ind]
        # return the lines that couldn't be classified as any type
    # def __init__(self):
    #     self.t = np.arange(0.0, 2.0, 0.01)
    #     self.s0 = np.sin(2 * np.pi * self.t)
    #     self.s1 = np.sin(4 * np.pi * self.t)
    #     self.s2 = np.sin(6 * np.pi * self.t)
    #     self.position = 1