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
            trace_names = Object.keys(data.traces)
            for(i=0; i<trace_names.length; i++){
                trace_name = trace_names[i]
                options.push({label: trace_name, value: trace_name})
            }
            return options
        },

        set_figure: function(modified_timestamp, data) {
            figure_data = build_figure_data(data)
            figure_layout = build_figure_layout()
            return {data:figure_data, layout:figure_layout}
        }


    }
});


function build_figure_data(data){

    trace_names = Object.keys(data.traces)
    traces = []
    for(i=0; i<trace_names.length; i++){
        trace_name = trace_names[i]
        trace_data = data.traces[trace_name]
        trace = {   name:data.traces[trace_name].name,
                    x: data.traces[trace_name].x_coords,
                    y: data.traces[trace_name].y_coords,
                    mode: "lines",
                    type: 'scattergl',
                    visible: data.traces[trace_name].visible,
                    color: data.traces[trace_name].color,
                    xaxis: "x",
                    yaxis: "y",
                    marker:{size: 12},
                    line:{color:data.traces[trace_name].color}
         }
        traces.push(trace)
    }
    return traces
}


function build_figure_layout(){
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

        title:{text: "SpecViewer", y: 0.9, x: 0.5, xanchor: 'center', yanchor: 'top'},
        title: {font: {size: 30}, text: "SpecViewer", y: 0.9, x: 0.5, xanchor: "center", yanchor: "top"},
        font: {family: "Courier New, monospace", size: 18, color: "#7f7f7f"},
        xaxis: {anchor: "y", domain: [0,1], title: {text: "Wavelength"} },
        yaxis: {anchor: "x", domain: [0,1], title: {text: "Flux"}},

        xaxis_title:"Wavelength", yaxis_title:"Flux",
        font:{family:"Courier New, monospace", size:18, color:"#7f7f7f"},
        plot_bgcolor:'rgb(250,250,250)',
        clickmode:'event+select'
    }
    return layout
}



