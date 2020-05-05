from specviewer import refresh_time
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
        dcc.Store(id='store'),
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
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.A('Upload file(s)')
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
            className="upload",
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dcc.Dropdown(
            id='dropdown-for-traces',
            options=[],  # [{'label': label, 'value': label} for label in labels],
            # options=[{'label': label, 'value': label} for label in labels],
            value='',
            placeholder="Select trace(s)",
            multi=True,
            style={}
        ),
        html.Button("Remove trace", id="remove_trace_button"),
        html.Div(dcc.Input(id='input-box', type='text')),
        html.Button('Submit', id='button'),
        html.Div(id='output-container-button',
                 children='Enter a value and press submit'),
        dcc.Graph(
            id='spec-graph',
            figure=self.spec_figure,
            # figure=main_figure,
            config={'displayModeBar': True, 'scrollZoom': False},
            animate=True
        ),

        html.Div(className='row', children=[
            html.Div([
                dcc.Markdown(d("""
                    **Hover Data**

                    Mouse over values in the graph.
                """)),
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
    ])
    return layout
