from specviewer import Viewer
from config import PORT, DEBUG




if __name__ == '__main__':
    viewer = Viewer(as_website=True)
    #viewer.app.run_server(port= PORT, debug=DEBUG,dev_tools_ui=True,dev_tools_props_check=True,dev_tools_hot_reload=True, dev_tools_silence_routes_logging=True)       # for Dash case
    #viewer.app.run_server(port=PORT, debug=DEBUG, dev_tools_ui=True, dev_tools_silence_routes_logging=True)  # for Dash case
    viewer.socketio.run(viewer.app.server, port= PORT, debug=DEBUG)   # for socketIO case
    # https://dash.plotly.com/devtools
