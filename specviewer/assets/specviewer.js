//alert("dedW")
var spectral_lines = []
$.getJSON('http://localhost:8050/assets/spectral_lines.json', function(jsondata) {
    line_names = Object.keys(jsondata)
    for(i=0; i<line_names.length; i++){
        spectral_lines.push(jsondata[line_names[i]])
    }
})



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
            figure_data = build_figure_data(data)
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

    label = "Wavelength"
    unit = get_wavelength_unit(data)
    if(unit != ""){
        label = label + " (" + unit + ")"
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






function build_figure_data(data){
    if(data != null){
        trace_names = Object.keys(data.traces)
        traces = []
        for(i=0; i<trace_names.length; i++){
            trace_name = trace_names[i]
            //trace_data = data.traces[trace_name]
            trace = {   name:data.traces[trace_name].name,
                        x: data.traces[trace_name].x_coords,
                        y: data.traces[trace_name].y_coords,
                        mode: "markers+lines",
                        type: 'scatter',
                        //type: 'scattergl',
                        visible: data.traces[trace_name].visible,
                        color: data.traces[trace_name].color,
                        xaxis: "x",
                        yaxis: "y",
                        marker:{size: 1.0},
                        line:{  color:data.traces[trace_name].color,
                                wavelength_unit: data.traces[trace_name].wavelength_unit,
                                flux_unit: data.traces[trace_name].flux_unit, width:1.0
                        }
            }
            traces.push(trace)
        }
        return traces
    }else{
        return []
    }
}


function build_figure_layout(data, spectral_lines_switch=false, redshift=0.0){

    x_axis_label = get_x_axis_label(data)
    y_axis_label = get_flux_unit(data)
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

                line = {type: 'line', layer:'above', xref:'x', yref: 'y', y0: y0, y1: y1, x0: x0, x1: x1, line:{ width:0.5}}
                shapes.push(line)

                annotation = {showarrow: false, text: line_label, align: "center",x: x0, xanchor: "center", y: y0, yanchor: "bottom"}
                annotations.push(annotation)
            }
        }
    }


    var layout = {
        showlegend: true,
        dragmode: "pan",

        //hoverlabel: {bgcolor:"white",font_size:100,font_family:"Rockwell",width:500},
        hoverlabel: {bgcolor:"white", bordercolor: "black", align: "left", font:{font_family:"Rockwell", size:20, color:"black"}},
        hovermode:'closest',
        //hoverdistance: 8,
        //transition : {'duration': 500},
        //margin:{"l": 0, "r": 0, "t": 0, "b": 0},
        //xaxis:{showgrid:false, showline:false, zeroline:false},
        //yaxis:{showgrid:false, showline:false, zeroline:false},
        //width: map_width,
        //height: map_height,

        //title:{text: "SpecViewer", y: 0.9, x: 0.5, xanchor: 'center', yanchor: 'top'},
        //title: {font: {size: 30}, text: "SpecViewer", y: 0.9, x: 0.5, xanchor: "center", yanchor: "top"},
        font: {family: "Courier New, monospace", size: 18, color: "#7f7f7f"},
        xaxis: {anchor: "y", title: {text: x_axis_label}, showgrid:false},
        yaxis: {anchor: "x", title: {text: y_axis_label}, showgrid:false},

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