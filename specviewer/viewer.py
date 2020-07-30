import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from specviewer import app, refresh_time, app_base_directory
from jupyterlab_dash import AppViewer
from plotly.tools import mpl_to_plotly
from matplotlib import pyplot as plt

import SpectrumViewer.specModel as M
import SpectrumViewer.specView as V
from SpectrumViewer import spectral_lines_info
import SpectrumViewer.dataDriver as driver
# from SpectrumViewer.data_models import Medium, Spectrum, SpectrumLineGrid, SpectrumLine
import SpectrumViewer
from collections import OrderedDict
import matplotlib.text
import numpy as np
import matplotlib.transforms as transforms
import copy
from specviewer import controller as c

from specviewer import data_driver
from specviewer import app_layout, callbacks
from datetime import datetime

import json
from textwrap import dedent as d
from jupyterlab_dash import AppViewer
import dash
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import multiprocessing
import base64
import pandas as pd
import io
import json
from astropy.io import fits
import traceback
import dash_table
from pathlib import Path
from astropy.convolution import convolve, Gaussian1DKernel, Box1DKernel, CustomKernel
from astropy.convolution.kernels import Model1DKernel
from astropy.modeling.models import custom_model
from specviewer.data_models import WavelenghUnit, FluxUnit, FittingModels, SmoothingKernels
from astropy.modeling import Fittable1DModel, Parameter
from specviewer.colors import get_next_color
from specviewer.flux import fnu_to_abmag,fnu_to_flambda,flambda_to_fnu,flambda_to_abmag,abmag_to_fnu,abmag_to_flambda
from astropy.modeling import models, fitting


process_manager = multiprocessing.Manager()
jupyter_viewer = AppViewer()
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# create global variable only for use inside jupyter
app_data = process_manager.dict()
debug_data = process_manager.dict()
app_data_timestamp = process_manager.dict()


#https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes
#https://stackoverflow.com/questions/17377426/shared-variable-in-pythons-multiprocessing
#https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Value

