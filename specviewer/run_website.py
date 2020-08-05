from specviewer import app, socketio_app, Viewer
from config import PORT, DEBUG




if __name__ == '__main__':
    viewer = Viewer(as_website=True)
    app.run_server(port= PORT, debug=DEBUG,dev_tools_ui=True,dev_tools_props_check=True,dev_tools_hot_reload=True)       # for Dash case
    #socketio_app.run(app.server, port= PORT, debug=DEBUG)   # for socketIO case
    # https://dash.plotly.com/devtools
