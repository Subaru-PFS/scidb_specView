import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
import plotly.tools as tls
import mpld3
class SpecView:
    def __init__(self,filename):
        self.figure = plt.figure("", figsize=(10, 8), dpi=100)
        # initialize the figure object with matplotlib
        #self.graphAx = self.figure.add_subplot(212)
        self.graphAx = self.figure.add_subplot(111)
        # generate axes object
        self.graphAx.set_xlabel(r'$\lambda $ [${\AA}$]')

        self.graphAx.set_ylabel(r'10$^{-17}$ ergs s$^{-1}$ cm$^{-2}$ $\AA^{-1}$')
        #self.graphAx.set_ylim([0, 500])
        #configure the axe where the spectrum will be showed


        self.rax = plt.axes([0.00, 0.05, 0.10, 0.15])
        # iniialize a seperate axes object that will be used to contain radio buttons
        self.checkBtns = CheckButtons(self.rax, ('Skyline',
                                                 'Flux',
                                                 'Model',
                                                 'Residual',
                                                 'Emission',
                                                 'Absorption',
                                                 'A or E',
                                                 'Other'),
                                      (True, True, True,True,False,False,False,False))
        # create buttons with tags: 'Skyline',
        #                                                  'Flux',
        #                                                  'Model',
        #                                                  'Emission',
        #                                                  'Absorption',
        #                                                  'A or E',
        #                                                  'Other')
        # and default value
        # when the check buttons was clicked, the gadget will call the callback function with the tag as argument
    def show(self):


        plt.show()
        #plt is the matplotlib state machine interface, once imported to the interpreter, can be used accross the code
        # show whatever has been passed to the state machine in previous program.
        #mpld3.show(fig=self.figure, ip='127.0.0.1', port=8888, n_retries=50, local=True, open_browser=True, http_server=None)
        #TODO : change the display mode to cell mode
class windowView:
    def __init__(self,filename):
        self.figure = plt.figure("", figsize=(18, 10), dpi=100)

        #self.graphAx = self.figure.add_subplot(212)
        self.graphAx = self.figure.add_subplot(111)
        self.graphAx.set_xlabel(r'$\lambda $ [${\AA}$]')
        self.graphAx.set_ylabel(r'10$^{-17}$ ergs s$^{-1}$ cm$^{-2}$ $\AA^{-1}$')
        #self.graphAx.set_ylim([0, 150])
    def getMatplotlibFig(self):
        return self.figure
    def returnPlotlyFig(self):
        return tls.mpl_to_plotly(self.figure)
        # port matplolib figure to plotly image object