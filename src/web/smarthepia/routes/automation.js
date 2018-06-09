var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var Automation = require('../models/automation');


// GET /automation
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        return res.render('pages/automation', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "automation" });
    }else{
        return res.redirect('/');
    }
});



// POST /automation/create
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

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

            // Check if the automation rule name already exist
            validation.checkUniqueAutomation(ruleName, function (matchAutomation) {
                if(matchAutomation){
                    var newAutomation = {name:ruleName, active:active, dt:dayTimeStart, nt:nightTimeStart, temp:temps, humidity:humidity, vdr: dayNightValve, vnr:dayNightValve, bdr:dayRulesBlind, bnr: nightRulesBlind};
                    Automation.create(newAutomation, function (error, automation) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Automation rule has been successfully created"});

                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Automation name must be unique"});
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


// GET /automation/listname
router.get('/listname', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, active: false, dt: false, nt: false, temp: false, humidity: false, vdr: false, vnr: false, bdr: false, bnr: false};
        Automation.find({}, toRemove, function(err, automation) {
            if (err) {
                return next(error);
            }
            res.type('json');
            return res.json({data: automation});
        });
    }else{
        return res.redirect('/');
    }
});

// GET /automation/list
router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        var name = req.query.name;
        if(name){
            let toRemove = {__v: false, _id: false};
            Automation.findOne({name: name}, toRemove, function(err, automation) {
                if (err) {
                    return next(error);
                }
                res.type('json');
                return res.json({data: automation});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST /automation/delete
router.post('/delete', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

        var ruleName = req.body.name;
        console.log(ruleName);
        if(ruleName) {

            // Check if the automation rule name exists
            validation.checkUniqueAutomation(ruleName, function (matchAutomation) {
                if (!matchAutomation) {

                    // Remove automation name entree
                    Automation.remove({name: ruleName}, function (err, automation) {
                        if (err) {
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Automation rule " + ruleName + " has been successfully deleted"});
                    });

                } else {
                    res.type('json');
                    return res.json({status: "error", message: "Automation name must exists"});
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