import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']
external_scripts = ['https://code.jquery.com/jquery-3.5.0.min.js', 'https://cdn.plot.ly/plotly-latest.min.js','https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
#app.scripts.append_script({"external_url": 'https://code.jquery.com/jquery-3.5.0.min.js'})
#app.layout = html.Div([dcc.Interval(id='interval-component',interval=1*1000,n_intervals=0),html.Div(className='row', children=[html.Div(id='live-update-text')])])
refresh_time = 1.0

#from specviewer import viewer
#from specviewer.viewer import Viewer

from specviewer.viewer import Viewer as Viewer
#viewer = Viewer2()



