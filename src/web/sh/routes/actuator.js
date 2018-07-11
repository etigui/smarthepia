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

// GET /actuator
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.render('pages/actuator', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "actuator" });
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


module.exports = router;