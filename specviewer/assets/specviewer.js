//alert("dedW")
//sessionStorage.clear()

var spectral_lines = null
var nclick_show_error_button = 0
var do_show_error = false
window.PlotlyConfig = {MathJaxConfig: 'local'}


//var socket =  io.connect('http://localhost:8050/');
/*
var socket =  io()
socket.on("update", function(data) {
    alert("from websocket")
    console.log("from websocket")
    update_clientside_app_data(data)
})
*/

$(document).ready(function(){
    var socket = io.connect();
    socket.on('update', function(msg) {
        //alert("from socket")
        update_clientside_app_data()
    });
});



function update_clientside_app_data(data){
    randval = uuidv4()
    update_component_porperty("pull_trigger", {value: randval})
}

function update_component_porperty(id, property){
    //sessionStorage.setItem("store",data)
    var element = document.getElementById(id);
    var key = Object.keys(element).find(key=>key.startsWith("__reactInternalInstance$"));
    var internalInstance = element[key];
    var setProps = internalInstance.return.memoizedProps.setProps;
    setProps(property)
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        set_dropdown_options: function(modified_timestamp, data) {
            options = []
            if(data != null){
                trace_names = Object.keys(data.traces)
                for(i=0; i<trace_names.length; i++){
                    trace_name = trace_names[i]
                    if(data.traces[trace_name].is_visible){
                        options.push({label: trace_name, value: trace_name})
                    }
                }
            }
            return options
        },

        set_smoothing_kernels_dropdown: function(modified_timestamp, data){
            options = []
            if(data != null){
                smoothing_kernels = data['smoothing_kernels']
                for(i=0; i<smoothing_kernels.length; i++){
                    kernel_name = smoothing_kernels[i]
                    options.push({label: kernel_name, value: kernel_name})
                }
            }
            return options
        },

        set_fitted_models_table: function(modified_timestamp, data) {
            if(data != null){
                var tab = "<table id='fitted_models_table'><tbody>"
                for(fitted_model_name in data['fitted_models']){
                    fitted_model = data['fitted_models'][fitted_model_name]
                    // create header:
                    tab += "<tr><th><u>" + fitted_model.name + "</u></th></tr>"
                    //add properties:
                    tab += "<tr><td>model:</td><td>" + fitted_model.model + "</td></tr>"
                    for(parameter_name in fitted_model['parameters']){
                        parameter_value = (fitted_model['parameters'][parameter_name]).toExponential(7)
                        tab += "<tr><td>" +  parameter_name + "</td><td>" + parameter_value + "</td></tr>"
                        if( fitted_model['parameter_errors'] != null){
                            parameter_error = (fitted_model['parameter_errors'][parameter_name]).toExponential(7)
                            tab += "<tr><td> 	&plusmn;  </td><td>" + parameter_error + "</td></tr>"
                        }


                    }
                    if(fitted_model['selection_range'] != null){
                        //tab += "<tr><td>  x_range  </td><td>[" + fitted_model['selection_range']['x_range'][0] +  ", " + fitted_model['selection_range']['x_range'][1]  + "]</td></tr>"
                        //tab += "<tr><td>  y_range  </td><td>[" + fitted_model['selection_range']['y_range'][0] +  ", " + fitted_model['selection_range']['y_range'][1]  + "]</td></tr>"
                    }
                    tab += "<tr><td>Wavelength unit:</td><td>" + fitted_model['wavelength_unit'] + "</td></tr>"
                    tab += "<tr><td>Flux unit:</td><td>" + fitted_model['flux_unit'] + "</td></tr>"

                }
                tab += "</tbody></table>"
                return tab
            }
        },

        select_all_traces_in_dropdown : function(select_all_traces_button_clicks, data, traces_dropdown) {
            options = []
            if(data != null){
                trace_names = Object.keys(data.traces)
                if(traces_dropdown.length != trace_names.length){
                    for(i=0; i<trace_names.length; i++){
                        trace_name = trace_names[i]
                        options.push(trace_name)
                    }
                }
            }
            return options
        },

        set_masks_dropdown: function(modified_timestamp, data){

            mask_dropdown_options = []

            catalogs_list = []
            options_ids = {}
            if(data != null && data['traces'] != null){

                for( trace_name in data['traces']){
                    //adding "all" entry:
                    catalog = data['traces'][trace_name].catalog
                    label_all = trace_name + " ALL MASKS"
                    options_for_all_entry = []
                    options_ids = {} // stores the IDs of all masks already added to the mask_dropdown_options, so that there are no duplicates
                    if( data['traces'][trace_name]['masks'] != null && data['traces'][trace_name]['masks']['and_mask_values'] != null){
                        for(mask_id in data['traces'][trace_name]['masks']['and_mask_values']){
                            label_value = mask_id
                            bit = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].bit
                            catalog = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].catalog
                            name = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].name
                            options_for_all_entry.push({label:label_value, value:{id:label_value, trace:trace_name, bit:bit, catalog:catalog, name:name, is_all:false}})
                        }
                        if(options_ids[label_all] == null){
                            val = JSON.stringify({id:label_all, trace:trace_name, bit:null, catalog:catalog, is_all:true, options_for_all_entry:options_for_all_entry})
                            mask_option = {label:label_all, value:val}
                            mask_dropdown_options.push(mask_option)
                            options_ids[label_all] = mask_option
                        }

                        //adding single mask entries
                        for(mask_id in data['traces'][trace_name]['masks']['and_mask_values']){
                            label_value = mask_id
                            bit = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].bit
                            catalog = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].catalog
                            name = data['traces'][trace_name]['masks']['and_mask_values'][mask_id].name

                            if(options_ids[label_value] == null){
                                mask_option = {label:label_value, value:JSON.stringify({id:mask_id, trace:trace_name, bit:bit, catalog:catalog, name:name, is_all:false})}
                                mask_dropdown_options.push(mask_option)
                                options_ids[label_value] = mask_option
                            }
                        }
                    }

                }
            }
            return mask_dropdown_options
        },

        set_figure: function(modified_timestamp, spectral_lines_switch, redshift, spectral_lines_dropdown, and_mask_switch, mask_dropdown, show_error_button_nclicks, data, spectral_lines_dict, trace_dropdown) {

            if(show_error_button_nclicks > nclick_show_error_button){
                nclick_show_error_button = show_error_button_nclicks
                if(do_show_error == true)
                    do_show_error=false
                else
                    do_show_error=true
            }

            figure_data = build_figure_data(data, spectral_lines_switch, redshift, spectral_lines_dropdown, spectral_lines_dict, trace_dropdown, do_show_error)
            //x_range = get_x_range(data)
            figure_layout = build_figure_layout(data, spectral_lines_switch=spectral_lines_switch, redshift, spectral_lines_dropdown, spectral_lines_dict, and_mask_switch, mask_dropdown, trace_dropdown)
            //console.log(JSON.stringify(figure_layout.xaxis))
            return {data:figure_data, layout:figure_layout}
        }
    }
});

