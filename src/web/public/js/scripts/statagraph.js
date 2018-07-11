var dom_chart_actuator = document.getElementById("graphActuator");


var chart_actuator  = echarts.init(dom_chart_actuator);


chart_actuator .showLoading();


option_actuator  = null;

function clear_graph(){
    chart_actuator.clear();
}

function loadGraphActuator(dateFrom, dateTo, room, devices){

    $.get('/actuator/measure', {dateFrom : dateFrom, dateTo : dateTo, room: room, devices: devices}).done( function (data) {
        console.log(data.data);
        function process_data(d){
            var out = []
            for(var xx in d) {

                var ds = new Date(d[xx].updatetime);
                let new_val = {name: ds, value: [d[xx].updatetime, d[xx].value]};
                out.push(new_val);

            }
            return out;
        }

        chart_actuator.setOption(option = {
            title: {text: 'Actuator value', subtext: '', x: 'center'},
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    params = params[0];
                    var date = new Date(params.name);
                    return "Date: " +date.getHours() + ":" + date.getMinutes() +":"+ date.getSeconds() + " " +date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + "</br> Actuator: " + params.value[1];
                },
                axisPointer: {animation: false}
            },
            xAxis: {type: 'time', name : '(Date)', splitLine: {show: false}
            },
            yAxis: {type: 'value', name : '()', boundaryGap: [0, '100%'], splitLine: {show: false}
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

        if (option_actuator && typeof option_actuator === "object") {
            chart_actuator.setOption(option_actuator, true);
        }
        chart_actuator.hideLoading();
    });
}
