var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');
var validation = require('../controllers/validation');

// Module variables
var isAuth = require('../controllers/isAuth');

// GET /location
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/location', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "location" });
    }else{
        return res.redirect('/');
    }
});

// GET manager register => /manager/register
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var locationType = req.body.locationCreate;
        var comment = req.body.commentCreate;
        var building = req.body.buildingCreate;
        var floor = req.body.floorCreate;
        var orientation = req.body.orientationCreate;
        var rule = req.body.ruleCreate;
        var room = req.body.roomCreate;
        var newLocation = {};

        // Check location type
        if(locationType){
            if(locationType === "Building"){
                if(building){

                    // Check if building name already exists
                    validation.checkUniqueLocation(building, 0, function (uniqueLocation) {
                        if(uniqueLocation){
                            newLocation = {name: building, type: "Building", parent: 0, enable: true, comment: comment ? comment: ""};
                            Devices.create(newLocation, function (error, user) {
                                if (error) {
                                    console.log(error);
                                    return next(error);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Building has been successfully created"});
                            });
                        }else{
                            res.type('json');
                            return res.json({status: "error", message: "Building name already exists"});
                        }
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else if(locationType === "Floor"){
                if(floor && building){

                    // Check if floor already exists for that building
                    validation.checkUniqueLocation(floor, parseInt(building), function (uniqueLocation) {
                        if(uniqueLocation){
                            newLocation = {name: floor, type: "Floor", parent: parseInt(building), enable: true, comment: comment ? comment: ""};
                            Devices.create(newLocation, function (error, user) {
                                if (error) {
                                    console.log(error);
                                    return next(error);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Floor has been successfully created"});
                            });
                        }else{
                            res.type('json');
                            return res.json({status: "error", message: "Floor name already exists for that building"});
                        }
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else if(locationType === "Room"){
                if(room && floor && building && rule && orientation){

                    // Check if room already exists for that floor
                    validation.checkUniqueLocation(room, parseInt(floor), function (uniqueLocation) {
                        if(uniqueLocation){
                            newLocation = {name: room, type: "Room", parent: parseInt(floor), enable: true, orientation: orientation, comment: (comment ? comment : ""), rules: rule};
                            Devices.create(newLocation, function (error, user) {
                                if (error) {
                                    console.log(error);
                                    return next(error);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Romm has been successfully created"});
                            });
                        }else{
                            res.type('json');
                            return res.json({status: "error", message: "Room name already exists for that floor"});
                        }
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else{
                res.type('json');
                return res.json({message: "Not a location type", status: "error" });
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, value: false, itemStyle: false, comment: false, dependency: false, group: false, rules: false, orientation: false, enable: false};
        Devices.find({}, toRemove, function(err, location) {
            if (err) {
                return next(error);
            }
            return res.json({"data": location});
        });

    }else{
        return res.redirect('/');
    }
});

// GET /device/listall
router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, id : false, value: false, itemStyle: false, group: false};
        Devices.find({$or: [{type: "Building"},  {type: "Floor"}, {type: "Room"} ] }, toRemove, function(err, user) {
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