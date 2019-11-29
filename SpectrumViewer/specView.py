import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.text
#from matplotlib.widgets import CheckButtons, RadioButtons
from .widgets import CheckButtons, RectangleSelector, Button
import plotly.tools as tls
import mpld3
from collections import OrderedDict
from SpectrumViewer.data_models import RectangleBoundaries

class SpecView:

    __main_ax_left_bottom_x = 0.15
    __main_ax_left_bottom_y = 0.1
    __main_ax_width = 0.82
    __main_ax_height = 0.88

    def __init__(self, width=10, height= 7, dpi = 100):
        #self.figure = plt.figure("", figsize=(10, 8), dpi=100)
        self.figure, axis = plt.subplots(figsize=(width, height), dpi=dpi)
        axis.set_axis_off()
        #self.figure = plt.subplots()

        self.load_main_axes()
        self.load_control_buttons()

        #self.load_side_panel()
        #self.rax = self.graphAx

        self.stream_plots  = OrderedDict() # saves the plot objects
        self.stream_plots_texts  = OrderedDict() # saves the plot objects plotted texts
        self.legend_colors = OrderedDict()
        self.plot_names = []
        self.legend = None

        # iniialize a seperate axes object that will be used to contain radio buttons
        self.checkbox_visibility = []
        self.checkbox_labels     = []
        #self.checkBtns = CheckButtons(self.rax, ('Skyline','Flux','Model','Residual','Emission','Absorption','A or E','Other'),(True, True, True,True,False,False,False,False))
        self.loadCheckButtons()

        self.rectangle_boundaries = None
        self.rectangle_selector_callback = None
        self.load_rectangle_selector()

        #self.checkbuttons = {}
        #self.checkbuttons_visibility = {}
        #self.checkbuttons_labels = {}

        # create buttons with tags: 'Skyline',
        #                                                  'Flux',
        #                                                  'Model',
        #                                                  'Emission',
        #                                                  'Absorption',
        #                                                  'A or E',
        #                                                  'Other')
        # and default value
        # when the check buttons was clicked, the gadget will call the callback function with the tag as argument

    def load_control_buttons(self):

        if not hasattr(self, 'select_all_button_axes'):
            rect = [0.16, 0.95, 0.13, 0.04]
            self.select_all_button_axes = self.figure.add_axes(rect)
            self.select_all_button_axes.set_xticks([])
            self.select_all_button_axes.set_yticks([])
            #self.select_all_button_axes.patch.set_alpha(0.0)

            self.select_all_button = Button(self.select_all_button_axes, 'check/uncheck all')
            #self.select_all_button_callback = lambda x: print("Event= " + str(x))
            #self.select_all_button.on_clicked(self.select_all_button_callback)


        if not hasattr(self, 'delete_unchecked_axes'):
            rect = [0.3, 0.95, 0.13, 0.04]
            self.delete_unchecked_axes = self.figure.add_axes(rect)
            self.delete_unchecked_axes.set_xticks([])
            self.delete_unchecked_axes.set_yticks([])

            self.delete_unchecked_button = Button(self.delete_unchecked_axes, 'delete unchecked')
            #self.select_all_button_callback = lambda x: print("Event= " + str(x))
            #self.select_all_button.on_clicked(self.select_all_button_callback)






    def loadCheckButtons(self):
        self.checkBtns = CheckButtons(ax=self.graphAx, labels=self.checkbox_labels, x1=0.02, y1=0.99, actives= self.checkbox_visibility)

    def load_rectangle_selector(self, callback_function=None):
        if callback_function is not None:
            self.rectangle_selector_callback = callback_function
        self.rectangle_selector = RectangleSelector(self.graphAx, self.load_rectangle_boundaries,
                                                    drawtype='box', useblit=True,
                                                    button=[1, 3],  # don't use middle button
                                                    minspanx=5, minspany=5,
                                                    spancoords='pixels',
                                                    interactive=True)
        plt.connect('key_press_event', self.toggle_rectangle_selector)

    def toggle_rectangle_selector(self, event):
        #print(event.key, self.rectangle_selector.active)
        #if event.key in ['Q', 'q'] and self.rectangle_selector.active:
        if event.key in ['r', 'R'] and self.rectangle_selector.active:
            #print(' RectangleSelector deactivated.')
            self.rectangle_selector.set_active(False)
            self.rectangle_selector.set_visible(False)
        if event.key in ['t', 'T'] and not self.rectangle_selector.active:
            #print(' RectangleSelector activated.')
            self.rectangle_selector.set_active(True)
            self.rectangle_selector.set_visible(True)

    def load_rectangle_boundaries(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.rectangle_boundaries = RectangleBoundaries(x1,y1,x2,y2)
        #print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        #print(x1,y1,x2,y2)
        #print(" The button you used were: %s %s" % (eclick.button, erelease.button))
        if self.rectangle_selector_callback is not None:
            #print("beg")
            self.rectangle_selector_callback(self.rectangle_boundaries)
            #print("end")
        #print(" The button you used were: %s %s" % (eclick.button, erelease.button))


    def show(self):

        #self.figure.canvas.mpl_connect('draw_event', self.on_draw)
        plt.draw()
        plt.show()
        #plt is the matplotlib state machine interface, once imported to the interpreter, can be used accross the code
        # show whatever has been passed to the state machine in previous program.
        #mpld3.show(fig=self.figure, ip='127.0.0.1', port=8888, n_retries=50, local=True, open_browser=True, http_server=None)
        #TODO : change the display mode to cell mode

    def load_main_axes(self):
        c= """
        self.graphAx = self.figure.add_axes([self.__main_ax_left_bottom_x, self.__main_ax_left_bottom_y, self.__main_ax_width, self.__main_ax_height],aspect="equal")
        #self.graphAx = self.figure.add_axes([0.1, 0.1, 0.88, 0.88])
        self.graphAx.spines['right'].set_visible(False)
        self.graphAx.spines['top'].set_visible(False)
        # Only show ticks on the left and bottom spines
        self.graphAx.yaxis.set_ticks_position('left')
        self.graphAx.xaxis.set_ticks_position('bottom')
        self.graphAx.patch.set_alpha(0.0)
        self.graphAx.set_xlabel(r'$\lambda $ [${\AA}$]')
        self.graphAx.set_ylabel(r'10$^{-17}$ ergs s$^{-1}$ cm$^{-2}$ $\AA^{-1}$')
        """

        rect = [self.__main_ax_left_bottom_x, self.__main_ax_left_bottom_y, self.__main_ax_width, self.__main_ax_height]
        if hasattr(self, 'graphAx'):
            plt.show()
            self.graphAx.clear()
            self.graphAx.set_position(rect)
        else:
            self.graphAx = self.figure.add_axes(rect)

        #self.graphAx.tick_params(axis=u'both', which=u'both')
        #self.rax = self.figure.add_axes(rect)
        #self.rax.set_aspect('equal')
        #self.graphAx.set_xlabel(r'$\lambda $ [${\AA}$]')
        #self.graphAx.set_ylabel(r'10$^{-17}$ ergs s$^{-1}$ cm$^{-2}$ $\AA^{-1}$')

        self.graphAx.set_xlabel(r'wavelength', fontsize="large")
        self.graphAx.set_ylabel(r'flux', fontsize="large")


        self.graphAx.spines['right'].set_visible(False)
        self.graphAx.spines['top'].set_visible(False)
        #self.graphAx.yaxis.set_ticks_position('left')
        #self.graphAx.xaxis.set_ticks_position('bottom')
        self.graphAx.patch.set_alpha(0.5)

    def toggle_streams(self,label):
        plots = self.stream_plots[label]
        if type(plots) == list:
            if type(plots[0]) == matplotlib.patches.Polygon:
                for plot in plots:
                    plot.set_visible(not plot.get_visible())
        else:
            self.stream_plots[label].set_visible(not self.stream_plots[label].get_visible())

        texts = self.stream_plots_texts[label]

        if type(texts) == list:
            #print(type(texts[0]))
            if type(texts[0]) == matplotlib.text.Text:
                #print(texts)
                for text in texts:
                    text.set_visible(not text.get_visible())
        plt.draw()





