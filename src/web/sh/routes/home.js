// Module Dependencies
var express = require('express');
var passport = require('../controllers/passport');
var auth = require('../controllers/auth');
var config = require('../configs/config');
var UserModel = require('../models/user');
var Devices = require('../models/devices');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');
var Notify = require('../controllers/alarm');
var router = express.Router();

var io = require('../sockets/socket').io;

// Module variables
var isAuth = require('../controllers/isAuth');

// Middleware
//router.use(passport.initialize());
router.use(passport.session());

// GET /home
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.status(200).render('pages/home', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "home"});
    }else{
        return res.redirect('/');
    }
});

// GET /home/list
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        let toRemove = {__v: false, _id: false, address: false};
        Devices.find({}, toRemove, function(err, devices) {
            if (err) {
                return next(error);
            }
            res.type('json');
            return res.json({data: devices});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /home/alarmnotfy
router.get('/alarmnotfy', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        // Get number of alarm not ack and the type
        Notify.alarmNotify(function (sucess, json) {
            if (sucess) {

                // Send to all client connected the new
                // alarm notify change
                io.emit('alarmNotify', json);
                io.emit('graphChange', "alarmNotify");

                // Response to the automation client
                res.type('json');
                return res.json({data: "alarmNotify"});
            }
        });

        // Get what type of alarm, not ack
        /*Alarm.aggregate([{$match: {ack: 0}},{$group: {_id: null, minType: {$min: "$atype"}}}], function (err, alarmMin) {
            if (err) {
                console.error(err);
                throw(err);
            }

            // Get number of alarm, not ack
            Alarm.count({ack: 0}, function (err, alarmNumber) {
                if (err) {
                    console.error(err);
                    throw(err);
                }

                // If atype == -1 or count == -1 => no alarm not ack
                var json = null;
                if(alarmNumber !== 0) {
                    json = {"atype": alarmMin[0].minType, "count": alarmNumber};
                }else{
                    json = {"atype": -1, "count": -1};
                }

                // Send to all client connected the new
                // alarm notify change
                io.emit('alarmNotify', json);
                io.emit('graphChange', "alarmNotify");

                // Response to the automation client
                res.type('json');
                return res.json({data: "alarmNotify"});
            });
        });*/
    }else{
        return res.redirect('/');
    }
});

module.exports = router;