function get_data_ranges(data){
    var x_min=0.0
    var x_max=1.0
    var y_min=0.0
    var y_max=1.0
    if(data == null || data.traces == null){
        return {x_range:[x_min,x_max], y_range:[y_min,y_max]}
    }
    trace_names = Object.keys(data.traces)
    if(trace_names.length == 0){
        return {x_range:[x_min,x_max], y_range:[y_min,y_max]}
    }else{
        x_min = Number.MAX_VALUE
        x_max = Number.MIN_VALUE
        y_min = Number.MAX_VALUE
        y_max = Number.MIN_VALUE
        for(i=0; i<trace_names.length; i++){
            trace_name = trace_names[i]
            x_min = Math.min(x_min, Math.min.apply(Math, data.traces[trace_name].wavelength))
            x_max = Math.max(x_max, Math.max.apply(Math, data.traces[trace_name].wavelength))
            y_min = Math.min(y_min, Math.min.apply(Math, data.traces[trace_name].flux))
            y_max = Math.max(y_max, Math.max.apply(Math, data.traces[trace_name].flux))
        }
        return {x_range:[x_min,x_max], y_range:[y_min,y_max]}
    }
}

function get_flux_unit(data){
    return "Flux"
}

function get_x_axis_label(data){

    label = "\\text{Wavelength}"
    unit = get_wavelength_unit(data)
    if(unit != ""){
        label = label + "\\quad [ \\text{" + unit + "} ]"
    }
    return "$" + label + "$"
}

