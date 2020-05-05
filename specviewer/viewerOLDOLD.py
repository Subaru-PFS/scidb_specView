import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from specviewer import app
from jupyterlab_dash import AppViewer
from plotly.tools import mpl_to_plotly
from matplotlib import pyplot as plt

import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
from SpectrumViewer import spectral_lines_info
import SpectrumViewer.dataDriver as driver
from SpectrumViewer.data_models import Medium, Spectrum, SpectrumLineGrid, SpectrumLine
import SpectrumViewer
from collections import OrderedDict
import matplotlib.text
import numpy as np
import matplotlib.transforms as transforms
import copy
from . import controller as c

class Viewer():
    def __init__(self):
        self.spectral_lines_info = spectral_lines_info
        #self.view = V.SpecView(width, height, dpi)
        #self.view.select_all_button.on_clicked(self.select_all_button_callback)
        #self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())
        self.spec_figure = None

    def add_stream(self, data_stream, display_name=None, data_stream_style={}):
        #check that streams are not already stored

        new_stream_dicts = driver.load_new_streams(self.model.streams, data_stream, display_name, data_stream_style)
        for stream_name in new_stream_dicts:
            self.model.streams[stream_name] = new_stream_dicts[stream_name]

    def show_app_old(self):

        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = [1, 2, 3, 4]
        y = [10, 20, 25, 30]
        ax.plot(x, y, color='lightblue', linewidth = 3)
        ax.scatter(x, y, color='darkgreen', marker ='.')
        ax.set_xlim(0.5, 4.5)
        ax.set_facecolor('xkcd:salmon')
        ax.set_facecolor((1.0, 0.47, 0.42))


        plotly_fig = mpl_to_plotly(fig)

        #graph = dcc.Graph(id='myGraph', fig=plotly_fig)

        fig = go.Figure(
            data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
            layout=go.Layout(
                title=go.layout.Title(text="A Bar Chart")
            )
        )

        fig2 = make_subplots(rows=2, cols=1)
        fig2.add_trace(go.Scatter(y=[4.4, 2, 1], mode="lines", name="scatter 1"), row=1, col=1)
        fig2.add_trace(go.Scatter(y=[4.1, 2, 1], mode="lines", name="scatter 2"), row=1, col=1)
        fig2.add_trace(go.Scatter(y=[4, 2.2, 1.5], mode="lines", name="scatter 3", line=dict(color="blue")), row=1, col=1)
        fig2.add_trace(go.Scatter(y=[4, 2, 1], mode="lines"), row=1, col=1)
        fig2.add_trace(go.Bar(y=[2, 1, 3]), row=2, col=1)
        fig2.update_layout(title={'text': "Plot Title", 'y':0.9, 'x':0.5, 'xanchor': 'center','yanchor': 'top'}, xaxis_title="x Axis Title", yaxis_title="y Axis Title",font=dict(family="Courier New, monospace",size=18,color="#7f7f7f"),title_text="A Bar Chart",title_font_size=30)


        app.layout = html.Div(children=[
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': x, 'y':y},
                        go.Bar(x=[1, 2, 3], y=[1, 3, 2])
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                },
                config={'displayModeBar': True, 'scrollZoom': True}
            ),
            dcc.Graph(id='myGraph2', figure=fig2,
                      config={'displayModeBar': True, 'scrollZoom': True}),
            dcc.Graph(id='myGraph', figure=plotly_fig,
                config={'displayModeBar': True, 'scrollZoom': True}),
            html.H2(children="Dqwedw")
        ])
        #jupyter_viewer.show(app, mode='split-right')

    def show_app(self):
        self.spec_figure = make_subplots(rows=1, cols=1)
        self.spec_figure.add_trace(go.Scatter(x=[1,2,3],y=[4, 2, 1], mode="lines"), row=1, col=1)
        #go.Figure(go.Scatter(x=[1,2],y=[3,4]))
        #self.spec_figure.update_layout(xaxis= {'showgrid': False}, yaxis= {'showgrid': False})

        app.layout = html.Div(children=[
            dcc.Graph(
                id='mainViewer',
                figure=self.spec_figure,
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ])

    def show_jupyter_app(self):
        jupyter_viewer = AppViewer()
        self.show_app()
        jupyter_viewer.show(app)


    def add_stream(self, data_stream, display_name=None, data_stream_style={}):
        #check that streams are not already stored

        #new_stream_dicts = driver.load_new_streams(self.model.streams, data_stream, display_name, data_stream_style)
        #for stream_name in new_stream_dicts:
        #    self.model.streams[stream_name] = new_stream_dicts[stream_name]
        self.spec_figure.append_trace({
        'x': data_stream.x_coords,
        'y': data_stream.x_coords,
        'name': 'Foo',
        'mode': 'lines+markers',
        'type': 'scatter'}, 1, 1)

    def add_data(self):
        self.spec_figure.append_trace({
        'x': [1,2,3,4],
        'y': [1,3,6,2],
        'name': 'Foo',
        'mode': 'lines+markers',
        'type': 'scatter'}, 1, 1)



    def show(self):
        pass