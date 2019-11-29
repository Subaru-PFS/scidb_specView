import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly
from IPython.display import FileLink, FileLinks
import plotly.graph_objs as go
import webbrowser
from colour import Color

class SpecController:

    def __init__(self,model,view):
        #if not isinstance(model, Iterable):
        #    model = list(model)
        self.number_of_objects = model.number_of_objects
        self.model = model
        # take SpecModel object as argument to initialize
        self.view = view
        # take SpecView or a windowView object as argument to initialize

        self.fluxLine       = [None for i in range(self.number_of_objects)]
        self.skyLine        = [None for i in range(self.number_of_objects)]
        self.modelLine      = [None for i in range(self.number_of_objects)]
        self.residualLine   = [None for i in range(self.number_of_objects)]
        self.aLines         = [None for i in range(self.number_of_objects)]
        self.eLines         = [None for i in range(self.number_of_objects)]
        self.aeLines        = [None for i in range(self.number_of_objects)]
        self.otherLines     = [None for i in range(self.number_of_objects)]

        self.flux_colors      = [ a.get_hex() for a in list(Color("#A11814").range_to(Color("#FFB5A1"),self.number_of_objects)) ] # shades of red
        self.skyline_colors   = [ a.get_hex() for a in list(Color("#0A237F").range_to(Color("#A2C1FF"),self.number_of_objects)) ] # shades of blue
        self.model_colors     = [ a.get_hex() for a in list(Color("#074111").range_to(Color("#8FCC95"),self.number_of_objects)) ] # shades of green
        self.residual_colors  = [ a.get_hex() for a in list(Color("#3E2804").range_to(Color("#C7B697"),self.number_of_objects)) ] # shades of brown

        self.num_shown_graph_per_object = 4  # those are: flux, sky, model and residual
        self.legend_colors = []
        for ind in range(self.number_of_objects):

            self.fluxLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getFluxline(ind),self.flux_colors[ind],label='flux'+str(ind+1), alpha=0.8, linewidth=0.6 )
            self.skyLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getSkyline(ind), self.skyline_colors[ind], label='sky'+str(ind+1), alpha=0.8, linewidth=0.6)
            self.modelLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getModelline(ind), self.model_colors[ind], label='model'+str(ind+1), alpha=0.8, linewidth=0.6)
            self.residualLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getResidualline(ind), self.residual_colors[ind], label='residual'+str(ind+1), alpha=0.8, linewidth=0.6)

            self.legend_colors.append(self.flux_colors[ind])
            self.legend_colors.append(self.skyline_colors[ind])
            self.legend_colors.append(self.model_colors[ind])
            self.legend_colors.append(self.residual_colors[ind])


                #initilize the line object by calling plot function in axes object
            self.aLines[ind]=[]
            self.eLines[ind] = []
            self.aeLines[ind] = []
            self.otherLines[ind] = []
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
            self.eLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                            self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.eline[ind].items()]
            # create a list tuple (text, position)
            # val0 position,val1 height, key name
            self.aLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                            self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.aline[ind].items()]
            self.aeLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                             self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.aeline[ind].items()]
            self.otherLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                                self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.otherline[ind].items()]

        # make legend:
        leg = self.view.graphAx.legend(ncol=self.number_of_objects, framealpha=0, handlelength=0)
        texts = leg.get_texts()
        for t in range(len(texts)):
            texts[t].set_color(self.legend_colors[t])



    def plotTable(self):
        for ind in range(self.number_of_objects):
            self.view.tableAx.table(cellText=self.model.table_vals[ind],
                       colWidths=[0.1] * 3,
                       rowLabels=self.model.row_labels[ind],
                       colLabels=self.model.col_labels[ind],
                        loc='center'
                       )
            self.view.tableAx.text(12, 3.4, 'redshift and error', size=8)

    def controlFunc(self,label):
        for ind in range(self.number_of_objects):
            if label == 'Skyline':
                self.skyLine[ind].set_visible(not self.skyLine[ind].get_visible())
            elif label == 'Flux':
                self.fluxLine[ind].set_visible(not self.fluxLine[ind].get_visible())
            elif label == 'Residual':
                self.residualLine[ind].set_visible(not self.residualLine[ind].get_visible())
            elif label == 'Model':
                self.modelLine[ind].set_visible(not self.modelLine[ind].get_visible())

            elif label == 'Emission':
                #print('em clicked')
                for l in self.eLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())
            elif label == 'Absorption':
                #print('ab clicked')

                for l in self.aLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())

            elif label == 'A or E':
                #print('ae clicked')
                for l in self.aeLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())
            elif label == 'Other':
                #print('other clicked')
                for l in self.otherLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())

        plt.draw()

    def run(self):

        self.view.checkBtns.on_clicked(self.controlFunc)
        # assign the callback function controlFunc to the radio buttons

        extraString = ""
        for ind in range(self.number_of_objects):
            extraString = extraString + 'z' + str(ind)+ ' = '+str(self.model.zObj[ind].ZAVG) + ", "

        extraString = extraString[:-2]

        # create the string as label to show the redshift/ ZAVG is the average value of redshift in zObj
        #handles, labels = self.view.graphAx.get_legend_handles_labels()
        # get a handle of the legend
        #handles.append(mpatches.Patch(color='black', label=extraString))
        #attatch the z string on the legend
        #self.view.graphAx.legend(handles=handles, ncol=self.number_of_objects, framealpha=0, handlelength=0)

        self.view.figure.suptitle(extraString)


        #self.view.graphAx.legend()
        self.view.show()
        # show the graphAx and buttons in a matplotlib.pyplot figure
        #self.controlFunc('Other')

    def windowRun(self,skyline ,flux,
                  model,residual,
                  emission,absorption,
                ae,other):

        for ind in range(self.number_of_objects):
            # take bool value as flag in order to determine which line to show.
            # all line object was constructed into controller class in the initiation
            if not skyline:
                self.skyLine[ind].remove()
                # if a flag is false, then remove the line from the axis it resides in
            if not flux:
                self.fluxLine[ind].remove()

            if not model:
                self.modelLine[ind].remove()

            if not residual:
                self.residualLine[ind].remove()

            if not emission:
                for l in self.eLines[ind]:
                    # eLines is a list of (key,value) pair
                    # a key is the name of the line
                    # a value is a tuple (position,height) denoting the location of annotation
                    # aLine and aeLines are similarly constructed
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not absorption:
                for l in self.aLines[ind]:
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not ae:
                for l in self.aeLines[ind]:
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not other:
                for l in self.otherLines[ind]:
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

        #for a in plotly_fig['layout']["annotations"]:
        #    a.update({
        #    "showarrow": True
        #})

        # plotly_figure will hide the annotations, so manualy override in here
        title = ""
        for ind in range(self.number_of_objects):
            title = title + 'z' + str(ind)+ ' = '+str(self.model.zObj[ind].ZAVG) + ", "

        title = title[:-2]
        plotly_fig['layout']['title'] = title


        # plotly_fig['layout']["annotations"][0].update({
        #     "showarrow": True
        # })

        plotly.offline.plot(plotly_fig, auto_open=True, filename='figure.html')
        #webbrowser.open(filename, new=1)

        FileLink('./figure.html')  # lists all downloadable files on server