function get_y_axis_label(data){
    unit = get_flux_unit(data)
    if(unit != ""){
        if(unit == "F_lambda"){
            label = "$\\text{F}_{\\lambda} \\quad [\\text{erg/s/cm}^2/\\text{A}]$"
        }else if(unit == "F_nu"){
            label = "$\\text{F}_{\\nu} \\quad [\\text{erg/s/cm}^2/\\text{Hz}]$"
        }else if(unit == "AB_magnitude"){
            label = "$\\text{F}_{\\text{AB}} \\quad [\\text{magnitude}]$"
        }else{
            label = "Flux"
        }
    }else{
        label = "Flux"
    }
    return label
}



function get_wavelength_unit(data){

    if(data == null){
        return ""
    }
    trace_names = Object.keys(data.traces)
    if(trace_names.length == 0){
        return ""
    }else{
        // getting unit from first trace, assumes all traces have same units
        trace_name = trace_names[0]
        if(data.traces[trace_name].wavelength_unit == null){
            return ""
        }else{
            unit = data.traces[trace_name].wavelength_unit
            return unit
        }
    }
}

function get_flux_unit(data){

    if(data == null){
        return ""
    }
    trace_names = Object.keys(data.traces)
    if(trace_names.length == 0){
        return ""
    }else{
        // getting unit from first trace, assumes all traces have same units
        trace_name = trace_names[0]
        if(data.traces[trace_name].flux_unit == null){
            return ""
        }else{
            unit = data.traces[trace_name].flux_unit
            return unit
        }
    }
}





