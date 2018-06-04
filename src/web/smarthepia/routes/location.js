var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var Devices = require('../models/devices');
var validation = require('../controllers/validation');

// GET /location
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        return res.render('pages/location', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "location" });
    }else{
        return res.redirect('/');
    }
});

// GET manager register => /manager/register
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

        // Check if the dependency name already exist
        //validation.checkUniqueLocation(locName, function (matchLocation) {

        //});


        //{color:
        // var newLocation = {name: "Building A", type: "Building", parent: 0, comment: "No comment", dependency: "KNX",group: "group", rules: "Default", orientation: "North", enable: true};
        var newLocation = {name: "Room 1", type: "Room", parent: 4, enable: true};

        Devices.create(newLocation, function (error, user) {
            if (error) {
                console.log(error);
                return next(error);
            }
            return res.send("Hello");
        });


    }else{
        return res.redirect('/');
    }
});

router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, value: false, itemStyle: false, comment: false, dependency: false, group: false, rules: false, orientation: false, enable: false};
        Devices.find({}, toRemove, function(err, location) {
            if (err) {
                return next(error);
            }
            return res.json({"data": location});
        });

    }else{
        return res.redirect('/');
    }
});

module.exports = router;