import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from specviewer import app, refresh_time
from jupyterlab_dash import AppViewer
from plotly.tools import mpl_to_plotly
from matplotlib import pyplot as plt

import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
from SpectrumViewer import spectral_lines_info
import SpectrumViewer.dataDriver as driver
# from SpectrumViewer.data_models import Medium, Spectrum, SpectrumLineGrid, SpectrumLine
import SpectrumViewer
from collections import OrderedDict
import matplotlib.text
import numpy as np
import matplotlib.transforms as transforms
import copy
from specviewer import controller as c

from specviewer import data_driver
from specviewer import app_layout, callbacks
from datetime import datetime

import json
from textwrap import dedent as d
from jupyterlab_dash import AppViewer
import dash
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import multiprocessing
import base64
import pandas as pd
import io
import json
from astropy.io import fits
import traceback
import dash_table
from pathlib import Path

process_manager = multiprocessing.Manager()
jupyter_viewer = AppViewer()
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# create global variable only for use inside jupyter
app_data = process_manager.dict()
debug_data = process_manager.dict()
app_data_timestamp = process_manager.dict()


#https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes
#https://stackoverflow.com/questions/17377426/shared-variable-in-pythons-multiprocessing
#https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Value

class Viewer():
    # app_data = {}

    def __init__(self, as_website=False):
        # global app_data
        # global fig
        self.as_website = as_website
        print("first " + str(self.as_website))
        # just for testing local website
        # self.app_data = {'traces':{}, 'selection':{}} #application_data.ApplicationData()
        # self.app_data = app_data
        self.app_data = app_data
        self.app_data_timestamp = app_data_timestamp
        self.app_data['traces'] = {}
        self.app_data['selection'] = {}
        self.app_data_timestamp['timestamp'] = 0
        self.debug_data = debug_data

        # self.spectral_lines_info = spectral_lines_info
        # self.view = V.SpecView(width, height, dpi)
        # self.view.select_all_button.on_clicked(self.select_all_button_callback)
        # self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        # self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())

        self.time2 = str(datetime.now())

        # self.spec_figure = make_subplots(rows=1, cols=1)
        # self.fill_spec_figure_with_app_data()
        self.spec_figure = self.get_spec_figure_from_data(self.app_data)

        #app.layout = self.load_app_layout
        app.layout = app_layout.load_app_layout(self)
        callbacks.load_callbacks(self)



    def parse_uploaded_file(self, contents, filename):

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        hdulist = fits.open(io.BytesIO(decoded))
        spectrum = data_driver.get_spectrum_from_fits(hdulist, filename)

        # name = filename + str(len(hdulist))
        # trace = self.build_trace(x_coords=[1,2,3,4], [float(np.random.random_sample()) for i in range(4)], filename)
        trace = self.build_trace(x_coords=[1, 2, 3, 4], y_coords=[float(np.random.random_sample()) for i in range(4)],
                                 name=filename)
        trace = self.build_trace(spectrum.wavelength, spectrum.flux, filename, color="black", linewidth=1, alpha=0.8)
        return filename, trace

    def update_figure_layout(self):
        time = str(datetime.now())
        self.spec_figure.update_layout(
            title={'text': "Plot Title", 'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
            xaxis_title="Wavelength", yaxis_title="y Axis Title",
            font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            title_text="A Bar Chart " + time, title_font_size=30, plot_bgcolor='rgb(250,250,250)',
            clickmode='event+select')

    def fill_spec_figure_with_app_data(self):
        a = """            
                    traces = self.app_data.get_traces()
                    for trace_name in self.app_data.get_traces():
                        spectrum = traces[trace_name]
                        scatter = go.Scatter(x=spectrum.wavelength, y=spectrum.flux, mode = "lines+markers",
                                             name = spectrum.name, marker = {'size': 12}, line = dict(color="blue"),
                                             text = ['a','b','c','d'],customdata = ['c.a', 'c.b', 'c.c', 'c.d'])
                        spec_figure.add_trace(scatter, row = 1, col = 1)
        """
        if not self.as_website:
            self.spec_figure = make_subplots(rows=1, cols=1)
            traces = self.app_data.get("traces", {})
            for trace_name in traces:
                scatter = go.Scattergl(x=traces[trace_name]['x_coords'], y=traces[trace_name]['y_coords'],
                                     mode="lines+markers",
                                     name=traces[trace_name]['name'], marker={'size': 12}, line=dict(color="blue"),
                                     text=['a', 'b', 'c', 'd'], customdata=['c.a', 'c.b', 'c.c', 'c.d'])
                self.spec_figure.add_trace(scatter, row=1, col=1)
            self.update_figure_layout()


        else:
            x = [1, 2, 3, 4]
            y = [4, 2.2, 1.5]
            name = "Trace 1"
            # trace = self.build_trace(wavelength=x, flux=y, name=name)
            # self.app_data['traces'][name] = trace
            scatter = go.Scattergl(x=x, y=y, mode="lines+markers",
                                 name=name, marker={'size': 12}, line=dict(color="blue"),
                                 text=['a', 'b', 'c', 'd'], customdata=['c.a', 'c.b', 'c.c', 'c.d'])
            self.spec_figure.add_trace(scatter, row=1, col=1)
            self.update_figure_layout()

    def get_spec_figure_from_data(self, data):
        # create figure with plotly api from data object
        figure = make_subplots(rows=1, cols=1)
        traces = data.get("traces", {})
        for trace_name in traces:
            scatter = go.Scattergl(x=traces[trace_name]['x_coords'], y=traces[trace_name]['y_coords'],
                                 mode="lines",
                                 name=traces[trace_name]['name'], marker={'size': 12}, line=dict(color="blue"),
                                 text=['a', 'b', 'c', 'd'], customdata=['c.a', 'c.b', 'c.c', 'c.d'])
            figure.add_trace(scatter, row=1, col=1)

        figure.update_layout(title={'text': "SpecViewer", 'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                             xaxis_title="Wavelength", yaxis_title="Flux",
                             font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
                             title_font_size=30, plot_bgcolor='rgb(250,250,250)',
                             clickmode='event+select')
        return figure.to_dict()

    def update_time(self):
        self.time2 = str(datetime.now())

    def load_callbacks(self):
        # from specviewer.callbacks import update_metrics, display_hover_data, display_click_data, display_relayout_data
        pass

    def show_jupyter_app(self):
        # self.load_callbacks()
        # app.layout = self.load_app_layout
        # app.layout = self.load_app_layout
        jupyter_viewer.show(app)

    def get_dropdown_options(self, application_data):
        traces = application_data['traces']
        options = [{'label': trace_name, 'value': trace_name} for trace_name in traces ]
        return options


    def synch_data(self,base_data_dict,incomplete_data_dict,do_update_client=False):
        #self.write_info("inc0  start " + str(incomplete_data_dict) + " " + str(base_data_dict))
        a = """
        for trace_name in base_data_dict['traces']:
            #self.write_info("inc0  trace  " +  trace_name + " " + str(incomplete_data_dict) + " " + str(base_data_dict))
            # if trace_name not in incomplete_data_dict['traces']:
            self.add_trace_to_data(incomplete_data_dict, trace_name, base_data_dict['traces'][trace_name], do_update_client=do_update_client)
            #self.write_info("inc0 "+ trace_name + str(incomplete_data_dict) )
        #self.write_info("inc0  end")
        """
        incomplete_data_dict['traces'] = base_data_dict['traces']
        if do_update_client:
            self.update_client()




    def add_trace_to_data(self, application_data, name, trace, do_update_client = True):
        traces = application_data['traces']
        #num_repeats = [name for name in traces].count(name)

        #if name in traces:
        #    name = name + "_copy"

        traces[name] = trace
        application_data['traces'] = traces

        if do_update_client:
            self.update_client()

        # self.app_data['traces'][name] = trace
        # if update_figure:
        #    self.fill_spec_figure_with_app_data(self.spec_figure)
        #    self.load_spec_figure(self.spec_figure)

    def add_trace(self, name, trace):
        print("Adding trace")
        return self.add_trace_to_data(self.app_data, name, trace, do_update_client = True)


    def _remove_traces(self, trace_names, data, do_update_client=True):
        traces = data['traces']
        for trace_name in trace_names:
            traces.pop(trace_name)
        data['traces'] = traces
        if do_update_client:
            self.update_client()


    def remove_trace(self, name):
        traces = self.app_data['traces']
        traces.pop(name)
        app_data['traces'] = traces
        self.update_client()

    def build_trace(self, x_coords=[], y_coords=[], name=None, parent=None, type=None, color="black", linewidth=1,
                    alpha=1.0):
        return {'name': name, 'x_coords': x_coords, 'y_coords': y_coords, 'type': type, 'parent': parent,
                'visible': True, 'color': color, 'linewidth': linewidth, 'alpha': alpha}

    def build_new_app_data(self, spec_traces=[], spec_layout=[], spec_selection = {}):
        return {'spec_figure': {'data':spec_traces, 'laylout':spec_layout }, 'spec_selection':spec_selection}

    def build_app_data(self, traces=None):
        if traces is None:
            return {'traces': {}, 'selection':{}}
        else:
            return {'traces': traces}

    def parse_contents(self, contents, filename, date):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),

            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),

            html.Hr(),  # horizontal line

            # For debugging, display the raw contents provided by the web browser
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])

    def write_info(self, info, file_endding=''):
        if file_endding != '':
            file_endding = '_' + file_endding
        with open('/home/mtp/ManuWork/python/scidb_specView_new/info' + file_endding +'.txt', 'a+') as f:
            f.write(str(datetime.now()) + " " + info + "\n")


    def set_app_data_timestamp(self, timestamp=None):
        if timestamp is not None:
            self.app_data_timestamp['timestamp'] = timestamp # in sceconds
        else:
            self.app_data_timestamp['timestamp'] = datetime.timestamp(datetime.now())  # in sceconds
        self.write_info("Updated timestamp to " + str(app_data_timestamp['timestamp']) )

    def update_client(self, timestamp=None):
        self.set_app_data_timestamp(timestamp)

        #Path('./assets/touch.txt').touch()


    def get_data_dict(self, data):
        #return json.loads(data) if data is not None else self.build_app_data()
        return data if data is not None else self.build_app_data()
