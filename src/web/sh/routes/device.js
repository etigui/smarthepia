var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');
var Statistic = require('../models/stat');
const request = require('request');

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

        var buildingName = req.body.buildingName;
        var floorName = req.body.floorName;
        var roomName = req.body.roomName;


        // Change here if actuator are not only KNX address type
        var validateKNXAddr = /^\d+\/\d+$/;
        if(type && address && subtype && type === "Actuator" && !address.match(validateKNXAddr) && (subtype === "Blind" || subtype === "Valve")){
            res.type('json');
            return res.json({status: "error", message: "Bad device id"});
        } else if(name && address && dependency && active && building && floor && room && type && subtype && buildingName && floorName && roomName){

            // Check if Device is unique by his parent and if id is unique by his dependency
            // (((id & dependency) => unique) | ((name & parent) => unique)) || name => unique
            // (((address & dependency & subtype & parent) => unique)
            // (((address & dependency & subtype) => unique)
            // (((address & dependency) => unique)
            // name => unique
            validation.checkUniqueDevice(subtype, room, name, address, dependency, function (deviceUnique, devicess) {
                if(deviceUnique){
                    var parentRelation = buildingName+">"+floorName+">"+roomName;
                    var newDevice = {name: name, address: address, type: type, parent: room, enable: active, dependency: dependency, subtype: subtype, comment: (comment ? comment : ""), parentrelation: parentRelation};
                    Devices.create(newDevice, function (error, device) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }

                        // Update knx ids in the
                        request('http://10.10.7.35:5000/update', { json: true }, (err, res, body) => {
                            if (err) { return console.log(err); }
                        });

                        res.type('json');
                        return res.json({status: "success", message: "Device has been successfully created"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Device name and device subtype, address, dependency must be unique"});
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
        let toRemove = {__v: false, id : false, value: false, itemStyle: false, group: false, rules: false, orientation: false};
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


// POST /device/edit
router.post('/edit', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var addressEdit = req.body.addressEdit;
        var enableEdit = req.body.enableEdit;
        var commentEdit = req.body.commentEdit;
        var nameEdit = req.body.nameEdit;
        var idEdit = req.body.idEdit;
        var subtypeEdit = req.body.subtypeEdit;
        var dependencyEdit = req.body.dependencyEdit;
        var parentEdit = parseInt(req.body.parentEdit);

        // Check empty value and update device
        if(addressEdit && enableEdit && nameEdit && idEdit && dependencyEdit && parentEdit){


            // Check if Device is unique by his parent and if id is unique by his dependency
            // (((id & dependency) => unique) | ((name & parent) => unique)) || name => unique
            // (((address & dependency & subtype & parent) => unique)
            // (((address & dependency & subtype) => unique)
            // (((address & dependency) => unique)
            // name => unique
            validation.checkUniqueDevice(subtypeEdit, parentEdit, nameEdit, addressEdit, dependencyEdit, function (deviceUnique, devicess) {

                // Check if the address, name, dependency, subtype are unique
                // If 0 => change the address for a new one that not exist
                if(devicess.length === 0){

                    // Update devicce
                    var set = {enable: enableEdit, comment: commentEdit ? commentEdit : "", address: addressEdit};
                    Devices.findOneAndUpdate({_id: idEdit}, set, function (err, device) {
                        if (err) {
                            return next(err);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Device " + nameEdit + " has been successfully edited"});
                    });
                } else if(devicess.length === 1){ // find one device with same prog => cause eg: change just "enable"

                    if(String(devicess[0]._id) === idEdit){ // Check if edit same device

                        // Update devicce
                        var set = {enable: enableEdit, comment: commentEdit ? commentEdit : "", address: addressEdit};
                        Devices.findOneAndUpdate({_id: idEdit}, set, function (err, device) {
                            if (err) {
                                return next(err);
                            }
                            res.type('json');
                            return res.json({status: "success", message: "Device " + nameEdit + " has been successfully edited"});
                        });
                    }else{
                        res.type('json');
                        return res.json({status: "error", message: "Device name and device subtype, address, dependency must be unique"});
                    }
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Device name and device subtype, address, dependency must be unique"});
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

// POST /device/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var idDelete = req.body.id;
        var nameDelete = req.body.name;

        if(idDelete && nameDelete) {

            // Remove device id entree
            Devices.remove({_id: idDelete}, function (err, rule) {
                if (err) {
                    return next(err);
                }

                // Remove all stat for this device
                Statistic.remove({name: nameDelete}, function (err, rule) {
                    if (err) {
                        return next(err);
                    }
                    res.type('json');
                    return res.json({
                        status: "success",
                        message: "Location " + nameDelete + " has been successfully deleted"
                    });
                });
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});


module.exports = router;