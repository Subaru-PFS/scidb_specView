import flask
from flask_socketio import SocketIO
import dash
from jupyter_dash import JupyterDash
from config import REFRESH_TIME, APP_BASE_DIRECTORY
from werkzeug.middleware.dispatcher import DispatcherMiddleware


server = flask.Flask(__name__) # define flask app.server

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']
external_scripts = ['https://code.jquery.com/jquery-3.5.0.min.js', 'https://cdn.plot.ly/plotly-latest.min.js','https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js','https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML',
                    {
                        "src": "//cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js",
                        "integrity": "sha256-yr4fRk/GU1ehYJPAs8P4JlTgu0Hdsp4ZKrx8bDEDC3I=",
                        "crossorigin": "anonymous",
                    }
                    ]

#server = flask.Flask(__name__) # define flask app.server
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, server=server,  requests_pathname_prefix='/specviewer/')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, server=server)
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, server=server)
app.server.secret_key = 'SOME_KEY_STRING'
socketio_app = SocketIO(app.server)




#app.scripts.append_script({"external_url": 'https://code.jquery.com/jquery-3.5.0.min.js'})
#app.layout = html.Div([dcc.Interval(id='interval-component',interval=1*1000,n_intervals=0),html.Div(className='row', children=[html.Div(id='live-update-text')])])
refresh_time = REFRESH_TIME
app_base_directory = APP_BASE_DIRECTORY

from specviewer.viewer import Viewer