
// Convert datetime to timestamp
function toTimestamp(strDate){
    var datum = Date.parse(strDate);
    return datum;
}

// Format series
function prepare_series(data){
    var series = [];
    for (var i = 0, len = data.data.length; i < len; i++) {

        var new_serie = {name: data.data[i].name, data: []};

        // First time add cause empty
        if (series.length === 0){
            series.push(new_serie);
        }else{
            var hasDuplicate = series.map(function(e){return e.name === new_serie.name}).reduce(function(pre, cur) {return pre || cur});
            if (!hasDuplicate) {
                series.push(new_serie);
            }
        }
    }
    return series;
}

// Format series
function gen_series(series, data, measure_type){
    for (var i = 0, len = data.data.length; i < len; i++) {

        for (var j = 0; j < series.length; j++) {
            if (series[j].name === data.data[i].name) {

                var t = measure_type.split(" ")[0].toLowerCase();
                if(t === "motion"){
                    series[j].data.push([toTimestamp(data.data[i].updatetime), convert_motion(data.data[i][t])]);
                }else{
                    series[j].data.push([toTimestamp(data.data[i].updatetime), data.data[i][t]]);
                }
            }
        }
    }
    return series;
}

// Convert
// true->1
// false->0
function convert_motion(motion){
    if(motion){
        return 1;
    }else{
        return 0;
    }
}

// Get data from db and load graph
function genMsGraph(dateFrom, dateTo, room, measure_type){
    var mt = {"Temperature (°C)":"mst", "Humidity (%)":"msh", "Battery (%)":"msb", "Luminance (lum)":"msl", "Motion":"msm"};
    if (mt[measure_type]) {
        $.get('/multisensor/' + mt[measure_type], {dateFrom: dateFrom, dateTo: dateTo, room: room}).done(function (data) {
            var series = gen_series(prepare_series(data), data, measure_type);
            loadMsGraph(series, measure_type);
        });
    }else{
        toastr.error("Could not load graph data", "error", {closeButton: true});
    }
}

// Load multisensor graph
function loadMsGraph(series, measure_type){

    // Clear charts
    clearGraph('#graphMultisensor');

    // Fill charts
    $('#graphMultisensor').highcharts({
        title: {
            text: 'Chart ' + measure_type.split(" ")[0]
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: "%e. %b",
                month: "%b '%y",
                year: "%Y"
            },title: {
                text: 'Date'
            },
        },
        yAxis: {
            title: {
                text: measure_type
            }
        },
        series: series,
    });
}

// Clear chart
function clearGraph(charts){
    var chart = $(charts).highcharts();
    if(chart) {
        var seriesLength = chart.series.length;
        for (var i = seriesLength - 1; i > -1; i--) {
            chart.series[i].remove();
        }
    }
}

// Get data from db and load graph
function genAcGraph(dateFrom, dateTo, room){
    $.get('/actuator/measure', {dateFrom: dateFrom, dateTo: dateTo, room: room}).done(function (data) {
        var series = gen_series(prepare_series(data), data, "value");
        loadAcGraph(series);
    });
}

// Load multisensor graph
function loadAcGraph(series){

    // Clear charts
    clearGraph('#graphActuator');

    // Fill charts
    $('#graphActuator').highcharts({
        title: {
            text: 'Chart actuator position'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: "%e. %b",
                month: "%b '%y",
                year: "%Y"
            },title: {
                text: 'Date'
            },
        },
        yAxis: {
            title: {
                text: "Position"
            }
        },
        series: series,
    });
}