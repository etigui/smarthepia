var dom_chart_temp = document.getElementById("graphTemp");
var dom_chart_hum = document.getElementById("graphHum");
var dom_chart_motion = document.getElementById("graphMotion");
var dom_chart_luminance = document.getElementById("graphLuminance");
var dom_chart_battery = document.getElementById("graphBattery");

var chart_temp = echarts.init(dom_chart_temp);
var chart_hum = echarts.init(dom_chart_hum);
var chart_motion = echarts.init(dom_chart_motion);
var chart_luminance = echarts.init(dom_chart_luminance);
var chart_battery = echarts.init(dom_chart_battery);

chart_temp.showLoading();
chart_hum.showLoading();
chart_motion.showLoading();
chart_luminance.showLoading();
chart_battery.showLoading();

option_temp = null;
option_hum = null;
option_motion = null;
option_luminance = null;
option_battery = null;

function loadGraphTem(dateFrom, dateTo, room, devices){

    $.get('/multisensor/mst', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done( function (data) {

        function process_data(d){
            var out = []
            for(var xx in d) {

                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].temperature]};
                out.push(new_val);

            }
            return out;
        }

        chart_temp.setOption(option = {
            title: {text: 'Temparture', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Temperature: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '(°C)', boundaryGap: [0, '100%'], splitLine: {show: false}
            },
            series: [{
                name: 'hepia',
                type: 'line',
                roam: false,
                selectedMode: false,
                data: process_data(data.data),
                breadcrumb: {show: true, textStyle: {fontSize: 100}},
            }]
        });

        if (option_temp && typeof option_temp === "object") {
            chart_temp.setOption(option_temp, true);
        }
        chart_temp.hideLoading();
    });
}
function loadGraphHum(dateFrom, dateTo, room, devices){

    $.get('/multisensor/msh', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done(function (data) {

        function process_data(d){
            var out = []
            for(var xx in d) {
                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].humidity]};
                out.push(new_val);

            }
            return out;
        }

        chart_hum.setOption(option = {
            title: {text: 'Humidity', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Humidity: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '(%)', boundaryGap: [0, '100%'], splitLine: {show: false}
            },
            series: [{
                name: 'hepia',
                type: 'line',
                roam: false,
                selectedMode: false,
                data: process_data(data.data),
                breadcrumb: {show: true, textStyle: {fontSize: 100}},
            }]
        });

        if (option_hum && typeof option_hum === "object") {
            chart_hum.setOption(option_hum, true);
        }
        chart_hum.hideLoading();
    });
}
function loadGraphMotion(dateFrom, dateTo, room, devices){
    $.get('/multisensor/msm', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done(function (data) {

        function process_data(d){
            var out = []
            for(var xx in d) {

                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].motion]};
                out.push(new_val);

            }
            return out;
        }

        chart_motion.setOption(option = {
            title: {text: 'Motion', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Motion: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '(-)', boundaryGap: [0, '100%'], splitLine: {show: false}
            },
            series: [{
                name: 'hepia',
                type: 'line',
                roam: false,
                selectedMode: false,
                data: process_data(data.data),
                breadcrumb: {show: true, textStyle: {fontSize: 100}},
            }]
        });

        if (option_motion && typeof option_motion === "object") {
            chart_motion.setOption(option_motion, true);
        }
        chart_motion.hideLoading();
    });
}
function loadGraphLum(dateFrom, dateTo, room, devices){
    $.get('/multisensor/msl', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done(function (data) {

        function process_data(d){
            var out = []
            for(var xx in d) {

                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].luminance]};
                out.push(new_val);

            }
            return out;
        }

        chart_luminance.setOption(option = {
            title: {text: 'Luminance', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Luminance: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '(lum)', boundaryGap: [0, '100%'], splitLine: {show: false}
            },
            series: [{
                name: 'hepia',
                type: 'line',
                roam: false,
                selectedMode: false,
                data: process_data(data.data),
                breadcrumb: {show: true, textStyle: {fontSize: 100}},
            }]
        });

        if (option_luminance && typeof option_luminance === "object") {
            chart_luminance.setOption(option_luminance, true);
        }
        chart_luminance.hideLoading();
    });
}
function loadGraphBat(dateFrom, dateTo, room, devices){
    $.get('/multisensor/msb', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done(function (data) {

        function process_data(d){
            var out = []
            for(var xx in d) {

                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].battery]};
                out.push(new_val);

            }
            return out;
        }

        chart_battery.setOption(option = {
            title: {text: 'Humidity', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Battery: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '(%)', boundaryGap: [0, '100%'], splitLine: {show: false}
            },
            series: [{
                name: 'hepia',
                type: 'line',
                roam: false,
                selectedMode: false,
                data: process_data(data.data),
                breadcrumb: {show: true, textStyle: {fontSize: 100}},
            }]
        });

        if (option_battery && typeof option_battery === "object") {
            chart_battery.setOption(option_battery, true);
        }
        chart_battery.hideLoading();
    });
}

