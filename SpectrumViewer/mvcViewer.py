import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
from SpectrumViewer import spectral_lines_info
import SpectrumViewer.dataDriver as driver
from SpectrumViewer.data_models import Medium, Stream2D, SpectrumLineGrid, SpectrumLine
import SpectrumViewer
import matplotlib.patches

from collections import OrderedDict
import matplotlib.text
import numpy as np
import matplotlib.transforms as transforms
import copy

class MvcViewer:
    def __init__(self, width=10, height= 7, dpi = 100):
        #self.streams = OrderedDict()
        #self.spectral_lines_grids = OrderedDict()
        self.spectral_lines_info = spectral_lines_info
        self.view = V.SpecView(width, height, dpi)
        #self.view.select_all_button_callback = self.select_all_button_callback
        self.view.select_all_button.on_clicked(self.select_all_button_callback)
        self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())


    def add_stream(self, data_stream, display_name=None, data_stream_style={}):
        #check that streams are not already stored

        new_stream_dicts = driver.load_new_streams(self.model.streams, data_stream, display_name, data_stream_style)
        for stream_name in new_stream_dicts:
            self.model.streams[stream_name] = new_stream_dicts[stream_name]


    def add_spectral_lines_grid(self, spectral_lines_names = None, spectral_lines_grid_name=None, redshift=0.0, medium=Medium.AIR, color="lightblue", alpha=0.3, linewidth=1):
        #check that streams are not already stored

        new_spectral_lines_grid, new_spectral_lines_name = driver.load_new_spectral_lines_grid(self.model.streams, spectral_lines_names, spectral_lines_grid_name, redshift, medium, color, alpha, linewidth)
        self.model.streams[new_spectral_lines_name] = new_spectral_lines_grid

    def add_stream2d(self, data_stream, replace=False):
        #check that streams are not already stored

        new_stream_array = driver.load_new_stream2d(self.model.streams, data_stream, replace)
        for new_stream in new_stream_array:
            self.model.streams[new_stream.name] = new_stream


    def remove_stream(self, stream_name):
        if stream_name not in self.model.streams.keys():
            raise NameError("Stream named '"+ str(stream_name) + "' does not exist")
        else:
            self.model.streams.pop(stream_name)

            # remove plot objects from figure in view: stremas and text
            plots = self.view.stream_plots[stream_name]
            print(plots)
            if type(plots) == list:
                if type(plots[0]) == matplotlib.patches.Polygon:
                    for plot in plots:
                        plot.remove()
            else:
                plots.remove()
            eraseme = self.view.stream_plots.pop(stream_name)

            print("if not none")
            if stream_name in self.view.stream_plots_texts and self.view.stream_plots_texts[stream_name] is not None:
                texts = self.view.stream_plots_texts[stream_name]
                print(texts)
                if type(texts) == list and len(texts) > 0:
                    if type(texts[0]) == matplotlib.text.Text:
                        for text in texts:
                            text.remove()
                eraseme = self.view.stream_plots_texts.pop(stream_name)
            #self.view.stream_plots[stream_name].remove()


        self.plot_all()

    def plot(self, create_new_plot=False):
        if create_new_plot:
            self.view = V2.SpecView()
            #self.view.select_all_button_callback = self.select_all_button_callback
        self.plot_all()

    def add_rectangle_select_callback(self, rectangle_select_callback):
        self.view.load_rectangle_selector(callback_function=rectangle_select_callback)

    def get_data_within_rectangle(self, rectangle_boundaries):
        data_within_rectangle = OrderedDict()
        if rectangle_boundaries is None:
            rectangle_boundaries = self.view.rectangle_boundaries
        print("rect bound = " + str(rectangle_boundaries))
        if rectangle_boundaries is not None and type(rectangle_boundaries) == SpectrumViewer.data_models.RectangleBoundaries:
            bounds = self.view.rectangle_boundaries
            for stream_name in self.model.streams:

                print("rect bound = " + str(rectangle_boundaries) + " " + str(type(self.model.streams[stream_name])))

                if type(self.model.streams[stream_name]) == SpectrumViewer.data_models.Stream2D:
                    stream = self.model.streams[stream_name]
                    if not (  bounds.x2 < np.min(stream.x_coords) or bounds.x1 > np.max(stream.x_coords) or \
                              bounds.y2 < np.min(stream.y_coords) or bounds.y1 > np.max(stream.y_coords) ):

                        x_coords = stream.x_coords[(  (stream.x_coords >= bounds.x1) & (stream.x_coords <= bounds.x2) & (stream.y_coords >= bounds.y1) & (stream.y_coords <= bounds.y2) )]
                        y_coords = stream.y_coords[(  (stream.x_coords >= bounds.x1) & (stream.x_coords <= bounds.x2) & (stream.y_coords >= bounds.y1) & (stream.y_coords <= bounds.y2) )]
                        new_stream = Stream2D(x_coords,y_coords,stream_name,stream.color, stream.linewidth, stream.alpha)
                        data_within_rectangle[stream_name] = new_stream

                elif type(self.model.streams[stream_name]) == SpectrumViewer.data_models.SpectrumLineGrid:
                    spec_line_grid = self.model.streams[stream_name]
                    new_spec_line_grid = SpectrumLineGrid()
                    for spec_line_name in spec_line_grid.grid.keys():
                        spec_line = spec_line_grid.grid[spec_line_name]
                        if not (spec_line.lambda2 < bounds.x1 or spec_line.lambda1 > bounds.x2):
                            print("")
                            new_spec_line = copy.deepcopy(spec_line)
                            if new_spec_line.lambda1 <= bounds.x2 and new_spec_line.lambda2 >= bounds.x2:
                                new_spec_line.lambda2 = bounds.x2
                            if new_spec_line.lambda1 <= bounds.x1 and new_spec_line.lambda2 >= bounds.x1:
                                new_spec_line.lambda1 = bounds.x1
                            new_spec_line_grid.grid[spec_line_name] = new_spec_line

                    data_within_rectangle[stream_name] = new_spec_line_grid

                else:
                    raise Exception("stream type not known")
        return data_within_rectangle






    def get_axes(self):
        return self.view.graphAx

    def select_all_button_callback(self, event):
        #print(" from self.select_all_button_callback: " + str(event))
        is_active = self.view.checkBtns.get_status()
        if sum(is_active) == 0 or sum(is_active) == len(is_active):
            for i in range(len(is_active)):
                self.view.checkBtns.set_active(i)
        else:
            for i in range(len(is_active)):
                if not is_active[i]:
                    self.view.checkBtns.set_active(i)


    def delete_unchecked_button_callback(self, event):
        is_active = self.view.checkBtns.get_status()
        labels = self.view.checkbox_labels.copy()
        for i in range(len(is_active)):
            if not is_active[i]:
                print('removing '+ labels[i])
                self.remove_stream(labels[i])
                print('finished removing '+ labels[i])


    def set_x_label(self, x_label):
        self.view.graphAx.set_xlabel(x_label)

    def set_y_label(self, y_label):
        self.view.graphAx.set_xlabel(y_label)

    def plot_all(self):

        #deleting previous plots
        self.view.legend_colors = OrderedDict()
        if self.view.legend is not None:
            self.view.legend.remove()
        for old_stream_name in self.view.stream_plots.keys():
            #plot_object = self.view.stream_plots[old_stream_name]
            #plot_object.remove()

            plots = self.view.stream_plots[old_stream_name]
            if type(plots) == list:
                if type(plots[0]) == matplotlib.patches.Polygon:
                    for plot in plots:
                        plot.remove()
            else:
                plots.remove()

            if old_stream_name in self.view.stream_plots_texts:
                texts = self.view.stream_plots_texts[old_stream_name]
                if type(texts) == list:
                    if type(texts[0]) == matplotlib.text.Text:
                        for text in texts:
                            text.remove()




        # adding new streams
        self.view.load_main_axes()
        x_range = [np.Inf,-np.Inf]
        y_range = [np.Inf, -np.Inf]
        num_spec_lines = len(spectral_lines_info)
        for stream_name in self.model.streams.keys():
            stream = self.model.streams[stream_name]
            if type(stream) == SpectrumViewer.data_models.Stream2D:
                x_range[0] = min(x_range[0],min(stream.x_coords))
                x_range[1] = max(x_range[1],max(stream.x_coords))
                y_range[0] = min(y_range[0],min(stream.y_coords))
                y_range[1] = max(y_range[1],max(stream.y_coords))
        place_line_text_up = 1

        transform = transforms.blended_transform_factory(self.view.graphAx.transData, self.view.graphAx.transAxes)

        for stream_name in self.model.streams.keys():

            stream = self.model.streams[stream_name]
            if type(stream) == SpectrumViewer.data_models.Stream2D:
                color = stream.color
                alpha = stream.alpha
                linewidth = stream.linewidth
                plot_object = self.view.graphAx.plot(stream.x_coords ,stream.y_coords,color=color,label=stream_name, alpha=alpha, linewidth=linewidth)
                self.view.stream_plots[stream_name] = plot_object[0]
                self.view.stream_plots_texts[stream_name] = None
                self.view.legend_colors[stream_name] = color

            elif type(stream) == SpectrumViewer.data_models.SpectrumLineGrid:
                plot_object = []
                plot_text_object = []
                for spectrum_line_name in stream.grid:
                    specline = stream.grid[spectrum_line_name]
                    color = specline.color
                    alpha = specline.alpha
                    linewidth = specline.linewidth

                    po = self.view.graphAx.axvspan(specline.lambda1, specline.lambda2, color=color,label=spectrum_line_name, alpha=alpha, linewidth=linewidth)
                    plot_object.append(po)

                    if (specline.lambda1+specline.lambda2)/2.0 <= x_range[1]+(x_range[1]-x_range[0])/20.0 and \
                       (specline.lambda1+specline.lambda2)/2.0 >= x_range[0]-(x_range[1]-x_range[0])/20.0:
                        if place_line_text_up ==1 :
                            ycoord = 0.05
                            place_line_text_up = 2
                        elif place_line_text_up ==2:
                            ycoord = 0.07
                            place_line_text_up = 3
                        elif place_line_text_up ==3:
                            ycoord = 0.03
                            place_line_text_up = 1
                        pt = self.view.graphAx.text( (specline.lambda1+specline.lambda2)/2.0, ycoord, s=spectrum_line_name, color="black",label=spectrum_line_name, alpha=1.0, fontsize="xx-small", transform=transform)
                        plot_text_object.append(pt)


                self.view.stream_plots[stream_name] = plot_object
                self.view.stream_plots_texts[stream_name] = plot_text_object
                self.view.legend_colors[stream_name] = color

            else:
                raise TypeError("Stream type "+ str(type(stream)) + " not supported")

        if x_range[0] != np.inf and x_range[0] != -np.inf:
            self.view.graphAx.set_xlim(x_range[0]-(x_range[1]-x_range[0])/20.0,x_range[1]+(x_range[1]-x_range[0])/20.0)
        # reinitializing the check buttons
        #self.view.load_side_panel(num_buttons = len(self.model.streams))

        self.view.checkbox_labels     = [ stream_name for stream_name in self.model.streams.keys() ]
        #self.view.checkbox_labels = ["\n".join(textwrap.wrap(stream_name,8))  for stream_name in self.model.streams.keys()]
        self.view.checkbox_visibility = [        True for stream_name in self.model.streams.keys() ]
        #self.view.spec_line_grid_names = [ stream_name        True for stream_name in self.model.streams.keys()    ]

        self.view.loadCheckButtons()
        self.view.checkBtns.on_clicked(self.view.toggle_streams)

        # make legend:
        #self.view.legend = self.view.graphAx.legend(ncol=self.number_of_plots, framealpha=0, handlelength=0)
        #texts = self.view.legend.get_texts()
        #for t in range(len(texts)):
        #    name = self.plot_names[t]
        #    texts[t].set_color(self.view.legend_colors[name])


        # assign the callback function controlFunc to the radio buttons

        #extraString = ""
        #for ind in range(self.number_of_objects):
        #    extraString = extraString + 'z' + str(ind)+ ' = '+str(self.model.zObj[ind].ZAVG) + ", "

        #extraString = extraString[:-2]

        # create the string as label to show the redshift/ ZAVG is the average value of redshift in zObj
        #handles, labels = self.view.graphAx.get_legend_handles_labels()
        # get a handle of the legend
        #handles.append(mpatches.Patch(color='black', label=extraString))
        #attatch the z string on the legend
        #self.view.graphAx.legend(handles=handles, ncol=self.number_of_objects, framealpha=0, handlelength=0)

        #self.view.figure.suptitle(extraString)


        #self.view.graphAx.legend()
        self.view.show()
        # show the graphAx and buttons in a matplotlib.pyplot figure
        #self.controlFunc('Other')



