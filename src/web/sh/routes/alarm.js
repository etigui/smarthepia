var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var dateFormat = require('dateformat');
var Alarm = require('../models/alarm');

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

module.exports = router;