##############################################################################################################################
##############################################################################################################################
##############################################################################################################################


class SpecController2:

    def __init__(self,model,view):
        #if not isinstance(model, Iterable):
        #    model = list(model)
        self.number_of_objects = model.number_of_objects
        self.model = model
        # take SpecModel object as argument to initialize
        self.view = view
        # take SpecView or a windowView object as argument to initialize

        self.fluxLine       = [None for i in range(self.number_of_objects)]
        self.skyLine        = [None for i in range(self.number_of_objects)]
        self.modelLine      = [None for i in range(self.number_of_objects)]
        self.residualLine   = [None for i in range(self.number_of_objects)]
        self.aLines         = [None for i in range(self.number_of_objects)]
        self.eLines         = [None for i in range(self.number_of_objects)]
        self.aeLines        = [None for i in range(self.number_of_objects)]
        self.otherLines     = [None for i in range(self.number_of_objects)]

        self.flux_colors      = [ a.get_hex() for a in list(Color("#A11814").range_to(Color("#FFB5A1"),self.number_of_objects)) ] # shades of red
        self.skyline_colors   = [ a.get_hex() for a in list(Color("#0A237F").range_to(Color("#A2C1FF"),self.number_of_objects)) ] # shades of blue
        self.model_colors     = [ a.get_hex() for a in list(Color("#074111").range_to(Color("#8FCC95"),self.number_of_objects)) ] # shades of green
        self.residual_colors  = [ a.get_hex() for a in list(Color("#3E2804").range_to(Color("#C7B697"),self.number_of_objects)) ] # shades of brown

        self.num_shown_graph_per_object = 4  # those are: flux, sky, model and residual
        self.legend_colors = []
        for ind in range(self.number_of_objects):

            self.fluxLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getFluxline(ind),self.flux_colors[ind],label='flux'+str(ind+1), alpha=0.8, linewidth=0.6 )
            self.skyLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getSkyline(ind), self.skyline_colors[ind], label='sky'+str(ind+1), alpha=0.8, linewidth=0.6)
            self.modelLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getModelline(ind), self.model_colors[ind], label='model'+str(ind+1), alpha=0.8, linewidth=0.6)
            self.residualLine[ind], = self.view.graphAx.plot(self.model.lam[ind], self.model.getResidualline(ind), self.residual_colors[ind], label='residual'+str(ind+1), alpha=0.8, linewidth=0.6)

            self.legend_colors.append(self.flux_colors[ind])
            self.legend_colors.append(self.skyline_colors[ind])
            self.legend_colors.append(self.model_colors[ind])
            self.legend_colors.append(self.residual_colors[ind])


                #initilize the line object by calling plot function in axes object
            self.aLines[ind]=[]
            self.eLines[ind] = []
            self.aeLines[ind] = []
            self.otherLines[ind] = []
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
            self.eLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                            self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.eline[ind].items()]
            # create a list tuple (text, position)
            # val0 position,val1 height, key name
            self.aLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                            self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.aline[ind].items()]
            self.aeLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                             self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.aeline[ind].items()]
            self.otherLines[ind] = [[self.view.graphAx.text(val[0], val[1]+baseoffset, key, rotation=90, visible=False),
                                self.view.graphAx.arrow(val[0], val[1]+baseoffset, 0, vOffset, width=0.5, visible=False)]
                           for key, val in self.model.otherline[ind].items()]

        # make legend:
        leg = self.view.graphAx.legend(ncol=self.number_of_objects, framealpha=0, handlelength=0)
        texts = leg.get_texts()
        for t in range(len(texts)):
            texts[t].set_color(self.legend_colors[t])



    def plotTable(self):
        for ind in range(self.number_of_objects):
            self.view.tableAx.table(cellText=self.model.table_vals[ind],
                       colWidths=[0.1] * 3,
                       rowLabels=self.model.row_labels[ind],
                       colLabels=self.model.col_labels[ind],
                        loc='center'
                       )
            self.view.tableAx.text(12, 3.4, 'redshift and error', size=8)

    def controlFunc(self,label):
        for ind in range(self.number_of_objects):
            if label == 'Skyline':
                self.skyLine[ind].set_visible(not self.skyLine[ind].get_visible())
            elif label == 'Flux':
                self.fluxLine[ind].set_visible(not self.fluxLine[ind].get_visible())
            elif label == 'Residual':
                self.residualLine[ind].set_visible(not self.residualLine[ind].get_visible())
            elif label == 'Model':
                self.modelLine[ind].set_visible(not self.modelLine[ind].get_visible())

            elif label == 'Emission':
                #print('em clicked')
                for l in self.eLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())
            elif label == 'Absorption':
                #print('ab clicked')

                for l in self.aLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())

            elif label == 'A or E':
                #print('ae clicked')
                for l in self.aeLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())
            elif label == 'Other':
                #print('other clicked')
                for l in self.otherLines[ind]:
                    #print(l[1].get_visible())
                    l[1].set_visible(not l[1].get_visible())
                    l[0].set_visible(l[1].get_visible())

        plt.draw()

    def run(self):

        self.view.checkBtns.on_clicked(self.controlFunc)
        # assign the callback function controlFunc to the radio buttons

        extraString = ""
        for ind in range(self.number_of_objects):
            extraString = extraString + 'z' + str(ind)+ ' = '+str(self.model.zObj[ind].ZAVG) + ", "

        extraString = extraString[:-2]

        # create the string as label to show the redshift/ ZAVG is the average value of redshift in zObj
        #handles, labels = self.view.graphAx.get_legend_handles_labels()
        # get a handle of the legend
        #handles.append(mpatches.Patch(color='black', label=extraString))
        #attatch the z string on the legend
        #self.view.graphAx.legend(handles=handles, ncol=self.number_of_objects, framealpha=0, handlelength=0)

        self.view.figure.suptitle(extraString)


        #self.view.graphAx.legend()
        self.view.show()
        # show the graphAx and buttons in a matplotlib.pyplot figure
        #self.controlFunc('Other')

    def windowRun(self,skyline ,flux,
                  model,residual,
                  emission,absorption,
                ae,other):

        for ind in range(self.number_of_objects):
            # take bool value as flag in order to determine which line to show.
            # all line object was constructed into controller class in the initiation
            if not skyline:
                self.skyLine[ind].remove()
                # if a flag is false, then remove the line from the axis it resides in
            if not flux:
                self.fluxLine[ind].remove()

            if not model:
                self.modelLine[ind].remove()

            if not residual:
                self.residualLine[ind].remove()

            if not emission:
                for l in self.eLines[ind]:
                    # eLines is a list of (key,value) pair
                    # a key is the name of the line
                    # a value is a tuple (position,height) denoting the location of annotation
                    # aLine and aeLines are similarly constructed
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not absorption:
                for l in self.aLines[ind]:
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not ae:
                for l in self.aeLines[ind]:
                # print(l[1].get_visible())
                    l[1].remove()
                    l[0].remove()
            if not other:
                for l in self.otherLines[ind]:
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

        #for a in plotly_fig['layout']["annotations"]:
        #    a.update({
        #    "showarrow": True
        #})

        # plotly_figure will hide the annotations, so manualy override in here
        title = ""
        for ind in range(self.number_of_objects):
            title = title + 'z' + str(ind)+ ' = '+str(self.model.zObj[ind].ZAVG) + ", "

        title = title[:-2]
        plotly_fig['layout']['title'] = title


        # plotly_fig['layout']["annotations"][0].update({
        #     "showarrow": True
        # })

        plotly.offline.plot(plotly_fig, auto_open=True, filename='figure.html')
        #webbrowser.open(filename, new=1)

        FileLink('./figure.html')  # lists all downloadable files on server


