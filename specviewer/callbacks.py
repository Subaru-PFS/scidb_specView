import json
from textwrap import dedent as d
from jupyterlab_dash import AppViewer
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from specviewer import app, refresh_time
from datetime import datetime
import time
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import traceback

def load_callbacks(self): # self is passed as the Viewer class

    try:
        b = """
                # display APP data
                @app.callback(Output('live-update-text', 'children'),
                              [Input('interval-component', 'n_intervals')])
                def update_metrics(n):
                    return "APP DATA " + str(datetime.datetime.now()) + " " + str(app_data)

                """

        # display local data
        @app.callback(
            Output('live-update-text2', 'children'),
            [Input('refresh-data-interval', 'n_intervals')],
            [State('store', 'data')]
        )
        def update_time(n, data):
            # print("from call update_time " + str(n))
            if data is None:
                # s = len(data)
                s = "has no data"
                # s = json.dump(data)
            else:
                if data['traces'] is not None:
                    s = str([t for t in data['traces']])
                else:
                    s = "none traces"
            return "LOC DATA " + str(datetime.now()) + " traces: " + s

        if False: #not self.as_website:
            # when on Jupyter, app_data has always the source of truth. All callbacks will be updating
            # local data and then app_data. Therefore, there is no need to update local data from app_data.
            # Only the figure has to be updated from the latest values in app_data
            @app.callback(Output('spec-graph', 'figure'),
                          [Input('refresh-data-interval', 'n_intervals')])
            def update_figure2(n):
                # print("from call " + n)
                # self.fill_spec_figure_with_app_data()
                self.spec_figure = self.get_spec_figure_from_data(self.app_data)
                return self.spec_figure

        @app.callback(
            Output('selected-data', 'children'),
            [Input('spec-graph', 'selectedData')])
        def display_selected_data(selectedData):
            # print("from call display_selected_data")
            self.app_data['selection'] = selectedData
            return json.dumps(self.app_data['selection'], indent=2)

        @app.callback(
            Output('hover-data', 'children'),
            [Input('spec-graph', 'hoverData')])
        def display_hover_data(hoverData):
            # print("from call display_hover_data")
            self.app_data['hover_data'] = hoverData
            return json.dumps(self.app_data['hover_data'], indent=2)

        @app.callback(
            Output('click-data', 'children'),
            [Input('spec-graph', 'clickData')])
        def display_click_data(clickData):
            # print("from call display_click_data")
            self.app_data['click_data'] = clickData
            return json.dumps(self.app_data['click_data'], indent=2)

        @app.callback(
            Output('relayout-data', 'children'),
            [Input('spec-graph', 'relayoutData')])
        def display_relayout_data(relayoutData):
            # print("from call display_relayout_data")
            self.app_data['relayout_data'] = relayoutData
            return json.dumps(self.app_data['relayout_data'], indent=2)

        @app.callback(
            dash.dependencies.Output('output-container-button', 'children'),
            [dash.dependencies.Input('button', 'n_clicks')],
            [dash.dependencies.State('input-box', 'value')])
        def update_output(n_clicks, value):
            self.debug_data['update_output'] = "update_output"
            return 'The input value was "{}" and the button has been clicked {} times'.format(
                value,
                n_clicks
            )

        a = """

                # update text every time the data changes
                @app.callback(
                    Output('live-update-text3', 'children'),
                    Input('store', 'data')
                )
                def update_from_client(data):
                    if data is not None:
                        return "LOCAL DATA2 " + " " + data
                    else:
                        return no_update


    """


        if self.as_website:

            # update main spec figure every time the data changes
            # @app.callback(
            app.clientside_callback(
                ClientsideFunction(
                    namespace='clientside',
                    function_name='set_figure'
                ),
                Output('spec-graph', 'figure'),
                # [Input('store', 'data')],
                [Input('store', 'modified_timestamp')],
                [State('store', 'data')]
            )

            # update dropdown of traces every time the data changes
            app.clientside_callback(
                ClientsideFunction(
                    namespace='clientside',
                    function_name='set_dropdown_options'
                ),
                Output('dropdown-for-traces', 'options'),
                # [Input('store', 'data')]
                # [Input('store', 'data')],
                [Input('store', 'modified_timestamp')],
                [State('store', 'data')]
            )

            @app.callback(
                Output('store', 'data'),
                [Input("remove_trace_button", "n_clicks"),
                 Input('upload-data', 'contents')],
                [State('upload-data', 'filename'),
                 State('upload-data', 'last_modified'),
                 State('store', 'data'),
                 State('store', 'modified_timestamp'),
                 State('dropdown-for-traces', 'value')
                 ])
            # def process_input(n_intervals, list_of_contents, list_of_names, list_of_dates, data, dropdown_values):
            def process_input(n_clicks, list_of_contents, list_of_names, list_of_dates, data,data_timestamp,dropdown_values):
                try:

                    # self.debug_data['process_uploaded_file'] = "process_uploaded_file"
                    task_name = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

                    # get data in local storage:


                    if task_name == "upload-data" and list_of_contents is not None:
                        self.write_info("Start processing uploaded file")
                        data_dict = self.get_data_dict(data)
                        new_data = [
                            self.parse_uploaded_file(c, n) for c, n, d in
                            zip(list_of_contents, list_of_names, list_of_dates)]
                        # traces = { name:trace for (name,trace) in new_data  }
                        for (name, trace) in new_data:
                            self.add_trace_to_data(data_dict, name, trace, do_update_client=False)

                        self.write_info("End processing uploaded file")
                        #return json.dumps(data_dict)
                        return data_dict

                    elif task_name == "remove_trace_button" and len(dropdown_values) > 0:
                        data_dict = self.get_data_dict(data)
                        self._remove_traces(dropdown_values, data_dict, do_update_client=False)
                        #return json.dumps(data_dict)
                        return data_dict
                    else:
                        return no_update

                except Exception as e:
                    exs = str(e)
                    # self.debug_data['error'] = str(e) + " " + traceback.format_exc()
                    exs = str(e)
                    track = traceback.format_exc()
                    with open("/home/mtp/ManuWork/python/scidb_specView_new/error.txt", "a+") as f:
                        f.write(str(datetime.now()) + " " + track)

                    raise Exception(exs)
                    # return no_update

        if not self.as_website:
            # websockets: https://community.plotly.com/t/support-for-websockets/19348/7
            #https://community.plotly.com/t/live-update-by-pushing-from-server-rather-than-polling-or-hitting-reload/23468/2
            #https://community.plotly.com/t/feature-request-for-builtin-support-or-a-component-to-support-callbacks-from-the-server-side/27099
            #https://community.plotly.com/t/triggering-callback-from-within-python/23321
            #https://drive.google.com/file/d/13WeuwPrhKPGRVZBAZCeBX3MtbvbNJOWZ/view

            #dicts unhashable:
            #https://github.com/plotly/dash-core-components/issues/332

            # update main spec figure every time the data changes

            @app.callback(
                Output('spec-graph', 'figure'),
                [Input('store', 'modified_timestamp')],
                [State('store', 'data')]
            )
            def update_figure(modified_timestamp, data):
                if data is not None:
                    self.write_info("UPDATE FIGURE: Starting updating figure from data")
                    #data_dict = json.loads(data)
                    #json_string = json.dumps(data_dict)
                    figure = self.get_spec_figure_from_data(data)
                    #f1 = json.dumps(figure)
                    self.write_info("UPDATE FIGURE: End updating figure from data")
                    return figure
                else:
                    self.write_info("UPDATE FIGURE: data is empty")
                    return no_update
            b = '''
                    app.clientside_callback(
                        """
                        function(data) {
                            return {
                                'data': data,
                                'layout': {
                                     'yaxis': {'type': scale}
                                 }
                            }
                        }
                        """,
                        Output('spec-graph', 'figure'),
                        [Input('store', 'data')]
                    )
                    '''

            # update dropdown of traces every time the data changes
            @app.callback(
                Output('dropdown-for-traces', 'options'),
                [Input('store', 'modified_timestamp')],
                [State('store', 'data')]
            )
            def update_dropdown(modified_timestamp, data):
                self.write_info("UPDATE DROPDOWN: start")
                data_dict = self.get_data_dict(data)
                dropdown_options = self.get_dropdown_options(data_dict)
                self.write_info("UPDATE DROPDOWN: end")
                return dropdown_options

            @app.callback(
                Output('store', 'data'),
                #[Input('synch_interval', 'n_intervals'), Input('upload-data', 'contents')],
                [Input('synch_interval', 'n_intervals'), Input("remove_trace_button", "n_clicks"), Input('upload-data', 'contents')],
                [State('upload-data', 'filename'),
                 State('upload-data', 'last_modified'),
                 State('store', 'data'),
                 State('store', 'modified_timestamp'),
                 State('dropdown-for-traces', 'value')
                 ])
            #def process_input(n_intervals, list_of_contents, list_of_names, list_of_dates, data, dropdown_values):
            def process_input(n_intervals, n_clicks, list_of_contents, list_of_names, list_of_dates, data, data_timestamp, dropdown_values):
                try:
                    task_name = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
                    if task_name == "synch_interval":
                        #self.write_info(
                        #    "Interval check: ENTER with timestamps " + str(None) + " " + str(self.app_data_timestamp['timestamp']) if data_timestamp is None else "Interval check: ENTER with timestamps " + str(data_timestamp / 1000) + " " + str(
                        #        self.app_data_timestamp['timestamp']), '')

                        # bring new data from global app_data to local data
                        if data_timestamp is None or data_timestamp/1000 < self.app_data_timestamp['timestamp']:
                            self.write_info("Interval check: START synchronizing appdata into datadict")
                            data_dict = self.get_data_dict(data)
                            self.synch_data(base_data_dict=self.app_data, incomplete_data_dict=data_dict, do_update_client=False)
                            self.write_info("Interval check: EXIT synch. Traces in datadict: " + str([trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str([trace for trace in self.app_data['traces']]))
                            return data_dict
                        else:
                            #self.write_info("Interval check: no need to synchronize")
                            return no_update

                    elif task_name == "upload-data" and list_of_contents is not None:
                        self.write_info("Upload data button: start upload")
                        data_dict = self.get_data_dict(data)
                        new_data = [
                            self.parse_uploaded_file(c, n) for c, n, d in
                            zip(list_of_contents, list_of_names, list_of_dates)]
                        #traces = { name:trace for (name,trace) in new_data }
                        for (name, trace) in new_data:
                            self.write_info("Upload data button: adding trace " + name + " to datadict")
                            self.add_trace_to_data(data_dict, name, trace, do_update_client=False)
                            self.write_info("Upload data button: adding trace " + name + " to add_data")
                            self.add_trace_to_data(self.app_data, name, trace, do_update_client=False)
                        self.write_info("Upload data button: ended upload. Traces in datadict: " + str(
                            [trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str(
                            [trace for trace in self.app_data['traces']]))
                        return data_dict

                    elif task_name == "remove_trace_button" and len(dropdown_values) > 0:
                        self.write_info("Remove data button: remove of " + str(dropdown_values))
                        data_dict = self.get_data_dict(data)
                        self.write_info("Remove data button: Initial Traces in datadict: " + str(
                            [trace for trace in data_dict['traces']]) + ", Initial Traces in appdate: " + str(
                            [trace for trace in self.app_data['traces']]))
                        self._remove_traces(dropdown_values, data_dict, do_update_client=False)
                        self._remove_traces(dropdown_values, self.app_data, do_update_client=False)
                        self.write_info("Remove data button: remove ended. Traces in datadict: " + str(
                            [trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str(
                            [trace for trace in self.app_data['traces']]))
                        return data_dict

                    else:
                        # verify
                        do_update = False
                        if data is None:
                            return no_update
                        self.write_info("CHECK: traces in dropdown: " + str(dropdown_values) + " , traces in datadict: " + str([t for t in data['traces']]) )
                        for trace_name in data['traces']:
                            if trace_name not in dropdown_values:
                                do_update = True
                        if do_update:
                            return data
                        else:
                            return no_update


                except Exception as e:
                    exs = str(e)
                    track = traceback.format_exc()
                    with open("/home/mtp/ManuWork/python/scidb_specView_new/error.txt", "a+") as f:
                        f.write(str(datetime.now()) + " " + track)

                    # self.debug_data['error'] = str(e) + " " + traceback.format_exc()
                    raise Exception(exs)
                    # return no_update


    except:
        pass