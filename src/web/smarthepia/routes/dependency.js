var express = require('express');
var router = express.Router();
var dateFormat = require('dateformat');
var Dependency = require('../models/dependency');
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');


// GET /dependency
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        return res.render('pages/dependency', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "dependency" });
    }else{
        return res.redirect('/');
    }
});

// POST /dependency/create
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){

        var dictionary = req.body;
        var args = Object.keys(dictionary).length;
        var depName = dictionary.depName;
        var max = Object.keys(dictionary).length -1;

        if(depName && args >= 6 && ((max % 5) === 0)){

            // Check if the dependency name already exist
            validation.checkUniqueDependency(depName, function (matchDependency) {
                if(matchDependency){

                    // Empty array to store dependency device
                    var newDevice = [];

                    // Add dico data to list
                    var length = max / 5;
                    for (var i = 0; i < length; i++){
                        newDevice.push({name: dictionary['dependency['+i+'][depdName]'], ip: dictionary['dependency['+i+'][depdIp]'], port: dictionary['dependency['+i+'][depdPort]'], comment: dictionary['dependency['+i+'][depdComment]'], method: dictionary['dependency['+i+'][depdMethod]']});
                    }
                    var newDependency = {depname: depName, devices: newDevice};
                    Dependency.create(newDependency, function (error, user) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Dependency has been successfully created"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Dependency name must be unique"});
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

router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, devices: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(error);
            }
            return res.json({"data": dependency});
        });

    }else{
        return res.redirect('/');
    }
});

router.get('/listall', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(error);
            }
            return res.json({"data": createNewData(dependency)});
        });

    }else{
        return res.redirect('/');
    }
});

// To solve the sub dict
function createNewData(data){
    var newData = []
    for (i = 0; i < data.length; i++) {
        for (j = 0; j < data[i].devices.length; j++) {
            newData.push({
                depName: data[i].depname,
                divName: data[i].devices[j].name,
                ip: data[i].devices[j].ip,
                port: data[i].devices[j].port,
                method: data[i].devices[j].method,
                comment: data[i].devices[j].comment
            });
        }
    }
    return newData;
}

module.exports = router;