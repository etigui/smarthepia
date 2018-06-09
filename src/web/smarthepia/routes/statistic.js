var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Statistic = require('../models/statistic');

// GET /statistic
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        return res.render('pages/statistic', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "statistic" });
    }else{
        return res.redirect('/');
    }
});

// GET /statistic
router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){

        /*let newStatistic = {address: "1", dependency: "Test dep", parent: 0, battery: 100, temp: 20, humidity: 45, luminance: 70, motion: false};
        Statistic.create(newStatistic, function (error, statistic) {
            if (error) {
                return next(error);
            }
        });*/

        let toRemove = {__v: false, _id: false};
        Statistic.find({}, toRemove, function(err, statistic) {
            if (err) {
                return next(error);
            }
            res.type('json');
            return res.json({"data": statistic});
        });
    }else{
        return res.redirect('/');
    }
});

module.exports = router;