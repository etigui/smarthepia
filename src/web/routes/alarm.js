var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');
var User = require('../models/user');
var io = require('../sockets/socket').io;
var Notify = require('../controllers/alarm');
var config = require('../configs/config');

// Module variables
var isAuth = require('../controllers/isAuth');

router.use(passport.session());

// GET /alarm
router.get('/',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/alarm', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm/dd/yyyy"),permission: req.session.permissions, page: "alarm"});
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
    if(auth.checkPermission(req, auth.getManager())) {

        var id = req.query.id;
        var comment = req.query.comment;
        var many = req.query.many;

        if (many && id) {
            if (many === "1") {

                // Ack one alarm
                var set = {
                    $set: {
                        ack: 1,
                        dend: Date.now(),
                        comment: (comment ? comment : ""),
                        assign: req.session.email
                    }
                };
                Alarm.update({_id: id}, set, function (err, alarm) {
                    if (err) {
                        return next(err);
                    }

                    // Send to all client connected the new
                    // alarm notify change
                    io.emit('alarmNotify', "");

                    res.type('json');
                    return res.json({status: "success", message: "Alarm has been successfully ack"});
                });
            } else if (many === "2") {
                var ids = [];

                // Add all id to assign to list
                id.forEach(function (item) {
                    ids.push(item['_id'])
                });

                // Ack multiple alarm
                var set = {
                    $set: {
                        ack: 1,
                        dend: Date.now(),
                        comment: (comment ? comment : ""),
                        assign: req.session.email
                    }
                };
                Alarm.updateMany({_id: {$in: ids}}, set, function (err, alarm) {
                    if (err) {
                        return next(err);
                    }

                    // Send to all client connected the new
                    // alarm notify change
                    io.emit('alarmNotify', "");
                    res.type('json');
                    return res.json({status: "success", message: "Alarm has been successfully ack"});
                });
            } else {
                res.type('json');
                return res.json({status: "error", message: "All field must be filled"});
            }
        }else {
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }





        /*var id = req.query.id;
        var comment = req.query.comment;
        var many = req.query.many;
        if(id) {
            var set = {$set: { ack: 1, dend: Date.now(), comment: (comment ? comment : ""), assign: req.session.email}};
            Alarm.update({_id: id}, set,  function (err, alarm) {
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
        }*/
    }else{
        return res.redirect('/');
    }
});

// GET /alarm/email
router.get('/email', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        User.find({$and : [{email: {$ne: req.session.email}}, {email: {$ne: config.emailNotify}}]}, function(err, user) { // loadUserEmail
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
        var many = req.query.many;
        var id = req.query.id;
        if(many && email && id){
            if(many === "1"){

                // Assign only one alarm
                Alarm.update({_id: id}, {$set: {assign: email}}, function (err, alarm) {
                    if (err) {
                        return next(err);
                    }

                    // Send to all client connected the new
                    // alarm notify change
                    io.emit('alarmNotify', "");

                    res.type('json');
                    return res.json({status: "success", message: "Alarm has been successfully assign"});
                });
            }else if(many === "2"){
                var ids = [];

                // Add all id to assign to list
                id.forEach(function(item) {
                    ids.push(item['_id'])
                });

                // Assign multiple alarm to user
                Alarm.updateMany({_id:{$in: ids}}, {$set: {assign: email}}, function (err, alarm) {
                    if (err) {
                        return next(err);
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