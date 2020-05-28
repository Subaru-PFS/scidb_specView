//alert("dedW")
var spectral_lines = []
$.getJSON('/assets/spectral_lines.json', function(jsondata) {
    line_names = Object.keys(jsondata)
    for(i=0; i<line_names.length; i++){
        spectral_lines.push(jsondata[line_names[i]])
    }
})


window.PlotlyConfig = {MathJaxConfig: 'local'}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
/*
        large_params_function: function(data) {
            var a = 1
            return [{label: 'trace1', value: 'trace1'}]
        }
*/
        set_dropdown_options: function(modified_timestamp, data) {
            options = []
            if(data != null){
                trace_names = Object.keys(data.traces)
                for(i=0; i<trace_names.length; i++){
                    trace_name = trace_names[i]
                    options.push({label: trace_name, value: trace_name})
                }
            }
            return options
        },

        set_figure: function(modified_timestamp, spectral_lines_switch, redshift, data) {
            figure_data = build_figure_data(data, spectral_lines_switch, redshift)
            //x_range = get_x_range(data)
            figure_layout = build_figure_layout(data, spectral_lines_switch=spectral_lines_switch, redshift)
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
            x_min = Math.min(x_min, Math.min.apply(Math, data.traces[trace_name].x_coords))
            x_max = Math.max(x_max, Math.max.apply(Math, data.traces[trace_name].x_coords))
            y_min = Math.min(y_min, Math.min.apply(Math, data.traces[trace_name].y_coords))
            y_max = Math.max(y_max, Math.max.apply(Math, data.traces[trace_name].y_coords))
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





function build_figure_data(data, spectral_lines_switch, redshift){
    traces = []

    ranges = get_data_ranges(data)
    wavelength_unit = get_wavelength_unit(data)
    ranges = get_data_ranges(data)


    var annotations = []
    var shapes = [] // https://plotly.com/python/reference/#layout-shapes
    if(spectral_lines_switch == true){

        for(i=0; i < spectral_lines.length;i++){
            line = spectral_lines[i]
            x0 = (1.0+redshift)*line.lambda_vacuum
            line_label = line.name
            if(wavelength_unit == "nanometer")
                x0 = x0/10.0
            x1=x0
            if(x0 >= ranges.x_range[0] && x0 <= ranges.x_range[1]){

                y0 = ranges.y_range[0] + 0.1*(ranges.y_range[1]-ranges.y_range[0])
                y1 = ranges.y_range[1] - 0.1*(ranges.y_range[1]-ranges.y_range[0])
                //https://plotly.com/javascript/reference/#bar
                trace = {   x: [x0], y:[y1], //mode: "markers+lines",
                            name: line_label,
                            width: [1],
                            type: 'bar',
                            visible: true,
                            color: 'black',
                            opacity: 1.0,
                            xaxis: "x",
                            yaxis: "y",
                            yref: "paper",
                            text: line_label,
                            textposition: 'auto',

                            //hoverinfo: 'none',
                            marker:{size: 0.5, color:"black"},
                            line:{  color:"black", width:0.5},
                            showlegend: false
                        }
                //traces.push(trace)
            }
        }
    }



    if(data != null){
        trace_names = Object.keys(data.traces)
        for(i=0; i<trace_names.length; i++){
            trace_name = trace_names[i]
            //trace_data = data.traces[trace_name]
            trace = {   name:data.traces[trace_name].name,
                        x: data.traces[trace_name].x_coords,
                        y: data.traces[trace_name].y_coords,
                        mode: "markers+lines",
                        //type: 'scatter',
                        type: 'scattergl',
                        visible: data.traces[trace_name].visible,
                        color: data.traces[trace_name].color,
                        xaxis: "x",
                        yaxis: "y",
                        marker:{size: 1.0, color:data.traces[trace_name].color},
                        line:{  color:data.traces[trace_name].color,
                                width:1.0
                        }
            }
            traces.push(trace)
        }
    }
    return traces
}


function build_figure_layout(data, spectral_lines_switch=false, redshift=0.0){

    x_axis_label = get_x_axis_label(data)
    y_axis_label = get_y_axis_label(data)
    wavelength_unit = get_wavelength_unit(data)
    flux_unit = get_flux_unit(data)
    ranges = get_data_ranges(data)

    var annotations = []
    var shapes = [] // https://plotly.com/python/reference/#layout-shapes
    if(spectral_lines_switch == true){

        for(i=0; i < spectral_lines.length;i++){
            line = spectral_lines[i]
            x0 = (1.0+redshift)*line.lambda_vacuum
            line_label = line.name
            line_label = line.label
            if(wavelength_unit == "nanometer")
                x0 = x0/10.0
            x1=x0
            if(x0 >= ranges.x_range[0] && x0 <= ranges.x_range[1]){

                if(i % 3 == 0){
                    y_line_annotation = 1.0
                }else if(i % 3 == 1){
                    y_line_annotation = 1.02
                }else{
                    y_line_annotation = 1.04
                }

                y0 = ranges.y_range[0] + 0.1*(ranges.y_range[1]-ranges.y_range[0])
                y1 = ranges.y_range[1] - 0.1*(ranges.y_range[1]-ranges.y_range[0])
                y0=0
                y1=1

                line = {type: 'line', name:line_label,  layer:'above', xref:'x', yref: 'paper', y0: y0, y1: y1, x0: x0, x1: x1, line:{ width:0.5, color:"grey"}, opacity:0.5 }
                shapes.push(line)

                annotation = {showarrow: false, text: line_label, align: "center",x: x0, xanchor: "center", y: y_line_annotation, yanchor: "bottom", yref:"paper", font:{size:10, family:"Arial",color:"grey"}, opacity:1}
                annotations.push(annotation)
            }
        }
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
        font:{family:"Courier New, monospace", size:18, color:"#7f7f7f"},
        plot_bgcolor:'rgb(250,250,250)',
        clickmode:'event+select',
        shapes: shapes,
        annotations: annotations
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