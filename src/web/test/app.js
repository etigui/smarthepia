var express = require('express');
//var body_parser = require('body-parser');
var app = express();
//app.use(body_parser.json());

app.set('view engine', 'ejs');

var data = {'value': JSON.stringify([{name:'rpi1-A500',itemStyle:{color:'#3aa255'},children:[{name:'S1',value:1,itemStyle:{color:'#ff3333'},label:{show:!0,formatter:'S1-A501',silent:!1,padding:3}},{name:'s2',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S2-A501'}},{name:'s3',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S3-A502'}},{name:'s4',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S4-A502'}},{name:'s5',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S5-A503'}},{name:'s6',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S6-A503'}},{name:'s7',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S7-A504'}},{name:'s8',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S8-A504'}},{name:'s9',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S9-A505'}},{name:'s10',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S10-A505'}},{name:'s11',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S11-A506'}},{name:'s12',value:1,itemStyle:{color:'#3aa255'},label:{show:!0,formatter:'S12-A506'}}]},{name:'rpi2-A500',itemStyle:{color:'#3aa255'},children:[{name:'s1',value:1,itemStyle:{color:'#3aa255'}}]},{name:'rpi3-A400',itemStyle:{color:'#3aa255'},children:[{name:'s1',value:1,itemStyle:{color:'#3aa255'}},{name:'s2',value:1,itemStyle:{color:'#3aa255'}},{name:'s3',value:1,itemStyle:{color:'#3aa255'}},{name:'s4',value:1,itemStyle:{color:'#3aa255'}},{name:'s5',value:1,itemStyle:{color:'#3aa255'}}]}])};

app.get('/', function (req, res) {
    res.render('index', {data: data});
});

app.listen(80, () => console.log('Server running'));
console.log(data);
