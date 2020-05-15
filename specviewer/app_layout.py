from specviewer import refresh_time
from specviewer.data_models import WavelenghUnit
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


def load_app_layout(self): # self is passed as the Viewer class to fill out the figure element on the
    layout = html.Div([
        # The local store will take the initial data only the first time the page is loaded
        # and keep it until it is cleared.
        # dcc.Store(id='store', storage_type='local'),
        dcc.Store(id='store', storage_type='session'),
        # Same as the local store but will lose the data when the browser/tab closes.
        dcc.Store(id='session-store', storage_type='session'),
        dcc.Interval(
            id='synch_interval',
            interval=1000 * refresh_time,  # refresh time in seconds
            n_intervals=0
        ),
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
        html.Div(id="top-panel-div", className="row", style= {}, children=[

            ## first column --------------------------------------------------------------------------------------------
            html.Div(id="top-panel-div1", className="col-md-2", style={}, children=[
                dcc.Upload(id='upload-data',className="upload", children=html.Div([
                        html.A('Upload file(s)')
                    ]),
                    style={
                        'width': '50%',
                        #'height': '60px',
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
                html.H2(["Select Spectrum or Trace:"]),
                dcc.Dropdown(
                    id='dropdown-for-traces',
                    options=[],  # [{'label': label, 'value': label} for label in labels],
                    # options=[{'label': label, 'value': label} for label in labels],
                    value='',
                    placeholder="Select trace(s)",
                    multi=True,
                    style={}
                ),
                html.Br(),
                html.Br(),
                html.H3(["Deletion:"]),
                html.Button("Remove trace", id="remove_trace_button"),
                html.Br(),
                html.Br(),
                html.H3(["Smoothing:"]),
                html.Div(className="row", children=[
                    html.Div(className="col-md-6", children=[
                        html.Span(["Kernel:"]),
                        dcc.Dropdown(
                            id='smoothing_kernels_dropdown',
                            options=[{'label': "Gaussian", 'value': "Gaussian1DKernel"},
                                     {'label': "Box", 'value': "Box1DKernel"}],
                            value='Gaussian1DKernel',
                            placeholder="Select Smoothing kernel",
                            multi=False,
                            style={},
                            clearable = False
                        )
                    ]),
                    html.Div(className="col-md-6", children=[
                        html.Span(["Width2:"]),
                        html.Div(dcc.Input(id='kernel_width_box', value='20', type='number')),
                    ]),
                ]),
                html.Br(),
                html.Button('Smooth spectrum', id='trace_smooth_button'),
                html.Button('Unsmooth spectrum', id='trace_unsmooth_button'),

                html.Div(dcc.Input(style={'display':'none'}, id='input-box', type='text')),
                html.Button('Submit', id='button', style={'display':'none'}),
                html.Div(id='output-container-button', style={'display':'none'},
                         children='Enter a value and press submit'),

            ]),
            ## next column --------------------------------------------------------------------------------------------
            html.Div(id="top-panel-div2", className="col-md-10", style={}, children=[

                dcc.Graph(
                    id='spec-graph',
                    figure=self.spec_figure,
                    # figure=main_figure,
                    config={'displayModeBar': True, 'scrollZoom': False},
                    #animate=True # gives lots of problems
                ),
                html.Div(className="row",children=[
                    html.Div(className="col-md-2", children=[
                        html.H3(["Wavelength unit"]),
                        dcc.Dropdown(
                            id='wavelength-unit',
                            options=[{'label': "nanometer", 'value': WavelenghUnit.NANOMETER},
                                     {'label': "Angstrom", 'value': WavelenghUnit.ANGSTROM}],
                            value=WavelenghUnit.ANGSTROM,
                            placeholder="Wavelength unit",
                            multi=False,
                            style={}, clearable=False
                        ),
                    ]),
                    html.Div(className="col-md-10", children=[

                    ])
                ]),



                html.Div(style={'display':'none'}, children=[

                    html.Div(className='row', children=[
                        html.Div([
                            dcc.Markdown(d("""
        **Hover Data**

        Mouse over values in the graph.
                                        """)
                            ),
                            html.Pre(id='hover-data', style=styles['pre'])
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

                ]),

            ]),
        ]),


    ])
    return layout
