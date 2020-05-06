from specviewer import app, Viewer
from config import PORT, DEBUG




if __name__ == '__main__':
    viewer = Viewer(as_website=True)
    #viewer.show_app()
    app.run_server(port= PORT, debug=DEBUG,dev_tools_ui=True,dev_tools_props_check=True,dev_tools_hot_reload=True)
    # https://dash.plotly.com/devtools
