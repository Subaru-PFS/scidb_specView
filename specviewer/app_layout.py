from specviewer import refresh_time
from specviewer.models.data_models import WavelenghUnit, FluxUnit
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from textwrap import dedent as d
from specviewer.spectral_lines import spectral_lines
import json
from specviewer.models.enum_models import SpectrumType
from specviewer.smoothing.smoother import default_smoothing_kernels, SmoothingKernels
from specviewer.fitting.fitter import default_fitting_models, FittingModels

spectral_line_dropdown_options = []
spectral_line_dropdown_options.append({'label':'all', 'value':'all'})
spectral_line_dropdown_options = spectral_line_dropdown_options + [ {'label':spectral_lines[line]['fullname'], 'value':spectral_lines[line]['fullname']} for line in spectral_lines]
smoothing_kernel_options = [{'label':type, 'value':type} for type in default_smoothing_kernels]
fitting_model_options = [{'label':type, 'value':type} for type in default_fitting_models]

# docs:
# https://dash-bootstrap-components.opensource.faculty.ai/
# https://github.com/ucg8j/awesome-dash#component-libraries
# https://pypi.org/project/dash-database/
# https://github.com/thedirtyfew/dash-extensions/


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


def load_app_layout(self, app_port, storage_mode): # self is passed as the Viewer class to fill out the figure element on the
    layout = html.Div([
        # The local store will take the initial data only the first time the page is loaded
        # and keep it until it is cleared.
        #dcc.Store(id='store', storage_type='memory'),
        # Same as the local store but will lose the data when the browser/tab closes.
        dcc.Loading(
            id="loading-1",
            type="default",
            children=dcc.Store(id='store', storage_type=storage_mode),
            style={'size': 5},
        ),
        # stores the URL of the page plus query string
        dcc.Location(id='url', refresh=False),
        dcc.Interval(
            id='synch_interval',
            interval=1000 * refresh_time,  # refresh time in seconds
            n_intervals=0
        ),
        #dcc.Interval(
        #    id='refresh-data-interval',
        #    interval=1000 * refresh_time,  # in refresh time in seconds
        #    n_intervals=0
        #),
        #dcc.Interval(
        #    id='interval-component',
        #    interval=1000 * refresh_time,  # in refresh time in seconds
        #    n_intervals=0
        #),
        html.Div(id="top-panel-div", className="row", style= {}, children=[

            ## first column --------------------------------------------------------------------------------------------
            html.Div(id="top-panel-div1", className="col-sm-2", style={}, children=[
                html.H5(["Loading spectra:"]),
                #https://dash.plotly.com/dash-core-components/input
                dcc.Input(id="pull_trigger", type="text",value="dwdww", style={'visibility': 'hidden'}),
                html.Br(),
                dcc.Input(id="specid", type="text", placeholder="Enter spectrum ID(s)",
                          debounce=True, autoFocus=True,
                          persistence="true", persistence_type=storage_mode, value=""),
                html.Button("load", id="search_spectrum_button"),
                html.Br(),
                dcc.Upload(id='upload-data',className="upload", children=html.Div([
                        html.H5('Upload file(s)')
                    ]),
                    style={
                        'width': '50%',
                        #'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '5px'
                    },
                    multiple=True # Allow multiple files to be uploaded
                ),
                html.Hr(),
                html.Br(),
                html.H5(["Select Trace(s):"]),
                dcc.Dropdown(
                    id='dropdown-for-traces',
                    options=[],  # [{'label': label, 'value': label} for label in labels],
                    # options=[{'label': label, 'value': label} for label in labels],
                    value=[],
                    placeholder="Select trace(s)",
                    multi=True,
                    style={},
                    persistence="true",
                    persisted_props=["value"],
                    persistence_type=storage_mode
                ),
                html.Button("(un)select all", id="select_all_traces_button"),
                html.Button("Remove selected", id="remove_trace_button"),
                html.Br(),
                dcc.Checklist(
                    id="remove_children_checklist",
                    options=[
                        {'label': 'also remove derived traces', 'value': 'remove_children'},
                    ],
                    value=['remove_children'],  # 'add_model'
                    labelStyle={'display': 'inline-block'},
                    persistence=True,
                    persistence_type=storage_mode,
                    persisted_props=["value"],
                ),

                html.Br(),
                html.H5(["Toggle:"]),
                html.Button('model', id='show_model_button'),
                html.Button('sky', id='show_sky_button'),
                html.Button('error', id='show_error_button'),

                html.Hr(),
                html.Br(),
                html.H5(["Smoothing:"]),
                html.Div(className="row", children=[
                    html.Div(className="col-sm-6", children=[
                        html.Span(["Kernel:"]),
                        dcc.Dropdown(
                            id='smoothing_kernels_dropdown',
                            #options=[{'label': "Gaussian", 'value': "Gaussian1DKernel"},
                            #         {'label': "Box", 'value': "Box1DKernel"}],
                            options = smoothing_kernel_options,
                            value=SmoothingKernels.MEDIAN,
                            placeholder="Select Smoothing kernel",
                            multi=False,
                            style={},
                            clearable = False,
                            #persistence=True,
                            persistence_type=storage_mode
                        )
                    ]),
                    html.Div(className="col-md-6", children=[
                        html.Span(["Width:"]),
                        html.Div(dcc.Input(id='kernel_width_box', value='5', type='number')),
                    ]),
                ]),
                html.Br(),
                html.Button('Smooth', id='trace_smooth_button'),
                html.Button('Substract smoothed', id='trace_smooth_substract_button'),
                html.Button('Reset', id='trace_unsmooth_button'),
                html.Br(),
                dcc.Checklist(
                    id="add_smoothing_as_trace_checklist",
                    options=[
                        {'label': 'add result as new trace', 'value': 'add_as_new_trace'},
                    ],
                    value=[],  # ['add_smoothed_as_trace']
                    labelStyle={'display': 'inline-block'},
                    persistence=True,
                    persistence_type=storage_mode,
                    persisted_props=["value"],
                ),
                html.Br(),
                html.Br(),
                html.H5(["Model Fitting:"]),
                dcc.Dropdown(
                    id='fitting-model-dropdown',
                    options= fitting_model_options,
                    value=[FittingModels.GAUSSIAN_PLUS_LINEAR],
                    placeholder="Select line profile",
                    multi=True,
                    style={},
                    persistence=True,
                    persistence_type=storage_mode
                ),
                html.Br(),
                html.Button('Fit model(s)', id='model_fit_button'),
                html.Br(),
                dcc.Checklist(
                    id="add_fit_substracted_trace_checklist",
                    options=[
                        {'label': 'add fit-substracted trace', 'value': 'add_fit_substracted_trace'},
                    ],
                    value=[],  # ['add_smoothed_as_trace']
                    labelStyle={'display': 'inline-block'},
                    persistence=True,
                    persistence_type=storage_mode,
                    persisted_props=["value"],
                ),
                html.Br(),
                html.Br(),
                dcc.Markdown(id = "fitted_models_table", children='', dangerously_allow_html=True),
                html.Br(),
                html.Br(),
                #html.Div(dcc.Input(style={'display':'none'}, id='input-box', type='text', value="")),
                html.Button('Submit', id='button', style={'display':'none'}),
                html.Br(),
                html.Div(id='output-container-button', style={'display':'none'},
                         children='Enter a value and press submit'),


            ]),
            ## next column --------------------------------------------------------------------------------------------
            html.Div(id="top-panel-div2", className="col-sm-10", style={}, children=[
                html.Br(),
                html.H4(["Spectrum Viewer"] , className="text-center"),
                dcc.Graph(
                    id='spec-graph',
                    #figure=self.spec_figure,
                    figure={},
                    config={'displayModeBar': True, 'scrollZoom': True, 'responsive': False, 'displaylogo': False},
                    #animate=True # gives lots of problems
                ),
                html.Div(className="row",children=[
                    html.Div(className="col-sm-2", children=[]),
                    html.Div(className="col-sm-2", children=[
                        html.H5(["Wavelength unit"]),
                        dcc.Dropdown(
                            id='wavelength-unit',
                            options=[{'label': "nanometer", 'value': WavelenghUnit.NANOMETER},
                                     {'label': "Angstrom", 'value': WavelenghUnit.ANGSTROM}],
                            value=WavelenghUnit.ANGSTROM,
                            placeholder="Wavelength unit",
                            multi=False,
                            style={}, clearable=False,
                            persistence=True,
                            persistence_type=storage_mode,
                        ),
                        html.Br(),
                        html.Br(),
                        html.H5(["Flux unit"]),
                        dcc.Dropdown(
                            id='flux-unit',
                            options=[
                                        {'label': "erg/s/cm^2/A", 'value': FluxUnit.F_lambda},
                                        {'label': "erg/s/cm^2/Hz", 'value': FluxUnit.F_nu},
                                        {'label': "AB Magnitude", 'value': FluxUnit.AB_magnitude}
                                    ],
                            value=FluxUnit.F_lambda,
                            placeholder="Flux unit",
                            multi=False,
                            style={}, clearable=False,
                            persistence=True,
                            persistence_type=storage_mode,
                        ),
                    ]),
                    html.Div(className="col-sm-2", children=[
                        #https://dash.plotly.com/dash-daq/booleanswitch
                        html.H5("SpectralLines:"),
                        daq.BooleanSwitch(id="spectral-lines-switch",
                            on=True,
                            label="Show lines",
                            labelPosition="top",
                            persistence=True,
                            persistence_type=storage_mode,
                        ),
                        html.Br(),
                        html.Br(),
                        dcc.Dropdown(
                            id='spectral_lines_dropdown',
                            options=spectral_line_dropdown_options,
                            value=[],
                            placeholder="Choose spectral line(s)",
                            multi=True,
                            style={}, clearable=True
                        ),
                        html.Div(dcc.Input(id='spectral_lines_dict', value=json.dumps(spectral_lines), style={'display': 'none'})),
                        html.Br(),
                        html.Br(),
                        html.H6("Line(s) redshift:"),
                        html.Div(dcc.Input(id='redshift_input', value='0', type='number')),
                        html.Button("Set", id="redshift_button"),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        #https://dash.plotly.com/dash-daq/slider
                        daq.Slider(id="redshift-slider",
                            min=0,
                            max=10,
                            value=0,
                            marks={ i: i for i in range(0,10+1)},
                            handleLabel={"showCurrentValue": True, "label": "Redshift"},
                            step=0.01
                        ),
                    ]),
                    html.Div(className="col-sm-4", children=[
                        html.H5(["Masks:"]),
                        html.Br(),
                        daq.BooleanSwitch(id="and_mask_switch",
                                          on=True,
                                          label="Show mask(s)",
                                          labelPosition="top",
                                          persistence=True,
                                          persistence_type=storage_mode,
                                          ),
                        html.Br(),
                        dcc.Dropdown(
                            id='dropdown-for-masks',
                            options=[],  # [{'label': label, 'value': label} for label in labels],
                            value='',
                            placeholder="Select masks(s)",
                            multi=True,
                            style={},
                            persistence=True,
                            persistence_type=storage_mode
                        ),
                    ]),
                    html.Div(className="col-sm-4", children=[])
                ]),



                html.Div(style={'display':'none'}, children=[
                #html.Div(style={}, children=[

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
