import json
import dash
from specviewer import app_base_directory
from .models.enum_models import FluxUnit, SpectrumType
from datetime import datetime
from dash import no_update
from dash.dependencies import Output, Input, State, ClientsideFunction
import traceback
from specviewer.smoothing.smoother import Smoother, SmoothingKernels, default_smoothing_kernels

def load_callbacks(self): # self is passed as the Viewer class

    try:
        b = """
                # display APP data
                @self.app.callback(Output('live-update-text', 'children'),
                              [Input('interval-component', 'n_intervals')])
                def update_metrics(n):
                    return "APP DATA " + str(datetime.datetime.now()) + " " + str(app_data)

                """

        # display local data
        a = """
        @self.app.callback(
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
        """

        if False: #not self.as_website:
            # when on Jupyter, app_data has always the source of truth. All callbacks will be updating
            # local data and then app_data. Therefore, there is no need to update local data from app_data.
            # Only the figure has to be updated from the latest values in app_data
            @self.app.callback(Output('spec-graph', 'figure'),
                          [Input('refresh-data-interval', 'n_intervals')])
            def update_figure2(n):
                # print("from call " + n)
                # self.fill_spec_figure_with_app_data()
                self.spec_figure = self.get_spec_figure_from_data(self.app_data)
                return self.spec_figure

        b =="""
        @self.app.callback(
            Output('selected-data', 'children'),
            [Input('spec-graph', 'selectedData')])
        def display_selected_data(selectedData):
            # print("from call display_selected_data")
            self.app_data['seclection'] = selectedData
            return json.dumps(self.app_data['selection'], indent=2)
        

        @self.app.callback(
            Output('hover-data', 'children'),
            [Input('spec-graph', 'hoverData')])
        def display_hover_data(hoverData):
            # print("from call display_hover_data")
            self.app_data['hover_data'] = hoverData
            return json.dumps(self.app_data['hover_data'], indent=2)

        @self.app.callback(
            Output('click-data', 'children'),
            [Input('spec-graph', 'clickData')])
        def display_click_data(clickData):
            # print("from call display_click_data")
            self.app_data['click_data'] = clickData
            return json.dumps(self.app_data['click_data'], indent=2)

        @self.app.callback(
            Output('relayout-data', 'children'),
            [Input('spec-graph', 'relayoutData')])
        def display_relayout_data(relayoutData):
            # print("from call display_relayout_data")
            self.app_data['relayout_data'] = relayoutData
            return json.dumps(self.app_data['relayout_data'], indent=2)
        
        
        @self.app.callback(
            dash.dependencies.Output('output-container-button', 'children'),
            [dash.dependencies.Input('button', 'n_clicks')],
            [dash.dependencies.State('input-box', 'value')])
        def update_output(n_clicks, value):
            self.debug_data['update_output'] = "update_output"
            return 'The input value was "{}" and the button has been clicked {} times'.format(
                value,
                n_clicks
            )
        """

        a = """

                # update text every time the data changes
                @self.app.callback(
                    Output('live-update-text3', 'children'),
                    Input('store', 'data')
                )
                def update_from_client(data):
                    if data is not None:
                        return "LOCAL DATA2 " + " " + data
                    else:
                        return no_update


    """


        @self.app.callback(
            Output('redshift_input', 'value'),
            [Input("redshift-slider", "value"),]
        )
        def process_redshift_slider(redshift):
            if redshift != None:
                return float(redshift)
            else:
                return no_update

        @self.app.callback(
            Output('redshift-slider', 'value'),
            [Input("redshift_button", "n_clicks"),],
            [State("redshift_input","value")]
        )
        def process_redshidt_input(n_clicks, redshift_input):
            if redshift_input != None:
                return float(redshift_input)
            else:
                return no_update

        # update main spec figure every time the data changes
        # @self.app.callback(
        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_figure'
            ),
            Output('spec-graph', 'figure'),
            # [Input('store', 'data')],
            [Input('store', 'modified_timestamp'), Input('spectral-lines-switch', 'on'),
             Input('redshift-slider', 'value'),Input('spectral_lines_dropdown', 'value'),
             Input('and_mask_switch', 'on'),
             Input('dropdown-for-masks', 'value'),
             Input('show_error_button', 'n_clicks'),
             Input('store', 'data'),
            ],
            [#State('store', 'data'),
             State('spectral_lines_dict','value'),
             State('dropdown-for-traces', 'value'),
            ]
        )

        # update dropdown of traces every time the data changes
        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_dropdown_options'
            ),
            Output('dropdown-for-traces', 'options'),
            [Input('store', 'modified_timestamp'),Input('store', 'data')],
            #[State('store', 'data')]
        )

        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_smoothing_kernels_dropdown'
            ),
            Output('smoothing_kernels_dropdown', 'options'),
            [Input('store', 'modified_timestamp'),Input('store', 'data')],
            #[State('store', 'data')]
        )

        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_fitting_models_dropdown'
            ),
            Output('fitting-model-dropdown', 'options'),
            [Input('store', 'modified_timestamp'),Input('store', 'data')],
        )

        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_masks_dropdown'
            ),
            Output('dropdown-for-masks', 'options'),
            [Input('store', 'modified_timestamp'),Input('store', 'data')]
        )

        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='set_fitted_models_table'
            ),
            Output('fitted_models_table', 'children'),
            [Input('store', 'modified_timestamp'),Input('store', 'data')],
            #[State('store', 'data')]
        )

        self.app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='select_all_traces_in_dropdown'
            ),
            Output('dropdown-for-traces', 'value'),
            [Input("select_all_traces_button", "n_clicks")],
            [State('store', 'data'),State('dropdown-for-traces', 'value')]
        )

        if self.as_website:


            @self.app.callback(
                Output('store', 'data'),
                [Input("remove_trace_button", "n_clicks"),
                 Input('upload-data', 'contents'),
                 Input('trace_smooth_button', 'n_clicks'),
                 Input('trace_smooth_substract_button', 'n_clicks'),
                 Input('trace_unsmooth_button', 'n_clicks'),
                 Input('wavelength-unit', 'value'),
                 Input('flux-unit', 'value'),
                 Input('model_fit_button', 'n_clicks'),
                 Input('show_model_button', 'n_clicks'),
                 Input('show_sky_button', 'n_clicks'),
                 Input('url', 'search'),
                 Input('search_spectrum_button','n_clicks'),
                ],
                [State('upload-data', 'filename'),
                 State('upload-data', 'last_modified'),
                 State('store', 'data'),
                 State('store', 'modified_timestamp'),
                 State('dropdown-for-traces', 'value'),
                 State('smoothing_kernels_dropdown', 'value'),
                 State('kernel_width_box', 'value'),
                 State('fitting-model-dropdown', 'value'),
                 State('spec-graph', 'selectedData'),
                 State('remove_children_checklist', 'value'),
                 State("specid","value"),
                 ])
            # def process_input(n_intervals, list_of_contents, list_of_names, list_of_dates, data, dropdown_values):
            def process_input(n_clicks_remove_trace_button, list_of_contents, n_clicks_smooth_button,n_clicks_smooth_substract_button,
                              n_clicks_unsmooth_button, wavelength_unit, flux_unit, n_clicks_model_fit_button, show_model_button,show_sky_button,url_search_string,n_clicks_specid_button,
                              list_of_names, list_of_dates, data, data_timestamp, dropdown_trace_names,
                              smoothing_kernel_name, smoothing_kernel_width, fitting_models, selected_data, remove_children_checklist,specid):
                try:

                    # self.debug_data['process_uploaded_file'] = "process_uploaded_file"
                    task_name = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

                    # get data in local storage:
                    data_dict = data if data is not None else self.build_app_data()

                    if task_name == "upload-data" and list_of_contents is not None:
                        self.write_info("Start processing uploaded file")
                        new_data_list = [
                            self._parse_uploaded_file(c, n, wavelength_unit=wavelength_unit, flux_unit=flux_unit) for c, n, d in
                            zip(list_of_contents, list_of_names, list_of_dates)]
                        # traces = { name:trace for (name,trace) in new_data  }
                        for traces in new_data_list:
                            for trace in traces:
                                self._set_color_for_new_trace(trace, data_dict)
                                self._add_trace_to_data(data_dict, trace.get('name'), trace, do_update_client=False)

                        self.write_info("End processing uploaded file")
                        #return json.dumps(data_dict)
                        return data_dict

                    elif task_name == 'wavelength-unit' or task_name == 'flux-unit':
                        self._rescale_axis(data_dict, to_wavelength_unit=wavelength_unit, to_flux_unit=flux_unit)
                        return data_dict

                    elif task_name == "remove_trace_button" and len(dropdown_trace_names) > 0:
                        also_remove_children = True if len(remove_children_checklist)>0 else False
                        self._remove_traces(dropdown_trace_names, data_dict, do_update_client=False, also_remove_children=also_remove_children)
                        #return json.dumps(data_dict)
                        return data_dict

                    elif (task_name == "trace_smooth_button" or task_name == 'trace_smooth_substract_button') and len(dropdown_trace_names)>0 and len(smoothing_kernel_name) > 0:
                        do_substract = True if task_name == 'trace_smooth_substract_button' else False

                        smoother = self._get_smoother(smoothing_kernel_name, smoothing_kernel_width)
                        self._smooth_trace(dropdown_trace_names, data_dict, smoother, do_update_client=False, do_substract=do_substract)
                        #self._smooth_trace(dropdown_trace_names, data_dict, do_update_client=False, kernel=smoothing_kernel_name, kernel_width=int(smoothing_kernel_width), do_substract=do_substract)
                        return data_dict

                    elif task_name == "trace_unsmooth_button" and len(dropdown_trace_names)>0:
                        self._unsmooth_trace(dropdown_trace_names, data_dict, do_update_client=False)
                        return data_dict

                    elif task_name == "model_fit_button":
                        if selected_data is None or len(fitting_models) == 0 \
                           or len(dropdown_trace_names) == 0 or flux_unit == FluxUnit.AB_magnitude:
                            return no_update
                        #self._fit_model_to_flux(dropdown_trace_names, data_dict, fitting_models, selected_data, do_update_client=False)
                        model_fitters = [ self._get_model_fitter(trace_name, data_dict, fitting_model, selected_data) for trace_name in dropdown_trace_names for fitting_model in fitting_models]
                        _ = self._fit_model_to_flux(dropdown_trace_names, data_dict, model_fitters, selected_data, do_update_client=False)
                        return data_dict
                    elif task_name == "show_model_button":
                        if len(dropdown_trace_names)>0:
                            self._toggle_derived_traces(SpectrumType.MODEL, dropdown_trace_names, data_dict, do_update_client=False)
                            return data_dict
                        else:
                            return no_update
                    elif task_name == "show_sky_button":
                        if len(dropdown_trace_names)>0:
                            self._toggle_derived_traces(SpectrumType.SKY, dropdown_trace_names, data_dict, do_update_client=False)
                            return data_dict
                        else:
                          return no_update
                    elif task_name == "url":
                        specid= "dedW"
                        if url_search_string is not None and url_search_string != "":
                            self._load_from_specid(specid, wavelength_unit, flux_unit, data_dict)

                        return data_dict

                    elif task_name == "search_spectrum_button":
                        if len(specid) > 0:
                            self._load_from_specid_text(specid, wavelength_unit, flux_unit, data_dict)
                            self._send_websocket_message(json.dumps(data_dict))
                            return data_dict
                        else:
                            return no_update
                    else:
                        return no_update

                except Exception as e:
                    exs = str(e)
                    # self.debug_data['error'] = str(e) + " " + traceback.format_exc()
                    exs = str(e)
                    track = traceback.format_exc()
                    print(track)
                    with open(app_base_directory + "error.txt", "a+") as f:
                        f.write(str(datetime.now()) + " " + track)
                    raise Exception(exs)
                    # return no_update

        else:
            # websockets: https://community.plotly.com/t/support-for-websockets/19348/7
            #https://community.plotly.com/t/live-update-by-pushing-from-server-rather-than-polling-or-hitting-reload/23468/2
            #https://community.plotly.com/t/feature-request-for-builtin-support-or-a-component-to-support-callbacks-from-the-server-side/27099
            #https://community.plotly.com/t/triggering-callback-from-within-python/23321
            #https://drive.google.com/file/d/13WeuwPrhKPGRVZBAZCeBX3MtbvbNJOWZ/view

            #dicts unhashable:
            #https://github.com/plotly/dash-core-components/issues/332

            # update main spec figure every time the data changes

            @self.app.callback(
                Output('store', 'data'),
                [Input('synch_interval', 'n_intervals'),
                 Input("remove_trace_button", "n_clicks"),
                 Input('upload-data', 'contents'),
                 Input('trace_smooth_button', 'n_clicks'),
                 Input('trace_smooth_substract_button', 'n_clicks'),
                 Input('trace_unsmooth_button', 'n_clicks'),
                 Input('wavelength-unit', 'value'),
                 Input('flux-unit', 'value'),
                 Input('model_fit_button', 'n_clicks'),
                 Input('show_model_button', 'n_clicks'),
                 Input('show_sky_button', 'n_clicks'),
                 Input('spec-graph', 'selectedData'),
                 Input('search_spectrum_button','n_clicks'),
                 Input("pull_trigger","value"),
                 ],
                [State('upload-data', 'filename'),
                 State('upload-data', 'last_modified'),
                 State('store', 'data'),
                 State('store', 'modified_timestamp'),
                 State('dropdown-for-traces', 'value'),
                 State('smoothing_kernels_dropdown', 'value'),
                 State('kernel_width_box', 'value'),
                 State('fitting-model-dropdown', 'value'),
                 State('remove_children_checklist', 'value'),
                 State("specid", "value"),
                 ])
            #def process_input(n_intervals, list_of_contents, list_of_names, list_of_dates, data, dropdown_values):
            def process_input(n_intervals, n_clicks_remove_trace_button, list_of_contents, n_clicks_smooth_button, n_clicks_smooth_substract_button,
                              n_clicks_unsmooth_button, wavelength_unit, flux_unit, n_clicks_model_fit_button, show_model_button,show_sky_button, selected_data,
                              n_clicks_specid_button, pull_trigger_value,
                              list_of_names,list_of_dates, data, data_timestamp, dropdown_trace_names,
                              smoothing_kernel_name,smoothing_kernel_width, fitting_models, remove_children_checklist, specid):
                try:
                    task_name = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
                    data_dict = data if data is not None else self.build_app_data()

                    if task_name == "pull_trigger":
                        if pull_trigger_value == "":
                            return no_update
                        else:
                            self.write_info("Pull Trigger: START synchronizing appdata into datadict")
                            #self._synch_data(base_data_dict=self.app_data, incomplete_data_dict=data_dict, do_update_client=False)
                            self.write_info("Pull Trigger: EXIT synch. Traces in datadict: " + str([trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str([trace for trace in self.app_data['traces']]))
                            return self.app_data.copy()

                    if task_name == "synch_interval":
                        #self.write_info(
                        #    "Interval check: ENTER with timestamps " + str(None) + " " + str(self.app_data_timestamp['timestamp']) if data_timestamp is None else "Interval check: ENTER with timestamps " + str(data_timestamp / 1000) + " " + str(
                        #        self.app_data_timestamp['timestamp']), '')

                        # bring new data from global app_data to local data

                        if data_timestamp is None or data_timestamp/1000 < self.app_data_timestamp['timestamp'] :
                           #or {trace for trace in self.app_data['traces']} != {trace for trace in data_dict['traces']}:
                            self.write_info("Interval check: START synchronizing appdata into datadict")
                            #self._synch_data(base_data_dict=self.app_data, incomplete_data_dict=data_dict, do_update_client=False)
                            self.write_info("Interval check: EXIT synch. Traces in datadict: " + str([trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str([trace for trace in self.app_data['traces']]))
                            return self.app_data.copy()
                        else:
                            #self.write_info("Interval check: no need to synchronize")
                            return no_update


                    elif task_name == "upload-data" and list_of_contents is not None:
                        self.write_info("Upload data button: start upload")
                        new_data_list = [
                            self._parse_uploaded_file(c, n, wavelength_unit=wavelength_unit, flux_unit=flux_unit) for c, n, d in
                            zip(list_of_contents, list_of_names, list_of_dates)]
                        #traces = { name:trace for (name,trace) in new_data }
                        for traces in new_data_list:
                            for trace in traces:
                                self.write_info("Upload data button: adding trace " + trace.get('name') + " to datadict")
                                self._set_color_for_new_trace(trace, self.app_data)
                                #self._add_trace_to_data(data_dict, trace.get('name'), trace, do_update_client=False)
                                self._add_trace_to_data(self.app_data, trace.get('name'), trace, do_update_client=False)
                            #self._synch_data(self.app_data, data_dict, do_update_client=False)
                        try:
                            self.write_info("Upload data button: ended upload. Traces in datadict: " + str(
                                [trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str(
                                [trace for trace in self.app_data['traces']]))
                        except Exception as e :
                            self.write_info("Error in writing info about uploading of files: "+ str(e))

                        #return data_dict
                        return self.app_data.copy()

                    elif task_name == 'wavelength-unit' or task_name == 'flux-unit':
                        data_dict = self.get_data_dict(data)
                        #self._rescale_axis(data_dict, to_wavelength_unit=wavelength_unit, to_flux_unit=flux_unit, do_update_client=False)
                        self._rescale_axis(self.app_data, to_wavelength_unit=wavelength_unit, to_flux_unit=flux_unit, do_update_client=False)
                        self._synch_data(self.app_data, data_dict, do_update_client=False)
                        return data_dict

                    elif task_name == "remove_trace_button" and len(dropdown_trace_names) > 0:
                        self.write_info("Remove data button: remove of " + str(dropdown_trace_names))
                        also_remove_children = True if len(remove_children_checklist) > 0 else False
                        self.write_info("Remove data button: Initial Traces in datadict: " + str(
                            [trace for trace in data_dict['traces']]) + ", Initial Traces in appdate: " + str(
                            [trace for trace in self.app_data['traces']]))
                        #self._remove_traces(dropdown_trace_names, data_dict, do_update_client=False, also_remove_children=also_remove_children)
                        self._remove_traces(dropdown_trace_names, self.app_data, do_update_client=False, also_remove_children=also_remove_children)
                        self._synch_data(self.app_data, data_dict, do_update_client=False)
                        try:
                            self.write_info("Remove data button: remove ended. Traces in datadict: " + str(
                                [trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str(
                                [trace for trace in self.app_data['traces']]))
                        except Exception as e:
                            self.write_info("Error in writing info about removal of traces: "+str(e))

                        return data_dict

                    elif (task_name == "trace_smooth_button" or task_name == 'trace_smooth_substract_button') and len(dropdown_trace_names)>0 and len(smoothing_kernel_name) > 0:
                        do_substract = True if task_name == 'trace_smooth_substract_button' else False
                        #self._smooth_trace(dropdown_trace_names, data_dict, do_update_client=False,
                        #                   kernel=smoothing_kernel_name, kernel_width=int(smoothing_kernel_width),
                        #                   do_substract=do_substract)


                        smoother = self._get_smoother(smoothing_kernel_name, smoothing_kernel_width)
                        self._smooth_trace(dropdown_trace_names, self.app_data, smoother, do_update_client=False, do_substract=do_substract)
                        #self._smooth_trace(dropdown_trace_names, self.app_data, do_update_client=False,kernel=smoothing_kernel_name, kernel_width=int(smoothing_kernel_width),do_substract=do_substract)
                        self._synch_data(self.app_data, data_dict, do_update_client=False)
                        return data_dict

                    elif task_name == "trace_unsmooth_button" and len(dropdown_trace_names)>0:
                        #self._unsmooth_trace(dropdown_trace_names, data_dict, do_update_client=False)
                        self._unsmooth_trace(dropdown_trace_names, self.app_data, do_update_client=False)
                        self._synch_data(self.app_data, data_dict, do_update_client=False)
                        return data_dict

                    elif task_name == "model_fit_button":
                        self.write_info("Start fitting model")
                        if selected_data is None or selected_data == {} or len(fitting_models) == 0 \
                           or len(dropdown_trace_names) == 0 or flux_unit == FluxUnit.AB_magnitude:
                            self.write_info("End fitting model: no update")
                            return no_update

                        #self._fit_model_to_flux(dropdown_trace_names, self.app_data, fitting_models, selected_data, do_update_client=False)

                        model_fitters = [self._get_model_fitter(trace_name, self.app_data, fitting_model, selected_data) for trace_name in dropdown_trace_names for fitting_model in fitting_models]
                        _ = self._fit_model_to_flux(dropdown_trace_names, self.app_data, model_fitters, selected_data, do_update_client=False)

                        self._synch_data(self.app_data, data_dict, do_update_client=False)
                        self.write_info("End fitting model . Traces in datadict: " + str(
                            [trace for trace in data_dict['traces']]) + ", Traces in appdata: " + str(
                            [trace for trace in self.app_data['traces']]) + " FittedModels in data dict: " + str([x for x in data_dict['fitted_models']]) + " FittedModels in app_data: " + str([x for x in self.app_data['fitted_models']])   )

                        return data_dict

                    elif task_name == "show_model_button":
                        if len(dropdown_trace_names)>0:
                            #self._toggle_derived_traces(SpectrumType.MODEL, dropdown_trace_names, data_dict, do_update_client=False)
                            self._toggle_derived_traces(SpectrumType.MODEL, dropdown_trace_names, self.app_data, do_update_client=False)
                            #self._synch_data(self.app_data, data_dict, do_update_client=False)
                            return self.app_data.copy()
                        else:
                            return no_update
                    elif task_name == "show_sky_button":
                        if len(dropdown_trace_names)>0:
                            self._toggle_derived_traces(SpectrumType.SKY, dropdown_trace_names, self.app_data, do_update_client=False)
                            #self._synch_data(self.app_data, data_dict, do_update_client=False)
                            return self.app_data.copy()
                        else:
                            return no_update
                    elif task_name == "spec-graph":
                        # data_dict['selection'] = selected_data # no need to save it in data_dict, since fit in UI is triggered by the fit button.
                        self.app_data['selection'] = self._get_selection(selected_data, self.app_data)
                        return no_update

                    elif task_name == "search_spectrum_button":
                        if len(specid) > 0:
                            self.write_info("Start adding from specid")
                            #self._load_from_specid_text(specid, wavelength_unit, flux_unit, data_dict)
                            self._load_from_specid_text(specid, wavelength_unit, flux_unit, self.app_data)
                            #self._synch_data(self.app_data, data_dict, do_update_client=False)
                            self.write_info("End adding from specid " + str([x for x in data_dict['traces']]) + " " + str([x for x in self.app_data['traces']]) )
                            #return data_dict
                            return self.app_data.copy()
                        else:
                            return no_update

                    else:
                        # verify
                        return no_update
                        a= """
                        do_update = False
                        if data is None:
                            return no_update
                        self.write_info("CHECK: traces in dropdown: " + str(dropdown_trace_names) + " , traces in datadict: " + str([t for t in data['traces']]) )
                        for trace_name in data['traces']:
                            if trace_name not in dropdown_trace_names:
                                do_update = True
                        if do_update:
                            return data
                        else:
                            return no_update
                        """

                except Exception as e:
                    exs = str(e)
                    track = traceback.format_exc()
                    #with open(app_base_directory + "error.txt", "a+") as f:
                    #    f.write(str(datetime.now()) + " " + track)
                    self.write_info("EXCEPTION: " + track)

                    # self.debug_data['error'] = str(e) + " " + traceback.format_exc()
                    raise Exception(exs)
                    # return no_update


    except:
        pass
