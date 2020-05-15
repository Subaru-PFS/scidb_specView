//alert("dedW")



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

        set_figure: function(modified_timestamp, data) {
            figure_data = build_figure_data(data)
            wavelength_unit = get_wavelength_unit(data)
            //x_range = get_x_range(data)
            figure_layout = build_figure_layout(x_axis_label=wavelength_unit)
            console.log(JSON.stringify(figure_layout.xaxis))
            return {data:figure_data, layout:figure_layout}
        }
    }
});

function get_x_range(data){
    var x_min=0.0
    var x_max=1.0
    if(data.traces == null){
        return [x_min,x_max]
    }
    trace_names = Object.keys(data.traces)
    if(trace_names.length == 0){
        return [x_min,x_max]
    }else{
        x_min = Number.MAX_VALUE
        x_max = Number.MIN_VALUE
        for(i=0; i<trace_names.length; i++){
            trace_name = trace_names[i]
            x_min = Math.min(x_min, Math.min.apply(Math, data.traces[trace_name].x_coords))
            x_max = Math.max(x_max, Math.max.apply(Math, data.traces[trace_name].x_coords))
        }
        return [x_min,x_max]
    }
}


function get_wavelength_unit(data){
    trace_names = Object.keys(data.traces)
    if(trace_names.length == 0){
        return "Wavelength"
    }else{
        // getting unit from first trace, assumes all traces have same units
        trace_name = trace_names[0]
        if(data.traces[trace_name].wavelength_unit == null){
            return "Wavelength"
        }else{
            unit = data.traces[trace_name].wavelength_unit
            if(unit == "angstrom"){
                return "Wavelength (angstrom)"
            }else if(unit == "nanometer"){
                return "Wavelength (nanometers)"
            }else{
                return "Wavelength"
            }
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
                        mode: "lines",
                        type: 'scatter',
                        //type: 'scattergl',
                        visible: data.traces[trace_name].visible,
                        color: data.traces[trace_name].color,
                        xaxis: "x",
                        yaxis: "y",
                        marker:{size: 12},
                        line:{color:data.traces[trace_name].color,
                        wavelength_unit: data.traces[trace_name].wavelength_unit,
                        flux_unit: data.traces[trace_name].flux_unit
                        }
            }
            traces.push(trace)
        }
        return traces
    }else{
        return []
    }
}


function build_figure_layout(x_axis_label="Wavelength", y_axis_label="Flux"){
    var layout = {
        showlegend: true,
        //dragmode: "pan",

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
        //clickmode:'event+select'
    }
    return layout
}



