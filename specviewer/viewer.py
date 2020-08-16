import flask
from flask_socketio import SocketIO
from jupyter_dash import JupyterDash

from specviewer import app_base_directory, external_stylesheets,external_scripts, port
from specviewer.file_browser.search import get_spectrum_path
import numpy as np

from specviewer import data_driver
from specviewer import app_layout, callbacks
from datetime import datetime

import multiprocessing
import base64
import io
from astropy.io import fits
from astropy.convolution import convolve, Gaussian1DKernel, Box1DKernel, CustomKernel
from astropy.convolution.kernels import Model1DKernel
from .models.enum_models import WavelenghUnit, FluxUnit, FittingModels, SmoothingKernels, SpectrumType
from .models.data_models import Trace
from astropy.modeling import Fittable1DModel
from specviewer.colors import get_next_color
import specviewer.flux as fl
from astropy.modeling import models, fitting
from specviewer.utilities import get_specid_list, get_unused_port
from .smoothing.smoother import Smoother, default_smoothing_kernels
process_manager = multiprocessing.Manager()
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# create global variable only for use inside jupyter
#app_data = process_manager.dict()
#debug_data = process_manager.dict()
#app_data_timestamp = process_manager.dict()

#https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes
#https://stackoverflow.com/questions/17377426/shared-variable-in-pythons-multiprocessing
#https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Value