class Viewer():
    # app_data = {}

    def __init__(self, as_website=False):
        # global app_data
        # global fig
        self.as_website = as_website
        print("first " + str(self.as_website))
        # just for testing local website
        # self.app_data = {'traces':{}, 'selection':{}} #application_data.ApplicationData()
        # self.app_data = app_data
        self.app_data = app_data
        self.app_data_timestamp = app_data_timestamp
        self.app_data['traces'] = {}
        self.app_data['fitted_models'] = {}
        self.app_data['selection'] = {}
        self.app_data_timestamp['timestamp'] = 0
        self.debug_data = debug_data

        # self.spectral_lines_info = spectral_lines_info
        # self.view = V.SpecView(width, height, dpi)
        # self.view.select_all_button.on_clicked(self.select_all_button_callback)
        # self.view.delete_unchecked_button.on_clicked(self.delete_unchecked_button_callback)
        # self.model = M.SpecModel(streams=OrderedDict(), spectral_lines=OrderedDict())

        self.time2 = str(datetime.now())

        # self.spec_figure = make_subplots(rows=1, cols=1)
        # self.fill_spec_figure_with_app_data()
        #self.spec_figure = self.get_spec_figure_from_data(self.app_data)

        #app.layout = self.load_app_layout
        app.layout = app_layout.load_app_layout(self)
        callbacks.load_callbacks(self)

    def build_app_data(self, traces=None):
        if traces is None:
            return {'traces': {}, 'fitted_models':{}, 'selection':{}}
        else:
            return {'traces': traces, 'fitted_models':{}, 'selection':{}}

    def _parse_uploaded_file(self, contents, file_name, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda, add_sky=False, add_model=False, add_error=False, add_masks=True):

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        hdulist = fits.open(io.BytesIO(decoded))

        if "." in file_name:
            file_name_parts = file_name.split(".")
            file_name = ".".join(file_name_parts[:(len(file_name_parts)-1)])

        return self._load_from_hdu(hdulist, file_name, wavelength_unit=wavelength_unit, flux_unit=flux_unit, add_sky=add_sky, add_model=add_model, add_error=add_error, add_masks=add_masks)

    def _load_from_hdu(self, hdulist, name, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda, add_sky=False, add_model=False, add_error=False, add_masks=True):

        # assumes that spectrum wavelength units are in Armstrong:
        spectrum_list = data_driver.get_spectrum_list_from_fits(hdulist, name, add_sky=add_sky, add_model=add_model, add_error=add_error, add_masks=add_masks)

        rescaled_traces = []
        for spectrum in spectrum_list:
            trace = self.build_trace(name=spectrum.name, x_coords=spectrum.wavelength, y_coords=spectrum.flux, color="black", linewidth=1,
                                     alpha=0.8, wavelength_unit=spectrum.wavelength_unit, flux_unit=spectrum.flux_unit,
                                     flambda=spectrum.flambda, masks=spectrum.masks, mask_bits=spectrum.mask_bits, catalog=spectrum.catalog, ancestors=spectrum.ancestors)
            rescaled_traces.append(self._get_rescaled_axis_in_trace(trace, to_wavelength_unit=wavelength_unit,
                                                                   to_flux_unit=flux_unit))
        return rescaled_traces




    def set_color_for_new_trace(self, trace, application_data):
        current_traces_colors = [application_data['traces'][trace_name]['color'] for trace_name in application_data['traces']]
        new_color = get_next_color(current_traces_colors)
        trace['color'] = new_color

    def update_time(self):
        self.time2 = str(datetime.now())

    def show_jupyter_app(self):
        # self.load_callbacks()
        # app.layout = self.load_app_layout
        # app.layout = self.load_app_layout
        jupyter_viewer.show(app)

    def synch_data(self,base_data_dict,incomplete_data_dict,do_update_client=False):
        #self.write_info("inc0  start " + str(incomplete_data_dict) + " " + str(base_data_dict))
        a = """
        for trace_name in base_data_dict['traces']:
            #self.write_info("inc0  trace  " +  trace_name + " " + str(incomplete_data_dict) + " " + str(base_data_dict))
            # if trace_name not in incomplete_data_dict['traces']:
            self.add_trace_to_data(incomplete_data_dict, trace_name, base_data_dict['traces'][trace_name], do_update_client=do_update_client)
            #self.write_info("inc0 "+ trace_name + str(incomplete_data_dict) )
        #self.write_info("inc0  end")
        """
        incomplete_data_dict['traces'] = base_data_dict['traces']
        if do_update_client:
            self.update_client()




    def _add_trace_to_data(self, application_data, name, trace, do_update_client = True):
        traces = application_data['traces']
        #num_repeats = [name for name in traces].count(name)

        if name in traces:
            raise Exception("Trace named '" + name + "' already exists.")

        traces[name] = trace
        application_data['traces'] = traces

        if do_update_client:
            self.update_client()

        # self.app_data['traces'][name] = trace
        # if update_figure:
        #    self.fill_spec_figure_with_app_data(self.spec_figure)
        #    self.load_spec_figure(self.spec_figure)

    def add_trace(self, name, trace):
        print("Adding trace")
        return self._add_trace_to_data(self.app_data, name, trace, do_update_client = True)

    def update_trace(self, name, trace):
        self.app_data['traces'][name] = trace
        self.update_client()


    def add_spectrum(self, spectrum):
        trace = self.build_trace(name=spectrum.name, x_coords=spectrum.wavelength, y_coords=spectrum.flux,
                                 color=spectrum.color, linewidth=spectrum.color,alpha=spectrum.alpha,
                                 wavelength_unit=spectrum.wavelength_unit, flux_unit=spectrum.flux_unit,
                                 flambda=spectrum.flambda, masks=spectrum.masks, mask_bits=spectrum.mask_bits,
                                 catalog=spectrum.catalog)

        return self._add_trace_to_data(self.app_data, spectrum.name, trace, do_update_client=True)

    def add_spectrum_from_file(self, file_path, name=None, add_sky=False, add_model=False, add_error=False, add_masks=False):
        hdulist = fits.open(file_path)
        if name is None:
            file_path_parts = file_path.split("/")
            name_parts = file_path_parts[-1].split(".")
            name = ".".join(name_parts[:(len(name_parts) - 1)])

        rescaled_traces = self._load_from_hdu(hdulist, name, wavelength_unit=WavelenghUnit.ANGSTROM, flux_unit=FluxUnit.F_lambda,
                                                add_sky=add_sky, add_model=add_model, add_error=add_error, add_masks=add_masks)
        for trace in rescaled_traces:
            self.set_color_for_new_trace(trace, self.app_data)
            self._add_trace_to_data(self.app_data, trace.get('name'), trace, do_update_client=True)

    def _remove_traces(self, trace_names, data, do_update_client=True, also_remove_children=False):

        _traces_to_remove = [name for name in trace_names]
        if also_remove_children:
            for name in data['traces']:
                for ancestor in data['traces'][name]['ancestors']:
                    if ancestor in _traces_to_remove:
                        if name not in _traces_to_remove:
                            _traces_to_remove.append(name)

        traces = data['traces']
        for trace_name in _traces_to_remove:
            traces.pop(trace_name)
        data['traces'] = traces

        fitted_models = data['fitted_models']
        fitted_models_names = [model for model in data['fitted_models']]
        for model in fitted_models_names:
            for trace_name in _traces_to_remove:
                if trace_name == model:
                    fitted_models.pop(model)
        data['fitted_models'] = fitted_models

        if do_update_client:
            self.update_client()

    def remove_trace(self, name, also_remove_children=False):
        self._remove_traces([name], self.app_data, do_update_client=True, also_remove_children=also_remove_children)

    def build_trace(self, name, x_coords=[], y_coords=[], ancestors=[], type=None, color="black", linewidth=1,
                    alpha=1.0, x_coords_original=None, y_coords_original=None, wavelength_unit=WavelenghUnit.ANGSTROM,
                    flux_unit=FluxUnit.F_lambda, flambda=None, masks=None, mask_bits=None, catalog=None):
        return {'name': name, 'x_coords': x_coords, 'y_coords': y_coords, 'type': type, 'ancestors':ancestors,
                'visible': True, 'color': color, 'linewidth': linewidth, 'alpha': alpha,
                'x_coords_original': x_coords_original, 'y_coords_original': y_coords_original,
                'wavelength_unit':wavelength_unit, "flux_unit":flux_unit, "flambda":flambda, 'masks':masks,
                'mask_bits':mask_bits, "catalog":catalog}

    def parse_contents(self, contents, filename, date):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),

            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),

            html.Hr(),  # horizontal line

            # For debugging, display the raw contents provided by the web browser
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])

    def write_info(self, info, file_endding=''):
        if file_endding != '':
            file_endding = '_' + file_endding
        with open(app_base_directory +  'info' + file_endding +'.txt', 'a+') as f:
            f.write(str(datetime.now()) + " " + info + "\n")


    def set_app_data_timestamp(self, timestamp=None):
        if timestamp is not None:
            self.app_data_timestamp['timestamp'] = timestamp # in sceconds
        else:
            self.app_data_timestamp['timestamp'] = datetime.timestamp(datetime.now())  # in sceconds
        self.write_info("Updated timestamp to " + str(app_data_timestamp['timestamp']) )

    def update_client(self, timestamp=None):
        self.set_app_data_timestamp(timestamp)

        #Path('./assets/touch.txt').touch()


    def get_data_dict(self, data):
        #return json.loads(data) if data is not None else self.build_app_data()
        return data if data is not None else self.build_app_data()


