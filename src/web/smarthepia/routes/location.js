var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');
var validation = require('../controllers/validation');

// GET /location
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        return res.render('pages/location', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "location" });
    }else{
        return res.redirect('/');
    }
});

// GET manager register => /manager/register
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

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
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else if(locationType === "Floor"){
                if(floor && building){
                    newLocation = {name: floor, type: "Floor", parent: parseInt(building, 10), enable: true, comment: comment ? comment: ""};
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
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else if(locationType === "Room"){
                if(room && floor && building && rule && orientation){
                    newLocation = {name: room, type: "Room", parent: parseInt(floor, 10), enable: true, orientation: orientation, comment: (comment ? comment : "")};
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

router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
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
router.get('/listall', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
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