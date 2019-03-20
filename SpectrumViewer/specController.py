import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly
from IPython.display import FileLink, FileLinks
import plotly.graph_objs as go
import webbrowser
class SpecController:
    def __init__(self,model,view):
        self.model = model
        # take SpecModel object as argument to initialize
        self.view = view
        # take SpecView or a windowView object as argument to initialize

        self.fluxLine, = self.view.graphAx.plot(self.model.lam, self.model.getFluxline(),'r',label='flux')
        self.skyLine, = self.view.graphAx.plot(self.model.lam, self.model.getSkyline(), 'y', label='sky')
        self.modelLine, = self.view.graphAx.plot(self.model.lam, self.model.getModelline(), 'c', label='best fit model')
        self.residualLine, = self.view.graphAx.plot(self.model.lam, self.model.getResidualline(), 'g', label='residual')
        #initilize the line object by calling plot function in axes object
        self.aLines=[]
        self.eLines = []
        self.aeLines = []
        self.otherLines = []
        #vertical line
        # self.eLines = [[self.view.graphAx.text(val[0]-5,val[1],key,rotation=90,visible=False),self.view.graphAx.axvline(val[0],visible=False)]
        #                for key, val in self.model.eline.items()]
        # #val0 position,val1 height, key name
        # self.aLines = [[self.view.graphAx.text(val[0]-5,val[1],key,rotation=90,visible=False),self.view.graphAx.axvline(val[0],visible=False)]
        #                for key, val in self.model.aline.items()]
        # self.aeLines = [[self.view.graphAx.text(val[0] - 5, val[1], key, rotation=90,visible=False), self.view.graphAx.axvline(val[0],visible=False)]
        #                for key, val in self.model.aeline.items()]
        # self.otherLines = [[self.view.graphAx.text(val[0]-5,val[1],key,rotation=90,visible=False),self.view.graphAx.axvline(val[0],visible=False)]
        #                    for key, val in self.model.otherline.items()]


        # arrow
        vOffset =-5
        # the vertical offset of the arrow
        width = 0.5
        # the width of the arrow
        headlengthoffset = 1.5*3*width
        # the length of arrow head
        baseoffset = headlengthoffset-vOffset
        #
        #default hide lines
        self.eLines = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                        self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                       for key, val in self.model.eline.items()]
        # create a list tuple (text, position)
        # val0 position,val1 height, key name
        self.aLines = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                        self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                       for key, val in self.model.aline.items()]
        self.aeLines = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                         self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                       for key, val in self.model.aeline.items()]
        self.otherLines = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                            self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                       for key, val in self.model.otherline.items()]


    def plotTable(self):
        self.view.tableAx.table(cellText=self.model.table_vals,
                   colWidths=[0.1] * 3,
                   rowLabels=self.model.row_labels,
                   colLabels=self.model.col_labels,
                    loc='center'
                   )
        self.view.tableAx.text(12, 3.4, 'redshift and error', size=8)
    def controlFunc(self,label):

        if label == 'Skyline':
            self.skyLine.set_visible(not self.skyLine.get_visible())
        elif label == 'Flux':
            self.fluxLine.set_visible(not self.fluxLine.get_visible())
        elif label == 'Model':
            self.modelLine.set_visible(not self.modelLine.get_visible())

        elif label == 'Emission':
            #print('em clicked')
            for l in self.eLines:
                #print(l[1].get_visible())
                l[1].set_visible(not l[1].get_visible())
                l[0].set_visible(l[1].get_visible())
        elif label == 'Absorption':
            #print('ab clicked')

            for l in self.aLines:
                #print(l[1].get_visible())
                l[1].set_visible(not l[1].get_visible())
                l[0].set_visible(l[1].get_visible())

        elif label == 'A or E':
            #print('ae clicked')
            for l in self.aeLines:
                #print(l[1].get_visible())
                l[1].set_visible(not l[1].get_visible())
                l[0].set_visible(l[1].get_visible())
        elif label == 'Other':
            #print('other clicked')
            for l in self.otherLines:
                #print(l[1].get_visible())
                l[1].set_visible(not l[1].get_visible())
                l[0].set_visible(l[1].get_visible())
        plt.draw()
    def run(self):

        self.view.checkBtns.on_clicked(self.controlFunc)
        # assign the callback function controlFunc to the radio buttons

        extraString = 'z= '+str(self.model.zObj.ZAVG)
        # create the string as label to show the redshift/ ZAVG is the average value of redshift in zObj
        handles, labels = self.view.graphAx.get_legend_handles_labels()
        # get a handle of the legend
        handles.append(mpatches.Patch(color='none', label=extraString))
        #attatch the z string on the legend
        self.view.graphAx.legend(handles=handles)

        #self.view.graphAx.legend()
        self.view.show()
        # show the graphAx and buttons in a matplotlib.pyplot figure
        #self.controlFunc('Other')
    def windowRun(self,skyline ,flux,
                  model,residual,
                  emission,absorption,
                ae,other):
        # take bool value as flag in order to determine which line to show.
        # all line object was constructed into controller class in the initiation
        if not skyline:
            self.skyLine.remove()
            # if a flag is false, then remove the line from the axis it resides in
        if not flux:
            self.fluxLine.remove()

        if not model:
            self.modelLine.remove()

        if not residual:
            self.residualLine.remove()

        if not emission:
            for l in self.eLines:
                # eLines is a list of (key,value) pair
                # a key is the name of the line
                # a value is a tuple (position,height) denoting the location of annotation
                # aLine and aeLines are similarly constructed
            # print(l[1].get_visible())
                l[1].remove()
                l[0].remove()
        if not absorption:
            for l in self.aLines:
            # print(l[1].get_visible())
                l[1].remove()
                l[0].remove()
        if not ae:
            for l in self.aeLines:
            # print(l[1].get_visible())
                l[1].remove()
                l[0].remove()
        if not other:
            for l in self.otherLines:
            # print(l[1].get_visible())
                l[1].remove()
                l[0].remove()
        # for l in self.aLines:
        #     # print(l[1].get_visible())
        #     l[1].set_visible(absorption)
        #     l[0].set_visible(absorption)
        # for l in self.aeLines:
        #     # print(l[1].get_visible())
        #     l[1].set_visible(ae)
        #     l[0].set_visible(ae)
        # for l in self.otherLines:
        #     # print(l[1].get_visible())
        #     l[1].set_visible(other)
        #     l[0].set_visible(other)
        # extraString = 'z= '+str(self.model.zObj.ZAVG)
        # handles, labels = self.view.graphAx.get_legend_handles_labels()
        # handles.append(mpatches.Patch(color='none', label=extraString))
        # self.view.graphAx.legend(handles=handles)
        #self.view.graphAx.legend()
        plotly_fig=self.view.returnPlotlyFig()
        # get the plotly figure

        for a in plotly_fig['layout']["annotations"]:
            a.update({
            "showarrow": True
        })
        # plotly_figure will hide the annotations, so manualy override in here
        plotly_fig['layout']['title'] = 'z= '+str(self.model.zObj.ZAVG)

        # plotly_fig['layout']["annotations"][0].update({
        #     "showarrow": True
        # })

        plotly.offline.plot(plotly_fig, auto_open=True, filename='figure.html')
        #webbrowser.open(filename, new=1)

        FileLink('./figure.html')  # lists all downloadable files on server

