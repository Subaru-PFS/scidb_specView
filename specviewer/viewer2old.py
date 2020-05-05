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
from . import controller as c

from . import data_driver

import json
from textwrap import dedent as d
from jupyterlab_dash import AppViewer
import dash
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import datetime
import multiprocessing as mp
import base64
import pandas as pd
import io
import json
from astropy.io import fits
import traceback
import dash_table

process_manager = mp.Manager()
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


class Viewer():
    # app_data = {}

    def __init__(self, as_website=False):
        # global app_data
        # global fig
        self.as_website = as_website
        print("first " + str(self.as_website))
        if not as_website:
            # self.app_data = application_data.ApplicationData()
            self.app_data = {'traces': {}, 'selection': {}}
        else:
            self.app_data = None
        # just for testing local website
        # self.app_data = {'traces':{}, 'selection':{}} #application_data.ApplicationData()
        # self.app_data = app_data
        self.app_data = app_data
        self.app_data['traces'] = {}
        self.app_data['selection'] = {}
        self.debug_data = debug_data

        # self.spectral_lines_info = spectral_lines_info
        # self.view = V.SpecView(width, height, dpi)
        # self.view.select_all_button.on_clicked(self.select_all_button_callback)
        # self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        # self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())

        self.time2 = str(datetime.datetime.now())

        # self.spec_figure = make_subplots(rows=1, cols=1)
        # self.fill_spec_figure_with_app_data()
        self.spec_figure = self.get_spec_figure_from_data(self.app_data)

        app.layout = self.load_app_layout
        # self.load_callbacks()

        try:

            @app.callback(Output('live-update-text', 'children'),
                          [Input('interval-component', 'n_intervals')])
            def update_metrics(n):
                # time.sleep(0.1)
                print("from call update_metrics  " + str(n))
                # return str(datetime.datetime.now() + " " + str(self.app_data))
                return "APP DATA " + str(datetime.datetime.now()) + " " + str(app_data)

            @app.callback(Output('live-update-text2', 'children'),
                          [Input('refresh-data-interval', 'n_intervals'), Input('store', 'data')])
            def update_time(n, data):
                print("from call update_time " + str(n))
                if data is not None:
                    s = str(data)
                    # s = json.dump(data)
                else:
                    s = "nodata"
                return "LOCAL DATA1 " + s

            if not self.as_website:
                # when on Jupyter, app_data has always the source of truth. All callbacks will be updating
                # local data and then app_data. Therefore, there is no need to update local data from app_data.
                # Only the figure has to be updated from the latest values in app_data
                @app.callback(Output('basic-interactions', 'figure'),
                              [Input('refresh-data-interval', 'n_intervals')])
                def update_figure2(n):
                    # print("from call " + n)
                    # self.fill_spec_figure_with_app_data()
                    self.spec_figure = self.get_spec_figure_from_data(self.app_data)
                    return self.spec_figure

            @app.callback(
                Output('selected-data', 'children'),
                [Input('basic-interactions', 'selectedData')])
            def display_selected_data(selectedData):
                # print("from call display_selected_data")
                app_data['selection'] = selectedData
                return json.dumps(app_data['selection'], indent=2)

            @app.callback(
                Output('hover-data2', 'children'),
                [Input('basic-interactions', 'hoverData')])
            def display_hover_data(hoverData):
                # print("from call display_hover_data")
                app_data['hover_data'] = hoverData
                return json.dumps(app_data['hover_data'], indent=2)

            @app.callback(
                Output('click-data', 'children'),
                [Input('basic-interactions', 'clickData')])
            def display_click_data(clickData):
                # print("from call display_click_data")
                app_data['click_data'] = clickData
                return json.dumps(app_data['click_data'], indent=2)

            @app.callback(
                Output('relayout-data', 'children'),
                [Input('basic-interactions', 'relayoutData')])
            def display_relayout_data(relayoutData):
                # print("from call display_relayout_data")
                app_data['relayout_data'] = relayoutData
                return json.dumps(app_data['relayout_data'], indent=2)

            @app.callback(
                dash.dependencies.Output('output-container-button', 'children'),
                [dash.dependencies.Input('button', 'n_clicks')],
                [dash.dependencies.State('input-box', 'value')])
            def update_output(n_clicks, value):
                self.debug_data['update_output'] = "update_output"
                return 'The input value was "{}" and the button has been clicked {} times'.format(
                    value,
                    n_clicks
                )

            @app.callback(
                [Output('live-update-text3', 'children'), Output('store', 'data'),
                 Output('basic-interactions', 'figure')],
                # [Input('store', 'data'),Input('upload-data', 'contents')],
                [Input('upload-data', 'contents')],
                [State('upload-data', 'filename'),
                 State('upload-data', 'last_modified'),
                 State('store', 'data')])
            def process_uploaded_file(list_of_contents, list_of_names, list_of_dates, data):
                self.debug_data['process_uploaded_file'] = "process_uploaded_file"
                try:

                    if list_of_contents is not None:
                        if data is not None:
                            data_dict = json.loads(data)
                        else:
                            data_dict = self.build_app_data()

                        if not as_website:
                            # synchronize global app_data with data in local store
                            self.synch_data(base_data_dict=self.app_data, incomplete_data_dict=data_dict)
                            # for trace_name in app_data['traces']:
                            #    if trace_name not in data_dict['traces']:
                            #        self.add_trace_to_data(data_dict, trace_name, app_data['traces'][trace_name])

                        new_data = [
                            self.parse_uploaded_file(c, n) for c, n, d in
                            zip(list_of_contents, list_of_names, list_of_dates)]
                        # traces = { name:trace for (name,trace) in new_data  }
                        for (name, trace) in new_data:
                            self.add_trace_to_data(data_dict, name, trace)
                            if not as_website:
                                # add new trace to global app data
                                self.add_trace_to_data(app_data, name, trace)

                        # if not as_website:
                        #    self.synch_data(base_data_dict=self.app_data, incomplete_data_dict=data_dict)

                        json_string = json.dumps(data_dict)
                        figure = self.get_spec_figure_from_data(data_dict)

                        return "LOCAL DATA2 " + " " + json_string, json_string, figure
                    else:
                        return no_update, no_update, no_update
                except Exception as e:
                    self.debug_data['error'] = str(e) + " " + traceback.format_exc()
                    raise Exception(str(e) + " " + str(data_dict))

            @app.callback(Output('output-data-upload', 'children'),
                          [Input('upload-data2', 'contents')],
                          [State('upload-data2', 'filename'),
                           State('upload-data2', 'last_modified')])
            def update_output2(list_of_contents, list_of_names, list_of_dates):
                self.debug_data['dwedfwe'] = ['fwefwefwefegre']
                if list_of_contents is not None:
                    children = [
                        self.parse_contents(c, n, d) for c, n, d in
                        zip(list_of_contents, list_of_names, list_of_dates)]
                    return children

            def synch_data(self, base_data_dict, incomplete_data_dict):
                for trace_name in base_data_dict['traces']:
                    # if trace_name not in incomplete_data_dict['traces']:
                    self.add_trace_to_data(incomplete_data_dict, trace_name, base_data_dict['traces'][trace_name])

        except:
            pass

    def parse_uploaded_file(self, contents, filename):

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        hdulist = fits.open(io.BytesIO(decoded))
        spectrum = data_driver.get_spectrum_from_fits(hdulist, filename)

        # name = filename + str(len(hdulist))
        # trace = self.build_trace(x_coords=[1,2,3,4], [float(np.random.random_sample()) for i in range(4)], filename)
        trace = self.build_trace(x_coords=[1, 2, 3, 4], y_coords=[float(np.random.random_sample()) for i in range(4)],
                                 name=filename)
        # trace = self.build_trace(spectrum.wavelength, spectrum.flux, filename, color="black", linewidth=1, alpha=0.8)
        return filename, trace

    def update_figure_layout(self):
        time = str(datetime.datetime.now())
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
                scatter = go.Scatter(x=traces[trace_name]['x_coords'], y=traces[trace_name]['y_coords'],
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
            scatter = go.Scatter(x=x, y=y, mode="lines+markers",
                                 name=name, marker={'size': 12}, line=dict(color="blue"),
                                 text=['a', 'b', 'c', 'd'], customdata=['c.a', 'c.b', 'c.c', 'c.d'])
            self.spec_figure.add_trace(scatter, row=1, col=1)
            self.update_figure_layout()

    def get_spec_figure_from_data(self, data):
        # create figure with plotly api from data object
        figure = make_subplots(rows=1, cols=1)
        traces = data.get("traces", {})
        for trace_name in traces:
            scatter = go.Scatter(x=traces[trace_name]['x_coords'], y=traces[trace_name]['y_coords'],
                                 mode="lines+markers",
                                 name=traces[trace_name]['name'], marker={'size': 12}, line=dict(color="blue"),
                                 text=['a', 'b', 'c', 'd'], customdata=['c.a', 'c.b', 'c.c', 'c.d'])
            figure.add_trace(scatter, row=1, col=1)

        figure.update_layout(title={'text': "Plot Title", 'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                             xaxis_title="Wavelength", yaxis_title="Flux",
                             font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
                             title_text="SpecViewer", title_font_size=30, plot_bgcolor='rgb(250,250,250)',
                             clickmode='event+select')
        return figure

    def update_time(self):
        self.time2 = str(datetime.datetime.now())

    def load_callbacks(self):
        # from specviewer.callbacks import update_metrics, display_hover_data, display_click_data, display_relayout_data
        pass

    def show_jupyter_app(self):
        # self.load_callbacks()
        # app.layout = self.load_app_layout
        # app.layout = self.load_app_layout
        jupyter_viewer.show(app)

    def add_trace_to_data(self, application_data, name, trace):
        traces = application_data['traces']
        traces[name] = trace
        application_data['traces'] = traces
        # self.app_data['traces'][name] = trace
        # if update_figure:
        #    self.fill_spec_figure_with_app_data(self.spec_figure)
        #    self.load_spec_figure(self.spec_figure)

    def add_trace(self, name, trace):
        return self.add_trace_to_data(self.app_data, name, trace)

    def remove_trace(self, name):
        traces = app_data['traces']
        traces.pop(name)
        app_data['traces'] = traces

    def build_trace(self, x_coords=[], y_coords=[], name=None, parent=None, type=None, color="black", linewidth=1,
                    alpha=1.0):
        return {'name': name, 'x_coords': x_coords, 'y_coords': y_coords, 'type': type, 'parent': parent,
                'visible': True, 'color': color, 'linewidth': linewidth, 'alpha': alpha}

    def build_app_data(self, traces=None):
        if traces is None:
            return {'traces': {}}
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

    def load_app_layout(self):
        layout = html.Div([
            html.Div(dcc.Input(id='input-box', type='text')),
            html.Button('Submit', id='button'),
            html.Div(id='output-container-button',
                     children='Enter a value and press submit'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '10%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            dcc.Upload(
                id='upload-data2',
                children=html.Div([
                    '2Drag and Drop or ',
                    html.A('2Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload'),

            # The local store will take the initial data only the first time the page is loaded
            # and keep it until it is cleared.
            # dcc.Store(id='store', storage_type='local'),
            dcc.Store(id='store'),
            # Same as the local store but will lose the data when the browser/tab closes.
            dcc.Store(id='session-store', storage_type='session'),
            dcc.Interval(
                id='refresh-data-interval',
                interval=1000 * refresh_time,  # in refresh time in seconds
                n_intervals=0
            ),
            dcc.Interval(
                id='interval-component',
                interval=1000 * refresh_time,  # in refresh time in seconds
                n_intervals=0
            ),
            dcc.Graph(
                id='basic-interactions',
                figure=self.spec_figure,
                # figure=main_figure,
                config={'displayModeBar': True, 'scrollZoom': True},
                animate=True
            ),

            html.Div(className='row', children=[
                html.Div([
                    dcc.Markdown(d("""
                        **Hover Data**

                        Mouse over values in the graph.
                    """)),
                    html.Pre(id='hover-data2', style=styles['pre'])
                ], className='three columns'),

                html.Div([
                    dcc.Markdown(d("""
                        **Click Data**

                        Click on points in the graph.
                    """)),
                    html.Pre(id='click-data', style=styles['pre']),
                ], className='three columns'),

                html.Div([
                    dcc.Markdown(d("""
                        **Selection Data**

                        Choose the lasso or rectangle tool in the graph's menu
                        bar and then select points in the graph.

                        Note that if `layout.clickmode = 'event+select'`, selection data also 
                        accumulates (or un-accumulates) selected data if you hold down the shift
                        button while clicking.
                    """)),
                    html.Pre(id='selected-data', style=styles['pre']),
                ], className='three columns'),

                html.Div([
                    dcc.Markdown(d("""
                        **Zoom and Relayout Data**

                        Click and drag on the graph to zoom or click on the zoom
                        buttons in the graph's menu bar.
                        Clicking on legend items will also fire
                        this event.
                    """)),
                    html.Pre(id='relayout-data', style=styles['pre']),
                ], className='three columns'),
                html.Div(className='row', children=[
                    html.Div(id='eraseme')
                ]),
                html.Div(className='row', children=[
                    html.Div(id='live-update-text')
                ]),
                html.Div(className='row', children=[
                    html.Div(id='live-update-text2')
                ]),
                html.Div(className='row', children=[
                    html.Div(id='live-update-text3')
                ])
            ])
        ])
        return layout
