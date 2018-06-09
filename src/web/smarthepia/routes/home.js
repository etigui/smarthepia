var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var Devices = require('../models/devices');
var dateFormat = require('dateformat');

// GET /home
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        return res.render('pages/home', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "home" });
    }else{
        return res.redirect('/');
    }
});

router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
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