function build_figure_data(data, spectral_lines_switch, redshift, spectral_lines_dropdown, spectral_lines_dict, trace_dropdown_names, do_show_error){

    traces = []

    wavelength_unit = get_wavelength_unit(data)
    //ranges = get_data_ranges(data)

    if(data != null){
        trace_names = Object.keys(data.traces)
        for(i=0; i<trace_names.length; i++){
            trace_name = trace_names[i]

            var add_error_bounds = do_show_error & trace_dropdown_names.includes(trace_name) & data.traces[trace_name].flux_error != null & data.traces[trace_name].flux_error.length>0
            var fill_color = add_alpha_to_rgb(data.traces[trace_name].color,0.2)

            if(add_error_bounds){
                var flux_lower_bound = []
                for(j=0;j<data.traces[trace_name].flux.length;j++){

                    if(data.traces[trace_name].flux_unit == "AB_magnitude"){
                        f = data.traces[trace_name].flambda[j] + data.traces[trace_name].flambda_error[j]
                        w = data.traces[trace_name].wavelength[j]
                        w_u = data.traces[trace_name].wavelength_unit
                        //ab = data.traces[trace_name].flux[j]
                        ab_bound = flambda_to_abmag(f,w,w_u)
                        flux_lower_bound.push(ab_bound)
                    }else{
                        flux_lower_bound.push(data.traces[trace_name].flux[j] - data.traces[trace_name].flux_error[j])
                    }
                }

                lower_error_trace = {   name:trace_name + "_lower_error_bound",
                                        x: data.traces[trace_name].wavelength,
                                        y: flux_lower_bound,
                                        mode: "lines",
                                        type: 'scattergl',
                                        xaxis: "x",
                                        yaxis: "y",
                                        line:{color:data.traces[trace_name].color, width:1.0},
                                        showlegend : false,
                                        hoverinfo:"x+y",
                                        opacity:0.3,
                                        fill: "tonexty", fillcolor: fill_color,
                                    }
                traces.push(lower_error_trace)
            }

            trace = {   name:trace_name,
                        x: data.traces[trace_name].wavelength,
                        y: data.traces[trace_name].flux,
                        mode: "markers+lines",
                        //type: 'scatter',
                        type: 'scattergl',
                        visible: data.traces[trace_name].is_visible,
                        color: data.traces[trace_name].color,
                        xaxis: "x",
                        yaxis: "y",
                        marker:{size: 1.4, color:data.traces[trace_name].color },
                        line:{ color:data.traces[trace_name].color, width:1.4 }
            }
            if(add_error_bounds){
                //trace['fill'] = "tonexty";trace['fillcolor'] = add_alpha_to_rgb(data.traces[trace_name].color,0.2)
            }

            if(add_error_bounds){
                var flux_upper_bound = []
                for(j=0;j<data.traces[trace_name].flux.length;j++){
                    if(data.traces[trace_name].flux_unit == "AB_magnitude"){
                        f = data.traces[trace_name].flambda[j] - data.traces[trace_name].flambda_error[j]
                        w = data.traces[trace_name].wavelength[j]
                        w_u = data.traces[trace_name].wavelength_unit
                        //ab = data.traces[trace_name].flux[j]
                        ab_bound = flambda_to_abmag(f,w,w_u)
                        flux_upper_bound.push(ab_bound)
                    }else{
                        flux_upper_bound.push(data.traces[trace_name].flux[j] + data.traces[trace_name].flux_error[j])
                    }

                }

                upper_error_trace = {   name:trace_name + "_upper_error_bound",
                                        x: data.traces[trace_name].wavelength,
                                        y: flux_upper_bound,
                                        mode: "lines",
                                        type: 'scattergl',
                                        xaxis: "x",
                                        yaxis: "y",
                                        line:{color:data.traces[trace_name].color, width:1.0},
                                        showlegend : false,
                                        hoverinfo:"x+y",
                                        fill: "tonexty", fillcolor: fill_color,
                                        opacity:0.3
                }
                traces.push(upper_error_trace)
            }


            traces.push(trace)


        }
    }
    return traces
}


