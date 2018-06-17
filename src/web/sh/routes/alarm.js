var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');
var User = require('../models/user');
var io = require('../sockets/socket').io;
var Notify = require('../controllers/alarm');

// Module variables
var isAuth = require('../controllers/isAuth');

router.use(passport.session());

// GET /alarm
router.get('/',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/alarm', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "alarm"});
    }else{
        return res.redirect('/');
    }
});

// GET /alarm/listall
router.get('/listall',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var toRemove = {_id: false};
        var query = {$and: [{$or : [{assign: {$eq: "anyone"}},{assign: {$eq: req.session.email}}]}, {ack: {$eq: 0}}]};
        Alarm.find(query, {}, function(err, alarm) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({data: alarm});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /alarm/ack
router.get('/ack',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var id = req.query.id;
        if(id) {
            Alarm.update({_id: id}, {$set: { ack: 1 }}, function (err, alarm) {
                if (err) {
                    return next(error);
                }

                // Send to all client connected the new
                // alarm notify change
                io.emit('alarmNotify', "");

                res.type('json');
                return res.json({status: "success", message: "Alarm has been successfully ack"});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// GET /alarm/email
router.get('/email', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        User.find({email: {$ne: req.session.email}}, function(err, user) {
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


// GET /alarm/assign
router.get('/assign', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var email = req.query.email;
        var id = req.query.id;

        if(email && id){
            Alarm.update({_id: id}, {$set: {assign: email}}, function (err, alarm) {
                if (err) {
                    return next(error);
                }

                // Send to all client connected the new
                // alarm notify change
                io.emit('alarmNotify', "");

                res.type('json');
                return res.json({status: "success", message: "Alarm has been successfully assign"});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// GET /alarm/badge
router.get('/badge', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        // Get number of alarm not ack and the type
        Notify.alarmNotify(req.session.email, function (sucess, json) {
            if (sucess) {
                res.type('json');
                return res.json(json);
            }
        });
    }else{
        return res.redirect('/');
    }
});

module.exports = router;