class Viewer():
    # app_data = {}

    APP_DATA_KEYS = ["traces", "fitted_models", "selection", "smoothing_kernels"]

    def __init__(self, as_website=False):
        # global app_data
        # global fig
        self.as_website = as_website
        self.app_port = get_unused_port(initial_port=port)
        self.as_website = as_website
        # just for testing local website
        # self.app_data = {'traces':{}, 'selection':{}} #application_data.ApplicationData()
        # self.app_data = app_data

        self.server = flask.Flask(__name__)  # define flask app.server
        #self.app = JupyterDash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts,server=self.server)
        self.app = JupyterDash(__name__, external_stylesheets=external_stylesheets,external_scripts=external_scripts, server=self.server)
        self.socketio = SocketIO(self.server)
        #self.app = JupyterSocketDash(__name__, external_stylesheets=external_stylesheets,external_scripts=external_scripts, server=self.server)
        self.app.server.secret_key = 'SOME_KEY_STRING'

        self.app_data = process_manager.dict()
        self.app_data_timestamp = process_manager.dict()
        for key,value in self.build_app_data().items():
            self.app_data[key] = value

        # setting the default values, which also show in the UI dropdown.

        #self.app_data['traces'] = {}
        #self.app_data['fitted_models'] = {}
        #self.app_data['selection'] = {}
        self.app_data_timestamp['timestamp'] = 0
        self.debug_data = process_manager.dict()

        self.smoother = Smoother()

        # self.spectral_lines_info = spectral_lines_info
        # self.view = V.SpecView(width, height, dpi)
        # self.view.select_all_button.on_clicked(self.select_all_button_callback)
        # self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        # self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())

        # self.spec_figure = make_subplots(rows=1, cols=1)
        # self.fill_spec_figure_with_app_data()
        #self.spec_figure = self.get_spec_figure_from_data(self.app_data)

        #app.layout = self.load_app_layout
        self.app.layout = app_layout.load_app_layout(self, self.app_port)
        callbacks.load_callbacks(self)

    def show_jupyter_app(self, debug=False):
        if not self.as_website:
            # self.load_callbacks()
            # self.load_callbacks()
            # app.layout = self.load_app_layout
            # app.layout = self.load_app_layout
            #jupyter_viewer.show(app)  # for dash + jupyterlab_dash
            #app.run_server(mode='inline')  # dash + jupyterdash
            #app.run_server(mode='jupyterlab', port=port, debug=True, dev_tools_ui=True,dev_tools_props_check=True,dev_tools_hot_reload=True, inline_exceptions=True, dev_tools_silence_routes_logging=False) # dash + jupyterdash
            self.app.run_server(mode='jupyterlab', port=self.app_port, debug=debug, dev_tools_ui=True,dev_tools_props_check=True,dev_tools_hot_reload=True,dev_tools_silence_routes_logging=True)  # dash + jupyterdash
            #jupyter_viewer.show(socketio_app)  # dash + jupyterlab_dash + socketIO
            #self.socketio_app.run(app.server) # dash + jupyterdash + socketIO

    @staticmethod
    def build_app_data():
        d = {}
        for key in Viewer.APP_DATA_KEYS:
            d[key] = {}

        # initialize smoothing kernels with the list of default names
        d["smoothing_kernels"] = default_smoothing_kernels
        return d

    def _parse_uploaded_file(self, contents, file_name, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda):

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        hdulist = fits.open(io.BytesIO(decoded))

        if "." in file_name:
            file_name_parts = file_name.split(".")
            file_name = ".".join(file_name_parts[:(len(file_name_parts)-1)])

        return self._load_from_hdu(hdulist, file_name, wavelength_unit=wavelength_unit, flux_unit=flux_unit)

    def _load_from_specid_text(self,specid_text,wavelength_unit, flux_unit, data_dict):
        specid_list = get_specid_list(specid_text)
        for specid in specid_list :
            self._load_from_specid(specid, wavelength_unit, flux_unit, data_dict)

    def _load_from_specid(self, specid, wavelength_unit, flux_unit, data_dict):
        name, spectrum_path = get_spectrum_path(specid=specid)
        self._add_spectrum_from_file(spectrum_path,data_dict,wavelength_unit,flux_unit,name)

    def _load_from_hdu(self, hdulist, name, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda):

        # assumes that spectrum wavelength units are in Armstrong:
        spectrum_list = data_driver.get_trace_list_from_fits(hdulist, name)

        rescaled_traces = []
        for spectrum in spectrum_list:
            trace = spectrum.to_dict()
            rescaled_traces.append(self._get_rescaled_axis_in_trace(trace, to_wavelength_unit=wavelength_unit,
                                                                   to_flux_unit=flux_unit))
        return rescaled_traces

    def _add_spectrum_from_file(self, file_path, data_dict, wavelength_unit, flux_unit, name=None, do_update_client=False):
        hdulist = fits.open(file_path)
        if name is None:
            file_path_parts = file_path.split("/")
            name_parts = file_path_parts[-1].split(".")
            name = ".".join(name_parts[:(len(name_parts) - 1)])

        rescaled_traces = self._load_from_hdu(hdulist, name, wavelength_unit, flux_unit)
        for trace in rescaled_traces:
            self._set_color_for_new_trace(trace, data_dict)
            self._add_trace_to_data(data_dict, trace.get('name'), trace, do_update_client=False)

        if do_update_client:
            self.update_client()



    def _set_color_for_new_trace(self, trace, application_data):
        current_traces_colors = [application_data['traces'][trace_name]['color'] for trace_name in application_data['traces']]
        new_color = get_next_color(current_traces_colors)
        trace['color'] = new_color


    def _synch_data(self,base_data_dict,incomplete_data_dict,do_update_client=False):
        #self.write_info("inc0  start " + str(incomplete_data_dict) + " " + str(base_data_dict))
        a = """
        for trace_name in base_data_dict['traces']:
            #self.write_info("inc0  trace  " +  trace_name + " " + str(incomplete_data_dict) + " " + str(base_data_dict))
            # if trace_name not in incomplete_data_dict['traces']:
            self.add_trace_to_data(incomplete_data_dict, trace_name, base_data_dict['traces'][trace_name], do_update_client=do_update_client)
            #self.write_info("inc0 "+ trace_name + str(incomplete_data_dict) )
        #self.write_info("inc0  end")
        """
        for key in Viewer.APP_DATA_KEYS:
            incomplete_data_dict[key] = base_data_dict[key]
        if do_update_client:
            self.update_client()

    def _add_trace_to_data(self, application_data, name, trace, do_update_client = True):
        traces = application_data['traces']
        if name in traces:
            raise Exception("Trace named '" + name + "' already exists.")

        num_stored_traces = len(application_data['traces'])
        trace['curveNumber'] = num_stored_traces # in base 0
        traces[name] = trace
        application_data['traces'] = traces

        if do_update_client:
            self.update_client()

    def _remove_traces(self, trace_names, data, do_update_client=True, also_remove_children=False):

        #add derived traces to be removed:
        _traces_to_remove = [name for name in trace_names]
        for name in data['traces']:
            for ancestor in data['traces'][name]['ancestors']:
                if ancestor in _traces_to_remove:
                    if also_remove_children:
                        _traces_to_remove.append(name)
                    else:
                        # remove only if it is not visible
                        if data['traces'][name]['is_visible'] == False:
                            _traces_to_remove.append(name)

        # remove duplicates
        _traces_to_remove = set(_traces_to_remove)

        traces = data['traces']
        for trace_name in _traces_to_remove:
            traces.pop(trace_name)
        data['traces'] = traces

        # update fitted models
        fitted_models = data['fitted_models']
        fitted_models_names = [model for model in data['fitted_models']]
        for model in fitted_models_names:
            for trace_name in _traces_to_remove:
                if trace_name == model:
                    fitted_models.pop(model)
        data['fitted_models'] = fitted_models

        if do_update_client:
            self.update_client()


    def _toggle_derived_traces(self, derived_trace_type, ancestor_trace_names, data_dict, do_update_client=False):
        ancestor_trace_names = np.asarray(ancestor_trace_names)
        traces = data_dict['traces']
        for derived_trace_name in traces:
            trace = traces[derived_trace_name]
            has_selected_ancestors = np.any(np.in1d(ancestor_trace_names,np.asarray(trace.get('ancestors'))))
            if has_selected_ancestors:
                if trace["spectrum_type"] == derived_trace_type:
                    #self.write_info("Toggle " + derived_trace_name + " from is_visible=" + str(data_dict['traces'][derived_trace_name]["is_visible"]))
                    trace["is_visible"] = False if trace["is_visible"] == True else True
                    #self.write_info("Toggle " + derived_trace_name + " intermediate to is_visible=" + str(trace["is_visible"]))
                    traces[derived_trace_name] = trace
                    #self.write_info("Toggle " + derived_trace_name + " to is_visible=" + str(data_dict['traces'][derived_trace_name]["is_visible"]))
        data_dict["traces"] = traces

        if do_update_client:
            self.update_client()


    def _include_derived_traces(self, spectrum_types, ancestor_trace_names, data_dict, do_update_client=False):
        ancestor_trace_names = np.asarray(ancestor_trace_names)
        for derived_trace_name in data_dict['traces']:
            trace = data_dict['traces'][derived_trace_name]
            has_selected_ancestors = np.any(np.in1d(ancestor_trace_names,np.asarray(trace.get('ancestors'))))
            if has_selected_ancestors:
                if trace["spectrum_type"] in spectrum_types:
                    trace["is_visible"] = True
                else:
                    trace["is_visible"] = False
                data_dict[derived_trace_name] = trace
        if do_update_client:
            self.update_client()




    def write_info(self, info, file_endding=''):
        if file_endding != '':
            file_endding = '_' + file_endding
        with open(app_base_directory +  'info' + file_endding +'.txt', 'a+') as f:
            f.write(str(datetime.now()) + " " + info + "\n")


    def __set_app_data_timestamp(self, timestamp=None):
        if timestamp is not None:
            self.app_data_timestamp['timestamp'] = timestamp # in sceconds
        else:
            self.app_data_timestamp['timestamp'] = datetime.timestamp(datetime.now())  # in sceconds
        self.write_info("Updated timestamp to " + str(self.app_data_timestamp['timestamp']))

    def update_client(self, timestamp=None):
        #self.__set_app_data_timestamp(timestamp)
        # https://stackoverflow.com/questions/28947581/how-to-convert-a-dictproxy-object-into-json-serializable-dict
        #self._send_websocket_message(json.dumps(self.app_data.copy()))
        self._send_websocket_message("{}")

    def _send_websocket_message(self, message):
        self.socketio.emit("update", message)

    def get_data_dict(self, data):
        #return json.loads(data) if data is not None else self.build_app_data()
        return data if data is not None else self.build_app_data()

    def _unsmooth_trace(self, trace_names, application_data, do_update_client=True):
        for trace_name in trace_names:
            traces = application_data['traces']
            trace = traces[trace_name]

            # use original flux stored as flambda
            flux = fl.convert_flux(flux=trace['flambda'], wavelength=trace['wavelength'],
                                   from_flux_unit=FluxUnit.F_lambda, to_flux_unit=trace.get('flux_unit'),
                                   to_wavelength_unit=trace.get('wavelength_unit'))
            trace['flux'] = flux
            traces[trace_name] = trace
            application_data['traces'] = traces

        if do_update_client:
            self.update_client()


    def _smooth_trace(self, trace_names, application_data, smoother, do_update_client=True, do_substract=False):
        for trace_name in trace_names:
            if trace_name in application_data['traces']:
                traces = application_data['traces']
                trace = traces[trace_name]

                flux = fl.convert_flux(flux=trace['flambda'], wavelength=trace['wavelength'],from_flux_unit=FluxUnit.F_lambda,to_flux_unit=trace.get('flux_unit'), to_wavelength_unit=trace.get('wavelength_unit'))

                smoothed_flux = smoother.get_smoothed_flux(flux)

                if do_substract:
                    smoothed_flux = flux - smoothed_flux
                trace['flux'] = smoothed_flux

                #remove old trace and replace it with new trace containing smoothed data
                traces[trace_name] = trace
                application_data['traces'] = traces

                # if kernel is custom, add it to the data dict:
                current_smoothing_kernels = application_data['smoothing_kernels']
                if smoother.kernel_func_type not in current_smoothing_kernels:
                    current_smoothing_kernels.append(smoother.kernel_func_type)
                application_data['smoothing_kernels'] = current_smoothing_kernels

        if do_update_client:
            self.update_client()





    def _smooth_trace2(self, trace_names, application_data, do_update_client=True, kernel=SmoothingKernels.GAUSSIAN1D, kernel_width=21, custom_kernel_array=None, custom_kernel_function=None, function_array_size=21, do_substract=False):
        # https://specutils.readthedocs.io/en/stable/manipulation.html
        # https://docs.astropy.org/en/stable/convolution/kernels.html

        # https://docs.astropy.org/en/stable/convolution/kernels.html
        # https://het.as.utexas.edu/HET/Software/Astropy-0.4.2/convolution/kernels.html
        # http://learn.astropy.org/rst-tutorials/User-Defined-Model.html
        # https://keflavich-astropy.readthedocs.io/en/latest/modeling/new.html
        # https://docs.astropy.org/en/stable/modeling/reference_api.html#module-astropy.modeling

        if self.as_website:
            smoother = Smoother()
            smoother.set_smoother(kernel, kernel_width, custom_kernel_array, custom_kernel_function,
                                  function_array_size)
        else:
            smoother = self.smoother
            smoother.set_smoother(kernel, kernel_width, custom_kernel_array, custom_kernel_function,
                                  function_array_size)

        for trace_name in trace_names:
            if trace_name in application_data['traces']:
                traces = application_data['traces']
                trace = traces[trace_name]

                a = """
                if custom_kernel_array is None and custom_kernel_function is None:
                    if kernel == SmoothingKernels.GAUSSIAN1D:
                        kernel_func = Gaussian1DKernel(int(kernel_width))
                    elif kernel == SmoothingKernels.Box1D:
                        kernel_func = Box1DKernel(int(kernel_width))
                    else:
                        raise Exception("Unsupported smoothing kernel " + str(kernel))
                elif custom_kernel_array is not None:
                    custom_kernel_array =  np.array([i for i in custom_kernel_array])
                    kernel_func = CustomKernel(custom_kernel_array)

                elif custom_kernel_function is not None:
                    if not isinstance(custom_kernel_function, Fittable1DModel):
                        raise Exception("custom_kernel_function must be an instance of astropy.modeling.Fittable1DModel")
                    kernel_func = Model1DKernel(custom_kernel_function, x_size=function_array_size)

                else:
                    raise Exception("Problem choosing smoothing kernel")
                """

                flux = fl.convert_flux(flux=trace['flambda'], wavelength=trace['wavelength'],from_flux_unit=FluxUnit.F_lambda,to_flux_unit=trace.get('flux_unit'), to_wavelength_unit=trace.get('wavelength_unit'))
                #smoothed_flux = convolve(flux, kernel_func)

                smoothed_flux = smoother.get_smoothed_flux(flux)

                if do_substract:
                    smoothed_flux = flux - smoothed_flux
                trace['flux'] = smoothed_flux

                #remove old trace and replace it with new trace containing smoothed data
                traces[trace_name] = trace
                application_data['traces'] = traces

                # if kernel is custom, add it to the data dict:
                current_smoothing_kernels = application_data['smoothing_kernels']
                if smoother.kernel_func_type not in current_smoothing_kernels:
                    current_smoothing_kernels.append(smoother.kernel_func_type)
                application_data['smoothing_kernels'] = current_smoothing_kernels

        if do_update_client:
            self.update_client()

    def _rescale_axis(self, application_data, to_wavelength_unit=WavelenghUnit.ANGSTROM, to_flux_unit=FluxUnit.F_lambda, do_update_client=False):
        traces = application_data['traces']
        for trace_name in traces:
           rescaled_trace = self._get_rescaled_axis_in_trace(traces[trace_name], to_wavelength_unit=to_wavelength_unit, to_flux_unit=to_flux_unit)
           traces[trace_name] = rescaled_trace

        application_data['traces'] = traces
        if do_update_client:
            self.update_client()

    def _get_rescaled_axis_in_trace(self, trace, to_wavelength_unit=WavelenghUnit.ANGSTROM, to_flux_unit=FluxUnit.F_lambda):
        # https://synphot.readthedocs.io/en/latest/synphot/units.html
        # https://synphot.readthedocs.io/en/latest/api/synphot.units.convert_flux.html#synphot.units.convert_flux

        # for wavelength axis:
        trace['wavelength'] = fl.convert_wavelength(wavelength=trace['wavelength'], from_wavelength_unit=trace['wavelength_unit'], to_wavelength_unit=to_wavelength_unit)
        trace['wavelength_unit'] = to_wavelength_unit

        # for flux axis:
        if trace.get('flux_unit') == FluxUnit.AB_magnitude and to_flux_unit != FluxUnit.AB_magnitude:
            if trace.get("flambda") is not None and len(trace.get("flambda")) > 0:
                trace['flux'] = fl.convert_flux(flux=trace.get("flambda"), wavelength=trace['wavelength'],from_flux_unit=FluxUnit.F_lambda,to_flux_unit=to_flux_unit, to_wavelength_unit=to_wavelength_unit)
                trace['flux_error'] = fl.convert_flux(flux=trace.get("flambda_error"), wavelength=trace['wavelength'],from_flux_unit=FluxUnit.F_lambda, to_flux_unit=to_flux_unit,to_wavelength_unit=to_wavelength_unit)
            else:
                trace['flux'] = fl.convert_flux(flux=trace['flux'], wavelength=trace['wavelength'],from_flux_unit=trace.get('flux_unit'), to_flux_unit=to_flux_unit, to_wavelength_unit=to_wavelength_unit)
                trace['flux_error'] = fl.convert_flux(flux=trace['flux_error'], wavelength=trace['wavelength'],from_flux_unit=trace.get('flux_unit'), to_flux_unit=to_flux_unit,to_wavelength_unit=to_wavelength_unit)
        else:
            trace['flux'] = fl.convert_flux(flux=trace['flux'], wavelength=trace['wavelength'],from_flux_unit=trace.get('flux_unit'),to_flux_unit=to_flux_unit, to_wavelength_unit=to_wavelength_unit)
            trace['flux_error'] = fl.convert_flux(flux=trace['flux_error'], wavelength=trace['wavelength'],from_flux_unit=trace.get('flux_unit'), to_flux_unit=to_flux_unit,to_wavelength_unit=to_wavelength_unit)

        trace['flux_unit'] = to_flux_unit
        return trace


    def _fit_model_to_flux(self, trace_names, application_data, fitting_models, selected_data, custom_model=None,
                           custom_fitter=None, do_update_client=True, include_fit_substracted_trace=False):
        # http://learn.astropy.org/rst-tutorials/User-Defined-Model.html
        # https://docs.astropy.org/en/stable/modeling/new-model.html
        # https://docs.astropy.org/en/stable/modeling/index.html
        # https://docs.astropy.org/en/stable/modeling/reference_api.html

        for fitting_model in fitting_models:
            for trace_name in trace_names:
                #ind = trace_indexes[trace_name]

                trace = application_data['traces'].get(trace_name)

                x = np.asarray([point['x'] for point in selected_data["points"] if point['curveNumber'] == trace["curveNumber"] ] )
                y = np.asarray([point['y'] for point in selected_data["points"] if point['curveNumber'] == trace["curveNumber"]])
                ind = [point['pointIndex'] for point in selected_data["points"] if point['curveNumber'] == trace["curveNumber"]]

                min_x,max_x = np.min(x),np.max(x)

                if custom_model is None and custom_fitter is None:

                    location_param = np.mean(x)
                    amplitude_param = np.max(np.abs(y))
                    spread_param = (max_x - min_x) / len(x)

                    if fitting_model == FittingModels.GAUSSIAN_PLUS_LINEAR:
                        data_model = models.Gaussian1D(amplitude=amplitude_param, mean=location_param, stddev=spread_param) + models.Polynomial1D(degree=1)
                    elif fitting_model == FittingModels.LORENTZIAN_PLUS_LINEAR:
                        data_model = models.Lorentz1D(amplitude=amplitude_param, x_0=location_param, fwhm=spread_param) + models.Polynomial1D(degree=1)
                    elif fitting_model == FittingModels.VOIGT_PLUS_LINEAR:
                        data_model = models.Voigt1D(x_0=location_param, amplitude_L=amplitude_param, fwhm_L=spread_param, fwhm_G=spread_param) + models.Polynomial1D(degree=1)
                    else:
                        raise Exception("Unsupported fitting model " + str(fitting_model))

                    fitting_model_name = fitting_model
                    fitter = fitting.LevMarLSQFitter()
                    fitted_model = fitter(data_model, x, y)

                else:
                    fitting_model_name = str(custom_model)
                    fitter = custom_fitter
                    fitted_model = fitter(custom_model, x, y)


                x_grid = np.linspace(min_x, max_x, 5*len(x))
                y_grid = fitted_model(x_grid)

                parameter_errors =  np.sqrt(np.diag(fitter.fit_info['param_cov'])) if fitter.fit_info['param_cov'] is not None else None

                fitted_trace_name = "fit" + str(len(application_data['fitted_models']) + 1) + "_" + trace_name
                ancestors = trace['ancestors'] + [trace_name]
                flambda = [f for f in np.asarray(trace['flambda'])[ind]]
                fitted_trace = Trace(name=fitted_trace_name, wavelength=[x for x in x_grid], flux=[y for y in y_grid],
                                                ancestors=ancestors,spectrum_type=SpectrumType.FIT, color="black", linewidth=1, alpha=1.0,
                                                wavelength_unit=trace['wavelength_unit'], flux_unit=trace['flux_unit'],
                                                flambda=flambda, catalog=trace['catalog']).to_dict()

                self._set_color_for_new_trace(fitted_trace, application_data)
                self._add_trace_to_data(application_data, fitted_trace_name, fitted_trace, False)

                if include_fit_substracted_trace:
                    fitted_trace_name = "fit_substr_" + str(len(application_data['fitted_models']) + 1) + "_" + trace_name
                    ancestors = trace['ancestors'] + [trace_name]

                    y_grid2 = fitted_model(x)
                    flux = y - y_grid2

                    f_labmda = fl.convert_flux(flux=x, wavelength=y,
                                           from_flux_unit=trace['flux_unit'], to_flux_unit=FluxUnit.F_lambda,
                                           to_wavelength_unit=trace.get('flux_unit'))

                    fitted_trace = Trace(name=fitted_trace_name, wavelength=[x for x in x],
                                         flux=[y for y in flux],
                                         ancestors=ancestors, spectrum_type=SpectrumType.FIT, color="black",
                                         linewidth=1, alpha=1.0,
                                         wavelength_unit=trace['wavelength_unit'], flux_unit=trace['flux_unit'],
                                         flambda=f_labmda, catalog=trace['catalog']).to_dict()

                    self._set_color_for_new_trace(fitted_trace, application_data)
                    self._add_trace_to_data(application_data, fitted_trace_name, fitted_trace, do_update_client=False)


                fitted_info = {}
                fitted_info['name'] = fitted_trace_name
                fitted_info['ancestors'] = ancestors
                fitted_info['model'] = fitting_model_name
                fitted_info['parameters'] = {x:y for (x,y) in zip(fitted_model.param_names, fitted_model.parameters)}
                fitted_info['parameter_errors'] = {x: y for (x, y) in zip(fitted_model.param_names, parameter_errors) } if parameter_errors is not None else None
                fitted_info['selection_indexes'] = ind
                fitted_info['wavelength_unit'] = trace['wavelength_unit']
                fitted_info['flux_unit'] = trace['flux_unit']

                # add to application data:
                fitted_models = application_data['fitted_models']
                fitted_models[fitted_trace_name] = fitted_info
                application_data['fitted_models'] = fitted_models

                application_data['traces'][fitted_trace_name] = fitted_trace
                application_data['fitted_models'][fitted_trace_name] = fitted_info
                self.write_info("fitting model2122 : " + str(application_data['fitted_models'][fitted_trace_name]) )


        if do_update_client:
            self.update_client()


