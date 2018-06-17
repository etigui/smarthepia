var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');
var Notify = require('../controllers/alarm');
var io = require('../sockets/socket').io;

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
        console.log(req.session.email);
        Alarm.find(query, {}, function(err, alarm) {
            if (err) {
                return next(error);
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

                // Get number of alarm not ack and the type
                Notify.alarmNotify(function (sucess, json) {
                    if (sucess) {

                        // Send to all client connected the new
                        // alarm notify change
                        io.emit('alarmNotify', json);

                        res.type('json');
                        return res.json({status: "success", message: "Alarm has been successfully ack"});

                    }
                });

                // Add
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

                        res.type('json');
                        return res.json({status: "success", message: "Alarm has been successfully ack"});
                    });
                });*/
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