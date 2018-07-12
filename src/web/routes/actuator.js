var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Statistic = require('../models/stat');
var Devices = require('../models/devices');
var passport = require('../controllers/passport');
var StatAcSchema = require('../models/statsac');

// Module variables
var isAuth = require('../controllers/isAuth');

// Middleware
//router.use(passport.initialize());
router.use(passport.session());

// GET /actuator
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.render('pages/actuator', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm/dd/yyyy"),permission: req.session.permissions, page: "actuator" });
    }else{
        return res.redirect('/');
    }
});

// GET /actuator/room
router.get('/room', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){

        let toRemove = {__v: false, value: false, itemStyle: false, group: false, rules: false, orientation: false};
        Devices.find({type: "Room"}, toRemove, function(err, user) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});


// GET /multisensor/device
router.get('/devices', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var id = req.query.id;
        let toRemove = {__v: false, value: false, itemStyle: false, group: false, rules: false, orientation: false};
        Devices.find({"$and": [{type: "Actuator"}, {parent: id}]}, toRemove, function(err, user) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});


// GET /statistic/mst
router.get('/measure', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        var devices = req.query.devices;
        let toRemove = {_id: false, __v: false, parent: false,};
        //parent: room, id: devices, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]
        StatAcSchema.find({parent: parseInt(room), id: parseInt(devices), "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]}, toRemove, function(err, user) {
            if (err) {
                return next(err);
            }
            console.log(user);
            res.type('json');
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /statistic/mst
router.get('/cc', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var newLocation = {name: "name", type: "Actuator", id: 2, subtype: "subtype", value: 222, parent: 4, dependency: "sssss", address: "ssss"};
        StatAcSchema.create(newLocation, function (err, user) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({status: "success", message: "Floor has been successfully created"});
        });
    }else{
        return res.redirect('/');
    }
});



module.exports = router;