// Module Dependencies
var express = require('express');
var passport = require('../controllers/passport');
var auth = require('../controllers/auth');
var config = require('../configs/config');
var UserModel = require('../models/user');
var Devices = require('../models/devices');
var dateFormat = require('dateformat');
var router = express.Router();

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


router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        res.type('json');
        let toRemove = {__v: false, _id: false};
        Devices.find({}, toRemove, function(err, devices) {
            if (err) {
                return next(error);
            }
            return res.json({data: devices});
        });

    }else{
        return res.redirect('/');
    }
});

module.exports = router;