########  Trace manipulation/analysis



    def reset_smoothing(self, trace_name):
        self._unsmooth_trace([trace_name], self.app_data, do_update_client=True)


    def set_smoothing_kernel(self,kernel=SmoothingKernels.GAUSSIAN1D, kernel_width=20, custom_kernel_array=None, custom_kernel_function=None, function_array_size=21):
        self.smoother.set_smoothing_kernel(kernel, kernel_width, custom_kernel_array, custom_kernel_function, function_array_size)


    def smooth_trace(self, trace_name, do_substract=False):
        self._smooth_trace([trace_name], self.app_data, self.smoother, do_update_client=True, do_substract=do_substract)
        #self._smooth_trace([trace_name], self.app_data, do_update_client=True, kernel=kernel, kernel_width=kernel_width, custom_kernel_array=custom_kernel_array, custom_kernel_function=custom_kernel_function, function_array_size=function_array_size, do_substract=do_substract)


    def fit_model(self, trace_name, fitting_model=FittingModels.GAUSSIAN_PLUS_LINEAR, selected_data=None, custom_model=None):
        pass


    def _get_selection(self, selected_data, data_dict):
        selection = {}
        if selected_data != {} and selected_data is not None:
            selection = {key: value for key, value in selected_data.items()}
            # adding trace name to each points:
            curve_mapping = { data_dict['traces'][trace]['curveNumber']:data_dict['traces'][trace]['name'] for trace in data_dict['traces']}

            points = []
            for point in selection['points']:
                point['trace_name'] = curve_mapping[point['curveNumber']]
                points.append(point)
            selection['points'] = points
            return selection

        return selection


    def get_selection(self):
        return self.app_data.get("selection")

    def add_spectrum_from_file(self, file_path, name=None, to_wavelength_unit=WavelenghUnit.ANGSTROM, to_flux_unit=FluxUnit.F_lambda ):
        self._add_spectrum_from_file(file_path, self.app_data, to_wavelength_unit, to_flux_unit, name, do_update_client=True)

    def add_trace(self, trace):
        return self._add_trace_to_data(self.app_data, trace['name'], trace, do_update_client = True)

    def update_trace(self, name, trace):
        self.app_data['traces'][name] = trace
        self.update_client()


    def add_spectrum(self, spectrum):
        trace = spectrum.to_dict()
        return self._add_trace_to_data(self.app_data, spectrum.name, trace, do_update_client=True)


    def remove_trace(self, name, also_remove_children=False):
        self._remove_traces([name], self.app_data, do_update_client=True, also_remove_children=also_remove_children)

    a = """
    def build_trace(self, name, x_coords=[], y_coords=[], ancestors=[], type=None, color="black", linewidth=1,
                    alpha=1.0, x_coords_original=None, y_coords_original=None, wavelength_unit=WavelenghUnit.ANGSTROM,
                    flux_unit=FluxUnit.F_lambda, flambda=None, masks=None, mask_bits=None, catalog=None):

        args = locals()
        args.pop('self') # remove self argument
        spec = Spectrum() # force to match the members of Spectrum class
        spec.from_dict(args)
        return spec.to_dict()
        """


    def resample(self):
        return None