########  Trace manipulation/analysis


    def _unsmooth_trace(self, trace_names, application_data, do_update_client=True):
        for trace_name in trace_names:
            traces = application_data['traces']
            trace = traces[trace_name]
            if trace['y_coords_original'] is not None and len(trace['y_coords_original'])>0:
                trace['y_coords'] = trace.get('y_coords_original')
                trace['y_coords_original'] = None
                traces[trace_name] = trace
                application_data['traces'] = traces

        if do_update_client:
            self.update_client()

    def unsmooth_trace(self, trace_name):
        self._unsmooth_trace([trace_name], self.app_data, do_update_client=True)


    def _smooth_trace(self, trace_names, application_data, do_update_client=True, kernel=SmoothingKernels.GAUSSIAN1D, kernel_width=21, custom_kernel_array=None, custom_kernel_function=None, function_array_size=21, do_substract=False):
        # https://specutils.readthedocs.io/en/stable/manipulation.html
        # https://docs.astropy.org/en/stable/convolution/kernels.html

        # https://docs.astropy.org/en/stable/convolution/kernels.html
        # https://het.as.utexas.edu/HET/Software/Astropy-0.4.2/convolution/kernels.html
        # http://learn.astropy.org/rst-tutorials/User-Defined-Model.html
        # https://keflavich-astropy.readthedocs.io/en/latest/modeling/new.html
        # https://docs.astropy.org/en/stable/modeling/reference_api.html#module-astropy.modeling


        for trace_name in trace_names:
            if trace_name in application_data['traces']:
                traces = application_data['traces']
                trace = traces[trace_name]

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


                if trace['y_coords_original'] is None or len(trace['y_coords_original']) == 0: # has not been smoothed yet
                    smoothed_trace = convolve(trace['y_coords'], kernel_func)
                    if do_substract:
                        smoothed_trace = trace['y_coords'] - smoothed_trace
                    trace['y_coords_original'] = trace['y_coords']
                else: # has been smoothed already; use original trace values
                    smoothed_trace = convolve(trace['y_coords_original'], kernel_func)
                    if do_substract:
                        smoothed_trace = trace['y_coords_original'] - smoothed_trace

                trace['y_coords'] = smoothed_trace

                #remove old trace and replace it with new trace containing smoothed data
                #traces.pop(trace_name)
                traces[trace_name] = trace
                application_data['traces'] = traces

        if do_update_client:
            self.update_client()

    def smooth_trace(self, trace_name, kernel=SmoothingKernels.GAUSSIAN1D, kernel_width=20, custom_kernel_array=None, custom_kernel_function=None, function_array_size=21, do_substract=False):
        self._smooth_trace([trace_name], self.app_data, do_update_client=True, kernel=kernel, kernel_width=kernel_width, custom_kernel_array=custom_kernel_array, custom_kernel_function=custom_kernel_function, function_array_size=function_array_size, do_substract=do_substract)

    def _rescale_axis(self, application_data, to_wavelength_unit=WavelenghUnit.ANGSTROM, to_flux_unit=FluxUnit.F_lambda, do_update_client=False):
        for trace_name in application_data['traces']:
           rescaled_trace = self._get_rescaled_axis_in_trace(application_data['traces'][trace_name], to_wavelength_unit=to_wavelength_unit, to_flux_unit=to_flux_unit)
           application_data['traces'][trace_name] = rescaled_trace
        if do_update_client:
            self.update_client()

    def _get_rescaled_axis_in_trace(self, trace, to_wavelength_unit=WavelenghUnit.ANGSTROM, to_flux_unit=FluxUnit.F_lambda):
        # for wavelength axis:
        if trace.get('wavelength_unit') != to_wavelength_unit and to_wavelength_unit is not None:
            if trace.get('wavelength_unit') == WavelenghUnit.ANGSTROM and to_wavelength_unit == WavelenghUnit.NANOMETER:
                trace['x_coords'] = [x/10.0 for x in trace['x_coords']]
            elif trace.get('wavelength_unit') == WavelenghUnit.NANOMETER and to_wavelength_unit == WavelenghUnit.ANGSTROM:
                trace['x_coords'] = [x*10.0 for x in trace['x_coords']]
            else:
                raise Exception("Unsupported unit " + str(to_wavelength_unit) + " . Parameter to_wavelength_unit takes values from class WavelenghUnit.")
        trace['wavelength_unit'] = to_wavelength_unit

        #https://en.wikipedia.org/wiki/AB_magnitude
        if trace.get('flux_unit') != to_flux_unit and to_flux_unit is not None:
            if trace.get('flux_unit') == FluxUnit.F_lambda and to_flux_unit == FluxUnit.F_nu:
                trace['y_coords'] = [ flambda_to_fnu(flam,trace['x_coords'][i], to_wavelength_unit) for (i,flam) in enumerate(trace['y_coords'])]
            elif trace.get('flux_unit') == FluxUnit.F_lambda and to_flux_unit == FluxUnit.AB_magnitude:
                trace['y_coords'] = [ flambda_to_abmag(flam,trace['x_coords'][i], to_wavelength_unit) for (i,flam) in enumerate(trace['y_coords'])]
            elif trace.get('flux_unit') == FluxUnit.F_nu and to_flux_unit == FluxUnit.F_lambda:
                trace['y_coords'] = [ fnu_to_flambda(fnu,trace['x_coords'][i], to_wavelength_unit) for (i,fnu) in enumerate(trace['y_coords'])]
            elif trace.get('flux_unit') == FluxUnit.F_nu and to_flux_unit == FluxUnit.AB_magnitude:
                trace['y_coords'] = [ fnu_to_abmag(fnu) for fnu in trace['y_coords']]
            elif trace.get('flux_unit') == FluxUnit.AB_magnitude and to_flux_unit == FluxUnit.F_lambda:
                if trace.get("flambda") is not None:
                    trace['y_coords'] = [f for f in trace['flambda']]
                else:
                    trace['y_coords'] = [ abmag_to_flambda(abmag,trace['x_coords'][i], to_wavelength_unit) for (i,abmag) in enumerate(trace['y_coords'])]
            elif trace.get('flux_unit') == FluxUnit.AB_magnitude and to_flux_unit == FluxUnit.F_nu:
                if trace.get("flambda") is not None:
                    trace['y_coords'] = [ flambda_to_fnu(flam,trace['x_coords'][i], to_wavelength_unit) for (i,flam) in enumerate(trace['flambda'])]
                else:
                    trace['y_coords'] = [ abmag_to_fnu(abmag) for abmag in trace['y_coords']]
            else:
                raise Exception("Unsupported unit " + str(to_flux_unit) + " . Parameter to_flux_unit takes values from class FluxUnit.")

        trace['flux_unit'] = to_flux_unit
        return trace


    def _fit_model_to_flux(self, trace_names, application_data, fitting_models, selected_data, custom_model=None, custom_fitter=None, do_update_client=True):
        #http://learn.astropy.org/rst-tutorials/User-Defined-Model.html

        x_range = selected_data.get('range').get('x')
        y_range = selected_data.get('range').get('y')

        for fitting_model in fitting_models:
            for trace_name in trace_names:
                #ind = trace_indexes[trace_name]
                trace = application_data['traces'].get(trace_name)
                x_array = np.asarray(trace['x_coords'])
                y_array = np.asarray(trace['y_coords'])
                ind = (x_array >= x_range[0]) & (x_array <= x_range[1]) & \
                      (y_array >= y_range[0]) & (y_array <= y_range[1])
                x = x_array[ind]
                y = y_array[ind]

                if custom_model is None and custom_fitter is None:

                    location_param = np.mean(x)
                    amplitude_param = np.max(np.abs(y))
                    spread_param = (x_range[1] - x_range[0]) / len(x)

                    if fitting_model == FittingModels.GAUSSIAN_PLUS_LINEAR:
                        data_model = models.Gaussian1D(amplitude=amplitude_param, mean=location_param, stddev=spread_param) + models.Polynomial1D(degree=1)
                    elif fitting_model == FittingModels.LORENTZIAN_PLUS_LINEAR:
                        data_model = models.Lorentz1D(amplitude=amplitude_param, x_0=location_param, fwhm=spread_param) + models.Polynomial1D(degree=1)
                    elif fitting_model == FittingModels.VOIGT_PLUS_LINEAR:
                        data_model = models.Voigt1D(x_0=location_param, amplitude_L=amplitude_param, fwhm_L=spread_param, fwhm_G=spread_param) + models.Polynomial1D(degree=1)
                    else:
                        raise Exception("Unsupported fitting model " + str(fitting_model))

                    fitting_model_name = fitting_model
                else:
                    data_model = custom_model
                    fitting_model_name = str(custom_model)

                fitter = fitting.LevMarLSQFitter()
                fitted_model = fitter(data_model, x, y)
                x_grid = np.linspace(x_range[0], x_range[1], 5*len(x))
                y_grid = fitted_model(x_grid)

                fitted_trace_name = "fit" + str(len(application_data['fitted_models']) + 1) + "_" + trace_name

                ancestors = trace['ancestors'] + [trace_name]


                flambda = [f for f in np.asarray(trace['flambda'])[ind]] if trace['flambda'] is not None else None
                x_coords_original = [f for f in np.asarray(trace['x_coords_original'])[ind]] if trace['x_coords_original'] is not None else None
                y_coords_original = [f for f in np.asarray(trace['y_coords_original'])[ind]] if trace['y_coords_original'] is not None else None

                fitted_trace = self.build_trace(name=fitted_trace_name, x_coords=[x for x in x_grid], y_coords=[y for y in y_grid],
                                                ancestors=ancestors,type=trace['type'], color=None, linewidth=1, alpha=1.0,
                                                x_coords_original=x_coords_original, y_coords_original=y_coords_original,
                                                wavelength_unit=trace['wavelength_unit'], flux_unit=trace['flux_unit'],
                                                flambda=flambda, masks=None, mask_bits=None, catalog=None)

                self.set_color_for_new_trace(fitted_trace, application_data)
                # add to application data:
                traces = application_data['traces']
                traces[fitted_trace_name] = fitted_trace
                application_data['traces'] = traces

                fitted_info = {}
                fitted_info['name'] = fitted_trace_name
                fitted_info['ancestors'] = ancestors
                fitted_info['model'] = fitting_model_name
                fitted_info['parameters'] = {x:y for (x,y) in zip(fitted_model.param_names, fitted_model.parameters)}
                fitted_info['selection_range'] = {'x_range':x_range, 'y_range':y_range}
                fitted_info['wavelength_unit'] = trace['wavelength_unit']
                fitted_info['flux_unit'] = trace['flux_unit']

                # add to application data:
                fitted_models = application_data['fitted_models']
                fitted_models[fitted_trace_name] = fitted_info
                application_data['fitted_models'] = fitted_models

                application_data['traces'][fitted_trace_name] = fitted_trace
                application_data['fitted_models'][fitted_trace_name] = fitted_info


        if do_update_client:
            self.update_client()


    def fit_model(self, trace_name, fitting_model=FittingModels.GAUSSIAN_PLUS_LINEAR, selected_data=None, custom_model=None):
        pass


    def get_selection(self):
        pass

    def resample(self):
        return None
