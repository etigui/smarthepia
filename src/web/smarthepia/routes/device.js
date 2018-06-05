var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');

// GET /device
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        return res.render('pages/device', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "device" });
    }else{
        return res.redirect('/');
    }
});


// GET /device/create
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

        var name = req.body.nameDevice;
        var address = req.body.idDevice;
        var dependency = req.body.dependencyDevice;
        var active = req.body.activeDevice;
        var building = req.body.buildingDevice;
        var floor = req.body.floorDevice;
        var room = req.body.roomDevice;
        var comment = req.body.commentDevice;
        var type = req.body.typeDevice;
        if(name && address && dependency && active && building && floor && room && type){
            var newLocation = {name: name, address: address, type: type, parent: parseInt(room, 10), enable: active, dependency: dependency, comment: (comment ? comment : "")};
            Devices.create(newLocation, function (error, user) {
                if (error) {
                    console.log(error);
                    return next(error);
                }
                res.type('json');
                return res.json({status: "success", message: "Device has been successfully created"});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// GET /device/listall
router.get('/listall', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, id : false, value: false, itemStyle: false, group: false, rules: false, orientation: false};
        Devices.find({$or: [{type: "Actuator"},  {type: "Sensor"} ]}, toRemove, function(err, user) {
            if (err) {
                return next(error);
            }
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});


module.exports = router;