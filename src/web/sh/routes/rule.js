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
    if(auth.checkPermission(req, auth.getManager())) {

        var ruleName = req.body.ruleName;
        var active = req.body.active;
        var dayTimeStart = req.body.dayTimeFrom;
        var nightTimeStart = req.body.nightTimeFrom;
        var temps = req.body.temp;
        var humidity = req.body.humidity;
        var dayNightValve = req.body.dnRulesValve;
        var dayRulesBlind = req.body.dayRulesBlind;
        var nightRulesBlind = req.body.nightRulesBlind;

        // Switch error
        if (active !== "on") {
            active = 0;
        } else {
            active = 1;
        }

        // Check rules exist
        if (ruleName && dayTimeStart && nightTimeStart && temps && humidity && dayNightValve && dayRulesBlind && nightRulesBlind) {

            // Check if night time is after day time
            if (dayTimeStart < nightTimeStart) {

                // Check if the rule rule name already exist
                validation.checkUniqueRule(ruleName, function (matchRule) {
                    if (matchRule) {
                        var newRule = {
                            name: ruleName,
                            active: active,
                            dt: dayTimeStart,
                            nt: nightTimeStart,
                            temp: temps,
                            humidity: humidity,
                            vdnr: dayNightValve,
                            bdr: dayRulesBlind,
                            bnr: nightRulesBlind
                        };
                        Rule.create(newRule, function (err, rule) {
                            if (err) {
                                return next(err);
                            }
                            res.type('json');
                            return res.json({status: "success", message: "Rule " + ruleName + " has been successfully created"});

                        });
                    } else {
                        res.type('json');
                        return res.json({status: "error", message: "Rule name must be unique"});
                    }
                });
            }else{
                res.type('json');
                return res.json({status: "error", message: "The night start time must be before (day meaning), the day time start"});
            }
        } else {
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// GET /rule/listall
router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        let toRemove = {__v: false};
        Rule.find({}, toRemove, function(err, rule) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({data: rule});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /rule/listall
router.post('/edit', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var idEdit = req.body.idEdit;
        var activeEdit = req.body.activeEdit;
        var ruleNameEdit = req.body.ruleNameEdit;
        var dayTimeFromEdit = req.body.dayTimeFromEdit;
        var nightTimeFromEdit = req.body.nightTimeFromEdit;
        var tempEdit = req.body.tempEdit;
        var humidityEdit = req.body.humidityEdit;
        var dnRulesValveEdit = req.body.dnRulesValveEdit;
        var dayRulesBlindEdit = req.body.dayRulesBlindEdit;
        var nightRulesBlindEdit = req.body.nightRulesBlindEdit;


        // Switch error
        if (activeEdit !== "on") {
            activeEdit = 0;
        } else {
            activeEdit = 1;
        }

        // Check rules exist
        if(idEdit && ruleNameEdit && dayTimeFromEdit && nightTimeFromEdit && tempEdit && humidityEdit && dnRulesValveEdit && dayRulesBlindEdit && nightRulesBlindEdit) {

            // Check if night time is after day time
            if (dayTimeFromEdit < nightTimeFromEdit) {
                var set = {
                    $set: {
                        active: activeEdit,
                        dt: dayTimeFromEdit,
                        nt: nightTimeFromEdit,
                        temp: tempEdit,
                        humidity: humidityEdit,
                        vdnr: dnRulesValveEdit,
                        bdr: dayRulesBlindEdit,
                        bnr: nightRulesBlindEdit,
                        name: ruleNameEdit
                    }
                };
                Rule.findOneAndUpdate({_id: idEdit}, set, function (err, rule) {
                    if (err) {
                        return next(err);
                    }
                    res.type('json');
                    return res.json({status: "success", message: "Rule " + ruleNameEdit + " has been successfully edited"});
                });
            }else{
                res.type('json');
                return res.json({status: "error", message: "The night start time must be before (day meaning), the day time start"});
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be fille or zero value is not permitted"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST /rule/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var ruleName = req.body.id;
        if(ruleName) {

            // Check if the rule rule name exists
            validation.checkUniqueRule(ruleName, function (matchRule) {
                if (!matchRule) {

                    // Remove rule name entree
                    Rule.remove({name: ruleName}, function (err, rule) {
                        if (err) {
                            return next(err);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Rule " + ruleName + " has been successfully deleted"});
                    });

                } else {
                    res.type('json');
                    return res.json({status: "error", message: "Rule name not exists"});
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
// Used When add location
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


module.exports = router;