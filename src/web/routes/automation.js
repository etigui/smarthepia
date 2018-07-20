var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var dateFormat = require('dateformat');
var Automation = require('../models/automation');
var User = require('../models/user');
var io = require('../sockets/socket').io;
var Notify = require('../controllers/alarm');
var config = require('../configs/config');

// Module variables
var isAuth = require('../controllers/isAuth');

router.use(passport.session());

// GET /automation
router.get('/',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        return res.render('pages/automation', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm/dd/yyyy"),permission: req.session.permissions, page: "automation"});
    }else{
        return res.redirect('/');
    }
});


// GET /automation
router.get('/list',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        Automation.find({},{}, function(err, automation) {
            if (err) {
                return next(err);
            }
            res.type('json');
            return res.json({data: automation});
        });

    }else{
        return res.redirect('/');
    }
});

// GET /create
router.post('/create',  isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        Automation.find({},{}, function(err, automationCheck) {
            if (err) {
                return next(err);
            }

            var oHpTempMin = req.body.oHpTempMin;
            var oHpTempMax = req.body.oHpTempMax;
            var HpTempMin = req.body.HpTempMin;
            var HpTempMax = req.body.HpTempMax;
            var minTempInside = req.body.minTempInside;
            var minTempOutside = req.body.minTempOutside;
            var maxTempSummer = req.body.maxTempSummer;
            var automationId = req.body.automationId;
            var pidProp = req.body.pidProp;
            var pidInt = req.body.pidInt;
            var pidDer = req.body.pidDer;
            var hpStartMonth = req.body.hpStartMonth;
            var hpEndMonth = req.body.hpEndMonth;
            var hpStartDay = req.body.hpStartDay;
            var hpEndDay = req.body.hpEndDay;
            console.log(automationId);

            // Check if all value are filled
            if(oHpTempMin && oHpTempMax && HpTempMin && HpTempMax && minTempInside && minTempOutside && maxTempSummer && pidProp && pidInt && parseFloat(pidDer) && hpStartMonth && hpEndMonth && hpStartDay && hpEndDay){

                // If eq than 0 => create
                if(automationCheck.length === 0){

                    var newAutomation = {hpstartday: hpStartDay, hpstartmonth: hpStartMonth, hpstopday: hpEndDay, hpstopmonth: hpEndMonth, hptempmin: HpTempMin, hptempmax: HpTempMax, nhptempmin: oHpTempMin, nhptempmax: oHpTempMax, outtempmin: minTempOutside, outsummax: maxTempSummer, kp: pidProp, ki: pidInt,kd: pidDer,intempmin: minTempInside};
                    Automation.create(newAutomation, function(err, automation) {
                        if (err) {
                            return next(err);

                        }
                        res.type('json');
                        return res.json({status: "success", message: "Automation has been successfully created"});
                    });

                }else{
                    if(automationId){

                        var setAutomation = {$set: {hpstartday: hpStartDay, hpstartmonth: hpStartMonth, hpstopday: hpEndDay, hpstopmonth: hpEndMonth, hptempmin: HpTempMin, hptempmax: HpTempMax, nhptempmin: oHpTempMin, nhptempmax: oHpTempMax, outtempmin: minTempOutside, outsummax: maxTempSummer, kp: pidProp, ki: pidInt,kd: parseFloat(pidDer),intempmin: minTempInside}};
                        Automation.findOneAndUpdate({_id: automationId}, setAutomation, function(err, automation) {
                            if (err) {
                                return next(err);
                            }
                            res.type('json');
                            return res.json({status: "success", message: "Automation has been successfully updated"});
                        });
                    }else{
                        res.type('json');
                        return res.json({status: "error", message: "All field must be fille or zero value is not permitted"});
                    }
                }
            }else{
                res.type('json');
                return res.json({status: "error", message: "All field must be fille or zero value is not permitted"});
            }
        });

    }else{
        return res.redirect('/');
    }
});


module.exports = router;