function build_figure_layout(data, spectral_lines_switch=false, redshift=0.0, spectral_lines_dropdown = [], spectral_lines_dict = [], and_mask_switch=false, mask_dropdown = [], trace_dropdown = []){

    if(spectral_lines == null){
        spectral_lines = JSON.parse(spectral_lines_dict)
    }

    x_axis_label = get_x_axis_label(data)
    y_axis_label = get_y_axis_label(data)
    wavelength_unit = get_wavelength_unit(data)
    flux_unit = get_flux_unit(data)
    ranges = get_data_ranges(data)

    var annotations = []
    var shapes = [] // https://plotly.com/python/reference/#layout-shapes

    // adding spectral lines
    if(spectral_lines_switch == true){

        spec_lines = []
        if(spectral_lines_dropdown.includes('all')){
            for(line in spectral_lines){
                spec_lines.push(spectral_lines[line])
            }
        }else{
            for(i=0;i<spectral_lines_dropdown.length;i++){
                line_name = spectral_lines_dropdown[i]
                if(line_name in spectral_lines){
                    spec_lines.push(spectral_lines[line_name])
                }
            }
        }

        for(i=0; i < spec_lines.length;i++){
            line = spec_lines[i]
            if(line.name.toLowerCase() != "sky"){
                x0 = (1.0+redshift)*line.lambda
            }else{
                x0 = line.lambda
            }
            line_label = line.name
            line_label = line.label
            if(wavelength_unit == "nanometer")
                x0 = x0/10.0
            x1=x0
            // need to include only lines within the range of data since otherwise the plotted are will be too big compared to the spectra.
            if(x0 >= ranges.x_range[0] && x0 <= ranges.x_range[1]){


                if(i % 3 == 0){
                    y_line_annotation = 1.0
                }else if(i % 3 == 1){
                    y_line_annotation = 1.02
                }else{
                    y_line_annotation = 1.04
                }

                //y0 = ranges.y_range[0] + 0.1*(ranges.y_range[1]-ranges.y_range[0])
                //y1 = ranges.y_range[1] - 0.1*(ranges.y_range[1]-ranges.y_range[0])
                y0=0
                y1=1

                line = {type: 'line', name:line_label,  layer:'above', xref:'x', yref: 'paper', y0: y0, y1: y1, x0: x0, x1: x1, line:{ width:0.5, color:"grey"}, opacity:0.5 }
                shapes.push(line)

                annotation = {showarrow: false, text: line_label, align: "center",x: x0, xanchor: "center", y: y_line_annotation, yanchor: "bottom", yref:"paper", font:{size:10, family:"Arial",color:"grey"}, opacity:1}
                annotations.push(annotation)
            }
        }
    }

    // adding masks

    if(and_mask_switch == true){
        //var selected_masks = []
        var selected_masks = {}
        for(i=0;i<mask_dropdown.length;i++){
            mask = JSON.parse(mask_dropdown[i])
            //selected_masks.push({'id':mask.id, 'catalog':mask.catalog,'bit':parseInt(mask.bit)})

            if(mask.is_all == true){
                options_for_all_entry = mask.options_for_all_entry
                for(j=0;j<options_for_all_entry.length;j++){
                    option_for_all_entry = options_for_all_entry[j]
                    selected_masks[option_for_all_entry.label] = option_for_all_entry
                }
            }else{
                if(selected_masks[mask.id] == null){
                    selected_masks[mask.id] = {label:mask.id, value:{id:mask.id, trace:mask.trace, name:mask.name, catalog:mask.catalog, bit:parseInt(mask.bit)}}
                }
            }
        }

        // plot masks for each trace:
        for(trace_name in data['traces']){

            selected_bit_list = []
            selected_masks_in_trace = []
            for(mask in selected_masks){
                if(selected_masks[mask].value.trace == trace_name){
                    selected_masks_in_trace.push(selected_masks[mask].value)
                }
            }

            if(selected_masks_in_trace.length > 0){


                mask_color = data['traces'][trace_name].color
                //mask_color = "rgb(211,211,211)"
                trace_catalog = data['traces'][trace_name]['catalog']
                and_mask = data['traces'][trace_name]['masks']['and_mask']
                wavelength_array = data['traces'][trace_name]['wavelength']

                for(mask_bit in and_mask){
                    mask_bit2 = parseInt(mask_bit)

                    bits_in_this_region = []
                    rect_label = ""
                    for(k=0;k<selected_masks_in_trace.length;k++){
                        selected_bit = parseInt(selected_masks_in_trace[k].bit)
                        if( (mask_bit2 & 2**selected_bit) != 0){
                            bits_in_this_region.push(selected_bit)
                            //rect_label = rect_label + " " + String(selected_masks_in_trace[k].id)
                            short_trace_name = String(selected_masks_in_trace[k].trace)
                            max_name_length = 10
                            halfname_length = 5
                            if(short_trace_name.length > max_name_length){
                                short_trace_name = short_trace_name.substring(0,halfname_length) + "..." + short_trace_name.substring(short_trace_name.length-halfname_length,short_trace_name.length)
                            }
                            rect_label = rect_label + short_trace_name + "<br>" + String(selected_masks_in_trace[k].name) + "<br>"
                        }
                    }
                    if(bits_in_this_region.length > 0){
                        // add masked region
                        wavelength_indices = and_mask[mask_bit]
                        for(j=0;j<wavelength_indices.length;j++){
                            indices = wavelength_indices[j]
                            x0 = wavelength_array[indices[0]]
                            x1 = wavelength_array[indices[1]]
                            y0 = 0.0
                            y1 = 1.0
                            if(x0 >= ranges.x_range[0] && x0 <= ranges.x_range[1]){
                                rectangle =  {type: 'rect', name:rect_label,  layer:'below', xref:'x', yref: 'paper', y0: y0, y1: y1, x0: x0, x1: x1, line:{ width:1.0, color:mask_color, opacity:0.2}, opacity:0.2, fillcolor:mask_color}
                                shapes.push(rectangle)
                                annotation = {showarrow: false, text: rect_label, align: "center", x: (x0+x1)/2.0, xref:'x', xanchor: "center", y: y0, yanchor: "bottom", yref:"paper", font:{size:11, family:"Arial",color:"black"}, opacity:0.4}
                                annotations.push(annotation)
                            }
                        }

                    }
                }
            }

        }

    }

    // https://plotly.com/javascript/reference/layout/#layout-legend
    var legend = {
        font: { size:10, color:"black", family:"Courier New, monospace"},
        x:0.90,
        y:1.2,
    }

    var layout = {
        showlegend: true,
        dragmode: "pan",
        hovermode: "x",
        //hovermode:'closest',
        //hoverlabel: {bgcolor:"white",font_size:100,font_family:"Rockwell",width:500},
        hoverlabel: {bgcolor:"white", bordercolor: "black", align: "left", font:{font_family:"Rockwell", size:20, color:"black"}},
        //hoverdistance: 100,
        //transition : {'duration': 500},
        //margin:{"l": 0, "r": 0, "t": 0, "b": 0},
        //xaxis:{showgrid:false, showline:false, zeroline:false},
        //yaxis:{showgrid:false, showline:false, zeroline:false},
        //width: map_width,
        //height: map_height,
        //title:{text: "SpecViewer", y: 0.9, x: 0.5, xanchor: 'center', yanchor: 'top'},
        //title: {font: {size: 30}, text: "SpecViewer", y: 0.9, x: 0.5, xanchor: "center", yanchor: "top"},
        font: {family: "Courier New, monospace", size: 18, color: "#7f7f7f"},
        xaxis: {anchor: "y", title: {text: x_axis_label}, showgrid:false, automargin: true,},
        yaxis: {anchor: "x", title: y_axis_label, showgrid:false, showexponent: 'last', exponentformat: 'power', automargin: true,},
        //xaxis_title:x_axis_label, yaxis_title:y_axis_label,
        font:{family:"Courier New, monospace", size:12, color:"black"},
        plot_bgcolor:'rgb(255,255,255)',
        clickmode:'event+select',
        shapes: shapes,
        annotations: annotations,
        uirevision: true,
        legend: legend,
    }
    return layout
}




function read_spectral_lines_list(){
    // read text from URL location
    var request = new XMLHttpRequest();
    request.open('GET', '/assets/spectral_lines.json', true);
    request.send(null);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            var type = request.getResponseHeader('Content-Type');
            if (type.indexOf("text") !== 1) {
                return request.responseText;
            }
        }
    }
}


function add_alpha_to_rgb(rgb_string, alpha){
    var rgb = rgb_string.replace(/[^\d,]/g, '').split(',');
    return "rgb("+rgb[0]+","+rgb[1]+","+rgb[2]+","+alpha+")"


}


function fnu_to_abmag(fnu){
    if(fnu <= 0)
        return null
    else
        return -2.5 * Math.log10(fnu) - 48.60
}

function flambda_to_fnu(flam, lam, wavelength_unit){
    if(wavelength_unit == "nanometer")
        lam = lam * 10.0
    return (10**-23) * 3.33564095 * (10**4) * (lam**2) * flam
}

function flambda_to_abmag(flam,lam, wavelength_unit){
    return fnu_to_abmag(flambda_to_fnu(flam,lam,wavelength_unit))
}






