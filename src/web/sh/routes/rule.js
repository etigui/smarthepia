var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Rule = require('../models/rule');

// Module variables
var isAuth = require('../controllers/isAuth');

// GET /rule
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/rule', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "rule" });
    }else{
        return res.redirect('/');
    }
});

// POST /rule/create
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var ruleName = req.body.rulesName;
        var active = req.body.active;
        var dayTimeStart = req.body.dayTimeFrom;
        var nightTimeStart = req.body.nightTimeFrom;
        var temps = req.body.temp;
        var humidity = req.body.humidity;
        var dayNightValve = req.body.dnRulesValve;
        var dayRulesBlind = req.body.dayRulesBlind;
        var nightRulesBlind = req.body.nightRulesBlind;

        // Switch error
        if(active !== "on"){
            active = 0;
        }else{
            active = 1;
        }

        // Check rules exist
        if(ruleName && dayTimeStart && nightTimeStart && temps && humidity && dayNightValve && dayRulesBlind && nightRulesBlind){

            // Check if the rule rule name already exist
            validation.checkUniqueRule(ruleName, function (matchRule) {
                if(matchRule){
                    var newRule = {name:ruleName, active:active, dt:dayTimeStart, nt:nightTimeStart, temp:temps, humidity:humidity, vdr: dayNightValve, vnr:dayNightValve, bdr:dayRulesBlind, bnr: nightRulesBlind};
                    Rule.create(newRule, function (error, rule) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Rule has been successfully created"});

                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Rule name must be unique"});
                }
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});


// GET /rule/listname
router.get('/listname', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, active: false, dt: false, nt: false, temp: false, humidity: false, vdr: false, vnr: false, bdr: false, bnr: false};
        Rule.find({}, toRemove, function(err, rule) {
            if (err) {
                return next(error);
            }
            res.type('json');
            return res.json({data: rule});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /rule/list
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var name = req.query.name;
        if(name){
            let toRemove = {__v: false, _id: false};
            Rule.findOne({name: name}, toRemove, function(err, rule) {
                if (err) {
                    return next(error);
                }
                res.type('json');
                return res.json({data: rule});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST /rule/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var ruleName = req.body.name;
        console.log(ruleName);
        if(ruleName) {

            // Check if the rule rule name exists
            validation.checkUniqueRule(ruleName, function (matchRule) {
                if (!matchRule) {

                    // Remove rule name entree
                    Rule.remove({name: ruleName}, function (err, rule) {
                        if (err) {
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Rule " + ruleName + " has been successfully deleted"});
                    });

                } else {
                    res.type('json');
                    return res.json({status: "error", message: "Rule name must exists"});
                }
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