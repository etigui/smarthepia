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

// GET /statistic
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.render('pages/statistic', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "statistic" });
    }else{
        return res.redirect('/');
    }
});

// GET /statistic/room
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


// GET /statistic/room
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


// GET /statistic/room
router.get('/mst', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        let toRemove = {_id: false, __v: false, parent: false, battery: false, humidity: false, luminance: false, motion: false, reftime: false};
        Statistic.find({parent: 60, address: 17}, toRemove, function(err, user) {
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


// GET /statistic
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){

        let newStatistic = {address: "1", dependency: "FAKE", parent: 0, battery: 100, temp: 20, humidity: 45, luminance: 70, motion: false};
        Statistic.create(newStatistic, function (error, statistic) {
            if (error) {
                return next(error);
            }
        });
        res.type('json');
        return res.json({"data": ""});
        /*let toRemove = {__v: false, _id: false};
        Statistic.find({}, toRemove, function(err, statistic) {
            if (err) {
                return next(error);
            }
            res.type('json');
            return res.json({"data": statistic});
        });*/
    }else{
        return res.redirect('/');
    }
});

module.exports = router;