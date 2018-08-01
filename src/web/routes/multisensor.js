var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Statistic = require('../models/stat');
var Devices = require('../models/devices');
var passport = require('../controllers/passport');

// Module variables
var isAuth = require('../controllers/isAuth');

// Middleware
//router.use(passport.initialize());
router.use(passport.session());


// GET /test
router.get('/',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.render('pages/multisensor', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm/dd/yyyy"),permission: req.session.permissions, page: "multisensor"});
    }else{
        return res.redirect('/');
    }
});

// GET /test/room
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

// GET /statistic/mst
router.get('/mst', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        let toRemove = {_id: false, __v: false, parent: false, battery: false, humidity: false, luminance: false, motion: false, reftime: false};
        Statistic.find({parent: room, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]}, toRemove, {sort: {updatetime: 1}}, function(err, user) {
            if (err) {
                console.log(err);
                return next(err);
            }
            res.type('json');
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /statistic/msh
router.get('/msh', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        let toRemove = {_id: false, __v: false, parent: false, battery: false, temperature: false, luminance: false, motion: false, reftime: false};
        Statistic.find({parent: room, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]}, toRemove, {sort: {updatetime: 1}}, function(err, user) {
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


// GET /statistic/msb
router.get('/msb', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        let toRemove = {_id: false, __v: false, parent: false, temperature: false, humidity: false, luminance: false, motion: false, reftime: false};
        Statistic.find({parent: room, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]}, toRemove, {sort: {updatetime: 1}}, function(err, user) {
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


// GET /statistic/msl
router.get('/msl', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        let toRemove = {_id: false, __v: false, parent: false, battery: false, humidity: false, temperature: false, motion: false, reftime: false};
        Statistic.find({parent: room, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]}, toRemove, {sort: {updatetime: 1}}, function(err, user) {
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


// GET /statistic/msm
router.get('/msm', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        var dateFrom = req.query.dateFrom;
        var dateTo = req.query.dateTo;
        var room = req.query.room;
        let toRemove = {_id: false, __v: false, parent: false, battery: false, humidity: false, luminance: false, temperature: false, reftime: false};
        Statistic.find({parent: room, "$and" : [{updatetime : {"$gte": new Date(dateFrom)}}, {updatetime : {"$lte": new Date(dateTo)}}]},  toRemove, {sort: {updatetime: 1}}, function(err, user) {
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

module.exports = router;