// Module Dependencies
var express = require('express');
var passport = require('../controllers/passport');
var auth = require('../controllers/auth');
var config = require('../configs/config');
var UserModel = require('../models/user');
var Devices = require('../models/devices');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');
var Status = require('../models/status');
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
                return next(err);
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
        Notify.alarmNotify(req.session.email, function (sucess, json) {
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
    }else{
        return res.redirect('/');
    }
});

// GET /home/statusnotfy
router.get('/statusnotfy', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

            // Send to all client connected the new
            // status notify change
            io.emit('statusNotify', "");

            // Response to the automation client
            res.type('json');
            return res.json({data: "statusNotify"});

    }else{
        return res.redirect('/');
    }
});

// GET /home/liststatus
router.get('/liststatus', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        Status.find({}, function(err, status) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({data: status});
        });
    }else{
        return res.redirect('/');
    }
});



// GET /home/status
/*router.get('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var newStatus = {name: "automation", color: 1, status: "Running 4/4", updatetime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy")};
        Status.create(newStatus, function(err, status) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({status: "success", message: "Floor has been successfully created"});
        });
    }else{
        return res.redirect('/');
    }
});*/

module.exports = router;