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

// GET manager register => /location/create
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var locationType = req.body.locationSelect;
        var building_parent = req.body.buildingSelect;
        var floor_parent = req.body.floorSelect;
        var building_name = req.body.buildingInput;
        var floor_name = req.body.floorInput;
        var corridor_name = req.body.corridorInput;
        var room_name = req.body.roomInput;
        var room_orientation = req.body.orientationInput;
        var room_rule = req.body.ruleSelect;
        var comment = req.body.commentInput;
        var floorNameRelation = req.body.floorName;
        var buildingNameRelation = req.body.buildingName;
        if(locationType) {
            if(locationType === "Building"){
                if(building_name && buildingNameRelation){

                    // Check if building name already exists
                    validation.checkUniqueLocation(building_name, 0, function (uniqueLocation) {
                        if(uniqueLocation){
                            var parentRelation = buildingNameRelation;
                            var newLocation = {name: building_name, type: "Building", parent: 0, enable: true, comment: comment ? comment: "", parentrelation: parentRelation};
                            Devices.create(newLocation, function (err, user) {
                                if (err) {
                                    return next(err);
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
                if(floor_name && building_parent && buildingNameRelation){

                    // Check if floor already exists for that building
                    validation.checkUniqueLocation(floor_name, parseInt(building_parent), function (uniqueLocation) {
                        if(uniqueLocation){
                            var parentRelation = buildingNameRelation;
                            var newLocation = {name: floor_name, type: "Floor", parent: parseInt(building_parent), enable: true, comment: comment ? comment: "", parentrelation: parentRelation};
                            Devices.create(newLocation, function (err, user) {
                                if (err) {
                                    return next(err);
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
                if(room_name && room_orientation && room_rule && building_parent && floor_parent && buildingNameRelation && floorNameRelation){

                    // Check if room already exists for that floor
                    validation.checkUniqueLocation(room_name, parseInt(floor_parent), function (uniqueLocation) {
                        if(uniqueLocation){
                            var parentRelation = buildingNameRelation+">"+floorNameRelation;
                            var newLocation = {name: room_name, type: "Room", parent: parseInt(floor_parent), enable: true, orientation: room_orientation, comment: (comment ? comment : ""), rules: room_rule, parentrelation: parentRelation};
                            Devices.create(newLocation, function (err, user) {
                                if (err) {
                                    return next(err);
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
            }else if(locationType === "Corridor"){
                if(corridor_name && building_parent && floor_parent && buildingNameRelation && floorNameRelation){

                    // Check if room already exists for that floor
                    validation.checkUniqueLocation(corridor_name, parseInt(floor_parent), function (uniqueLocation) {
                        if(uniqueLocation){
                            var parentRelation = buildingNameRelation+">"+floorNameRelation;
                            var newLocation = {name: corridor_name, type: "Corridor", parent: parseInt(floor_parent), enable: true, comment: (comment ? comment : ""), parentrelation: parentRelation};
                            Devices.create(newLocation, function (err, user) {
                                if (err) {
                                    return next(err);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Corridor has been successfully created"});
                            });
                        }else{
                            res.type('json');
                            return res.json({status: "error", message: "Corridor name already exists for that floor"});
                        }
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "All field must be filled"});
                }
            }else{
                res.type('json');
                return res.json({status: "error", message: "Not a location type"});
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// GET /location/list
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, value: false, itemStyle: false, comment: false, dependency: false, group: false, rules: false, orientation: false, enable: false};
        Devices.find({}, toRemove, function(err, location) {
            if (err) {
                return next(err);
            }
            return res.json({"data": location});
        });

    }else{
        return res.redirect('/');
    }
});

// GET /location/listall
router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, value: false, itemStyle: false, group: false};
        Devices.find({$or: [{type: "Building"},  {type: "Floor"}, {type: "Room"}, {type: "Corridor"} ] }, toRemove, function(err, location) {
            if (err) {
                return next(err);
            }
            return res.json({data: location});
        });
    }else{
        return res.redirect('/');
    }
});

// POST /location/edit
router.post('/edit', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){


        var idEdit = req.body.idEdit;
        var nameEdit = req.body.nameEdit;
        var enableEdit = req.body.enableEdit;
        var ruleEdit = req.body.ruleEdit;
        var commentEdit = req.body.commentEdit;
        var orientationEdit = req.body.orientationEdit;
        var typeEdit = req.body.typeEdit;

        // Check if not empty
        if (typeEdit && idEdit && nameEdit && enableEdit){

            // Check if room => update other way
            if(typeEdit === "Room"){

                // Check if not empty
                if(orientationEdit && ruleEdit){
                    var set = {enable: enableEdit, rules: ruleEdit, orientation: orientationEdit, comment: commentEdit ? commentEdit : ""};
                    Devices.findOneAndUpdate({_id: idEdit}, set, function (err, location) {
                        if (err) {
                            return next(err);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Location " + nameEdit + " has been successfully edited"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "All field must be filled"});
                }

            }else{
                var set = {enable: enableEdit, comment: commentEdit ? commentEdit : ""};
                Devices.findOneAndUpdate({_id: idEdit}, set, function (err, location) {
                    if (err) {
                        return next(err);
                    }
                    res.type('json');
                    return res.json({status: "success", message: "Location " + nameEdit + " has been successfully edited"});
                });
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});


// POST /location/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var idDelete = req.body.id;
        var nameDelete = req.body.name;
        var childIdDelete = req.body.childId;

        // Check if not empty
        if(idDelete && nameDelete && (childIdDelete || childIdDelete === 0)){

            // Check child <-> parent
            Devices.find({parent: parseInt(childIdDelete)}, function(err, deviceParent) {

                // If > 0 then we have child
                // So we must delete child before delete the root parent
                if(deviceParent.length > 0){
                    res.type('json');
                    return res.json({status: "error", message: "There are device, room, floor which belong to that location. You must deleted them before to delete the location."});
                }else{

                    // Remove location name entree
                    Devices.remove({_id: idDelete}, function (err, rule) {
                        if (err) {
                            return next(err);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Location " + nameDelete + " has been successfully deleted"});
                    });
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

module.exports = router;