import flask
import dash
from config import REFRESH_TIME
from werkzeug.middleware.dispatcher import DispatcherMiddleware

server = flask.Flask(__name__) # define flask app.server

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']
external_scripts = ['https://code.jquery.com/jquery-3.5.0.min.js', 'https://cdn.plot.ly/plotly-latest.min.js','https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js']

#server = flask.Flask(__name__) # define flask app.server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, server=server,  requests_pathname_prefix='/specviewer/')
app.server.secret_key = 'SOME_KEY_STRING'




#app.scripts.append_script({"external_url": 'https://code.jquery.com/jquery-3.5.0.min.js'})
#app.layout = html.Div([dcc.Interval(id='interval-component',interval=1*1000,n_intervals=0),html.Div(className='row', children=[html.Div(id='live-update-text')])])
refresh_time = REFRESH_TIME

#from specviewer import viewer
#from specviewer.viewer import Viewer

from specviewer.viewer import Viewer as Viewer, app as app2
viewer = Viewer(as_website=True)



website = DispatcherMiddleware(server, {
    '/specviewer': app.server,
})