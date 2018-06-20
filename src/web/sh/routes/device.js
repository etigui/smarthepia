var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');

// Module variables
var isAuth = require('../controllers/isAuth');

// GET /device
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/device', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "device" });
    }else{
        return res.redirect('/');
    }
});

// GET /device/create
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var name = req.body.nameDevice;
        var address = req.body.idDevice;
        var dependency = req.body.dependencyDevice;
        var active = req.body.activeDevice;
        var building = req.body.buildingDevice;
        var floor = req.body.floorDevice;
        var room = parseInt(req.body.roomDevice);
        var comment = req.body.commentDevice;
        var type = req.body.typeDevice;
        var subtype = req.body.subTypeDevice;


        // Change here if actuator are not only KNX address type
        var validateKNXAddr = /^\d+\/\d+$/;
        if(type && address && subtype && type === "Actuator" && !address.match(validateKNXAddr) && (subtype === "Blind" || subtype === "Valve")){
            res.type('json');
            return res.json({status: "error", message: "Bad device id"});
        } else if(name && address && dependency && active && building && floor && room && type && subtype){



            // Check if Device is unique by his parent and if id is unique by his dependency
            // (((id & dependency) => unique) | ((name & parent) => unique))
            validation.checkUniqueDevice(room, name, address, dependency, function (deviceUnique) {
                if(deviceUnique){

                    var newDevice = {name: name, address: address, type: type, parent: room, enable: active, dependency: dependency, subtype: subtype, comment: (comment ? comment : "")};
                    Devices.create(newDevice, function (error, device) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Device has been successfully created"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Device name already exists for that room or device id already exists for that dependency"});
                }
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
router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, id : false, value: false, itemStyle: false, group: false, rules: false, orientation: false};
        Devices.find({$or: [{type: "Actuator"},  {type: "Sensor"}]}, toRemove, function(err, user) {
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